from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, UserDetailView, ProfileView, CompanyView, ProfileDetailView,
    ChangePasswordView, UserListView, BlockUserView, DeleteUserView, current_user_view,
    PasswordResetRequestView, PasswordResetConfirmView, PasswordResetDirectView,
    JobSeekerDashboardView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', current_user_view, name='current_user'),
    # IMPORTANT: More specific paths must come BEFORE less specific ones
    path('profile/seeker/', ProfileView.as_view(), name='seeker_profile'),
    path('jobseeker-dashboard/', JobSeekerDashboardView.as_view(), name='jobseeker_dashboard'),
    path('profiles/<int:pk>/', ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/company/', CompanyView.as_view(), name='company_profile'),

    path('profile/', UserDetailView.as_view(), name='user_detail'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-direct/', PasswordResetDirectView.as_view(), name='password_reset_direct'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:user_id>/block/', BlockUserView.as_view(), name='block_user'),
    path('users/<int:user_id>/delete/', DeleteUserView.as_view(), name='delete_user'),
]

