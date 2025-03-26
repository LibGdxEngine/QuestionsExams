from django.db import models
from django.conf import settings

from core_apps.coupon.models import Coupon
from core_apps.products.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.email} - {self.status} - ${self.total_price} - ${self.final_price}"

    def calculate_total_price(self):
        """Calculate total price based on order items."""
        self.total_price = sum(item.total_price for item in self.items.all())
        self.save()

    @property
    def final_price(self):
        if self.coupon:
            if self.coupon.discount_type == Coupon.PERCENTAGE:
                discount_amount = (self.total_price * self.coupon.discount_value) / 100  # Percentage-based discount
            else:
                discount_amount = self.coupon.discount_value  # Fixed amount discount

            return max(self.total_price - discount_amount, 0)  # Ensure price isn't negative
        return self.total_price

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        """Calculate total price for this order item."""
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (${self.total_price})"
