from rest_framework import serializers
from .models import StartupIdea, Vote, Comment, Bookmark


class VoteSerializer(serializers.ModelSerializer):
    """Serializer for Vote model"""
    
    class Meta:
        model = Vote
        fields = ['id', 'idea', 'vote_type', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'idea', 'user', 'user_name', 'content', 'parent',
            'replies', 'is_reported', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'is_reported', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        if obj.parent is None:
            replies = obj.replies.all()
            return CommentSerializer(replies, many=True).data
        return []


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments"""
    
    class Meta:
        model = Comment
        fields = ['idea', 'content', 'parent']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BookmarkSerializer(serializers.ModelSerializer):
    """Serializer for Bookmark model"""
    
    idea_title = serializers.CharField(source='idea.title', read_only=True)
    
    class Meta:
        model = Bookmark
        fields = ['id', 'idea', 'idea_title', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class StartupIdeaSerializer(serializers.ModelSerializer):
    """Serializer for StartupIdea model"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_vote = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    comment_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = StartupIdea
        fields = [
            'id', 'user', 'user_name', 'title', 'problem_statement', 'solution',
            'target_audience', 'business_model', 'category', 'status',
            'ai_summary', 'ai_strengths', 'ai_weaknesses', 'ai_market_score',
            'ai_trend_analysis', 'upvotes', 'downvotes', 'vote_score',
            'views', 'comment_count', 'user_vote', 'is_bookmarked',
            'is_reported', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'ai_summary', 'ai_strengths',
            'ai_weaknesses', 'ai_market_score', 'ai_trend_analysis',
            'upvotes', 'downvotes', 'vote_score', 'views', 'comment_count',
            'is_reported', 'created_at', 'updated_at'
        ]
    
    def get_user_vote(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            vote = Vote.objects.filter(idea=obj, user=user).first()
            return vote.vote_type if vote else None
        return None
    
    def get_is_bookmarked(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return Bookmark.objects.filter(idea=obj, user=user).exists()
        return False


class StartupIdeaListSerializer(serializers.ModelSerializer):
    """Simplified serializer for startup idea listings"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_vote = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    
    class Meta:
        model = StartupIdea
        fields = [
            'id', 'user_name', 'title', 'category', 'status',
            'upvotes', 'downvotes', 'vote_score', 'comment_count',
            'user_vote', 'is_bookmarked', 'created_at'
        ]
        read_only_fields = fields
    
    def get_user_vote(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            vote = Vote.objects.filter(idea=obj, user=user).first()
            return vote.vote_type if vote else None
        return None
    
    def get_is_bookmarked(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return Bookmark.objects.filter(idea=obj, user=user).exists()
        return False


class StartupIdeaCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating startup ideas"""
    
    class Meta:
        model = StartupIdea
        fields = [
            'title', 'problem_statement', 'solution', 'target_audience',
            'business_model', 'category'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class IdeaApprovalSerializer(serializers.ModelSerializer):
    """Serializer for idea approval/rejection"""
    
    class Meta:
        model = StartupIdea
        fields = ['status']
    
    def validate(self, attrs):
        if self.instance.status != 'pending':
            raise serializers.ValidationError(
                {"error": "Can only approve or reject pending ideas"}
            )
        return attrs
