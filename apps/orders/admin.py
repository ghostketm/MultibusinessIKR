"""
Admin configuration for orders
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, Payment, ShippingMethod, Coupon


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)
    fields = ('product', 'product_variant', 'quantity', 'unit_price', 'total_price')


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'status', 'payment_status', 
                   'total_amount', 'items_count', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at', 'shipping_country')
    search_fields = ('order_number', 'customer__username', 'customer__email', 
                    'shipping_name', 'shipping_email')
    readonly_fields = ('order_number', 'subtotal', 'tax_amount', 'total_amount', 
                      'items_count', 'created_at', 'updated_at')
    inlines = [OrderItemInline, PaymentInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status', 'payment_status')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax_amount', 'shipping_amount', 'discount_amount', 'total_amount')
        }),
        ('Shipping Address', {
            'fields': ('shipping_name', 'shipping_email', 'shipping_phone',
                      'shipping_address_line1', 'shipping_address_line2',
                      'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country')
        }),
        ('Billing Address', {
            'fields': ('billing_same_as_shipping', 'billing_name', 'billing_email', 'billing_phone',
                      'billing_address_line1', 'billing_address_line2',
                      'billing_city', 'billing_state', 'billing_postal_code', 'billing_country'),
            'classes': ('collapse',)
        }),
        ('Tracking & Delivery', {
            'fields': ('tracking_number', 'shipped_date', 'delivered_date')
        }),
        ('Notes', {
            'fields': ('notes', 'internal_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_shipped', 'calculate_totals']
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status=Order.Status.CONFIRMED)
    mark_as_confirmed.short_description = "Mark selected orders as confirmed"
    
    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone
        queryset.update(status=Order.Status.SHIPPED, shipped_date=timezone.now())
    mark_as_shipped.short_description = "Mark selected orders as shipped"
    
    def calculate_totals(self, request, queryset):
        for order in queryset:
            order.calculate_totals()
    calculate_totals.short_description = "Recalculate totals for selected orders"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'method', 'status', 'created_at')
    list_filter = ('method', 'status', 'created_at')
    search_fields = ('order__order_number', 'transaction_id', 'mpesa_receipt')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'estimated_days', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'discount_display', 'usage_display', 
                   'valid_from', 'valid_until', 'is_active')
    list_filter = ('discount_type', 'is_active', 'first_order_only', 'valid_from')
    search_fields = ('code', 'name', 'description')
    readonly_fields = ('usage_count', 'created_at', 'updated_at')
    
    def discount_display(self, obj):
        if obj.discount_type == obj.DiscountType.FIXED:
            return f"{obj.discount_value} KES"
        else:
            return f"{obj.discount_value}%"
    discount_display.short_description = 'Discount'
    
    def usage_display(self, obj):
        if obj.usage_limit:
            return f"{obj.usage_count}/{obj.usage_limit}"
        return f"{obj.usage_count}/∞"
    usage_display.short_description = 'Usage'