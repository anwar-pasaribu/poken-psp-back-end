# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from poken_rest.utils.file_helper import *


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class HomeItem(models.Model):
    featured_items = models.ManyToManyField('FeaturedItem', help_text='item yang akan ditampilkan di home screen')
    sections = models.ManyToManyField('HomeProductSection', help_text='section barang')

    class Meta:
        ordering = ('-id', )


class HomeProductSection(models.Model):
    name = models.CharField(max_length=250, blank=True)
    section_action_value = models.CharField(max_length=250, blank=True)
    section_action_id = models.PositiveSmallIntegerField(default=0)
    products = models.ManyToManyField('Product', max_length=5, help_text='lima produk per section')


class FeaturedItem(models.Model):
    name = models.CharField(max_length=250, blank=True)
    image = models.ImageField(upload_to=generated_featured_image_file_name, blank=False)
    expiry_date = models.DateTimeField(auto_now_add=False)
    target_id = models.PositiveSmallIntegerField(default=0)

    def __unicode__(self):
        return '{0}, {1}'.format(
            self.name,
            self.pk
        )


class UserLocation(models.Model):
    address = models.TextField(blank=True)
    district = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip = models.CharField(max_length=10)
    state = models.CharField(max_length=50)

    def district_city(self):
        return '{0}, {1}'.format(
            self.district,
            self.city
        )

    def formatted_address(self):
        return '{0}, {1}, {2} {3}'.format(self.address, self.district, self.city, self.zip)

    def __unicode__(self):
        return '{0}, {1}'.format(
            self.address,
            self.district
        )


# Create your models here.
class Seller(models.Model):
    related_user = models.ForeignKey(User, default=None, related_name='seller', on_delete=models.CASCADE)

    password = models.CharField(max_length=128, help_text="password")
    name = models.CharField(max_length=200, help_text='nama penjual')
    username = models.CharField(max_length=50, help_text='user name yang singkat')
    email = models.EmailField(help_text='email address')
    bio = models.TextField(blank=True)
    tag_line = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15)
    location = models.ForeignKey(UserLocation)


class Customer(models.Model):
    related_user = models.ForeignKey(User, default=None, related_name='customer', on_delete=models.CASCADE)

    phone_number = models.CharField(max_length=15)
    location = models.ForeignKey(UserLocation, related_name='location', on_delete=models.CASCADE)

    def __unicode__(self):
        return '%s (%s)' % (self.related_user.first_name, self.related_user.email)


class ProductBrand(models.Model):
    name = models.CharField(max_length=200, help_text="merek barang")
    logo = models.ImageField(upload_to=generated_logo_file_name, blank=True)

    def __unicode__(self):
        return 'Brand name: {0}'.format(self.name)


class ProductSize(models.Model):
    name = models.CharField(max_length=200, help_text="merek barang")

    def __unicode__(self):
        return 'Size: {0}'.format(self.name)


class ProductCategory(models.Model):
    name = models.CharField(max_length=200, help_text="kategori barang")
    sizes = models.ManyToManyField(ProductSize, help_text='ukuran yang tersedia')

    def __unicode__(self):
        return 'Category: {0}'.format(self.name)


class ProductImage(models.Model):
    path = models.ImageField(upload_to=generated_product_image_file_name, blank=True)


class Courier(models.Model):
    name = models.CharField(max_length=100, help_text="nama vendor")
    code = models.CharField(max_length=10, help_text="kode identifikasi vendor")

    def __unicode__(self):
        return 'Courier: {0} ({1})'.format(self.name, self.code)


class Location(models.Model):
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zip = models.CharField(max_length=6)
    state = models.CharField(max_length=50)

    def __unicode__(self):
        return '{0}, {1}'.format(
            self.city,
            self.district
        )


class AddressBook(models.Model):
    customer = models.ForeignKey(Customer)
    location = models.ForeignKey(Location)
    name = models.CharField(max_length=100, help_text="nama address book")
    address = models.CharField(max_length=250, help_text="alamat spesifik dari user")
    phone = models.CharField(max_length=15, blank=True)


class Shipping(models.Model):
    name = models.CharField(max_length=50)
    fee = models.PositiveIntegerField()


class OrderDetails(models.Model):
    # non unique id order id
    order_id = models.CharField(max_length=10, help_text="order id")
    customer = models.ForeignKey(Customer)
    address = models.ForeignKey(AddressBook)
    date = models.DateTimeField(auto_now_add=True)
    shipping = models.ForeignKey(Shipping)


class Subscribed(models.Model):
    seller = models.ForeignKey(Seller)
    customer = models.ForeignKey(Customer)


class Product(models.Model):
    name = models.CharField(max_length=200, help_text="isi nama barang")
    description = models.TextField(blank=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    is_posted = models.BooleanField(default=True)
    is_new = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    brand = models.ForeignKey(ProductBrand)
    category = models.ForeignKey(ProductCategory)
    images = models.ManyToManyField(ProductImage)
    size = models.ForeignKey(ProductSize)
    stock = models.PositiveSmallIntegerField(blank=False)  # MAX 32767 items
    price = models.PositiveIntegerField(blank=False)
    weight = models.PositiveIntegerField(blank=False)  # MAX 2147483647 gram

    class Meta(object):
        ordering = ('-name', )

    def __unicode__(self):
        return '{0}, {1}'.format(
            self.name,
            self.pk
        )


class ShoppingCart(models.Model):
    customer = models.ForeignKey(Customer)
    product = models.ForeignKey(Product)
    date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta(object):
        ordering = ('-date', )


class OrderedProduct(models.Model):
    order_details = models.ForeignKey(OrderDetails)
    shopping_cart = models.ForeignKey(ShoppingCart)
    status = models.SmallIntegerField(default=0)


class CollectedProduct(models.Model):
    product = models.ForeignKey(Product)
    customer = models.ForeignKey(Customer)
    status = models.SmallIntegerField(default=0)  # 0: last seen, 1: favorite
