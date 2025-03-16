from django.urls import path
from .views import create_payment, webhook

urlpatterns = [
    path('create-payment/', create_payment, name='create_payment'),
    path('webhook/', webhook, name='stripe_webhook'),
]