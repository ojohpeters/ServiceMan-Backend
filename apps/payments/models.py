from django.db import models
from apps.services.models import ServiceRequest

class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('INITIAL_BOOKING', 'Initial Booking'),
        ('FINAL_PAYMENT', 'Final Payment'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESSFUL', 'Successful'),
        ('FAILED', 'Failed'),
    ]
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, null=True, blank=True)
    payment_type = models.CharField(max_length=16, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paystack_reference = models.CharField(max_length=100, unique=True)
    paystack_access_code = models.CharField(max_length=100)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES)
    is_emergency = models.BooleanField(default=False, help_text="Whether this is for an emergency booking")
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['paystack_reference']),
        ]

    def __str__(self):
        request_id = self.service_request.id if self.service_request else "No Request"
        return f"{request_id} | {self.payment_type} | {self.status}"