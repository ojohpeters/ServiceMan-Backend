from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from .tasks import send_notification_email
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Notification)
def trigger_email_notification(sender, instance, created, **kwargs):
    """
    Send email notification via Celery when notification is created.
    
    Fails gracefully if Celery/Redis is not available (development mode).
    """
    if created:
        try:
            send_notification_email.delay(instance.id)
        except Exception as e:
            # Celery/Redis not available - fail silently
            # This is expected in development without Redis running
            logger.debug(f"Could not queue notification email (Celery not available): {e}")
            pass