"""
Custom Middleware for Authentication and Role-Based Access
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class RoleBasedRedirectMiddleware:
    """
    Middleware to redirect users to appropriate dashboards based on their role
    after login
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Process view before it's called
        You can add custom logic here if needed
        """
        pass


class EnsureAuthenticatedMiddleware:
    """
    Middleware to ensure users are authenticated for protected routes
    """
    
    # Define public URLs that don't require authentication
    PUBLIC_URLS = [
        '/signin/',
        '/signup/',
        '/admin/',
        '/static/',
        '/media/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if URL is public
        is_public = any(request.path.startswith(url) for url in self.PUBLIC_URLS)
        
        # If not public and user is not authenticated, redirect to signin
        if not is_public and not request.user.is_authenticated:
            messages.warning(request, 'Please login to continue.')
            return redirect('signin')
        
        response = self.get_response(request)
        return response


# Add to settings.py MIDDLEWARE:
"""
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Custom middleware (optional - uncomment if needed)
    # 'accounts.middleware.RoleBasedRedirectMiddleware',
    # 'accounts.middleware.EnsureAuthenticatedMiddleware',  # Use with caution
]
"""