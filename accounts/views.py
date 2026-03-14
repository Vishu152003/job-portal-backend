from django.db.models import Q
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.password_validation import validate_password
import json
from .models import Profile, Company
import logging
from .serializers import (
    UserSerializer, UserRegistrationSerializer, ProfileSerializer,
    CompanySerializer, LoginSerializer, ChangePasswordSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer, PasswordResetDirectSerializer
)
from jobs.models import SavedJob
from applications.models import Application

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """API endpoint for user registration"""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """API endpoint for user login"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not username and not email:
            return Response(
                {'error': 'Username or email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not password:
            return Response(
                {'error': 'Password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find user - try username first, then email
        User = get_user_model()
        user = None
        
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=username)
                except User.DoesNotExist:
                    pass
        elif email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                pass
        
        if user is None:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.check_password(password):
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if user.is_blocked:
            return Response(
                {'error': 'Your account has been blocked'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        refresh = RefreshToken.for_user(user)
        
        extra_data = {}
        if user.role == 'seeker':
            profile, created = Profile.objects.get_or_create(user=user)
            extra_data['profile'] = ProfileSerializer(profile).data
        elif user.role == 'recruiter':
            try:
                company = user.company
                extra_data['company'] = CompanySerializer(company).data
            except Company.DoesNotExist:
                company = Company.objects.create(user=user)
                extra_data['company'] = CompanySerializer(company).data
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            **extra_data
        }, status=status.HTTP_200_OK)


class UserDetailView(generics.RetrieveUpdateAPIView):
    """API endpoint to get/update current user"""
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class ProfileView(generics.RetrieveUpdateAPIView):
    """API endpoint for user profile (seekers) - Full profile management"""
    
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_object(self):
        if self.request.user.role != 'seeker':
            return Response(
                {'error': 'Only job seekers have profiles'},
                status=status.HTTP_403_FORBIDDEN
            )
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        if isinstance(instance, Response):
            return instance
        
        # Get the data - handle both form data and JSON
        if hasattr(request, 'data'):
            data = request.data
        else:
            data = request
        
        # Process JSON fields properly - only update if they are provided
        json_fields = ['skills', 'languages', 'education', 'projects', 'accomplishments', 
                      'employment_history', 'internships', 'preferred_job_type', 'preferred_locations']
        
        # Create a copy of data to modify
        update_data = {}
        
        for key in data.keys():
            if key in json_fields:
                value = data.get(key)
                if isinstance(value, str) and value:
                    try:
                        update_data[key] = json.loads(value)
                    except:
                        update_data[key] = []
                elif isinstance(value, list):
                    update_data[key] = value
                elif value == '' or value is None:
                    # Don't update if empty - keep existing value
                    continue
            else:
                # For non-JSON fields, just copy as is
                update_data[key] = data.get(key)
        

        for key, value in update_data.items():
            if key in json_fields:
                # For JSON fields, set the value directly
                setattr(instance, key, value)
            else:
                setattr(instance, key, value)
        
        instance.save()
        
        # Return updated serializer data
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CompanyView(generics.RetrieveUpdateAPIView):
    """API endpoint for company profile (recruiters)"""
    
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_object(self):
        if self.request.user.role != 'recruiter':
            return Response(
                {'error': 'Only recruiters have company profiles'},
                status=status.HTTP_403_FORBIDDEN
            )
        company, created = Company.objects.get_or_create(user=self.request.user)
        return company


class ChangePasswordView(APIView):
    """API endpoint to change password"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Invalid old password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response(
            {'message': 'Password changed successfully'},
            status=status.HTTP_200_OK
        )


