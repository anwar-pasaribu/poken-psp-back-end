# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import thread
import threading

import requests
from django.utils import html
from django.utils.formats import localize
from django.utils import timezone
import pytz
from fcm_django.models import FCMDevice

from poken_psp import properties
from poken_rest.domain import Order

URL_SLACK_TEST = "https://hooks.slack.com/services/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"
URL_SLACK_POKEN_SALES = "https://hooks.slack.com/services/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"
URL_SLACK_POKEN_ORDER_EXPIRE = "https://hooks.slack.com/services/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"
URL_SLACK_POKEN_ORDER_RECEIVED = "https://hooks.slack.com/services/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"
URL_SLACK_POKEN_ORDER_REFUND = "https://hooks.slack.com/services/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"


class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)


def send_slack_order_status_changes_notif(order_data):
    request = order_data['request']
    order_details = order_data['data']

    url_order = request.build_absolute_uri(
        'admin/poken_rest/orderdetails/%d/change/' % order_details.id)

    shopping_carts = order_details.orderedproduct_set.first().shopping_carts.all()

    order_ref = order_details.order_id
    order_status = int(order_details.order_status)
    customer = order_details.customer
    cust_name = html.escape(str(customer.related_user.get_full_name()))

    slack_url = ""
    slack_msg = ":)"

    print ("Order status: %d" % order_status)

    str_template_product_info = '''{
                        "title": "%s",
                        "title_link": "%s",
                        "text": "%s\nStok barang: %d",
                        "color": "%s"
                    }'''

    str_ordered_items = ""
    str_color_code = "#ED1C24"
    for sc in shopping_carts:

        # Replace poken_rest/order_details/183/
        url_product_detail = request.build_absolute_uri('admin/poken_rest/product/%d/change/' % sc.product.id)

        if order_status == Order.RECEIVED:
            url_product_detail = url_product_detail.replace(('poken_rest/order_details/%s/' % order_details.id), '')
            str_color_code = "#1BA260"  # GREEN GOOGLE CHROME
        elif order_status == Order.REFUND:
            url_product_detail = url_product_detail.replace(('poken_rest/order_details/%s/' % order_details.id), '')
            str_color_code = "#F4AF39"  #ORANGE GOOGLE CHROME
        else:
            url_product_detail = url_product_detail.replace('poken_rest/ordered_product/', '')
            str_color_code = "#ED1C24"  # RED GOOGLE CHROME

        str_ordered_items += str_template_product_info % (
            html.escape(sc.product.name.replace('"', '\\"')),
            url_product_detail,
            html.escape(sc.product.description.replace('"', '\\"'))[:100],  # First hundred
            sc.product.stock,
            str_color_code
        ) + ","

    str_ordered_items = str_ordered_items.rsplit(',', 1)[0]

    if order_status == Order.RECEIVED:
        slack_url = URL_SLACK_POKEN_ORDER_RECEIVED
        url_order = url_order.replace(('poken_rest/order_details/%s/' % order_details.id), '')
        slack_msg = """{ 
            "text": "Pesanan Barang order ref. <%s|%s> oleh %s telah %s.",
            "attachments": [%s]
            }""" % (url_order, order_ref, cust_name, Order.RECEIVED_TEXT, str_ordered_items)
    elif order_status == Order.REFUND:
        slack_url = URL_SLACK_POKEN_ORDER_REFUND
        url_order = url_order.replace(('poken_rest/order_details/%s/' % order_details.id), '')
        slack_msg = """{ 
            "text": "Pesanan Barang order ref. <%s|%s> oleh %s telah %s. Segera proses.",
            "attachments": [%s]
            }""" % (url_order, order_ref, cust_name, Order.REFUND_TEXT, str_ordered_items)
        print(slack_msg)
    elif order_status == Order.EXPIRE:
        slack_url = URL_SLACK_POKEN_ORDER_EXPIRE
        url_order = url_order.replace('poken_rest/ordered_product/', '')
        slack_msg = """{ "text": "Pesanan Barang order ref. <%s|%s> oleh %s telah %s.", "attachments": [%s] }""" \
                    % (url_order, order_ref, cust_name, Order.EXPIRE_TEXT, str_ordered_items)

    payload = slack_msg

    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache"
    }

    if properties.IS_TEST_SLACK:
        slack_url = URL_SLACK_TEST

    response = requests.request("POST", slack_url, data=payload.encode('utf-8'), headers=headers)

    print ("Slack webhook order-expire response: " + str(response.text))


