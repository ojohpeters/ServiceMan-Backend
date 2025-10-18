"""
Service Request Status History Tracking

This model tracks all status changes for service requests, providing a complete audit trail.
"""
from django.db import models
from apps.users.models import User
from .models import ServiceRequest


class ServiceRequestStatusHistory(models.Model):
    """
    Tracks the complete history of status changes for each service request.
    
    This provides an audit trail showing:
    - When status changed
    - Who changed it
    - What it changed from/to
    - Optional notes/reason for change
    """
    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    previous_status = models.CharField(
        max_length=32,
        choices=ServiceRequest.STATUS_CHOICES,
        null=True,
        blank=True,
        help_text="Previous status (null for initial creation)"
    )
    new_status = models.CharField(
        max_length=32,
        choices=ServiceRequest.STATUS_CHOICES,
        help_text="New status"
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='status_changes_made',
        help_text="User who made the change"
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the status was changed"
    )
    notes = models.TextField(
        blank=True,
        help_text="Optional notes explaining why the status was changed"
    )
    
    # Additional metadata
    is_automated = models.BooleanField(
        default=False,
        help_text="Whether this change was automated (e.g., payment confirmation)"
    )
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name = 'Service Request Status History'
        verbose_name_plural = 'Service Request Status Histories'
        indexes = [
            models.Index(fields=['service_request', '-changed_at']),
            models.Index(fields=['changed_by', '-changed_at']),
        ]
    
    def __str__(self):
        return f"{self.service_request.id}: {self.previous_status} → {self.new_status}"
    
    @property
    def time_in_previous_status(self):
        """Calculate how long the request was in the previous status"""
        if self.previous_status is None:
            return None
        
        # Get the previous history entry
        previous_entry = ServiceRequestStatusHistory.objects.filter(
            service_request=self.service_request,
            new_status=self.previous_status,
            changed_at__lt=self.changed_at
        ).first()
        
        if previous_entry:
            duration = self.changed_at - previous_entry.changed_at
            return duration
        return None


class ServiceRequestNote(models.Model):
    """
    Additional notes/comments on service requests (not status changes).
    
    Useful for:
    - Client comments/requests
    - Admin internal notes
    - Serviceman work notes
    """
    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='service_request_notes'
    )
    note_type = models.CharField(
        max_length=20,
        choices=[
            ('CLIENT', 'Client Note'),
            ('SERVICEMAN', 'Serviceman Note'),
            ('ADMIN', 'Admin Note'),
            ('SYSTEM', 'System Note'),
        ],
        default='SYSTEM'
    )
    content = models.TextField()
    is_visible_to_client = models.BooleanField(
        default=True,
        help_text="Whether this note is visible to the client"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['service_request', '-created_at']),
        ]
    
    def __str__(self):
        return f"Note on SR#{self.service_request.id} by {self.created_by}"

