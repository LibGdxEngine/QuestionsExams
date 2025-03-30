from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import authentication, permissions
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Order
from .serializers import OrderSerializer
from .services import create_order_from_cart
from ..coupon.models import Coupon


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """POST: Create an order from the cart"""
        user = request.user
        order = create_order_from_cart(user)

        if order:
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_order(self, request):
        """Alternative create method (if needed separately)"""
        return self.create(request)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """GET: Retrieve a specific order"""
        try:
            order = Order.objects.get(pk=pk, user=request.user)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    # create function to list all orders

    def list(self, request, *args, **kwargs):
        """GET: List all orders"""
        queryset = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, pk=None, *args, **kwargs):
        """PATCH: Update order status (Only Staff Users)"""
        try:
            order = Order.objects.get(pk=pk)

            if not request.user.is_staff:
                return Response({"error": "Permission denied. Only staff can update status."},
                                status=status.HTTP_403_FORBIDDEN)

            order.status = request.data.get("status", order.status)
            order.save()
            return Response(OrderSerializer(order).data)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def apply_coupon(self, request):
        """Apply a coupon to the order."""
        try:
            order_id = request.data.get("order_id")
            order = Order.objects.get(id=order_id, user=request.user)  # ✅ Use 'pk' from URL
            coupon_code = request.data.get("coupon_code")

            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                order.coupon = coupon
                order.save()
                return Response({
                    "message": "Coupon applied successfully",
                    "discount_type": coupon.discount_type,
                    "discount_value": coupon.discount_value,
                    "final_price": order.final_price
                }, status=status.HTTP_200_OK)
            except Coupon.DoesNotExist:
                return Response({"error": "Invalid or inactive coupon"}, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)