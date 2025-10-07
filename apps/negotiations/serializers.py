from rest_framework import serializers
from .models import PriceNegotiation
from apps.users.serializers import UserSerializer

class PriceNegotiationSerializer(serializers.ModelSerializer):
    proposed_by = UserSerializer(read_only=True)
    class Meta:
        model = PriceNegotiation
        fields = [
            'id', 'service_request', 'proposed_by', 'proposed_amount',
            'message', 'status', 'created_at'
        ]
        read_only_fields = ['proposed_by', 'status', 'created_at']

class PriceNegotiationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceNegotiation
        fields = ['service_request', 'proposed_amount', 'message']