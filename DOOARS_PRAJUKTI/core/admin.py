from django.contrib import admin
from .models import (
    Service, Project, ProjectCategory,
    ContactMessage, TeamMember, Testimonial, FAQ,
    CompanySettings
)


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for Company Settings (Singleton)
    """
    fieldsets = (
        ('Basic Information', {
            'fields': ('company_name', 'tagline', 'description', 'founded_year')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address_line1', 'address_line2', 
                      'city', 'state', 'country', 'postal_code', 'business_hours')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 
                      'instagram_url', 'github_url', 'youtube_url')
        }),
        ('Homepage Settings', {
            'fields': ('hero_title', 'hero_subtitle', 'hero_cta_text', 'hero_cta_link')
        }),
        ('SEO Settings', {
            'fields': ('meta_description', 'meta_keywords')
        }),
        ('Footer Settings', {
            'fields': ('footer_text', 'copyright_text')
        }),
        ('Statistics', {
            'fields': ('manual_years_experience',),
            'description': 'Override automatic calculation of years of experience'
        }),
        ('Branding', {
            'fields': ('logo', 'favicon')
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent adding more than one instance"""
        if CompanySettings.objects.exists():
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of settings"""
        return False


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'featured', 'order', 'created_at')
    list_filter = ('is_active', 'featured', 'created_at')
    search_fields = ('title', 'short_description', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_active', 'featured', 'order')
    ordering = ('order', '-created_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'icon')
        }),
        ('Content', {
            'fields': ('short_description', 'description')
        }),
        ('Display Settings', {
            'fields': ('featured', 'order', 'is_active')
        }),
    )


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'project_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_filter = ('is_active',)
    
    def project_count(self, obj):
        """Show number of projects in this category"""
        return obj.projects.filter(is_active=True).count()
    project_count.short_description = 'Active Projects'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'client', 'featured', 'is_active', 'completion_date', 'order')
    list_filter = ('category', 'featured', 'is_active', 'completion_date')
    search_fields = ('title', 'description', 'client', 'technologies')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('featured', 'is_active', 'order')
    date_hierarchy = 'completion_date'
    ordering = ('order', '-created_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'client')
        }),
        ('Content', {
            'fields': ('short_description', 'description', 'technologies')
        }),
        ('Media & Links', {
            'fields': ('image', 'project_url', 'github_url')
        }),
        ('Project Details', {
            'fields': ('completion_date', 'duration_months')
        }),
        ('Display Settings', {
            'fields': ('featured', 'order', 'is_active')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize query with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('category')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'phone', 'subject', 'message', 
                      'ip_address', 'user_agent', 'created_at')
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_replied', 'mark_as_archived']
    
    def mark_as_read(self, request, queryset):
        queryset.update(status='read')
        self.message_user(request, f"{queryset.count()} message(s) marked as read.")
    mark_as_read.short_description = "Mark selected as Read"
    
    def mark_as_replied(self, request, queryset):
        queryset.update(status='replied')
        self.message_user(request, f"{queryset.count()} message(s) marked as replied.")
    mark_as_replied.short_description = "Mark selected as Replied"
    
    def mark_as_archived(self, request, queryset):
        queryset.update(status='archived')
        self.message_user(request, f"{queryset.count()} message(s) archived.")
    mark_as_archived.short_description = "Archive selected messages"


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'email', 'is_active', 'order')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'position', 'bio')
    list_editable = ('is_active', 'order')
    ordering = ('order', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'position', 'bio')
        }),
        ('Photo', {
            'fields': ('photo',)
        }),
        ('Contact & Social', {
            'fields': ('email', 'linkedin', 'twitter')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'company', 'rating', 'featured', 'is_active', 'order')
    list_filter = ('rating', 'featured', 'is_active', 'created_at')
    search_fields = ('client_name', 'company', 'content')
    list_editable = ('featured', 'is_active', 'order')
    ordering = ('order', '-created_at')
    
    fieldsets = (
        ('Client Information', {
            'fields': ('client_name', 'company', 'position', 'photo')
        }),
        ('Testimonial', {
            'fields': ('content', 'rating')
        }),
        ('Display Settings', {
            'fields': ('featured', 'order', 'is_active')
        }),
    )


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question_preview', 'category', 'is_active', 'order')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('question', 'answer')
    list_editable = ('is_active', 'order')
    ordering = ('category', 'order', '-created_at')
    
    fieldsets = (
        ('FAQ Content', {
            'fields': ('question', 'answer', 'category')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )
    
    def question_preview(self, obj):
        """Show first 60 characters of question"""
        return obj.question[:60] + '...' if len(obj.question) > 60 else obj.question
    question_preview.short_description = 'Question'


# Customize admin site header and title
admin.site.site_header = "Dooars Prajukti Admin"
admin.site.site_title = "Dooars Prajukti Admin Portal"
admin.site.index_title = "Welcome to Dooars Prajukti Admin Dashboard"