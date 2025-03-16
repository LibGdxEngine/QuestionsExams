from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
from rest_framework.authtoken.models import Token
from core_apps.payments.models import Payment
import json

User = get_user_model()


class PaymentViewSetTestCase(APITestCase):
    def setUp(self):
        """Set up test user, authentication, and test data."""
        self.user = User.objects.create_user(
            email='test@example.com', password='password123', first_name='Test', last_name='User'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.payment_url = reverse('create_payment')  # Adjust if needed
        self.webhook_url = reverse('stripe_webhook')  # Adjust if needed

    @patch('stripe.PaymentIntent.create')
    def test_create_payment(self, mock_stripe_payment_intent):
        """Test successful payment creation."""
        # Mock Stripe PaymentIntent response
        mock_intent = MagicMock()
        mock_intent.id = "pi_123"
        mock_intent.client_secret = "secret_123"
        mock_stripe_payment_intent.return_value = mock_intent

        data = {
            'amount': 50.00,
            'currency': 'usd',
            'description': 'Test payment'
        }

        response = self.client.post(self.payment_url, data, format='json')

        print(response.json())  # Debugging output

        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Expecting success
        self.assertIn('client_secret', response.json())
        self.assertIn('payment_id', response.json())

        # Check if payment was created in the database
        payment = Payment.objects.get(user=self.user)
        self.assertEqual(payment.amount, 50.00)
        self.assertEqual(payment.currency, 'usd')
        self.assertEqual(payment.description, 'Test payment')
        self.assertEqual(payment.status, 'pending')

    def test_create_payment_without_authentication(self):
        """Test creating payment without authentication should fail."""
        self.client.credentials()  # Remove auth token
        data = {'amount': 50.00, 'currency': 'usd', 'description': 'Test payment'}
        response = self.client.post(self.payment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('stripe.Webhook.construct_event')
    def test_webhook_payment_successful(self, mock_construct_event):
        """Test webhook updates payment status to completed."""
        payment = Payment.objects.create(
            user=self.user, stripe_payment_intent_id="pi_123", amount=50.00, currency="usd", status="pending"
        )

        # Mock Stripe webhook event
        mock_event = {'type': 'payment_intent.succeeded', 'data': {'object': {'id': "pi_123"}}}
        mock_construct_event.return_value = mock_event

        response = self.client.post(
            self.webhook_url, data=json.dumps(mock_event), content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'completed')

    @patch('stripe.Webhook.construct_event')
    def test_webhook_payment_failed(self, mock_construct_event):
        """Test webhook updates payment status to failed."""
        payment = Payment.objects.create(
            user=self.user, stripe_payment_intent_id="pi_123", amount=50.00, currency="usd", status="pending"
        )

        # Mock Stripe webhook event for failed payment
        mock_event = {'type': 'payment_intent.payment_failed', 'data': {'object': {'id': "pi_123"}}}
        mock_construct_event.return_value = mock_event

        response = self.client.post(
            self.webhook_url, data=json.dumps(mock_event), content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'failed')
