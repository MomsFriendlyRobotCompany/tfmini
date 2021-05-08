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

class Dec:
    cmd = b"\x42\x57\x02\x00\x00\x00\x04\x06"
    unpack = struct.Struct("<hh")

    def get(self, ser, retry):
        # it looks like it streams data, so no command to measure needed
        ser.flushInput()

        # find header
        tmp = deque(maxlen=retry*11)
        count = retry*11

        a = ser.read(1)
        b = ser.read(1)
        while True:
            if a == 0x59 and b == 0x59:
                # print('found header')
                break
            if count == 0:
                return None
            a = b
            b = ser.read(1)
            count -= 1

        pkt = ser.read(7)
        try:
            ret = self.processPkt(pkt)
        except Exception as e:
            # print('bad')
            # print(e)
            ret = None
        return ret

    def process(self, pkt):
        """
        packet = [0x59, 0x59, distL, distH, strL, strH, reserved, integration time, checksum]

        Note: the integration time always seems to be 0
        """
        # calculate checksum
        cs = 0x59 + 0x59 + sum(pkt[:-1])
        cs &= 0xff
        # print('cs', cs, pkt[8])

        if pkt[-1] != cs:
            # print('cs', cs, pkt[8])
            raise Exception(f"ERROR: bad checksum in packet: {cs} != {pkt[-1]}")

        dist, strength = self.unpack(*pkt[:4])

        return dist/100, strength


class Std:
    cmd = b"\x42\x57\x02\x00\x00\x00\x04\x06"

    def get(self, ser, retry):
        self.serial.flushInput()
        d = ser.read(retry*11)
        n = d.find("\r\n")
        if n > 0:
            s = d[:n]
            try:
                ret = float(s)
            except:
                ret = None
        else:
            ret = None
        return ret, -1


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

    def __init__(self, port, mode=5, retry=2):
        """
        port: serial port, /dev/tty.usb1234 or /dev/ttyUSB0
        mode: DEC_MODE or STD_MODE
        retry: number of attempts to read input for valid data before failing
        """
        self.serial = Serial()
        self.serial.port = port
        self.serial.baudrate = 115200
        self.serial.timeout = 0.005
        self.serial.open()
        self.retry = retry  # how many times will I retry to find the packet header
        self.mode = mode
        self.strength = -1


        if mode == self.STD_MODE:
            self.proto = Std()
        elif mode == self.DEC_MODE:
            self.prot = Dec()
        else:
            raise Exception(f"Invalid mode: {mode}")

        if not self.serial.is_open:
            raise Exception(f"ERROR: couldn't open port: {port}")

        self.serial.write(self.proto.cmd)
        time.sleep(0.1)

    def __del__(self):
        self.close()

    def close(self):
        self.serial.close()

    def read(self):
        """
        This is the main read() function. The others are automagically selected
        based off the mode the sensor was set too.
        STD Mode: return (dist, strength, quality)
        DEC Mode: return range in meters
        """
        ret = self.proto.get(self.serial, self.retry)
        if ret is None:
            return None

        # weed out stupid returns ... strings can give crazy numbers
        dist, self.strength = ret
        if dist > 12.0 or dist < 0.3:
            return None

        return dist


#######################################################################


