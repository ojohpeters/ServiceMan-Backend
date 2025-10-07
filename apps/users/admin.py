from django.contrib import admin
from .models import User, ClientProfile, ServicemanProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "user_type", "is_active", "is_superuser", "is_email_verified", "date_joined")
    list_filter = ("user_type", "is_active", "is_superuser", "is_email_verified", "date_joined")
    search_fields = ("username", "email")
    readonly_fields = ("last_login", "date_joined")

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone_number", "address", "created_at", "updated_at")
    search_fields = ("user__username", "phone_number", "address")
    readonly_fields = ("created_at", "updated_at")

@admin.register(ServicemanProfile)
class ServicemanProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "category", "rating", "total_jobs_completed", "is_available", "years_of_experience", "phone_number"
    )
    list_filter = ("category", "is_available")
    search_fields = ("user__username", "phone_number", "bio")
    readonly_fields = ("created_at", "updated_at")