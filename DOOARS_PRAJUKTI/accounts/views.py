"""
Authentication Views for ERP System
Handles user registration, login, and logout
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views import View
from django.urls import reverse

from .forms import SignUpForm, SignInForm
from .models import User


@csrf_protect
@never_cache
def signup_view(request):
    """
    Handle user registration
    """
    # Redirect if user is already authenticated
    if request.user.is_authenticated:
        return redirect('dashboard:home')  # Redirect to dashboard
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        
        if form.is_valid():
            # Create the user
            user = form.save()
            
            # Log the user in
            login(request, user)
            
            # Success message
            messages.success(
                request,
                f'Welcome {user.username}! Your account has been created successfully.'
            )
            
            # Redirect to dashboard
            return redirect('dashboard:home')
        else:
            # Form has errors - they will be displayed in the template
            messages.error(
                request,
                'Please correct the errors below.'
            )
    else:
        form = SignUpForm()
    
    context = {
        'form': form,
        'page_title': 'Sign Up',
    }
    
    return render(request, 'register.html', context)


@csrf_protect
@never_cache
def signin_view(request):
    """
    Handle user login
    """
    # Redirect if user is already authenticated
    if request.user.is_authenticated:
        return redirect('dashboard:home')  # Redirect to dashboard
    
    if request.method == 'POST':
        form = SignInForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Log the user in
                login(request, user)
                
                # Success message
                messages.success(
                    request,
                    f'Welcome back, {user.username}!'
                )
                
                # Redirect to next page or dashboard
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('dashboard:home')
            else:
                messages.error(
                    request,
                    'Invalid username or password.'
                )
        else:
            # Form has errors
            messages.error(
                request,
                'Invalid username or password.'
            )
    else:
        form = SignInForm()
    
    context = {
        'form': form,
        'page_title': 'Sign In',
    }
    
    return render(request, 'login.html', context)


@login_required
def logout_view(request):
    """
    Handle user logout
    """
    username = request.user.username
    logout(request)
    
    messages.success(
        request,
        f'Goodbye, {username}! You have been logged out successfully.'
    )
    
    return redirect('signin')


# Alternative class-based views (optional)

class SignUpView(View):
    """
    Class-based view for user registration
    """
    template_name = 'register.html'
    form_class = SignUpForm
    
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        
        form = self.form_class(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f'Welcome {user.username}! Your account has been created successfully.'
            )
            return redirect('dashboard:home')
        
        messages.error(request, 'Please correct the errors below.')
        return render(request, self.template_name, {'form': form})


class SignInView(View):
    """
    Class-based view for user login
    """
    template_name = 'login.html'
    form_class = SignInForm
    
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        
        form = self.form_class(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            next_url = request.GET.get('next') or request.POST.get('next')
            return redirect(next_url if next_url else 'dashboard:home')
        
        messages.error(request, 'Invalid username or password.')
        return render(request, self.template_name, {'form': form})