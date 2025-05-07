from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    img = models.ImageField(upload_to='products/', null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    product_images = models.ManyToManyField('ProductImage', blank=True, related_name='products')

class ProductImage(models.Model):
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_feature = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.products.first().name if self.products.exists() else 'No Product'}"

    def __str__(self):
        return self.name