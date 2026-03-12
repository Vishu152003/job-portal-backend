from rest_framework import serializers
from .models import Notification, UserNotificationSettings


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'is_read', 'link', 'created_at', 'time_ago']
        read_only_fields = ['id', 'created_at', 'time_ago']


class UserNotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for notification settings"""
    
    class Meta:
        model = UserNotificationSettings
        fields = ['id', 'email_notifications', 'application_notifications', 'message_notifications', 
                  'interview_notifications', 'job_notifications']
