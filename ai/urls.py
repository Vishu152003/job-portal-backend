from django.urls import path
from .views import match_resume, recommend_jobs, analyze_idea, parse_resume, job_match_details

urlpatterns = [
    path('match-resume/', match_resume, name='match_resume'),
    path('recommend-jobs/', recommend_jobs, name='recommend_jobs'),
    path('analyze-idea/', analyze_idea, name='analyze_idea'),
    path('parse-resume/', parse_resume, name='parse_resume'),
    path('job-match-details/', job_match_details, name='job_match_details'),
]
