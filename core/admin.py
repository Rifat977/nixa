# admin.py
from django.contrib import admin
from .models import *
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.models import Group

# admin.site.unregister(Group)
# admin.site.register(User)


class CustomAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'passport_number', 'is_verified', 'is_active', 'is_staff')
    list_filter = ('is_verified', 'is_active', 'is_staff', 'is_superuser')
    
    
    search_fields = ('email', 'first_name', 'last_name', 'passport_number')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(Account, CustomAdmin)


# class ProgramInline(admin.TabularInline):
#     model = Program
#     extra = 1

# class SubjectInline(admin.TabularInline):
#     model = Subject
#     extra = 1

class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'country', 'is_featured')
    list_editable = ('is_featured',)
    list_display_links = ('name', 'title')
    list_filter = ('is_featured', 'country')
    search_fields = ('name', 'title', 'description', 'country')

class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name',) # filter by university or program type
    # inlines = [SubjectInline]

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('program', 'name', 'course_period', 'intake', 'fee', 'course_type')
    search_fields = ('name', 'course_period')  # search by subject name, course period, or start date
    list_filter = ('program', 'course_type') 

admin.site.register(University, UniversityAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Application)


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'preferred_destination', 'consultation_type', 'preferred_date', 'status', 'created_at')
    list_filter = ('status', 'consultation_type', 'created_at')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('created_at',)
admin.site.register(GalleryImage)
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'content')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('question', 'answer')


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_display_links = ('name', 'slug')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'order', 'is_active')}),
        (_('Content'), {'fields': ('description', 'image')}),
    )


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ('title', 'university_name', 'deadline')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'event_type', 'event_date', 'is_upcoming', 'is_active')
    list_editable = ('is_upcoming', 'is_active')
    list_display_links = ('title', 'slug')
    list_filter = ('event_type', 'is_upcoming', 'is_active')
    search_fields = ('title', 'venue', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at',)
    date_hierarchy = 'event_date'
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'event_type', 'event_date', 'venue', 'is_upcoming', 'is_active')}),
        (_('Content'), {'fields': ('description', 'image')}),
        (_('Meta'), {'fields': ('created_at',)}),
    )


@admin.register(EventBooking)
class EventBookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'institution_name', 'event', 'status', 'created_at')
    list_filter = ('status', 'event', 'created_at')
    list_editable = ('status',)
    search_fields = ('name', 'email', 'phone', 'institution_name', 'inquery')
    readonly_fields = ('created_at',)
    list_display_links = ('name', 'email')


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)
    fields = ('title', 'image', 'link', 'is_active', 'order')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'phone', 'is_read', 'created_at')
    list_editable = ('is_read',)
    list_filter = ('is_read', 'subject', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'subject', 'phone', 'message', 'created_at')

    def has_add_permission(self, request):
        return False


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('email', 'subscribed_at')

    def has_add_permission(self, request):
        return False


admin.site.site_header = _('Nixaglobal Adminstrator')  # change the site header
admin.site.site_title = _('Nixaglobal Adminstrator')  # change the site title
admin.site.index_title = _('Nixaglobal Adminstrator') 

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'is_published', 'is_pinned')
    list_editable = ('is_published', 'is_pinned')
    search_fields = ('title', 'content')
    list_filter = ('is_published', 'is_pinned', 'published_at')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'logo_preview', 'hero_banner_preview')
    list_display_links = ('__str__',)

    fieldsets = (
        (_('Logo'), {
            'fields': ('logo',),
            'description': _('Site logo for header and footer. Leave blank to use default.'),
        }),
        (_('Hero section'), {
            'fields': ('hero_banner', 'hero_headline', 'hero_subtitle', 'hero_cta_label'),
            'description': _('Home page hero banner and text. Leave text fields blank to use defaults.'),
        }),
        (_('SEO & Meta'), {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'canonical_base_url', 'default_robots_meta'),
            'description': _('Default meta tags for search engines. Used across the site when pages do not set their own.'),
        }),
        (_('Social sharing (Open Graph)'), {
            'fields': ('site_name', 'og_title', 'og_description', 'og_image'),
            'description': _('How the site appears when shared on Facebook, LinkedIn, etc. Leave blank to use SEO fields or logo.'),
        }),
        (_('Analytics & Tracking'), {
            'fields': (
                'gtm_container_id',
                'ga4_measurement_id',
                'meta_pixel_id',
                'enable_meta_capi',
                'meta_capi_access_token',
                'meta_capi_test_event_code',
            ),
            'description': _(
                'Global analytics configuration. Public IDs (GTM / GA4 / Pixel) are used in templates; '
                'Meta Conversions API credentials are stored server-side for backend use.'
            ),
        }),
        (_('Global Schema Markup'), {
            'fields': ('global_schema_json', 'robots_txt_content', 'sitemap_url'),
            'description': _(
                'Optional JSON-LD schema for the entire site (e.g. Organization, WebSite). '
                'Paste valid JSON without surrounding <script> tags. '
                'robots.txt content can also be managed here; when left blank a simple default is served.'
            ),
        }),
        (_('Sticky CTA & Chat'), {
            'fields': (
                'enable_sticky_cta',
                'sticky_cta_label',
                'sticky_cta_url',
                'enable_whatsapp_chat',
                'whatsapp_number',
                'enable_messenger_chat',
                'messenger_page_id',
            ),
            'description': _(
                'Configure a global sticky Call-to-Action and optional WhatsApp / Messenger chat launchers.'
            ),
        }),
        (_('Social links'), {
            'fields': (
                'facebook_url',
                'instagram_url',
                'linkedin_url',
                'youtube_url',
            ),
            'description': _(
                'Public social media profiles shown in the footer.'
            ),
        }),
    )

    def logo_preview(self, obj):
        if obj and obj.logo:
            return mark_safe(f'<img src="{obj.logo.url}" style="max-height: 40px; width: auto;" alt="Logo" />')
        return '—'
    logo_preview.short_description = _('Logo')

    def hero_banner_preview(self, obj):
        if obj and obj.hero_banner:
            return mark_safe(f'<img src="{obj.hero_banner.url}" style="max-height: 40px; width: auto;" alt="Hero" />')
        return '—'
    hero_banner_preview.short_description = _('Hero image')

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Redirect to the single SiteSettings edit form if it exists."""
        from django.shortcuts import redirect
        from django.urls import reverse
        obj = SiteSettings.objects.first()
        if obj and not request.GET.get('add'):
            return redirect(reverse('admin:core_sitesettings_change', args=[obj.pk]))
        return super().changelist_view(request, extra_context)


@admin.register(PageSEO)
class PageSEOAdmin(admin.ModelAdmin):
    list_display = ('name', 'path', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name', 'path', 'meta_title', 'meta_description')
    list_filter = ('is_active',)