from core_apps.cart.models import Cart
from .models import Order, OrderItem


def create_order_from_cart(user):
    """Create an order from the cart"""
    try:
        cart = Cart.objects.get(user=user)
        if not cart.items.exists():
            return None

        order = Order.objects.create(user=user, total_price=0)

        total_price = 0
        for cart_item in cart.items.all():
            order_item = OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            total_price += order_item.quantity * order_item.price

        order.total_price = total_price
        order.save()

        cart.items.all().delete()

        return order

    except Cart.DoesNotExist:
        return None
