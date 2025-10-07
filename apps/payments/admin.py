from django.contrib import admin
from .models import Payment

def mark_successful(modeladmin, request, queryset):
    for payment in queryset:
        payment.status = "SUCCESSFUL"
        payment.save()
mark_successful.short_description = "Mark selected payments as successful"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id", "service_request", "payment_type", "amount", "paystack_reference",
        "status", "paid_at", "created_at"
    )
    list_filter = ("payment_type", "status", "created_at", "paid_at")
    search_fields = ("service_request__id", "paystack_reference")
    readonly_fields = ("created_at", "updated_at", "paid_at", "paystack_access_code")
    actions = [mark_successful]