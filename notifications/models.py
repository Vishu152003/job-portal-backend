from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    """Model for user notifications"""
    
    NOTIFICATION_TYPES = [
        ('application', 'Job Application'),
        ('status', 'Application Status'),
        ('message', 'New Message'),
        ('job', 'Job Related'),
        ('interview', 'Interview'),
        ('system', 'System'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
    
    @property
    def time_ago(self):
        from django.utils import timezone
        from django.utils.timesince import timesince
        return timesince(self.created_at, timezone.now())


class UserNotificationSettings(models.Model):
    """Model for user notification preferences"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    email_notifications = models.BooleanField(default=True)
    application_notifications = models.BooleanField(default=True)
    message_notifications = models.BooleanField(default=True)
    interview_notifications = models.BooleanField(default=True)
    job_notifications = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Notification settings for {self.user.username}"
