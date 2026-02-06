"""
Admin Configuration for Accounts App
Customizes the Django admin interface for User management
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin with role management
    """
    
    # List display configuration
    list_display = (
        'username',
        'email',
        'role',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'date_joined',
    )
    
    list_filter = (
        'role',
        'is_staff',
        'is_active',
        'is_superuser',
        'date_joined',
    )
    
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    
    ordering = ('-date_joined',)
    
    # Fieldsets for detail view
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email')
        }),
        (_('Role & Permissions'), {
            'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Fieldsets for add user view
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'role',
                'password1',
                'password2',
            ),
        }),
        (_('Optional Information'), {
            'classes': ('collapse',),
            'fields': ('first_name', 'last_name'),
        }),
        (_('Permissions'), {
            'classes': ('collapse',),
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'created_at', 'updated_at')
    
    # Enable actions
    actions = ['activate_users', 'deactivate_users', 'make_managers', 'make_team_members']
    
    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} user(s) have been activated.'
        )
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} user(s) have been deactivated.'
        )
    deactivate_users.short_description = 'Deactivate selected users'
    
    def make_managers(self, request, queryset):
        """Change role to Manager"""
        updated = queryset.update(role=User.Role.MANAGER)
        self.message_user(
            request,
            f'{updated} user(s) have been changed to Manager role.'
        )
    make_managers.short_description = 'Change role to Manager'
    
    def make_team_members(self, request, queryset):
        """Change role to Team Member"""
        updated = queryset.update(role=User.Role.TEAM_MEMBER)
        self.message_user(
            request,
            f'{updated} user(s) have been changed to Team Member role.'
        )
    make_team_members.short_description = 'Change role to Team Member'