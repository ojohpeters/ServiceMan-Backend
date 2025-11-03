from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
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

    @extend_schema(
        responses={200: OpenApiResponse(description="Email verified successfully")}
    )
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

    @extend_schema(
        request={'application/json': {'type': 'object', 'properties': {'email': {'type': 'string'}}}},
        responses={200: OpenApiResponse(description="Verification email sent")}
    )
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


class UserDetailView(generics.RetrieveAPIView):
    """
    Get any user's details by ID (Admin only or public for servicemen).
    
    Returns user information including:
    - Basic user data (username, email, user_type)
    - Profile data (if serviceman or client)
    
    Access:
    - Admins can view any user
    - Authenticated users can view servicemen (public profiles)
    - Users can view themselves
    
    Tags: User Profiles
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    lookup_field = 'pk'
    
    def get_object(self):
        user = super().get_object()
        request_user = self.request.user
        
        # Allow access if:
        # 1. Admin viewing any user
        # 2. User viewing themselves
        # 3. Anyone viewing a serviceman (public profiles)
        if (request_user.user_type == 'ADMIN' or 
            request_user.id == user.id or 
            user.user_type == 'SERVICEMAN'):
            return user
        
        # Restrict access to client profiles (privacy)
        if user.user_type == 'CLIENT' and request_user.user_type != 'ADMIN':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to view this user's details.")
        
        return user


class ClientProfileDetailView(generics.RetrieveAPIView):
    """
    Get client profile by ID (Admin only or self).
    
    Returns complete client profile including:
    - User information
    - Contact details (phone, address)
    - Account creation date
    
    Access:
    - Admins can view any client
    - Clients can view their own profile
    
    Needed for: Service request client details, admin management
    
    Tags: User Profiles
    """
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ClientProfile.objects.select_related('user')
    lookup_field = 'user_id'
    
    def get_object(self):
        profile = super().get_object()
        request_user = self.request.user
        
        # Allow access if admin or viewing own profile
        if request_user.user_type == 'ADMIN' or request_user.id == profile.user_id:
            return profile
        
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied("You don't have permission to view this client's profile.")

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
        from django.db import connection
        import logging
        import traceback
        
        logger = logging.getLogger(__name__)
        
        try:
            # Check which fields exist in the database
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users_servicemanprofile'
                """)
                existing_columns = [row[0] for row in cursor.fetchall()]
            
            logger.info(f"ServicemanProfileView.get_object - existing columns: {existing_columns}")
            
            # Determine which fields to defer
            fields_to_defer = []
            potential_new_fields = ['is_approved', 'approved_by_id', 'approved_at', 'rejection_reason']
            
            for field in potential_new_fields:
                if field not in existing_columns:
                    defer_name = field.replace('_id', '') if field.endswith('_id') else field
                    fields_to_defer.append(defer_name)
            
            logger.info(f"ServicemanProfileView.get_object - fields to defer: {fields_to_defer}")
            
            # Get profile with deferred fields
            queryset = ServicemanProfile.objects.filter(user=self.request.user)
            if fields_to_defer:
                queryset = queryset.defer(*fields_to_defer)
            
            logger.info(f"ServicemanProfileView.get_object - executing query for user {self.request.user.id}")
            profile = queryset.first()
            
            # If profile doesn't exist, create it
            if not profile:
                logger.warning(f"ServicemanProfileView.get_object - Profile doesn't exist for user {self.request.user.id}, creating...")
                
                # Use raw SQL to insert only existing columns
                from django.db import connection
                from django.utils import timezone
                
                # Get all fields that should have default values
                insert_fields = ['user_id']
                insert_values = [self.request.user.id]
                
                # Add fields that exist in database with their defaults
                now = timezone.now()
                field_defaults = {
                    'rating': '0.00',
                    'total_jobs_completed': 0,
                    'bio': '',
                    'years_of_experience': 0,
                    'phone_number': '',
                    'is_available': True,
                    'created_at': now,
                    'updated_at': now,
                }
                
                for field, default_value in field_defaults.items():
                    if field in existing_columns:
                        insert_fields.append(field)
                        insert_values.append(default_value)
                
                # Build and execute INSERT statement
                placeholders = ', '.join(['%s'] * len(insert_values))
                fields_str = ', '.join(insert_fields)
                
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"INSERT INTO users_servicemanprofile ({fields_str}) VALUES ({placeholders}) RETURNING id",
                        insert_values
                    )
                    profile_id = cursor.fetchone()[0]
                
                # Fetch the created profile with deferred fields
                profile = ServicemanProfile.objects.filter(id=profile_id)
                if fields_to_defer:
                    profile = profile.defer(*fields_to_defer)
                profile = profile.first()
                
                logger.info(f"ServicemanProfileView.get_object - Profile created: {profile}")
            else:
                logger.info(f"ServicemanProfileView.get_object - profile retrieved: {profile}")
            
            return profile
            
        except Exception as e:
            logger.error(f"ServicemanProfileView.get_object - ERROR: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def update(self, request, *args, **kwargs):
        import logging
        import traceback
        
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"ServicemanProfileView.update - starting update for user {request.user.id}")
            logger.info(f"ServicemanProfileView.update - request data: {request.data}")
            return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"ServicemanProfileView.update - ERROR: {str(e)}")
            logger.error(traceback.format_exc())
            from rest_framework.response import Response
            return Response(
                {
                    "error": "Update failed",
                    "detail": str(e),
                    "traceback": traceback.format_exc()
                },
                status=500
            )
    
    def partial_update(self, request, *args, **kwargs):
        import logging
        import traceback
        
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"ServicemanProfileView.partial_update - starting for user {request.user.id}")
            logger.info(f"ServicemanProfileView.partial_update - request data: {request.data}")
            return super().partial_update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"ServicemanProfileView.partial_update - ERROR: {str(e)}")
            logger.error(traceback.format_exc())
            from rest_framework.response import Response
            return Response(
                {
                    "error": "Partial update failed",
                    "detail": str(e),
                    "traceback": traceback.format_exc()
                },
                status=500
            )

