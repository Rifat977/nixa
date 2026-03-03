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


def page_seo(request):
    """
    Inject a PageSEO object for the current request path, if configured.

    Matching is done on the exact request.path (e.g. "/", "/blog/", "/contact/").
    """
    try:
        from .models import PageSEO
        path = request.path
        seo = PageSEO.objects.filter(path=path, is_active=True).first()
        return {'page_seo': seo}
    except Exception:
        return {'page_seo': None}
