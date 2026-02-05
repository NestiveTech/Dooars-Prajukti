from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    Service, Project, ProjectCategory,
    ContactMessage, Testimonial, FAQ, TeamMember
)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


def home(request):
    """Homepage view with ALL data from database - NO hardcoded values"""
    
    # Get featured services (max 4)
    services = Service.objects.filter(is_active=True, featured=True).order_by('order')[:4]
    
    # Get featured projects (max 3)
    projects = Project.objects.filter(is_active=True, featured=True).select_related('category').order_by('order')[:3]
    
    # Get featured testimonials (max 3)
    testimonials = Testimonial.objects.filter(is_active=True, featured=True).order_by('order')[:3]
    
    # Calculate real statistics from database - NO FALLBACKS
    total_projects = Project.objects.filter(is_active=True).count()
    
    # Count unique clients (non-empty client field)
    total_clients = Project.objects.filter(
        is_active=True, 
        client__isnull=False
    ).exclude(client='').values('client').distinct().count()
    
    # Calculate years of experience from oldest project completion date
    # If you want to calculate from database, use this approach:
    from django.db.models import Min
    from datetime import datetime
    
    oldest_project = Project.objects.filter(
        is_active=True,
        completion_date__isnull=False
    ).aggregate(oldest=Min('completion_date'))
    
    if oldest_project['oldest']:
        years_experience = (datetime.now().date() - oldest_project['oldest']).days // 365
        # Ensure at least 1 year of experience if projects exist
        years_experience = max(1, years_experience)
    else:
        # If no projects with completion dates, calculate from team members
        # Or from when the company was founded (add this to a CompanySettings model)
        years_experience = 0
    
    context = {
        'services': services,
        'projects': projects,
        'testimonials': testimonials,
        'stats': {
            'total_projects': total_projects,
            'total_clients': total_clients,
            'years_experience': years_experience,
        }
    }
    return render(request, 'home.html', context)


def about(request):
    """About page view - pulls team members and company info from database"""
    
    # Get active team members
    team_members = TeamMember.objects.filter(is_active=True).order_by('order')
    
    # Get testimonials for about page
    testimonials = Testimonial.objects.filter(is_active=True).order_by('order')[:6]
    
    # Calculate company statistics
    total_projects = Project.objects.filter(is_active=True).count()
    total_clients = Project.objects.filter(
        is_active=True,
        client__isnull=False
    ).exclude(client='').values('client').distinct().count()
    
    # Get service count
    total_services = Service.objects.filter(is_active=True).count()
    
    context = {
        'team_members': team_members,
        'testimonials': testimonials,
        'stats': {
            'total_projects': total_projects,
            'total_clients': total_clients,
            'total_services': total_services,
            'team_size': team_members.count(),
        }
    }
    
    return render(request, 'about.html', context)


def services(request):
    """Services listing page with search - all data from database"""
    qs = Service.objects.filter(is_active=True)

    q = request.GET.get('q')
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(short_description__icontains=q) |
            Q(description__icontains=q)
        )

    # Get related projects count for each service (optional enhancement)
    # This requires proper categorization - you might need to add service field to Project model
    
    return render(request, 'services.html', {
        'services': qs,
        'search_query': q or '',
        'total_services': qs.count(),
    })


def service_details(request, slug):
    """Individual service detail page"""
    service = get_object_or_404(Service, slug=slug, is_active=True)
    
    # Get related services (exclude current one)
    related_services = Service.objects.filter(
        is_active=True
    ).exclude(id=service.id).order_by('order')[:3]
    
    # Optional: Get projects related to this service
    # This would require adding a service foreign key to Project model
    
    context = {
        'service': service,
        'related_services': related_services,
    }
    return render(request, 'service_details.html', context)


def projects(request):
    """Projects listing page with filtering, search and pagination"""
    qs = Project.objects.filter(is_active=True).select_related('category')

    # Filter by category
    category = request.GET.get('category')
    if category:
        qs = qs.filter(category__slug=category)

    # Search functionality
    q = request.GET.get('q')
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(short_description__icontains=q) |
            Q(technologies__icontains=q) |
            Q(client__icontains=q)
        )

    # Pagination
    paginator = Paginator(qs, 9)  # 9 projects per page
    page_obj = paginator.get_page(request.GET.get('page'))

    # Get all active categories with project counts
    categories = ProjectCategory.objects.filter(
        is_active=True
    ).annotate(
        project_count=Count('projects', filter=Q(projects__is_active=True))
    ).order_by('name')
    
    # Get featured testimonials if they exist
    testimonials = Testimonial.objects.filter(
        is_active=True, 
        featured=True
    ).order_by('order')[:3]

    context = {
        'projects': page_obj,
        'categories': categories,
        'testimonials': testimonials if testimonials.exists() else None,
        'current_category': category,
        'search_query': q or '',
        'total_projects': qs.count(),
    }
    
    return render(request, 'projects.html', context)


