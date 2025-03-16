from django.contrib import admin
from django.contrib import messages
from .models import Cart, CartItem
from core_apps.order.services import create_order_from_cart

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['total_price']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'item_count', 'total_price', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['total_price']
    inlines = [CartItemInline]
    actions = ['create_order']

    def item_count(self, obj):
        return obj.items.count()

    item_count.short_description = 'Number of Items'

    def create_order(self, request, queryset):
        """Admin action to create an order from the selected cart"""
        for cart in queryset:
            order = create_order_from_cart(cart.user)
            if order:
                messages.success(request, f"Order {order.id} created successfully!")
            else:
                messages.error(request, f"Failed to create order for {cart.user}. Cart may be empty.")

    create_order.short_description = "Create Order from Cart"