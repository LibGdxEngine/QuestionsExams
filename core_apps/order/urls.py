from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderListView,
    OrderCreateView,
    OrderDetailView,
    OrderUpdateView,
    ApplyCouponView,
)

urlpatterns = [
    path("orders/", OrderListView.as_view(), name="order-list"),
    path("orders/create/", OrderCreateView.as_view(), name="order-create"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:pk>/update/", OrderUpdateView.as_view(), name="order-update"),
    path("orders/apply-coupon/", ApplyCouponView.as_view(), name="apply-coupon"),
]
