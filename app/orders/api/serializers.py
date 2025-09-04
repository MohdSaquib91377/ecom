from rest_framework import serializers
from orders.models import Order, OrderItem
from store.models import Product
from accounts.models import Address

class CreateOrderSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=["COD", "RAZORPAY"], default="RAZORPAY")




# -------------------------------
# ORDER ITEM SERIALIZER
# -------------------------------
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_image = serializers.ImageField(source="product.image", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "product_image", "quantity", "price"]


# -------------------------------
# LIGHTWEIGHT ORDER LIST SERIALIZER
# -------------------------------
class OrderListSerializer(serializers.ModelSerializer):
    total_items = serializers.IntegerField(source="items.count", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    payment_display = serializers.CharField(source="get_payment_method_display", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "status_display",
            "payment_method",
            "payment_display",
            "total_price",
            "total_items",
            "created_at",
        ]


# -------------------------------
# DETAILED ORDER SERIALIZER
# -------------------------------
class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = serializers.CharField(source="shipping_address.full_address", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    payment_display = serializers.CharField(source="get_payment_method_display", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "status_display",
            "payment_method",
            "payment_display",
            "shipping_address",
            "total_price",
            "is_paid",
            "created_at",
            "items",
        ]
