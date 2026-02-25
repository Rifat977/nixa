from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField


class Account(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    passport_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    gender_choices = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=gender_choices, blank=True)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    password_reset_token = models.CharField(max_length=64, blank=True, null=True)

    # Add related_name to avoid conflicts
    groups = models.ManyToManyField(Group, related_name='account_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='account_permissions', blank=True)

    def is_email_verification_token_expired(self):
        if self.email_verification_sent_at:
            expiration_time = timedelta(hours=24)  # 24 hours validity
            return self.email_verification_sent_at + expiration_time < timezone.now()
        return True

    def generate_password_reset_token(self):
        token = get_random_string(length=32)
        self.password_reset_token = token
        self.save()
        return token

    class Meta:
        verbose_name = "User Accounts"
        verbose_name_plural = "          User Accounts"


class University(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='university_logos', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = RichTextField(null=True, blank=True)
    image = models.ImageField(upload_to='university_images', null=True, blank=True)
    country = models.CharField(
        max_length=100,
        blank=True,
        help_text='Country of the university (e.g. Malaysia, UK). Used to group universities on the university list page.'
    )
    is_featured = models.BooleanField(
        default=False,
        help_text='Show this university in the "Featured Universities" section on the home page.'
    )

    class Meta:
        verbose_name = "University"
        verbose_name_plural = "         University"

    def __str__(self):
        return self.name


class Program(models.Model):
    """
    Represents a Program offered by a University.
    """
    # UNIVERSITY_PROGRAM_TYPES = [
    #     ('BACHELOR', 'Bachelor'),
    #     ('MASTER', 'Master'),
    #     ('PHD', 'PhD'),
    #     ('Foundation', 'Foundation'),
    #     ('Pharmacy', 'Pharmacy'),
    # ]

    # university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='programs')
    # program_type = models.CharField(max_length=10, choices=UNIVERSITY_PROGRAM_TYPES)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Program"
        verbose_name_plural = "        Programs"

    def __str__(self):
        return f"{self.name}"


class Subject(models.Model):
    """
    Represents a Subject offered by a Program.
    """
    COURSE_TYPES = [
        ('Coursework', 'Coursework'),
    ]

    university = models.ForeignKey(University, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=255)
    course_period = models.CharField(max_length=255)
    intake = models.CharField(max_length=255)
    fee = models.CharField(max_length=255)
    course_type = models.CharField(max_length=10, choices=COURSE_TYPES)

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "       Subject"

    def __str__(self):
        return f"{self.program.name} - {self.name}"


class Application(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    name = models.CharField(max_length=255)
    reference_code = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=15)  # Example regex for phone number validation
    email = models.EmailField()
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    passport_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    highest_qualification = models.CharField(max_length=255)
    year_of_passing = models.CharField(max_length=10)
    english_language_certificate = models.BooleanField(default=False)  # Use a BooleanField to represent yes/no
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    certificate_upload = models.FileField(upload_to='certificates/')
    passport_information_page = models.FileField(upload_to='passports/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application by {self.name} for {self.program.name} at {self.university.name}"

    class Meta:
        verbose_name = 'Application'
        verbose_name_plural = '      Applications'



class GalleryImage(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True) 
    image_primary = models.ImageField(upload_to='gallery_images/')
    image_1 = models.ImageField(upload_to='gallery_images/', null=True, blank=True)
    image_2 = models.ImageField(upload_to='gallery_images/', null=True, blank=True)
    image_3 = models.ImageField(upload_to='gallery_images/', null=True, blank=True)
    image_4 = models.ImageField(upload_to='gallery_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title if self.title else f'Gallery Image {self.id}'

    class Meta:
        verbose_name = 'Gallery'
        verbose_name_plural = '     Galleries'


class Video(models.Model):
    """Student experience videos - manageable from admin"""
    title = models.CharField(max_length=255)
    video_url = models.URLField(max_length=500, help_text="YouTube URL: paste watch (youtube.com/watch?v=ID) or embed (youtube.com/embed/ID) link")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, help_text="Show on homepage when checked")
    created_at = models.DateTimeField(auto_now_add=True)

    def get_embed_url(self):
        """Return a clean YouTube embed URL for iframe (avoids Error 153)."""
        from urllib.parse import urlparse, parse_qs
        if not self.video_url:
            return ""
        url = (self.video_url or "").strip()
        video_id = None
        # Embed URL: .../embed/VIDEO_ID or .../embed/VIDEO_ID?...
        if "/embed/" in url:
            parsed = urlparse(url)
            path = (parsed.path or "").strip("/")
            if "embed" in path:
                parts = path.split("/")
                try:
                    idx = parts.index("embed")
                    if idx + 1 < len(parts):
                        video_id = parts[idx + 1].split("?")[0]
                except ValueError:
                    pass
        # Watch URL: youtube.com/watch?v=VIDEO_ID
        elif "youtube.com/watch" in url:
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            video_id = (qs.get("v") or [None])[0]
        # Short URL: youtu.be/VIDEO_ID
        elif "youtu.be" in url:
            parsed = urlparse(url)
            video_id = (parsed.path or "").strip("/").split("/")[0].split("?")[0]
        if video_id:
            # Use youtube-nocookie.com to avoid Error 153 on some pages (e.g. homepage)
            return f"https://www.youtube-nocookie.com/embed/{video_id}"
        return ""

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'


class Testimonial(models.Model):
    """Student/client reviews - manageable from admin"""
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to='testimonials/avatars/', blank=True, null=True)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, help_text="Show on homepage when checked")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.designation}"

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'


