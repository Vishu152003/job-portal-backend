from django.contrib import admin
from .models import StartupIdea, Vote, Comment, Bookmark


@admin.register(StartupIdea)
class StartupIdeaAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'status', 'vote_score', 'views', 'created_at']
    list_filter = ['status', 'category', 'is_reported', 'created_at']
    search_fields = ['title', 'problem_statement', 'solution']
    ordering = ['-created_at']
    readonly_fields = ['views', 'upvotes', 'downvotes', 'vote_score', 'created_at', 'updated_at']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['idea', 'user', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']
    search_fields = ['idea__title', 'user__username']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['idea', 'user', 'content', 'is_reported', 'created_at']
    list_filter = ['is_reported', 'created_at']
    search_fields = ['content', 'idea__title', 'user__username']


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['idea', 'user', 'created_at']
    search_fields = ['idea__title', 'user__username']
