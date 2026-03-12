from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Application, ApplicationStatusHistory
from .serializers import (
    ApplicationSerializer, ApplicationCreateSerializer,
    ApplicationStatusUpdateSerializer, ApplicationStatusHistorySerializer,
    RecruiterApplicationSerializer
)
from chat.models import Conversation
from chat.serializers import ConversationSerializer


class IsSeekerOrRecruiter(permissions.BasePermission):
    """Allow access to seekers and recruiters"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['seeker', 'recruiter', 'admin'] or request.user.is_superuser


class ApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for Application model"""
    
    queryset = Application.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['applied_at', 'match_score']
    ordering = ['-applied_at']
    
    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ApplicationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ApplicationStatusUpdateSerializer
        elif self.action in ['job_applicants', 'my_job_applicants']:
            return RecruiterApplicationSerializer
        return ApplicationSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'seeker':
            return Application.objects.filter(seeker=user)
        elif user.role == 'recruiter':
            return Application.objects.filter(job__recruiter=user)
        elif user.is_admin:
            return Application.objects.all()
        
        return Application.objects.none()
    
    def create(self, request, *args, **kwargs):
        if request.user.role != 'seeker':
            return Response(
                {'error': 'Only job seekers can apply for jobs'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            ApplicationSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        user = request.user
        if user.role == 'seeker' and instance.seeker != user:
            return Response(
                {'error': 'You can only update your own applications'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if user.role == 'seeker':
            new_status = request.data.get('status')
            if new_status and new_status != 'withdrawn':
                return Response(
                    {'error': 'You can only withdraw your application'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        return super().update(request, *args, **kwargs)
    
    def _create_or_get_conversation(self, application):
        """Create or get conversation for an application"""
        existing_conversation = Conversation.objects.filter(
            application=application
        ).first()
        
        if existing_conversation:
            return existing_conversation
        
        conversation = Conversation.objects.create(
            job=application.job,
            application=application,
            is_active=False
        )
        conversation.participants.add(application.seeker, application.job.recruiter)
        
        return conversation
    
    def _create_notification(self, application, old_status, new_status, notes):
        """Create notification for the job seeker when application status changes"""
        from notifications.models import Notification
        
        status_messages = {
            'pending': 'Your application is being reviewed',
            'applied': 'Your application has been received',
            'shortlisted': 'Congratulations! You have been shortlisted',
            'interview': 'You have been invited for an interview',
            'offered': 'Congratulations! You have been offered the job',
            'hired': 'You have been hired!',
            'rejected': 'Your application was not selected',
            'withdrawn': 'You have withdrawn your application'
        }
        
        message = status_messages.get(new_status, f'Your application status has been updated to {new_status}')
        if notes:
            message += f': {notes}'
        
        Notification.objects.create(
            user=application.seeker,
            title=f'Application Update: {application.job.title}',
            message=message,
            notification_type='application',
            link=f'/my-applications'
        )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update application status (recruiter/admin only)"""
        if request.user.role not in ['recruiter', 'admin'] and not request.user.is_superuser:
            return Response(
                {'error': 'Only recruiters can update application status'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        application = self.get_object()
        
        if request.user.role == 'recruiter':
            if application.job.recruiter != request.user:
                return Response(
                    {'error': 'You can only update applications for your own jobs'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        old_status = application.status
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if new_status:
            ApplicationStatusHistory.objects.create(
                application=application,
                status=new_status,
                notes=notes,
                changed_by=request.user
            )
            
            application.status = new_status
            if notes:
                application.notes = notes
            application.save()
            
            conversation = self._create_or_get_conversation(application)
            
            if new_status in ['shortlisted', 'interview', 'offered', 'hired']:
                if not conversation.is_active:
                    conversation.is_active = True
                    conversation.save()
                    
                    from chat.models import Message
                    Message.objects.create(
                        conversation=conversation,
                        sender=request.user,
                        content=f"Your application for {application.job.title} has been {new_status.replace('_', ' ')}. You can now chat with the recruiter.",
                        message_type='general'
                    )
            
            self._create_notification(application, old_status, new_status, notes)
        
        return Response(ApplicationSerializer(application).data)
    
    @action(detail=True, methods=['get'])
    def status_history(self, request, pk=None):
        """Get application status history"""
        application = self.get_object()
        
        user = request.user
        if user.role == 'seeker' and application.seeker != user:
            return Response(
                {'error': 'You can only view your own application history'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if user.role == 'recruiter' and application.job.recruiter != user:
            return Response(
                {'error': 'You can only view applications for your own jobs'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        history = application.status_history.all()
        serializer = ApplicationStatusHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_applications(self, request):
        """Get current user's applications"""
        if request.user.role != 'seeker':
            return Response(
                {'error': 'Only job seekers can view their applications'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        applications = Application.objects.filter(seeker=request.user)
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='job/(?P<job_id>[^/.]+)')
    def job_applicants(self, request, job_id=None):
        """Get applicants for a specific job (recruiter only) - ranked by match score"""
        if request.user.role != 'recruiter':
            return Response(
                {'error': 'Only recruiters can view job applicants'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not job_id:
            job_id = request.query_params.get('job_id')

        if not job_id:
            return Response(
                {'error': 'job_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            applications = Application.objects.filter(job__id=job_id, job__recruiter=request.user).select_related('seeker', 'job', 'job__recruiter').order_by('-match_score')
            
            # Increment profile_views when recruiter views applicants
            from accounts.models import Profile
            for application in applications:
                try:
                    profile = application.seeker.profile
                    profile.profile_views += 1
                    profile.save(update_fields=['profile_views'])
                except Exception:
                    pass
            
            serializer = RecruiterApplicationSerializer(applications, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='my-job-applicants')
    def my_job_applicants(self, request):
        """Get all applicants for all jobs posted by the recruiter - ranked by match score"""
        if request.user.role != 'recruiter':
            return Response(
                {'error': 'Only recruiters can view job applicants'},
                status=status.HTTP_403_FORBIDDEN
            )

        applications = Application.objects.filter(job__recruiter=request.user).select_related('job', 'seeker').order_by('-match_score')
        serializer = RecruiterApplicationSerializer(applications, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='recalculate-scores')
    def recalculate_scores(self, request):
        """Recalculate match scores for all applications (recruiter only)"""
        if request.user.role != 'recruiter':
            return Response(
                {'error': 'Only recruiters can recalculate scores'},
                status=status.HTTP_403_FORBIDDEN
            )

        job_id = request.data.get('job_id')
        if not job_id:
            return Response(
                {'error': 'job_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from jobs.models import Job
        try:
            job = Job.objects.get(id=job_id, recruiter=request.user)
        except Job.DoesNotExist:
            return Response(
                {'error': 'Job not found or you do not have permission'},
                status=status.HTTP_404_NOT_FOUND
            )

        applications = Application.objects.filter(job=job)
        updated_count = 0

        for application in applications:
            old_score = application.match_score
            application.match_score = application.calculate_match_score()
            application.save()
            if old_score != application.match_score:
                updated_count += 1

        return Response({
            'message': f'Successfully recalculated scores for {applications.count()} applications',
            'updated_count': updated_count,
            'total_applications': applications.count()
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get application statistics"""
        user = request.user
        
        if user.role == 'seeker':
            total = Application.objects.filter(seeker=user).count()
            pending = Application.objects.filter(seeker=user, status='applied').count()
            interview = Application.objects.filter(seeker=user, status='interview').count()
            rejected = Application.objects.filter(seeker=user, status='rejected').count()
            offered = Application.objects.filter(seeker=user, status__in=['offered', 'hired']).count()
        elif user.role == 'recruiter':
            total = Application.objects.filter(job__recruiter=user).count()
            pending = Application.objects.filter(job__recruiter=user, status='applied').count()
            interview = Application.objects.filter(job__recruiter=user, status='interview').count()
            rejected = Application.objects.filter(job__recruiter=user, status='rejected').count()
            offered = Application.objects.filter(job__recruiter=user, status__in=['offered', 'hired']).count()
        else:
            total = Application.objects.count()
            pending = Application.objects.filter(status='applied').count()
            interview = Application.objects.filter(status='interview').count()
            rejected = Application.objects.filter(status='rejected').count()
            offered = Application.objects.filter(status__in=['offered', 'hired']).count()
        
        return Response({
            'total': total,
            'pending': pending,
            'interview': interview,
            'rejected': rejected,
            'offered': offered
        })
    
    @action(detail=True, methods=['get'])
    def get_conversation(self, request, pk=None):
        """Get or create conversation for this application"""
        application = self.get_object()
        
        user = request.user
        is_seeker = user.role == 'seeker' and application.seeker == user
        is_recruiter = user.role == 'recruiter' and application.job.recruiter == user
        is_admin = user.is_superuser or user.is_admin
        
        if not (is_seeker or is_recruiter or is_admin):
            return Response(
                {'error': 'You do not have permission to view this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        conversation = self._create_or_get_conversation(application)
        
        if not conversation.is_active and user.role == 'seeker':
            return Response({
                'error': 'Chat will be available once you are shortlisted',
                'conversation': None,
                'is_active': False
            })
        
        serializer = ConversationSerializer(conversation, context={'request': request})
        return Response({
            'conversation': serializer.data,
            'is_active': conversation.is_active
        })
