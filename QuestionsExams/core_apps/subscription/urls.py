from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubscriptionPlanViewSet, SubscriptionViewSet
from .webhooks import stripe_webhook_view

router = DefaultRouter()
router.register(r'subscription-plans', SubscriptionPlanViewSet)
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/', stripe_webhook_view, name='stripe-webhook'),
]