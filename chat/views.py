from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, MessageSerializer, 
    ConversationCreateSerializer, InterviewDetailsSerializer,
    InterviewResponseSerializer, FinalSelectionSerializer
)

User = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing conversations"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Seeker: only show active conversations (shortlisted/interview)
        if user.role == 'seeker':
            return Conversation.objects.filter(
                participants=user,
                is_active=True
            ).prefetch_related('participants', 'messages')
        
        # Recruiter: show all their conversations
        if user.role == 'recruiter':
            return Conversation.objects.filter(
                participants=user
            ).prefetch_related('participants', 'messages')
        
        # Admin: show all
        return Conversation.objects.all().prefetch_related('participants', 'messages')
    
    def create(self, request, *args, **kwargs):
        serializer = ConversationCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        
        # Return the conversation with full data
        serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get', 'post'])
    def messages(self, request, pk=None):
        """Get all messages in a conversation or send a new message"""
        conversation = self.get_object()
        
        # Handle POST request - send a new message
        if request.method == 'POST':
            content = request.data.get('content')
            if not content:
                return Response(
                    {'error': 'Content is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verify user is part of this conversation
            if not conversation.participants.filter(id=request.user.id).exists():
                return Response(
                    {'error': 'You are not part of this conversation'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if conversation is active for seekers
            if request.user.role == 'seeker' and not conversation.is_active:
                return Response(
                    {'error': 'Chat is not active yet. You will be able to chat once you are shortlisted.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Create the message
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content,
                message_type=request.data.get('message_type', 'text')
            )
            
            # Update conversation timestamp
            conversation.last_message_at = message.created_at
            conversation.save()
            
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Handle GET request - get all messages
        messages = conversation.messages.all().order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark all messages in conversation as read"""
        conversation = self.get_object()
        updated_count = conversation.messages.filter(
            is_read=False
        ).exclude(
            sender=request.user
        ).update(is_read=True)
        
        return Response({'updated': updated_count})
    
    @action(detail=True, methods=['post'])
    def send_interview_details(self, request, pk=None):
        """Send interview details to a candidate (recruiter only)"""
        if request.user.role != 'recruiter':
            return Response(
                {'error': 'Only recruiters can send interview details'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        conversation = self.get_object()
        
        # Verify recruiter is part of this conversation
        if not conversation.participants.filter(id=request.user.id).exists():
            return Response(
                {'error': 'You are not part of this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = InterviewDetailsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Update conversation with interview details
        conversation.interview_date = serializer.validated_data.get('interview_date')
        conversation.interview_time = serializer.validated_data.get('interview_time')
        conversation.interview_mode = serializer.validated_data.get('interview_mode')
        conversation.meeting_link = serializer.validated_data.get('meeting_link', '')
        conversation.hr_contact = serializer.validated_data.get('hr_contact', '')
        conversation.required_documents = serializer.validated_data.get('required_documents', '')
        conversation.interview_notes = serializer.validated_data.get('interview_notes', '')
        
        # Reset interview status when new interview is scheduled
        conversation.interview_status = 'pending'
        
        # Make conversation active if not already
        if not conversation.is_active:
            conversation.is_active = True
        
        conversation.save()
        
        # Update application status to 'interview'
        if conversation.application:
            conversation.application.status = 'interview'
            conversation.application.save()
        
        # Create a system message about the interview
        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=f"Interview details sent: {conversation.get_interview_mode_display()} on {conversation.interview_date} at {conversation.interview_time}",
            message_type='interview_invite'
        )
        
        # Send notification to job seeker
        from notifications.models import Notification
        seeker = conversation.participants.exclude(id=request.user.id).first()
        if seeker and conversation.job:
            Notification.objects.create(
                user=seeker,
                title=f'Interview Scheduled: {conversation.job.title}',
                message=f'You have been invited for an interview for {conversation.job.title}. Date: {conversation.interview_date}, Time: {conversation.interview_time}',
                notification_type='interview',
                link=f'/chat?conversation={conversation.id}'
            )
        
        return Response(ConversationSerializer(conversation, context={'request': request}).data)
    
    @action(detail=True, methods=['post'])
    def respond_to_interview(self, request, pk=None):
        """Jobseeker responds to interview invitation (accept/reject/reschedule)"""
        if request.user.role != 'seeker':
            return Response(
                {'error': 'Only job seekers can respond to interview invitations'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        conversation = self.get_object()
        
        # Verify seeker is part of this conversation
        if not conversation.participants.filter(id=request.user.id).exists():
            return Response(
                {'error': 'You are not part of this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if interview details exist
        if not conversation.interview_date or not conversation.interview_time:
            return Response(
                {'error': 'No interview has been scheduled yet'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = InterviewResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action = serializer.validated_data.get('action')
        reschedule_reason = serializer.validated_data.get('reschedule_reason', '')
        
        # Update conversation based on response
        if action == 'accept':
            conversation.interview_status = 'accepted'
            content = f"Interview accepted! The candidate has confirmed the interview on {conversation.interview_date} at {conversation.interview_time}."
            status_message = 'Interview Accepted'
        elif action == 'reject':
            conversation.interview_status = 'rejected'
            content = f"Interview declined. The candidate has declined the interview invitation."
            status_message = 'Interview Declined'
        else:  # reschedule
            conversation.interview_status = 'reschedule_requested'
            conversation.reschedule_reason = reschedule_reason
            content = f"Interview reschedule requested. Reason: {reschedule_reason}"
            status_message = 'Reschedule Requested'
        
        conversation.interview_response_date = timezone.now()
        conversation.save()
        
        # Create system message
        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content,
            message_type='general'
        )
        
        # Send notification to recruiter
        from notifications.models import Notification
        recruiter = conversation.participants.filter(role='recruiter').first()
        if recruiter and conversation.job:
            Notification.objects.create(
                user=recruiter,
                title=f'{status_message}: {conversation.job.title}',
                message=content,
                notification_type='interview',
                link=f'/chat?conversation={conversation.id}'
            )
        
        return Response(ConversationSerializer(conversation, context={'request': request}).data)
    
    @action(detail=True, methods=['post'])
    def final_selection(self, request, pk=None):
        """Recruiter makes final selection (hire/reject after interview)"""
        if request.user.role != 'recruiter':
            return Response(
                {'error': 'Only recruiters can make final selection'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        conversation = self.get_object()
        
        # Verify recruiter is part of this conversation
        if not conversation.participants.filter(id=request.user.id).exists():
            return Response(
                {'error': 'You are not part of this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = FinalSelectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action = serializer.validated_data.get('action')
        selection_notes = serializer.validated_data.get('selection_notes', '')
        
        # Update conversation based on selection
        if action == 'selected':
            conversation.final_selection_status = 'selected'
            conversation.selection_date = timezone.now()
            conversation.selection_notes = selection_notes
            
            # Update application status
            new_status = 'offered'
            content = f"🎉 Congratulations! You have been selected for the position! {selection_notes}"
            status_message = 'Candidate Selected'
            
            # Create celebration message
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content,
                message_type='general'
            )
        else:  # rejected
            conversation.final_selection_status = 'rejected'
            conversation.selection_date = timezone.now()
            conversation.selection_notes = selection_notes
            
            # Update application status
            new_status = 'rejected'
            content = f"Thank you for your time. We regret to inform you that we have selected another candidate. {selection_notes}"
            status_message = 'Application Not Selected'
            
            # Create message
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content,
                message_type='general'
            )
        
        conversation.save()
        
        # Update application status in database
        if conversation.application:
            conversation.application.status = new_status
            conversation.application.notes = selection_notes
            conversation.application.save()
            
            # Create status history
            from applications.models import ApplicationStatusHistory
            ApplicationStatusHistory.objects.create(
                application=conversation.application,
                status=new_status,
                notes=selection_notes,
                changed_by=request.user
            )
        
        # Send notification to job seeker
        from notifications.models import Notification
        seeker = conversation.participants.exclude(id=request.user.id).first()
        if seeker and conversation.job:
            Notification.objects.create(
                user=seeker,
                title=f'{status_message}: {conversation.job.title}',
                message=content,
                notification_type='interview',
                link=f'/my-applications'
            )
        
        return Response(ConversationSerializer(conversation, context={'request': request}).data)
    
    @action(detail=False, methods=['get'])
    def my_active_chats(self, request):
        """Get active conversations for the current user (for chat list)"""
        # Seeker: only active chats
        if request.user.role == 'seeker':
            conversations = Conversation.objects.filter(
                participants=request.user,
                is_active=True
            ).prefetch_related('participants', 'messages', 'job', 'application')
        else:
            # Recruiter: all their conversations
            conversations = Conversation.objects.filter(
                participants=request.user
            ).prefetch_related('participants', 'messages', 'job', 'application')
        
        serializer = ConversationSerializer(conversations, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def eligible_for_chat(self, request):
        """Get applications eligible for chat (recruiter can start chat)"""
        from applications.models import Application
        
        if request.user.role != 'recruiter':
            return Response(
                {'error': 'Only recruiters can use this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get applications that are shortlisted/interview/offered/hired
        eligible_applications = Application.objects.filter(
            job__recruiter=request.user,
            status__in=['shortlisted', 'interview', 'offered', 'hired']
        ).select_related('job', 'seeker').prefetch_related('conversations')
        
        result = []
        for app in eligible_applications:
            # Check if conversation already exists
            existing_conversation = app.conversations.first()
            
            result.append({
                'application_id': app.id,
                'job_title': app.job.title,
                'candidate_name': app.seeker.get_full_name() or app.seeker.username,
                'candidate_email': app.seeker.email,
                'application_status': app.status,
                'conversation_exists': existing_conversation is not None,
                'conversation_id': existing_conversation.id if existing_conversation else None,
                'is_active': existing_conversation.is_active if existing_conversation else False
            })
        
        return Response(result)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing messages"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        return Message.objects.filter(
            conversation__participants=self.request.user
        )
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        conversation_id = request.data.get('conversation')
        content = request.data.get('content')
        
        # Get or validate conversation
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                participants=request.user
            )
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if conversation is active for seekers
        if request.user.role == 'seeker' and not conversation.is_active:
            return Response(
                {'error': 'Chat is not active yet. You will be able to chat once you are shortlisted.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create message
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content,
            message_type=request.data.get('message_type', 'text')
        )
        
        # Update conversation timestamp
        conversation.last_message_at = message.created_at
        conversation.save()
        
        # Serialize and return
        output_serializer = MessageSerializer(message)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
