from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, ClientProfile, ServicemanProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            if instance.user_type == 'CLIENT':
                ClientProfile.objects.get_or_create(user=instance)
            elif instance.user_type == 'SERVICEMAN':
                ServicemanProfile.objects.get_or_create(user=instance)
        except Exception as e:
            # Log the error but don't raise it to prevent user creation from failing
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create profile for user {instance.id}: {e}")