def send_slack_new_order_notif(new_ordered_product):
    request = new_ordered_product['request']
    ordered_product = new_ordered_product['data']

    url_order = request.build_absolute_uri(
        'admin/poken_rest/orderdetails/%d/change/' % ordered_product.order_details.id)

    url_order = url_order.replace(('poken_rest/order_details/%s/' % ordered_product.order_details.id), '')

    order_id_link = '<%s|%s>' % (url_order, ordered_product.order_details.order_id)
    # Custom time zone 'Asia/Jakarta'
    order_date = timezone.localtime(ordered_product.order_details.date, pytz.timezone('Asia/Jakarta')).strftime("%A, %d %B %Y %H:%M:%S")
    customer = ordered_product.order_details.customer
    address_book = ordered_product.order_details.address_book
    cust_name = html.escape(str(customer.related_user.get_full_name()))
    shipping_receiver_name = html.escape(str(address_book.name))
    shipping_receiver_phone = html.escape(address_book.phone)
    shipping_receiver_address = html.escape(address_book.address)

    message = "Pesanan baru %s pada %s" % (cust_name, order_date)

    for sc in ordered_product.shopping_carts.all():

        # sc.product.price = (sc.product.price - ((sc.product.price * sc.product.discount_amount) / 100))
        # total_cost = sc.product.price * sc.quantity + sc.shipping_fee
        #
        # str_note = html.escape(sc.extra_note.replace('"', '\\"'))
        # if len(str_note) == 0:
        #     str_note = '-'
        #
        # str_ordered_items += str_ordered_temp % (
        #     html.escape(sc.product.name.replace('"', '\\"')),
        #     html.escape(request.build_absolute_uri(sc.product.images.first().path.url)),
        #     html.escape(sc.product.description.replace('"', '\\"'))[:100],  # First hundred
        #     sc.quantity,
        #     "{:,}".format(sc.product.price),
        #     "{:,}".format(total_cost),
        #     sc.product.stock,
        #     sc.shipping.name,
        #     "{:,}".format(sc.shipping_fee),
        #     sc.shipping_service,
        #     str_note,
        #     html.escape(sc.product.seller.store_name.replace('"', '\\"')),
        #     html.escape(sc.product.seller.phone_number), html.escape(sc.product.seller.phone_number)
        # ) + ","

        product_seller = sc.product.seller
        seller_related_user = product_seller.related_user

        fcm_devices = FCMDevice.objects.filter(user=seller_related_user)
        print("FCM Devices count", len(fcm_devices))
        if len(fcm_devices) > 0:
            device = fcm_devices.first()
            print("Device : ", device)
            if device:
                print("Message " + message)
                res = device.send_message(
                    title="Poken - Pesanan Baru",
                    body=message,
                    data={"product_id": '%s' % sc.product.id, "order_id": '%s' % ordered_product.order_details.order_id}
                )
                print("Res: ", res)


# NEW ORDER NOTIF.
def start_message_ordered_product(new_ordered_product, request):
    slack_content = {
        'request': request,
        'data': new_ordered_product
    }

    if properties.IS_SLACK_MESSAGE_ON:
        thread.start_new_thread(send_slack_new_order_notif, (slack_content,))


def start_message_order_status_changes(order_details, request):
    slack_content = {
        'request': request,
        'data': order_details
    }

    if properties.IS_SLACK_MESSAGE_ON:
        thread.start_new_thread(send_slack_order_status_changes_notif, (slack_content,))
