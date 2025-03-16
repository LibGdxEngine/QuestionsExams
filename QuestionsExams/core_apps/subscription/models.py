from django.db import models
from django.conf import settings
import stripe

# Configure Stripe with your API key
stripe.api_key = settings.STRIPE_SECRET_KEY


class SubscriptionPlan(models.Model):
    """Model to store subscription plans"""
    name = models.CharField(max_length=100)
    stripe_price_id = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='usd')
    interval = models.CharField(
        max_length=20,
        choices=[
            ('day', 'Daily'),
            ('week', 'Weekly'),
            ('month', 'Monthly'),
            ('year', 'Yearly'),
        ],
        default='month'
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.amount} {self.currency}/{self.interval}"

    def create_stripe_price(self):
        """Create a price object in Stripe if it doesn't exist"""
        if not self.stripe_price_id:
            # Convert decimal to integer cents/pence
            amount_in_cents = int(self.amount * 100)

            # Create a price object in Stripe
            price = stripe.Price.create(
                unit_amount=amount_in_cents,
                currency=self.currency,
                recurring={"interval": self.interval},
                product_data={"name": self.name},
            )
            self.stripe_price_id = price.id
            self.save()

        return self.stripe_price_id


class Subscription(models.Model):
    """Model to store user subscriptions"""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('incomplete', 'Incomplete'),
        ('incomplete_expired', 'Incomplete Expired'),
        ('trialing', 'Trialing'),
        ('unpaid', 'Unpaid'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='incomplete')
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.plan.name} - {self.status}"

    def get_or_create_stripe_customer(self):
        """Get or create a Stripe customer for the user"""
        if not self.stripe_customer_id:
            # Check if the user already has a customer ID in any subscription
            existing_sub = Subscription.objects.filter(
                user=self.user,
                stripe_customer_id__isnull=False
            ).first()

            if existing_sub and existing_sub.stripe_customer_id:
                self.stripe_customer_id = existing_sub.stripe_customer_id
                self.save()
            else:
                # Create a new customer in Stripe
                customer = stripe.Customer.create(
                    email=self.user.email,
                    name=f"{self.user.first_name} {self.user.last_name}".strip(),
                    metadata={"user_id": str(self.user.id)}  # Convert UUID to string
                )
                self.stripe_customer_id = customer.id
                self.save()

        return self.stripe_customer_id