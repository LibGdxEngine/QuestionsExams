from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from core_apps.order.models import Order
from core_apps.coupon.models import Coupon
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_coupon(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
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