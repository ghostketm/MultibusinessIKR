"""
Serializers for the orders app
"""
from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for items within an order"""
    class Meta:
        model = OrderItem
        fields = ['product_name', 'product_sku', 'unit_price', 'quantity', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for the Order model"""
    items = OrderItemSerializer(many=True, read_only=True)
    customer = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = [
            'order_number', 'customer', 'status', 'payment_status',
            'subtotal', 'tax_amount', 'shipping_amount', 'discount_amount',
            'total_amount', 'created_at', 'items'
        ]
        read_only_fields = fields