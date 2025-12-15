from rest_framework import serializers
from .models import PaymentIntent, Subscription, Plan
from ..order.models import Order

class PaymentIntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentIntent
        fields = ['id', 'stripe_payment_intent_id', 'amount', 'currency', 'status', 'created_at']
        read_only_fields = ['stripe_payment_intent_id', 'status']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'stripe_subscription_id', 'status', 'current_period_end', 'created_at']
        read_only_fields = ['stripe_subscription_id', 'status', 'current_period_end']


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'price', 'interval', 'description', 'features', 'popular', 'color', 'icon']