from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from .models import Payment
from django.contrib.auth import get_user_model
import stripe
import json

# Get custom user model
User = get_user_model()

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def create_payment(request):
    if request.method == 'POST':
        auth_header = request.headers.get('Authorization')

        if auth_header:
            try:
                token_key = auth_header.split(' ')[1]  # Get token from "Token <key>"
                token = Token.objects.get(key=token_key)
                user = token.user
            except (IndexError, Token.DoesNotExist):
                return JsonResponse({'error': 'Invalid token'}, status=401)
        else:
            return JsonResponse({'error': 'Authentication credentials were not provided'}, status=401)

        data = json.loads(request.body)
        amount = data.get('amount')
        currency = data.get('currency', 'usd')
        description = data.get('description', '')

        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency=currency,
                description=description,
                metadata={"user_id": user.id},
            )

            payment = Payment.objects.create(
                user=user,
                stripe_payment_intent_id=intent.id,
                amount=amount,
                currency=currency,
                description=description,
                status='pending'
            )

            return JsonResponse({'client_secret': intent.client_secret, 'payment_id': payment.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def webhook(request):
    payload = request.body
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        payment = get_object_or_404(Payment, stripe_payment_intent_id=intent['id'])
        payment.status = 'completed'
        payment.save()
    elif event['type'] == 'payment_intent.payment_failed':
        intent = event['data']['object']
        payment = get_object_or_404(Payment, stripe_payment_intent_id=intent['id'])
        payment.status = 'failed'
        payment.save()

    return JsonResponse({'status': 'success'})