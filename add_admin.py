#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from accounts.models import User
from jobs.models import Job
from ideas.models import StartupIdea

# Create admin user if not exists
admin_username = 'admin'
if not User.objects.filter(username=admin_username).exists():
    admin = User.objects.create_superuser(
        username=admin_username,
        email='admin@jobportal.com',
        password='admin123',
        first_name='System',
        last_name='Admin',
        role='admin'
    )
    print(f"Created admin user: {admin_username}")
else:
    admin = User.objects.get(username=admin_username)
    # Ensure role is admin
    if admin.role != 'admin':
        admin.role = 'admin'
        admin.save()
        print(f"Updated {admin_username} role to admin")
    else:
        print(f"Admin user already exists: {admin_username}")

# Add some sample jobs if none exist
if Job.objects.count() < 3:
    recruiters = User.objects.filter(role='recruiter')
    if recruiters.exists():
        recruiter = recruiters.first()
        jobs_data = [
            {'title': 'Senior Python Developer', 'description': 'We are looking for an experienced Python developer...', 'location': 'Remote', 'job_type': 'full_time'},
            {'title': 'Frontend Developer', 'description': 'Join our team as a frontend developer...', 'location': 'Mumbai', 'job_type': 'full_time'},
            {'title': 'UI/UX Designer', 'description': 'Create beautiful user interfaces...', 'location': 'Delhi', 'job_type': 'full_time'},
        ]
        for j in jobs_data:
            if not Job.objects.filter(title=j['title']).exists():
                Job.objects.create(
                    recruiter=recruiter,
                    title=j['title'],
                    description=j['description'],
                    location=j['location'],
                    job_type=j['job_type'],
                    status='approved',
                    skills=['Python', 'JavaScript', 'React']
                )
                print(f"Created job: {j['title']}")

# Add some sample ideas if none exist
if StartupIdea.objects.count() < 3:
    seekers = User.objects.filter(role='seeker')
    if seekers.exists():
        seeker = seekers.first()
        ideas_data = [
            {'title': 'Food Delivery App', 'problem_statement': 'People want fast food delivery', 'solution': 'A mobile app for food delivery', 'target_audience': 'Urban consumers', 'category': 'food'},
            {'title': 'EdTech Platform', 'problem_statement': 'Online learning needs improvement', 'solution': 'Interactive learning platform', 'target_audience': 'Students', 'category': 'education'},
            {'title': 'Health Tracker', 'problem_statement': 'People need to track health', 'solution': 'Wearable health monitoring', 'target_audience': 'Health conscious people', 'category': 'healthcare'},
        ]
        for i in ideas_data:
            if not StartupIdea.objects.filter(title=i['title']).exists():
                StartupIdea.objects.create(
                    user=seeker,
                    title=i['title'],
                    problem_statement=i['problem_statement'],
                    solution=i['solution'],
                    target_audience=i['target_audience'],
                    category=i['category'],
                    status='approved'
                )
                print(f"Created idea: {i['title']}")

print("\n=== Updated Database Statistics ===")
print(f"Total Users: {User.objects.count()}")
print(f"  - Admins: {User.objects.filter(role='admin').count()}")
print(f"  - Recruiters: {User.objects.filter(role='recruiter').count()}")
print(f"  - Seekers: {User.objects.filter(role='seeker').count()}")
print(f"Total Jobs: {Job.objects.count()}")
print(f"Total Ideas: {StartupIdea.objects.count()}")
print("\nAdmin login credentials:")
print("  Username: admin")
print("  Password: admin123")
