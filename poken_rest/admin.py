# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import pytz
from django.contrib import admin

from poken_psp import properties
from poken_rest.domain import Order
from poken_rest.models import Seller, Customer, ProductBrand, ProductSize, ProductCategory, ProductImage, Courier, \
    UserLocation, Location, AddressBook, Shipping, OrderDetails, Subscribed, Product, ShoppingCart, OrderedProduct, \
    CollectedProduct, FeaturedItem, HomeProductSection, HomeItem, UserImage, ProductCategoryFeatured, UserBank, Bank, \
    SellerPromo


class HomeItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'related_featured_items', 'related_sections')

    def related_featured_items(self, obj):
        if obj.featured_items:
            return ''.join('%s, ' % (featured_item.name) for featured_item in obj.featured_items.all()).rsplit(',', 1)[
                0]
        else:
            return "Tidak data featured item."

    def related_sections(self, obj):
        if obj.sections:
            return ''.join('%s, ' % (section.name) for section in obj.sections.all()).rsplit(',', 1)[0]
        else:
            return "Tidak data sections."


class HomeProductSectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'section_action_value', 'section_action_id', 'related_products')

    def related_products(self, obj):
        if obj.products:
            return ''.join('%s, ' % (product.name) for product in obj.products.all()).rsplit(',', 1)[0]
        else:
            return "Tidak data produk."


class FeaturedItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image', 'expiry_date', 'target_id',)

    def related_products(self, obj):
        if obj.related_products:
            return ''.join('%d, ' % product.id for product in obj.related_products.all()).rsplit(',', 1)[0]
        else:
            return 'Tidak ada data'


class ProductCategoryFeaturedAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_category', 'related_products')

    def related_products(self, obj):
        if obj.products:
            return ''.join('%d, ' % product.id for product in obj.products.all()).rsplit(',', 1)[0]
        else:
            return 'Tidak ada data'


class UserLocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'address', 'city', 'district', 'zip', 'state')


class SellerAdmin(admin.ModelAdmin):
    list_display = ('id', 'store_name', 'user_info', 'bio', 'tag_line', 'phone_number', 'address')

    search_fields = ('store_name', 'tag_line')

    def user_info(self, obj):
        if obj.related_user:
            return 'User: %s (%s)' % (obj.related_user.first_name, obj.related_user.email)
        else:
            return 'Data User bermasalah'

    def address(self, obj):
        if obj.location.zip and obj.location.city and len(obj.location.zip) >= 5:
            return '%s %s' % (obj.location.city, obj.location.zip)
        else:
            return 'ALAMAT TIDAK LENGKAP'


class SellerPromoItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'seller', 'name', 'image', 'thumbnail', 'expiry_date', 'target_id', 'featured_text')


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_info', 'phone_number', 'location')

    search_fields = ('related_user__email', )

    def user_info(self, obj):
        if obj.related_user:
            return 'User: %s (%s)' % (obj.related_user.first_name, obj.related_user.email)
        else:
            return 'Data User bermasalah'

    def thumbnail(self, obj):
        if obj.user_image:
            return '<img src="%s" style="height: 50px; width: auto">' % (obj.user_image.profile_pic.url)
        else:
            return "no image"


class UserImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile_pic', 'file_name',)

    def file_name(self, obj):
        if obj.profile_pic:
            return '%s (%s)' % (obj.profile_pic.name, obj.profile_pic.size)
        else:
            return 'Gambar bermasalah'


class BankAdmin(admin.ModelAdmin):
    list_display = ('name', 'code_number', 'logo')


class UserBankAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'account_name', 'bank')

    def bank(self, obj):
        if obj.bank:
            return '%s (%s)' % (obj.bank.name, obj.bank.code_number)
        else:
            return "Tidak ada bank."


class ProductBrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'logo')


class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'related_sizes',)

    def related_sizes(self, obj):
        if obj.sizes:
            return ''.join('%s, ' % (size.name) for size in obj.sizes.all()).rsplit(',', 1)[0]
        else:
            return "Tidak ada sizes."


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'path', 'file_name',)

    def file_name(self, obj):
        if obj.path:
            return '%s (%s)' % (obj.path.name, obj.path.size)
        else:
            return 'Gambar bermasalah'


class CourierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code',)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'district', 'zip',)


class AddressBookAdmin(admin.ModelAdmin):
    list_display = ('id', 'cust_name', 'name', 'location_address', 'address', 'phone',)

    def cust_name(self, obj):
        if obj.customer:
            return '%s' % obj.customer.related_user.username
        else:
            return 'Customer kosong'

    def location_address(self, obj):
        if obj.location:
            return '%s, %s %s' % (obj.location.district, obj.location.city, obj.location.zip)
        else:
            return 'Lokasi kosong'


class ShippingAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'fee',)


class OrderDetailsAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'order_id',
                    'cust_name',
                    'shipping_address',
                    'orders',
                    'date',
                    'shipping_tracking_id',
                    'payment_expiration',
                    'order_status_text')

    exclude = ('order_expiration_date',)

    search_fields = ('order_id', 'customer__related_user__first_name')

    def cust_name(self, obj):
        if obj.customer:
            return '%s' % obj.customer.related_user.get_full_name()
        else:
            return 'Customer kosong'

    cust_name.short_description = 'Akun Pemesan'

    def shipping_address(self, obj):
        if obj.address_book:
            return '%s, <a href="tel:%s">%s</a>, %s ' \
                   % (obj.address_book.name, obj.address_book.phone, obj.address_book.phone, obj.address_book.address)
        else:
            return 'NULL'

    shipping_address.short_description = 'Penerima Pesanan'
    shipping_address.allow_tags = True

    def orders(self, obj):

        if obj.orderedproduct_set.first():
            product_count = 1
            str_orders = ""
            for sc in obj.orderedproduct_set.first().shopping_carts.all():
                url = '%s/admin/poken_rest/product/%s/change/' % (properties.DJANGO_HOST, sc.product.id)
                str_orders += '%d - <a target="_blank" href="%s">%s</a> (%d)<hr /><br />' \
                              % (product_count, url, sc.product.name[:50], sc.quantity)
                product_count += 1

            return '%s' % str_orders
        else:
            return '-'

    orders.short_description = 'Produk Pesanan'
    orders.allow_tags = True

    def shopping_cart_data(self, obj):
        if obj.shopping_carts:
            return ''.join('Produk ID: %s (banyak: %s), ' %
                           (sc.product.id, sc.quantity) for sc in obj.shopping_carts.all()).rsplit(',', 1)[0]
        else:
            return 'Data produk troli kosong'

    def payment_expiration(self, obj):
        if obj.payment_expiration_date:
            now = datetime.datetime.now(pytz.utc)
            diff = obj.payment_expiration_date - now
            if (diff.total_seconds() < 0):
                return Order.EXPIRE_TEXT
            else:
                return "Sisa waktu: %s" % diff
        else:
            return 'NOT SET'

    def order_status_text(self, obj):
        status = obj.order_status
        if status == Order.INITIALIZE:
            return Order.INITIALIZE_TEXT
        elif status == Order.SOLD_OUT:
            return Order.SOLD_OUT_TEXT
        elif status == Order.BOOKED:
            return Order.BOOKED_TEXT
        elif status == Order.PAID:
            return Order.PAID_TEXT
        elif status == Order.SENT:
            return Order.SENT_TEXT
        elif status == Order.RECEIVED:
            return Order.RECEIVED_TEXT
        elif status == Order.SUCCESS:
            return Order.SUCCESS_TEXT
        elif status == Order.REFUND:
            return Order.REFUND_TEXT
        elif status == Order.EXPIRE:
            return Order.EXPIRE_TEXT
        elif status == Order.COD_AUTO_SUCCESS:
            return Order.COD_AUTO_SUCCESS_TEXT


class SubscribedAdmin(admin.ModelAdmin):
    list_display = ('id', 'seller', 'customer',)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'description', 'seller_name', 'discount_status', 'is_posted', 'is_new', 'date_created',
        'product_brand', 'category_name', 'size_name', 'stock', 'price', 'weight')

    search_fields = ('name', 'description')

    def seller_name(self, obj):
        if obj.seller:
            return '%s' % (obj.seller.store_name)

    def product_brand(self, obj):
        if obj.brand:
            return '%s' % (obj.brand.name)
        else:
            return 'Brand kosong'

    def category_name(self, obj):
        if obj.category:
            return '%s' % (obj.category.name)
        else:
            return 'Kategori kosong'

    def size_name(self, obj):
        if obj.size:
            return '%s' % (obj.size.name)
        else:
            return 'Ukuran kosong'

    def discount_status(self, obj):
        if obj.is_discount:
            return "Diskon %d" % obj.discount_amount
        else:
            return "NON DISCOUNT"


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_data', 'product_data', 'date', 'quantity',
                    'shipping_method', 'selected_product_fee', 'shipping_fee', 'shopping_cart_item_fee', 'extra_note')

    def shipping_method(self, obj):
        if obj.shipping:
            return '%s' % obj.shipping.name
        else:
            return 'Pengiriman tidak ada'

    def customer_data(self, obj):
        if obj.customer:
            return '%s' % (obj.customer.related_user.username)
        else:
            return 'Customer kosong'

    def product_data(self, obj):
        if obj.product:
            return '%s' % (obj.product.name)
        else:
            return 'Produk kosong'


class OrderedProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_details_data', 'shopping_cart_data',)

    def order_details_data(self, obj):
        if obj.order_details:
            return 'ID: %s' % (obj.order_details.order_id)
        else:
            return 'ID Order kosong'

    def shopping_cart_data(self, obj):
        if obj.shopping_carts:
            return ''.join('Produk ID: %s, Seller ID: %s (banyak: %s), ' %
                           (sc.product.id, sc.product.seller, sc.quantity) for sc in obj.shopping_carts.all()).rsplit(',', 1)[0]
        else:
            return 'Data produk troli kosong'


class CollectedProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_data', 'customer_data', 'status')

    def product_data(self, obj):
        if obj.product:
            return '%s' % (obj.product.name)
        else:
            return 'Produk kosong'

    def customer_data(self, obj):
        if obj.customer:
            return '%s' % (obj.customer.related_user.username)
        else:
            return 'Customer kosong'


admin.site.register(HomeItem, HomeItemAdmin)
admin.site.register(HomeProductSection, HomeProductSectionAdmin)
admin.site.register(FeaturedItem, FeaturedItemAdmin)
admin.site.register(ProductCategoryFeatured, ProductCategoryFeaturedAdmin)
admin.site.register(Seller, SellerAdmin)
admin.site.register(SellerPromo, SellerPromoItemAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(ProductBrand, ProductBrandAdmin)
admin.site.register(ProductSize, ProductSizeAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(UserImage, UserImageAdmin)
admin.site.register(UserBank, UserBankAdmin)
admin.site.register(Bank, BankAdmin)
admin.site.register(Courier, CourierAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(AddressBook, AddressBookAdmin)
admin.site.register(Shipping, ShippingAdmin)
admin.site.register(OrderDetails, OrderDetailsAdmin)
admin.site.register(Subscribed, SubscribedAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(OrderedProduct, OrderedProductAdmin)
admin.site.register(CollectedProduct, CollectedProductAdmin)
admin.site.register(UserLocation, UserLocationAdmin)
