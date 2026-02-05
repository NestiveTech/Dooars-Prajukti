from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.urls import reverse


class CompanySettings(models.Model):
    """
    Singleton model to store company-wide settings and information.
    Only one instance should exist in the database.
    """
    # Company Basic Info
    company_name = models.CharField(
        max_length=200,
        default="Dooars Prajukti",
        help_text="Company name"
    )
    tagline = models.CharField(
        max_length=300,
        blank=True,
        help_text="Company tagline or slogan"
    )
    description = models.TextField(
        blank=True,
        help_text="Company description for about page"
    )
    founded_year = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1900)],
        help_text="Year company was founded (for calculating years of experience)"
    )
    
    # Contact Information
    email = models.EmailField(
        blank=True,
        help_text="Primary company email"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Primary phone number"
    )
    address_line1 = models.CharField(
        max_length=255,
        blank=True,
        help_text="Street address"
    )
    address_line2 = models.CharField(
        max_length=255,
        blank=True,
        help_text="Additional address details"
    )
    city = models.CharField(
        max_length=100,
        blank=True
    )
    state = models.CharField(
        max_length=100,
        blank=True
    )
    country = models.CharField(
        max_length=100,
        blank=True
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True
    )
    
    # Business Hours
    business_hours = models.CharField(
        max_length=200,
        blank=True,
        default="Mon - Sat: 9:00 AM - 6:00 PM",
        help_text="Business hours text"
    )
    
    # Social Media Links
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    
    # SEO Settings
    meta_description = models.TextField(
        max_length=160,
        blank=True,
        help_text="Default meta description for SEO (max 160 characters)"
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated keywords for SEO"
    )
    
    # Homepage Settings
    hero_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Main hero section title on homepage"
    )
    hero_subtitle = models.TextField(
        max_length=500,
        blank=True,
        help_text="Hero section subtitle/description"
    )
    hero_cta_text = models.CharField(
        max_length=50,
        blank=True,
        default="Get Started",
        help_text="Call-to-action button text"
    )
    hero_cta_link = models.CharField(
        max_length=200,
        blank=True,
        default="/contact/",
        help_text="Call-to-action button link"
    )
    
    # Statistics (can be manually updated or auto-calculated)
    manual_years_experience = models.IntegerField(
        null=True,
        blank=True,
        help_text="Manually set years of experience (overrides auto-calculation)"
    )
    
    # Footer Settings
    footer_text = models.TextField(
        max_length=500,
        blank=True,
        default="Building innovative digital solutions for businesses worldwide.",
        help_text="Footer description text"
    )
    copyright_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Copyright text (leave blank to auto-generate)"
    )
    
    # Additional Settings
    logo = models.ImageField(
        upload_to='company/',
        blank=True,
        null=True,
        help_text="Company logo"
    )
    favicon = models.ImageField(
        upload_to='company/',
        blank=True,
        null=True,
        help_text="Website favicon"
    )
    
    # Maintenance Mode
    maintenance_mode = models.BooleanField(
        default=False,
        help_text="Enable to show maintenance page"
    )
    maintenance_message = models.TextField(
        blank=True,
        help_text="Message to display during maintenance"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Company Settings'
        verbose_name_plural = 'Company Settings'
    
    def __str__(self):
        return f"{self.company_name} Settings"
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (Singleton pattern)"""
        if not self.pk and CompanySettings.objects.exists():
            # If trying to create a new instance but one already exists,
            # update the existing one instead
            existing = CompanySettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
    
    def get_full_address(self):
        """Return formatted full address"""
        parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join([part for part in parts if part])
    
    def get_years_experience(self):
        """Calculate years of experience"""
        from datetime import datetime
        
        # Use manual value if set
        if self.manual_years_experience:
            return self.manual_years_experience
        
        # Calculate from founded year
        if self.founded_year:
            current_year = datetime.now().year
            return max(1, current_year - self.founded_year)
        
        # Calculate from oldest project
        from django.db.models import Min
        
        oldest_project = Project.objects.filter(
            is_active=True,
            completion_date__isnull=False
        ).aggregate(oldest=Min('completion_date'))
        
        if oldest_project['oldest']:
            years = (datetime.now().date() - oldest_project['oldest']).days // 365
            return max(1, years)
        
        return 0
    
    def get_copyright_text(self):
        """Return copyright text (auto-generated if not set)"""
        from datetime import datetime
        
        if self.copyright_text:
            return self.copyright_text
        
        current_year = datetime.now().year
        return f"© {current_year} {self.company_name}. All Rights Reserved."


class Service(models.Model):
    """
    Model to represent services offered by Dooars Prajukti.
    """
    title = models.CharField(
        max_length=200,
        help_text="Service title (e.g., Web Development)"
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        help_text="URL-friendly version of title (auto-generated)"
    )
    short_description = models.TextField(
        max_length=300,
        help_text="Brief description for cards/previews (max 300 characters)"
    )
    description = models.TextField(
        help_text="Detailed service description"
    )
    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="Bootstrap icon class (e.g., 'bi-globe')"
    )
    featured = models.BooleanField(
        default=False,
        help_text="Display on homepage"
    )
    order = models.IntegerField(
        default=0,
        help_text="Display order (lower numbers appear first)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Active services are displayed on the site"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Auto-generate slug from title if not provided"""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Return the URL for this service"""
        return reverse('service_details', kwargs={'slug': self.slug})


class ProjectCategory(models.Model):
    """
    Categories for organizing projects (e.g., Web Development, Mobile Apps)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Active categories are displayed on the site"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Project Category'
        verbose_name_plural = 'Project Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Project(models.Model):
    """
    Model to represent portfolio projects.
    """
    title = models.CharField(
        max_length=200,
        help_text="Project title"
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        help_text="URL-friendly version of title"
    )
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
        help_text="Project category"
    )
    client = models.CharField(
        max_length=200,
        blank=True,
        help_text="Client name"
    )
    short_description = models.TextField(
        max_length=300,
        help_text="Brief description for cards (max 300 characters)"
    )
    description = models.TextField(
        help_text="Detailed project description"
    )
    technologies = models.CharField(
        max_length=255,
        help_text="Comma-separated list of technologies used"
    )
    image = models.ImageField(
        upload_to='projects/%Y/%m/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text="Project featured image"
    )
    project_url = models.URLField(
        blank=True,
        help_text="Live project URL"
    )
    github_url = models.URLField(
        blank=True,
        help_text="GitHub repository URL"
    )
    completion_date = models.DateField(
        null=True,
        blank=True,
        help_text="Project completion date"
    )
    duration_months = models.IntegerField(
        default=0,
        help_text="Project duration in months"
    )
    featured = models.BooleanField(
        default=False,
        help_text="Display on homepage"
    )
    order = models.IntegerField(
        default=0,
        help_text="Display order"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Active projects are displayed on the site"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('project_details', kwargs={'slug': self.slug})

    def get_technologies_list(self):
        """Return technologies as a list"""
        return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]


