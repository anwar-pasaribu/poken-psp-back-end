# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import print_function
from __future__ import unicode_literals

import datetime

import pytz
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.db.models.fields import related
from fcm_django.models import FCMDevice
from rest_framework.views import APIView
from rest_framework import viewsets, permissions, status
# GET USER DATA BY TOKEN
from rest_framework.authtoken.models import Token
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from poken_rest.domain import Order
from poken_rest.models import Product, UserLocation, Customer, Seller, ProductBrand, HomeItem, ShoppingCart, \
    AddressBook, OrderedProduct, CollectedProduct, Subscribed, OrderDetails, ProductImage, FeaturedItem, \
    ProductCategory, Shipping, UserBank
from poken_rest.poken_serializers.bank import UserBankSerializer
from poken_rest.poken_serializers.cart import ShoppingCartSerializer
from poken_rest.poken_serializers.category import ProductCategoryFeaturedSerializer, ProductCategorySerializer
from poken_rest.poken_serializers.fcm import PokenFCMSerializer
from poken_rest.poken_serializers.shipping import ShippingRatesSerializer
from poken_rest.poken_serializers.storecredits import StoreCreditsSerializer
from poken_rest.poken_serializers.storeproduct import StoreProductSerializer
from poken_rest.poken_serializers.storesummary import StoreSummarySerializer
from poken_rest.poken_serializers.user import UserRegisterSerializer as user_UserSerializer
from poken_rest.serializers import UserSerializer, GroupSerializer, ProductSerializer, UserLocationSerializer, \
    CustomersSerializer, SellerSerializer, ProductBrandSerializer, InsertProductSerializer, HomeContentSerializer, \
    InsertShoppingCartSerializer, AddressBookSerializer, OrderedProductSerializer, \
    CollectedProductSerializer, SubscribedSerializer, InsertOrderedProductSerializer, InsertOrderDetailsSerializer, \
    FeaturedItemDetailedSerializer, InsertCustomerSubscribedSerializer, InsertProductImageSerializer, \
    OrderDetailsSerializer
# Create your views here.
from poken_rest.services import integration_slack
from poken_rest.utils import constants, price_helper


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class FeaturedItemDetailViewSet(viewsets.ModelViewSet):
    serializer_class = FeaturedItemDetailedSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = FeaturedItem.objects.all()


class ProductCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = ProductCategorySerializer
    permission_classes = (permissions.AllowAny,)
    queryset = ProductCategory.objects.all()


class ShippingRatesViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingRatesSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_context(self):
        """
        pass request attribute to serializer
        """
        context = super(ShippingRatesViewSet, self).get_serializer_context()
        return context

    def get_queryset(self):
        data = self.request.query_params
        print('Data : ' + str(data))
        return Shipping.objects.all()


class ProductCategoryFeaturedViewSet(viewsets.ModelViewSet):
    serializer_class = ProductCategoryFeaturedSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = ProductCategory.objects.all()

    def get_serializer_context(self):
        """
        pass request attribute to serializer
        """
        context = super(ProductCategoryFeaturedViewSet, self).get_serializer_context()
        return context


class PokenFCMViewSet(viewsets.ModelViewSet):
    serializer_class = PokenFCMSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        """
        This view should return a list of all the address book
        for the currently authenticated user.
        """
        user = self.request.user
        print("User: ", user)
        if not user:
            return []
        else:
            fcm_device = FCMDevice.objects.filter(user=user)

            return fcm_device

    def get_serializer_context(self):
        """
        pass request attribute to serializer
        """
        context = super(PokenFCMViewSet, self).get_serializer_context()
        return context


class StoreSummaryViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSummarySerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        user = self.request.user
        seller = Seller.objects.filter(related_user=user)[:1]
        print("Seller %s" % seller)
        return seller

    def get_serializer_context(self):
        """
        pass request attribute to serializer
        """
        context = super(StoreSummaryViewSet, self).get_serializer_context()
        return context


class StoreProductViewSet(viewsets.ModelViewSet):
    serializer_class = StoreProductSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        user = self.request.user
        seller = Seller.objects.filter(related_user=user)
        if len(seller) > 0:
            seller_products = Product.objects.filter(seller=seller.first()).order_by('-id')
            return seller_products

        return []

    def get_serializer_context(self):
        """
        pass request attribute to serializer
        """
        context = super(StoreProductViewSet, self).get_serializer_context()
        return context


