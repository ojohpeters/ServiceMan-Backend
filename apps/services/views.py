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

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
    permission_classes = [IsAdmin]  # Only admins can create categories

class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
    permission_classes = [IsAdmin]  # Only admins can update categories

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

class ServiceRequestCreateView(generics.CreateAPIView):
    serializer_class = ServiceRequestSerializer
    permission_classes = [IsClient]
    def perform_create(self, serializer):
        serializer.save()

class ServiceRequestDetailView(generics.RetrieveAPIView):
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
        raise permissions.PermissionDenied

class ServiceRequestListView(generics.ListAPIView):
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

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