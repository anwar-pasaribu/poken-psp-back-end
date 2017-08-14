from rest_framework import serializers

from poken_rest.models import Shipping


class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = ('id', 'name', 'fee',)