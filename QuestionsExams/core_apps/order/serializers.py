from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'total_price']

    def get_total_price(self, obj):
        return obj.total_price

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    final_price = serializers.SerializerMethodField()
    coupon_code = serializers.CharField(source="coupon.code", read_only=True, default=None)
    coupon_type = serializers.SerializerMethodField()
    coupon_discount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "user_email",
            "status",
            "coupon",
            "coupon_code",
            "coupon_discount",
            "coupon_type",
            "total_price",
            "final_price",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "total_price", "final_price", "created_at", "updated_at"]

    def get_final_price(self, obj):
        return obj.final_price  # Uses @property from Order

    def get_coupon_discount(self, obj):
        """Returns the discount value applied via coupon"""
        if obj.coupon:
            return obj.coupon.discount_value  # ✅ Fixed return value
        return None

    def get_coupon_type(self, obj):
        """Retrieve applied coupon type ('PERCENTAGE' or 'FIXED')"""
        return obj.coupon.discount_type if obj.coupon else None
