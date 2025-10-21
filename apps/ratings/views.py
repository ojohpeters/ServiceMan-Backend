from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Count
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Rating
from .serializers import RatingSerializer
from apps.services.models import ServiceRequest, Category
from apps.users.models import User

class RatingCreateView(generics.CreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        service_request = serializer.validated_data["service_request"]
        # Only allow client who owns the service request to create
        if service_request.client != user:
            raise permissions.PermissionDenied("You may only rate your own requests.")
        rating = serializer.validated_data["rating"]
        # Update serviceman profile stats
        serviceman_profile = service_request.serviceman.serviceman_profile
        # Update running average
        prev_total = serviceman_profile.total_jobs_completed
        prev_rating = serviceman_profile.rating
        new_avg = ((prev_rating * prev_total) + rating) / (prev_total + 1)
        serviceman_profile.rating = round(new_avg, 2)
        serviceman_profile.total_jobs_completed += 1
        serviceman_profile.save()
        serializer.save()

class RatingListView(generics.ListAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.AllowAny]  # Public access to view ratings
    queryset = Rating.objects.all()
    
    def get_queryset(self):
        queryset = Rating.objects.all()
        serviceman_id = self.request.query_params.get('serviceman_id')
        if serviceman_id:
            queryset = queryset.filter(service_request__serviceman_id=serviceman_id)
        return queryset

# --- Analytics Endpoints ---

class RevenueAnalyticsView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    @extend_schema(
        responses={200: OpenApiResponse(description="Revenue analytics")}
    )
    def get(self, request):
        from apps.payments.models import Payment
        from django.utils import timezone
        import datetime
        now = timezone.now()
        this_month = now.replace(day=1)
        total = Payment.objects.filter(status="SUCCESSFUL").aggregate(total=Count("amount"))["total"] or 0
        month = Payment.objects.filter(status="SUCCESSFUL", created_at__gte=this_month).aggregate(month=Count("amount"))["month"] or 0
        return Response({"total_revenue": total, "this_month": month})

class TopServicemenAnalyticsView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    @extend_schema(
        responses={200: OpenApiResponse(description="Top servicemen")}
    )
    def get(self, request):
        servicemen = User.objects.filter(user_type="SERVICEMAN").order_by("-serviceman_profile__rating", "-serviceman_profile__total_jobs_completed")[:10]
        data = [
            {
                "id": s.id,
                "full_name": s.get_full_name(),
                "rating": s.serviceman_profile.rating,
                "total_jobs_completed": s.serviceman_profile.total_jobs_completed,
            }
            for s in servicemen
        ]
        return Response(data)

class TopCategoriesAnalyticsView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    @extend_schema(
        responses={200: OpenApiResponse(description="Top categories")}
    )
    def get(self, request):
        qs = Category.objects.annotate(request_count=Count("servicerequest")).order_by("-request_count")[:10]
        data = [
            {"id": cat.id, "name": cat.name, "request_count": cat.request_count}
            for cat in qs
        ]
        return Response(data)