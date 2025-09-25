"""
Common mixins for views and models
"""
from django.db import models
from django.utils import timezone


class TimestampMixin(models.Model):
    """Add created_at and updated_at fields to any model"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class SEOMixin(models.Model):
    """Add SEO fields to any model"""
    meta_title = models.CharField(max_length=60, blank=True, 
                                 help_text="SEO title (60 chars max)")
    meta_description = models.TextField(max_length=160, blank=True,
                                      help_text="SEO description (160 chars max)")
    meta_keywords = models.CharField(max_length=255, blank=True,
                                   help_text="SEO keywords (comma separated)")
    
    class Meta:
        abstract = True