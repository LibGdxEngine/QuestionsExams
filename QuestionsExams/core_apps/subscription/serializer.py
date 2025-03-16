from rest_framework import serializers
from .models import SubscriptionPlan, Subscription
from ..payments.models import Payment


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'description', 'amount', 'currency', 'interval']


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'plan', 'plan_id', 'status', 'current_period_start',
            'current_period_end', 'cancel_at_period_end', 'created_at'
        ]
        read_only_fields = ['user', 'status', 'current_period_start', 'current_period_end']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        plan_id = validated_data.pop('plan_id')
        plan = SubscriptionPlan.objects.get(id=plan_id)
        validated_data['plan'] = plan

        return Subscription.objects.create(**validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'currency', 'status', 'description', 'created_at']
        read_only_fields = ['status', 'created_at']