class StoreCreditsViewSet(viewsets.ModelViewSet):
    serializer_class = StoreCreditsSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        user = self.request.user
        seller = Seller.objects.get(related_user=user)
        if seller:
            seller_credits = OrderedProduct.objects.filter(shopping_carts__product__seller=seller)
            print("Seller credits %s, len: %s" % (seller_credits, len(seller_credits)))
            return seller_credits

        return []

    def get_serializer_context(self):
        """
        pass request attribute to serializer
        """
        context = super(StoreCreditsViewSet, self).get_serializer_context()
        return context


class HomeContentViewSet(viewsets.ModelViewSet):
    """
    Get Home Content:
    Updated on: 
        - July 31st : Various changes related to Order
    """
    serializer_class = HomeContentSerializer

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return [HomeItem.objects.latest('id'), ]


class ProductBrandViewSet(viewsets.ModelViewSet):
    queryset = ProductBrand.objects.all()
    serializer_class = ProductBrandSerializer

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ProductViewSet(viewsets.ModelViewSet):
    # queryset = Product.objects.all()
    serializer_class = ProductSerializer

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    # [Aug 6th] Filter
    # filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    # filter_class = ProductFilter

    def get_serializer_context(self):
        """
        pass request attribute to serializer
        """
        context = super(ProductViewSet, self).get_serializer_context()
        return context

    def get_queryset(self):
        data = self.request.query_params
        seller_id = data.get('seller_id', None)
        action_id = data.get('action_id', None)

        # URL PARAMS
        product_name = data.get('name', None)

        # BROWSE PRODUCT BY CATEGORY
        category_id = data.get('category_id', None)
        category_name = data.get('category_name', None)

        # BROWSE PRODCUTS BY SELLER
        if seller_id is not None:
            return Product.objects.filter(seller__id=seller_id, is_posted=True)
        elif action_id is not None:
            if int(action_id) == constants.ACTION_SALE_PRODUCT:
                return Product.objects.filter(is_discount=True, is_posted=True)
        elif category_id is not None and category_name is not None:

            if category_name == constants.CATEGORY_ALL:
                return Product.objects.all()

            return Product.objects.filter(
                category__name__contains=category_name
            )
        elif product_name and category_name is not None:
            print("Search category name: \"%s\" and product name: \"%s\"" % (category_name, product_name))
            # First attempt search by product name OR category name
            product_search_result = Product.objects.filter(
                Q(name__icontains=str(product_name)) | Q(category__name__icontains=str(category_name))
                | Q(seller__store_name__icontains=str(product_name))
            )

            print("Search result size: %d" % len(product_search_result))

            return product_search_result

        return Product.objects.filter(is_posted=True)


class InsertProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = InsertProductSerializer
    permission_classes = (permissions.IsAuthenticated,)


class InsertUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = user_UserSerializer
    permission_classes = ()


class InsertProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = InsertProductImageSerializer
    permission_classes = (permissions.IsAuthenticated,)


class InsertShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = InsertShoppingCartSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_context(self):
        """
        pass request attribute to serializer
        """
        context = super(InsertShoppingCartViewSet, self).get_serializer_context()
        return context


class InsertOrderDetailsViewSet(viewsets.ModelViewSet):
    """
    Insert order detail (require to continue orider)
    """
    queryset = OrderDetails.objects.all()
    serializer_class = InsertOrderDetailsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_context(self):
        """
        pass request attribute to serializer
        """
        context = super(InsertOrderDetailsViewSet, self).get_serializer_context()
        return context


class InsertAddressBookViewSet(viewsets.ModelViewSet):
    """
    Insert Address Book
    """
    queryset = AddressBook.objects.all()
    serializer_class = InsertOrderDetailsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_context(self):
        context = super(InsertAddressBookViewSet, self).get_serializer_context()
        return context


class InsertOrderedProductViewSet(viewsets.ModelViewSet):
    queryset = OrderedProduct.objects.all()
    serializer_class = InsertOrderedProductSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_context(self):
        """
        pass request attribute to serializer
        """
        context = super(InsertOrderedProductViewSet, self).get_serializer_context()
        return context