class FAQ(models.Model):
    """Frequently asked questions - manageable from admin"""
    question = models.CharField(max_length=500)
    answer = models.TextField(help_text="HTML allowed for formatting")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, help_text="Show on homepage when checked")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:80] + ("..." if len(self.question) > 80 else "")

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'



from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tags'
        verbose_name_plural = ' Tags'


class Blog(models.Model):
    title = models.CharField(max_length=200)  
    image = models.ImageField(upload_to='blog/')
    content = RichTextField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, related_name='blogs', blank=True)

    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/blog/{self.slug}/"

    class Meta:
        ordering = ['-is_pinned', '-published_at']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'


class Destination(models.Model):
    """Study destinations - Malaysia, Australia, UK, etc. Managed from Admin; shown in navbar and list/detail pages."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, help_text='URL-friendly name (e.g. study-in-malaysia). Auto-filled from name.')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='destinations/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0, help_text='Lower numbers appear first in navbar and list.')
    is_active = models.BooleanField(default=True, help_text='Inactive destinations are hidden from navbar and list.')

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Destination'
        verbose_name_plural = 'Destinations'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('core:destination-detail', kwargs={'slug': self.slug})


class Scholarship(models.Model):
    """University scholarship programs worldwide"""
    title = models.CharField(max_length=255)
    description = RichTextField(null=True, blank=True)
    university_name = models.CharField(max_length=255, blank=True)
    deadline = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='scholarships/', null=True, blank=True)
    link = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Scholarship'
        verbose_name_plural = 'Scholarships'

    def __str__(self):
        return self.title


class Event(models.Model):
    """Education expo, fair, assessment day, spot admission. Managed from Admin; list and detail pages."""
    EVENT_TYPE_CHOICES = [
        ('expo', 'Education Expo'),
        ('fair', 'Education Fair'),
        ('assessment', 'Assessment Day'),
        ('spot_admission', 'Spot Admission'),
        ('other', 'Other'),
    ]
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, help_text='URL-friendly (e.g. education-expo-2025). Auto-filled from title.')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='other')
    description = RichTextField(null=True, blank=True)
    venue = models.CharField(max_length=255, blank=True)
    event_date = models.DateTimeField()
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    is_upcoming = models.BooleanField(default=True, help_text='Show in upcoming events list when checked.')
    is_active = models.BooleanField(default=True, help_text='Inactive events are hidden from the site.')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['event_date']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or 'event'
            self.slug = base
            n = 1
            while Event.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f'{base}-{n}'
                n += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('core:event-detail', kwargs={'slug': self.slug})


class EventBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    seats = models.PositiveIntegerField(default=1)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Event Booking'
        verbose_name_plural = 'Event Bookings'

    def __str__(self):
        return f"{self.name} — {self.event.title} ({self.seats} seat{'s' if self.seats != 1 else ''})"


class Consultation(models.Model):
    """Free consultation booking requests"""
    CONSULTATION_TYPE_CHOICES = [
        ('online', 'Online (Video Call)'),
        ('in_person', 'In Person'),
        ('phone', 'Phone Call'),
    ]
    TIME_SLOT_CHOICES = [
        ('10:00-12:00', '10:00 AM - 12:00 PM'),
        ('12:00-14:00', '12:00 PM - 2:00 PM'),
        ('14:00-16:00', '2:00 PM - 4:00 PM'),
        ('16:00-18:00', '4:00 PM - 6:00 PM'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    preferred_destination = models.CharField(max_length=100, blank=True, null=True)  # Malaysia, Australia, UK, etc.
    consultation_type = models.CharField(max_length=20, choices=CONSULTATION_TYPE_CHOICES, default='online')
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time_slot = models.CharField(max_length=20, choices=TIME_SLOT_CHOICES, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Consultation'
        verbose_name_plural = 'Consultations'

    def __str__(self):
        return f"{self.name} - {self.preferred_destination or 'General'} ({self.created_at.date()})"


class Offer(models.Model):
    """Latest & Upcoming section - banner image with title and apply now link"""
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='offers/', null=True, blank=True, help_text='Banner image. Clicking it redirects to the Apply Now URL.')
    link = models.URLField(max_length=500, blank=True, help_text='Apply Now URL. Leave blank to use the default application page.')
    is_active = models.BooleanField(default=True, help_text="Show on homepage when checked")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('Student Visa', 'Student Visa'),
        ('Tourist Visa', 'Tourist Visa'),
        ('Commercial Visa', 'Commercial Visa'),
        ('Residence Visa', 'Residence Visa'),
        ('Working Visa', 'Working Visa'),
    ]
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=100, choices=SUBJECT_CHOICES, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} — {self.subject or 'General'} ({self.created_at.date()})"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'

    def __str__(self):
        return self.email


class SiteSettings(models.Model):
    """
    Singleton-style site settings. Use the first record (id=1) for hero and global options.
    """
    logo = models.ImageField(
        upload_to='settings/logo/',
        blank=True,
        null=True,
        help_text='Site logo used in header and footer. Leave blank to use default.'
    )
    hero_banner = models.ImageField(
        upload_to='settings/hero/',
        blank=True,
        null=True,
        help_text='Full-width hero background image. Recommended: 1920×1080 or larger.'
    )
    hero_headline = models.CharField(
        max_length=255,
        blank=True,
        help_text='Main headline on the hero. Leave blank to use default.'
    )
    hero_subtitle = models.TextField(
        blank=True,
        help_text='Supporting text under the headline. Leave blank to use default.'
    )
    hero_cta_label = models.CharField(
        max_length=100,
        blank=True,
        help_text='Button text, e.g. "Book Free Consultation". Leave blank to use default.'
    )
    # SEO
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        help_text='Default page title for search engines (e.g. "Nixa Global – Study Abroad Consultancy"). Used when a page does not set its own title.'
    )
    meta_description = models.TextField(
        blank=True,
        help_text='Default meta description for search results. Keep under 160 characters for best display.'
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text='Optional comma-separated keywords for SEO (e.g. "study abroad, visa, university admission").'
    )
    og_title = models.CharField(
        max_length=255,
        blank=True,
        help_text='Title for social sharing (Open Graph, Facebook, etc.). Leave blank to use meta title.'
    )
    og_description = models.TextField(
        blank=True,
        help_text='Description for social sharing. Leave blank to use meta description.'
    )
    og_image = models.ImageField(
        upload_to='settings/og/',
        blank=True,
        null=True,
        help_text='Image for social sharing (e.g. Facebook, LinkedIn). Recommended: 1200×630 px. Leave blank to use logo or hero.'
    )
    site_name = models.CharField(
        max_length=100,
        blank=True,
        help_text='Brand/site name for Open Graph (e.g. "Nixa Global").'
    )

    class Meta:
        verbose_name = 'Site settings'
        verbose_name_plural = 'Site settings'

    def __str__(self):
        return 'Site settings'

    @classmethod
    def get_settings(cls):
        """Return the single site settings instance (creates with defaults if missing)."""
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                'hero_headline': 'Your Study Abroad Dream Starts Here',
                'hero_subtitle': "Expert admission and visa guidance. From application to arrival—we support you every step of the way.",
                'hero_cta_label': 'Book Free Consultation',
            }
        )
        return obj
