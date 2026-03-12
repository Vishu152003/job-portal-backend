from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with roles"""
    
    ROLE_CHOICES = [
        ('seeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='seeker')
    is_blocked = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'users'
    
    @property
    def is_seeker(self):
        return self.role == 'seeker' or self.is_superuser
    
    @property
    def is_recruiter(self):
        return self.role == 'recruiter' or self.is_superuser
    
    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser


class Profile(models.Model):
    """User profile for job seekers - Comprehensive job portal profile"""
    
    # Basic Info
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    
    # Bio & Summary
    profile_summary = models.TextField(blank=True, help_text="Brief summary about yourself")
    bio = models.TextField(blank=True)
    
    # Social Links
    linkedin_url = models.URLField(blank=True, help_text="Your LinkedIn profile URL")
    github_url = models.URLField(blank=True, help_text="Your GitHub profile URL")
    portfolio_url = models.URLField(blank=True, help_text="Your portfolio website URL")
    
    # Skills (stored as JSON array)
    skills = models.JSONField(default=list, blank=True, help_text="List of your skills")
    
    # Languages
    languages = models.JSONField(default=list, blank=True, help_text="Languages you know")
    
    # Resume
    resume = models.FileField(upload_to='resumes/', blank=True, null=True, help_text="Upload your resume (PDF)")
    resume_text = models.TextField(blank=True, help_text="Extracted text from resume")
    
    # Employment Details
    is_fresher = models.BooleanField(default=True, help_text="Are you a fresher?")
    current_company = models.CharField(max_length=200, blank=True)
    current_job_title = models.CharField(max_length=200, blank=True)
    current_salary = models.CharField(max_length=50, blank=True, help_text="Current CTC")
    expected_salary = models.CharField(max_length=50, blank=True, help_text="Expected CTC")
    
    # Employment History (stored as JSON array of dictionaries)
    employment_history = models.JSONField(default=list, blank=True, help_text="List of previous jobs")
    
    # Internships (stored as JSON array)
    internships = models.JSONField(default=list, blank=True, help_text="List of internships done")
    
    # Education (stored as JSON array)
    education = models.JSONField(default=list, blank=True, help_text="Educational background")
    
    # Projects (stored as JSON array)
    projects = models.JSONField(default=list, blank=True, help_text="Projects you've worked on")
    
    # Accomplishments/Awards
    accomplishments = models.JSONField(default=list, blank=True, help_text="Awards and achievements")
    
    # Job Preferences
    preferred_job_type = models.JSONField(default=list, blank=True, help_text="Full-time, Part-time, Contract, etc.")
    preferred_locations = models.JSONField(default=list, blank=True, help_text="Preferred work locations")
    preferred_industry = models.CharField(max_length=100, blank=True, help_text="Preferred industry")
    willing_to_relocate = models.BooleanField(default=False)
    
    # Availability
    notice_period = models.CharField(max_length=50, blank=True, help_text="Notice period")
    available_from = models.DateField(null=True, blank=True)
    
    # Location
    current_location = models.CharField(max_length=200, blank=True)
    hometown = models.CharField(max_length=200, blank=True)
    
    # Personal Details
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    marital_status = models.CharField(max_length=20, blank=True)
    
    # Family Details (optional)
    father_name = models.CharField(max_length=200, blank=True)
    mother_name = models.CharField(max_length=200, blank=True)
    
    # Status
    is_profile_complete = models.BooleanField(default=False)
    profile_views = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'profiles'
    
    def __str__(self):
        return f"{self.user.username}'s profile"


class Company(models.Model):
    """Company profile for recruiters"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    founded_year = models.IntegerField(null=True, blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'companies'
    
    def __str__(self):
        return self.name
