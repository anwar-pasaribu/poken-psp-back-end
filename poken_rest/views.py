# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions

from poken_rest.models import Product, UserLocation, Customer, Seller, ProductBrand, HomeItem, ShoppingCart, \
    AddressBook, OrderedProduct
from poken_rest.serializers import UserSerializer, GroupSerializer, ProductSerializer, UserLocationSerializer, \
    CustomersSerializer, SellerSerializer, ProductBrandSerializer, InsertProductSerializer, HomeContentSerializer, \
    ShoppingCartSerializer, InsertShoppingCartSerializer, AddressBookSerializer, OrderedProductSerializer


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
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class InsertProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = InsertProductSerializer

class InsertShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = InsertShoppingCartSerializer


class UserLocationViewSet(viewsets.ModelViewSet):
    queryset = UserLocation.objects.all()
    serializer_class = UserLocationSerializer


class AddressBookSerializerViewSet(viewsets.ModelViewSet):
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

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        print "Logged user: %s" % user.username
        customerSet = Customer.objects.filter(related_user=user)

        print "Customer: %s" % customerSet

        if customerSet.first() is not None:
            print "Logged customer: %s" % customerSet.first().related_user.email
            return ShoppingCart.objects.filter(customer=customerSet)
        else:
            print "Customer found"

        return []


class OrderedProductViewSet(viewsets.ModelViewSet):
    queryset = OrderedProduct.objects.all()
    serializer_class = OrderedProductSerializer
    permission_classes = (permissions.IsAuthenticated,)

