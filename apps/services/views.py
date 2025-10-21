from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Category, ServiceRequest
from .serializers import (
    CategorySerializer, CategoryCreateSerializer, ServiceRequestSerializer
)
from .permissions import (
    IsAdmin, IsClient, IsServiceman, IsRequestOwner, IsAssignedServiceman
)
from apps.users.models import User

# --- Category Views ---

class CategoryListCreateView(generics.ListCreateAPIView):
    """
    List all active categories (Public) or create a new category (Admin only).
    
    GET: Public access - Returns all active categories
    POST: Admin only - Create a new category
    """
    queryset = Category.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CategoryCreateSerializer
        return CategorySerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        # For POST requests (create), use all categories
        if self.request.method == 'POST':
            return Category.objects.all()
        # For GET requests (list), only show active categories
        return Category.objects.filter(is_active=True)

class CategoryDetailUpdateView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a category.
    
    GET: Public access - View category details
    PUT/PATCH: Admin only - Update category
    """
    queryset = Category.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CategoryCreateSerializer
        return CategorySerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [IsAdmin()]
        return [permissions.AllowAny()]

class CategoryServicemenListView(APIView):
    """
    List servicemen in a category with availability status.
    
    Response includes:
    - Serviceman details
    - Availability status (available/busy)
    - Active jobs count
    - Warnings if busy
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        responses={200: OpenApiResponse(description="Servicemen in category with availability")}
    )
    def get(self, request, pk):
        from django.db.models import Q, Count, Case, When, IntegerField
        from django.db import connection
        
        # Check which fields exist in the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users_servicemanprofile'
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Determine which fields to defer
        fields_to_defer = []
        potential_new_fields = ['is_approved', 'approved_by_id', 'approved_at', 'rejection_reason']
        
        for field in potential_new_fields:
            if field not in existing_columns:
                # Don't add _id suffix for FK fields when deferring
                defer_name = field.replace('_id', '') if field.endswith('_id') else field
                fields_to_defer.append(defer_name)
        
        # Build queryset - don't use select_related yet
        servicemen = User.objects.filter(
            user_type='SERVICEMAN',
            serviceman_profile__category_id=pk
        ).annotate(
            active_jobs_count=Count(
                Case(
                    When(
                        Q(serviceman_requests__status='IN_PROGRESS', serviceman_requests__is_deleted=False) |
                        Q(backup_requests__status='IN_PROGRESS', backup_requests__is_deleted=False),
                        then=1
                    ),
                    output_field=IntegerField()
                )
            )
        )
        
        # Only order by is_available if field exists
        if 'is_available' in existing_columns:
            servicemen = servicemen.order_by('-serviceman_profile__is_available', '-serviceman_profile__rating')
        else:
            servicemen = servicemen.order_by('-serviceman_profile__rating')
        
        data = []
        available_count = 0
        busy_count = 0
        
        for s in servicemen:
            # Safely get is_available (may not exist in database yet)
            is_available = getattr(s.serviceman_profile, 'is_available', True)
            active_jobs = s.active_jobs_count
            
            if is_available:
                available_count += 1
            else:
                busy_count += 1
            
            serviceman_data = {
                "id": s.id,
                "full_name": s.get_full_name() or s.username,
                "username": s.username,
                "rating": float(s.serviceman_profile.rating),
                "total_jobs_completed": s.serviceman_profile.total_jobs_completed,
                "bio": s.serviceman_profile.bio,
                "years_of_experience": s.serviceman_profile.years_of_experience,
                "is_available": is_available,
                "active_jobs_count": active_jobs,
                "availability_status": {
                    "status": "available" if is_available else "busy",
                    "label": "Available" if is_available else "Currently Busy",
                    "badge_color": "green" if is_available else "orange"
                }
            }
            
            # Add warning if busy
            if not is_available:
                serviceman_data["booking_warning"] = {
                    "message": f"This serviceman is currently working on {active_jobs} active job(s)",
                    "recommendation": "Consider choosing an available serviceman for faster service",
                    "can_still_book": True,
                    "estimated_delay": "Service may be delayed" if active_jobs > 1 else "Minor delay possible"
                }
            
            data.append(serviceman_data)
        
        # Build response with summary
        response_data = {
            "category_id": pk,
            "total_servicemen": len(data),
            "available_servicemen": available_count,
            "busy_servicemen": busy_count,
            "servicemen": data
        }
        
        # Add overall availability message
        if available_count == 0:
            response_data["availability_message"] = {
                "type": "warning",
                "message": f"All {busy_count} servicemen in this category are currently busy. You can still book, but please expect potential delays."
            }
        elif available_count < busy_count:
            response_data["availability_message"] = {
                "type": "info",
                "message": f"{available_count} available, {busy_count} busy. Choose available servicemen for immediate service."
            }
        else:
            response_data["availability_message"] = {
                "type": "success",
                "message": f"{available_count} servicemen are available for immediate service."
            }
        
        return Response(response_data)

# --- ServiceRequest Views ---

class ServiceRequestListCreateView(generics.ListCreateAPIView):
    """
    List service requests or create a new one.
    
    GET: Authenticated users see their relevant requests
    POST: Clients only - Create a new service request
    """
    serializer_class = ServiceRequestSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsClient()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        qs = ServiceRequest.objects.all()
        if user.user_type == 'ADMIN':
            return qs
        elif user.user_type == 'CLIENT':
            return qs.filter(client=user)
        elif user.user_type == 'SERVICEMAN':
            return qs.filter(serviceman=user) | qs.filter(backup_serviceman=user)
        return ServiceRequest.objects.none()
    
    def perform_create(self, serializer):
        serializer.save()

class ServiceRequestDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific service request.
    
    Access control:
    - Admins: Can view all requests
    - Clients: Can view their own requests
    - Servicemen: Can view assigned requests (primary or backup)
    """
    queryset = ServiceRequest.objects.all()
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        # Role-based access
        user = self.request.user
        if user.user_type == 'ADMIN':
            return obj
        if user.user_type == 'CLIENT' and obj.client == user:
            return obj
        if user.user_type == 'SERVICEMAN' and (obj.serviceman == user or obj.backup_serviceman == user):
            return obj
        raise permissions.PermissionDenied()