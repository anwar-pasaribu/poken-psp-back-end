# encoding=utf8
import random

from time import time
from django.utils import timezone
import datetime

from django.contrib.auth.models import User, Group
from django.http import request
from django.http.request import HttpRequest
from rest_framework import serializers

from poken_rest.domain import Order
from poken_rest.models import Product, UserLocation, Customer, Seller, ProductBrand, ProductCategory, \
    ProductImage, ProductSize, FeaturedItem, HomeItem, HomeProductSection, ShoppingCart, AddressBook, Location, \
    Shipping, OrderDetails, OrderedProduct, CollectedProduct, Subscribed

from django.contrib.auth import get_user_model  # If used custom user model

from poken_rest.utils import stringutils

UserModel = get_user_model()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


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
        fields = ('id', 'store_name', 'tag_line', 'phone_number', 'location')


class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('path',)


class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ('name',)


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
        fields = ('id', 'name', 'description', 'seller', 'discount_amount',
                  'is_discount', 'is_cod', 'is_new', 'date_created', 'brand', 'category',
                  'images', 'size', 'stock', 'price', 'weight')


class ProductCartSerializer(serializers.ModelSerializer):
    # Show certain field on related relationship
    # ref: http://www.django-rest-framework.org/api-guide/relations/#slugrelatedfield
    size = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    images = ProductImagesSerializer(many=True, read_only=True)
    seller = ProductSellerSerializer(many=False, read_only=True)

    class Meta:
        model = Product
        fields = ('name', 'images', 'size', 'stock', 'price', 'weight', 'seller')


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
    related_user = UserSerializer(many=False, read_only=False)
    location = UserLocationSerializer(many=False, read_only=False)

    class Meta:
        model = Customer
        fields = ('id', 'related_user', 'phone_number', 'location')

    def create(self, validated_data):
        user_data = validated_data.pop('related_user')  # Add Django User data
        address_data = validated_data.pop('location')
        user = get_user_model().objects.create_user(**user_data)

        print "User data %s: " % user_data
        print "Django User created %s: " % user
        print "Location data %s: " % address_data

        location_data = UserLocation.objects.create(**address_data)
        customer = Customer.objects.create(related_user=user, location=location_data, **validated_data)

        return customer


class SellerSerializer(serializers.ModelSerializer):
    location = UserLocationSerializer(many=False, read_only=True)
    related_user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Seller
        fields = ('store_name', 'related_user', 'bio', 'tag_line', 'phone_number', 'location')

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
    top_sellers = ProductSellerSerializer(many=True, read_only=True)

    class Meta:
        model = HomeProductSection
        fields = ('name', 'section_action_value', 'section_action_id', 'products', 'top_sellers')


class HomeContentSerializer(serializers.ModelSerializer):
    featured_items = FeaturedItemSerializer(many=True, read_only=True)
    sections = HomeProductSectionSerializer(many=True, read_only=True)

    class Meta:
        model = HomeItem
        fields = ('id', 'featured_items', 'sections',)


class InsertShoppingCartSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=False,
        queryset=Product.objects.all()
    )
    shipping_id = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=False,
        queryset=Shipping.objects.all()
    )

    class Meta:
        model = ShoppingCart
        fields = ('product_id', 'shipping_id', 'quantity')

    def create(self, validated_data):
        request = self.context.get('request')  # InsertShoppingCartViewSet should pass 'request' object
        shipping_data = validated_data.pop('shipping_id')
        product_data = validated_data.pop('product_id')
        quantity_data = validated_data.pop('quantity')

        cust = Customer.objects.filter(related_user=request.user).first()

        prev_cart_item = ShoppingCart.objects.filter(customer=cust, product=product_data).first()

        print "Current customer: %s" % cust
        print "Product data: %s" % product_data
        print "Shipping data: %s" % shipping_data
        print "Quantity data: %s" % quantity_data

        if prev_cart_item is not None:
            print "Prev. shopping cart available (quantity): %d" % prev_cart_item.quantity
            prev_cart_item.quantity = prev_cart_item.quantity + 1
            prev_cart_item.shipping = shipping_data
            prev_cart_item.save()

            return prev_cart_item

        new_cart = ShoppingCart.objects.create(
            customer=cust,
            product=product_data,
            shipping=shipping_data,
            quantity=quantity_data)

        return new_cart


class InsertOrderedProductSerializer(serializers.ModelSerializer):

    order_details_id = serializers.PrimaryKeyRelatedField(
        many = False,
        read_only = False,
        queryset = OrderDetails.objects.all())

    shopping_carts = serializers.SlugRelatedField(
        many=True,
        read_only = False,
        slug_field='id',
        queryset=ShoppingCart.objects.all())

    class Meta:
        model = OrderedProduct
        fields = ('id', 'order_details_id', 'shopping_carts', 'status')

    def create(self, validated_data):
        request = self.context.get('request')  # InsertShoppingCartViewSet should pass 'request' object
        order_details = validated_data.pop('order_details_id')
        shopping_carts = validated_data.pop('shopping_carts')

        cust = Customer.objects.filter(related_user=request.user).first()

        for sc in shopping_carts:
            print "Shopping cart item id: %s" % sc.id

        print "Validated data: %s" % validated_data.keys
        print "Current customer: %s" % cust
        print "order_details data: %s" % order_details
        print "shopping_carts data: %s" % shopping_carts

        # 1 - CREATE ORDER DETAILS
        generated_order_id = stringutils.mobile_order_id_generator()
        print "Generated order id: %s " % generated_order_id

        new_ordered_product = OrderedProduct.objects.create(
            order_details=order_details,
            status=Order.BOOKED)

        new_ordered_product.shopping_carts = shopping_carts
        new_ordered_product.save()

        return new_ordered_product


class AddressBookSerializer(serializers.ModelSerializer):

    class Meta:
        model = AddressBook
        fields = ('id', 'name', 'address', 'phone')

    def create(self, validated_data):
        request = self.context.get('request')

        cust = Customer.objects.filter(related_user=request.user).first()

        # name = validated_data.pop('name')
        # address = validated_data.pop('address')
        # phone = validated_data.pop('phone')

        print "Validated data: %s " % validated_data
        print "Cust from validated_data: %s " % cust

        created_address_book = AddressBook.objects.create(
            customer=cust,
            location=None,
            **validated_data)
        return created_address_book


class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = ('id', 'name', 'fee',)


class ShoppingCartSerializer(serializers.ModelSerializer):
    product = ProductCartSerializer(many=False)
    shipping = ShippingSerializer(many=False)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'product', 'date', 'quantity', 'shipping', 'shipping_fee')


class InsertOrderDetailsSerializer(serializers.ModelSerializer):

    address_book_id = serializers.PrimaryKeyRelatedField(
        many = False,
        read_only = False,
        queryset = AddressBook.objects.all())

    class Meta:
        model = OrderDetails
        fields = ('id', 'address_book_id', )

    def create(self, validated_data):
        request = self.context.get('request')  # InsertShoppingCartViewSet should pass 'request' object
        address_book_data = validated_data.pop('address_book_id')

        cust = Customer.objects.filter(related_user=request.user).first()

        print "Validated data: %s" % validated_data.keys
        print "Current customer: %s" % cust
        print "address_book_data: %s" % address_book_data

        # 1 - CREATE ORDER DETAILS
        generated_order_id = stringutils.mobile_order_id_generator()
        created_datetime = timezone.now()
        new_order_details = OrderDetails.objects.create(
            order_id=generated_order_id,
            customer=cust,
            address_book=address_book_data,
            date=created_datetime
        )

        return new_order_details


class OrderDetailsSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=False,
        queryset=Customer.objects.all()
    )
    address_book = AddressBookSerializer(many=False, read_only=False)

    class Meta:
        model = OrderDetails
        fields = ('id', 'order_id', 'customer', 'address_book', 'date',)


class OrderedProductSerializer(serializers.ModelSerializer):
    order_details = OrderDetailsSerializer(many=False, read_only=True)
    shopping_carts = ShoppingCartSerializer(many=True, read_only=True)

    class Meta:
        model = OrderedProduct
        fields = ('id', 'order_details', 'shopping_carts', 'status')


class CollectedProductSerializer(serializers.ModelSerializer):
    # parent_name = serializers.CharField(source='name', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.IntegerField(source='product.price', read_only=True)
    product_image = serializers.SerializerMethodField()  # Get get_product_images method

    class Meta:
        model = CollectedProduct
        fields = ('id', 'product_id', 'product_name', 'product_price', 'product_image', 'status')

    def get_product_image(self, obj):
        if obj.product:
            request = self.context.get('request')  # View set should pass 'request' object
            if obj.product.images.first() is None:
                return ""
            image_url = obj.product.images.first().path.url
            print "Images: %s" % image_url
            return request.build_absolute_uri(image_url)
        else:
            return ""


class SubscribedSerializer(serializers.ModelSerializer):
    # parent_name = serializers.CharField(source='name', read_only=True)
    seller_id = serializers.IntegerField(source='seller.id', read_only=True)
    seller_name = serializers.CharField(source='seller.store_name', read_only=True)
    seller_profile_pic = serializers.SerializerMethodField()
    seller_tag_line = serializers.CharField(source='seller.tag_line', read_only=True)
    seller_location = serializers.CharField(source='seller.location.city', read_only=True)

    class Meta:
        model = Subscribed
        fields = ('id', 'is_get_notif', 'seller_id', 'seller_name', 'seller_profile_pic', 'seller_tag_line', 'seller_location')

    def get_seller_profile_pic(self, obj):
        if obj.seller:
            request = self.context.get('request')  # View set should pass 'request' object
            if obj.seller.user_image is None:
                return None
            image_url = obj.seller.user_image.profile_pic.url
            print "Images: %s" % image_url
            return request.build_absolute_uri(image_url)
        else:
            return None

