# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from poken_rest.models import Seller, Customer, ProductBrand, ProductSize, ProductCategory, ProductImage, Courier, \
    UserLocation, Location, AddressBook, Shipping, OrderDetails, Subscribed, Product, ShoppingCart, OrderedProduct, \
    CollectedProduct, FeaturedItem, HomeProductSection, HomeItem


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


class UserLocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'address', 'city', 'district', 'zip', 'state')


class SellerAdmin(admin.ModelAdmin):
    list_display = ('user_info', 'bio', 'tag_line', 'phone_number')

    def user_info(self, obj):
        if obj.related_user:
            return 'User: %s (%s)' % (obj.related_user.first_name, obj.related_user.email)
        else:
            return 'Data User bermasalah'


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user_info', 'phone_number', 'location')

    def user_info(self, obj):
        if obj.related_user:
            return 'User: %s (%s)' % (obj.related_user.first_name, obj.related_user.email)
        else:
            return 'Data User bermasalah'


class ProductBrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'logo')


class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'related_sizes', 'name',)

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
    list_display = ('cust_name', 'name', 'location_address', 'address', 'phone',)

    def cust_name(self, obj):
        if obj.customer:
            return '%s' % obj.customer.related_user.username
        else:
            return 'Customer kosong'

    def location_address(self, obj):
        if obj.location:
            return '%s, %s' % (obj.location.district, obj.location.city)
        else:
            return 'Lokasi kosong'


class ShippingAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'fee',)


class OrderDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'cust_name', 'shipping_address', 'date', 'shipping_fee')

    def cust_name(self, obj):
        if obj.customer:
            return '%s' % obj.customer.name
        else:
            return 'Customer kosong'

    def shipping_address(self, obj):
        if obj.address:
            return '%s' % (obj.address.name)
        else:
            return 'Address book kosong'

    def shipping_fee(self, obj):
        if obj.shipping:
            return '%s: Rp %s' % (obj.shipping.name, obj.shipping.fee)
        else:
            return 'Kurir pengiriman kosong'


class SubscribedAdmin(admin.ModelAdmin):
    list_display = ('id', 'seller', 'customer',)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'seller_name', 'is_posted', 'is_new', 'date_created',
                    'product_brand', 'category_name', 'size_name', 'stock', 'price', 'weight')

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


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_data', 'product_data', 'date', 'quantity')

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
    list_display = ('id', 'order_details_data', 'shopping_cart_data', 'status')

    def order_details_data(self, obj):
        if obj.order_details:
            return 'ID: %s' % (obj.order_details.order_id)
        else:
            return 'ID Order kosong'

    def shopping_cart_data(self, obj):
        if obj.shopping_cart:
            return ''.join('Produk ID: %s (banyak: %s), ' %
                           (sc.product.id, sc.quantity) for sc in obj.shopping_cart.all()).rsplit(',', 1)[0]
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
            return '%s' % (obj.customer.name)
        else:
            return 'Customer kosong'


admin.site.register(HomeItem, HomeItemAdmin)
admin.site.register(HomeProductSection, HomeProductSectionAdmin)
admin.site.register(FeaturedItem, FeaturedItemAdmin)
admin.site.register(Seller, SellerAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(ProductBrand, ProductBrandAdmin)
admin.site.register(ProductSize, ProductSizeAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
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