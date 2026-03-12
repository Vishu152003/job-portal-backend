from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StartupIdeaViewSet, CommentViewSet, BookmarkViewSet

router = DefaultRouter()
router.register('', StartupIdeaViewSet, basename='idea')
router.register('comments', CommentViewSet, basename='comment')
router.register('bookmarks', BookmarkViewSet, basename='bookmark')

# Custom action paths must come BEFORE the router URLs
urlpatterns = [
    path('my-ideas/', StartupIdeaViewSet.as_view({'get': 'my_ideas'}), name='my-ideas'),
    path('', include(router.urls)),
]
