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
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=16, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paystack_reference = models.CharField(max_length=100, unique=True)
    paystack_access_code = models.CharField(max_length=100)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['paystack_reference']),
        ]

    def __str__(self):
        return f"{self.service_request.id} | {self.payment_type} | {self.status}"