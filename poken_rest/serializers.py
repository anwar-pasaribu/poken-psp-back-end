# encoding=utf8

from __future__ import print_function

from django.contrib.auth import get_user_model  # If used custom user model
from django.contrib.auth.models import User, Group
from django.utils import timezone
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status

from poken_rest.domain import Order
from poken_rest.models import Product, UserLocation, Customer, Seller, ProductBrand, ProductCategory, \
    ProductImage, ProductSize, FeaturedItem, HomeItem, HomeProductSection, ShoppingCart, AddressBook, Shipping, \
    OrderDetails, OrderedProduct, CollectedProduct, Subscribed, Location
from poken_rest.poken_serializers.shipping import ShippingSerializer
from poken_rest.services import integration_slack
from poken_rest.utils import stringutils
from django.utils.encoding import force_text
from django.core.serializers.json import DjangoJSONEncoder

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


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBrand
        fields = ('name', 'logo')


class ProductBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBrand
        fields = ('name', 'logo')


class ProductSellerSerializer(serializers.ModelSerializer):
    location = serializers.SlugRelatedField(many=False, read_only=True, slug_field='city')

    store_avatar = serializers.SerializerMethodField()  # Get get_seller_avatars method

    is_subscribed = serializers.SerializerMethodField()

    def get_store_avatar(self, obj):
        if obj.user_image:
            request = self.context.get('request')  # View set should pass 'request' object
            if obj.user_image.profile_pic is None:
                return ""
            image_url = obj.user_image.profile_pic.url
            return request.build_absolute_uri(image_url)
        else:
            return ""

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.id is not None:
            subscribed = obj.subscribed_set.filter(customer__related_user=user).first()
            if subscribed:
                return subscribed.is_get_notif
        else:
            return False

    class Meta:
        model = Seller
        fields = ('id', 'store_avatar', 'store_name', 'tag_line', 'phone_number', 'location', 'is_subscribed')


class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'path', 'thumbnail',)
        read_only_fields = ('thumbnail',)


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
        fields = ('name', 'images', 'size', 'stock', 'price', 'weight', 'seller', 'is_discount', 'discount_amount')


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Product):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)


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
    location = UserLocationSerializer(many=False, read_only=False, allow_null=True)

    # Change password
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    class Meta:
        model = Customer
        fields = ('id', 'related_user', 'phone_number', 'location', 'current_password', 'new_password')

    def create(self, validated_data):
        user_data = validated_data.pop('related_user')  # Add Django User data
        address_data = validated_data.pop('location')
        user = get_user_model().objects.create_user(**user_data)

        location_data = UserLocation.objects.create(**address_data)
        customer = Customer.objects.create(related_user=user, location=location_data, **validated_data)

        return customer

    def update(self, instance, validated_data):

        current_user = instance.related_user

        if validated_data.has_key('current_password'):
            if not current_user.check_password(validated_data.get('current_password')):
                details = { 'detail': 'Password lama salah.' }
                raise serializers.ValidationError(detail=details)
            else:
                # Update User password
                instance.related_user.set_password(validated_data.get('new_password'))

        # 'first_name', 'last_name',
        if validated_data.has_key('related_user'):
            related_user_data = dict(validated_data.pop('related_user'))
            instance.related_user.first_name = related_user_data['first_name']
            instance.related_user.last_name = related_user_data['last_name']
            instance.related_user.email = related_user_data['email']

        for key in validated_data.keys():
            setattr(instance, key, validated_data.get(key))

        # Save User and Customer data
        instance.related_user.save()
        instance.save()

        return instance



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


class FeaturedItemDetailedSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeaturedItem
        fields = ('id', 'name', 'image', 'expiry_date', 'target_id', 'featured_text')


class FeaturedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeaturedItem
        fields = ('id', 'name', 'image', 'thumbnail', 'expiry_date', 'target_id')


class HomeProductSectionSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    top_sellers = ProductSellerSerializer(many=True, read_only=True)

    class Meta:
        model = HomeProductSection
        fields = ('id', 'name', 'section_action_value', 'section_action_id', 'products', 'top_sellers')


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

    product = ProductSerializer(read_only=True)
    shipping = ShippingSerializer(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('product_id', 'shipping_id', 'shipping_fee', 'shipping_service', 'date', 'quantity', 'product',
                  'shipping')

    def create(self, validated_data):
        request = self.context.get('request')  # InsertShoppingCartViewSet should pass 'request' object
        shipping_data = validated_data.pop('shipping_id')
        product_data = validated_data.pop('product_id')
        quantity_data = validated_data.pop('quantity')
        shipping_fee_data = validated_data.pop('shipping_fee')
        shipping_service_data = validated_data.pop('shipping_service')

        cust = Customer.objects.filter(related_user=request.user).first()

        # Looking for Shopping Cart which is not available on OrderedProduct
        prev_cart_item = ShoppingCart.objects.filter(
            customer=cust,
            product=product_data,
            orderedproduct=None
        ).first()

        # Incement quantity
        if prev_cart_item is not None:
            if prev_cart_item.shipping == shipping_data:
                return prev_cart_item

        new_cart = ShoppingCart.objects.create(
            customer=cust,
            product=product_data,
            shipping=shipping_data,
            quantity=quantity_data,
            shipping_fee=shipping_fee_data,
            shipping_service=shipping_service_data
        )

        return new_cart


class InsertOrderedProductSerializer(serializers.ModelSerializer):
    order_details_id = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=False,
        queryset=OrderDetails.objects.all())

    shopping_carts = serializers.SlugRelatedField(
        many=True,
        read_only=False,
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
            print('Shopping cart item id: %s' % sc.id)

        print('Current customer: %s' % cust)
        print('order_details data: %s' % order_details)
        print('shopping_carts data: %s' % shopping_carts)

        # Substract product stock by one
        for shopping_item in shopping_carts:
            shopping_item.product.stock = shopping_item.product.stock - shopping_item.quantity
            shopping_item.product.save()

        new_ordered_product = OrderedProduct.objects.create(
            order_details=order_details,
            status=Order.BOOKED)

        new_ordered_product.shopping_carts = shopping_carts
        new_ordered_product.save()

        return new_ordered_product


class InsertCustomerSubscribedSerializer(serializers.ModelSerializer):
    seller_id = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=False,
        queryset=Seller.objects.all()
    )

    class Meta:
        model = Subscribed
        fields = ('seller_id', 'is_get_notif')

    def create(self, validated_data):
        request = self.context.get('request')  # InsertShoppingCartViewSet should pass 'request' object
        seller = validated_data.pop('seller_id')
        is_get_notif = validated_data.pop('is_get_notif')

        cust = Customer.objects.filter(related_user=request.user).first()

        prev_subscription = Subscribed.objects.filter(
            seller=seller,
            customer=cust
        ).first()

        if prev_subscription:
            prev_subscription.is_get_notif = is_get_notif
            prev_subscription.save()
            return prev_subscription
        else:
            new_cust_subscribed = Subscribed.objects.create(
                seller=seller,
                customer=cust,
                is_get_notif=is_get_notif
            )
            return new_cust_subscribed


class InsertProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'path', 'title', 'description')


class AddressBookLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('subdistrict', 'district', 'city', 'zip', )
        extra_kwargs = {
            'zip': {'read_only': True},
        }


class AddressBookSerializer(serializers.ModelSerializer):

    location = AddressBookLocationSerializer()

    class Meta:
        model = AddressBook
        fields = ('id', 'name', 'address', 'phone', 'location')

    def create(self, validated_data):
        request = self.context.get('request')

        # Dict convert OrderedDict to regular dict
        location_post_data = dict(validated_data.pop('location'))

        location_by_name = Location.objects.filter(
            city=location_post_data['city'],
            subdistrict=location_post_data['subdistrict'],
            district=location_post_data['district']
        ).first()

        cust = Customer.objects.filter(related_user=request.user).first()

        created_address_book = AddressBook.objects.create(
            customer=cust,
            location=location_by_name,
            **validated_data)

        return created_address_book

    def update(self, instance, validated_data):

        if validated_data.has_key('location'):
            # Dict convert OrderedDict to regular dict
            location_post_data = dict(validated_data.pop('location'))

            location_by_name = Location.objects.filter(
                city=location_post_data['city'],
                subdistrict=location_post_data['subdistrict'],
                district=location_post_data['district']
            ).first()

            if location_by_name:
                instance.location = location_by_name

        for key in validated_data.keys():
            setattr(instance, key, validated_data.get(key))

        instance.save()

        return instance


