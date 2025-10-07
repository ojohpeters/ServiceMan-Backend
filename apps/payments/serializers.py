from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'service_request', 'payment_type', 'amount', 'paystack_reference',
            'paystack_access_code', 'status', 'paid_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['paystack_access_code', 'status', 'paid_at', 'created_at', 'updated_at']