class InsertCustomerSubscribedViewSet(viewsets.ModelViewSet):
    queryset = Subscribed.objects.all()
    serializer_class = InsertCustomerSubscribedSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_context(self):
        """
        pass request attribute to serializer
        """
        context = super(InsertCustomerSubscribedViewSet, self).get_serializer_context()
        return context


class UserLocationViewSet(viewsets.ModelViewSet):
    queryset = UserLocation.objects.all()
    serializer_class = UserLocationSerializer


class AddressBookSerializerViewSet(viewsets.ModelViewSet):
    """
    Available request GET to get address book list or POST to add
    more Address Book.
    """
    queryset = AddressBook.objects.all()
    serializer_class = AddressBookSerializer

    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """
        This view should return a list of all the address book
        for the currently authenticated user.
        """
        user = self.request.user
        cust = Customer.objects.filter(related_user=user).first()
        address_book_set = AddressBook.objects.filter(customer=cust)

        return address_book_set

    def get_serializer_context(self):
        """
        pass request attribute to serializer
        """
        context = super(AddressBookSerializerViewSet, self).get_serializer_context()
        return context


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomersSerializer

    # Special permission to allow anyone to register as
    # a customer
    permission_classes = (permissions.AllowAny,)

    # Get single data
    def get_object(self):
        # Get pk from URL (customer/{pk}/)
        # {pk} could be a user Token on Customer id
        pk_data = self.kwargs.get('pk')

        try:
            int_pk = int(pk_data)
            cust = Customer.objects.filter(id=int_pk)
            return get_object_or_404(queryset=cust)

        except ValueError as value_error_ex:

            user_token = Token.objects.filter(key__exact=pk_data).first()
            if user_token is not None:
                selected_cust = Customer.objects.filter(
                    related_user=user_token.user
                )

                return get_object_or_404(queryset=selected_cust)

    def get_queryset(self):
        query_data = self.request.query_params
        token_data = query_data.get('token_key')
        user_token = Token.objects.filter(key__exact=token_data).first()

        if user_token is not None:
            selected_cust = Customer.objects.filter(
                related_user=user_token.user
            )

            return selected_cust

        return Customer.objects.none()


class UserBankViewSet(viewsets.ModelViewSet):
    serializer_class = UserBankSerializer
    queryset = UserBank.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_context(self):
        """
        pass request attribute to serializer
        """
        context = super(UserBankViewSet, self).get_serializer_context()
        return context