class UserListView(generics.ListAPIView):
    """API endpoint to list users (admin only)"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_admin:
            return User.objects.none()
        
        queryset = User.objects.all()
        role = self.request.query_params.get('role')
        is_blocked = self.request.query_params.get('is_blocked')
        
        if role:
            queryset = queryset.filter(role=role)
        if is_blocked is not None:
            queryset = queryset.filter(is_blocked=is_blocked.lower() == 'true')
        
        return queryset


class BlockUserView(APIView):
    """API endpoint to block/unblock users (admin only)"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can block users'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if user == request.user:
            return Response(
                {'error': 'You cannot block yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_blocked = not user.is_blocked
        user.save()
        
        action = 'unblocked' if not user.is_blocked else 'blocked'
        return Response(
            {'message': f'User {action} successfully'},
            status=status.HTTP_200_OK
        )


class DeleteUserView(APIView):
    """API endpoint to delete users (admin only)"""
    
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, user_id):
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can delete users'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if user == request.user:
            return Response(
                {'error': 'You cannot delete yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        username = user.username
        user.delete()
        
        return Response(
            {'message': f'User @{username} deleted successfully'},
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """Get current user info with profile/company data"""
    user = request.user
    data = UserSerializer(user).data
    
    if user.role == 'seeker':
        profile, _ = Profile.objects.get_or_create(user=user)
        data['profile'] = ProfileSerializer(profile).data
    elif user.role == 'recruiter':
        company, _ = Company.objects.get_or_create(user=user)
        data['company'] = CompanySerializer(company).data
    
    return Response(data)


class PasswordResetRequestView(APIView):
    """API endpoint to request password reset - direct flow (no email)"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        User = get_user_model()
        
        try:
            user = User.objects.get(email=email)
            return Response(
                {'message': 'Email verified. You can now reset your password.'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'Email not registered.'},
                status=status.HTTP_404_NOT_FOUND
            )


class PasswordResetConfirmView(APIView):
    """API endpoint to confirm password reset"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        uid = serializer.validated_data['uid']
        new_password = serializer.validated_data['new_password']
        
        User = get_user_model()
        
        from django.utils.encoding import force_str
        from django.utils.http import urlsafe_base64_decode
        
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=user_id)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response(
                {'error': 'Invalid reset link'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not default_token_generator.check_token(user, token):
            return Response(
                {'error': 'Invalid or expired reset token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response(
            {'message': 'Password reset successfully'},
            status=status.HTTP_200_OK
        )


class PasswordResetDirectView(APIView):
    """API endpoint for direct password reset (email verify + new password)"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetDirectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        new_password = serializer.validated_data['new_password']
        
        User = get_user_model()
        
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            return Response(
                {'message': 'Password updated successfully. Please login.'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'Email not registered.'},
                status=status.HTTP_404_NOT_FOUND
            )


class IsJobSeeker(permissions.BasePermission):
    """Permission class for job seekers only"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'seeker'
        )


class JobSeekerDashboardView(APIView):
    """API endpoint for job seeker dashboard stats"""
    
    permission_classes = [IsJobSeeker]
    
    def get(self, request):
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)
        
        applied_count = Application.objects.filter(seeker=user).count()
        saved_count = SavedJob.objects.filter(user=user).count()
        interviews_count = Application.objects.filter(
            seeker=user, 
            status__in=['interview', 'offered']
        ).count()
        profile_views = profile.profile_views
        
        return Response({
            'applied_count': applied_count,
            'saved_count': saved_count,
            'interviews_count': interviews_count,
            'profile_views': profile_views
        })


class ProfileDetailView(APIView):
    logger = logging.getLogger(__name__)
    """API endpoint for viewing job seeker profile (increments views for recruiters)"""
    
    def get(self, request, pk):
        try:
            profile = Profile.objects.get(id=pk)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Increment views ONLY if recruiter viewing different seeker's profile
        if (request.user.is_authenticated and 
            hasattr(request.user, 'role') and 
            request.user.role == 'recruiter' and 
            request.user != profile.user):
            try:
                with transaction.atomic():
                    profile.profile_views = F('profile_views') + 1
                    profile.save()
                    self.logger.info("Incremented profile view for profile %s by recruiter %s", pk, request.user.username)
            except Exception as e:
                self.logger.error("Error incrementing profile view %s: %s", pk, e)
        
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

