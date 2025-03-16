from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import stripe
from django.conf import settings
import json
import logging
from .models import Subscription, SubscriptionPlan
from django.utils import timezone

from ..payments.models import Payment

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def stripe_webhook_view(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid Stripe payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid Stripe signature: {str(e)}")
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        handle_payment_intent_succeeded(payment_intent)
    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        handle_payment_intent_failed(payment_intent)
    elif event.type == 'customer.subscription.created':
        subscription = event.data.object
        handle_subscription_created(subscription)
    elif event.type == 'customer.subscription.updated':
        subscription = event.data.object
        handle_subscription_updated(subscription)
    elif event.type == 'customer.subscription.deleted':
        subscription = event.data.object
        handle_subscription_deleted(subscription)

    return HttpResponse(status=200)


def handle_payment_intent_succeeded(payment_intent):
    try:
        # Find the corresponding payment in our DB
        payment = Payment.objects.filter(stripe_payment_intent_id=payment_intent.id).first()

        if not payment:
            logger.error(f"Payment not found for payment intent: {payment_intent.id}")
            return

        # Update payment status
        payment.status = 'completed'
        payment.save()

        # Check if this is for a new subscription
        if 'subscription_type' in payment.metadata and payment.metadata['subscription_type'] == 'new':
            # Create the subscription in Stripe
            plan_id = payment.metadata.get('plan_id')

            if not plan_id:
                logger.error(f"Plan ID not found in payment metadata: {payment_intent.id}")
                return

            try:
                plan = SubscriptionPlan.objects.get(id=plan_id)
                subscription = Subscription.objects.filter(
                    user=payment.user,
                    plan=plan,
                    status='incomplete'
                ).order_by('-created_at').first()

                if not subscription:
                    logger.error(f"Subscription not found for payment: {payment_intent.id}")
                    return

                # Create subscription in Stripe
                stripe_subscription = stripe.Subscription.create(
                    customer=subscription.stripe_customer_id,
                    items=[
                        {"price": plan.stripe_price_id},
                    ],
                    metadata={
                        "user_id": str(payment.user.id),  # Convert UUID to string
                        "subscription_id": subscription.id,
                        "plan_id": plan.id,
                    }
                )

                # Update our subscription record
                subscription.stripe_subscription_id = stripe_subscription.id
                subscription.status = stripe_subscription.status
                subscription.current_period_start = timezone.datetime.fromtimestamp(
                    stripe_subscription.current_period_start)
                subscription.current_period_end = timezone.datetime.fromtimestamp(
                    stripe_subscription.current_period_end)
                subscription.save()

            except SubscriptionPlan.DoesNotExist:
                logger.error(f"Plan not found for ID: {plan_id}")
            except Exception as e:
                logger.error(f"Error creating subscription after payment: {str(e)}")

    except Exception as e:
        logger.error(f"Error handling payment_intent.succeeded: {str(e)}")


def handle_payment_intent_failed(payment_intent):
    try:
        # Find the corresponding payment in our DB
        payment = Payment.objects.filter(stripe_payment_intent_id=payment_intent.id).first()

        if not payment:
            logger.error(f"Payment not found for payment intent: {payment_intent.id}")
            return

        # Update payment status
        payment.status = 'failed'
        payment.save()

        # If this was for a new subscription, update the subscription status
        if 'subscription_type' in payment.metadata and payment.metadata['subscription_type'] == 'new':
            plan_id = payment.metadata.get('plan_id')

            if plan_id:
                try:
                    plan = SubscriptionPlan.objects.get(id=plan_id)
                    subscription = Subscription.objects.filter(
                        user=payment.user,
                        plan=plan,
                        status='incomplete'
                    ).order_by('-created_at').first()

                    if subscription:
                        subscription.status = 'incomplete_expired'
                        subscription.save()

                except SubscriptionPlan.DoesNotExist:
                    logger.error(f"Plan not found for ID: {plan_id}")
                except Exception as e:
                    logger.error(f"Error updating subscription after failed payment: {str(e)}")

    except Exception as e:
        logger.error(f"Error handling payment_intent.failed: {str(e)}")


def handle_subscription_created(subscription):
    # This is mostly handled in the payment_intent.succeeded handler
    pass


def handle_subscription_updated(subscription):
    try:
        # Find the corresponding subscription in our DB
        db_subscription = Subscription.objects.filter(stripe_subscription_id=subscription.id).first()

        if not db_subscription:
            logger.error(f"Subscription not found for Stripe subscription: {subscription.id}")
            return

        # Update subscription status and period details
        db_subscription.status = subscription.status
        db_subscription.current_period_start = timezone.datetime.fromtimestamp(subscription.current_period_start)
        db_subscription.current_period_end = timezone.datetime.fromtimestamp(subscription.current_period_end)
        db_subscription.cancel_at_period_end = subscription.cancel_at_period_end

        if subscription.status == 'canceled' and subscription.ended_at:
            db_subscription.ended_at = timezone.datetime.fromtimestamp(subscription.ended_at)

        db_subscription.save()

    except Exception as e:
        logger.error(f"Error handling subscription.updated: {str(e)}")


def handle_subscription_deleted(subscription):
    try:
        # Find the corresponding subscription in our DB
        db_subscription = Subscription.objects.filter(stripe_subscription_id=subscription.id).first()

        if not db_subscription:
            logger.error(f"Subscription not found for Stripe subscription: {subscription.id}")
            return

        # Update subscription status
        db_subscription.status = 'canceled'

        if subscription.ended_at:
            db_subscription.ended_at = timezone.datetime.fromtimestamp(subscription.ended_at)
        else:
            db_subscription.ended_at = timezone.now()

        db_subscription.save()

    except Exception as e:
        logger.error(f"Error handling subscription.deleted: {str(e)}")