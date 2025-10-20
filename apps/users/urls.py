from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView,
)
from . import views

app_name = "users"

urlpatterns = [
    # Authentication & Registration
    path("register/", views.RegisterView.as_view(), name="register"),
    path("verify-email/", views.VerifyEmailView.as_view(), name="verify-email"),
    path("resend-verification-email/", views.ResendVerificationEmailView.as_view(), name="resend-verification-email"),
    path("token/", TokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # Password Reset
    path("password-reset/", views.PasswordResetRequestView.as_view(), name="password-reset"),
    path("password-reset-confirm/", views.PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    
    # User Profile
    path("me/", views.UserMeView.as_view(), name="me"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="user-detail"),
    path("client-profile/", views.ClientProfileView.as_view(), name="client-profile"),
    path("serviceman-profile/", views.ServicemanProfileView.as_view(), name="serviceman-profile"),
    
    # Clients - Get by ID
    path("clients/<int:user_id>/", views.ClientProfileDetailView.as_view(), name="client-detail"),
    
    # Servicemen - List all or get specific
    path("servicemen/", views.AllServicemenListView.as_view(), name="servicemen-list"),
    path("servicemen/<int:user_id>/", views.PublicServicemanProfileView.as_view(), name="public-serviceman-profile"),
    
    # Skills Management
    path("skills/", views.SkillListView.as_view(), name="skill-list"),
    path("skills/<int:pk>/", views.SkillDetailView.as_view(), name="skill-detail"),
    path("skills/create/", views.SkillCreateView.as_view(), name="skill-create"),
    path("skills/<int:pk>/update/", views.SkillUpdateView.as_view(), name="skill-update"),
    path("skills/<int:pk>/delete/", views.SkillDeleteView.as_view(), name="skill-delete"),
    path("servicemen/<int:serviceman_id>/skills/", views.ServicemanSkillsView.as_view(), name="serviceman-skills"),
    
    # Admin Management
    path("admin/create/", views.AdminCreateView.as_view(), name="admin-create"),
    path("admin/assign-category/", views.AdminAssignServicemanCategoryView.as_view(), name="admin-assign-category"),
    path("admin/bulk-assign-category/", views.AdminBulkAssignCategoryView.as_view(), name="admin-bulk-assign-category"),
    path("admin/servicemen-by-category/", views.AdminGetServicemenByCategoryView.as_view(), name="admin-servicemen-by-category"),
    
    # Development/Testing (Remove in production)
    path("create-test-servicemen/", views.CreateTestServicemenView.as_view(), name="create-test-servicemen"),
    path("test-email/", views.TestEmailView.as_view(), name="test-email"),
]