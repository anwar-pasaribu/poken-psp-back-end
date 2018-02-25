# Send to single device.

from __future__ import print_function
from fcm_django.models import FCMDevice


def test():

    device = FCMDevice.objects.all().first()

    if device:
        #device.send_message("Title", "Message")
        #device.send_message(data={"test": "test"})
        device.send_message(title="Title", body="Message", data={"test": "test"})

    else:
        print("No device found.")



    print(device)
