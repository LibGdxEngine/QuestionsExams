from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock
from core_apps.subscription.models import SubscriptionPlan, Subscription
import stripe

User = get_user_model()

class SubscriptionViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        self.plan = SubscriptionPlan.objects.create(
            name='Test Plan',
            stripe_price_id='price_123',
            amount=10.00,
            currency='usd',
            interval='month',
            is_active=True
        )
        self.client.force_authenticate(user=self.user)
        self.subscription_url = reverse('subscription-list')  # Ensure this matches your urls.py

    @patch('stripe.PaymentIntent.create')
    @patch('stripe.Customer.create')
    @patch('core_apps.subscription.models.Subscription.get_or_create_stripe_customer')
    @patch('core_apps.subscription.models.SubscriptionPlan.create_stripe_price')
    def test_create_subscription(self, mock_create_stripe_price, mock_get_stripe_customer, mock_stripe_customer, mock_stripe_payment_intent):
        # Ensure methods return expected data types
        mock_get_stripe_customer.return_value = "cus_123"  # Should be a string, not a dict
        mock_create_stripe_price.return_value = "price_123"  # Should be a string
        mock_stripe_customer.return_value = MagicMock(id="cus_123")  # Ensure it has an `.id` attribute
        mock_stripe_payment_intent.return_value = MagicMock(id="pi_123", client_secret="secret_123")

        data = {'plan_id': self.plan.id}
        response = self.client.post(self.subscription_url, data, format='json')

        print(response.data)  # Debugging: Check response content

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Expecting 201
        self.assertIn('subscription', response.data)
        self.assertIn('payment', response.data)
        self.assertIn('client_secret', response.data)

    @patch('stripe.Subscription.modify')
    def test_cancel_subscription(self, mock_stripe_subscription_modify):
        subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            status='active',
            stripe_subscription_id='sub_123'
        )

        cancel_url = reverse('subscription-cancel', args=[subscription.id])
        response = self.client.post(cancel_url)

        subscription.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(subscription.cancel_at_period_end)
        self.assertEqual(response.data['status'], 'Subscription will be canceled at the end of the billing period')

    @patch('stripe.Subscription.modify')
    def test_reactivate_subscription(self, mock_stripe_subscription_modify):
        subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            status='active',
            stripe_subscription_id='sub_123',
            cancel_at_period_end=True
        )

        reactivate_url = reverse('subscription-reactivate', args=[subscription.id])
        response = self.client.post(reactivate_url)

        subscription.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(subscription.cancel_at_period_end)
        self.assertEqual(response.data['status'], 'Subscription reactivated')
