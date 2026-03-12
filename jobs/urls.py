from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobViewSet

router = DefaultRouter()
router.register('', JobViewSet, basename='job')

# Custom action paths must come BEFORE the router URLs
urlpatterns = [
    path('my-jobs/', JobViewSet.as_view({'get': 'my_jobs'}), name='my-jobs'),
    path('saved-jobs/', JobViewSet.as_view({'get': 'saved_jobs'}), name='saved-jobs'),
    path('', include(router.urls)),
]
