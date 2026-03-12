
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Job, SavedJob
from .serializers import (
    JobSerializer, JobListSerializer, JobCreateUpdateSerializer, 
    JobApprovalSerializer, SavedJobSerializer
)


class SavedJobViewSet(viewsets.ModelViewSet):
    """ViewSet for SavedJob model - allows users to save/bookmark jobs"""
    
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Return only the current user's saved jobs
        return SavedJob.objects.filter(user=self.request.user).select_related('job', 'job__recruiter')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_saved_jobs(self, request):
        """Get all saved jobs for the current user"""
        saved_jobs = SavedJob.objects.filter(user=request.user).select_related('job', 'job__recruiter')
        serializer = self.get_serializer(saved_jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_save(self, request, pk=None):
        """Toggle save/unsave a job"""
        job_id = request.data.get('job_id') or pk
        
        if not job_id:
            return Response(
                {'error': 'job_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response(
                {'error': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already saved
        saved_job = SavedJob.objects.filter(user=request.user, job=job).first()
        
        if saved_job:
            # Unsave/remove
            saved_job.delete()
            return Response({'message': 'Job unsaved', 'saved': False})
        else:
            # Save
            SavedJob.objects.create(user=request.user, job=job)
            return Response({'message': 'Job saved', 'saved': True})
    
    @action(detail=False, methods=['get'])
    def check_saved(self, request):
        """Check if a job is saved by the user"""
        job_id = request.query_params.get('job_id')

        if not job_id:
            return Response(
                {'error': 'job_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        is_saved = SavedJob.objects.filter(user=request.user, job_id=job_id).exists()
        return Response({'is_saved': is_saved})


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow read access to all, write access to admin only"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsRecruiterOrAdmin(permissions.BasePermission):
    """Allow access to recruiters and admins"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['recruiter', 'admin'] or request.user.is_superuser


class JobViewSet(viewsets.ModelViewSet):
    """ViewSet for Job model"""
    
    queryset = Job.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location', 'skills']
    ordering_fields = ['created_at', 'salary_min', 'salary_max', 'views']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        elif self.action in ['create']:
            return [IsRecruiterOrAdmin()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return JobCreateUpdateSerializer
        return JobSerializer
    
    def get_queryset(self):
        queryset = Job.objects.all()
        
        # For non-admin users, only show approved jobs in list
        if self.action == 'list':
            user = self.request.user
            if not user.is_authenticated or user.role not in ['admin', 'recruiter']:
                queryset = queryset.filter(status='approved')
        
        # Apply filters
        job_type = self.request.query_params.get('job_type')
        location = self.request.query_params.get('location')
        salary_min = self.request.query_params.get('salary_min')
        salary_max = self.request.query_params.get('salary_max')
        skills = self.request.query_params.get('skills')
        is_remote = self.request.query_params.get('is_remote')
        
        if job_type:
            queryset = queryset.filter(job_type=job_type)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if salary_min:
            queryset = queryset.filter(salary_max__gte=int(salary_min))
        if salary_max:
            queryset = queryset.filter(salary_min__lte=int(salary_max))
        if skills:
            skill_list = skills.split(',')
            for skill in skill_list:
                queryset = queryset.filter(skills__contains=skill.strip())
        if is_remote:
            queryset = queryset.filter(is_remote=is_remote.lower() == 'true')
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment views
        instance.views += 1
        instance.save(update_fields=['views'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            JobSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Only allow recruiter to update their own jobs
        if instance.recruiter != request.user and not request.user.is_admin:
            return Response(
                {'error': 'You can only update your own jobs'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.recruiter != request.user and not request.user.is_admin:
            return Response(
                {'error': 'You can only delete your own jobs'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a job (admin only)"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can approve jobs'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        job = self.get_object()
        job.status = 'approved'
        job.rejection_reason = ''
        job.save()
        
        return Response(JobSerializer(job).data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a job (admin only)"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can reject jobs'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        job = self.get_object()
        rejection_reason = request.data.get('reason', '')
        
        job.status = 'rejected'
        job.rejection_reason = rejection_reason
        job.save()
        
        return Response(JobSerializer(job).data)
    
    @action(detail=False, methods=['get'])
    def my_jobs(self, request):
        """Get jobs posted by current recruiter with applicant counts"""
        if not request.user.is_recruiter and not request.user.is_admin:
            return Response(
                {'error': 'Only recruiters can view their jobs'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.user.is_admin:
            jobs = Job.objects.all().prefetch_related('applications')
        else:
            jobs = Job.objects.filter(recruiter=request.user).prefetch_related('applications')
        
        # Manually construct response with applicant counts
        job_data = []
        for job in jobs:
            job_data.append({
                'id': job.id,
                'recruiter': job.recruiter.id,
                'recruiter_name': job.recruiter.username,
                'company_name': job.recruiter.company.name if hasattr(job.recruiter, 'company') and job.recruiter.company else None,
                'title': job.title,
                'description': job.description,
                'requirements': job.requirements,
                'skills': job.skills,
                'location': job.location,
                'is_remote': job.is_remote,
                'salary_min': job.salary_min,
                'salary_max': job.salary_max,
                'salary_currency': job.salary_currency,
                'job_type': job.job_type,
                'experience_level': job.experience_level,
                'application_deadline': job.application_deadline,
                'positions': job.positions,
                'status': job.status,
                'rejection_reason': job.rejection_reason,
                'views': job.views,
                'application_count': job.applications.count(),
                'applicants': list(job.applications.values('id', 'seeker', 'status', 'applied_at', 'match_score')),
                'created_at': job.created_at,
                'updated_at': job.updated_at,
            })
        
        return Response(job_data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def pending(self, request):
        """Get pending jobs (admin only)"""
        jobs = Job.objects.filter(status='pending')
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search jobs"""
        query = request.query_params.get('q', '')
        jobs = Job.objects.filter(
            Q(status='approved') &
            (Q(title__icontains=query) | Q(description__icontains=query))
        )
        serializer = JobListSerializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def saved_jobs(self, request):
        """Get saved jobs for current user"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        saved_jobs = SavedJob.objects.filter(user=request.user).select_related('job', 'job__recruiter')
        serializer = SavedJobSerializer(saved_jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def save_job(self, request, pk=None):
        """Save a job for current user"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if request.user.role != 'seeker':
            return Response(
                {'error': 'Only job seekers can save jobs'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            job = Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            return Response(
                {'error': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already saved
        saved_job, created = SavedJob.objects.get_or_create(
            user=request.user,
            job=job
        )
        
        if created:
            return Response(
                {'message': 'Job saved successfully'},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': 'Job already saved'},
                status=status.HTTP_200_OK
            )
    
    @action(detail=True, methods=['post'])
    def unsave_job(self, request, pk=None):
        """Unsave a job for current user"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            saved_job = SavedJob.objects.get(user=request.user, job_id=pk)
            saved_job.delete()
            return Response(
                {'message': 'Job unsaved successfully'},
                status=status.HTTP_200_OK
            )
        except SavedJob.DoesNotExist:
            return Response(
                {'error': 'Job not saved'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def check_saved(self, request, pk=None):
        """Check if a job is saved by current user"""
        if not request.user.is_authenticated:
            return Response({'is_saved': False})

        is_saved = SavedJob.objects.filter(user=request.user, job_id=pk).exists()
        return Response({'is_saved': is_saved})