class SellerViewSet(viewsets.ModelViewSet):
    serializer_class = SellerSerializer

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        data = self.request.query_params
        # URL PARAMS
        store_name = data.get('store_name', None)

        if store_name:
            print("Search by store name: " + store_name)
            return Seller.objects.filter(
                Q(store_name__icontains=str(store_name)))

        return Seller.objects.all()

    def get_serializer_context(self):
        """
        pass request attribute to serializer
        """
        context = super(SellerViewSet, self).get_serializer_context()
        return context


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        Exclude shopping cart which is avaibale on ordered product
        """
        user = self.request.user
        print("[Shopping cart] Logged user: %s" % user.username)
        active_cust = Customer.objects.filter(
            related_user=user,
        ).first()

        return ShoppingCart.objects.filter(
            product__stock__gte=1,
            customer=active_cust,
            orderedproduct=None)

    def partial_update(self, request, *args, **kwargs):
        shopping_cart = self.get_object()

        # Update shopping cart quantity
        quantity_data = request.data.get('quantity')
        if quantity_data:
            updated_selected_product_fee = \
                price_helper.get_discounted_product_fee(shopping_cart.product) * int(quantity_data)
            updated_shopping_cart_item_fee = updated_selected_product_fee + shopping_cart.shipping_fee

            shopping_cart.selected_product_fee = updated_selected_product_fee
            shopping_cart.shopping_cart_item_fee = updated_shopping_cart_item_fee

        serializer = ShoppingCartSerializer(shopping_cart,
                                            data=request.data,
                                            partial=True,
                                            context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def get_serializer_context(self):
        """
        pass request attribute to serializer
        """
        context = super(ShoppingCartViewSet, self).get_serializer_context()
        return context


class OrderDetailsViewSet(viewsets.ModelViewSet):
    serializer_class = OrderDetailsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """
        Ordered Product based on Logged in user.
        """
        user = self.request.user
        seller = Seller.objects.filter(related_user=user).first()

        if seller:
            print("Seller available. Seller: %s" % seller)
            return OrderDetails.objects.all()

        active_customer = Customer.objects.filter(related_user=user).first()

        return OrderDetails.objects.filter(customer=active_customer)

    def partial_update(self, request, *args, **kwargs):
        order_details = self.get_object()

        order_status_data = request.data.get('order_status')

        if order_status_data:
            order_status_int = int(order_status_data)

            print("Order status: %d" % order_status_int)

            if order_status_int == Order.BOOKED:
                print("User begin order product")
                order_details.order_status = Order.BOOKED
                # Slack - Send notification to Slack
                integration_slack.start_message_ordered_product(
                    order_details.orderedproduct_set.first(),
                    self.request
                )

            elif order_status_int == Order.RECEIVED:
                print("User tend to update to received")
                # Slack message to notify shipment received
                order_details.order_status = Order.RECEIVED
                integration_slack.start_message_order_status_changes(order_details, self.request)

            elif order_status_int == Order.REFUND:
                print("User try to refund order")
                order_details.order_status = Order.REFUND
                integration_slack.start_message_order_status_changes(order_details, self.request)

        serializer = OrderDetailsSerializer(order_details, data=request.data,
                                            partial=True)  # set partial=True to update a data partially
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class OrderedProductViewSet(viewsets.ModelViewSet):
    serializer_class = OrderedProductSerializer
    permission_classes = (permissions.IsAuthenticated,)

    # Get single data
    def get_object(self):

        user = self.request.user
        seller = Seller.objects.filter(related_user=user).first()

        # Get pk from URL (ordered_product/{pk}/)
        pk_data = self.kwargs.get('pk')

        if seller:
            print("Seller mode. Seller: %s" % seller)
            ordered_products = OrderedProduct.objects.filter(id=int(pk_data))
            return get_object_or_404(queryset=ordered_products)

        try:
            int_pk = int(pk_data)
            cust = OrderedProduct.objects.filter(id=int_pk)
            return get_object_or_404(queryset=cust)

        except ValueError as value_error_ex:
            print(value_error_ex)
            return get_object_or_404(queryset=[])

    def get_queryset(self):
        """
        Ordered Product based on Logged in user.
        """
        user = self.request.user
        active_customer = Customer.objects.filter(related_user=user).first()

        print ("Active cust %s" % active_customer)

        if active_customer is None:
            return []

        # CHECK EXPIRE ORDER
        # SET ORDER STATUS TO EXPIRE WHEN PAYMENT DUE IS OVER
        for order_detail in OrderDetails.objects.filter(customer=active_customer):
            now = datetime.datetime.now(pytz.utc)
            diff = order_detail.payment_expiration_date - now
            if diff.total_seconds() < 0 and (
                    order_detail.order_status == Order.BOOKED or order_detail.order_status == Order.INITIALIZE):
                print("Order %s %s" % (order_detail.order_id, Order.EXPIRE_TEXT))
                order_detail.order_status = Order.EXPIRE
                order_detail.save()

                # Send Slack Poken Order Expire Message
                integration_slack.start_message_order_status_changes(order_detail, self.request)

        return OrderedProduct.objects.filter(order_details__customer=active_customer)


class CollectedProductViewSet(viewsets.ModelViewSet):
    serializer_class = CollectedProductSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        active_customer = Customer.objects.filter(related_user=user).first()

        if active_customer is not None:
            return CollectedProduct.objects.filter(customer=active_customer, status=1)

        return Response(status=status.HTTP_204_NO_CONTENT, data=[])

    def get_serializer_context(self):
        """
        pass request attribute to serializer
        """
        context = super(CollectedProductViewSet, self).get_serializer_context()
        return context


class SubscribedViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribedSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        active_user = Customer.objects.filter(related_user=user).first()

        if active_user is not None:
            return Subscribed.objects.filter(customer=active_user, is_get_notif=True)

        return Response(status=status.HTTP_204_NO_CONTENT, data=[])
