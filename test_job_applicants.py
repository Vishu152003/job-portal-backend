import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from jobs.models import Job
from applications.serializers import RecruiterApplicationSerializer

print("=== Testing Job Applicants API ===")

# Get recruiter users
from accounts.models import User
recruiters = User.objects.filter(role='recruiter')
print(f"\nRecruiters: {list(recruiters.values_list('username', flat=True))}")

for recruiter in recruiters:
    print(f"\n--- Recruiter: {recruiter.username} ---")
    jobs = Job.objects.filter(recruiter=recruiter)
    print(f"Jobs posted: {jobs.count()}")
    
    for job in jobs:
        apps = job.applications.all()
        print(f"  Job: {job.title} (ID: {job.id}) - {apps.count()} applications")
        
        if apps.exists():
            # Test the serializer
            serializer = RecruiterApplicationSerializer(apps, many=True)
            data = serializer.data
            print(f"  Serialized {len(data)} applications")
            if data:
                print(f"  First app: seeker_name={data[0].get('seeker_name')}, seeker_email={data[0].get('seeker_email')}")
