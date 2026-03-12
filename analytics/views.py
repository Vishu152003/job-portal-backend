from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta


# Custom permission class for admin role
class IsAdminRole:
    """Custom permission class to check if user has admin role"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == 'admin' or request.user.is_superuser or request.user.is_staff)
        )


def IsAdminPermission():
    """Function to return the permission class for use in @permission_classes"""
    return [IsAuthenticated, IsAdminRole]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def simple_dashboard(request):
    """Simple dashboard for non-admin users"""
    return Response({
        'message': 'Welcome to job portal'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def dashboard_stats(request):
    """Get overall dashboard statistics"""
    from jobs.models import Job
    from applications.models import Application
    from ideas.models import StartupIdea
    
    User = get_user_model()
    
    # User counts
    total_users = User.objects.count()
    total_seekers = User.objects.filter(role='seeker').count()
    total_recruiters = User.objects.filter(role='recruiter').count()
    total_admins = User.objects.filter(role='admin').count()
    active_users = User.objects.filter(is_active=True).count()
    blocked_users = User.objects.filter(is_blocked=True).count()
    
    # Job counts
    total_jobs = Job.objects.count()
    approved_jobs = Job.objects.filter(status='approved').count()
    pending_jobs = Job.objects.filter(status='pending').count()
    rejected_jobs = Job.objects.filter(status='rejected').count()
    
    # Application counts
    total_applications = Application.objects.count()
    
    # Idea counts
    total_ideas = StartupIdea.objects.count()
    approved_ideas = StartupIdea.objects.filter(status='approved').count()
    pending_ideas = StartupIdea.objects.filter(status='pending').count()
    rejected_ideas = StartupIdea.objects.filter(status='rejected').count()
    reported_ideas = StartupIdea.objects.filter(is_reported=True).count()
    
    return Response({
        'users': {
            'total': total_users,
            'seekers': total_seekers,
            'recruiters': total_recruiters,
            'admins': total_admins,
            'active': active_users,
            'blocked': blocked_users
        },
        'jobs': {
            'total': total_jobs,
            'approved': approved_jobs,
            'pending': pending_jobs,
            'rejected': rejected_jobs
        },
        'applications': {
            'total': total_applications
        },
        'ideas': {
            'total': total_ideas,
            'approved': approved_ideas,
            'pending': pending_ideas,
            'rejected': rejected_ideas,
            'reported': reported_ideas
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def user_analytics(request):
    """Get user analytics"""
    User = get_user_model()
    
    # Users by role
    users_by_role = User.objects.values('role').annotate(count=Count('id'))
    
    # Users by registration month
    six_months_ago = timezone.now() - timedelta(days=180)
    users_by_month = User.objects.filter(
        date_joined__gte=six_months_ago
    ).annotate(
        month=TruncMonth('date_joined')
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    # Blocked users
    blocked_users = User.objects.filter(is_blocked=True).count()
    
    # Active users (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    active_users = User.objects.filter(last_login__gte=thirty_days_ago).count()
    
    return Response({
        'users_by_role': list(users_by_role),
        'users_by_month': list(users_by_month),
        'blocked_users': blocked_users,
        'active_users': active_users
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def job_analytics(request):
    """Get job analytics"""
    from jobs.models import Job
    
    # Jobs by status
    jobs_by_status = Job.objects.values('status').annotate(count=Count('id'))
    
    # Jobs by type (using job_type, not category)
    jobs_by_type = Job.objects.values('job_type').annotate(count=Count('id'))
    
    # Jobs by location (using location field)
    jobs_by_location = Job.objects.values('location').annotate(count=Count('id')).order_by('-count')[:10]
    
    # Jobs by month
    six_months_ago = timezone.now() - timedelta(days=180)
    jobs_by_month = Job.objects.filter(
        created_at__gte=six_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    return Response({
        'jobs_by_status': list(jobs_by_status),
        'jobs_by_type': list(jobs_by_type),
        'jobs_by_location': list(jobs_by_location),
        'jobs_by_month': list(jobs_by_month)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def application_analytics(request):
    """Get application analytics"""
    from applications.models import Application
    
    # Applications by status
    applications_by_status = Application.objects.values('status').annotate(count=Count('id'))
    
    # Applications by month
    six_months_ago = timezone.now() - timedelta(days=180)
    applications_by_month = Application.objects.filter(
        applied_at__gte=six_months_ago
    ).annotate(
        month=TruncMonth('applied_at')
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    return Response({
        'applications_by_status': list(applications_by_status),
        'applications_by_month': list(applications_by_month)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def idea_analytics(request):
    from ideas.models import StartupIdea, Vote
    
    # Ideas by status
    ideas_by_status = StartupIdea.objects.values('status').annotate(count=Count('id'))
    
    # Ideas by category
    ideas_by_category = StartupIdea.objects.values('category').annotate(count=Count('id'))
    
    # Top voted ideas
    top_ideas = StartupIdea.objects.order_by('-vote_score')[:10]
    
    # Ideas by month
    twelve_months_ago = timezone.now() - timedelta(days=365)
    ideas_by_month = StartupIdea.objects.filter(
        created_at__gte=twelve_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    # Total votes
    total_upvotes = Vote.objects.filter(vote_type='up').count()
    total_downvotes = Vote.objects.filter(vote_type='down').count()
    
    return Response({
        'ideas_by_status': list(ideas_by_status),
        'ideas_by_category': list(ideas_by_category),
        'top_ideas': [{
            'id': idea.id,
            'title': idea.title,
            'vote_score': idea.vote_score,
            'upvotes': idea.upvotes,
            'downvotes': idea.downvotes,
            'views': idea.views
        } for idea in top_ideas],
        'ideas_by_month': list(ideas_by_month),
        'total_votes': {
            'upvotes': total_upvotes,
            'downvotes': total_downvotes
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def skill_demand_analytics(request):
    """Get skill demand analytics based on job requirements"""
    from jobs.models import Job
    from collections import Counter
    
    # Get all job skills
    all_skills = []
    jobs = Job.objects.filter(status='approved')
    for job in jobs:
        if job.skills:
            all_skills.extend(job.skills)
    
    skill_counts = Counter(all_skills).most_common(30)
    
    # Skills by job type
    skills_by_type = {}
    for job_type in ['full_time', 'part_time', 'contract', 'internship']:
        type_jobs = jobs.filter(job_type=job_type)
        type_skills = []
        for job in type_jobs:
            if job.skills:
                type_skills.extend(job.skills)
        # Format display name
        display_name = job_type.replace('_', '-').title()
        skills_by_type[display_name] = Counter(type_skills).most_common(10)
    
    return Response({
        'top_demanded_skills': [{'skill': s[0], 'count': s[1]} for s in skill_counts],
        'skills_by_job_type': {
            k: [{'skill': s[0], 'count': s[1]} for s in v] 
            for k, v in skills_by_type.items()
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def home_stats(request):
    """Get public stats for home page - no authentication required"""
    from jobs.models import Job
    from applications.models import Application
    from ideas.models import StartupIdea
    from accounts.models import Company
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Public stats (show all jobs for visibility)
    total_jobs = Job.objects.count()
    total_companies = Company.objects.count()
    total_candidates = User.objects.filter(role='seeker').count()
    total_ideas = StartupIdea.objects.count()
    
    return Response({
        'jobs': total_jobs,
        'companies': total_companies,
        'candidates': total_candidates,
        'ideas': total_ideas
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def featured_jobs(request):
    """Get featured/latest jobs for home page (all statuses)"""
    from jobs.models import Job
    from jobs.serializers import JobListSerializer
    
    # Get latest jobs (limit to 6) - show all for home page visibility
    jobs = Job.objects.order_by('-created_at')[:6]
    serializer = JobListSerializer(jobs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def featured_companies(request):
    """Get companies with logos for home page"""
    from accounts.models import Company
    from django.conf import settings
    
    companies = Company.objects.all()[:10]
    
    return Response([{
        'id': c.id,
        'name': c.name,
        'logo': request.build_absolute_uri(c.logo.url) if c.logo else None,
        'industry': c.industry,
        'is_verified': c.is_verified
    } for c in companies])
