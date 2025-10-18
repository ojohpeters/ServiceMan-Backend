# 📊 Service Request Status Tracking System

## ✅ Current Status Tracking (What You Have)

Your system already tracks service request status through **10 different stages**:

### Status Flow
```
1. PENDING_ADMIN_ASSIGNMENT      (Client books service)
         ↓
2. ASSIGNED_TO_SERVICEMAN        (Admin assigns serviceman)
         ↓
3. SERVICEMAN_INSPECTED          (Serviceman inspects & estimates)
         ↓
4. AWAITING_CLIENT_APPROVAL      (Client reviews estimate)
         ↓
5. NEGOTIATING                   (Optional: Price negotiation)
         ↓
6. AWAITING_PAYMENT              (Client needs to pay)
         ↓
7. PAYMENT_CONFIRMED             (Payment received)
         ↓
8. IN_PROGRESS                   (Work in progress)
         ↓
9. COMPLETED                     (Job done)

         (OR)
10. CANCELLED                    (Job cancelled)
```

### Existing Tracking Fields
```python
# ServiceRequest model has:
status = CharField(max_length=32)  # Current status
created_at = DateTimeField()       # When created
updated_at = DateTimeField()       # Last updated
inspection_completed_at = DateTimeField()  # Inspection time
work_completed_at = DateTimeField()        # Completion time
```

## 🆕 Enhanced Status History Tracking

### What's Missing
❌ **No history** - Can't see when status changed  
❌ **No audit trail** - Don't know who changed it  
❌ **No change reason** - Don't know why it changed  
❌ **No time tracking** - Can't calculate time in each status  

### Solution: Status History Model

I've created a comprehensive tracking system in `status_history_models.py` with:

#### 1. ServiceRequestStatusHistory Model
Tracks every status change:
- Previous status
- New status
- Who changed it
- When it changed
- Why it changed (notes)
- Whether automated or manual

#### 2. ServiceRequestNote Model
Additional notes/comments:
- Client comments
- Serviceman work notes
- Admin internal notes
- System notifications

## 🚀 Implementation Steps

### Step 1: Add Models to Your App

**Option A: Integrate into existing models.py**
```bash
# Append to apps/services/models.py
cat apps/services/status_history_models.py >> apps/services/models.py
```

**Option B: Keep separate and import**
```python
# In apps/services/models.py, add at the bottom:
from .status_history_models import ServiceRequestStatusHistory, ServiceRequestNote
```

### Step 2: Create Signal to Auto-Track Changes

Create `apps/services/signals.py`:

```python
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import ServiceRequest, ServiceRequestStatusHistory


# Store the old status before save
@receiver(pre_save, sender=ServiceRequest)
def store_previous_status(sender, instance, **kwargs):
    if instance.pk:  # Only for existing instances
        try:
            old_instance = ServiceRequest.objects.get(pk=instance.pk)
            instance._previous_status = old_instance.status
        except ServiceRequest.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


# Create history entry after save
@receiver(post_save, sender=ServiceRequest)
def track_status_change(sender, instance, created, **kwargs):
    # Get the user who made the change (from request context if available)
    changed_by = getattr(instance, '_changed_by', None)
    
    if created:
        # New service request
        ServiceRequestStatusHistory.objects.create(
            service_request=instance,
            previous_status=None,
            new_status=instance.status,
            changed_by=changed_by,
            notes="Service request created",
            is_automated=False
        )
    else:
        # Check if status changed
        previous_status = getattr(instance, '_previous_status', None)
        if previous_status and previous_status != instance.status:
            ServiceRequestStatusHistory.objects.create(
                service_request=instance,
                previous_status=previous_status,
                new_status=instance.status,
                changed_by=changed_by,
                notes=getattr(instance, '_status_change_notes', ''),
                is_automated=getattr(instance, '_is_automated_change', False)
            )
```

### Step 3: Update apps/services/apps.py

```python
from django.apps import AppConfig

class ServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.services'
    
    def ready(self):
        import apps.services.signals  # Import signals
```

### Step 4: Create Serializers

Create `apps/services/status_serializers.py`:

```python
from rest_framework import serializers
from .models import ServiceRequestStatusHistory, ServiceRequestNote
from apps.users.serializers import UserSerializer


class StatusHistorySerializer(serializers.ModelSerializer):
    changed_by = UserSerializer(read_only=True)
    time_in_previous_status = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceRequestStatusHistory
        fields = [
            'id', 'previous_status', 'new_status', 'changed_by',
            'changed_at', 'notes', 'is_automated', 'time_in_previous_status'
        ]
    
    def get_time_in_previous_status(self, obj):
        duration = obj.time_in_previous_status
        if duration:
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return None


class ServiceRequestNoteSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ServiceRequestNote
        fields = [
            'id', 'note_type', 'content', 'is_visible_to_client',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class StatusUpdateSerializer(serializers.Serializer):
    """For updating service request status with tracking"""
    new_status = serializers.ChoiceField(
        choices=ServiceRequest.STATUS_CHOICES
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional notes explaining the status change"
    )
```

### Step 5: Create Views for Status History

Add to `apps/services/views.py`:

