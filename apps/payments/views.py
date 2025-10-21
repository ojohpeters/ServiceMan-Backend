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
            # Optionally: Send notifications, update ServiceRequest etc.
        else:
            payment.status = 'FAILED'
            payment.save()
        return Response({"status": payment.status})