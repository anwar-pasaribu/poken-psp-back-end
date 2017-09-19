from rest_framework import serializers

from poken_rest.models import ProductCategory, Product


class ProductCategoryFeaturedSerializer(serializers.ModelSerializer):

    product_category = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = ('id', 'product_category', 'products' )

    def get_product_category(self, obj):
        data = {}
        data['id'] = obj.id
        data['name'] = str(obj.name)

        return data

    def get_products(self, obj):
        request = self.context.get('request')  # View set should pass 'request' object

        related_products = []
        featured_product = Product.objects.filter(category=obj)

        print ("Category: %s " % str(obj) )

        if len(featured_product) < 3:
            featured_product = Product.objects.all()[:3]

        for product in featured_product:
            if product is not None:
                # Create compat product data
                product_data = {}
                product_data['images'] = [
                    {
                        'thumbnail' : u'%s' % request.build_absolute_uri(product.images.first().thumbnail.url)
                    }
                ]
                related_products.append(product_data)

        return related_products


class ProductCategorySerializer(serializers.ModelSerializer):
    '''
    General serializer for Product Category
    '''
    class Meta:
        model = ProductCategory
        fields = ('id', 'name',)