class ShoppingCartSerializer(serializers.ModelSerializer):
    product = ProductCartSerializer(many=False)
    shipping = ShippingSerializer(many=False)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'product', 'date', 'quantity', 'shipping', 'shipping_fee', 'extra_note')


class InsertOrderDetailsSerializer(serializers.ModelSerializer):
    address_book_id = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=False,
        queryset=AddressBook.objects.all())

    class Meta:
        model = OrderDetails
        fields = ('id', 'address_book_id', 'order_status')
        extra_kwargs = {
            'order_status': {'read_only': True}
        }

    def create(self, validated_data):
        request = self.context.get('request')  # InsertShoppingCartViewSet should pass 'request' object
        address_book_data = validated_data.pop('address_book_id')
        generated_order_id = stringutils.mobile_order_id_generator()
        created_datetime = timezone.now()
        # Expire in 24 Hours
        expire_payment_time = timezone.now() + timezone.timedelta(days=0, hours=24, minutes=0, seconds=0)
        # Expire in 7 days
        expire_order_time = timezone.now() + timezone.timedelta(days=7, hours=0, minutes=0, seconds=0)

        # PROCEED OTHER POST DATA
        post_data = self.context.get('request').POST
        order_details_id_data = post_data.get('order_details_id')

        # UPDATE ORDER ID
        if order_details_id_data is not None:
            order_details_id = int(order_details_id_data)
            previous_order_details = OrderDetails.objects.filter(pk=order_details_id).first()

            if previous_order_details is not None:
                print("Previous order details: %s " % previous_order_details)
                previous_order_details.address_book = address_book_data
                previous_order_details.date = created_datetime
                previous_order_details.save()
                return previous_order_details
            else:
                print("NO PREVIOUS ORDER DETAIL. THEN CREATE ONE!!!")

        cust = Customer.objects.filter(related_user=request.user).first()

        print("Validated data: %s" % validated_data.keys)
        print("Current customer: %s" % cust)
        print("address_book_data: %s" % address_book_data)

        # CREATE ORDER DETAILS
        new_order_details = OrderDetails.objects.create(
            order_id=generated_order_id,
            customer=cust,
            address_book=address_book_data,
            date=created_datetime,
            payment_expiration_date=expire_payment_time,
            order_expiration_date=expire_order_time
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
        fields = ('id', 'order_id', 'customer', 'address_book', 'date', 'shipping_tracking_id',
                  'payment_expiration_date', 'order_expiration_date', 'order_status')


class OrderedProductSerializer(serializers.ModelSerializer):
    order_details = OrderDetailsSerializer(many=False, read_only=True)
    shopping_carts = ShoppingCartSerializer(many=True, read_only=True)

    total_shopping = serializers.SerializerMethodField()

    class Meta:
        model = OrderedProduct
        fields = ('id', 'order_details', 'shopping_carts', 'status', 'total_shopping')

    # Calculate all shooping costs
    def get_total_shopping(self, obj):
        if obj.shopping_carts:
            total_cost = 0
            for sc in obj.shopping_carts.all():
                if sc.product.is_discount:
                    sc.product.price = (sc.product.price - ((sc.product.price * sc.product.discount_amount) / 100))
                total_cost += sc.product.price * sc.quantity + sc.shipping.fee

            return total_cost


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
            image_url = obj.product.images.first().thumbnail.url
            print("Images: %s" % image_url)
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
        fields = (
            'id', 'is_get_notif', 'seller_id', 'seller_name', 'seller_profile_pic',
            'seller_tag_line', 'seller_location')

    def get_seller_profile_pic(self, obj):
        if obj.seller:
            request = self.context.get('request')  # View set should pass 'request' object
            if obj.seller.user_image is None:
                return None
            image_url = obj.seller.user_image.profile_pic.url
            print("Images: %s" % image_url)
            return request.build_absolute_uri(image_url)
        else:
            return None
