from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'notification_type', 'title', 'message',
            'service_request', 'is_read', 'sent_to_email', 'email_sent_at', 'created_at'
        ]
        read_only_fields = ['sent_to_email', 'email_sent_at', 'created_at']