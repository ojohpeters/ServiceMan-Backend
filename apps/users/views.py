from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from .models import ClientProfile, ServicemanProfile, Skill
from .serializers import (
    UserSerializer, RegisterSerializer,
    ClientProfileSerializer, ServicemanProfileSerializer,
    SkillSerializer, SkillCreateSerializer, AdminCreateSerializer
)
from .tokens import email_verification_token
from .utils import send_verification_email, send_password_reset_email, send_password_reset_success_email
from .permissions import IsAdmin

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    Register a new user (Client or Serviceman).
    
    Creates a new user account and sends a verification email.
    User profiles (ClientProfile or ServicemanProfile) are created automatically via signals.
    
    Features:
    - Blocks ADMIN creation (use /api/users/admin/create/ instead)
    - Supports skill assignment during serviceman registration
    - Sends beautiful HTML verification email
    - Auto-creates user profile based on user_type
    
    Tags: Authentication
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        # Profile creation is handled by the post_save signal in signals.py
        # Send verification email using HTML template
        try:
            send_verification_email(user, self.request)
        except Exception as e:
            # Log email sending errors but don't fail user registration
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send verification email to user {user.id}: {e}")

class VerifyEmailView(APIView):
    """
    Verify user email address with token.
    
    Called when user clicks the verification link in their email.
    Marks the user's email as verified.
    
    Query Parameters:
    - uid: User ID
    - token: Verification token (expires after 24 hours)
    
    Tags: Email Verification
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        uid = request.GET.get('uid')
        token = request.GET.get('token')
        user = get_object_or_404(User, pk=uid)
        if email_verification_token.check_token(user, token):
            user.is_email_verified = True
            user.save()
            return Response({"detail": "Email verified successfully."}, status=200)
        return Response({"detail": "Invalid or expired token."}, status=400)

class ResendVerificationEmailView(APIView):
    """
    Resend email verification link.
    
    Allows users to request a new verification email if they didn't receive
    the original one or if it expired.
    
    Security: Returns generic message to prevent email enumeration.
    
    Tags: Email Verification
    """
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
                send_verification_email(user, self.request)
                return Response({"detail": "Verification email sent."}, status=200)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to resend verification email to user {user.id}: {e}")
                return Response({"detail": "Failed to send verification email."}, status=500)
        else:
            return Response({"detail": "Email is already verified."}, status=400)

class UserMeView(generics.RetrieveAPIView):
    """
    Get current authenticated user information.
    
    Returns basic user data including username, email, user_type, and verification status.
    
    Tags: User Profiles
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class ClientProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update client profile.
    
    Clients can view and update their own profile information including
    phone number and address.
    
    Tags: User Profiles
    """
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.client_profile

class ServicemanProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update serviceman profile.
    
    Servicemen can view and update their profile including:
    - Bio and experience
    - Phone number
    - Availability status
    - Skills (via skill_ids)
    - Category
    
    Note: Rating and total_jobs_completed are read-only.
    
    Tags: User Profiles
    """
    serializer_class = ServicemanProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.serviceman_profile

class PublicServicemanProfileView(generics.RetrieveAPIView):
    """
    Public view of serviceman profile.
    
    Allows clients to browse serviceman profiles without authentication.
    Includes skills, ratings, jobs completed, and other public information.
    
    Tags: User Profiles
    """
    serializer_class = ServicemanProfileSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ServicemanProfile.objects.all()
    lookup_field = 'user_id'

