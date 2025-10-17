from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
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
    permission_classes = [permissions.AllowAny]
    def get(self, request, pk):
        servicemen = User.objects.filter(
            user_type='SERVICEMAN',
            serviceman_profile__category_id=pk
        )
        data = [
            {
                "id": s.id,
                "full_name": s.get_full_name(),
                "rating": s.serviceman_profile.rating,
                "total_jobs_completed": s.serviceman_profile.total_jobs_completed,
                "bio": s.serviceman_profile.bio,
                "years_of_experience": s.serviceman_profile.years_of_experience,
            }
            for s in servicemen
        ]
        return Response(data)

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