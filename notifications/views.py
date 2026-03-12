from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Notification, UserNotificationSettings
from .serializers import NotificationSerializer, UserNotificationSettingsSerializer

User = get_user_model()


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notifications"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        unread_count = queryset.filter(is_read=False).count()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'notifications': serializer.data,
            'unread_count': unread_count
        })
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        notifications = self.get_queryset().filter(is_read=False)
        count = notifications.count()
        notifications.update(is_read=True)
        return Response({'status': f'{count} notifications marked as read'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread notification count"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})
    
    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """Clear all notifications"""
        count = self.get_queryset().count()
        self.get_queryset().delete()
        return Response({'status': f'{count} notifications cleared'})


class NotificationSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notification settings"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = UserNotificationSettingsSerializer
    
    def get_queryset(self):
        return UserNotificationSettings.objects.filter(user=self.request.user)
    
    def get_object(self):
        obj, created = UserNotificationSettings.objects.get_or_create(user=self.request.user)
        return obj
    
    def list(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# Utility function to create notifications
def create_notification(user, title, message, notification_type, link=None):
    """Helper function to create a notification"""
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link
    )
