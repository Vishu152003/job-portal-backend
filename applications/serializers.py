from rest_framework import serializers
from .models import Application, ApplicationStatusHistory


class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer for Application model"""
    
    seeker_name = serializers.CharField(source='seeker.username', read_only=True)
    seeker_email = serializers.CharField(source='seeker.email', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.recruiter.company.name', read_only=True)
    job_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = [
            'id', 'job', 'job_title', 'company_name', 'job_details', 'seeker', 'seeker_name',
            'seeker_email', 'resume', 'cover_letter', 'status', 'match_score',
            'notes', 'applied_at', 'updated_at'
        ]
        read_only_fields = ['id', 'seeker', 'status', 'match_score', 'applied_at', 'updated_at']
    
    def get_job_details(self, obj):
        try:
            company_name = obj.job.recruiter.company.name if hasattr(obj.job.recruiter, 'company') else 'Company'
        except:
            company_name = 'Company'
        return {
            'id': obj.job.id,
            'title': obj.job.title,
            'company_name': company_name,
            'location': obj.job.location,
            'job_type': obj.job.job_type,
        }


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating applications"""
    
    class Meta:
        model = Application
        fields = ['job', 'resume', 'cover_letter']
    
    def create(self, validated_data):
        validated_data['seeker'] = self.context['request'].user
        
        # Check if user has already applied
        if Application.objects.filter(
            job=validated_data['job'],
            seeker=validated_data['seeker']
        ).exists():
            raise serializers.ValidationError(
                {"error": "You have already applied for this job"}
            )
        
        # Check if job exists and is approved
        if validated_data['job'].status != 'approved':
            raise serializers.ValidationError(
                {"error": "Cannot apply for unapproved jobs"}
            )
        
        return super().create(validated_data)


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating application status"""
    
    class Meta:
        model = Application
        fields = ['status', 'notes']


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for application status history"""
    
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)
    
    class Meta:
        model = ApplicationStatusHistory
        fields = ['id', 'status', 'notes', 'changed_by', 'changed_by_name', 'changed_at']
        read_only_fields = fields


