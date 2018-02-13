.. image:: https://raw.githubusercontent.com/MomsFriendlyRobotCompany/tfmini/master/tfmini.jpg

TFmini
========

Install
----------

Install using ``pip``:

::

    pip install -U tfmini

Usage
------

Reading the sensor returns the range in meters.

.. code-block:: python

    from __future__ import division, print_function
    import time
    from tfmini import TFmini

    # create the sensor and give it a port and (optional) operating mode
    tf = TFmini('/dev/tty.usbserial-A506BOT5', mode=TFmini.STD_MODE)

    try:
        print('='*25)
        while True:
            d = tf.read()
            if d:
                print('Distance: {:5}'.format(d))
            else:
                print('No valid response')
            time.sleep(0.1)

    except KeyboardInterrupt:
        tf.close()
        print('bye!!')


- ``TFmini(port, mode=5, retry=25)``: the constructor takes several inputs
    - ``port``: serial port the sensor is connected too
    - ``mode``: either standard (*default*) or decimal mode
    - ``retry``: how many times the driver should search the serial port for the packet header. This only applies in standard mode.
- ``read()``: in any mode, returns the distance in meters
- ``TFmini.strength``: in standard mode, each packet contains the returned IR strength level. In decimal mode, this doesn't exist and is always set to -1.

Standard (Packet) Mode
-----------------------------

In this mode, a data packet is sent from the sensor:

::

    packet = [0x59, 0x59, distL, distH, strL, strH, reserved, integration time, checksum]

Where the first two bytes ``0x59, 0x59`` are the header and each packet has a
checksum to ensure the packet is valid data.

Decimal (String) Mode
----------------------------

In this mode, the sensor can sometimes returns an incorrect value because the
ASCII string was read wrong across the serial port. There is no error checking
in this mode.

.. code-block:: bash

    Distance:  2.96
    Distance:  2.96
    Distance:  96.0 <<< Error
    Distance:  2.95
    Distance:  2.95
    Distance:  2.96

References
-------------

- `Sparkfun product page <https://www.sparkfun.com/products/14577>`_
- `Manufacturer produce page <http://www.benewake.com/en/tfmini.html>`_

MIT License
============

**Copyright (c) 2018 Kevin Walchko**

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
