from django.db import models
from django.contrib.auth.models import AbstractUser


class Skill(models.Model):
    """
    Represents a skill that servicemen can have.
    Skills are categorized and can be assigned to multiple servicemen.
    """
    CATEGORY_CHOICES = [
        ('TECHNICAL', 'Technical'),
        ('MANUAL', 'Manual Labor'),
        ('CREATIVE', 'Creative'),
        ('PROFESSIONAL', 'Professional Services'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class User(AbstractUser):
    ADMIN = 'ADMIN'
    SERVICEMAN = 'SERVICEMAN'
    CLIENT = 'CLIENT'
    USER_TYPE_CHOICES = [
        (ADMIN, 'Admin'),
        (SERVICEMAN, 'Serviceman'),
        (CLIENT, 'Client'),
    ]
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES)
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    REQUIRED_FIELDS = ['email', 'user_type']

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    phone_number = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ServicemanProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='serviceman_profile')
    category = models.ForeignKey('services.Category', on_delete=models.SET_NULL, null=True, blank=True)
    skills = models.ManyToManyField(Skill, related_name='servicemen', blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_jobs_completed = models.IntegerField(default=0)
    bio = models.TextField(blank=True)
    years_of_experience = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, default='')
    is_available = models.BooleanField(default=True)
    
    # Approval fields
    is_approved = models.BooleanField(
        default=False,
        help_text="Admin approval status for serviceman application"
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_servicemen',
        help_text="Admin who approved this serviceman"
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the serviceman was approved"
    )
    rejection_reason = models.TextField(
        blank=True,
        help_text="Reason for rejection (if applicable)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['is_approved', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Serviceman Profile"