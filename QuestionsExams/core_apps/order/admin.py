from django.contrib import admin
from core_apps.order.models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    """Shows Order Items inside an Order in Admin"""
    model = OrderItem
    extra = 0
    readonly_fields = ['price', 'quantity', 'total_price']

    def total_price(self, obj):
        """Compute total price dynamically (handle None values)"""
        if obj.quantity is None or obj.price is None:
            return "N/A"
        return obj.quantity * obj.price

    total_price.short_description = "Total Price"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['total_price']

    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    search_fields = ['product__name', 'order__id']
