from rest_framework import serializers
from .models import Job, JobSkill, SavedJob


class JobSerializer(serializers.ModelSerializer):
    """Serializer for Job model"""
    
    recruiter_name = serializers.CharField(source='recruiter.username', read_only=True)
    company_name = serializers.CharField(source='recruiter.company.name', read_only=True)
    application_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'recruiter', 'recruiter_name', 'company_name', 'title', 'description',
            'requirements', 'skills', 'location', 'is_remote', 'salary_min', 'salary_max',
            'salary_currency', 'job_type', 'experience_level', 'application_deadline',
            'positions', 'status', 'rejection_reason', 'views', 'application_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'recruiter', 'status', 'rejection_reason', 'views', 'created_at', 'updated_at']
    
    def get_application_count(self, obj):
        return obj.applications.count()
    
    def create(self, validated_data):
        validated_data['recruiter'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Only allow updates if status is pending or rejected
        if instance.status not in ['pending', 'rejected']:
            if set(validated_data.keys()) - {'application_deadline', 'positions'}:
                raise serializers.ValidationError(
                    {"error": "Cannot update job after it's been approved"}
                )
        return super().update(instance, validated_data)


class JobListSerializer(serializers.ModelSerializer):
    """Simplified serializer for job listings"""
    
    recruiter_name = serializers.CharField(source='recruiter.username', read_only=True)
    company_name = serializers.CharField(source='recruiter.company.name', read_only=True)
    application_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company_name', 'recruiter_name', 'location', 'is_remote',
            'salary_min', 'salary_max', 'salary_currency', 'job_type', 'skills',
            'description', 'requirements', 'experience_level',
            'application_deadline', 'positions', 'status', 'application_count',
            'created_at'
        ]
        read_only_fields = fields
    
    def get_application_count(self, obj):
        return obj.applications.count()


class JobCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating jobs"""
    
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'requirements', 'skills', 'location',
            'is_remote', 'salary_min', 'salary_max', 'salary_currency',
            'job_type', 'experience_level', 'application_deadline', 'positions'
        ]
    
    def create(self, validated_data):
        # Jobs created by recruiters need admin approval first
        recruiter = self.context['request'].user
        job = Job.objects.create(
            recruiter=recruiter,
            status='pending',
            title=validated_data.get('title'),
            description=validated_data.get('description'),
            requirements=validated_data.get('requirements', ''),
            skills=validated_data.get('skills', []),
            location=validated_data.get('location', ''),
            is_remote=validated_data.get('is_remote', False),
            salary_min=validated_data.get('salary_min'),
            salary_max=validated_data.get('salary_max'),
            salary_currency=validated_data.get('salary_currency', 'USD'),
            job_type=validated_data.get('job_type', 'full_time'),
            experience_level=validated_data.get('experience_level', ''),
            application_deadline=validated_data.get('application_deadline'),
            positions=validated_data.get('positions', 1),
        )
        return job


class JobApprovalSerializer(serializers.ModelSerializer):
    """Serializer for job approval/rejection"""
    
    class Meta:
        model = Job
        fields = ['status', 'rejection_reason']
    
    def validate(self, attrs):
        if self.instance.status != 'pending':
            raise serializers.ValidationError(
                {"error": "Can only approve or reject pending jobs"}
            )
        return attrs


class SavedJobSerializer(serializers.ModelSerializer):
    """Serializer for SavedJob model"""

    job_id = serializers.IntegerField(source='job.id', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_company = serializers.CharField(source='job.company_name', read_only=True)
    job_location = serializers.CharField(source='job.location', read_only=True)
    job_type = serializers.CharField(source='job.job_type', read_only=True)
    salary = serializers.SerializerMethodField()

    class Meta:
        model = SavedJob
        fields = ['id', 'job', 'job_id', 'job_title', 'job_company', 'job_location', 'job_type', 'salary', 'saved_at']
        read_only_fields = ['id', 'saved_at']

    def get_salary(self, obj):
        job = obj.job
        if job.salary_min and job.salary_max:
            return f"${job.salary_min} - ${job.salary_max}"
        return 'Negotiable'