class CreateTestServicemenView(APIView):
    """
    Create test servicemen for development.
    
    ⚠️ REMOVE IN PRODUCTION - This is for development/testing only.
    
    Creates 3 test servicemen with predefined profiles for a given category.
    Useful for quickly populating the database during development.
    
    Tags: Development
    """
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
    """
    Request a password reset link via email.
    
    Security: Returns success message even if email doesn't exist to prevent email enumeration.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({"detail": "Email is required."}, status=400)
        
        try:
            user = User.objects.get(email=email)
            # Send password reset email with HTML template
            send_password_reset_email(user, request)
        except User.DoesNotExist:
            # Don't reveal if email exists or not (security best practice)
            pass
        
        # Always return success to prevent email enumeration
        return Response({
            "detail": "If the email exists in our system, a password reset link has been sent."
        }, status=200)

class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with token and set new password.
    
    Sends a confirmation email after successful password reset.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        uid = request.GET.get('uid')
        token = request.GET.get('token')
        password = request.data.get('password')
        
        if not all([uid, token, password]):
            return Response({
                "detail": "Missing required parameters (uid, token, password)."
            }, status=400)
        
        # Validate password strength
        if len(password) < 8:
            return Response({
                "detail": "Password must be at least 8 characters long."
            }, status=400)
        
        user = get_object_or_404(User, pk=uid)
        
        if default_token_generator.check_token(user, token):
            user.set_password(password)
            user.save()
            
            # Send password reset success confirmation email
            try:
                send_password_reset_success_email(user, request)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send password reset success email: {e}")
            
            return Response({"detail": "Password has been reset successfully."}, status=200)
        
        return Response({"detail": "Invalid or expired token."}, status=400)

class TestEmailView(APIView):
    """
    Test email configuration.
    
    ⚠️ REMOVE IN PRODUCTION - This is for development/testing only.
    
    Sends a test email to verify SMTP configuration is working correctly.
    Returns email configuration details for debugging.
    
    Tags: Development
    """
    permission_classes = [permissions.AllowAny]  # Only for development
    
    def post(self, request):
        # Test email configuration
        email = request.data.get('email', 'test@example.com')
        
        import logging
        logger = logging.getLogger(__name__)
        
        # Log current email settings
        logger.info("=== EMAIL CONFIGURATION DEBUG ===")
        logger.info(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        logger.info(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        logger.info(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        logger.info(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        logger.info(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        logger.info(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        try:
            result = send_mail(
                "Test Email from ServiceMan API",
                "This is a test email to verify email configuration is working.",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            logger.info(f"Test email sent successfully. Result: {result}")
            return Response({
                "detail": "Test email sent successfully",
                "email_settings": {
                    "backend": settings.EMAIL_BACKEND,
                    "host": settings.EMAIL_HOST,
                    "port": settings.EMAIL_PORT,
                    "user": settings.EMAIL_HOST_USER,
                    "tls": settings.EMAIL_USE_TLS,
                    "from": settings.DEFAULT_FROM_EMAIL,
                }
            }, status=200)
        except Exception as e:
            logger.error(f"Test email failed: {e}")
            return Response({
                "detail": f"Test email failed: {str(e)}",
                "email_settings": {
                    "backend": settings.EMAIL_BACKEND,
                    "host": settings.EMAIL_HOST,
                    "port": settings.EMAIL_PORT,
                    "user": settings.EMAIL_HOST_USER,
                    "tls": settings.EMAIL_USE_TLS,
                    "from": settings.DEFAULT_FROM_EMAIL,
                }
            }, status=500)


# ============================================================================
# SKILLS MANAGEMENT VIEWS
# ============================================================================

class SkillListView(generics.ListAPIView):
    """
    List all active skills.
    
    Public endpoint - no authentication required.
    Useful for displaying skills during serviceman registration or profile update.
    
    Query Parameters:
    - category: Filter by skill category (TECHNICAL, MANUAL, CREATIVE, PROFESSIONAL, OTHER)
    """
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Skill.objects.filter(is_active=True)
        
        # Filter by category if provided
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category.upper())
        
        return queryset


class SkillDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific skill by ID.
    
    Public endpoint - no authentication required.
    """
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Skill.objects.filter(is_active=True)


class SkillCreateView(generics.CreateAPIView):
    """
    Create a new skill (Admin only).
    
    Only administrators can create new skills.
    Skills are used by servicemen to showcase their expertise.
    """
    serializer_class = SkillCreateSerializer
    permission_classes = [IsAdmin]
    
    def perform_create(self, serializer):
        serializer.save()


