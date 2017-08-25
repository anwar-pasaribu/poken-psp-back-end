# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone

from django.conf import settings as conf_settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from poken_rest.domain import Order
from poken_rest.utils.file_helper import *


PHONE_MAX_DIGIT = 15


@receiver(post_save, sender=conf_settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    print "Sender: %s, kwargs: %s" % (sender, kwargs)
    if created:
        Token.objects.create(user=instance)


class HomeItem(models.Model):
    featured_items = models.ManyToManyField('FeaturedItem', help_text='item yang akan ditampilkan di home screen')
    sections = models.ManyToManyField('HomeProductSection',
                                      help_text='section barang')

    class Meta:
        ordering = ('-id', )


class HomeProductSection(models.Model):
    name = models.CharField(max_length=250, blank=True)
    section_action_value = models.CharField(max_length=250, blank=True)
    section_action_id = models.PositiveSmallIntegerField(default=0)
    products = models.ManyToManyField('Product', blank=True, max_length=5, help_text='lima produk per section')
    top_sellers = models.ManyToManyField('poken_rest.Seller', blank=True, max_length=5, help_text='lima seller top')


class FeaturedItem(models.Model):
    name = models.CharField(max_length=250, blank=True)
    image = models.ImageField(upload_to=generated_featured_image_file_name, blank=False)
    # thumbnail
    thumbnail = models.ImageField("Gambar kecil mewakili gambar asli", blank=True)
    expiry_date = models.DateTimeField(auto_now_add=False)
    target_id = models.PositiveSmallIntegerField(default=0)

    featured_text = models.TextField("Teks promosi", default="Teks promosi")

    def __unicode__(self):
        return '{0}, {1}'.format(
            self.name,
            self.pk
        )

    class Meta:
        ordering = ('-id', )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        On save, generate a new thumbnail
        :param force_insert:
        :param force_update:
        :param using:
        :param update_fields:
        :return:
        """
        # generate and set thumbnail or none
        self.thumbnail = create_featured_image_thumbnail(self.image)

        # Check if a pk has been set, meaning that we are not creating a new image, but updateing an existing one
        # if self.pk:
        #    force_update = True

        # force update as we just changed something
        super(FeaturedItem, self).save(force_update=force_update)


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

    store_name = models.TextField(blank=False, default='', help_text='nama toko')

    bio = models.TextField(blank=True)
    tag_line = models.TextField(blank=True)
    phone_number = models.CharField(max_length=PHONE_MAX_DIGIT)
    location = models.ForeignKey(UserLocation, help_text='lokasi toko')

    user_image = models.ForeignKey('UserImage', blank=True, null=True)

    owner_name = models.CharField(max_length=150, blank=False, default='', help_text='nama pemilik toko')
    owner_phone = models.CharField(max_length=PHONE_MAX_DIGIT, blank=False, default='0',
                                   help_text='nomor telepon pemilik toko')
    owner_address = models.TextField(blank=False, default='', help_text='alamat pemilik toko')

    def __unicode__(self):
        return '%s (%s)' % (self.store_name, self.related_user.email)


class Customer(models.Model):
    related_user = models.ForeignKey(User, default=None, related_name='customer', on_delete=models.CASCADE)

    phone_number = models.CharField(max_length=PHONE_MAX_DIGIT)
    location = models.ForeignKey(UserLocation, related_name='location', on_delete=models.CASCADE)

    user_image = models.ForeignKey('UserImage', blank=True, null=True)

    class Meta(object):
        ordering = ('-id', )

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

    class Meta(object):
        ordering = ('name', )

class ProductCategoryFeatured(models.Model):
    product_category = models.ForeignKey('ProductCategory')
    products = models.ManyToManyField('Product', help_text='3 produk yg ditampilakan')

    # Featured item expiration
    featured_expiration_date = models.DateTimeField(
        "Tanggal berakhir promot",
        auto_now_add=False,
        null=True,
        default=timezone.now
    )

    def __unicode__(self):
        return 'Featured cat: {0}'.format(self.product_category.name)

    class Meta(object):
        ordering = ('-product_category__name', )

class UserImage(models.Model):
    profile_pic = models.ImageField(upload_to=generated_user_image_file_name, blank=True)


class ProductImage(models.Model):
    path = models.ImageField(upload_to=generated_product_image_file_name)

    # thumbnail
    thumbnail = models.ImageField("Gambar kecil mewakili gambar asli", blank=True)

    # title and description
    title = models.CharField("Judul gambar yg akan muncul", max_length=255, default="Unknown Picture")
    description = models.TextField("Deskripsi gambar", default="")

    class Meta(object):
        ordering = ('-id', )

    def __unicode__(self):
        return '%s' % self.title

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        On save, generate a new thumbnail
        :param force_insert:
        :param force_update:
        :param using:
        :param update_fields:
        :return:
        """
        # generate and set thumbnail or none
        self.thumbnail = create_thumbnail(self.path)

        # Check if a pk has been set, meaning that we are not creating a new image, but updateing an existing one
        # if self.pk:
        #    force_update = True

        # force update as we just changed something
        super(ProductImage, self).save(force_update=force_update)


class Courier(models.Model):
    name = models.CharField(max_length=100, help_text="nama vendor")
    code = models.CharField(max_length=10, help_text="kode identifikasi vendor")

    def __unicode__(self):
        return 'Courier: {0} ({1})'.format(self.name, self.code)


class Location(models.Model):
    district = models.CharField(max_length=100, help_text="kecamantan/kabupaten")
    city = models.CharField(max_length=100, help_text='nama kota')
    zip = models.CharField(max_length=6, help_text='kode pos')
    state = models.CharField(max_length=50, help_text='negara')

    def __unicode__(self):
        return '{0}, {1}'.format(
            self.city,
            self.district
        )


class AddressBook(models.Model):
    customer = models.ForeignKey(Customer)
    location = models.ForeignKey(Location, null=True, blank=True)
    name = models.CharField(max_length=100, help_text="nama address book")
    # TODO Person In Charge name for next release
    address = models.CharField(max_length=250, help_text="alamat spesifik dari user")
    phone = models.CharField(max_length=15, blank=True)

    class Meta(object):
        ordering = ('-id', )

    def __unicode__(self):
        return "%s - %s" % (self.address, self.phone)


class Shipping(models.Model):
    name = models.CharField(max_length=50)
    fee = models.PositiveIntegerField()

    def __unicode__(self):
        return "%s - %s" % (self.name, self.fee)


class OrderDetails(models.Model):
    # non unique id order id
    order_id = models.CharField(max_length=10, help_text="order id")
    customer = models.ForeignKey(Customer)
    address_book = models.ForeignKey(AddressBook, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    # Payment expiration
    payment_expiration_date = models.DateTimeField(
        auto_now_add=False,
        null=True,
        default=timezone.now
    )

    # Transaction/Order expiration
    order_expiration_date = models.DateTimeField(
        auto_now_add=False,
        null=True,
        default=timezone.now
    )

    # Moved from Ordered Product
    order_status = models.SmallIntegerField(default=Order.BOOKED)

    def __unicode__(self):
        return '{%s}' % self.order_id


class Subscribed(models.Model):
    seller = models.ForeignKey(Seller)
    customer = models.ForeignKey(Customer)
    is_get_notif = models.BooleanField(default=False)

    class Meta(object):
        ordering = ('-id', )


class Product(models.Model):
    name = models.CharField(max_length=200, help_text="isi nama barang")
    description = models.TextField(blank=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    is_posted = models.BooleanField(default=True)
    is_discount = models.BooleanField(default=False)
    discount_amount = models.PositiveIntegerField(blank=False, default=0)
    is_cod = models.BooleanField(default=False)
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

    shipping = models.ForeignKey('Shipping', blank=True, null=True)
    shipping_fee = models.PositiveIntegerField(default=0, blank=True)

    extra_note = models.TextField(blank=True)

    class Meta(object):
        ordering = ('-date', )

    def __unicode__(self):
        return '%s - Cust: %s, product: %s (%s items), added: %s' % (self.id, self.customer.id, self.product.id, self.quantity, self.date)


class OrderedProduct(models.Model):
    order_details = models.ForeignKey(OrderDetails, on_delete=models.CASCADE)
    shopping_carts = models.ManyToManyField(ShoppingCart)
    status = models.SmallIntegerField(default=0)

    class Meta(object):
        ordering = ('-id', )

    def __unicode__(self):
        return 'order id: %s, cart: %s' % (self.order_details.order_id, self.shopping_carts)


class CollectedProduct(models.Model):
    product = models.ForeignKey(Product)
    customer = models.ForeignKey(Customer)
    status = models.SmallIntegerField(default=0)  # 0: last seen, 1: favorite

    class Meta(object):
        ordering = ('-id', )  # Last id on top

    def __unicode__(self):
        return '%s - product: %s, status: %s' % (self.id, self.product, self.status)
