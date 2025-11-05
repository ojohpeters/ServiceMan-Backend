from rest_framework import serializers
from .models import Category, ServiceRequest
from apps.users.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon_url', 'is_active', 'created_at', 'updated_at']

class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon_url']

class ServiceRequestSerializer(serializers.ModelSerializer):
    client = UserSerializer(read_only=True)
    preferred_serviceman = UserSerializer(read_only=True)
    serviceman = UserSerializer(read_only=True)
    backup_serviceman = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)
    preferred_serviceman_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(user_type='SERVICEMAN'), 
        source='preferred_serviceman', 
        write_only=True, 
        required=False,
        allow_null=True,
        help_text="Optional: Client's preferred serviceman ID"
    )

    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'client', 'preferred_serviceman', 'preferred_serviceman_id', 
            'serviceman', 'backup_serviceman', 'category', 'category_id',
            'booking_date', 'is_emergency', 'auto_flagged_emergency', 'status',
            'initial_booking_fee', 'serviceman_estimated_cost', 'admin_markup_percentage',
            'final_cost', 'client_address', 'service_description',
            'created_at', 'updated_at', 'inspection_completed_at', 'work_completed_at'
        ]
        read_only_fields = ['client', 'serviceman', 'backup_serviceman', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['client'] = user
        # Emergency auto-flag
        booking_date = validated_data['booking_date']
        from datetime import date, timedelta
        auto_flagged_emergency = False
        is_emergency = validated_data.get("is_emergency", False)
        if booking_date <= date.today() + timedelta(days=2):
            auto_flagged_emergency = True
            is_emergency = True  # override
        validated_data['auto_flagged_emergency'] = auto_flagged_emergency
        validated_data['is_emergency'] = is_emergency
        validated_data['initial_booking_fee'] = 5000 if is_emergency else 2000
        validated_data['status'] = 'PENDING_ADMIN_ASSIGNMENT'  # Initial state after booking fee payment
        return super().create(validated_data)