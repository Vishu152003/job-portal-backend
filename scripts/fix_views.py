import re

# Read the file
with open('backend/applications/views.py', 'r') as f:
    content = f.read()

# Find and replace the job_applicants method body
old_code = '''            applications = Application.objects.filter(job__id=job_id, job__recruiter=request.user).select_related('seeker', 'job', 'job__recruiter').order_by('-match_score')
            serializer = RecruiterApplicationSerializer(applications, many=True, context={'request': request})
            return Response(serializer.data)'''

new_code = '''            applications = Application.objects.filter(job__id=job_id, job__recruiter=request.user).select_related('seeker', 'job', 'job__recruiter').order_by('-match_score')
            
            # Increment profile_views when recruiter views applicants
            from accounts.models import Profile
            for application in applications:
                try:
                    profile = application.seeker.profile
                    profile.profile_views += 1
                    profile.save(update_fields=['profile_views'])
                except Exception:
                    pass
            
            serializer = RecruiterApplicationSerializer(applications, many=True, context={'request': request})
            return Response(serializer.data)'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('backend/applications/views.py', 'w') as f:
        f.write(content)
    print('File updated successfully')
else:
    print('Pattern not found')
