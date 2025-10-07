from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from .models import ClientProfile, ServicemanProfile
from .serializers import (
    UserSerializer, RegisterSerializer,
    ClientProfileSerializer, ServicemanProfileSerializer
)
from .tokens import email_verification_token

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        # Profile creation is handled by the post_save signal in signals.py
        # Send verification email
        try:
            self.send_verification_email(user)
        except Exception as e:
            # Log email sending errors but don't fail user registration
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send verification email to user {user.id}: {e}")

    def send_verification_email(self, user):
        token = email_verification_token.make_token(user)
        uid = user.pk
        url = self.request.build_absolute_uri(
            reverse('users:verify-email') + f"?uid={uid}&token={token}"
        )
        send_mail(
            "Verify your email",
            f"Please verify your email: {url}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )

class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        uid = request.GET.get('uid')
        token = request.GET.get('token')
        user = get_object_or_404(User, pk=uid)
        if email_verification_token.check_token(user, token):
            user.is_email_verified = True
            user.save()
            return Response({"detail": "Email verified."}, status=200)
        return Response({"detail": "Invalid token."}, status=400)

class ResendVerificationEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "Email is required."}, status=400)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            return Response({"detail": "If the email exists and is not verified, a verification email has been sent."}, status=200)
        
        # Only send if email is not already verified
        if not user.is_email_verified:
            try:
                self.send_verification_email(user)
                return Response({"detail": "Verification email sent."}, status=200)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to resend verification email to user {user.id}: {e}")
                return Response({"detail": "Failed to send verification email."}, status=500)
        else:
            return Response({"detail": "Email is already verified."}, status=400)

    def send_verification_email(self, user):
        token = email_verification_token.make_token(user)
        uid = user.pk
        url = self.request.build_absolute_uri(
            reverse('users:verify-email') + f"?uid={uid}&token={token}"
        )
        send_mail(
            "Verify your email",
            f"Please verify your email: {url}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )

class UserMeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class ClientProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.client_profile

class ServicemanProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ServicemanProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.serviceman_profile

class PublicServicemanProfileView(generics.RetrieveAPIView):
    """Public view of serviceman profile for clients to browse"""
    serializer_class = ServicemanProfileSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ServicemanProfile.objects.all()
    lookup_field = 'user_id'

class RunMigrationsView(APIView):
    """Run database migrations - REMOVE IN PRODUCTION"""
    permission_classes = [permissions.AllowAny]  # Only for development
    
    def post(self, request):
        import subprocess
        import sys
        
        try:
            # Run migrations
            result = subprocess.run([
                sys.executable, 'manage.py', 'migrate'
            ], capture_output=True, text=True, cwd='/opt/render/project/src')
            
            if result.returncode == 0:
                return Response({
                    "message": "Migrations completed successfully",
                    "output": result.stdout
                })
            else:
                return Response({
                    "error": "Migration failed",
                    "output": result.stderr
                }, status=500)
                
        except Exception as e:
            return Response({
                "error": f"Failed to run migrations: {str(e)}"
            }, status=500)

class CreateTestServicemenView(APIView):
    """Create test servicemen for development - REMOVE IN PRODUCTION"""
    permission_classes = [permissions.AllowAny]  # Only for development
    
    def post(self, request):
        from apps.services.models import Category
        
        category_id = request.data.get('category_id', 1)
        
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"error": f"Category with ID {category_id} does not exist"}, status=400)

        # Create test servicemen
        test_servicemen = [
            {
                'username': 'john_electrician',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'bio': 'Experienced electrician with 10+ years in residential and commercial electrical work.',
                'years_of_experience': 10,
                'phone_number': '+2348012345678'
            },
            {
                'username': 'jane_electrician',
                'email': 'jane@example.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'bio': 'Professional electrician specializing in smart home installations and electrical repairs.',
                'years_of_experience': 8,
                'phone_number': '+2348012345679'
            },
            {
                'username': 'mike_electrician',
                'email': 'mike@example.com',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'bio': 'Licensed electrician with expertise in industrial electrical systems and emergency repairs.',
                'years_of_experience': 12,
                'phone_number': '+2348012345680'
            }
        ]

        created_servicemen = []
        for i, serviceman_data in enumerate(test_servicemen):
            # Check if user already exists
            if User.objects.filter(email=serviceman_data['email']).exists():
                continue

            # Create user
            user = User.objects.create_user(
                username=serviceman_data['username'],
                email=serviceman_data['email'],
                password='TestPass123!',
                user_type='SERVICEMAN',
                first_name=serviceman_data['first_name'],
                last_name=serviceman_data['last_name']
            )

            # Update serviceman profile
            profile = user.serviceman_profile
            profile.category = category
            profile.bio = serviceman_data['bio']
            profile.years_of_experience = serviceman_data['years_of_experience']
            profile.phone_number = serviceman_data['phone_number']
            profile.rating = 4.5 + (i * 0.1)  # Vary ratings slightly
            profile.total_jobs_completed = 20 + (i * 5)  # Vary job counts
            profile.save()

            created_servicemen.append({
                'id': user.id,
                'full_name': user.get_full_name(),
                'email': user.email,
                'rating': profile.rating,
                'total_jobs_completed': profile.total_jobs_completed
            })

        return Response({
            "message": f"Created {len(created_servicemen)} servicemen for category '{category.name}'",
            "servicemen": created_servicemen
        })

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get('email')
        user = get_object_or_404(User, email=email)
        token = default_token_generator.make_token(user)
        uid = user.pk
        url = self.request.build_absolute_uri(
            reverse('users:password-reset-confirm') + f"?uid={uid}&token={token}"
        )
        send_mail(
            "Password Reset",
            f"Use this link to reset your password: {url}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        return Response({"detail": "Password reset email sent."})

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        uid = request.GET.get('uid')
        token = request.GET.get('token')
        password = request.data.get('password')
        user = get_object_or_404(User, pk=uid)
        if default_token_generator.check_token(user, token):
            user.set_password(password)
            user.save()
            return Response({"detail": "Password has been reset."})
        return Response({"detail": "Invalid token."}, status=400)