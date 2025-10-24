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
        import traceback
        import logging
        
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
            
            logger.info(f"Existing columns in users_servicemanprofile: {existing_columns}")
            
            # Determine which fields to defer from ServicemanProfile
            from django.db.models import Prefetch
            from apps.users.models import ServicemanProfile
            
            fields_to_defer = []
            potential_new_fields = ['is_approved', 'approved_by_id', 'approved_at', 'rejection_reason']
            
            for field in potential_new_fields:
                if field not in existing_columns:
                    defer_name = field.replace('_id', '') if field.endswith('_id') else field
                    fields_to_defer.append(defer_name)
            
            logger.info(f"Fields to defer: {fields_to_defer}")
            
            # Build ServicemanProfile queryset with deferred fields
            profile_qs = ServicemanProfile.objects.all()
            if fields_to_defer:
                profile_qs = profile_qs.defer(*fields_to_defer)
            
            # Build queryset with safe prefetch
            servicemen = User.objects.filter(
                user_type='SERVICEMAN',
                serviceman_profile__category_id=pk
            ).prefetch_related(
                Prefetch('serviceman_profile', queryset=profile_qs)
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
            
            # Simple order - avoid ordering by deferred fields
            servicemen = servicemen.order_by('id')
            
            logger.info(f"Queryset created, count: {servicemen.count()}")
            
            data = []
            available_count = 0
            busy_count = 0
            
            for s in servicemen:
                try:
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
                except Exception as e:
                    logger.error(f"Error processing serviceman {s.id}: {str(e)}")
                    logger.error(traceback.format_exc())
                    # Skip this serviceman and continue
                    continue
            
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
            
        except Exception as e:
            logger.error(f"Error in CategoryServicemenListView: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {
                    "error": "Internal server error",
                    "detail": str(e),
                    "traceback": traceback.format_exc()
                },
                status=500
            )

# --- ServiceRequest Views ---

