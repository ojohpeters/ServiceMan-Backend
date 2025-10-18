from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from .models import Notification
from .serializers import NotificationSerializer
from .tasks import send_notification_email

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

class NotificationUnreadCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})

class NotificationMarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def patch(self, request, pk):
        notif = Notification.objects.get(pk=pk, user=request.user)
        notif.is_read = True
        notif.save()
        return Response({'detail': 'Notification marked as read.'}, status=200)

class NotificationMarkAllReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def patch(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'detail': 'All notifications marked as read.'})


class SendNotificationView(APIView):
    """
    Send a notification to a user (Admin only).
    
    Creates both dashboard and email notifications.
    
    Body:
    {
        "user_id": int,
        "title": string,
        "message": string,
        "notification_type": string (optional, defaults to "SERVICE_ASSIGNED"),
        "service_request_id": int (optional)
    }
    
    Use cases:
    - Admin assigns serviceman to request
    - Admin sends custom notifications
    - System sends automated notifications
    
    Tags: Notifications
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        from apps.users.models import User
        from apps.users.permissions import IsAdmin
        
        # Only admins can send notifications manually
        if request.user.user_type != 'ADMIN':
            return Response({
                "detail": "Only administrators can send notifications."
            }, status=403)
        
        # Get data from request
        user_id = request.data.get('user_id')
        title = request.data.get('title')
        message = request.data.get('message')
        notification_type = request.data.get('notification_type', 'SERVICE_ASSIGNED')
        service_request_id = request.data.get('service_request_id', None)
        
        # Validate required fields
        if not all([user_id, title, message]):
            return Response({
                "detail": "Missing required fields: user_id, title, message"
            }, status=400)
        
        # Get user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                "detail": f"User with ID {user_id} not found."
            }, status=404)
        
        # Get service request if provided
        service_request = None
        if service_request_id:
            try:
                from apps.services.models import ServiceRequest
                service_request = ServiceRequest.objects.get(id=service_request_id)
            except ServiceRequest.DoesNotExist:
                return Response({
                    "detail": f"Service request with ID {service_request_id} not found."
                }, status=404)
        
        # Create notification
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            service_request=service_request,
            is_read=False
        )
        
        # Send email notification asynchronously
        try:
            send_notification_email.delay(notification.id)
            email_queued = True
        except Exception as e:
            # If Celery not available, send synchronously
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                
                send_mail(
                    subject=title,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True
                )
                email_queued = True
            except Exception:
                email_queued = False
        
        # Serialize and return
        serializer = NotificationSerializer(notification)
        
        return Response({
            "detail": "Notification sent successfully",
            "notification": serializer.data,
            "email_queued": email_queued,
            "recipient": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "user_type": user.user_type
            }
        }, status=201)