class AllServicemenListView(generics.ListAPIView):
    """
    List all servicemen across all categories (Public).
    
    Returns all servicemen with:
    - Availability status
    - Active jobs count
    - Skills, ratings, experience
    - Category information
    
    Query Parameters:
    - category: Filter by category ID
    - is_available: Filter by availability (true/false)
    - min_rating: Filter by minimum rating
    - search: Search by name or username
    - ordering: Sort by rating, total_jobs_completed, etc.
    
    Tags: User Profiles
    """
    serializer_class = ServicemanProfileSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        from django.db.models import Q, Count, Case, When, IntegerField
        from django.core.exceptions import FieldError
        from django.db import connection
        
        # Check which fields exist in the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users_servicemanprofile'
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Start with basic queryset
    queryset = ServicemanProfile.objects.all()
        
        # Defer fields that don't exist yet
        fields_to_defer = []
        potential_new_fields = ['is_approved', 'approved_by_id', 'approved_at', 'rejection_reason']
        
        for field in potential_new_fields:
            if field not in existing_columns:
                fields_to_defer.append(field.replace('_id', ''))  # approved_by_id -> approved_by
        
        if fields_to_defer:
            queryset = queryset.defer(*fields_to_defer)
        
        # By default, show only approved servicemen (unless admin wants to see all)
        show_all = self.request.query_params.get('show_all', 'false').lower() == 'true'
        is_admin = self.request.user.is_authenticated and self.request.user.user_type == 'ADMIN'
        
        # Try to filter by is_approved (only if field exists)
        if not (show_all and is_admin) and 'is_approved' in existing_columns:
            queryset = queryset.filter(is_approved=True)
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by availability
        is_available = self.request.query_params.get('is_available', None)
        if is_available is not None:
            is_available_bool = is_available.lower() == 'true'
            queryset = queryset.filter(is_available=is_available_bool)
        
        # Filter by minimum rating
        min_rating = self.request.query_params.get('min_rating', None)
        if min_rating:
            queryset = queryset.filter(rating__gte=float(min_rating))
        
        # Search by name or username
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-rating')
        valid_orderings = ['rating', '-rating', 'total_jobs_completed', 
                          '-total_jobs_completed', 'years_of_experience', 
                          '-years_of_experience', 'created_at', '-created_at']
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)
        else:
            # Default: Available first, then by rating
            queryset = queryset.order_by('-is_available', '-rating')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Calculate statistics
        total_count = queryset.count()
        available_count = queryset.filter(is_available=True).count()
        busy_count = total_count - available_count
        
        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['statistics'] = {
                'total_servicemen': total_count,
                'available': available_count,
                'busy': busy_count,
            }
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'statistics': {
                'total_servicemen': total_count,
                'available': available_count,
                'busy': busy_count,
            },
            'results': serializer.data
        })


