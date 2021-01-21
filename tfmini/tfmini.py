# MIT License
#
# TFmini appears to be an eye safe laser ... asked for confirmation
# 120 mW @ 850 nm, class ?
# Sparkfun website says it is not a laser ... hence, no eye issues
#
from serial import Serial
import time


class TFmini(object):
    """
    TFMini - Micro LiDAR Module
    https://www.sparkfun.com/products/14577
    http://www.benewake.com/en/tfmini.html
    """
    NOHEADER = 1
    BADCHECKSUM = 2
    TOO_MANY_TRIES = 3
    DEC_MODE = 4
    STD_MODE = 5

    def __init__(self, port, mode=5, retry=25):
        self.serial = Serial()
        self.serial.port = port
        self.serial.baudrate = 115200
        self.serial.timeout = 0.005
        self.serial.open()
        self.retry = retry  # how many times will I retry to find the packet header
        self.mode = mode
        self.strength = -1

        if not self.serial.is_open:
            raise Exception("ERROR: couldn't open port: {}".format(port))

        self.setStdMode(self.mode)

    def setStdMode(self, mode):
        # do I need this?
        if mode == self.STD_MODE:
            cmd = [0x42, 0x57, 0x02, 0x00, 0x00, 0x00, 0x01, 0x06]  # hex - packet
        elif mode == self.DEC_MODE:
            cmd = [0x42, 0x57, 0x02, 0x00, 0x00, 0x00, 0x04, 0x06]  # dec - string
        else:
            raise Exception("ERROR: invalid mode {}".format(mode))

        self.mode = mode
        data = bytearray(cmd)
        data = bytes(data)
        self.serial.write(data)
        time.sleep(0.1)

    def __del__(self):
        self.close()

    def close(self):
        self.serial.close()

    def readString(self):
        self.serial.flushInput()
        tmp = []

        d = ' '
        while d != '\n':
            d = self.serial.read(1)
            tmp.append(d)
        try:
            tmp = tmp[:-2]  # get rid of \r\n
            ret = float(''.join(tmp))
        except:
            ret = None
        return ret

    def readPacket(self):
        # it looks like it streams data, so no command to measure needed
        self.serial.flushInput()

        # find header
        a, b = ' ', ' '
        tmp = []
        count = self.retry
        while True:
            tmp.append(a)
            a = b
            b = self.serial.read(1)
            if len(a) > 0 and len(b) > 0:
                if ord(a) == 0x59 and ord(b) == 0x59:
                    # print('found header')
                    break
            if count == 0:
                # print('nothing:', tmp)
                # print('str', ''.join(tmp))
                return None
            count -= 1

        raw = self.serial.read(7)
        # build a packet (array) of ints
        pkt = [ord(a), ord(b)] + list(map(ord, raw))
        # print('pkt', pkt)
        try:
            ret = self.processPkt(pkt)
        except Exception as e:
            # print('bad')
            print(e)
            ret = None
        return ret

    def read(self):
        """
        This is the main read() function. The others are automagically selected
        based off the mode the sensor was set too.
        STD Mode: return (dist, strength, quality)
        DEC Mode: return range in meters
        """
        if self.mode == self.STD_MODE:
            ret = self.readPacket()
        elif self.mode == self.DEC_MODE:
            ret = self.readString()
        else:
            raise Exception('ERROR: read() invalid mode {}'.format(self.mode))

        # weed out stupid returns ... strings can give crazy numbers
        if ret > 12.0 or ret < 0.3:
            ret = None

        return ret

    def processPkt(self, pkt):
        """
        packet = [0x59, 0x59, distL, distH, strL, strH, reserved, integration time, checksum]

        Note: the integration time always seems to be 0
        """
        # turn string data into array of bytes
        # pkt = list(map(ord, pkt))
        if len(pkt) != 9:
            raise Exception("ERROR: packet size {} != 9".format(len(pkt)))

        # check header
        if pkt[0] != 0x59 or pkt[1] != 0x59:
            raise Exception("ERROR: bad header in packet")

        # calculate checksum
        cs = sum(pkt[:8])
        cs &= 0xff
        # print('cs', cs, pkt[8])

        if pkt[8] != cs:
            print('cs', cs, pkt[8])
            raise Exception("ERROR: bad checksum in packet")

        # print('L {} H {}'.format(pkt[2], pkt[3]))
        dist = (pkt[2] + (pkt[3] << 8))/100
        self.strength = pkt[4] + (pkt[5] << 8)
        # q    = pkt[7]

        # print('ans',dist, st, q)

        return dist