class SkillUpdateView(generics.UpdateAPIView):
    """
    Update an existing skill (Admin only).
    
    Only administrators can update skills.
    All servicemen using this skill will see the updated information.
    """
    serializer_class = SkillSerializer
    permission_classes = [IsAdmin]
    queryset = Skill.objects.all()


class SkillDeleteView(generics.DestroyAPIView):
    """
    Soft delete a skill (Admin only).
    
    Marks skill as inactive instead of deleting it.
    This preserves data integrity and historical records.
    """
    permission_classes = [IsAdmin]
    queryset = Skill.objects.all()
    
    def perform_destroy(self, instance):
        # Soft delete - mark as inactive instead of deleting
        instance.is_active = False
        instance.save()


class ServicemanSkillsView(APIView):
    """
    Manage skills for a specific serviceman.
    
    GET: List all skills for a serviceman (public)
    POST: Add skills to a serviceman (serviceman themselves or admin)
    DELETE: Remove skills from a serviceman (serviceman themselves or admin)
    """
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get(self, request, serviceman_id):
        """Get all skills for a specific serviceman"""
        serviceman = get_object_or_404(
            ServicemanProfile,
            user_id=serviceman_id
        )
        skills = serviceman.skills.filter(is_active=True)
        serializer = SkillSerializer(skills, many=True)
        return Response({
            "serviceman": {
                "id": serviceman.user.id,
                "username": serviceman.user.username,
                "full_name": serviceman.user.get_full_name()
            },
            "skills": serializer.data
        })
    
    def post(self, request, serviceman_id):
        """Add skills to a serviceman"""
        serviceman = get_object_or_404(
            ServicemanProfile,
            user_id=serviceman_id
        )
        
        # Check permissions: serviceman themselves or admin
        if request.user.id != serviceman_id and request.user.user_type != User.ADMIN:
            return Response({
                "detail": "You don't have permission to modify this serviceman's skills."
            }, status=403)
        
        skill_ids = request.data.get('skill_ids', [])
        if not skill_ids:
            return Response({
                "detail": "skill_ids is required."
            }, status=400)
        
        # Add skills (doesn't remove existing ones)
        skills = Skill.objects.filter(id__in=skill_ids, is_active=True)
        serviceman.skills.add(*skills)
        
        # Return updated skills list
        updated_skills = serviceman.skills.filter(is_active=True)
        serializer = SkillSerializer(updated_skills, many=True)
        return Response({
            "message": f"Added {len(skills)} skill(s) successfully.",
            "skills": serializer.data
        })
    
    def delete(self, request, serviceman_id):
        """Remove skills from a serviceman"""
        serviceman = get_object_or_404(
            ServicemanProfile,
            user_id=serviceman_id
        )
        
        # Check permissions: serviceman themselves or admin
        if request.user.id != serviceman_id and request.user.user_type != User.ADMIN:
            return Response({
                "detail": "You don't have permission to modify this serviceman's skills."
            }, status=403)
        
        skill_ids = request.data.get('skill_ids', [])
        if not skill_ids:
            return Response({
                "detail": "skill_ids is required."
            }, status=400)
        
        # Remove skills
        skills = Skill.objects.filter(id__in=skill_ids)
        serviceman.skills.remove(*skills)
        
        # Return updated skills list
        updated_skills = serviceman.skills.filter(is_active=True)
        serializer = SkillSerializer(updated_skills, many=True)
        return Response({
            "message": f"Removed {len(skills)} skill(s) successfully.",
            "skills": serializer.data
        })


# ============================================================================
# ADMIN CREATION VIEW
# ============================================================================

class AdminCreateView(generics.CreateAPIView):
    """
    Create a new administrator user (Admin only).
    
    Security:
    - Only existing administrators can create new admins
    - Requires password confirmation
    - Auto-sets: user_type=ADMIN, is_staff=True, is_email_verified=True
    - Prevents email enumeration by validating in serializer
    
    The public registration endpoint blocks ADMIN user_type creation.
    """
    serializer_class = AdminCreateSerializer
    permission_classes = [IsAdmin]
    
    def perform_create(self, serializer):
        user = serializer.save()
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"New admin user created: {user.username} (ID: {user.id}) by {self.request.user.username}")