import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from jobs.models import Job
from jobs.serializers import JobListSerializer

print("=== Testing Featured Jobs API ===")
jobs = Job.objects.order_by('-created_at')[:6]
print(f"Jobs found: {jobs.count()}")

for job in jobs:
    print(f"\nJob: {job.title}")
    print(f"  Recruiter: {job.recruiter.username}")
    print(f"  Has company: {hasattr(job.recruiter, 'company')}")
    if hasattr(job.recruiter, 'company'):
        company = job.recruiter.company
        print(f"  Company: {company.name if company else 'None'}")

print("\n=== Serializing ===")
serializer = JobListSerializer(jobs, many=True)
data = serializer.data
print(f"Serialized {len(data)} jobs")
if data:
    print(f"First job: {data[0]}")
