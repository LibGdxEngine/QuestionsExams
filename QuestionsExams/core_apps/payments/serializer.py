from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    stripe_payment_id = serializers.CharField()
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'currency', 'status', 'description', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

class PaymentIntentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(default='usd', max_length=3)
    description = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False)

class PaymentIntentResponseSerializer(serializers.Serializer):
    client_secret = serializers.CharField()
    payment_intent_id = serializers.CharField()
    publishable_key = serializers.CharField()