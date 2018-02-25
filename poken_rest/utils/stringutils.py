import random
import string

import datetime
import calendar

from django.utils import timezone


def mobile_order_id_generator(size=9, chars=string.ascii_uppercase + string.digits):
    hour = datetime.datetime.today().hour
    minute = datetime.datetime.today().minute
    second = datetime.datetime.today().second
    day = datetime.datetime.today().day

    rand_id = 'M' + ''.join(random.choice(chars) for _ in range(size))

    return rand_id

def get_one_day_from_now():

    tomorrow = datetime.datetime.now() + datetime.timedelta(days=0, hours=24)

    return tomorrow

"""
Test run function.
"""
if __name__ == '__main__':
    print "Code: %s" % mobile_order_id_generator()
    print "Tomorrow : %s" % get_one_day_from_now()

    # TEST EXPIRE 5 seconds
    now = datetime.datetime(2017, 07, 30, 12, 1, 5)
    then = datetime.datetime(2017, 07, 30, 12, 1, 0)
    diff = then - now
    if diff.total_seconds() < 0:
        print "Expire %s " % diff.total_seconds()
    else:
        print "Diff %s " % diff.total_seconds()

    a = ['A', 'A', 'X', 'B', 'C']
    print("Data: %s", a)