from rest_framework import serializers

from poken_rest.models import UserBank


class UserBankSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source='bank.name', read_only=True)
    bank_code_number = serializers.CharField(source='bank.code_number', read_only=True)
    bank_logo = serializers.SerializerMethodField()

    class Meta:
        model = UserBank
        fields = ('id', 'account_number', 'account_name', 'bank_name', 'bank_code_number', 'bank_logo')

    def get_bank_logo(self, obj):
        if obj and obj.bank:
            request = self.context.get('request')  # View set should pass 'request' object
            if obj.bank.logo is None:
                return ""
            image_url = obj.bank.logo.url
            if request:
                return request.build_absolute_uri(image_url)
            else:
                return ""
        else:
            return ""
