"""
Admin configuration for accounts
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Enhanced user admin"""
    list_display = ('username', 'email', 'membership_tier', 'is_verified', 
                   'is_staff', 'date_joined')
    list_filter = ('membership_tier', 'is_verified', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'company_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Business Information', {
            'fields': ('company_name', 'business_type', 'tax_number', 'phone'),
        }),
        ('Membership', {
            'fields': ('membership_tier', 'is_verified', 'avatar'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'newsletter_subscribed', 'created_at')
    list_filter = ('newsletter_subscribed', 'email_notifications')
    search_fields = ('user__username', 'user__email', 'location')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'bio', 'website', 'location', 'birth_date')
        }),
        ('Preferences', {
            'fields': ('newsletter_subscribed', 'email_notifications')
        }),
    )
    readonly_fields = ('user',)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False