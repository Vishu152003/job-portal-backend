y#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from accounts.models import User
from jobs.models import Job
from applications.models import Application
from ideas.models import StartupIdea

print("=== Database Statistics ===")
print(f"Total Users: {User.objects.count()}")
print(f"  - Admins: {User.objects.filter(role='admin').count()}")
print(f"  - Recruiters: {User.objects.filter(role='recruiter').count()}")
print(f"  - Seekers: {User.objects.filter(role='seeker').count()}")
print(f"Total Jobs: {Job.objects.count()}")
print(f"  - Approved: {Job.objects.filter(status='approved').count()}")
print(f"  - Pending: {Job.objects.filter(status='pending').count()}")
print(f"Total Applications: {Application.objects.count()}")
print(f"Total Ideas: {StartupIdea.objects.count()}")
print(f"  - Approved: {StartupIdea.objects.filter(status='approved').count()}")
print(f"  - Pending: {StartupIdea.objects.filter(status='pending').count()}")

print("\n=== Sample Users ===")
for u in User.objects.all()[:5]:
    print(f"  - {u.username} | role: {u.role} | is_admin: {u.is_admin}")
