"""
Custom User Model for ERP System
Extends Django's AbstractUser to include role-based access control
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model with role-based permissions
    """
    
    # Role choices for the ERP system
    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', _('Super Admin')
        MANAGER = 'manager', _('Manager')
        TEAM_MEMBER = 'team_member', _('Team Member')
    
    # Additional fields
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        }
    )
    
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=Role.choices,
        default=Role.TEAM_MEMBER,
        help_text=_('Designates the user role and permissions level.')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Make email required
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username
    
    @property
    def is_super_admin(self):
        """Check if user is a super admin"""
        return self.role == self.Role.SUPER_ADMIN
    
    @property
    def is_manager(self):
        """Check if user is a manager"""
        return self.role == self.Role.MANAGER
    
    @property
    def is_team_member(self):
        """Check if user is a team member"""
        return self.role == self.Role.TEAM_MEMBER
    
    def has_role(self, role):
        """Check if user has a specific role"""
        return self.role == role
    
    def get_role_display_name(self):
        """Get human-readable role name"""
        return self.get_role_display()