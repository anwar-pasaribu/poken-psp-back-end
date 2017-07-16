# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from poken_rest.models import Product, UserLocation, Customer, Seller, ProductBrand, HomeItem, ShoppingCart, \
    AddressBook, OrderedProduct, CollectedProduct, Subscribed, OrderDetails
from poken_rest.serializers import UserSerializer, GroupSerializer, ProductSerializer, UserLocationSerializer, \
    CustomersSerializer, SellerSerializer, ProductBrandSerializer, InsertProductSerializer, HomeContentSerializer, \
    ShoppingCartSerializer, InsertShoppingCartSerializer, AddressBookSerializer, OrderedProductSerializer, \
    CollectedProductSerializer, SubscribedSerializer, InsertOrderedProductSerializer, InsertOrderDetailsSerializer


# Create your views here.


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


class HomeContentViewSet(viewsets.ModelViewSet):
    serializer_class = HomeContentSerializer

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        latestItem = HomeItem.objects.latest('id')
        print "Max ID: %s" % latestItem.id
        print "Section name: %s" % latestItem.sections.all().count()

        data = self.request.query_params

        print "Data params: %s" % data

        return [HomeItem.objects.latest('id'), ]


class ProductBrandViewSet(viewsets.ModelViewSet):
    queryset = ProductBrand.objects.all()
    serializer_class = ProductBrandSerializer

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ProductViewSet(viewsets.ModelViewSet):
    # queryset = Product.objects.all()
    serializer_class = ProductSerializer

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        data = self.request.query_params
        seller_id = data.get('seller_id', None)
        action_id = data.get('action_id', None)

        # BROWSE PRODUCT BY CATEGORY
        category_id = data.get('category_id', None)
        category_name = data.get('category_name', None)

        if seller_id is not None:
            print "Seller ID: %s" % seller_id
            return Product.objects.filter(seller__id=seller_id, is_posted=True)
        elif action_id is not None:
            print "Action ID: %s" % action_id
            if int(action_id) == 3:
                return Product.objects.filter(is_discount=True, is_posted=True)
        elif category_id is not None and category_name is not None:
            print "Get product by category id: %s, name: %s" % (category_id, category_name)
            return Product.objects.filter(category_id=int(category_id), category__name__contains=category_name)

        print "Show all products."
        return Product.objects.filter(is_posted=True)


class InsertProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = InsertProductSerializer


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
        print "Logged user: %s" % user.username
        cust = Customer.objects.get(related_user=user)
        print "Cust : %s" % cust
        addressBookSet = AddressBook.objects.filter(customer=cust)

        print "Address book set: %s" % addressBookSet

        return addressBookSet

    def get_serializer_context(self):
        """
        pass request attribute to serializer
        """
        context = super(AddressBookSerializerViewSet, self).get_serializer_context()
        return context


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomersSerializer

    # Special permission to allow anyone to register as
    # a customer
    permission_classes = (permissions.AllowAny,)


class SellerViewSet(viewsets.ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


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
        print "Logged user: %s" % user.username
        active_cust = Customer.objects.filter(related_user=user).first()

        return ShoppingCart.objects.filter(customer=active_cust, orderedproduct=None)


class OrderedProductViewSet(viewsets.ModelViewSet):
    queryset = OrderedProduct.objects.all()
    serializer_class = OrderedProductSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CollectedProductViewSet(viewsets.ModelViewSet):
    serializer_class = CollectedProductSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        print "Logged user: %s" % user.username
        active_customer = Customer.objects.filter(related_user=user).first()

        if active_customer is not None:
            return CollectedProduct.objects.filter(customer=active_customer, status=1)
        else:
            print "User not login"

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
            return Subscribed.objects.filter(customer=active_user)

        return Response(status=status.HTTP_204_NO_CONTENT, data=[])