class RecruiterApplicationSerializer(serializers.ModelSerializer):
    """Serializer for recruiters to view applications - includes full applicant details"""
    
    seeker_name = serializers.SerializerMethodField()
    seeker_email = serializers.SerializerMethodField()
    seeker_skills = serializers.SerializerMethodField()
    seeker_experience = serializers.SerializerMethodField()
    seeker_profile_photo = serializers.SerializerMethodField()
    seeker_phone = serializers.SerializerMethodField()
    seeker_location = serializers.SerializerMethodField()
    seeker_linkedin = serializers.SerializerMethodField()
    seeker_github = serializers.SerializerMethodField()
    seeker_portfolio = serializers.SerializerMethodField()
    resume_url = serializers.SerializerMethodField()
    job_title = serializers.CharField(source='job.title', read_only=True)
    match_breakdown = serializers.SerializerMethodField()
    conversation_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = [
            'id', 'job', 'job_title', 'seeker', 'seeker_name', 'seeker_email',
            'seeker_skills', 'seeker_experience', 'seeker_profile_photo', 
            'seeker_phone', 'seeker_location', 'seeker_linkedin', 'seeker_github',
            'seeker_portfolio', 'resume', 'resume_url',
            'cover_letter', 'status', 'match_score', 'match_breakdown', 'notes', 'applied_at', 'updated_at',
            'conversation_id'
        ]
        read_only_fields = fields
    
    def get_conversation_id(self, obj):
        """Get the conversation ID if it exists for this application"""
        try:
            from chat.models import Conversation
            conversation = Conversation.objects.filter(application=obj).first()
            return conversation.id if conversation else None
        except:
            return None
    
    def get_seeker_name(self, obj):
        try:
            profile = obj.seeker.profile
            return f"{profile.first_name} {profile.last_name}".strip() or obj.seeker.username
        except:
            return obj.seeker.username
    
    def get_seeker_email(self, obj):
        return obj.seeker.email
    
    def get_seeker_skills(self, obj):
        try:
            return obj.seeker.profile.skills or []
        except:
            return []
    
    def get_seeker_experience(self, obj):
        try:
            employment_history = obj.seeker.profile.employment_history or []
            if employment_history:
                return f"{len(employment_history)} position(s)"
            if obj.seeker.profile.is_fresher:
                return "Fresher"
            return ''
        except:
            return ''
    
    def get_seeker_profile_photo(self, obj):
        try:
            if obj.seeker.profile.profile_photo:
                return obj.seeker.profile.profile_photo.url
        except:
            pass
        return None
    
    def get_seeker_phone(self, obj):
        try:
            return obj.seeker.profile.phone or ''
        except:
            return ''
    
    def get_seeker_location(self, obj):
        try:
            return obj.seeker.profile.current_location or ''
        except:
            return ''
    
    def get_seeker_linkedin(self, obj):
        try:
            return obj.seeker.profile.linkedin_url or ''
        except:
            return ''
    
    def get_seeker_github(self, obj):
        try:
            return obj.seeker.profile.github_url or ''
        except:
            return ''
    
    def get_seeker_portfolio(self, obj):
        try:
            return obj.seeker.profile.portfolio_url or ''
        except:
            return ''
    
    def get_resume_url(self, obj):
        # First try to get resume from the application itself
        try:
            if obj.resume:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.resume.url)
                return obj.resume.url
        except:
            pass
        
        # Fallback: try to get resume from the seeker's profile
        try:
            if obj.seeker.profile.resume:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.seeker.profile.resume.url)
                return obj.seeker.profile.resume.url
        except:
            pass
        
        return None
    
    def get_match_breakdown(self, obj):
        """Calculate detailed match breakdown for the applicant"""
        try:
            profile = obj.seeker.profile
            
            # Skill Match (40%)
            job_skills = set(obj.job.skills or [])
            seeker_skills = set(profile.skills or [])
            
            skill_match = 0
            matched_skills = []
            if job_skills:
                matched = job_skills.intersection(seeker_skills)
                skill_match = round((len(matched) / len(job_skills)) * 100, 1)
                matched_skills = list(matched)
            
            # Experience Match (30%)
            job_experience = (obj.job.experience_level or "").lower()
            seeker_experience = len(profile.employment_history or [])
            
            if job_experience in ['senior', 'lead', 'principal']:
                experience_score = min(seeker_experience / 5, 1)
            elif job_experience in ['mid', 'intermediate']:
                experience_score = min(seeker_experience / 3, 1)
            else:
                experience_score = min(seeker_experience / 1, 1)
            
            experience_match = round(experience_score * 100, 1)
            
            # Education Match (20%)
            job_requirements = (obj.job.requirements or "").lower()
            education = profile.education or []
            
            education_keywords = ['bachelor', 'master', 'phd', 'degree', 'diploma']
            education_match = 0
            
            for edu in education:
                edu_str = str(edu).lower()
                if any(keyword in edu_str for keyword in education_keywords):
                    education_match = 100
                    break
            
            # If job requires specific education, give full weight
            if any(keyword in job_requirements for keyword in education_keywords):
                pass  # Already at 100%
            else:
                education_match = education_match / 2  # Lower weight if not specified
            
            education_match = round(education_match, 1)
            
            # Profile Completeness (10%)
            profile_fields = [
                profile.phone,
                profile.bio,
                profile.current_location,
                profile.resume,
                profile.skills,
                profile.education,
                profile.employment_history,
            ]
            
            filled_fields = sum(1 for field in profile_fields if field)
            completeness = round((filled_fields / len(profile_fields)) * 100, 1)
            
            return {
                'skill_match': skill_match,
                'matched_skills': matched_skills,
                'required_skills': list(job_skills),
                'experience_match': experience_match,
                'experience_years': seeker_experience,
                'education_match': education_match,
                'profile_completeness': completeness,
                'overall_score': obj.match_score or 0
            }
        except Exception as e:
            return {
                'skill_match': 0,
                'matched_skills': [],
                'required_skills': [],
                'experience_match': 0,
                'experience_years': 0,
                'education_match': 0,
                'profile_completeness': 0,
                'overall_score': obj.match_score or 0
            }
