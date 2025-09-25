"""
Product catalog models
"""
from django.db import models
from django.urls import reverse
from apps.core.mixins import TimestampMixin, SEOMixin
from apps.core.utils import generate_unique_slug, generate_sku, upload_to_path


class Category(TimestampMixin, SEOMixin):
    """Product categories"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, 
                              blank=True, null=True, related_name='children')
    image = models.ImageField(upload_to='categories/', blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Category, self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:category', kwargs={'slug': self.slug})


class Product(TimestampMixin, SEOMixin):
    """Product model with comprehensive business features"""

    class ProductType(models.TextChoices):
        PHYSICAL = 'physical', 'Physical Product'
        DIGITAL = 'digital', 'Digital Product'
        SERVICE = 'service', 'Service'
        SUBSCRIPTION = 'subscription', 'Subscription'
        CONSULTATION = 'consultation', 'Consultation'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        OUT_OF_STOCK = 'out_of_stock', 'Out of Stock'

    class PricingModel(models.TextChoices):
        FIXED = 'fixed', 'Fixed Price'
        HOURLY = 'hourly', 'Hourly Rate'
        TIERED = 'tiered', 'Tiered Pricing'
        SUBSCRIPTION = 'subscription', 'Subscription'

    # Basic Information
    sku = models.CharField(max_length=50, unique=True, blank=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)

    # Classification
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    product_type = models.CharField(max_length=20, choices=ProductType.choices,
                                   default=ProductType.PHYSICAL)
    status = models.CharField(max_length=20, choices=Status.choices,
                             default=Status.DRAFT)

    # Pricing Model
    pricing_model = models.CharField(max_length=20, choices=PricingModel.choices,
                                    default=PricingModel.FIXED)

    # Base Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2,
                                    help_text="Base price for fixed pricing")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2,
                                     blank=True, null=True,
                                     help_text="Hourly rate for services/consultation")
    compare_price = models.DecimalField(max_digits=10, decimal_places=2,
                                       blank=True, null=True,
                                       help_text="Original price for showing discounts")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2,
                                    blank=True, null=True,
                                    help_text="Cost price for profit calculations")

    # Service-specific pricing
    minimum_hours = models.PositiveIntegerField(default=1,
                                               help_text="Minimum hours for consultation")
    estimated_duration = models.PositiveIntegerField(blank=True, null=True,
                                                   help_text="Estimated duration in hours")

    # Subscription pricing
    subscription_price = models.DecimalField(max_digits=10, decimal_places=2,
                                           blank=True, null=True)
    billing_cycle = models.CharField(max_length=20, blank=True,
                                    help_text="monthly, yearly, etc.")

    # Inventory (for physical products)
    track_inventory = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)

    # Physical attributes
    weight = models.DecimalField(max_digits=8, decimal_places=2,
                                blank=True, null=True, help_text="Weight in kg")
    dimensions = models.CharField(max_length=100, blank=True,
                                 help_text="L x W x H in cm")

    # Digital attributes
    download_url = models.URLField(blank=True, help_text="For digital products")
    download_limit = models.PositiveIntegerField(blank=True, null=True,
                                               help_text="Max downloads per purchase")

    # SEO & Marketing
    featured = models.BooleanField(default=False)
    featured_image = models.ImageField(upload_to=upload_to_path, blank=True)
    tags = models.CharField(max_length=255, blank=True,
                           help_text="Comma-separated tags")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'featured']),
            models.Index(fields=['category', 'status']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = generate_sku()
        if not self.slug:
            self.slug = generate_unique_slug(Product, self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug': self.slug})
    
    @property
    def price(self):
        """Get the effective price based on pricing model"""
        if self.pricing_model == self.PricingModel.FIXED:
            return self.base_price
        elif self.pricing_model == self.PricingModel.HOURLY:
            return self.hourly_rate or self.base_price
        elif self.pricing_model == self.PricingModel.SUBSCRIPTION:
            return self.subscription_price or self.base_price
        return self.base_price

    @property
    def is_on_sale(self):
        return self.compare_price and self.compare_price > self.price

    @property
    def discount_percentage(self):
        if self.is_on_sale:
            return round(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0
    
    @property
    def is_in_stock(self):
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0
    
    @property
    def is_low_stock(self):
        if not self.track_inventory:
            return False
        return self.stock_quantity <= self.low_stock_threshold


class ProductImage(TimestampMixin):
    """Product images"""
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_to_path)
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductVariant(TimestampMixin):
    """Product variants (size, color, etc.)"""
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="e.g., 'Large Red'")
    sku = models.CharField(max_length=50, unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Variant attributes
    size = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    material = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"{self.product.sku}-{generate_sku()[:6]}"
        super().save(*args, **kwargs)
    
    @property
    def effective_price(self):
        return self.price or self.product.price


class PricingTier(TimestampMixin):
    """Pricing tiers for different service levels"""
    name = models.CharField(max_length=100, help_text="e.g., 'Basic', 'Premium', 'Enterprise'")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    minimum_hours = models.PositiveIntegerField(default=1)
    features = models.JSONField(default=list, help_text="List of features included")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'price']

    def __str__(self):
        return f"{self.name} - {self.price}"


class ServicePackage(TimestampMixin):
    """Service packages for consultation and other services"""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)

    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    minimum_hours = models.PositiveIntegerField(default=1)
    estimated_duration = models.PositiveIntegerField(blank=True, null=True)

    # Package details
    deliverables = models.JSONField(default=list, help_text="What the client will receive")
    timeline = models.CharField(max_length=100, blank=True, help_text="e.g., '2-3 weeks'")
    revisions = models.PositiveIntegerField(default=2, help_text="Number of revisions included")

    # Status
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-featured', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(ServicePackage, self.name)
        super().save(*args, **kwargs)

    @property
    def price(self):
        return self.base_price
