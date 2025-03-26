from django.contrib import admin
from .models import PaymentIntent, Subscription, Plan

@admin.register(PaymentIntent)
class PaymentIntentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order', 'stripe_payment_intent_id', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'stripe_payment_intent_id')
    readonly_fields = ('stripe_payment_intent_id', 'created_at', 'updated_at')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'stripe_subscription_id', 'status', 'current_period_end')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'stripe_subscription_id')
    readonly_fields = ('stripe_subscription_id', 'stripe_customer_id', 'created_at', 'updated_at')


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'interval', 'stripe_price_id')
    list_filter = ('interval',)
    search_fields = ('name', 'stripe_price_id')