def project_details(request, slug):
    """Individual project detail page"""
    project = get_object_or_404(Project, slug=slug, is_active=True)
    
    # Get related projects from the same category
    related_projects = None
    if project.category:
        related_projects = Project.objects.filter(
            category=project.category,
            is_active=True
        ).exclude(id=project.id).order_by('order')[:3]
    
    # If no category or not enough related projects, get recent projects
    if not related_projects or related_projects.count() < 3:
        additional_projects = Project.objects.filter(
            is_active=True
        ).exclude(id=project.id)
        
        if related_projects:
            additional_projects = additional_projects.exclude(
                id__in=[p.id for p in related_projects]
            )
        
        additional_projects = additional_projects.order_by('-created_at')[:3]
        
        if related_projects:
            related_projects = list(related_projects) + list(additional_projects)
        else:
            related_projects = additional_projects
    
    context = {
        'project': project,
        'related_projects': related_projects[:3],  # Ensure max 3
        'technologies': project.get_technologies_list(),
    }
    
    return render(request, 'project_details.html', context)


@require_http_methods(["GET", "POST"])
def contact(request):
    """Contact form page"""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        # Validation
        if not name or not email or not message:
            messages.error(request, "All required fields are mandatory.")
            return redirect('contact')

        # Create contact message
        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=request.POST.get("phone", ""),
            subject=request.POST.get("subject", ""),
            message=message,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
        )

        # Send email notification to company
        if getattr(settings, 'COMPANY_EMAIL', None):
            try:
                send_mail(
                    subject=f"New Contact Form Submission - {name}",
                    message=f"Name: {name}\nEmail: {email}\nPhone: {request.POST.get('phone', 'N/A')}\n\nMessage:\n{message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.COMPANY_EMAIL],
                    fail_silently=True
                )
            except Exception as e:
                # Log the error but don't break the flow
                print(f"Email sending failed: {e}")

        messages.success(request, "Thank you for contacting us! We'll get back to you soon.")
        return redirect('contact')
    
    # Get contact page data from database
    # You could create a ContactPageSettings model to store contact info
    # For now, getting recent testimonials for contact page
    testimonials = Testimonial.objects.filter(
        is_active=True,
        featured=True
    ).order_by('order')[:3]

    context = {
        'testimonials': testimonials if testimonials.exists() else None,
    }

    return render(request, 'contact.html', context)


def faq(request):
    """FAQ page with category filtering - all from database"""
    qs = FAQ.objects.filter(is_active=True)

    # Filter by category
    category = request.GET.get('category')
    if category:
        qs = qs.filter(category=category)

    # Group FAQs by category
    grouped = {}
    for f in qs:
        grouped.setdefault(f.get_category_display(), []).append(f)

    # Get FAQ statistics
    total_faqs = qs.count()
    categories_with_count = {}
    for cat_key, cat_name in FAQ.CATEGORY_CHOICES:
        count = qs.filter(category=cat_key).count()
        if count > 0:
            categories_with_count[cat_name] = count

    context = {
        'faqs_by_category': grouped,
        'categories': FAQ.CATEGORY_CHOICES,
        'current_category': category,
        'total_faqs': total_faqs,
        'categories_with_count': categories_with_count,
    }
    
    return render(request, 'faq.html', context)


def search_projects_ajax(request):
    """AJAX endpoint for project search"""
    q = request.GET.get('q', '')
    category = request.GET.get('category')

    qs = Project.objects.filter(is_active=True).select_related('category')

    # Search filter
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(short_description__icontains=q) |
            Q(technologies__icontains=q)
        )

    # Category filter
    if category:
        qs = qs.filter(category__slug=category)

    # Prepare JSON response
    data = [{
        'title': p.title,
        'slug': p.slug,
        'category': p.category.name if p.category else 'Uncategorized',
        'image': p.image.url if p.image else '',
        'tech': p.get_technologies_list(),
        'short_description': p.short_description,
    } for p in qs[:12]]

    return JsonResponse({
        'projects': data,
        'total': qs.count()
    })


# Error handlers
def handler404(request, exception):
    """Custom 404 error page"""
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    """Custom 500 error page"""
    return render(request, 'errors/500.html', status=500)