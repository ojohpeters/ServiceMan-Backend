from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ClientProfile, ServicemanProfile, Skill

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type', 'is_email_verified']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES)
    skill_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of skill IDs for servicemen"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_type', 'skill_ids']

    def validate_user_type(self, value):
        """Prevent ADMIN creation through public registration"""
        if value == User.ADMIN:
            raise serializers.ValidationError(
                "Cannot create admin users through public registration. "
                "Please contact an administrator."
            )
        return value

    def create(self, validated_data):
        skill_ids = validated_data.pop('skill_ids', [])
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        # If user is a serviceman and skills were provided, add them
        if user.user_type == User.SERVICEMAN and skill_ids:
            skills = Skill.objects.filter(id__in=skill_ids, is_active=True)
            user.serviceman_profile.skills.set(skills)
        
        return user

class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = ['user', 'phone_number', 'address', 'created_at', 'updated_at']

class SkillSerializer(serializers.ModelSerializer):
    """Serializer for Skill model"""
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class SkillCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating skills (admin only)"""
    class Meta:
        model = Skill
        fields = ['name', 'category', 'description']
    
    def validate_name(self, value):
        """Ensure skill name is unique (case-insensitive)"""
        if Skill.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A skill with this name already exists.")
        return value


class ServicemanProfileSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    skill_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of skill IDs to assign to serviceman"
    )
    
    class Meta:
        model = ServicemanProfile
        fields = [
            'user', 'category', 'skills', 'skill_ids', 'rating', 
            'total_jobs_completed', 'bio', 'years_of_experience', 
            'phone_number', 'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'rating', 'total_jobs_completed', 'created_at', 'updated_at']
    
    def update(self, instance, validated_data):
        # Handle skills update separately
        skill_ids = validated_data.pop('skill_ids', None)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update skills if provided
        if skill_ids is not None:
            skills = Skill.objects.filter(id__in=skill_ids, is_active=True)
            instance.skills.set(skills)
        
        return instance


class AdminCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating admin users (admin-only endpoint)"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate_username(self, value):
        """Check if username already exists"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate(self, data):
        """Validate that passwords match"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                "password_confirm": "Passwords do not match."
            })
        return data
    
    def create(self, validated_data):
        # Remove password_confirm as it's not needed for user creation
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Create admin user with proper flags
        user = User(**validated_data)
        user.user_type = User.ADMIN
        user.is_staff = True
        user.is_email_verified = True  # Admins don't need email verification
        user.set_password(password)
        user.save()
        
        return user