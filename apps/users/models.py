from django.db import models
from django.contrib.auth.models import AbstractUser

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
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_jobs_completed = models.IntegerField(default=0)
    bio = models.TextField(blank=True)
    years_of_experience = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, default='')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)