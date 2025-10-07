from django.contrib import admin
from .models import PriceNegotiation

@admin.register(PriceNegotiation)
class PriceNegotiationAdmin(admin.ModelAdmin):
    list_display = ("id", "service_request", "proposed_by", "proposed_amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("service_request__id", "proposed_by__username", "message")
    readonly_fields = ("created_at",)