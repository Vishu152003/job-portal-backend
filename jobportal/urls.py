"""
URL configuration for jobportal project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/applications/', include('applications.urls')),
    path('api/ideas/', include('ideas.urls')),
    path('api/ai/', include('ai.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/notifications/', include('notifications.urls')),
]

# WebSocket URL patterns
from chat.routing import websocket_urlpatterns

# For development server, we need to handle WebSocket connections
# The actual WebSocket routing is handled in asgi.py

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
