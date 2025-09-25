"""
Custom context processors
"""
from django.conf import settings


def site_settings(request):
    """Add site settings to template context"""
    return {
        'SITE_NAME': getattr(settings, 'META_SITE_NAME', 'IKr Multibusiness'),
        'SITE_PROTOCOL': getattr(settings, 'META_SITE_PROTOCOL', 'http'),
        'SITE_TYPE': getattr(settings, 'META_SITE_TYPE', 'website'),
        'SITE_DOMAIN': getattr(settings, 'META_SITE_DOMAIN', 'localhost:8000'),
        'DEBUG': settings.DEBUG,
    }