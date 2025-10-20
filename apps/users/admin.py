from django.contrib import admin
from .models import User, ClientProfile, ServicemanProfile, Skill


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "user_type", "is_active", "is_superuser", "is_email_verified", "date_joined")
    list_filter = ("user_type", "is_active", "is_superuser", "is_email_verified", "date_joined")
    search_fields = ("username", "email")
    readonly_fields = ("last_login", "date_joined")
    fieldsets = (
        ('Basic Information', {
            'fields': ('username', 'email', 'first_name', 'last_name')
        }),
        ('User Type & Permissions', {
            'fields': ('user_type', 'is_active', 'is_staff', 'is_superuser', 'is_email_verified')
        }),
        ('Timestamps', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone_number", "address", "created_at", "updated_at")
    search_fields = ("user__username", "phone_number", "address")
    readonly_fields = ("created_at", "updated_at")
    list_filter = ("created_at",)


@admin.register(ServicemanProfile)
class ServicemanProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "category", "is_approved", "approved_status_badge", 
        "rating", "total_jobs_completed", "is_available", "years_of_experience", "skill_count"
    )
    list_filter = ("category", "is_approved", "is_available", "rating", "approved_at")
    search_fields = ("user__username", "user__email", "phone_number", "bio")
    readonly_fields = ("created_at", "updated_at", "rating", "total_jobs_completed", "approved_at", "approved_by")
    filter_horizontal = ("skills",)  # Makes it easier to manage many-to-many relationships
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Professional Details', {
            'fields': ('category', 'skills', 'bio', 'years_of_experience', 'phone_number')
        }),
        ('Availability & Performance', {
            'fields': ('is_available', 'rating', 'total_jobs_completed')
        }),
        ('Approval Status', {
            'fields': ('is_approved', 'approved_by', 'approved_at', 'rejection_reason'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_servicemen', 'reject_servicemen']
    
    def skill_count(self, obj):
        """Display the number of skills a serviceman has"""
        return obj.skills.count()
    skill_count.short_description = 'Skills Count'
    
    def approved_status_badge(self, obj):
        """Display approval status with colored badge"""
        if obj.is_approved:
            return "✅ Approved"
        elif obj.rejection_reason:
            return "❌ Rejected"
        else:
            return "⏳ Pending"
    approved_status_badge.short_description = 'Status'
    
    def approve_servicemen(self, request, queryset):
        """Bulk approve selected servicemen"""
        from django.utils import timezone
        updated = queryset.filter(is_approved=False).update(
            is_approved=True,
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f"{updated} serviceman application(s) approved successfully.")
    approve_servicemen.short_description = "Approve selected servicemen"
    
    def reject_servicemen(self, request, queryset):
        """Bulk reject selected servicemen"""
        rejected = queryset.filter(is_approved=False).update(
            rejection_reason="Rejected by admin via bulk action"
        )
        self.message_user(request, f"{rejected} serviceman application(s) rejected.")
    reject_servicemen.short_description = "Reject selected servicemen"


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "is_active", "serviceman_count", "created_at")
    list_filter = ("category", "is_active", "created_at")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at", "serviceman_count")
    
    fieldsets = (
        ('Skill Information', {
            'fields': ('name', 'category', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Statistics', {
            'fields': ('serviceman_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def serviceman_count(self, obj):
        """Display the number of servicemen with this skill"""
        return obj.servicemen.count()
    serviceman_count.short_description = 'Servicemen Count'
    
    actions = ['activate_skills', 'deactivate_skills']
    
    def activate_skills(self, request, queryset):
        """Bulk activate selected skills"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} skill(s) activated successfully.")
    activate_skills.short_description = "Activate selected skills"
    
    def deactivate_skills(self, request, queryset):
        """Bulk deactivate selected skills (soft delete)"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} skill(s) deactivated successfully.")
    deactivate_skills.short_description = "Deactivate selected skills"