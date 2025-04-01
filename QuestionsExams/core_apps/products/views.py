from rest_framework import viewsets, pagination
from rest_framework.response import Response
from rest_framework import status
from core_apps.products.models import Product
from core_apps.products.serializers import ProductSerializer


# Optional: Custom paginator if you want more control
class ProductPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(viewsets.ViewSet):
    # Add this line if you want to use the custom paginator
    pagination_class = ProductPagination

    def list(self, request):
        """GET: List all products with pagination"""
        products = Product.objects.all()

        # Get the paginator
        paginator = self.pagination_class()

        # Paginate the queryset
        paginated_products = paginator.paginate_queryset(products, request)

        # Serialize the paginated data
        serializer = ProductSerializer(paginated_products, many=True)

        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)