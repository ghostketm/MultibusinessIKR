"""
Admin configuration for products
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ProductVariant, PricingTier, ServicePackage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'sort_order')


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ('name', 'sku', 'price', 'stock_quantity', 'size', 'color', 'is_active')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'sort_order', 'created_at')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'product_type', 'price', 
                   'stock_status', 'status', 'featured')
    list_filter = ('status', 'product_type', 'featured', 'category', 'created_at')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'description', 'short_description')
        }),
        ('Classification', {
            'fields': ('category', 'product_type', 'status', 'tags')
        }),
        ('Pricing Model', {
            'fields': ('pricing_model', 'base_price', 'hourly_rate', 'compare_price', 'cost_price')
        }),
        ('Service Pricing', {
            'fields': ('minimum_hours', 'estimated_duration'),
            'classes': ('collapse',)
        }),
        ('Subscription Pricing', {
            'fields': ('subscription_price', 'billing_cycle'),
            'classes': ('collapse',)
        }),
        ('Inventory', {
            'fields': ('track_inventory', 'stock_quantity', 'low_stock_threshold')
        }),
        ('Physical Attributes', {
            'fields': ('weight', 'dimensions'),
            'classes': ('collapse',)
        }),
        ('Digital Attributes', {
            'fields': ('download_url', 'download_limit'),
            'classes': ('collapse',)
        }),
        ('SEO & Marketing', {
            'fields': ('featured', 'featured_image', 'meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )
    
    def stock_status(self, obj):
        if not obj.track_inventory:
            return format_html('<span style="color: green;">Not Tracked</span>')
        elif obj.stock_quantity <= 0:
            return format_html('<span style="color: red;">Out of Stock</span>')
        elif obj.stock_quantity <= obj.low_stock_threshold:
            return format_html('<span style="color: orange;">Low Stock ({})</span>', obj.stock_quantity)
        else:
            return format_html('<span style="color: green;">In Stock ({})</span>', obj.stock_quantity)
    stock_status.short_description = 'Stock Status'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_primary', 'sort_order', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name', 'alt_text')


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'sku', 'effective_price', 'stock_quantity', 'is_active')
    list_filter = ('is_active', 'size', 'color')
    search_fields = ('product__name', 'name', 'sku')


@admin.register(PricingTier)
class PricingTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'hourly_rate', 'minimum_hours', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    list_editable = ('price', 'hourly_rate', 'minimum_hours', 'is_active', 'sort_order')


@admin.register(ServicePackage)
class ServicePackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price', 'hourly_rate', 'minimum_hours', 'is_active', 'featured')
    list_filter = ('is_active', 'featured')
    search_fields = ('name', 'description', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('base_price', 'hourly_rate', 'minimum_hours', 'is_active', 'featured')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'short_description')
        }),
        ('Pricing', {
            'fields': ('base_price', 'hourly_rate', 'minimum_hours', 'estimated_duration')
        }),
        ('Package Details', {
            'fields': ('deliverables', 'timeline', 'revisions')
        }),
        ('Status', {
            'fields': ('is_active', 'featured')
        }),
    )
