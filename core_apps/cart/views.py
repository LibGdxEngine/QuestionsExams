from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import authentication, permissions
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, AddToCartSerializer
from core_apps.products.models import Product

# generics
class CartViewSet(viewsets.GenericViewSet):
    serializer_class = CartSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

# create cart

    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart = self.get_object()
        serializer = AddToCartSerializer(data=request.data)

        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']

            product = Product.objects.get(id=product_id)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            cart_serializer = self.get_serializer(cart)
            return Response(cart_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def update_item(self, request):
        cart = self.get_object()
        serializer = AddToCartSerializer(data=request.data)

        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']

            try:
                cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
                if quantity <= 0:
                    cart_item.delete()
                else:
                    cart_item.quantity = quantity
                    cart_item.save()

                cart_serializer = self.get_serializer(cart)
                return Response(cart_serializer.data)
            except CartItem.DoesNotExist:
                return Response(
                    {"error": "Item not in cart"},
                    status=status.HTTP_404_NOT_FOUND
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        cart = self.get_object()
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = request.data.get('product_id')
        if not product_id:
            return Response(
                {"error": "Product ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            cart.save()
            return Response(
                {"result": "Product removed from cart"},
                status=status.HTTP_200_OK
            )
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Product not in cart"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = self.get_object()
        cart.items.all().delete()
        cart_serializer = self.get_serializer(cart)
        return Response({"result: Cart cleared"}, status=status.HTTP_200_OK)
