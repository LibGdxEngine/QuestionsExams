from django.urls import path
from .views import apply_coupon

urlpatterns = [
    path('apply-coupon/<int:order_id>/', apply_coupon, name='apply-coupon'),
]
