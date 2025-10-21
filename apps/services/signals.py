"""
Service Request Signals - Auto-update serviceman availability

Automatically manages serviceman availability based on job status:
- Sets to BUSY when job is IN_PROGRESS
- Sets to AVAILABLE when job is COMPLETED or CANCELLED
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import Q
from .models import ServiceRequest


@receiver(pre_save, sender=ServiceRequest)
def store_previous_status(sender, instance, **kwargs):
    """Store the previous status before saving"""
    if instance.pk:
        try:
            old_instance = ServiceRequest.objects.get(pk=instance.pk)
            instance._previous_status = old_instance.status
            instance._previous_serviceman = old_instance.serviceman
        except ServiceRequest.DoesNotExist:
            instance._previous_status = None
            instance._previous_serviceman = None
    else:
        instance._previous_status = None
        instance._previous_serviceman = None


@receiver(post_save, sender=ServiceRequest)
def update_serviceman_availability(sender, instance, created, **kwargs):
    """
    Auto-update serviceman availability based on job status.
    
    Rules:
    - When status changes to IN_PROGRESS: Set serviceman to BUSY
    - When status changes to COMPLETED/CANCELLED: Check if serviceman has other active jobs
    - If no active jobs: Set serviceman to AVAILABLE
    - If has active jobs: Keep serviceman as BUSY
    """
    # Get previous status
    previous_status = getattr(instance, '_previous_status', None)
    previous_serviceman = getattr(instance, '_previous_serviceman', None)
    current_serviceman = instance.serviceman
    
    # Skip if no serviceman assigned
    if not current_serviceman:
        return
    
    # Status changed to IN_PROGRESS - Set serviceman to BUSY
    if instance.status == 'IN_PROGRESS' and previous_status != 'IN_PROGRESS':
        profile = current_serviceman.serviceman_profile
        if profile.is_available:
            profile.is_available = False
            profile.save(update_fields=['is_available'])
            print(f"✓ Serviceman {current_serviceman.username} set to BUSY (Job #{instance.id} in progress)")
    
    # Status changed to COMPLETED or CANCELLED - Check if can set to AVAILABLE
    elif instance.status in ['COMPLETED', 'CANCELLED']:
        if previous_status not in ['COMPLETED', 'CANCELLED']:
            _check_and_update_availability(current_serviceman)
    
    # Serviceman changed on request - Update both old and new serviceman
    if previous_serviceman and previous_serviceman != current_serviceman:
        _check_and_update_availability(previous_serviceman)
        _check_and_update_availability(current_serviceman)


def _check_and_update_availability(serviceman):
    """
    Check if serviceman has any active jobs and update availability accordingly.
    
    Args:
        serviceman: User instance with user_type='SERVICEMAN'
    """
    if not serviceman or serviceman.user_type != 'SERVICEMAN':
        return
    
    # Check for active jobs (IN_PROGRESS status)
    active_jobs = ServiceRequest.objects.filter(
        Q(serviceman=serviceman) | Q(backup_serviceman=serviceman),
        status='IN_PROGRESS',
        is_deleted=False
    ).count()
    
    profile = serviceman.serviceman_profile
    
    if active_jobs > 0:
        # Has active jobs - should be BUSY
        if profile.is_available:
            profile.is_available = False
            profile.save(update_fields=['is_available'])
            print(f"✓ Serviceman {serviceman.username} set to BUSY ({active_jobs} active job(s))")
    else:
        # No active jobs - can be AVAILABLE
        if not profile.is_available:
            profile.is_available = True
            profile.save(update_fields=['is_available'])
            print(f"✓ Serviceman {serviceman.username} set to AVAILABLE (no active jobs)")


# Optional: Signal for when serviceman manually changes their availability
@receiver(pre_save, sender='users.ServicemanProfile')
def log_manual_availability_change(sender, instance, **kwargs):
    """Log when serviceman manually changes their availability"""
    if instance.pk:
        try:
            from django.db import connection
            
            # Check which fields exist before fetching old instance
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users_servicemanprofile'
                """)
                existing_columns = [row[0] for row in cursor.fetchall()]
            
            # Defer non-existent fields when fetching old instance
            fields_to_defer = []
            for field in ['is_approved', 'approved_by_id', 'approved_at', 'rejection_reason']:
                if field not in existing_columns:
                    defer_name = field.replace('_id', '') if field.endswith('_id') else field
                    fields_to_defer.append(defer_name)
            
            queryset = sender.objects.filter(pk=instance.pk)
            if fields_to_defer:
                queryset = queryset.defer(*fields_to_defer)
            
            old_instance = queryset.first()
            if old_instance and old_instance.is_available != instance.is_available:
                # Check if this is a manual change (not from auto-update)
                active_jobs = ServiceRequest.objects.filter(
                    Q(serviceman=instance.user) | Q(backup_serviceman=instance.user),
                    status='IN_PROGRESS',
                    is_deleted=False
                ).count()
                
                if active_jobs > 0 and instance.is_available:
                    print(f"⚠️ Warning: Serviceman {instance.user.username} set to AVAILABLE "
                          f"but has {active_jobs} active job(s)")
                
                status = "AVAILABLE" if instance.is_available else "BUSY"
                print(f"ℹ️ Serviceman {instance.user.username} availability manually changed to {status}")
        except sender.DoesNotExist:
            pass

