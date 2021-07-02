# MIT License
#
# TFmini appears to be an eye safe laser ... asked for confirmation
# 120 mW @ 850 nm, class ?
# Sparkfun website says it is not a laser ... hence, no eye issues
#
from serial import Serial
import time
from collections import deque
import struct


class SerialBase:

    def __init__(self, port):
        """
        port: serial port, /dev/tty.usb1234 or /dev/ttyUSB0
        mode: DEC_MODE or STD_MODE
        retry: number of attempts to read input for valid data before failing
        """
        self.serial = Serial()
        self.serial.port = port
        self.serial.baudrate = 115200
        self.serial.timeout = 0.1
        self.serial.open()
        if not self.serial.is_open:
            raise Exception(f"ERROR: couldn't open port: {port}")

    def __del__(self):
        self.close()

    def close(self):
        if self.serial.is_open:
            self.serial.close()

    def format(self, newmode):
        self.__config(newmode)

    def print(self, front, msg):
        print(front, ','.join([hex(i) for i in msg]))

    def __send(self, msg):
        """
        return ok[T/F], reply[bytearray]
        """
        self.serial.flushInput()
        self.serial.write(msg)

        limit = 15
        for i in range(limit+1):
            ch = self.serial.read(1)
            # print(f">> {ch}")
            if not ch:
                continue

            if ch[0] == 0x42:
                reply = self.serial.read(len(msg) - 1)
                # print(f">> header {i}")
                return True, reply
            elif i == limit:
                return False, None
        return False, None

    def __sendRespond(self, msg):
        """
        return T/F
        """
        for rev in range(5):
            # print(f"{rev}:------------------------")
            ok, reply = self.__send(msg)
            if ok:
                break

        # self.print("msg:", msg)
        # self.print("reply:", reply)

        if reply[2] == 0x01:
            # print(">> GOOD copy")
            return True

        # print("*** ERROR ***")
        return False

    def __config(self, command):
        """Manager for sending commands, put sensor into config mode, config,
        then exit configuration mode

        Return T/F
        """
        ENTER = b"\x42\x57\x02\x00\x00\x00\x01\x02"
        EXIT = b"\x42\x57\x02\x00\x00\x00\x00\x02"
        if self.__sendRespond(ENTER):
            if self.__sendRespond(command):
                if self.__sendRespond(EXIT):
                    return True
        return False

# this is standard
class Std(SerialBase):
    unpack = struct.Struct("<HHb")

    def __init__(self, port):
        super().__init__(port)

        cmd = b"\x42\x57\x02\x00\x00\x00\x01\x06"
        self.format(cmd)

    def get(self, retry):
        """
        Return distance[m] or None
        """
        # find header
        tmp = deque(maxlen=retry*9)
        count = retry*12
        ret = None

        self.serial.flushInput()
        a = self.serial.read(1)
        b = self.serial.read(1)
        while True:
            if a[0] == 0x59 and b[0] == 0x59:
                # print('found header')
                pkt = self.serial.read(7)
                try:
                    ret = self.process(pkt)
                except Exception as e:
                    # print('bad')
                    print(e)
                    ret = None
                break
            if count == 0:
                # print("crap")
                break
            a = b
            b = self.serial.read(1)
            count -= 1

        return ret

    def process(self, pkt):
        """
        packet = [0x59, 0x59, distL, distH, strL, strH, reserved, integration time, checksum]

        Note: the integration time always seems to be 0
        """
        # calculate checksum
        cs = 0x59 + 0x59 + sum(pkt[:-1])
        cs &= 0xff

        if pkt[-1] != cs:
            raise Exception(f"ERROR: bad checksum in packet: {cs} != {pkt[-1]}")

        dist, strength, mode = self.unpack.unpack(pkt[:5])
        # print(dist, strength, mode)

        return dist/100, strength

# this is PIX
class Pix(SerialBase):
    """
    ASCII output for PixHawk
    """
    def __init__(self, port):
        super().__init__(port)

        cmd = b"\x42\x57\x02\x00\x00\x00\x04\x06"
        self.format(cmd)

    def get(self, retry):
        self.serial.flushInput()
        d = self.serial.read(retry*12)
        n = d.find(b"\r\n")
        if n > 0:
            s = d[:n]
            print([hex(x) for x in s])
            try:
                ret = float(s)
            except:
                ret = None
        else:
            ret = None
        return ret, -1


class Dec(Pix):
    """
    Use Pix instead
    """
    pass

class TFmini(object):
    """
    Outputs sensor measurements in meters. You can select either Std format or
    Pix format.

    TFMini - Micro LiDAR Module
    https://www.sparkfun.com/products/14577
    http://www.benewake.com/en/tfmini.html
    """
    NOHEADER = 1
    BADCHECKSUM = 2
    TOO_MANY_TRIES = 3
    DEC_MODE = 4  # packet - old name
    STD_MODE = 5  # packet
    PIX_MODE = 6  # ascii

    def __init__(self, port, mode=6, retry=2):
        """
        port: serial port, /dev/tty.usb1234 or /dev/ttyUSB0
        mode: DEC_MODE/PIX_MODE or STD_MODE
        retry: number of attempts to read input for valid data before failing
        """
        self.retry = retry  # how many times will I retry to find the packet header
        self.mode = mode
        self.strength = -1

        if mode == self.STD_MODE:
            self.proto = Std(port)
        elif mode in [self.DEC_MODE, self.PIX_MODE]:
            self.proto = Pix(port)
        else:
            raise Exception(f"Invalid mode: {mode}")

    def close(self):
        self.proto.close()

    def read(self):
        """
        This is the main read() function. The others are automagically selected
        based off the mode the sensor was set too.
        STD Mode: return (dist, strength, quality)
        DEC Mode: return range in meters
        """
        ret = self.proto.get(self.retry)
        if ret is None:
            return None

        # weed out stupid returns ... strings can give crazy numbers
        dist, self.strength = ret
        if dist is None:
            return None

        # if dist > 12.0 or dist < 0.3:
        #     return None
        if dist > 12.0:
            dist = 12.0
        elif dist < 0.0:
            dist = 0.0

        return dist
