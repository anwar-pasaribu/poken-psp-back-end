"""poken_psp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import url, include
from rest_framework import routers
from poken_rest import views

from rest_framework.authtoken import views as token_views

router = routers.DefaultRouter()
router.register(r'home', views.HomeContentViewSet, 'home')
router.register(r'featured', views.FeaturedItemDetailViewSet, 'featured')
router.register(r'order_details', views.OrderDetailsViewSet, 'order_details')
router.register(r'ordered_product', views.OrderedProductViewSet, 'ordered_product')
router.register(r'insert_ordered_product', views.InsertOrderedProductViewSet, 'insert_ordered_product')
router.register(r'insert_product', views.InsertProductViewSet, 'insert_product')
router.register(r'insert_product_image', views.InsertProductImageViewSet, 'insert_product_image')
router.register(r'insert_cart', views.InsertShoppingCartViewSet, 'insert_cart')
router.register(r'insert_user', views.InsertUserViewSet, 'insert_user')
router.register(r'insert_order_detail', views.InsertOrderDetailsViewSet, 'insert_order_detail')
router.register(r'insert_customer_subscribed', views.InsertCustomerSubscribedViewSet, 'insert_customer_subscribed')
router.register(r'product_brand', views.ProductBrandViewSet, 'product_brand')
router.register(r'product_category', views.ProductCategoryViewSet, 'product_category')
router.register(r'product_category_featured', views.ProductCategoryFeaturedViewSet, 'product_category_featured')
router.register(r'product', views.ProductViewSet, 'product')
router.register(r'user_location', views.UserLocationViewSet, 'user_location')
router.register(r'seller', views.SellerViewSet, 'seller')
router.register(r'shipping_rates', views.ShippingRatesViewSet, 'shipping_rates')
router.register(r'customer', views.CustomerViewSet, 'customer')
router.register(r'customer_collection', views.CollectedProductViewSet, 'customer_collection')
router.register(r'customer_subscription', views.SubscribedViewSet, 'customer_subscription')
router.register(r'address_book', views.AddressBookSerializerViewSet, 'address_book')
router.register(r'cart', views.ShoppingCartViewSet, 'cart')
router.register(r'users', views.UserViewSet, 'users')
router.register(r'groups', views.GroupViewSet, 'groups')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^poken_rest/', include(router.urls)),
    url(r'^poken_web/', include('poken_web.urls', namespace="peber_web")),
    url(r'^poken_rest/poken_rest-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
# we are serving static and media files here at the moment - if we deploy this app to a server, we do necessarily want this
if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    url(r'^poken_rest/api-token-auth/', token_views.obtain_auth_token)
]

