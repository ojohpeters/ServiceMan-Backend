from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ClientProfile, ServicemanProfile, Skill

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type', 'is_email_verified']

class UserBasicSerializer(serializers.ModelSerializer):
    """Lightweight serializer for nested user data in serviceman profiles"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'first_name', 'last_name', 'user_type', 'is_email_verified']
        read_only_fields = fields
    
    def get_full_name(self, obj) -> str:
        """Get user's full name or fallback to username"""
        full_name = obj.get_full_name()
        return full_name if full_name else obj.username

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
    # ✅ CRITICAL FIX: Expand user object instead of just showing ID
    user = UserBasicSerializer(read_only=True)
    category = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    skill_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of skill IDs to assign to serviceman"
    )
    active_jobs_count = serializers.SerializerMethodField()
    availability_status = serializers.SerializerMethodField()
    is_approved = serializers.SerializerMethodField()
    approved_by = serializers.SerializerMethodField()
    approved_at = serializers.SerializerMethodField()
    rejection_reason = serializers.SerializerMethodField()
    
    class Meta:
        model = ServicemanProfile
        fields = [
            'id', 'user', 'category', 'skills', 'skill_ids', 'rating', 
            'total_jobs_completed', 'bio', 'years_of_experience', 
            'phone_number', 'is_available', 'active_jobs_count', 
            'availability_status', 'is_approved', 'approved_by', 'approved_at',
            'rejection_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'rating', 'total_jobs_completed', 'active_jobs_count', 
                          'availability_status', 'is_approved', 'approved_by', 'approved_at',
                          'rejection_reason', 'created_at', 'updated_at']
    
    def get_category(self, obj) -> dict:
        """Get category details"""
        if obj.category:
            return {
                "id": obj.category.id,
                "name": obj.category.name,
                "icon": obj.category.icon if hasattr(obj.category, 'icon') else None
            }
        return None
    
    def get_skills(self, obj) -> list:
        """
        Safely get skills, return empty list if field doesn't exist yet.
        This prevents 500 errors when migrations haven't been run in production.
        """
        try:
            if hasattr(obj, 'skills'):
                skills = obj.skills.filter(is_active=True)
                return SkillSerializer(skills, many=True).data
            return []
        except Exception:
            # If the skills table doesn't exist yet, return empty list
            return []
    
    def get_active_jobs_count(self, obj) -> int:
        """
        Get count of serviceman's active jobs (IN_PROGRESS status).
        """
        try:
            from apps.services.models import ServiceRequest
            from django.db.models import Q
            
            active_jobs = ServiceRequest.objects.filter(
                Q(serviceman=obj.user) | Q(backup_serviceman=obj.user),
                status='IN_PROGRESS',
                is_deleted=False
            ).count()
            return active_jobs
        except Exception:
            return 0
    
    def get_availability_status(self, obj) -> dict:
        """
        Get human-readable availability status with context.
        """
        if obj.is_available:
            return {
                "status": "available",
                "label": "Available",
                "message": "This serviceman is available for new jobs",
                "can_book": True
            }
        else:
            active_jobs = self.get_active_jobs_count(obj)
            return {
                "status": "busy",
                "label": "Currently Busy",
                "message": f"This serviceman is currently working on {active_jobs} job(s). You can still book them, but delivery may be delayed.",
                "can_book": True,  # Can still book, just with warning
                "active_jobs": active_jobs,
                "warning": "Booking a busy serviceman may result in delayed service. Consider choosing an available serviceman or proceed if you prefer this specific serviceman."
            }
    
    def get_is_approved(self, obj) -> bool:
        """Safely get approval status, default to True if field doesn't exist"""
        try:
            return getattr(obj, 'is_approved', True)
        except Exception:
            return True
    
    def get_approved_by(self, obj):
        """Safely get approved_by field"""
        try:
            return getattr(obj, 'approved_by_id', None)
        except Exception:
            return None
    
    def get_approved_at(self, obj):
        """Safely get approved_at field"""
        try:
            approved_at = getattr(obj, 'approved_at', None)
            return approved_at.isoformat() if approved_at else None
        except Exception:
            return None
    
    def get_rejection_reason(self, obj) -> str:
        """Safely get rejection_reason field"""
        try:
            return getattr(obj, 'rejection_reason', '')
        except Exception:
            return ''
    
    def update(self, instance, validated_data):
        # Handle skills update separately
        skill_ids = validated_data.pop('skill_ids', None)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update skills if provided and skills field exists
        if skill_ids is not None:
            try:
                if hasattr(instance, 'skills'):
                    skills = Skill.objects.filter(id__in=skill_ids, is_active=True)
                    instance.skills.set(skills)
            except Exception:
                # Silently skip if skills table doesn't exist yet
                pass
        
        return instance


class AdminServicemanProfileSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for admin endpoints with full user details.
    Eliminates N+1 queries by including nested user data.
    """
    user = UserBasicSerializer(read_only=True)
    category = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    skill_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of skill IDs to assign to serviceman"
    )
    active_jobs_count = serializers.SerializerMethodField()
    availability_status = serializers.SerializerMethodField()
    is_approved = serializers.SerializerMethodField()
    approved_by = serializers.SerializerMethodField()
    approved_at = serializers.SerializerMethodField()
    rejection_reason = serializers.SerializerMethodField()
    
    class Meta:
        model = ServicemanProfile
        fields = [
            'id', 'user', 'category', 'skills', 'skill_ids', 'rating', 
            'total_jobs_completed', 'bio', 'years_of_experience', 
            'phone_number', 'is_available', 'active_jobs_count', 
            'availability_status', 'is_approved', 'approved_by', 'approved_at',
            'rejection_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'rating', 'total_jobs_completed', 'active_jobs_count', 
                          'availability_status', 'is_approved', 'approved_by', 'approved_at',
                          'rejection_reason', 'created_at', 'updated_at']
    
    def get_category(self, obj) -> dict:
        """Get category details"""
        if obj.category:
            return {
                "id": obj.category.id,
                "name": obj.category.name,
                "icon": obj.category.icon if hasattr(obj.category, 'icon') else None
            }
        return None
    
    def get_skills(self, obj) -> list:
        """
        Safely get skills, return empty list if field doesn't exist yet.
        This prevents 500 errors when migrations haven't been run in production.
        """
        try:
            if hasattr(obj, 'skills'):
                skills = obj.skills.filter(is_active=True)
                return SkillSerializer(skills, many=True).data
            return []
        except Exception:
            # If the skills table doesn't exist yet, return empty list
            return []
    
    def get_active_jobs_count(self, obj) -> int:
        """
        Get count of serviceman's active jobs (IN_PROGRESS status).
        """
        try:
            from apps.services.models import ServiceRequest
            from django.db.models import Q
            
            active_jobs = ServiceRequest.objects.filter(
                Q(serviceman=obj.user) | Q(backup_serviceman=obj.user),
                status='IN_PROGRESS',
                is_deleted=False
            ).count()
            return active_jobs
        except Exception:
            return 0
    
    def get_availability_status(self, obj) -> dict:
        """
        Get human-readable availability status with context.
        """
        if obj.is_available:
            return {
                "status": "available",
                "label": "Available",
                "message": "This serviceman is available for new jobs",
                "can_book": True
            }
        else:
            active_jobs = self.get_active_jobs_count(obj)
            return {
                "status": "busy",
                "label": "Currently Busy",
                "message": f"This serviceman is currently working on {active_jobs} job(s). You can still book them, but delivery may be delayed.",
                "can_book": True,  # Can still book, just with warning
                "active_jobs": active_jobs,
                "warning": "Booking a busy serviceman may result in delayed service. Consider choosing an available serviceman or proceed if you prefer this specific serviceman."
            }
    
    def get_is_approved(self, obj) -> bool:
        """Safely get approval status, default to True if field doesn't exist"""
        try:
            return getattr(obj, 'is_approved', True)
        except Exception:
            return True
    
    def get_approved_by(self, obj):
        """Safely get approved_by field with user details"""
        try:
            approved_by_user = getattr(obj, 'approved_by', None)
            if approved_by_user:
                return {
                    "id": approved_by_user.id,
                    "username": approved_by_user.username,
                    "email": approved_by_user.email
                }
            return None
        except Exception:
            return None
    
    def get_approved_at(self, obj):
        """Safely get approved_at field"""
        try:
            approved_at = getattr(obj, 'approved_at', None)
            return approved_at.isoformat() if approved_at else None
        except Exception:
            return None
    
    def get_rejection_reason(self, obj) -> str:
        """Safely get rejection_reason field"""
        try:
            return getattr(obj, 'rejection_reason', '')
        except Exception:
            return ''


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