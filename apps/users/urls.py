from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView,
)
from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("verify-email/", views.VerifyEmailView.as_view(), name="verify-email"),
    path("resend-verification-email/", views.ResendVerificationEmailView.as_view(), name="resend-verification-email"),
    path("me/", views.UserMeView.as_view(), name="me"),
    path("client-profile/", views.ClientProfileView.as_view(), name="client-profile"),
    path("serviceman-profile/", views.ServicemanProfileView.as_view(), name="serviceman-profile"),
    path("servicemen/<int:user_id>/", views.PublicServicemanProfileView.as_view(), name="public-serviceman-profile"),
    path("health/", views.HealthCheckView.as_view(), name="health-check"),
    path("run-migrations/", views.RunMigrationsView.as_view(), name="run-migrations"),
    path("create-test-servicemen/", views.CreateTestServicemenView.as_view(), name="create-test-servicemen"),
    path("token/", TokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("password-reset/", views.PasswordResetRequestView.as_view(), name="password-reset"),
    path("password-reset-confirm/", views.PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
]