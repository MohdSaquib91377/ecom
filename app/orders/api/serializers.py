from rest_framework import serializers


class CreateOrderSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=["COD", "RAZORPAY"], default="RAZORPAY")