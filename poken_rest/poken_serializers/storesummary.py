from rest_framework import serializers

from poken_rest.models import Product, Seller, SellerPromo


class StoreSummarySerializer(serializers.ModelSerializer):
    seller_detail = serializers.SerializerMethodField()
    latest_products = serializers.SerializerMethodField()
    total_credits = serializers.SerializerMethodField()
    promotions = serializers.SerializerMethodField()

    class Meta:
        model = Seller
        fields = ('id', 'seller_detail', 'latest_products', 'total_credits', 'promotions')

    def get_seller_detail(self, obj):
        request = self.context.get('request')  # View set should pass 'request' object
        return {
            'id': obj.id,
            'store_name': obj.store_name,
            'store_avatar': u'%s' % request.build_absolute_uri(obj.user_image.profile_pic.url),
        }

    def get_promotions(self, obj):
        request = self.context.get('request')  # View set should pass 'request' object

        promos = SellerPromo.objects.filter(seller=obj).order_by('-id')

        data = []

        if len(promos) == 0:
            promos = SellerPromo.objects.all()

        for promo in promos:
            if promo:
                promo_data = {
                    'id': promo.id,
                    'thumbnail': u'%s' % request.build_absolute_uri(promo.thumbnail.url)
                }

                data.append(promo_data)

        return data

    def get_total_credits(self, obj):
        data = 345000

        return data

    def get_latest_products(self, obj):
        request = self.context.get('request')  # View set should pass 'request' object

        related_products = []
        featured_product = Product.objects.filter(seller=obj).order_by('-id')[:9]

        print ("Category: %s " % str(obj))

        if len(featured_product) < 3:
            featured_product = Product.objects.all()[:3]

        for product in featured_product:
            if product is not None:
                # Create compat product data
                product_data = {
                    'id': product.id,
                    'images': [
                        {
                            'thumbnail': u'%s' % request.build_absolute_uri(product.images.first().thumbnail.url)
                        }
                    ]}
                related_products.append(product_data)

        return related_products