class ContactMessage(models.Model):
    """
    Model to store contact form submissions.
    """
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(
        max_length=150,
        help_text="Contact person's name"
    )
    email = models.EmailField(
        help_text="Contact email address"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Phone number (optional)"
    )
    subject = models.CharField(
        max_length=200,
        blank=True,
        help_text="Message subject"
    )
    message = models.TextField(
        help_text="Message content"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        help_text="Message status"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Sender's IP address"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="Browser user agent"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} - {self.email} ({self.get_status_display()})"

    def mark_as_read(self):
        """Mark message as read"""
        if self.status == 'new':
            self.status = 'read'
            self.save(update_fields=['status', 'updated_at'])

    def mark_as_replied(self):
        """Mark message as replied"""
        self.status = 'replied'
        self.save(update_fields=['status', 'updated_at'])


class TeamMember(models.Model):
    """
    Model to represent team members (optional - for About page).
    """
    name = models.CharField(max_length=150)
    position = models.CharField(max_length=100, help_text="Job title/role")
    bio = models.TextField(blank=True, help_text="Short biography")
    photo = models.ImageField(
        upload_to='team/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])]
    )
    email = models.EmailField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'

    def __str__(self):
        return f"{self.name} - {self.position}"


class Testimonial(models.Model):
    """
    Model for client testimonials (optional - for homepage/about).
    """
    client_name = models.CharField(max_length=150)
    company = models.CharField(max_length=200, blank=True)
    position = models.CharField(max_length=100, blank=True)
    content = models.TextField(help_text="Testimonial text")
    rating = models.IntegerField(
        default=5,
        choices=[(i, i) for i in range(1, 6)],
        help_text="Rating out of 5"
    )
    photo = models.ImageField(
        upload_to='testimonials/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])]
    )
    featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'

    def __str__(self):
        return f"{self.client_name} - {self.company}"


class FAQ(models.Model):
    """
    Model for Frequently Asked Questions.
    """
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('services', 'Services'),
        ('pricing', 'Pricing'),
        ('technical', 'Technical'),
        ('support', 'Support'),
    ]

    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general'
    )
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'order', '-created_at']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return f"[{self.get_category_display()}] {self.question[:50]}"