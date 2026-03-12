from django.core.management.base import BaseCommand
from django.db import connection
from accounts.models import Profile

class Command(BaseCommand):
    help = 'Fix invalid JSON data in Profile model'

    def handle(self, *args, **options):
        profiles = Profile.objects.all()
        
        for profile in profiles:
            fixed = False
            
            # Fix skills
            if profile.skills is None or profile.skills == '' or profile.skills == 'null':
                profile.skills = []
                fixed = True
            
            # Fix education
            if profile.education is None or profile.education == '' or profile.education == 'null':
                profile.education = []
                fixed = True
            
            # Fix employment_history
            if profile.employment_history is None or profile.employment_history == '' or profile.employment_history == 'null':
                profile.employment_history = []
                fixed = True
            
            # Fix internships
            if profile.internships is None or profile.internships == '' or profile.internships == 'null':
                profile.internships = []
                fixed = True
            
            # Fix projects
            if profile.projects is None or profile.projects == '' or profile.projects == 'null':
                profile.projects = []
                fixed = True
            
            # Fix accomplishments
            if profile.accomplishments is None or profile.accomplishments == '' or profile.accomplishments == 'null':
                profile.accomplishments = []
                fixed = True
            
            # Fix languages
            if profile.languages is None or profile.languages == '' or profile.languages == 'null':
                profile.languages = []
                fixed = True
            
            # Fix preferred_job_type
            if profile.preferred_job_type is None or profile.preferred_job_type == '' or profile.preferred_job_type == 'null':
                profile.preferred_job_type = []
                fixed = True
            
            # Fix preferred_locations
            if profile.preferred_locations is None or profile.preferred_locations == '' or profile.preferred_locations == 'null':
                profile.preferred_locations = []
                fixed = True
            
            if fixed:
                profile.save()
                self.stdout.write(f'Fixed profile: {profile.user.username}')
        
        self.stdout.write(self.style.SUCCESS('Successfully fixed all JSON fields'))
