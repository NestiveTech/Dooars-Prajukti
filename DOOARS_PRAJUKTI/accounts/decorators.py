"""
Custom Decorators for Role-Based Access Control
Use these decorators to protect views based on user roles
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import User


def role_required(*allowed_roles):
    """
    Decorator to restrict access to specific roles
    
    Usage:
        @role_required(User.Role.SUPER_ADMIN)
        def admin_only_view(request):
            ...
        
        @role_required(User.Role.SUPER_ADMIN, User.Role.MANAGER)
        def admin_or_manager_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(
                    request,
                    'You do not have permission to access this page.'
                )
                raise PermissionDenied
        return wrapper
    return decorator


def super_admin_required(view_func):
    """
    Decorator to restrict access to super admins only
    
    Usage:
        @super_admin_required
        def super_admin_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_super_admin:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(
                request,
                'Only super administrators can access this page.'
            )
            raise PermissionDenied
    return wrapper


def manager_required(view_func):
    """
    Decorator to restrict access to managers and super admins
    
    Usage:
        @manager_required
        def manager_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_super_admin or request.user.is_manager:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(
                request,
                'Only managers and administrators can access this page.'
            )
            raise PermissionDenied
    return wrapper


def anonymous_required(redirect_url='dashboard:home'):
    """
    Decorator to restrict access to anonymous users only
    Redirects authenticated users to specified URL
    
    Usage:
        @anonymous_required()
        def public_only_view(request):
            ...
        
        @anonymous_required(redirect_url='profile')
        def login_page(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_url)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Example usage in views.py:
"""
from .decorators import role_required, super_admin_required, manager_required
from .models import User

@super_admin_required
def admin_dashboard(request):
    # Only super admins can access
    return render(request, 'admin_dashboard.html')

@manager_required
def manager_dashboard(request):
    # Managers and super admins can access
    return render(request, 'manager_dashboard.html')

@role_required(User.Role.SUPER_ADMIN, User.Role.MANAGER)
def reports_view(request):
    # Super admins and managers can access
    return render(request, 'reports.html')

@login_required
def team_dashboard(request):
    # All authenticated users can access
    return render(request, 'team_dashboard.html')
"""