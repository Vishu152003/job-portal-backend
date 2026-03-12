from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ApplicationViewSet

router = DefaultRouter()
router.register('', ApplicationViewSet, basename='application')

# Note: Custom actions (my_applications, job_applicants, stats) are handled by the router
# The @action decorator with url_path in views.py generates the correct URLs

urlpatterns = [
    path('', include(router.urls)),
]
