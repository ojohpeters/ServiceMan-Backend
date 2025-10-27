from django.db import models
from apps.users.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        # Initial State
        ('PENDING_ADMIN_ASSIGNMENT', 'Pending Admin Assignment'),  # Initial state after client booking & booking fee payment. Waiting for admin to assign a serviceman.
        
        # Estimation Phase
        ('PENDING_ESTIMATION', 'Pending Estimation'),  # Admin has assigned serviceman. Serviceman needs to visit site and provide raw estimate.
        ('ESTIMATION_SUBMITTED', 'Estimation Submitted'),  # Serviceman has submitted raw estimate. Waiting for admin to add platform fee.
        
        # Client Approval & Payment Phase
        ('AWAITING_CLIENT_APPROVAL', 'Awaiting Client Approval'),  # Admin has added platform fee and sent final price to client. Waiting for client to approve and pay.
        ('PAYMENT_COMPLETED', 'Payment Completed'),  # Client has successfully paid the full amount. Job is now officially active.
        
        # Execution Phase
        ('IN_PROGRESS', 'In Progress'),  # Serviceman has started the work. Job appears on both client and serviceman dashboards.
        ('COMPLETED', 'Completed'),  # Serviceman has marked the job as finished.
        
        # Final State
        ('CLIENT_REVIEWED', 'Client Reviewed'),  # Client has left a rating and review for the serviceman.
        
        # Cancellation State
        ('CANCELLED', 'Cancelled'),  # Job was cancelled by admin, client, or serviceman before completion.
        
        # Legacy statuses (deprecated but kept for backward compatibility)
        ('ASSIGNED_TO_SERVICEMAN', 'Assigned to Serviceman'),
        ('SERVICEMAN_INSPECTED', 'Serviceman Inspected'),
        ('NEGOTIATING', 'Negotiating'),
        ('AWAITING_PAYMENT', 'Awaiting Payment'),
        ('PAYMENT_CONFIRMED', 'Payment Confirmed'),
    ]
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_requests')
    serviceman = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='serviceman_requests')
    backup_serviceman = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='backup_requests')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    booking_date = models.DateField()
    is_emergency = models.BooleanField(default=False)
    auto_flagged_emergency = models.BooleanField(default=False)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    initial_booking_fee = models.DecimalField(max_digits=10, decimal_places=2)
    serviceman_estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    admin_markup_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    final_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    client_address = models.TextField()
    service_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    inspection_completed_at = models.DateTimeField(null=True, blank=True)
    work_completed_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['client']),
            models.Index(fields=['serviceman']),
            models.Index(fields=['booking_date']),
        ]
    def __str__(self):
        return f"{self.client} - {self.category} - {self.status}"