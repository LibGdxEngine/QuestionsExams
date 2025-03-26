from django.db import models


class Coupon(models.Model):
    PERCENTAGE = 'percentage'
    FIXED = 'fixed'

    DISCOUNT_TYPE_CHOICES = [
        (PERCENTAGE, 'Percentage'),
        (FIXED, 'Fixed Amount'),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default=FIXED)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)  # Can be percentage or fixed amount
    is_active = models.BooleanField(default=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.code} ({self.discount_type} - {self.discount_value})"