# class TFminiold(object):
#     """
#     TFMini - Micro LiDAR Module
#     https://www.sparkfun.com/products/14577
#     http://www.benewake.com/en/tfmini.html
#     """
#     NOHEADER = 1
#     BADCHECKSUM = 2
#     TOO_MANY_TRIES = 3
#     DEC_MODE = 4
#     STD_MODE = 5
#
#     unpack = struct.Struct("<hh")
#
#     def __init__(self, port, mode=5, retry=2):
#         """
#         port: serial port, /dev/tty.usb1234 or /dev/ttyUSB0
#         mode: DEC_MODE or STD_MODE
#         retry: number of attempts to read input for valid data before failing
#         """
#         self.serial = Serial()
#         self.serial.port = port
#         self.serial.baudrate = 115200
#         self.serial.timeout = 0.005
#         self.serial.open()
#         self.retry = retry  # how many times will I retry to find the packet header
#         self.mode = mode
#         self.strength = -1
#
#         if not self.serial.is_open:
#             raise Exception(f"ERROR: couldn't open port: {port}")
#
#         self.setStdMode(self.mode)
#
#     def setStdMode(self, mode):
#         # do I need this?
#         if mode == self.STD_MODE:
#             cmd = [0x42, 0x57, 0x02, 0x00, 0x00, 0x00, 0x01, 0x06]  # hex - packet
#         elif mode == self.DEC_MODE:
#             cmd = [0x42, 0x57, 0x02, 0x00, 0x00, 0x00, 0x04, 0x06]  # dec - string
#         else:
#             raise Exception(f"ERROR: invalid mode {mode}")
#
#         self.mode = mode
#         # data = bytearray(cmd)
#         data = bytes(data)
#         self.serial.write(data)
#         time.sleep(0.1)
#
#     def __del__(self):
#         self.close()
#
#     def close(self):
#         self.serial.close()
#
#     def readString(self):
#         self.serial.flushInput()
#         # tmp = []
#         # tmp = deque(maxlen=64)
#         #
#         # d = b' '
#         # while d != b'\n':
#         #     d = self.serial.read(1)
#         #     tmp.append(d)
#         # try:
#         #     tmp = tmp[:-2]  # get rid of \r\n
#         #     ret = float(b''.join(tmp))
#         # except:
#         #     ret = None
#
#         d = self.serial.read(32)
#         n = d.find("\r\n")
#         if n > 0:
#             s = d[:n]
#             try:
#                 ret = float(s)
#             except:
#                 ret = None
#         else:
#             ret = None
#         return ret
#
#     def readPacket(self):
#         # it looks like it streams data, so no command to measure needed
#         self.serial.flushInput()
#
#         # find header
#         a, b = ' ', ' '
#         # tmp = []
#         tmp = deque(maxlen=64)
#         count = self.retry*11
#
#         a = self.serial.read(1)
#         b = self.serial.read(1)
#         while True:
#             # a = self.serial.read(1)
#             # b = self.serial.read(1)
#             # if len(a) > 0 and len(b) > 0:
#             if a == 0x59 and b == 0x59:
#                 # print('found header')
#                 break
#             if count == 0:
#                 return None
#             a = b
#             b = self.serial.read(1)
#             count -= 1
#
#         raw = self.serial.read(7)
#         pkt = b"\x59\x59" + raw
#         # build a packet (array) of ints
#         # pkt = [ord(a), ord(b)] + list(map(ord, raw))
#         # print('pkt', pkt)
#         try:
#             ret = self.processPkt(pkt)
#         except Exception as e:
#             # print('bad')
#             # print(e)
#             ret = None
#         return ret
#
#     def read(self):
#         """
#         This is the main read() function. The others are automagically selected
#         based off the mode the sensor was set too.
#         STD Mode: return (dist, strength, quality)
#         DEC Mode: return range in meters
#         """
#         if self.mode == self.STD_MODE:
#             ret = self.readPacket()
#         elif self.mode == self.DEC_MODE:
#             ret = self.readString()
#         else:
#             raise Exception(f'ERROR: read() invalid mode {self.mode}')
#
#         # weed out stupid returns ... strings can give crazy numbers
#         if ret > 12.0 or ret < 0.3:
#             ret = None
#
#         return ret
#
#     def processPkt(self, pkt):
#         """
#         packet = [0x59, 0x59, distL, distH, strL, strH, reserved, integration time, checksum]
#
#         Note: the integration time always seems to be 0
#         """
#         # turn string data into array of bytes
#         # pkt = list(map(ord, pkt))
#         if len(pkt) != 9:
#             raise Exception(f"ERROR: packet size {len(pkt)} != 9")
#
#         # check header
#         if pkt[0] != 0x59 or pkt[1] != 0x59:
#             raise Exception("ERROR: bad header in packet")
#
#         # calculate checksum
#         cs = sum(pkt[:8])
#         cs &= 0xff
#         # print('cs', cs, pkt[8])
#
#         if pkt[8] != cs:
#             # print('cs', cs, pkt[8])
#             raise Exception(f"ERROR: bad checksum in packet: {cs} != {pkt[8]}")
#
#         # print('L {} H {}'.format(pkt[2], pkt[3]))
#         # dist = (pkt[2] + (pkt[3] << 8))/100
#         # self.strength = pkt[4] + (pkt[5] << 8)
#         # q    = pkt[7]
#
#         # dist, strength = struct.unpack("<hh", *pkt[2:6])
#         dist, strength = self.unpack(*pkt[2:6])
#
#         # print('ans',dist, st, q)
#
#         return dist/100
