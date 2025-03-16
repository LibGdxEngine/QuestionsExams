from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import Order, OrderItem
from core_apps.coupon.models import Coupon
from core_apps.products.models import Product

User = get_user_model()


class OrderViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',  # Add first_name
            last_name='User'    # Add last_name
        )
        self.staff_user = User.objects.create_user(
            email='staffuser@example.com',
            password='testpass123',
            is_staff=True,
            first_name='Staff',  # Add first_name
            last_name='User'    # Add last_name
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=100.00
        )
        self.coupon = Coupon.objects.create(
            code='TEST123',
            discount_type=Coupon.PERCENTAGE,
            discount_value=10,
            is_active=True
        )
        self.order = Order.objects.create(
            user=self.user,
            total_price=100.00,
            status='pending'
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=100.00
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_order(self):
        """Test retrieving a specific order."""
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order.id)

    def test_update_order_status_by_staff(self):
        """Test updating order status by a staff user."""
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        data = {'status': 'processing'}
        # Use PUT instead of PATCH since your update method doesn't handle partial updates
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'processing')

    def test_update_order_status_by_non_staff(self):
        """Test updating order status by a non-staff user (should fail)."""
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        data = {'status': 'processing'}
        # Use PUT instead of PATCH since your update method doesn't handle partial updates
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_apply_coupon_to_order(self):
        """Test applying a valid coupon to the order."""
        url = reverse('order-apply-coupon', kwargs={'pk': self.order.id})
        data = {'coupon_code': 'TEST123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.coupon.code, 'TEST123')

    def test_apply_invalid_coupon_to_order(self):
        """Test applying an invalid coupon to the order."""
        url = reverse('order-apply-coupon', kwargs={'pk': self.order.id})
        data = {'coupon_code': 'INVALID'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_nonexistent_order(self):
        """Test retrieving an order that does not exist."""
        url = reverse('order-detail', kwargs={'pk': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)