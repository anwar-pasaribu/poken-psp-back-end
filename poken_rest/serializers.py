from django.contrib.auth.models import User, Group
from rest_framework import serializers

from poken_rest.admin import Seller
from poken_rest.models import Product, UserLocation, Customer, Seller, ProductBrand, Location, ProductCategory, \
    ProductImage, ProductSize, FeaturedItem, HomeItem, HomeProductSection


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'first_name', 'last_name', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ('name',)


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBrand
        fields = ('name', 'logo')


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ('name',)


class ProductBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBrand
        fields = ('name', 'logo')


class ProductSellerSerializer(serializers.ModelSerializer):
    location = serializers.SlugRelatedField(many=False, read_only=True, slug_field='city')
    class Meta:
        model = Seller
        fields = ('id', 'name', 'tag_line', 'phone_number', 'location')


class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('path', )


class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ('name', )


class ProductSerializer(serializers.ModelSerializer):
    seller = ProductSellerSerializer(many=False, read_only=True)
    brand = ProductBrandSerializer(many=False, read_only=True)
    # Show certain field on related relationship
    # ref: http://www.django-rest-framework.org/api-guide/relations/#slugrelatedfield
    category = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    size = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    images = ProductImagesSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('name', 'description', 'seller', 'is_new', 'date_created', 'brand', 'category',
                  'images', 'size', 'stock', 'price', 'weight')


class InsertProductSerializer(serializers.ModelSerializer):
    seller = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=Seller.objects.all())
    brand = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=ProductBrand.objects.all())
    category = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=ProductCategory.objects.all())
    size = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=ProductSize.objects.all())
    images = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=ProductImage.objects.all())

    class Meta:
        model = Product
        fields = ('name', 'description', 'seller', 'is_new', 'date_created', 'brand', 'category',
                  'images', 'size', 'stock', 'price', 'weight')


class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = ('address', 'city', 'district', 'zip', 'state')


class CustomersSerializer(serializers.ModelSerializer):
    location = UserLocationSerializer(many=False, read_only=False)
    class Meta:
        model = Customer
        fields = ('id', 'name', 'email', 'phone_number', 'location')

    def create(self, validated_data):
        address_data = validated_data.pop('location')
        location_data = UserLocation.objects.create(**address_data)
        customer = Customer.objects.create(location=location_data, **validated_data)

        return customer


class SellerSerializer(serializers.ModelSerializer):
    location = UserLocationSerializer(many=False, read_only=True)
    class Meta:
        model = Seller
        fields = ('name', 'username', 'email', 'bio', 'tag_line', 'phone_number', 'location')

    def create(self, validated_data):
        address_data = validated_data.pop('location')
        location_data = UserLocation.objects.create(**address_data)
        customer = Customer.objects.create(location=location_data, **validated_data)

        return customer


class FeaturedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeaturedItem
        fields = ('name', 'image', 'expiry_date', 'target_id')


class HomeProductSectionSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = HomeProductSection
        fields = ('name', 'section_action_value', 'section_action_id', 'products')


class HomeContentSerializer(serializers.ModelSerializer):
    featured_items = FeaturedItemSerializer(many=True, read_only=True)
    sections = HomeProductSectionSerializer(many=True, read_only=True)

    class Meta:
        model = HomeItem
        fields = ('id', 'featured_items', 'sections',)


