from django.urls import path
from . import views

# app_name = 'core'

urlpatterns = [
    # Homepage
    path('signin/', views.login, name='signin'),
    path('signup/', views.signup, name='signup'),
    # About
    # path('about/', views.about, name='about'),
    
    # # Services
    # path('services/', views.services, name='services'),
    # # path('services/<slug:slug>/', views.service_details, name='service_details'),
    
    # # Projects
    # path('projects/', views.projects, name='projects'),
    # # path('projects/<slug:slug>/', views.project_details, name='project_details'),
    
    # # Contact
    # path('contact/', views.contact, name='contact'),
    
    # # FAQ
    # path('faq/', views.faq, name='faq'),
    
    # # AJAX/API endpoints (optional)
    # path('api/search-projects/', views.search_projects_ajax, name='search_projects_ajax'),
]