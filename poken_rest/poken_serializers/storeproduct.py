from rest_framework import serializers

from poken_rest.models import Product, ProductImage, ProductCategory


class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'thumbnail',)
        read_only_fields = ('thumbnail',)


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ('id', 'name',)


class StoreProductSerializer(serializers.ModelSerializer):
    images = ProductImagesSerializer(many=True, read_only=True)
    # category = ProductCategorySerializer(many=False, read_only=True)
    original_price = serializers.SerializerMethodField()
    is_ordered = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'images', 'price', 'original_price', 'stock', 'is_ordered')

    def get_original_price(self, obj):
        if obj.original_price == 0:
            return obj.price
        else: return obj.original_price

    def get_is_ordered(self, obj):
        print("Product: %s" % obj)
        if obj.shoppingcart_set.first() is None:
            return False
        return True
