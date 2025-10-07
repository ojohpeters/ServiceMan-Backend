from django.db import models
from apps.services.models import ServiceRequest
from apps.users.models import User

class PriceNegotiation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('COUNTERED', 'Countered'),
    ]
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='negotiations')
    proposed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    proposed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Negotiation #{self.id} for Request {self.service_request.id} - {self.status}"