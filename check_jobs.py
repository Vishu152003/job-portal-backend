import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from jobs.models import Job
from accounts.models import User

print("=== Jobs Check ===")
print(f"Total Jobs: {Job.objects.count()}")
print(f"Total Users: {User.objects.count()}")

print("\n=== Sample Jobs ===")
for j in Job.objects.all()[:5]:
    print(f"  - ID: {j.id}, Title: {j.title}, Status: {j.status}, Recruiter: {j.recruiter.username}")
