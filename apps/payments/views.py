from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Payment
from .serializers import PaymentSerializer
from .paystack import initialize_payment, verify_payment
from apps.services.models import ServiceRequest
from django.utils import timezone
from decimal import Decimal
import logging
import traceback

logger = logging.getLogger(__name__)

# Booking fee constants
NORMAL_BOOKING_FEE = Decimal('2000.00')
EMERGENCY_BOOKING_FEE = Decimal('5000.00')

class InitializeBookingFeeView(APIView):
    """
    Initialize booking fee payment BEFORE creating a service request.
    
    Client must pay the booking fee first:
    - Normal booking: ₦2,000
    - Emergency booking: ₦5,000
    
    Returns Paystack payment URL for the client to complete payment.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request={'application/json': {
            'type': 'object',
            'properties': {
                'is_emergency': {'type': 'boolean', 'description': 'Whether this is an emergency booking'}
            },
            'required': ['is_emergency']
        }},
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'payment': {'type': 'object'},
                    'paystack_url': {'type': 'string'},
                    'amount': {'type': 'number'},
                    'reference': {'type': 'string'}
                }
            }
        }
    )
    def post(self, request):
        """Initialize booking fee payment"""
        try:
            logger.info(f"[InitializeBookingFee] Request received from user {request.user.id}")
            logger.info(f"[InitializeBookingFee] Request data: {request.data}")
            
            is_emergency = request.data.get('is_emergency', False)
            logger.info(f"[InitializeBookingFee] is_emergency: {is_emergency}")
            
            # Calculate booking fee
            amount = EMERGENCY_BOOKING_FEE if is_emergency else NORMAL_BOOKING_FEE
            logger.info(f"[InitializeBookingFee] Calculated amount: {amount}")
            
            # Generate unique reference
            timestamp = timezone.now().timestamp()
            reference = f"BOOKING-{request.user.id}-{timestamp}"
            logger.info(f"[InitializeBookingFee] Generated reference: {reference}")
            
            # Check FRONTEND_URL setting
            frontend_url = getattr(settings, 'FRONTEND_URL', None)
            logger.info(f"[InitializeBookingFee] FRONTEND_URL: {frontend_url}")
            
            if not frontend_url:
                logger.error("[InitializeBookingFee] FRONTEND_URL not configured in settings")
                return Response({
                    "error": "Server configuration error",
                    "detail": "FRONTEND_URL is not configured"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Initialize Paystack payment
            callback_url = frontend_url + "/payment/booking-callback"
            logger.info(f"[InitializeBookingFee] Callback URL: {callback_url}")
            
            logger.info(f"[InitializeBookingFee] Calling Paystack initialize_payment...")
            paystack_data = initialize_payment(
                amount=amount,
                email=request.user.email,
                reference=reference,
                callback_url=callback_url
            )
            logger.info(f"[InitializeBookingFee] Paystack response: {paystack_data}")
            
            # Create payment record (without service_request yet)
            # Migration-safe: check which columns exist in the database
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT column_name, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name='payments_payment' 
                    AND column_name IN ('is_emergency', 'service_request_id')
                """)
                column_info = {row[0]: row[1] == 'YES' for row in cursor.fetchall()}
            
            has_is_emergency = 'is_emergency' in column_info
            service_request_nullable = column_info.get('service_request_id', False)
            
            logger.info(f"[InitializeBookingFee] Column check - is_emergency exists: {has_is_emergency}, service_request nullable: {service_request_nullable}")
            logger.info(f"[InitializeBookingFee] Creating Payment record...")
            
            # If service_request is NOT NULL in DB, we can't create booking fee payments yet
            if not service_request_nullable:
                logger.error("[InitializeBookingFee] service_request_id is NOT NULL in database - migrations needed")
                return Response({
                    "error": "Database migration required",
                    "detail": "The booking fee payment feature requires database migrations to be run. "
                             "Please contact the administrator to run: python manage.py migrate payments"
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # Use raw SQL to create payment record to avoid ORM trying to insert is_emergency
            # when the column doesn't exist
            if has_is_emergency:
                # Column exists, use ORM normally
                payment = Payment.objects.create(
                    service_request=None,
                    payment_type='INITIAL_BOOKING',
                    amount=amount,
                    paystack_reference=paystack_data['reference'],
                    paystack_access_code=paystack_data['access_code'],
                    status='PENDING',
                    is_emergency=is_emergency
                )
            else:
                # is_emergency column doesn't exist yet, use raw SQL to insert only existing columns
                logger.info("[InitializeBookingFee] Using raw SQL (is_emergency column missing)")
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO payments_payment 
                        (service_request_id, payment_type, amount, paystack_reference, 
                         paystack_access_code, status, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, [
                        None,  # service_request_id (now nullable)
                        'INITIAL_BOOKING',  # payment_type
                        amount,
                        paystack_data['reference'],
                        paystack_data['access_code'],
                        'PENDING',
                        timezone.now(),
                        timezone.now()
                    ])
                    payment_id = cursor.fetchone()[0]
                
                # Fetch the created payment
                payment = Payment.objects.get(id=payment_id)
            
            logger.info(f"[InitializeBookingFee] Payment record created: ID={payment.id}")
            
            serializer = PaymentSerializer(payment)
            logger.info(f"[InitializeBookingFee] Success! Returning response")
            
            return Response({
                "payment": serializer.data,
                "paystack_url": paystack_data['authorization_url'],
                "amount": str(amount),
                "reference": reference,
                "message": f"Please complete payment of ₦{amount:,.2f} to proceed"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"[InitializeBookingFee] Error occurred: {str(e)}")
            logger.error(f"[InitializeBookingFee] Traceback: {traceback.format_exc()}")
            return Response({
                "error": "Failed to initialize payment",
                "detail": str(e),
                "traceback": traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InitializePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentSerializer

    @extend_schema(
        request={'application/json': {
            'type': 'object',
            'properties': {
                'service_request': {'type': 'integer'},
                'payment_type': {'type': 'string'},
                'amount': {'type': 'number'}
            }
        }},
        responses={201: PaymentSerializer}
    )
    def post(self, request):
        service_request_id = request.data.get('service_request')
        payment_type = request.data.get('payment_type')
        amount = request.data.get('amount')
        service_request = get_object_or_404(ServiceRequest, id=service_request_id)
        reference = f"{service_request_id}-{payment_type}-{timezone.now().timestamp()}"
        callback_url = settings.FRONTEND_URL + "/payment/callback"
        paystack_data = initialize_payment(
            amount=amount,
            email=request.user.email,
            reference=reference,
            callback_url=callback_url
        )

        payment = Payment.objects.create(
            service_request=service_request,
            payment_type=payment_type,
            amount=amount,
            paystack_reference=paystack_data['reference'],
            paystack_access_code=paystack_data['access_code'],
            status='PENDING'
        )
        serializer = PaymentSerializer(payment)
        return Response({
            "payment": serializer.data,
            "paystack_url": paystack_data['authorization_url']
        }, status=201)

class PaystackWebhookView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        exclude=True  # Exclude from API docs as it's only called by Paystack
    )
    def post(self, request):
        from django.http import HttpResponseForbidden
        import hmac, hashlib

        signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
        secret = settings.PAYSTACK_WEBHOOK_SECRET
        payload = request.body

        expected = hmac.new(
            key=secret.encode(),
            msg=payload,
            digestmod=hashlib.sha512
        ).hexdigest()
        if signature != expected:
            return HttpResponseForbidden("Invalid signature")

        import json
        event = json.loads(payload)
        if event['event'] == "charge.success":
            reference = event['data']['reference']
            payment = get_object_or_404(Payment, paystack_reference=reference)
            if payment.status != 'SUCCESSFUL':
                payment.status = 'SUCCESSFUL'
                payment.paid_at = timezone.now()
                payment.save()
                # Optionally: Send notifications, update ServiceRequest etc.
        return Response({"status": "ok"})

class PaymentVerifyView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        request={'application/json': {'type': 'object', 'properties': {'reference': {'type': 'string'}}}},
        responses={200: OpenApiResponse(description="Payment verification result")}
    )
    def post(self, request):
        reference = request.data.get('reference')
        paystack_data = verify_payment(reference)
        payment = get_object_or_404(Payment, paystack_reference=reference)
        if paystack_data['status'] == 'success':
            payment.status = 'SUCCESSFUL'
            payment.paid_at = timezone.now()
            payment.save()
            
            # STEP 5: Notify admin when client pays full amount (not booking fee)
            if payment.service_request and payment.payment_type == 'SERVICE_PAYMENT':
                try:
                    from apps.notifications.models import Notification
                    from django.contrib.auth import get_user_model
                    import logging
                    
                    logger = logging.getLogger(__name__)
                    User = get_user_model()
                    
                    # Update service request status
                    service_request = payment.service_request
                    service_request.status = 'PAYMENT_COMPLETED'
                    service_request.save()
                    
                    # Notify all admins
                    admins = User.objects.filter(user_type='ADMIN')
                    for admin in admins:
                        Notification.objects.create(
                            user=admin,
                            title=f'Payment Received - Request #{service_request.id}',
                            message=f'Client {service_request.client.get_full_name()} has completed payment of ₦{payment.amount:,.2f} for service request #{service_request.id}.\n\n'
                                   f'Category: {service_request.category.name}\n'
                                   f'Serviceman: {service_request.serviceman.get_full_name() if service_request.serviceman else "Not assigned"}\n\n'
                                   f'Please authorize the serviceman to begin work.',
                            notification_type='ADMIN_ALERT',
                            is_read=False
                        )
                    logger.info(f"Notified {admins.count()} admin(s) about payment for request #{service_request.id}")
                    
                    # Also notify client
                    Notification.objects.create(
                        user=service_request.client,
                        title='Payment Confirmed',
                        message=f'Your payment of ₦{payment.amount:,.2f} has been confirmed.\n\n'
                               f'The admin will authorize the serviceman to begin work shortly. You will be notified once work begins.',
                        notification_type='PAYMENT_CONFIRMED',
                        is_read=False
                    )
                except Exception as e:
                    logger.error(f"Error sending payment notifications: {str(e)}")
        else:
            payment.status = 'FAILED'
            payment.save()
        return Response({"status": payment.status})