from django.contrib import admin
from .models import SubscriptionPlan, Subscription
from ..payments.models import Payment


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'currency', 'interval', 'is_active')
    list_filter = ('is_active', 'interval', 'currency')
    search_fields = ('name', 'description')
    readonly_fields = ('stripe_price_id',)

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Pricing Details', {
            'fields': ('amount', 'currency', 'interval')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_price_id',),
            'classes': ('collapse',)
        }),
    )

    actions = ['create_stripe_prices']

    def create_stripe_prices(self, request, queryset):
        for plan in queryset:
            plan.create_stripe_price()
        self.message_user(request, f"Created Stripe prices for {queryset.count()} plans")

    create_stripe_prices.short_description = "Create Stripe prices for selected plans"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'current_period_end', 'cancel_at_period_end')
    list_filter = ('status', 'cancel_at_period_end', 'plan')
    search_fields = ('user__username', 'user__email', 'stripe_subscription_id', 'stripe_customer_id')
    readonly_fields = (
        'stripe_subscription_id', 'stripe_customer_id',
        'current_period_start', 'ended_at',
        'created_at', 'updated_at'
    )

    fieldsets = (
        (None, {
            'fields': ('user', 'plan', 'status', 'cancel_at_period_end')
        }),
        ('Period Information', {
            'fields': ('current_period_start', 'current_period_end', 'ended_at')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_subscription_id', 'stripe_customer_id'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['cancel_subscriptions', 'reactivate_subscriptions']

    def cancel_subscriptions(self, request, queryset):
        import stripe
        from django.conf import settings

        stripe.api_key = settings.STRIPE_SECRET_KEY

        canceled = 0
        for subscription in queryset:
            if subscription.stripe_subscription_id and not subscription.cancel_at_period_end:
                try:
                    stripe.Subscription.modify(
                        subscription.stripe_subscription_id,
                        cancel_at_period_end=True
                    )

                    subscription.cancel_at_period_end = True
                    subscription.save()
                    canceled += 1
                except Exception as e:
                    self.message_user(request, f"Error canceling subscription {subscription.id}: {str(e)}",
                                      level='ERROR')

        self.message_user(request, f"Canceled {canceled} subscriptions")

    cancel_subscriptions.short_description = "Cancel selected subscriptions at period end"

    def reactivate_subscriptions(self, request, queryset):
        import stripe
        from django.conf import settings

        stripe.api_key = settings.STRIPE_SECRET_KEY

        reactivated = 0
        for subscription in queryset:
            if subscription.stripe_subscription_id and subscription.cancel_at_period_end:
                try:
                    stripe.Subscription.modify(
                        subscription.stripe_subscription_id,
                        cancel_at_period_end=False
                    )

                    subscription.cancel_at_period_end = False
                    subscription.save()
                    reactivated += 1
                except Exception as e:
                    self.message_user(request, f"Error reactivating subscription {subscription.id}: {str(e)}",
                                      level='ERROR')

        self.message_user(request, f"Reactivated {reactivated} subscriptions")

    reactivate_subscriptions.short_description = "Reactivate selected canceled subscriptions"


# You might also want to customize the Payment admin if you haven't already
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency')
    search_fields = ('user__username', 'user__email', 'stripe_payment_intent_id', 'description')
    readonly_fields = ('stripe_payment_intent_id', 'created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('user', 'amount', 'currency', 'status', 'description')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Stripe Integration', {
            'fields': ('stripe_payment_intent_id',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )