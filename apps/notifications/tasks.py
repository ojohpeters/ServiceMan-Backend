from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification

@shared_task
def send_notification_email(notification_id):
    notif = Notification.objects.get(id=notification_id)
    if notif.sent_to_email:
        return
    send_mail(
        notif.title,
        notif.message,
        settings.DEFAULT_FROM_EMAIL,
        [notif.user.email],
        fail_silently=False,
    )
    notif.sent_to_email = True
    notif.email_sent_at = notif.created_at
    notif.save()

@shared_task
def check_overdue_inspections():
    # Implement logic to notify admin if inspection overdue
    pass