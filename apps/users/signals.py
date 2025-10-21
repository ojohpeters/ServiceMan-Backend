from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import connection
from .models import User, ClientProfile, ServicemanProfile
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            if instance.user_type == 'CLIENT':
                # Use create() instead of get_or_create() since we know user is new
                ClientProfile.objects.create(user=instance)
            elif instance.user_type == 'SERVICEMAN':
                # Check which fields exist before creating
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='users_servicemanprofile'
                    """)
                    existing_columns = [row[0] for row in cursor.fetchall()]
                
                # Build creation kwargs with only existing fields
                profile_data = {'user': instance}
                
                # Add optional fields if they exist
                if 'is_approved' in existing_columns:
                    profile_data['is_approved'] = False  # New servicemen need approval
                
                ServicemanProfile.objects.create(**profile_data)
                logger.info(f"Created ServicemanProfile for user {instance.id}")
                
        except Exception as e:
            # Log the error but don't raise it to prevent user creation from failing
            logger.error(f"Failed to create profile for user {instance.id}: {e}")
            # Profile will be created later or manually