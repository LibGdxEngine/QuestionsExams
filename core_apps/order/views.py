from rest_framework import status
from rest_framework.response import Response
from .models import Order
from rest_framework import status, viewsets
from .serializers import OrderSerializer
from .services import create_order_from_cart
from rest_framework.views import APIView
from ..coupon.models import Coupon
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, authentication, status


class OrderCreateView(generics.CreateAPIView):
    """Create an order from the user's cart"""
    serializer_class = OrderSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """POST: Create an order from the cart"""
        print(request.data)
        user = request.user
        print(user)
        order = create_order_from_cart(user)

        if order:
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

class OrderListView(generics.ListAPIView):
    """List all orders for the current user"""
    serializer_class = OrderSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter orders to only show those belonging to the current user"""
        return Order.objects.filter(user=self.request.user)

class OrderDetailView(generics.RetrieveAPIView):
    """Retrieve a specific order"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (authentication.TokenAuthentication,)
    
    def get_object(self):
        """Get the order, ensuring it belongs to the requesting user"""
        order_id = self.kwargs.get('pk')
        return get_object_or_404(Order, pk=order_id, user=self.request.user)

class OrderUpdateView(generics.UpdateAPIView):
    """Update an order's status (staff only)"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (authentication.TokenAuthentication,)
    
    def get_object(self):
        """Get the order to update"""
        order_id = self.kwargs.get('pk')
        return get_object_or_404(Order, pk=order_id)
    
    def update(self, request, *args, **kwargs):
        """PATCH: Update order status (Only Staff Users)"""
        order = self.get_object()

        if not request.user.is_staff:
            return Response(
                {"error": "Permission denied. Only staff can update status."},
                status=status.HTTP_403_FORBIDDEN,
            )

        order.status = request.data.get("status", order.status)
        order.save()
        return Response(OrderSerializer(order).data)

class ApplyCouponView(APIView):
    """Apply a coupon to an order"""
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (authentication.TokenAuthentication,)
    
    def post(self, request, *args, **kwargs):
        """Apply a coupon to the order."""
        try:
            order_id = request.data.get("order_id")
            order = get_object_or_404(Order, id=order_id, user=request.user)
            coupon_code = request.data.get("coupon_code")

            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                order.coupon = coupon
                order.save()
                return Response(
                    {
                        "message": "Coupon applied successfully",
                        "discount_type": coupon.discount_type,
                        "discount_value": coupon.discount_value,
                        "final_price": order.final_price,
                    },
                    status=status.HTTP_200_OK,
                )
            except Coupon.DoesNotExist:
                return Response(
                    {"error": "Invalid or inactive coupon"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )