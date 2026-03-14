from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Profile, Company
import json

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_blocked', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'role', 'first_name', 'last_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        
        # Create profile or company based on role
        if user.role == 'seeker':
            Profile.objects.create(user=user)
        elif user.role == 'recruiter':
            Company.objects.create(user=user)
        
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """Comprehensive Serializer for Profile model - Job Seeker Profile"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    # Override JSON fields to handle both string and list
    skills = serializers.JSONField(required=False, default=list)
    languages = serializers.JSONField(required=False, default=list)
    education = serializers.JSONField(required=False, default=list)
    projects = serializers.JSONField(required=False, default=list)
    accomplishments = serializers.JSONField(required=False, default=list)
    employment_history = serializers.JSONField(required=False, default=list)
    internships = serializers.JSONField(required=False, default=list)
    preferred_job_type = serializers.JSONField(required=False, default=list)
    preferred_locations = serializers.JSONField(required=False, default=list)
    
    class Meta:
        model = Profile
        fields = [
            # User info
            'id', 'username', 'email', 'first_name', 'last_name',
            
            # Basic Info
            'phone', 'profile_photo', 'profile_summary', 'bio',
            
            # Social Links
            'linkedin_url', 'github_url', 'portfolio_url',
            
            # Skills & Languages
            'skills', 'languages',
            
            # Resume
            'resume', 'resume_text',
            
            # Employment Details
            'is_fresher', 'current_company', 'current_job_title', 
            'current_salary', 'expected_salary',
            'employment_history', 'internships',
            
            # Education
            'education',
            
            # Projects
            'projects',
            
            # Accomplishments
            'accomplishments',
            
            # Job Preferences
            'preferred_job_type', 'preferred_locations', 'preferred_industry',
            'willing_to_relocate',
            
            # Availability
            'notice_period', 'available_from',
            
            # Location
            'current_location', 'hometown',
            
            # Personal Details
            'date_of_birth', 'gender', 'marital_status',
            'father_name', 'mother_name',
            
            # Status
            'is_profile_complete', 'profile_views',
            
            # Timestamps
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'profile_views', 'created_at', 'updated_at']
    
    def to_internal_value(self, data):
        # Convert stringified JSON fields to actual lists/dicts
        for field_name in ['skills', 'languages', 'education', 'projects', 'accomplishments', 'employment_history', 'internships', 'preferred_job_type', 'preferred_locations']:
            if field_name in data:
                value = data.get(field_name)
                if isinstance(value, str):
                    try:
                        data[field_name] = json.loads(value)
                    except:
                        data[field_name] = []
                elif value is None:
                    data[field_name] = []
        return super().to_internal_value(data)


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id', 'username', 'email', 'name', 'description', 'website', 'logo',
            'location', 'industry', 'company_size', 'founded_year', 'is_verified',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']


class LoginSerializer(serializers.Serializer):
    """Serializer for login"""
    
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')
        
        if not username and not email:
            raise serializers.ValidationError("Username or email is required")
        
        if not password:
            raise serializers.ValidationError("Password is required")
        
        # Try to find user by username or email
        User = get_user_model()
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid credentials")
        else:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid credentials")
        
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting password reset"""
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        User = get_user_model()
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            # Don't reveal whether the email exists or not
            pass
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming password reset"""
    
    token = serializers.CharField()
    uid = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs


class PasswordResetDirectSerializer(serializers.Serializer):
    """Serializer for direct password reset (no email)"""
    email = serializers.EmailField()
    new_password = serializers.CharField(min_length=8, validators=[validate_password])
    new_password_confirm = serializers.CharField(min_length=8, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Passwords don't match."})
        return attrs



