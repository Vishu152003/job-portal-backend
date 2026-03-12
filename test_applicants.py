import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from applications.models import Application
from jobs.models import Job
from accounts.models import User

print("=== Applications Check ===")
print(f"Total Applications: {Application.objects.count()}")

print("\n=== All Applications ===")
for app in Application.objects.all():
    print(f"  - ID: {app.id}, Job: {app.job.title}, Seeker: {app.seeker.username}, Status: {app.status}")

print("\n=== Jobs with Applications ===")
jobs_with_apps = Job.objects.annotate(app_count=Count('applications')).filter(app_count__gt=0)
for job in jobs_with_apps:
    print(f"  - Job: {job.title}, Recruiter: {job.recruiter.username}, Applications: {job.applications.count()}")

print("\n=== Recruiter Users ===")
for user in User.objects.filter(role='recruiter'):
    jobs = Job.objects.filter(recruiter=user)
    print(f"  - {user.username}: {jobs.count()} jobs")
    for job in jobs:
        apps = Application.objects.filter(job=job).count()
        print(f"      Job: {job.title}, Applications: {apps}")
