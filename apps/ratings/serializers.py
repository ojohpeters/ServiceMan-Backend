from rest_framework import serializers
from .models import Rating

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["id", "service_request", "rating", "review", "created_at"]
        read_only_fields = ["id", "created_at"]