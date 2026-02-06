"""
Authentication Forms for ERP System
Includes custom signup and signin forms with validation
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User


class SignUpForm(UserCreationForm):
    """
    Custom user registration form with role selection
    """
    
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Choose a username',
            'autocomplete': 'username',
        }),
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')
    )
    
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email',
        }),
        help_text=_('Required. Enter a valid email address.')
    )
    
    role = forms.ChoiceField(
        choices=User.Role.choices,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        help_text=_('Select your role in the organization.')
    )
    
    password1 = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Create a password',
            'autocomplete': 'new-password',
        }),
        help_text=_(
            'Your password must contain at least 8 characters and cannot be entirely numeric.'
        )
    )
    
    password2 = forms.CharField(
        label=_('Confirm Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password',
        }),
        help_text=_('Enter the same password as before, for verification.')
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')
    
    def clean_email(self):
        """
        Validate that the email is unique
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                _('A user with that email already exists.'),
                code='email_exists'
            )
        return email
    
    def clean_username(self):
        """
        Validate username
        """
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(
                _('A user with that username already exists.'),
                code='username_exists'
            )
        return username
    
    def save(self, commit=True):
        """
        Save the user with the selected role
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        
        if commit:
            user.save()
        return user


class SignInForm(AuthenticationForm):
    """
    Custom authentication form with enhanced styling
    """
    
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your username',
            'autocomplete': 'username',
            'autofocus': True,
        }),
    )
    
    password = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        }),
    )
    
    error_messages = {
        'invalid_login': _(
            'Please enter a correct username and password. Note that both fields may be case-sensitive.'
        ),
        'inactive': _('This account is inactive.'),
    }
    
    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in
        """
        if not user.is_active:
            raise ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )