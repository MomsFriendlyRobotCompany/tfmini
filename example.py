#!/usr/bin/env python3
#
# MIT License
#

import time
from tfmini import TFmini

port = "/dev/tty.usbserial-A904MISU"

# mode = TFmini.PIX_MODE # Pixhawk - ascii
mode = TFmini.STD_MODE # packet

tf = TFmini(port, mode=mode)

try:
    print('='*25)
    # while True:
    for _ in range(100):
        d = tf.read()
        if d:
            print(f'Distance: {d:5}')
        else:
            print('No valid response')
        time.sleep(0.01)

except KeyboardInterrupt:
    tf.close()
    print('bye!!')
