from django.contrib import admin
from .models import Rating

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("id", "service_request", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("service_request__id", "review")
    readonly_fields = ("created_at",)