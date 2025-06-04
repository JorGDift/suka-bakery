from rest_framework import serializers

from .models import Order, OrderDetail

class OrderDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    cake_flavor_name = serializers.CharField(source='cake_flavor.name')
    cake_size_name = serializers.CharField(source='cake_size.name')

    class Meta:
        model = OrderDetail
        fields = ['product_name', 'cake_flavor_name', 'cake_size_name',
                  'quantity', 'item_unit_price', 'item_total']

class OrderSerializer(serializers.ModelSerializer):
    details = OrderDetailSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display')

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'status', 'status_display',
                 'subtotal', 'total_items', 'shipping_cost', 'total', 'details']