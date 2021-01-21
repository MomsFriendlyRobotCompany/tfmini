#!/usr/bin/env python3
#
# MIT License
#

# from serial import Serial
import time
from tfmini import TFmini


tf = TFmini('/dev/tty.usbserial-A506BOT5', mode=TFmini.STD_MODE)

try:
    print('='*25)
    while True:
        d = tf.read()
        # d = tf.read()
        # s = q = 0
        if d:
            print('Distance: {:5}'.format(d))
        else:
            print('No valid response')
        time.sleep(0.1)

except KeyboardInterrupt:
    tf.close()
    print('bye!!')
