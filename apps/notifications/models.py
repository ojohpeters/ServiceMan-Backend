from django.db import models
from apps.users.models import User
from apps.services.models import ServiceRequest

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('SERVICE_ASSIGNED', 'Service Assigned'),
        ('PAYMENT_RECEIVED', 'Payment Received'),
        ('COST_ESTIMATE_READY', 'Cost Estimate Ready'),
        ('NEGOTIATION_UPDATE', 'Negotiation Update'),
        ('JOB_COMPLETED', 'Job Completed'),
        ('BACKUP_OPPORTUNITY', 'Backup Opportunity'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=32, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    service_request = models.ForeignKey(ServiceRequest, null=True, blank=True, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    sent_to_email = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.user} - {self.notification_type} - {self.title}"