from django.contrib import admin
from .models import Notification

def mark_read(modeladmin, request, queryset):
    queryset.update(is_read=True)
mark_read.short_description = "Mark selected notifications as read"

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "notification_type", "title", "is_read",
        "sent_to_email", "email_sent_at", "created_at"
    )
    list_filter = ("notification_type", "is_read", "sent_to_email", "created_at")
    search_fields = ("user__username", "title", "message")
    readonly_fields = ("created_at", "email_sent_at")
    actions = [mark_read]