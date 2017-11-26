from rest_framework import serializers

from poken_rest.models import ProductImage, UserLocation, Product, Seller, ShoppingCart, Shipping


class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = ('id', 'name',)


class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = ('city',)


class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'thumbnail',)
        read_only_fields = ('thumbnail',)


class ProductSellerSerializer(serializers.ModelSerializer):
    # location = UserLocationSerializer(many=False, read_only=True)

    store_avatar = serializers.SerializerMethodField()  # Get get_seller_avatars method

    class Meta:
        model = Seller
        fields = ('id', 'store_avatar', 'store_name', )

    def get_store_avatar(self, obj):
        if obj and obj.user_image:
            request = self.context.get('request')  # View set should pass 'request' object
            if obj.user_image.profile_pic is None:
                return ""
            image_url = obj.user_image.profile_pic.url
            if request:
                return request.build_absolute_uri(image_url)
            else:
                return ""
        else:
            return ""


class ProductCartSerializer(serializers.ModelSerializer):
    # Show certain field on related relationship
    # ref: http://www.django-rest-framework.org/api-guide/relations/#slugrelatedfield
    size = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')

    # TODO Limit to 1 image
    images = ProductImagesSerializer(many=True, read_only=True)
    seller = ProductSellerSerializer(many=False, read_only=True)

    class Meta:
        model = Product
        fields = ('name', 'images', 'size', 'stock', 'price', 'weight', 'seller', 'is_discount', 'discount_amount')

    def get_images(self, obj):
        print("Image len: %d" % len(obj.images))
        return obj.images[0]



class ShoppingCartSerializer(serializers.ModelSerializer):
    product = ProductCartSerializer(many=False)
    shipping = ShippingSerializer(many=False)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'product', 'date', 'quantity', 'shipping', 'shipping_fee', 'extra_note')
