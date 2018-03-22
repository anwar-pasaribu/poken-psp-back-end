from rest_framework import serializers

from poken_rest.models import OrderedProduct


class StoreCreditsSerializer(serializers.ModelSerializer):

    order_details = serializers.StringRelatedField(source='order_details.order_id', read_only=True)
    order_date = serializers.DateTimeField(source='order_details.date', read_only=True)
    order_total_credits = serializers.SerializerMethodField()
    order_total_ordered_item = serializers.SerializerMethodField()

    class Meta:
        model = OrderedProduct
        fields = ('id', 'order_details', 'order_date', 'order_total_credits', 'order_total_ordered_item')

    def get_order_total_credits(self, obj):
        total_credits_per_order = 0
        if obj:
            for sc in obj.shopping_carts.all():
                print ("Sc: %s" % sc.shopping_cart_item_fee)
                total_credits_per_order += sc.shopping_cart_item_fee

        print("Total order fee: %d" % total_credits_per_order)

        return total_credits_per_order

    def get_order_total_ordered_item(self, obj):
        total_item_count = len(obj.shopping_carts.all())

        print("Total order fee: %d" % total_item_count)

        return total_item_count