```python
from rest_framework.decorators import action
from .status_serializers import StatusHistorySerializer, StatusUpdateSerializer


class ServiceRequestDetailView(generics.RetrieveAPIView):
    # ... existing code ...
    
    @action(detail=True, methods=['get'])
    def status_history(self, request, pk=None):
        """Get status history for a service request"""
        service_request = self.get_object()
        history = service_request.status_history.all()
        serializer = StatusHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def update_status(self, request, pk=None):
        """Update service request status with tracking"""
        service_request = self.get_object()
        serializer = StatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Set tracking attributes
            service_request._changed_by = request.user
            service_request._status_change_notes = serializer.validated_data.get('notes', '')
            service_request.status = serializer.validated_data['new_status']
            service_request.save()
            
            return Response({
                "message": "Status updated successfully",
                "new_status": service_request.status
            })
        
        return Response(serializer.errors, status=400)
```

### Step 6: Add URL Routes

```python
# apps/services/urls.py
urlpatterns = [
    # ... existing routes ...
    path(
        "service-requests/<int:pk>/status-history/",
        views.ServiceRequestStatusHistoryView.as_view(),
        name="service-request-status-history"
    ),
    path(
        "service-requests/<int:pk>/update-status/",
        views.ServiceRequestStatusUpdateView.as_view(),
        name="service-request-update-status"
    ),
]
```

### Step 7: Run Migrations

```bash
python manage.py makemigrations services
python manage.py migrate
```

## 📡 API Endpoints

### Get Status History
```bash
GET /api/service-requests/{id}/status-history/
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "previous_status": "ASSIGNED_TO_SERVICEMAN",
    "new_status": "SERVICEMAN_INSPECTED",
    "changed_by": {
      "id": 5,
      "username": "john_serviceman",
      "email": "john@example.com"
    },
    "changed_at": "2025-10-17T14:30:00Z",
    "notes": "Inspection completed. Estimate: ₦50,000",
    "is_automated": false,
    "time_in_previous_status": "2h 30m"
  },
  {
    "id": 2,
    "previous_status": "PENDING_ADMIN_ASSIGNMENT",
    "new_status": "ASSIGNED_TO_SERVICEMAN",
    "changed_by": {
      "id": 1,
      "username": "admin",
      "email": "admin@servicemanplatform.com"
    },
    "changed_at": "2025-10-17T12:00:00Z",
    "notes": "Assigned to John - Primary electrician",
    "is_automated": false,
    "time_in_previous_status": "1h 15m"
  }
]
```

### Update Status (Admin Only)
```bash
POST /api/service-requests/{id}/update-status/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "new_status": "IN_PROGRESS",
  "notes": "Payment confirmed. Work started."
}
```

### Get Service Request with History
```bash
GET /api/service-requests/{id}/
Authorization: Bearer <token>
```

**Include status history in response by updating serializer:**
```python
class ServiceRequestSerializer(serializers.ModelSerializer):
    status_history = StatusHistorySerializer(many=True, read_only=True)
    # ... rest of fields
```

## 📊 Analytics Queries

### Average Time in Each Status
```python
from django.db.models import Avg, F
from datetime import timedelta

# Calculate average time spent in each status
status_times = ServiceRequestStatusHistory.objects.annotate(
    duration=F('changed_at') - F('service_request__created_at')
).values('new_status').annotate(
    avg_time=Avg('duration')
)
```

### Status Change Frequency by User
```python
changes_by_user = ServiceRequestStatusHistory.objects.values(
    'changed_by__username'
).annotate(
    total_changes=Count('id')
).order_by('-total_changes')
```

### Requests Stuck in Status
```python
from datetime import datetime, timedelta

# Find requests in same status for more than 24 hours
stuck_requests = ServiceRequest.objects.annotate(
    last_change=Max('status_history__changed_at')
).filter(
    last_change__lt=datetime.now() - timedelta(hours=24)
)
```

## 🎯 Benefits

### For Clients
✅ See complete journey of their service request  
✅ Know exactly who handled what  
✅ Understand delays and reasons  
✅ Better transparency  

### For Admin
✅ Complete audit trail  
✅ Identify bottlenecks  
✅ Track serviceman performance  
✅ Compliance and reporting  

### For Servicemen
✅ See their action history  
✅ Reference past notes  
✅ Better communication  

## 🔧 Quick Implementation

Want me to implement this right now? I can:

1. ✅ Add the models to your codebase
2. ✅ Create the signals
3. ✅ Add serializers and views
4. ✅ Update URLs
5. ✅ Create migrations
6. ✅ Add to admin interface
7. ✅ Create comprehensive docs

**Would you like me to implement this complete status tracking system?**

---

## 📞 Alternative: Simple Tracking

If you just want basic tracking without full history:

### Option 1: Use Updated_At Field
```python
# Already exists in your model
updated_at = models.DateTimeField(auto_now=True)
```

### Option 2: Add Status Changed At Field
```python
# Add to ServiceRequest model
status_changed_at = models.DateTimeField(auto_now=True)
```

### Option 3: Use Django Admin History
Django admin already tracks all changes if you use the admin interface.

---

**Current Status**: You have basic status tracking ✅  
**Enhanced Tracking**: Ready to implement 🚀  
**Time to Implement**: 15-20 minutes

