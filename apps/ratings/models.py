from django.db import models
from apps.services.models import ServiceRequest
from apps.users.models import User

class Rating(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.rating} for SR {self.service_request.id}"