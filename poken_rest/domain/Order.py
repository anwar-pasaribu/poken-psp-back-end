BOOKED = 0  # Default order status
PAID = 1
SENT = 2
RECEIVED = 3
SUCCESS = 4
REFUND = 5
EXPIRE = 6

BOOKED_TEXT = 'DIPESAN'# Default order status
PAID_TEXT = 'DIBAYAR'
SENT_TEXT = 'DIKIRIM'
RECEIVED_TEXT = 'DITERIMA'
SUCCESS_TEXT = 'BERES'
REFUND_TEXT = 'REFUND'
EXPIRE_TEXT = 'HANGUS'

'''
* [0] Booked: menunggu verifikasi. 
* [1] Paid
* [2] Sent. 
* [3] Received. Auto: **seminggu**. Atau cek resi melalui API pos Indonesia. 
* [4] Success
* [5] Refund: kantor pos gratis.
* [6] Expire. 
'''