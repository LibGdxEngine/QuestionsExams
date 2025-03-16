from django.db import models
from django.conf import settings
from core_apps.products.models import Product


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.email}"

    @property
    def total_price(self):
        # Use a safer approach for summing up the totals
        total = 0
        for item in self.items.all():
            if hasattr(item, 'total_price'):
                item_total = item.total_price
                if item_total is not None:
                    total += item_total
        return total


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        # Add a check to handle None values
        if not self.product or not hasattr(self.product,'price') or self.product.price is None or self.quantity is None:
            return 0
        return self.product.price * self.quantity