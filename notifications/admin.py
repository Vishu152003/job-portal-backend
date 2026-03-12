from django.contrib import admin
from .models import Notification, UserNotificationSettings


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']


@admin.register(UserNotificationSettings)
class UserNotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'email_notifications', 'application_notifications', 
                    'message_notifications', 'interview_notifications', 'job_notifications']
    search_fields = ['user__username']
