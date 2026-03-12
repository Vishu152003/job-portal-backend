# Generated manually to add new profile fields

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Add new fields to Profile (only ADD, no REMOVE to avoid errors)
        migrations.AddField(
            model_name='profile',
            name='accomplishments',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='profile',
            name='available_from',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='current_company',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='profile',
            name='current_job_title',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='profile',
            name='current_location',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='profile',
            name='current_salary',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='profile',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='employment_history',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='profile',
            name='expected_salary',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='profile',
            name='father_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='profile',
            name='gender',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='profile',
            name='github_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='hometown',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='profile',
            name='internships',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_fresher',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_profile_complete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='languages',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='profile',
            name='linkedin_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='marital_status',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='profile',
            name='mother_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='profile',
            name='notice_period',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='profile',
            name='portfolio_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='preferred_industry',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='profile',
            name='preferred_job_type',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='profile',
            name='preferred_locations',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='profile',
            name='profile_photo',
            field=models.ImageField(blank=True, null=True, upload_to='profile_photos/'),
        ),
        migrations.AddField(
            model_name='profile',
            name='profile_summary',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='profile_views',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='projects',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='profile',
            name='resume_text',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='willing_to_relocate',
            field=models.BooleanField(default=False),
        ),
        # Add is_verified to Company
        migrations.AddField(
            model_name='company',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]
