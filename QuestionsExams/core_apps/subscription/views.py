from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SubscriptionPlan, Subscription
from .serializer import SubscriptionPlanSerializer, SubscriptionSerializer, PaymentSerializer
import stripe
import logging

from ..payments.models import Payment

logger = logging.getLogger(__name__)


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            plan_id = serializer.validated_data.get('plan_id')
            plan = SubscriptionPlan.objects.get(id=plan_id)

            # Create a subscription object
            subscription = Subscription(
                user=request.user,
                plan=plan,
                status='incomplete'
            )

            # Get or create Stripe customer
            customer_id = subscription.get_or_create_stripe_customer()

            # Make sure the plan has a Stripe price ID
            stripe_price_id = plan.create_stripe_price()

            # Create a payment intent for the first payment
            payment_intent = stripe.PaymentIntent.create(
                amount=int(plan.amount * 100),
                currency=plan.currency,
                customer=customer_id,
                metadata={
                    'user_id': str(request.user.id),  # Convert UUID to string
                    'plan_id': plan.id,
                    'subscription_type': 'new',
                }
            )

            # Create our payment record
            payment = Payment.objects.create(
                user=request.user,
                stripe_payment_intent_id=payment_intent.id,
                amount=plan.amount,
                currency=plan.currency,
                status='pending',
                description=f"Subscription to {plan.name}",
                metadata={
                    'plan_id': plan.id,
                    'subscription_type': 'new',
                }
            )

            # Save the subscription
            subscription.save()

            return Response({
                'subscription': SubscriptionSerializer(subscription).data,
                'payment': PaymentSerializer(payment).data,
                'client_secret': payment_intent.client_secret
            }, status=status.HTTP_201_CREATED)

        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Subscription plan not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        subscription = self.get_object()

        if not subscription.stripe_subscription_id:
            return Response({'error': 'No active subscription to cancel'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Cancel the subscription at the end of the billing period
            stripe_sub = stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )

            subscription.cancel_at_period_end = True
            subscription.save()

            return Response({'status': 'Subscription will be canceled at the end of the billing period'})

        except Exception as e:
            logger.error(f"Error canceling subscription: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        subscription = self.get_object()

        if not subscription.stripe_subscription_id or subscription.status != 'active':
            return Response({'error': 'No active subscription to reactivate'}, status=status.HTTP_400_BAD_REQUEST)

        if not subscription.cancel_at_period_end:
            return Response({'error': 'Subscription is not set to cancel'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Remove the cancellation at period end
            stripe_sub = stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=False
            )

            subscription.cancel_at_period_end = False
            subscription.save()

            return Response({'status': 'Subscription reactivated'})

        except Exception as e:
            logger.error(f"Error reactivating subscription: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)