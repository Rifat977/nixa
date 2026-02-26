"""
Context processors for global template context.
"""


def destinations(request):
    """Inject active destinations for navbar and any global destination links."""
    try:
        from .models import Destination
        return {'nav_destinations': Destination.objects.filter(is_active=True).order_by('order', 'name')}
    except Exception:
        return {'nav_destinations': []}


# Fallback when migration not run or DB error (same shape as SiteSettings)
class _FallbackSettings:
    logo = None
    hero_banner = None
    hero_headline = ''
    hero_subtitle = ''
    hero_cta_label = ''
    meta_title = ''
    meta_description = ''
    meta_keywords = ''
    og_title = ''
    og_description = ''
    og_image = None
    site_name = ''


def site_settings(request):
    """Inject site_settings into every template (hero banner, hero text, etc.)."""
    try:
        from .models import SiteSettings
        return {'site_settings': SiteSettings.get_settings()}
    except Exception:
        return {'site_settings': _FallbackSettings()}
