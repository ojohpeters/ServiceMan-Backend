from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    # Migration-safe: use SerializerMethodField for is_emergency
    is_emergency = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'service_request', 'payment_type', 'amount', 'paystack_reference',
            'paystack_access_code', 'status', 'is_emergency', 'paid_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['paystack_access_code', 'status', 'paid_at', 'created_at', 'updated_at']
    
    def get_is_emergency(self, obj) -> bool:
        """
        Safely get is_emergency field (migration-safe).
        If field doesn't exist in DB, derive from amount.
        """
        # Try to get from database field
        is_emergency = getattr(obj, 'is_emergency', None)
        
        # If field doesn't exist, derive from amount
        if is_emergency is None:
            # Emergency booking is 5000, normal is 2000
            is_emergency = float(obj.amount) >= 5000
        
        return is_emergency