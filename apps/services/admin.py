from django.contrib import admin
from .models import Category, ServiceRequest

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")

def soft_delete(modeladmin, request, queryset):
    queryset.update(is_deleted=True)
soft_delete.short_description = "Soft delete selected requests"

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id", "client", "serviceman", "backup_serviceman", "category", "status", "booking_date",
        "is_emergency", "initial_booking_fee", "final_cost", "created_at"
    )
    list_filter = ("status", "category", "is_emergency", "booking_date", "created_at")
    search_fields = ("id", "client__username", "serviceman__username", "category__name")
    readonly_fields = ("created_at", "updated_at", "inspection_completed_at", "work_completed_at")
    actions = [soft_delete]
    fieldsets = (
        ("Core Info", {"fields": ("client", "serviceman", "backup_serviceman", "category", "status")}),
        ("Booking/Service", {"fields": ("booking_date", "is_emergency", "auto_flagged_emergency", "client_address", "service_description")}),
        ("Financials", {"fields": ("initial_booking_fee", "serviceman_estimated_cost", "admin_markup_percentage", "final_cost")}),
        ("Timestamps", {"fields": ("created_at", "updated_at", "inspection_completed_at", "work_completed_at")}),
        ("Soft Delete", {"fields": ("is_deleted", "deleted_at")}),
    )