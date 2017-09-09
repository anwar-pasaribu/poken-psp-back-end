from django.contrib.auth import get_user_model  # If used custom user model
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from poken_rest.models import Customer

UserModel = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):

    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password', 'token')
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'read_only': True}
        }

    def get_token(self, obj):
        if obj.username:
            user = User.objects.filter(username=obj.username)
            if user:
                token = Token.objects.filter(user=user).first()
                if token:
                    return token.key
        else:
            return ""

    def create(self, validated_data):
        user = super(UserRegisterSerializer, self).create(validated_data)
        user.username = validated_data['email']
        user.set_password(validated_data['password'])
        user.save()

        # Save Customer data
        cust = Customer.objects.update_or_create(related_user=user)

        return user
