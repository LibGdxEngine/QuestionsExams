from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'plans', views.PlanViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create-checkout-session/', views.CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('create-subscription/', views.CreateSubscriptionCheckoutView.as_view(), name='create-subscription'),
    path('success/', views.payment_success, name='payment-success'),
    path('cancel/', views.payment_cancel,  name='payment-cancel'),
    path('subscription/success/', views.subscription_success, name='subscription-success'),
    path('webhook/', views.stripe_webhook, name='stripe-webhook'),
    path('my-subscription/', views.UserSubscriptionView.as_view(), name='my-subscription'),
]