class ServiceRequestListCreateView(generics.ListCreateAPIView):
    """
    List service requests or create a new one.
    
    GET: Authenticated users see their relevant requests
    POST: Clients only - Create a new service request
    
    IMPORTANT: Client must pay booking fee first!
    1. Call POST /api/payments/initialize-booking-fee/ to get payment URL
    2. User pays on Paystack
    3. Call POST /api/payments/verify/ to confirm payment
    4. Call POST /api/services/requests/ with payment_reference to create request
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
    
    def create(self, request, *args, **kwargs):
        """Create service request only if booking fee is paid"""
        from apps.payments.models import Payment
        
        # Get payment reference from request
        payment_reference = request.data.get('payment_reference')
        
        if not payment_reference:
            return Response({
                "error": "Payment required",
                "detail": "You must pay the booking fee before creating a service request. "
                         "Please call POST /api/payments/initialize-booking-fee/ first."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify payment exists and is successful
        try:
            payment = Payment.objects.get(paystack_reference=payment_reference)
        except Payment.DoesNotExist:
            return Response({
                "error": "Invalid payment reference",
                "detail": "The provided payment reference does not exist."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if payment.status != 'SUCCESSFUL':
            return Response({
                "error": "Payment not completed",
                "detail": f"Payment status is '{payment.status}'. Please complete payment first.",
                "payment_status": payment.status
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if payment.service_request is not None:
            return Response({
                "error": "Payment already used",
                "detail": "This payment has already been used for another service request.",
                "existing_request_id": payment.service_request.id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify payment amount matches the booking type
        is_emergency = request.data.get('is_emergency', False)
        expected_amount = 5000 if is_emergency else 2000
        
        if float(payment.amount) != float(expected_amount):
            return Response({
                "error": "Payment amount mismatch",
                "detail": f"Expected ₦{expected_amount:,.2f} for {'emergency' if is_emergency else 'normal'} booking, "
                         f"but payment was ₦{payment.amount:,.2f}. "
                         f"Please initialize payment again with correct booking type."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the service request
        response = super().create(request, *args, **kwargs)
        
        # Link payment to service request
        if response.status_code == status.HTTP_201_CREATED:
            service_request_id = response.data['id']
            service_request = ServiceRequest.objects.get(id=service_request_id)
            payment.service_request = service_request
            payment.save()
            
            # Add payment info to response
            response.data['payment_reference'] = payment_reference
            response.data['payment_amount'] = str(payment.amount)
        
        return response
    
    def perform_create(self, serializer):
        serializer.save()

class ServiceRequestDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update a specific service request.
    
    Access control:
    - Admins: Can view and update all requests
    - Clients: Can view and update their own requests (limited fields)
    - Servicemen: Can view assigned requests (primary or backup), limited updates
    
    Update permissions:
    - Admins: Can update all fields including serviceman assignment
    - Clients: Can update description, address, booking_date
    - Servicemen: Can update status, estimated_cost (when assigned)
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
    
    def get_serializer_class(self):
        """Return different serializers based on user type and action"""
        if self.request.method == 'GET':
            return ServiceRequestSerializer
        
        user = self.request.user
        if user.user_type == 'ADMIN':
            return ServiceRequestSerializer  # Admins can update everything
        elif user.user_type == 'CLIENT':
            return ServiceRequestSerializer  # Clients can update their requests
        elif user.user_type == 'SERVICEMAN':
            return ServiceRequestSerializer  # Servicemen can update assigned requests
        else:
            return ServiceRequestSerializer
    
    def perform_update(self, serializer):
        """Custom update logic based on user type"""
        user = self.request.user
        instance = self.get_object()
        
        # Log the update
        import logging
        logger = logging.getLogger(__name__)
        
        if user.user_type == 'ADMIN':
            # Admins can update everything
            logger.info(f"Admin {user.username} updated service request {instance.id}")
            serializer.save()
            
        elif user.user_type == 'CLIENT':
            # Clients can update their own requests (limited fields)
            if instance.client != user:
                raise permissions.PermissionDenied("You can only update your own service requests")
            
            # Only allow updating certain fields
            allowed_fields = ['service_description', 'client_address', 'booking_date']
            for field in allowed_fields:
                if field in serializer.validated_data:
                    setattr(instance, field, serializer.validated_data[field])
            
            instance.save()
            logger.info(f"Client {user.username} updated service request {instance.id}")
            
        elif user.user_type == 'SERVICEMAN':
            # Servicemen can update assigned requests
            if instance.serviceman != user and instance.backup_serviceman != user:
                raise permissions.PermissionDenied("You can only update requests assigned to you")
            
            # Servicemen can update status and estimated cost
            allowed_fields = ['status', 'serviceman_estimated_cost']
            for field in allowed_fields:
                if field in serializer.validated_data:
                    setattr(instance, field, serializer.validated_data[field])
            
            instance.save()
            logger.info(f"Serviceman {user.username} updated service request {instance.id}")
        
        else:
            raise permissions.PermissionDenied()


class ServiceRequestAssignView(APIView):
    """
    Assign servicemen to service requests (Admin only).
    
    This endpoint allows admins to:
    - Assign a primary serviceman to a request
    - Assign a backup serviceman to a request
    - Update serviceman assignments
    - Remove serviceman assignments
    
    Body:
    {
        "serviceman_id": int (optional - primary serviceman),
        "backup_serviceman_id": int (optional - backup serviceman),
        "notes": string (optional - assignment notes)
    }
    
    Tags: Admin
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request={'application/json': {
            'type': 'object',
            'properties': {
                'serviceman_id': {'type': 'integer', 'nullable': True},
                'backup_serviceman_id': {'type': 'integer', 'nullable': True},
                'notes': {'type': 'string'}
            }
        }},
        responses={
            200: OpenApiResponse(description="Servicemen assigned successfully"),
            400: OpenApiResponse(description="Invalid serviceman ID or validation error"),
            403: OpenApiResponse(description="Only administrators can assign servicemen"),
            404: OpenApiResponse(description="Service request or serviceman not found")
        }
    )
    def post(self, request, pk):
        from apps.users.models import User
        from django.utils import timezone
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Check if user is admin
        if request.user.user_type != 'ADMIN':
            return Response({
                "detail": "Only administrators can assign servicemen to service requests"
            }, status=403)
        
        # Get service request
        try:
            service_request = ServiceRequest.objects.get(pk=pk)
        except ServiceRequest.DoesNotExist:
            return Response({
                "detail": f"Service request with ID {pk} not found"
            }, status=404)
        
        serviceman_id = request.data.get('serviceman_id')
        backup_serviceman_id = request.data.get('backup_serviceman_id')
        notes = request.data.get('notes', '')
        
        # Validate serviceman IDs
        serviceman = None
        backup_serviceman = None
        
        if serviceman_id:
            try:
                serviceman = User.objects.get(id=serviceman_id, user_type='SERVICEMAN')
                # Check if serviceman is approved
                if hasattr(serviceman, 'serviceman_profile') and not getattr(serviceman.serviceman_profile, 'is_approved', True):
                    return Response({
                        "detail": f"Serviceman {serviceman.username} is not approved yet"
                    }, status=400)
            except User.DoesNotExist:
                return Response({
                    "detail": f"Serviceman with ID {serviceman_id} not found"
                }, status=404)
        
        if backup_serviceman_id:
            try:
                backup_serviceman = User.objects.get(id=backup_serviceman_id, user_type='SERVICEMAN')
                # Check if backup serviceman is approved
                if hasattr(backup_serviceman, 'serviceman_profile') and not getattr(backup_serviceman.serviceman_profile, 'is_approved', True):
                    return Response({
                        "detail": f"Backup serviceman {backup_serviceman.username} is not approved yet"
                    }, status=400)
            except User.DoesNotExist:
                return Response({
                    "detail": f"Backup serviceman with ID {backup_serviceman_id} not found"
                }, status=404)
        
        # Prevent assigning same serviceman as both primary and backup
        if serviceman_id and backup_serviceman_id and serviceman_id == backup_serviceman_id:
            return Response({
                "detail": "Primary and backup servicemen cannot be the same person"
            }, status=400)
        
        # Update assignments
        old_serviceman = service_request.serviceman
        old_backup = service_request.backup_serviceman
        
        if serviceman_id is not None:
            service_request.serviceman = serviceman
        if backup_serviceman_id is not None:
            service_request.backup_serviceman = backup_serviceman
        
        # Update status if assigning serviceman
        if serviceman and service_request.status == 'PENDING':
            service_request.status = 'ASSIGNED'
        
        service_request.save()
        
        # Send notifications
        try:
            from apps.notifications.models import Notification
            
            # Notify primary serviceman
            if serviceman and serviceman != old_serviceman:
                Notification.objects.create(
                    user=serviceman,
                    notification_type='SERVICE_ASSIGNED',
                    title='New Service Request Assignment',
                    message=f'You have been assigned to a new service request #{service_request.id}. '
                            f'Category: {service_request.category.name}. '
                            f'Date: {service_request.booking_date}. '
                            f'Address: {service_request.client_address}. '
                            f'{f"Notes: {notes}" if notes else ""}',
                    is_read=False
                )
            
            # Notify backup serviceman
            if backup_serviceman and backup_serviceman != old_backup:
                Notification.objects.create(
                    user=backup_serviceman,
                    notification_type='SERVICE_ASSIGNED',
                    title='Service Request Backup Assignment',
                    message=f'You have been assigned as backup serviceman for request #{service_request.id}. '
                            f'Category: {service_request.category.name}. '
                            f'Date: {service_request.booking_date}.',
                    is_read=False
                )
            
            # Notify client
            Notification.objects.create(
                user=service_request.client,
                notification_type='SERVICE_ASSIGNED',
                title='Service Request Update',
                message=f'Your service request #{service_request.id} has been assigned to a serviceman. '
                        f'You will be contacted soon to discuss the details.',
                is_read=False
            )
            
        except Exception as e:
            logger.error(f"Failed to send assignment notifications: {e}")
        
        # Log the assignment
        logger.info(
            f"Admin {request.user.username} assigned servicemen to request {service_request.id}. "
            f"Primary: {serviceman.username if serviceman else 'None'}, "
            f"Backup: {backup_serviceman.username if backup_serviceman else 'None'}. "
            f"Notes: {notes}"
        )
        
        return Response({
            "detail": "Servicemen assigned successfully",
            "service_request": {
                "id": service_request.id,
                "status": service_request.status,
                "serviceman": {
                    "id": serviceman.id,
                    "username": serviceman.username,
                    "email": serviceman.email
                } if serviceman else None,
                "backup_serviceman": {
                    "id": backup_serviceman.id,
                    "username": backup_serviceman.username,
                    "email": backup_serviceman.email
                } if backup_serviceman else None,
                "assigned_by": request.user.username,
                "assigned_at": timezone.now().isoformat(),
                "notes": notes
            }
        }, status=200)