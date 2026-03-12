from django.urls import path
from .views import (
    dashboard_stats, user_analytics, job_analytics,
    application_analytics, idea_analytics, skill_demand_analytics,
    home_stats, featured_jobs, featured_companies
)

urlpatterns = [
    path('dashboard/', dashboard_stats, name='dashboard_stats'),
    path('users/', user_analytics, name='user_analytics'),
    path('jobs/', job_analytics, name='job_analytics'),
    path('applications/', application_analytics, name='application_analytics'),
    path('ideas/', idea_analytics, name='idea_analytics'),
    path('skills/', skill_demand_analytics, name='skill_demand_analytics'),
    path('home-stats/', home_stats, name='home_stats'),
    path('featured-jobs/', featured_jobs, name='featured_jobs'),
    path('featured-companies/', featured_companies, name='featured_companies'),
]
