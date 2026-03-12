
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user info"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for messages"""
    
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'content', 'is_read', 'message_type', 'created_at']
        read_only_fields = ['id', 'sender', 'is_read', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations"""
    
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    job_title = serializers.SerializerMethodField()
    other_participant = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'other_participant', 'job', 'job_title',
            'created_at', 'updated_at', 'last_message_at', 'last_message', 
            'unread_count', 'is_active', 'application',
            'interview_date', 'interview_time', 'interview_mode',
            'meeting_link', 'hr_contact', 'required_documents', 'interview_notes',
            # New interview status fields
            'interview_status', 'interview_response_date', 'reschedule_reason',
            # New final selection fields
            'final_selection_status', 'selection_date', 'selection_notes'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_message_at']
    
    def get_last_message(self, obj):
        message = obj.messages.last()
        if message:
            return MessageSerializer(message).data
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0
    
    def get_job_title(self, obj):
        if obj.job:
            return obj.job.title
        return None
    
    def get_other_participant(self, obj):
        request = self.context.get('request')
        if request and request.user:
            other = obj.participants.exclude(id=request.user.id).first()
            if other:
                return UserSerializer(other).data
        return None


class InterviewDetailsSerializer(serializers.Serializer):
    """Serializer for sending interview details"""
    
    interview_date = serializers.DateField(required=True)
    interview_time = serializers.TimeField(required=True)
    interview_mode = serializers.ChoiceField(
        choices=['online', 'offline', 'phone'],
        required=True
    )
    meeting_link = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    hr_contact = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    required_documents = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    interview_notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class InterviewResponseSerializer(serializers.Serializer):
    """Serializer for jobseeker responding to interview"""
    
    ACTION_CHOICES = [
        ('accept', 'Accept'),
        ('reject', 'Reject'),
        ('reschedule', 'Reschedule'),
    ]
    
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    reschedule_reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class FinalSelectionSerializer(serializers.Serializer):
    """Serializer for recruiter's final selection"""
    
    ACTION_CHOICES = [
        ('selected', 'Select/Hire'),
        ('rejected', 'Reject'),
    ]
    
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    selection_notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class ConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating conversations"""
    
    participant_id = serializers.IntegerField(write_only=True)
    job_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    application_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'participant_id', 'job_id', 'application_id', 'is_active']
    
    def create(self, validated_data):
        participant_id = validated_data.pop('participant_id')
        job_id = validated_data.pop('job_id', None)
        application_id = validated_data.pop('application_id', None)
        
        user = self.context['request'].user
        
        # Get participant
        try:
            participant = User.objects.get(id=participant_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"participant_id": "User not found"})
        
        # Check if conversation already exists between these users for this job
        conversation = Conversation.objects.filter(
            participants__in=[user.id, participant.id]
        )
        
        if job_id:
            conversation = conversation.filter(job_id=job_id)
        
        conversation = conversation.distinct()
        
        if conversation.exists():
            existing_conv = conversation.first()
            # Ensure existing conversation is active
            if not existing_conv.is_active:
                existing_conv.is_active = True
                existing_conv.save()
            return existing_conv
        
        # Create new conversation - set is_active=True by default
        # This allows both recruiter and jobseeker to send messages
        conversation = Conversation.objects.create(is_active=True)
        conversation.participants.add(user, participant)
        
        # Link to job
        if job_id:
            from jobs.models import Job
            try:
                job = Job.objects.get(id=job_id)
                conversation.job = job
                conversation.save()
            except Job.DoesNotExist:
                pass
        
        # Link to application
        if application_id:
            from applications.models import Application
            try:
                application = Application.objects.get(id=application_id)
                conversation.application = application
                conversation.save()
            except Application.DoesNotExist:
                pass
        
        return conversation
