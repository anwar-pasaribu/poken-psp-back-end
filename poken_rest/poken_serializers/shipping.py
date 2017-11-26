import os

import osa
import zeep
from django.forms.models import model_to_dict

from rest_framework import serializers

from poken_psp import settings, properties
from poken_rest.models import Shipping, Product, AddressBook


class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = ('id', 'name', 'fee',)


class ShippingRatesSerializer(serializers.ModelSerializer):

    product_id = serializers.IntegerField(read_only=True)
    address_book_id = serializers.IntegerField(read_only=True)
    courier_rates = serializers.SerializerMethodField()

    class Meta:
        model = Shipping
        fields = ('id', 'name', 'fee', 'product_id', 'address_book_id', 'courier_rates')
        extra_kwargs = {
            'product_id': {'write_only': True},
            'address_book_id': {'write_only': True}
        }

    def get_courier_rates(self, obj):
        courier_name = str(obj.name)

        # List to hold all rates
        tariff_list = []

        if courier_name.lower().__contains__('pos indonesia'):
            print ("Tariff for POS Indonesia")

            request = self.context.get('request')
            data = request.query_params
            product_id = data.get('product_id', None)
            product_quantity = data.get('product_quantity', 1)
            address_book_id = data.get('address_book_id', None)

            if product_id and address_book_id:
                product = Product.objects.filter(pk=int(product_id)).first()
                address_book = AddressBook.objects.filter(pk=int(address_book_id)).first()

                if product and address_book:
                    wsdl_path = os.path.join(settings.STATIC_ROOT, "poken_rest/PosWebServices-20161201.wsdl.xml")

                    product_seller = product.seller
                    product_weight = product.weight * int(product_quantity)
                    seller_zip_code = product_seller.location.zip
                    cust_zip_code = address_book.location.zip

                    print("Product weight: %d " % product_weight)

                    client = zeep.Client(wsdl=wsdl_path)

                    # Print all WSDL Data
                    # client.wsdl.dump()

                    tariff_data = client.service.getFee(
                        properties.DEV_USER_ID, properties.DEV_USER_PWD,
                        '0', '1',
                        seller_zip_code, cust_zip_code, product_weight,
                        '0', '0', '0', '0', '0')

                    print("Tariff data: %s" % str(tariff_data))
                    for tariff_item in tariff_data:
                        # Create shipping item then convert to dict
                        item = Shipping(fee=int(eval(tariff_item['totalFee'])), name=tariff_item['serviceName'])
                        tariff_list.append(model_to_dict(item, fields=[field.name for field in item._meta.fields]))

                    return tariff_list

        return tariff_list
