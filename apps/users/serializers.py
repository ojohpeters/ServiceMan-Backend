from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ClientProfile, ServicemanProfile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type', 'is_email_verified']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES)
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_type']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = ['user', 'phone_number', 'address', 'created_at', 'updated_at']

class ServicemanProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicemanProfile
        fields = [
            'user', 'category', 'rating', 'total_jobs_completed', 'bio',
            'years_of_experience', 'phone_number', 'is_available',
            'created_at', 'updated_at'
        ]