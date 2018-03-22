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

    class Meta:
        model = Product
        fields = ('id', 'name', 'images', 'price', 'stock')
