import random
import string

import datetime
import calendar


def mobile_order_id_generator(size=9, chars=string.ascii_uppercase + string.digits):
    hour = datetime.datetime.today().hour
    minute = datetime.datetime.today().minute
    second = datetime.datetime.today().second
    day = datetime.datetime.today().day

    print "Day: %s" % day

    rand_id = 'M' + ''.join(random.choice(chars) for _ in range(size))

    return rand_id

"""
Test run function.
"""
if __name__ == '__main__':
    print "Code: %s" % mobile_order_id_generator()