from fcm_django.models import FCMDevice
from rest_framework import serializers


class PokenFCMSerializer(serializers.ModelSerializer):

    class Meta:
        model = FCMDevice
        fields = ('id', 'name', 'registration_id', 'device_id', 'active', 'type', )