class PublicServicemanProfileView(generics.RetrieveAPIView):
    """
    Public view of serviceman profile.
    
    Allows clients to browse serviceman profiles without authentication.
    Includes skills, ratings, jobs completed, and other public information.
    
    Tags: User Profiles
    """
    serializer_class = ServicemanProfileSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'user_id'
    
    def get_queryset(self):
        from django.core.exceptions import FieldError
        from django.db import connection
        
        # Check which fields exist in the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users_servicemanprofile'
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Start with basic queryset
        queryset = ServicemanProfile.objects.all()
        
        # Defer fields that don't exist yet
        fields_to_defer = []
        potential_new_fields = ['is_approved', 'approved_by_id', 'approved_at', 'rejection_reason']
        
        for field in potential_new_fields:
            if field not in existing_columns:
                fields_to_defer.append(field.replace('_id', ''))  # approved_by_id -> approved_by
        
        if fields_to_defer:
            queryset = queryset.defer(*fields_to_defer)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            # Log the error for debugging
            import traceback
            traceback.print_exc()
            return Response(
                {"detail": f"Error retrieving serviceman profile: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CreateTestServicemenView(APIView):
    """
    Create test servicemen for development.
    
    ⚠️ REMOVE IN PRODUCTION - This is for development/testing only.
    
    Creates 3 test servicemen with predefined profiles for a given category.
    Useful for quickly populating the database during development.
    
    Tags: Development
    """
    permission_classes = [permissions.AllowAny]  # Only for development
    
    @extend_schema(
        request={'application/json': {'type': 'object', 'properties': {'category_id': {'type': 'integer'}}}},
        responses={200: OpenApiResponse(description="Test servicemen created")}
    )
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
    
    @extend_schema(
        request={'application/json': {'type': 'object', 'properties': {'email': {'type': 'string'}}}},
        responses={200: OpenApiResponse(description="Password reset email sent")}
    )
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
    
    @extend_schema(
        request={'application/json': {'type': 'object', 'properties': {'password': {'type': 'string'}}}},
        responses={200: OpenApiResponse(description="Password reset successfully")}
    )
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
    
    @extend_schema(
        request={'application/json': {'type': 'object', 'properties': {'email': {'type': 'string'}}}},
        responses={200: OpenApiResponse(description="Test email sent")}
    )
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
    
    Tags: Public
    """
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        parameters=[
            {
                'name': 'category',
                'in': 'query',
                'description': 'Filter by skill category',
                'required': False,
                'schema': {'type': 'string', 'enum': ['TECHNICAL', 'MANUAL', 'CREATIVE', 'PROFESSIONAL', 'OTHER']}
            }
        ],
        responses={
            200: OpenApiResponse(description="List of active skills"),
            503: OpenApiResponse(description="Database migration required")
        }
    )
    def get(self, request, *args, **kwargs):
        from django.db import connection
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Check if Skills table exists
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'users_skill'
                    );
                """)
                table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                logger.warning("Skills table does not exist - returning empty list")
                return Response([], status=200)
                
        except Exception as e:
            logger.error(f"Error checking Skills table existence: {e}")
            return Response([], status=200)
        
        # Proceed with normal list
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        try:
            queryset = Skill.objects.filter(is_active=True)
            
            # Filter by category if provided
            category = self.request.query_params.get('category', None)
            if category:
                queryset = queryset.filter(category=category.upper())
            
            return queryset
        except Exception:
            # Skills table doesn't exist yet, return empty queryset
            return Skill.objects.none()


class SkillDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific skill by ID.
    
    Public endpoint - no authentication required.
    """
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        try:
            return Skill.objects.filter(is_active=True)
        except Exception:
            return Skill.objects.none()
    
    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception:
            return Response({"detail": "Skills feature not available yet"}, status=404)


class SkillCreateView(generics.CreateAPIView):
    """
    Create a new skill (Admin only).
    
    Only administrators can create new skills.
    Skills are used by servicemen to showcase their expertise.
    
    Body:
    {
        "name": "string (required)",
        "category": "string (optional - TECHNICAL, MANUAL, CREATIVE, PROFESSIONAL, OTHER)",
        "description": "string (optional)"
    }
    
    Tags: Admin
    """
    serializer_class = SkillCreateSerializer
    permission_classes = [IsAdmin]
    
    @extend_schema(
        request={'application/json': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'maxLength': 100},
                'category': {'type': 'string', 'enum': ['TECHNICAL', 'MANUAL', 'CREATIVE', 'PROFESSIONAL', 'OTHER']},
                'description': {'type': 'string'}
            },
            'required': ['name']
        }},
        responses={
            201: OpenApiResponse(description="Skill created successfully"),
            400: OpenApiResponse(description="Invalid input data"),
            403: OpenApiResponse(description="Only administrators can create skills"),
            503: OpenApiResponse(description="Database migration required")
        }
    )
    def post(self, request, *args, **kwargs):
        from django.db import connection
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Check if Skills table exists
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'users_skill'
                    );
                """)
                table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                logger.error("Skills table does not exist - migration needed")
                return Response({
                    "error": "Database migration required",
                    "detail": "The skills system requires database migrations to be run. "
                             "Please contact the administrator to run: python manage.py migrate users"
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        except Exception as e:
            logger.error(f"Error checking Skills table existence: {e}")
            return Response({
                "error": "Database error",
                "detail": "Unable to verify database schema. Please try again later."
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Proceed with normal creation
        return super().post(request, *args, **kwargs)
    
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
    
    def get_queryset(self):
        try:
            return Skill.objects.all()
        except Exception:
            return Skill.objects.none()


class SkillDeleteView(generics.DestroyAPIView):
    """
    Soft delete a skill (Admin only).
    
    Marks skill as inactive instead of deleting it.
    This preserves data integrity and historical records.
    """
    serializer_class = SkillSerializer
    permission_classes = [IsAdmin]
    
    def get_queryset(self):
        try:
            return Skill.objects.all()
        except Exception:
            return Skill.objects.none()
    
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
    serializer_class = SkillSerializer
    
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
# ADMIN MANAGEMENT VIEWS
# ============================================================================

class AdminAssignServicemanCategoryView(APIView):
    """
    Assign or reassign a serviceman to a category (Admin only).
    
    Allows admin to:
    - Assign serviceman to a category
    - Change serviceman's category
    - Remove category assignment (set to null)
    
    Body:
    {
        "serviceman_id": int,
        "category_id": int (or null to remove)
    }
    
    Tags: Admin
    """
    permission_classes = [IsAdmin]
    
    @extend_schema(
        request={'application/json': {
            'type': 'object',
            'properties': {
                'serviceman_id': {'type': 'integer'},
                'category_id': {'type': 'integer', 'nullable': True}
            }
        }},
        responses={200: OpenApiResponse(description="Category assigned successfully")}
    )
    def post(self, request):
        from apps.services.models import Category
        
        serviceman_id = request.data.get('serviceman_id')
        category_id = request.data.get('category_id')
        
        # Validate required fields
        if serviceman_id is None:
            return Response({
                "detail": "serviceman_id is required"
            }, status=400)
        
        # Get serviceman
        try:
            user = User.objects.get(id=serviceman_id, user_type='SERVICEMAN')
        except User.DoesNotExist:
            return Response({
                "detail": f"Serviceman with ID {serviceman_id} not found"
            }, status=404)
        
        # Get category (if provided)
        category = None
        if category_id is not None:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response({
                    "detail": f"Category with ID {category_id} not found"
                }, status=404)
        
        # Update serviceman category
        profile = user.serviceman_profile
        old_category = profile.category
        profile.category = category
        profile.save()
        
        # Prepare response
        response_data = {
            "detail": "Category assignment updated successfully",
            "serviceman": {
                "id": user.id,
                "username": user.username,
                "full_name": user.get_full_name()
            },
            "previous_category": {
                "id": old_category.id if old_category else None,
                "name": old_category.name if old_category else None
            } if old_category else None,
            "new_category": {
                "id": category.id if category else None,
                "name": category.name if category else None
            } if category else None
        }
        
        # Log the change
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"Admin {request.user.username} changed serviceman {user.username}'s "
            f"category from {old_category} to {category}"
        )
        
        return Response(response_data, status=200)


class AdminBulkAssignCategoryView(APIView):
    """
    Bulk assign multiple servicemen to a category (Admin only).
    
    Useful for:
    - Assigning new servicemen to categories
    - Moving servicemen between categories
    - Organizing servicemen by expertise
    
    Body:
    {
        "serviceman_ids": [1, 2, 3, 4, 5],
        "category_id": 2
    }
    
    Tags: Admin
    """
    permission_classes = [IsAdmin]
    
    @extend_schema(
        request={'application/json': {
            'type': 'object',
            'properties': {
                'serviceman_ids': {'type': 'array', 'items': {'type': 'integer'}},
                'category_id': {'type': 'integer'}
            }
        }},
        responses={200: OpenApiResponse(description="Servicemen assigned to category successfully")}
    )
    def post(self, request):
        from apps.services.models import Category
        
        serviceman_ids = request.data.get('serviceman_ids', [])
        category_id = request.data.get('category_id')
        
        # Validate
        if not serviceman_ids:
            return Response({
                "detail": "serviceman_ids array is required"
            }, status=400)
        
        if category_id is None:
            return Response({
                "detail": "category_id is required"
            }, status=400)
        
        # Get category
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({
                "detail": f"Category with ID {category_id} not found"
            }, status=404)
        
        # Get servicemen
        servicemen = User.objects.filter(
            id__in=serviceman_ids,
            user_type='SERVICEMAN'
        )
        
        if servicemen.count() == 0:
            return Response({
                "detail": "No valid servicemen found with provided IDs"
            }, status=404)
        
        # Update categories
        updated_count = 0
        updated_servicemen = []
        
        for serviceman in servicemen:
            profile = serviceman.serviceman_profile
            profile.category = category
            profile.save()
            updated_count += 1
            updated_servicemen.append({
                "id": serviceman.id,
                "username": serviceman.username,
                "full_name": serviceman.get_full_name()
            })
        
        # Log the change
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"Admin {request.user.username} assigned {updated_count} servicemen "
            f"to category '{category.name}'"
        )
        
        return Response({
            "detail": f"Successfully assigned {updated_count} servicemen to category '{category.name}'",
            "category": {
                "id": category.id,
                "name": category.name
            },
            "updated_servicemen": updated_servicemen,
            "total_updated": updated_count,
            "not_found": len(serviceman_ids) - updated_count
        }, status=200)


class AdminGetServicemenByCategoryView(APIView):
    """
    Get servicemen grouped by category for admin management (Admin only).
    
    Returns all servicemen organized by their categories.
    Useful for admin dashboard to see category distribution.
    
    Tags: Admin
    """
    permission_classes = [IsAdmin]
    serializer_class = ServicemanProfileSerializer
    
    @extend_schema(
        responses={
            200: OpenApiResponse(description="Servicemen grouped by category"),
            403: OpenApiResponse(description="Only administrators can access this endpoint"),
            503: OpenApiResponse(description="Database error or migration required")
        }
    )
    def get(self, request):
        from apps.services.models import Category
        from django.db.models import Count
        from django.db import connection
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Check if approval fields exist in database
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users_servicemanprofile'
                    AND column_name IN ('is_approved', 'is_available', 'rating', 'total_jobs_completed')
                """)
                existing_columns = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error checking ServicemanProfile columns: {e}")
            existing_columns = []
        
        has_approval_fields = 'is_approved' in existing_columns
        has_availability_field = 'is_available' in existing_columns
        has_rating_field = 'rating' in existing_columns
        has_jobs_field = 'total_jobs_completed' in existing_columns
        
        # Get all categories with servicemen count
        try:
            categories = Category.objects.annotate(
                servicemen_count=Count('servicemanprofile')
            ).order_by('name')
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return Response({
                "error": "Database error",
                "detail": "Unable to retrieve categories. Please try again later."
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        result = []
        total_servicemen = 0
        
        for category in categories:
            # Get servicemen in this category
            try:
                servicemen = User.objects.filter(
                    user_type='SERVICEMAN',
                    serviceman_profile__category=category
                ).select_related('serviceman_profile')
                
                servicemen_data = []
                for s in servicemen:
                    profile = s.serviceman_profile
                    
                    serviceman_info = {
                        "id": s.id,
                        "username": s.username,
                        "full_name": s.get_full_name() or s.username,
                        "email": s.email,
                    }
                    
                    # Add fields only if they exist in database
                    if has_availability_field:
                        serviceman_info["is_available"] = getattr(profile, 'is_available', True)
                    
                    if has_approval_fields:
                        serviceman_info["is_approved"] = getattr(profile, 'is_approved', True)
                    
                    if has_rating_field:
                        serviceman_info["rating"] = float(getattr(profile, 'rating', 0.0))
                    
                    if has_jobs_field:
                        serviceman_info["total_jobs_completed"] = getattr(profile, 'total_jobs_completed', 0)
                    
                    servicemen_data.append(serviceman_info)
                
                total_servicemen += len(servicemen_data)
                
                result.append({
                    "category": {
                        "id": category.id,
                        "name": category.name,
                        "description": category.description
                    },
                    "servicemen_count": len(servicemen_data),
                    "servicemen": servicemen_data
                })
                
            except Exception as e:
                logger.error(f"Error processing category {category.name}: {e}")
                continue
        
        # Get unassigned servicemen (no category)
        try:
            unassigned = User.objects.filter(
                user_type='SERVICEMAN',
                serviceman_profile__category__isnull=True
            ).select_related('serviceman_profile')
            
            if unassigned.exists():
                unassigned_data = []
                for s in unassigned:
                    profile = s.serviceman_profile
                    
                    serviceman_info = {
                        "id": s.id,
                        "username": s.username,
                        "full_name": s.get_full_name() or s.username,
                        "email": s.email,
                    }
                    
                    # Add fields only if they exist in database
                    if has_availability_field:
                        serviceman_info["is_available"] = getattr(profile, 'is_available', True)
                    
                    if has_approval_fields:
                        serviceman_info["is_approved"] = getattr(profile, 'is_approved', True)
                    
                    if has_rating_field:
                        serviceman_info["rating"] = float(getattr(profile, 'rating', 0.0))
                    
                    if has_jobs_field:
                        serviceman_info["total_jobs_completed"] = getattr(profile, 'total_jobs_completed', 0)
                    
                    unassigned_data.append(serviceman_info)
                
                result.append({
                    "category": None,
                    "servicemen_count": len(unassigned_data),
                    "servicemen": unassigned_data,
                    "note": "Unassigned servicemen - no category set"
                })
                total_servicemen += len(unassigned_data)
                
        except Exception as e:
            logger.error(f"Error processing unassigned servicemen: {e}")
        
        return Response({
            "total_servicemen": total_servicemen,
            "total_categories": categories.count(),
            "categories": result,
            "database_status": {
                "has_approval_fields": has_approval_fields,
                "has_availability_field": has_availability_field,
                "has_rating_field": has_rating_field,
                "has_jobs_field": has_jobs_field
            }
        })


class AdminPendingServicemenView(generics.ListAPIView):
    """
    List pending serviceman applications awaiting approval (Admin only).
    
    Returns all servicemen who have registered but not yet been approved by admin.
    Shows complete profile information for admin review.
    
    Tags: Admin
    """
    serializer_class = ServicemanProfileSerializer
    permission_classes = [IsAdmin]
    
    def get_queryset(self):
        from django.core.exceptions import FieldError
        from django.db import connection
        
        # Check which fields exist in the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users_servicemanprofile'
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Start with basic queryset
        queryset = ServicemanProfile.objects.all()
        
        # Defer fields that don't exist yet
        fields_to_defer = []
        potential_new_fields = ['is_approved', 'approved_by_id', 'approved_at', 'rejection_reason']
        
        for field in potential_new_fields:
            if field not in existing_columns:
                fields_to_defer.append(field.replace('_id', ''))  # approved_by_id -> approved_by
        
        if fields_to_defer:
            queryset = queryset.defer(*fields_to_defer)
        
        # Try to filter by is_approved (only if field exists)
        if 'is_approved' in existing_columns:
            queryset = queryset.filter(is_approved=False)
        
        return queryset.order_by('created_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        total_pending = queryset.count()
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            "total_pending": total_pending,
            "pending_applications": serializer.data
        })


class AdminApproveServicemanView(APIView):
    """
    Approve a serviceman application (Admin only).
    
    Approves a serviceman, allowing them to:
    - Be assigned to service requests
    - Appear in public servicemen listings
    - Accept jobs and work
    
    Body:
    {
        "serviceman_id": int,
        "category_id": int (optional - assign category during approval),
        "notes": string (optional - internal notes)
    }
    
    Tags: Admin
    """
    permission_classes = [IsAdmin]
    
    @extend_schema(
        request={'application/json': {
            'type': 'object',
            'properties': {
                'serviceman_id': {'type': 'integer'},
                'category_id': {'type': 'integer', 'nullable': True},
                'notes': {'type': 'string'}
            },
            'required': ['serviceman_id']
        }},
        responses={200: OpenApiResponse(description="Serviceman approved successfully")}
    )
    def post(self, request):
        from apps.services.models import Category
        from django.utils import timezone
        from django.db import connection
        import logging
        
        logger = logging.getLogger(__name__)
        
        serviceman_id = request.data.get('serviceman_id')
        category_id = request.data.get('category_id')
        notes = request.data.get('notes', '')
        
        # Validate
        if not serviceman_id:
            return Response({
                "detail": "serviceman_id is required"
            }, status=400)
        
        # Get serviceman
        try:
            user = User.objects.get(id=serviceman_id, user_type='SERVICEMAN')
        except User.DoesNotExist:
            return Response({
                "detail": f"Serviceman with ID {serviceman_id} not found"
            }, status=404)
        
        profile = user.serviceman_profile
        
        # Check if approval fields exist in database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users_servicemanprofile'
                AND column_name IN ('is_approved', 'approved_by_id', 'approved_at', 'rejection_reason')
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
        
        has_approval_fields = 'is_approved' in existing_columns
        
        if not has_approval_fields:
            logger.error("Approval fields do not exist in database - migration needed")
            return Response({
                "error": "Database migration required",
                "detail": "The approval system requires database migrations to be run. "
                         "Please contact the administrator to run: python manage.py migrate users"
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Check if already approved (safe to access now)
        if getattr(profile, 'is_approved', False):
            return Response({
                "detail": "This serviceman is already approved"
            }, status=400)
        
        # Get category if provided
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                profile.category = category
            except Category.DoesNotExist:
                return Response({
                    "detail": f"Category with ID {category_id} not found"
                }, status=404)
        
        # Approve serviceman
        profile.is_approved = True
        profile.approved_by = request.user
        profile.approved_at = timezone.now()
        profile.save()
        
        # Send approval notification
        try:
            from apps.notifications.models import Notification
            Notification.objects.create(
                user=user,
                notification_type='SERVICE_ASSIGNED',  # Using existing type
                title='Serviceman Application Approved',
                message=f'Congratulations! Your serviceman application has been approved by {request.user.username}. '
                        f'You can now be assigned to service requests and start accepting jobs. '
                        f'{f"You have been assigned to category: {profile.category.name}." if profile.category else ""}',
                is_read=False
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to send approval notification: {e}")
        
        # Log the approval
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"Admin {request.user.username} approved serviceman {user.username} (ID: {user.id}). "
            f"Category: {profile.category.name if profile.category else 'Not assigned'}. Notes: {notes}"
        )
        
        return Response({
            "detail": "Serviceman application approved successfully",
            "serviceman": {
                "id": user.id,
                "username": user.username,
                "full_name": user.get_full_name(),
                "email": user.email
            },
            "approved_by": request.user.username,
            "approved_at": profile.approved_at,
            "category": {
                "id": profile.category.id if profile.category else None,
                "name": profile.category.name if profile.category else None
            } if profile.category else None
        }, status=200)


class AdminRejectServicemanView(APIView):
    """
    Reject a serviceman application (Admin only).
    
    Rejects a serviceman application and optionally provides a reason.
    The serviceman remains in the system but cannot be assigned to jobs.
    
    Body:
    {
        "serviceman_id": int,
        "rejection_reason": string (required)
    }
    
    Tags: Admin
    """
    permission_classes = [IsAdmin]
    
    @extend_schema(
        request={'application/json': {
            'type': 'object',
            'properties': {
                'serviceman_id': {'type': 'integer'},
                'rejection_reason': {'type': 'string'}
            },
            'required': ['serviceman_id', 'rejection_reason']
        }},
        responses={200: OpenApiResponse(description="Serviceman rejected")}
    )
    def post(self, request):
        from django.db import connection
        import logging
        
        logger = logging.getLogger(__name__)
        
        serviceman_id = request.data.get('serviceman_id')
        rejection_reason = request.data.get('rejection_reason', '')
        
        # Validate
        if not serviceman_id:
            return Response({
                "detail": "serviceman_id is required"
            }, status=400)
        
        if not rejection_reason:
            return Response({
                "detail": "rejection_reason is required"
            }, status=400)
        
        # Get serviceman
        try:
            user = User.objects.get(id=serviceman_id, user_type='SERVICEMAN')
        except User.DoesNotExist:
            return Response({
                "detail": f"Serviceman with ID {serviceman_id} not found"
            }, status=404)
        
        profile = user.serviceman_profile
        
        # Check if approval fields exist in database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users_servicemanprofile'
                AND column_name IN ('is_approved', 'rejection_reason')
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
        
        has_approval_fields = 'is_approved' in existing_columns
        
        if not has_approval_fields:
            logger.error("Approval fields do not exist in database - migration needed")
            return Response({
                "error": "Database migration required",
                "detail": "The approval system requires database migrations to be run. "
                         "Please contact the administrator to run: python manage.py migrate users"
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Check if already approved (safe to access now)
        if getattr(profile, 'is_approved', False):
            return Response({
                "detail": "Cannot reject an already approved serviceman. Consider deactivating their account instead."
            }, status=400)
        
        # Reject application
        profile.rejection_reason = rejection_reason
        profile.save()
        
        # Send rejection notification
        try:
            from apps.notifications.models import Notification
            Notification.objects.create(
                user=user,
                notification_type='SERVICE_ASSIGNED',
                title='Serviceman Application Update',
                message=f'We regret to inform you that your serviceman application has not been approved at this time. '
                        f'Reason: {rejection_reason}. '
                        f'If you have questions, please contact support.',
                is_read=False
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to send rejection notification: {e}")
        
        # Log the rejection
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"Admin {request.user.username} rejected serviceman {user.username} (ID: {user.id}). "
            f"Reason: {rejection_reason}"
        )
        
        return Response({
            "detail": "Serviceman application rejected",
            "serviceman": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            "rejected_by": request.user.username,
            "rejection_reason": rejection_reason
        }, status=200)


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