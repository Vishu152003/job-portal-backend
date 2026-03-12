from django.db import models
from django.conf import settings
from jobs.models import Job


class Application(models.Model):
    """Job application model"""
    
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview'),
        ('rejected', 'Rejected'),
        ('offered', 'Offered'),
        ('hired', 'Hired'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    seeker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    resume = models.FileField(upload_to='applications/resumes/', blank=True, null=True)
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    match_score = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'applications'
        ordering = ['-applied_at']
        unique_together = ['job', 'seeker']
    
    def calculate_match_score(self):
        """Calculate match score based on skills, experience, education, and profile completeness"""
        score = 0
        total_weight = 0

        # Skill Match (40% weight)
        job_skills = set(self.job.skills or [])
        seeker_skills = set(self.seeker.profile.skills or [])

        if job_skills:
            skill_match = len(job_skills.intersection(seeker_skills)) / len(job_skills)
            score += skill_match * 40
            total_weight += 40

        # Experience Match (30% weight)
        job_experience = self.job.experience_level or ""
        seeker_experience = len(self.seeker.profile.employment_history or [])

        # Simple experience matching - more experience is better
        if job_experience.lower() in ['senior', 'lead', 'principal']:
            experience_score = min(seeker_experience / 5, 1)  # Max at 5+ years
        elif job_experience.lower() in ['mid', 'intermediate']:
            experience_score = min(seeker_experience / 3, 1)  # Max at 3+ years
        else:  # junior, entry
            experience_score = min(seeker_experience / 1, 1)  # Max at 1+ years

        score += experience_score * 30
        total_weight += 30

        # Education Match (20% weight)
        job_requirements = (self.job.requirements or "").lower()
        seeker_education = self.seeker.profile.education or []

        education_keywords = ['bachelor', 'master', 'phd', 'degree', 'diploma']
        education_score = 0

        for edu in seeker_education:
            edu_str = str(edu).lower()
            if any(keyword in edu_str for keyword in education_keywords):
                education_score = 1
                break

        # Check if job requires specific education
        if any(keyword in job_requirements for keyword in education_keywords):
            score += education_score * 20
        else:
            score += education_score * 10  # Lower weight if not specified

        total_weight += 20

        # Profile Completeness (10% weight)
        profile_fields = [
            self.seeker.profile.phone,
            self.seeker.profile.bio,
            self.seeker.profile.current_location,
            self.seeker.profile.resume,
            self.seeker.profile.skills,
            self.seeker.profile.education,
            self.seeker.profile.employment_history,
        ]

        filled_fields = sum(1 for field in profile_fields if field)
        completeness = filled_fields / len(profile_fields)
        score += completeness * 10
        total_weight += 10

        # Calculate final score
        if total_weight > 0:
            final_score = (score / total_weight) * 100
        else:
            final_score = 0

        return round(final_score, 2)

    def save(self, *args, **kwargs):
        """Override save to calculate match score"""
        if not self.match_score:
            self.match_score = self.calculate_match_score()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.seeker.username} - {self.job.title}"


class ApplicationStatusHistory(models.Model):
    """Track application status changes"""
    
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'application_status_history'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.application.id} - {self.status}"
