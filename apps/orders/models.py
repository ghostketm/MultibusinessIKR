"""
Order management models
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.core.mixins import TimestampMixin


class Order(TimestampMixin):
    """Main order model"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'
        REFUNDED = 'refunded', 'Refunded'
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        PARTIAL = 'partial', 'Partially Paid'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'
    
    # Order Identification
    order_number = models.CharField(max_length=50, unique=True, blank=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                related_name='orders')
    
    # Status
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices,
                                    default=PaymentStatus.PENDING)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Shipping Information
    shipping_name = models.CharField(max_length=255)
    shipping_email = models.EmailField()
    shipping_phone = models.CharField(max_length=20, blank=True)
    shipping_address_line1 = models.CharField(max_length=255)
    shipping_address_line2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default='Kenya')
    
    # Billing Information (can be same as shipping)
    billing_same_as_shipping = models.BooleanField(default=True)
    billing_name = models.CharField(max_length=255, blank=True)
    billing_email = models.EmailField(blank=True)
    billing_phone = models.CharField(max_length=20, blank=True)
    billing_address_line1 = models.CharField(max_length=255, blank=True)
    billing_address_line2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)
    
    # Additional Information
    notes = models.TextField(blank=True, help_text="Special instructions")
    internal_notes = models.TextField(blank=True, help_text="Internal notes (not visible to customer)")
    
    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True)
    shipped_date = models.DateTimeField(blank=True, null=True)
    delivered_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['order_number']),
        ]
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = f"IKR-{uuid.uuid4().hex[:8].upper()}"
        
        # Copy shipping to billing if same
        if self.billing_same_as_shipping:
            self.billing_name = self.shipping_name
            self.billing_email = self.shipping_email
            self.billing_phone = self.shipping_phone
            self.billing_address_line1 = self.shipping_address_line1
            self.billing_address_line2 = self.shipping_address_line2
            self.billing_city = self.shipping_city
            self.billing_state = self.shipping_state
            self.billing_postal_code = self.shipping_postal_code
            self.billing_country = self.shipping_country
        
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate order totals from line items"""
        self.subtotal = sum(item.total_price for item in self.items.all())
        
        # Simple tax calculation (16% VAT for Kenya)
        self.tax_amount = self.subtotal * Decimal('0.16')
        
        # Simple shipping calculation
        if self.subtotal < 1000:  # Free shipping over 1000 KES
            self.shipping_amount = Decimal('200')
        else:
            self.shipping_amount = Decimal('0')
        
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_amount - self.discount_amount
        self.save()
    
    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(TimestampMixin):
    """Individual items in an order"""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    product_variant = models.ForeignKey('products.ProductVariant', 
                                      on_delete=models.PROTECT, blank=True, null=True)
    
    # Snapshot of product info at time of purchase
    product_name = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=50)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Digital product delivery
    download_url = models.URLField(blank=True)
    download_count = models.PositiveIntegerField(default=0)
    download_expires_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.product_name} in {self.order}"
    
    def save(self, *args, **kwargs):
        # Store product snapshot
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_sku:
            self.product_sku = self.product_variant.sku if self.product_variant else self.product.sku
        if not self.unit_price:
            self.unit_price = self.product_variant.effective_price if self.product_variant else self.product.price
        
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class Payment(TimestampMixin):
    """Payment records for orders"""
    
    class PaymentMethod(models.TextChoices):
        MPESA = 'mpesa', 'M-Pesa'
        CARD = 'card', 'Credit/Debit Card'
        BANK = 'bank', 'Bank Transfer'
        CASH = 'cash', 'Cash on Delivery'
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    order = models.ForeignKey(Order, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Payment gateway info
    transaction_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(blank=True, null=True)
    
    # M-Pesa specific fields
    mpesa_phone = models.CharField(max_length=15, blank=True)
    mpesa_receipt = models.CharField(max_length=50, blank=True)
    mpesa_checkout_request_id = models.CharField(max_length=100, blank=True)
    mpesa_response_code = models.CharField(max_length=10, blank=True)
    
    def __str__(self):
        return f"Payment of {self.amount} for {self.order}"


class ShippingMethod(TimestampMixin):
    """Available shipping methods"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = models.PositiveIntegerField(help_text="Estimated delivery days")
    is_active = models.BooleanField(default=True)
    
    # Geographic restrictions
    available_countries = models.TextField(
        blank=True,
        help_text="Comma-separated list of country codes (leave blank for all)"
    )
    
    def __str__(self):
        return f"{self.name} - {self.price} KES"


class Coupon(TimestampMixin):
    """Discount coupons"""
    
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', 'Percentage'
        FIXED = 'fixed', 'Fixed Amount'
    
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Usage restrictions
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, 
                                        default=0, help_text="Minimum order amount")
    maximum_discount = models.DecimalField(max_digits=10, decimal_places=2,
                                         blank=True, null=True,
                                         help_text="Maximum discount amount for percentage coupons")
    usage_limit = models.PositiveIntegerField(blank=True, null=True,
                                            help_text="Maximum number of uses")
    usage_count = models.PositiveIntegerField(default=0)
    
    # Validity period
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    # Restrictions
    first_order_only = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def is_valid(self, order_amount=None, user=None):
        """Check if coupon is valid for use"""
        from django.utils import timezone
        
        if not self.is_active:
            return False, "Coupon is not active"
        
        if timezone.now() < self.valid_from:
            return False, "Coupon is not yet valid"
        
        if timezone.now() > self.valid_until:
            return False, "Coupon has expired"
        
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False, "Coupon usage limit reached"
        
        if order_amount and order_amount < self.minimum_amount:
            return False, f"Minimum order amount is {self.minimum_amount}"
        
        if self.first_order_only and user and user.orders.exists():
            return False, "Coupon is only valid for first orders"
        
        return True, "Valid"
    
    def calculate_discount(self, order_amount):
        """Calculate discount amount for given order amount"""
        if self.discount_type == self.DiscountType.FIXED:
            discount = min(self.discount_value, order_amount)
        else:  # percentage
            discount = order_amount * (self.discount_value / 100)
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
        
        return discount