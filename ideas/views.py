from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from .models import StartupIdea, Vote, Comment, Bookmark
from .serializers import (
    StartupIdeaSerializer, StartupIdeaListSerializer, StartupIdeaCreateSerializer,
    VoteSerializer, CommentSerializer, CommentCreateSerializer,
    BookmarkSerializer, IdeaApprovalSerializer
)


class StartupIdeaViewSet(viewsets.ModelViewSet):
    """ViewSet for StartupIdea model"""
    
    queryset = StartupIdea.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'problem_statement', 'solution']
    ordering_fields = ['vote_score', 'created_at', 'comment_count']
    ordering = ['-vote_score', '-created_at']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        elif self.action in ['create']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StartupIdeaListSerializer
        elif self.action in ['create']:
            return StartupIdeaCreateSerializer
        return StartupIdeaSerializer
    
    def get_queryset(self):
        queryset = StartupIdea.objects.all()
        
        # For non-admin users, only show approved ideas in list
        if self.action == 'list':
            user = self.request.user
            if not user.is_authenticated or user.role not in ['admin']:
                queryset = queryset.filter(status='approved')
        
        # Apply filters
        category = self.request.query_params.get('category')
        sort = self.request.query_params.get('sort')
        
        if category:
            queryset = queryset.filter(category=category)
        
        if sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'most_voted':
            queryset = queryset.order_by('-vote_score')
        elif sort == 'most_discussed':
            queryset = queryset.order_by('-comment_count')
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment views
        instance.views += 1
        instance.save(update_fields=['views'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to submit ideas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            StartupIdeaSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Only allow creator to update their own ideas
        if instance.user != request.user and not request.user.is_admin:
            return Response(
                {'error': 'You can only update your own ideas'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_admin:
            return Response(
                {'error': 'You can only delete your own ideas'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        """Vote on a startup idea"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to vote'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        idea = self.get_object()
        vote_type = request.data.get('vote_type')
        
        if vote_type not in ['up', 'down']:
            return Response(
                {'error': 'vote_type must be "up" or "down"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get existing vote
        existing_vote = Vote.objects.filter(idea=idea, user=request.user).first()
        
        if existing_vote:
            if existing_vote.vote_type == vote_type:
                # Remove vote if same type
                existing_vote.delete()
                # Update vote counts
                if vote_type == 'up':
                    idea.upvotes = max(0, idea.upvotes - 1)
                else:
                    idea.downvotes = max(0, idea.downvotes - 1)
                idea.vote_score = idea.upvotes - idea.downvotes
                idea.save()
                return Response({'message': 'Vote removed', 'vote_type': None})
            else:
                # Change vote
                old_type = existing_vote.vote_type
                existing_vote.vote_type = vote_type
                existing_vote.save()
                # Update vote counts
                if old_type == 'up':
                    idea.upvotes = max(0, idea.upvotes - 1)
                    idea.downvotes += 1
                else:
                    idea.downvotes = max(0, idea.downvotes - 1)
                    idea.upvotes += 1
                idea.vote_score = idea.upvotes - idea.downvotes
                idea.save()
                return Response({'message': 'Vote changed', 'vote_type': vote_type})
        else:
            # Create new vote
            Vote.objects.create(idea=idea, user=request.user, vote_type=vote_type)
            # Update vote counts
            if vote_type == 'up':
                idea.upvotes += 1
            else:
                idea.downvotes += 1
            idea.vote_score = idea.upvotes - idea.downvotes
            idea.save()
            return Response({'message': 'Vote added', 'vote_type': vote_type})
    
    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        """Report a startup idea"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to report'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        idea = self.get_object()
        reason = request.data.get('reason', '')
        
        idea.is_reported = True
        idea.report_reason = reason
        idea.save()
        
        return Response({'message': 'Idea reported successfully'})
    
    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """Get or create comments for an idea"""
        idea = self.get_object()
        
        if request.method == 'GET':
            comments = idea.comments.filter(parent__isnull=True)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required to comment'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            serializer = CommentCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            # Update comment count
            idea.comment_count = idea.comments.count()
            idea.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def bookmark(self, request, pk=None):
        """Bookmark a startup idea"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to bookmark'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        idea = self.get_object()
        
        existing_bookmark = Bookmark.objects.filter(idea=idea, user=request.user).first()
        
        if existing_bookmark:
            existing_bookmark.delete()
            return Response({'message': 'Bookmark removed', 'is_bookmarked': False})
        else:
            Bookmark.objects.create(idea=idea, user=request.user)
            return Response({'message': 'Idea bookmarked', 'is_bookmarked': True})
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve an idea (admin only)"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can approve ideas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        idea = self.get_object()
        idea.status = 'approved'
        idea.save()
        
        return Response(StartupIdeaSerializer(idea).data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject an idea (admin only)"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can reject ideas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        idea = self.get_object()
        idea.status = 'rejected'
        idea.save()
        
        return Response(StartupIdeaSerializer(idea).data)
    
    @action(detail=False, methods=['get'])
    def my_ideas(self, request):
        """Get current user's submitted ideas"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        ideas = StartupIdea.objects.filter(user=request.user)
        serializer = StartupIdeaSerializer(ideas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def pending(self, request):
        """Get pending ideas (admin only)"""
        ideas = StartupIdea.objects.filter(status='pending')
        serializer = StartupIdeaSerializer(ideas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def reported(self, request):
        """Get reported ideas (admin only)"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can view reported ideas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        ideas = StartupIdea.objects.filter(is_reported=True)
        serializer = StartupIdeaSerializer(ideas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all categories with counts"""
        categories = StartupIdea.objects.filter(status='approved').values('category').annotate(
            count=Count('id')
        ).order_by('-count')
        return Response(categories)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Comment model"""
    
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        return Comment.objects.filter(parent__isnull=True)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_admin:
            return Response(
                {'error': 'You can only delete your own comments'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        """Report a comment"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        comment = self.get_object()
        reason = request.data.get('reason', '')
        
        comment.is_reported = True
        comment.report_reason = reason
        comment.save()
        
        return Response({'message': 'Comment reported successfully'})


class BookmarkViewSet(viewsets.ModelViewSet):
    """ViewSet for Bookmark model"""
    
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
