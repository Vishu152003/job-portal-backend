from django.contrib import admin
from .models import Application, ApplicationStatusHistory


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['job', 'seeker', 'status', 'match_score', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['job__title', 'seeker__username']
    ordering = ['-applied_at']
    readonly_fields = ['applied_at', 'updated_at']


@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['application', 'status', 'changed_by', 'changed_at']
    list_filter = ['status', 'changed_at']
    search_fields = ['application__job__title', 'changed_by__username']
    ordering = ['-changed_at']
