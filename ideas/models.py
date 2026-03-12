from django.db import models
from django.conf import settings


class StartupIdea(models.Model):
    """Startup idea model"""
    
    CATEGORY_CHOICES = [
        ('technology', 'Technology'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('finance', 'Finance'),
        ('e-commerce', 'E-commerce'),
        ('food', 'Food & Beverage'),
        ('travel', 'Travel'),
        ('real_estate', 'Real Estate'),
        ('entertainment', 'Entertainment'),
        ('social', 'Social Impact'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='startup_ideas'
    )
    title = models.CharField(max_length=200)
    problem_statement = models.TextField()
    solution = models.TextField()
    target_audience = models.TextField()
    business_model = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='technology')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # AI-generated insights
    ai_summary = models.TextField(blank=True)
    ai_strengths = models.JSONField(default=list, blank=True)
    ai_weaknesses = models.JSONField(default=list, blank=True)
    ai_market_score = models.FloatField(null=True, blank=True)
    ai_trend_analysis = models.TextField(blank=True)
    
    # Voting
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    vote_score = models.IntegerField(default=0)
    
    # Stats
    views = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    
    is_reported = models.BooleanField(default=False)
    report_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'startup_ideas'
        ordering = ['-vote_score', '-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_approved(self):
        return self.status == 'approved'


class Vote(models.Model):
    """Vote model for startup ideas"""
    
    VOTE_CHOICES = [
        ('up', 'Upvote'),
        ('down', 'Downvote'),
    ]
    
    idea = models.ForeignKey(StartupIdea, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'votes'
        unique_together = ['idea', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.idea.title} ({self.vote_type})"


class Comment(models.Model):
    """Comment model for startup ideas"""
    
    idea = models.ForeignKey(StartupIdea, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_reported = models.BooleanField(default=False)
    report_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.idea.title}"


class Bookmark(models.Model):
    """Bookmark model for startup ideas"""
    
    idea = models.ForeignKey(StartupIdea, on_delete=models.CASCADE, related_name='bookmarks')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bookmarks'
        unique_together = ['idea', 'user']
    
    def __str__(self):
        return f"{self.user.username} bookmarked {self.idea.title}"
