from django.db import models
from django.conf import settings


class Job(models.Model):
    """Job listing model"""
    
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_jobs'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    skills = models.JSONField(default=list, blank=True)
    location = models.CharField(max_length=200)
    is_remote = models.BooleanField(default=False)
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    salary_currency = models.CharField(max_length=10, default='USD')
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    experience_level = models.CharField(max_length=50, blank=True)
    application_deadline = models.DateField(null=True, blank=True)
    positions = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'jobs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recruiter.username}"
    
    @property
    def is_active(self):
        return self.status == 'approved'


class JobSkill(models.Model):
    """Skills associated with jobs"""
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='job_skills')
    skill = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'job_skills'
        unique_together = ['job', 'skill']
    
    def __str__(self):
        return f"{self.job.title} - {self.skill}"


class SavedJob(models.Model):
    """Saved jobs by job seekers"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_jobs'
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='saved_by'
    )
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'saved_jobs'
        unique_together = ['user', 'job']
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"
