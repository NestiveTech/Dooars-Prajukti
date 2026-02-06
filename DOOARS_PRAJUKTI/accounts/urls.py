"""
URL Configuration for Accounts App
Defines authentication routes
"""

from django.urls import path
from . import views

# app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('signup/', views.signup_view, name='signup'),
    path('signin/', views.signin_view, name='signin'),
    path('logout/', views.logout_view, name='logout'),
    
    # Alternative: If you want to use class-based views, uncomment below
    # path('signup/', views.SignUpView.as_view(), name='signup'),
    # path('signin/', views.SignInView.as_view(), name='signin'),
]