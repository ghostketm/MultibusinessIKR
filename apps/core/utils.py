"""
Core utilities for the IKr Business Platform
"""
import uuid
from django.utils.text import slugify
from django.core.files.storage import default_storage


def generate_unique_slug(model_class, title, slug_field='slug'):
    """Generate a unique slug for a model instance"""
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    
    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug


def generate_sku():
    """Generate a unique SKU for products"""
    return f"IKR-{uuid.uuid4().hex[:8].upper()}"


def upload_to_path(instance, filename):
    """Generate upload path for files"""
    model_name = instance.__class__.__name__.lower()
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return f"{model_name}s/{filename}"