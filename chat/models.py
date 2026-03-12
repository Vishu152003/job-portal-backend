from django.db import models
from django.conf import settings


class Conversation(models.Model):
    """A conversation between two users (recruiter and job seeker)"""
    
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations'
    )
    job = models.ForeignKey(
        'jobs.Job',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations'
    )
    application = models.ForeignKey(
        'applications.Application',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations'
    )
    # Chat status - chat becomes active only when shortlisted/interview
    is_active = models.BooleanField(default=False)
    # Interview details
    interview_date = models.DateField(null=True, blank=True)
    interview_time = models.TimeField(null=True, blank=True)
    interview_mode = models.CharField(
        max_length=20,
        choices=[
            ('online', 'Online'),
            ('offline', 'Offline'),
            ('phone', 'Phone'),
        ],
        null=True,
        blank=True
    )
    meeting_link = models.URLField(blank=True, null=True)
    hr_contact = models.TextField(blank=True, null=True)
    required_documents = models.TextField(blank=True, null=True)
    interview_notes = models.TextField(blank=True, null=True)
    
    # Interview Status Tracking
    INTERVIEW_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('reschedule_requested', 'Reschedule Requested'),
        ('completed', 'Completed'),
    ]
    interview_status = models.CharField(
        max_length=20,
        choices=INTERVIEW_STATUS_CHOICES,
        default='pending',
        blank=True,
        null=True
    )
    interview_response_date = models.DateTimeField(blank=True, null=True)
    reschedule_reason = models.TextField(blank=True, null=True)
    
    # Final Selection Status
    SELECTION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
    ]
    final_selection_status = models.CharField(
        max_length=20,
        choices=SELECTION_STATUS_CHOICES,
        default='pending',
        blank=True,
        null=True
    )
    selection_date = models.DateTimeField(blank=True, null=True)
    selection_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversations'
        ordering = ['-last_message_at']
    
    def __str__(self):
        participant_names = ', '.join([p.username for p in self.participants.all()[:2]])
        return f"Conversation between {participant_names}"


class Message(models.Model):
    """A message within a conversation"""
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    # Message types for structured content
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('interview_invite', 'Interview Invite'),
        ('document_request', 'Document Request'),
        ('general', 'General'),
    ]
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
        default='text'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"
