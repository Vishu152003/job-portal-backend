import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from jobs.models import Job
from accounts.models import User

# Simulate the view's get_queryset
def test_my_jobs(user):
    print(f"\n--- Testing my_jobs for: {user.username} (role: {user.role}) ---")
    
    if user.role == 'recruiter':
        jobs = Job.objects.filter(recruiter=user)
        print(f"Jobs found: {jobs.count()}")
        for job in jobs:
            apps = job.applications.count()
            print(f"  - {job.title}: {apps} applications")
    else:
        print(f"User is not a recruiter, role: {user.role}")

# Test with testuser123 (recruiter)
user = User.objects.get(username='testuser123')
test_my_jobs(user)

# Test with johndoe (recruiter)
user = User.objects.get(username='johndoe')
test_my_jobs(user)

# Test with nehal (recruiter)
user = User.objects.get(username='nehal')
test_my_jobs(user)
