from django.contrib import admin
from .models import Job, JobSkill


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'recruiter', 'status', 'job_type', 'location', 'created_at']
    list_filter = ['status', 'job_type', 'is_remote', 'created_at']
    search_fields = ['title', 'description', 'location']
    ordering = ['-created_at']
    readonly_fields = ['views', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'requirements', 'skills')
        }),
        ('Job Details', {
            'fields': ('location', 'is_remote', 'salary_min', 'salary_max', 
                      'salary_currency', 'job_type', 'experience_level')
        }),
        ('Application Info', {
            'fields': ('application_deadline', 'positions')
        }),
        ('Status', {
            'fields': ('status', 'rejection_reason', 'views')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(JobSkill)
class JobSkillAdmin(admin.ModelAdmin):
    list_display = ['job', 'skill']
    search_fields = ['skill', 'job__title']
