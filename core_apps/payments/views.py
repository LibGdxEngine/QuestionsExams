from datetime import datetime

import pytz
import stripe
from django.conf import settings
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PaymentIntent, Subscription, Plan
from .serializer import SubscriptionSerializer, PlanSerializer
from ..order.models import Order

# Configure Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        try:
            # Get order or return error
            order_id = request.data.get('order_id')

            try:
                order = Order.objects.get(id=order_id, user=request.user)
            except Order.DoesNotExist:
                return Response(
                    {"error": "Order not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Create line items for Stripe from order items
            line_items = []
            for item in order.items.all():
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': item.product.name,
                            'description': item.product.description[:500],  # Stripe limits description length
                            'images': [request.build_absolute_uri(item.product.img.url)] if item.product.img else [],
                        },
                        'unit_amount': int(item.price * 100),  # Stripe requires cents
                    },
                    'quantity': item.quantity,
                })

            # Apply discount if coupon exists
            discounts = []
            if order.coupon:
                # Create a coupon in Stripe (you should handle this more robustly)
                stripe_coupon = None
                if order.coupon.discount_type == 'percentage':
                    stripe_coupon = stripe.Coupon.create(
                        percent_off=float(order.coupon.discount_value),
                        duration="once",
                        name=f"Coupon-{order.coupon.code}"
                    )
                else:
                    stripe_coupon = stripe.Coupon.create(
                        amount_off=int(order.coupon.discount_value * 100),  # Convert to cents
                        currency="usd",
                        duration="once",
                        name=f"Coupon-{order.coupon.code}"
                    )

                discounts.append({"coupon": stripe_coupon.id})

            # Create Checkout Session
            checkout_session = stripe.checkout.Session.create(
                customer_email=request.user.email,
                payment_method_types=['card'],
                line_items=line_items,
                discounts=discounts,
                mode='payment',
                success_url=request.build_absolute_uri('/api/v1/payments/success/') + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri('/api/v1/payments/cancel/'),
                metadata={
                    'order_id': order.id
                }
            )

            # Create a PaymentIntent record
            payment_intent = PaymentIntent.objects.create(
                user=request.user,
                order=order,
                stripe_payment_intent_id=checkout_session.id,
                amount=order.final_price,
                status='pending'
            )

            return Response({'checkout_url': checkout_session.url}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreateSubscriptionCheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        try:
            # Get plan
            plan_id = request.data.get('plan_id')

            try:
                plan = Plan.objects.get(id=plan_id)
            except Plan.DoesNotExist:
                return Response(
                    {"error": "Plan not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Create Checkout Session for subscription
            checkout_session = stripe.checkout.Session.create(
                customer_email=request.user.email,
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': plan.stripe_price_id,
                        'quantity': 1,
                    }
                ],
                mode='subscription',
                success_url=request.build_absolute_uri(
                    '/api/v1/payments/subscription/success/') + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri('/api/v1/payments/subscription/cancel/'),
                metadata={
                    'user_id': request.user.id,
                    'plan_id': plan.id
                }
            )

            return Response({'checkout_url': checkout_session.url}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def payment_success(request):
    session_id = request.GET.get('session_id')

    if not session_id:
        return Response({'error': 'No session ID provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Retrieve session info from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)

        # Ensure session has a valid order ID
        order_id = checkout_session.metadata.get('order_id')
        if not order_id:
            return Response({'error': 'Order ID missing in session metadata'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the order and update its status
        try:
            order = Order.objects.get(id=order_id)
            order.status = 'processing'  # Update status as needed
            order.save()
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Fix: Check `payment_status` instead of `payment_intent`
        if checkout_session.payment_status == "paid":
            payment_intent = PaymentIntent.objects.get(stripe_payment_intent_id=checkout_session.id)
            payment_intent.status = 'succeeded'
            payment_intent.save()
            return Response({'message': 'Payment successful!'}, status=status.HTTP_200_OK)

        return Response({'error': 'Payment not completed'}, status=status.HTTP_400_BAD_REQUEST)

    except stripe.error.StripeError as e:
        return Response({'error': f'Stripe error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def subscription_success(request):
    # Handle successful subscription
    session_id = request.GET.get('session_id')

    if not session_id:
        return Response({'error': 'No session ID provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Retrieve session info from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)

        # Get subscription details
        subscription_id = checkout_session.subscription
        if not subscription_id:
            return Response({'error': 'Subscription ID not found in session'}, status=status.HTTP_400_BAD_REQUEST)
        subscription_data = stripe.Subscription.retrieve(subscription_id)

        current_period_end = datetime.fromtimestamp(subscription_data.current_period_end, pytz.UTC)

        # Create subscription record
        Subscription.objects.create(
            user=request.user,
            stripe_subscription_id=subscription_id,
            stripe_customer_id=checkout_session.customer,
            status=subscription_data.status,
            current_period_end=current_period_end
        )

        return Response({'message': 'Subscription successful!'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    # Handle specific events
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Handle payment success
        if session.mode == 'payment':
            order_id = session.metadata.get('order_id')
            if order_id:
                order = Order.objects.get(id=order_id)
                order.status = 'processing'
                order.save()

                # Update payment intent
                try:
                    payment_intent = PaymentIntent.objects.get(stripe_payment_intent_id=session.payment_intent)
                    payment_intent.status = 'succeeded'
                    payment_intent.save()
                except PaymentIntent.DoesNotExist:
                    pass

        # Handle subscription success
        elif session.mode == 'subscription':
            user_id = session.metadata.get('user_id')
            plan_id = session.metadata.get('plan_id')

            if user_id and session.subscription:
                from django.contrib.auth import get_user_model
                User = get_user_model()

                try:
                    user = User.objects.get(id=user_id)
                    subscription_data = stripe.Subscription.retrieve(session.subscription)

                    # Create or update subscription
                    Subscription.objects.update_or_create(
                        stripe_subscription_id=session.subscription,
                        defaults={
                            'user': user,
                            'stripe_customer_id': session.customer,
                            'status': subscription_data.status,
                            'current_period_end': datetime.fromtimestamp(subscription_data.current_period_end, pytz.UTC)
                        }
                    )
                except User.DoesNotExist:
                    pass

    # Handle subscription updates
    elif event['type'] == 'customer.subscription.updated':
        subscription_data = event['data']['object']

        try:
            subscription = Subscription.objects.get(stripe_subscription_id=subscription_data.id)
            subscription.status = subscription_data.status
            subscription.current_period_end = subscription_data.current_period_end
            subscription.save()
        except Subscription.DoesNotExist:
            pass

    # Handle subscription cancellations
    elif event['type'] == 'customer.subscription.deleted':
        subscription_data = event['data']['object']

        try:
            subscription = Subscription.objects.get(stripe_subscription_id=subscription_data.id)
            subscription.status = 'canceled'
            subscription.save()
        except Subscription.DoesNotExist:
            pass

    return HttpResponse(status=200)


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing subscription plans
    """
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class UserSubscriptionView(APIView):
    """
    API endpoint for viewing user's subscription
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get(self, request):
        try:
            subscription = Subscription.objects.filter(user=request.user, status='active').first()
            if subscription:
                serializer = SubscriptionSerializer(subscription)
                return Response(serializer.data)
            return Response({"detail": "No active subscription found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)