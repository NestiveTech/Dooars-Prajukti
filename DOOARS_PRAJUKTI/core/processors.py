"""
Context Processor for Company Settings
Add this file as: core/context_processors.py

This makes company settings and statistics available in ALL templates
without having to pass them in every view.

SETUP:
Add to settings.py in TEMPLATES['OPTIONS']['context_processors']:
    'core.context_processors.company_settings',
    'core.context_processors.site_statistics',
"""

from django.db.models import Count
from .models import CompanySettings, Project, Service


def company_settings(request):
    """
    Make company settings available in all templates as 'company'
    
    Usage in templates:
        {{ company.company_name }}
        {{ company.email }}
        {{ company.get_full_address }}
    """
    try:
        settings = CompanySettings.get_settings()
    except:
        # If model doesn't exist yet or database not migrated
        settings = None
    
    return {
        'company': settings
    }


def site_statistics(request):
    """
    Make site statistics available in all templates
    
    Usage in templates:
        {{ site_stats.total_projects }}
        {{ site_stats.total_clients }}
        {{ site_stats.years_experience }}
    """
    try:
        # Calculate statistics
        total_projects = Project.objects.filter(is_active=True).count()
        
        total_clients = Project.objects.filter(
            is_active=True,
            client__isnull=False
        ).exclude(client='').values('client').distinct().count()
        
        total_services = Service.objects.filter(is_active=True).count()
        
        # Get years of experience from company settings
        try:
            company = CompanySettings.get_settings()
            years_experience = company.get_years_experience()
        except:
            years_experience = 0
        
        stats = {
            'total_projects': total_projects,
            'total_clients': total_clients,
            'total_services': total_services,
            'years_experience': years_experience,
        }
    except:
        # If database not ready
        stats = {
            'total_projects': 0,
            'total_clients': 0,
            'total_services': 0,
            'years_experience': 0,
        }
    
    return {
        'site_stats': stats
    }


def social_links(request):
    """
    Make social media links available in all templates
    
    Usage in templates:
        {% if social.facebook_url %}
            <a href="{{ social.facebook_url }}">Facebook</a>
        {% endif %}
    """
    try:
        settings = CompanySettings.get_settings()
        social = {
            'facebook_url': settings.facebook_url,
            'twitter_url': settings.twitter_url,
            'linkedin_url': settings.linkedin_url,
            'instagram_url': settings.instagram_url,
            'github_url': settings.github_url,
            'youtube_url': settings.youtube_url,
        }
    except:
        social = {}
    
    return {
        'social': social
    }