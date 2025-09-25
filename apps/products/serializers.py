"""
Serializers for the products app
"""
from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductVariant


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'image']


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for Product Images"""
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_primary']


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for Product Variants"""
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'sku', 'effective_price', 'stock_quantity', 'size', 'color']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for the Product model"""
    category = serializers.StringRelatedField()
    class Meta:
        model = Product
        fields = '__all__'