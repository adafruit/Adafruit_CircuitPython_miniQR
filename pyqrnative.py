import math

# QRCode for CircuitPython
#
#  Ported from the Javascript library by Sam Curren
#  QRCode for Javascript
#  http://d-project.googlecode.com/svn/trunk/misc/qrcode/js/qrcode.js
#
#  Copyright (c) 2009 Kazuhiko Arase
#  URL: http://www.d-project.com/
#
#  Licensed under the MIT license:
#    http://www.opensource.org/licenses/mit-license.php
#
#  The word "QR Code" is registered trademark of
#  DENSO WAVE INCORPORATED
#    http://www.denso-wave.com/qrcode/faqpatent-e.html


# Consts!
M = 0
L = 1
H = 2
Q = 3

_MODE_8BIT_BYTE = 1 << 2
_PAD0 = 0xEC
_PAD1 = 0x11

# Optimized polynomial helpers

def _glog(n):
    if (n < 1):
        raise ValueError("glog(" + n + ")")
    return LOG_TABLE[n];

def _gexp(n):
    while n < 0:
        n += 255
    while n >= 256:
        n -= 255
    return EXP_TABLE[n];

EXP_TABLE = b'\x01\x02\x04\x08\x10 @\x80\x1d:t\xe8\xcd\x87\x13&L\x98-Z\xb4u\xea\xc9\x8f\x03\x06\x0c\x180`\xc0\x9d\'N\x9c%J\x945j\xd4\xb5w\xee\xc1\x9f#F\x8c\x05\n\x14(P\xa0]\xbai\xd2\xb9o\xde\xa1_\xbea\xc2\x99/^\xbce\xca\x89\x0f\x1e<x\xf0\xfd\xe7\xd3\xbbk\xd6\xb1\x7f\xfe\xe1\xdf\xa3[\xb6q\xe2\xd9\xafC\x86\x11"D\x88\r\x1a4h\xd0\xbdg\xce\x81\x1f>|\xf8\xed\xc7\x93;v\xec\xc5\x973f\xcc\x85\x17.\\\xb8m\xda\xa9O\x9e!B\x84\x15*T\xa8M\x9a)R\xa4U\xaaI\x929r\xe4\xd5\xb7s\xe6\xd1\xbfc\xc6\x91?~\xfc\xe5\xd7\xb3{\xf6\xf1\xff\xe3\xdb\xabK\x961b\xc4\x957n\xdc\xa5W\xaeA\x82\x192d\xc8\x8d\x07\x0e\x1c8p\xe0\xdd\xa7S\xa6Q\xa2Y\xb2y\xf2\xf9\xef\xc3\x9b+V\xacE\x8a\t\x12$H\x90=z\xf4\xf5\xf7\xf3\xfb\xeb\xcb\x8b\x0b\x16,X\xb0}\xfa\xe9\xcf\x83\x1b6l\xd8\xadG\x8e\x01'

LOG_TABLE = b'\x00\x00\x01\x19\x022\x1a\xc6\x03\xdf3\xee\x1bh\xc7K\x04d\xe0\x0e4\x8d\xef\x81\x1c\xc1i\xf8\xc8\x08Lq\x05\x8ae/\xe1$\x0f!5\x93\x8e\xda\xf0\x12\x82E\x1d\xb5\xc2}j\'\xf9\xb9\xc9\x9a\txM\xe4r\xa6\x06\xbf\x8bbf\xdd0\xfd\xe2\x98%\xb3\x10\x91"\x886\xd0\x94\xce\x8f\x96\xdb\xbd\xf1\xd2\x13\\\x838F@\x1eB\xb6\xa3\xc3H~nk:(T\xfa\x85\xba=\xca^\x9b\x9f\n\x15y+N\xd4\xe5\xacs\xf3\xa7W\x07p\xc0\xf7\x8c\x80c\rgJ\xde\xed1\xc5\xfe\x18\xe3\xa5\x99w&\xb8\xb4|\x11D\x92\xd9# \x89.7?\xd1[\x95\xbc\xcf\xcd\x90\x87\x97\xb2\xdc\xfc\xbea\xf2V\xd3\xab\x14*]\x9e\x84<9SGmA\xa2\x1f-C\xd8\xb7{\xa4v\xc4\x17I\xec\x7f\x0co\xf6l\xa1;R)\x9dU\xaa\xfb`\x86\xb1\xbb\xcc>Z\xcbY_\xb0\x9c\xa9\xa0Q\x0b\xf5\x16\xebzu,\xd7O\xae\xd5\xe9\xe6\xe7\xad\xe8t\xd6\xf4\xea\xa8PX\xaf'


class QRCode:
    def __init__(self, *, qr_type=None, error_correct=L):
        self.type = qr_type
        self.ECC = error_correct
        self.matrix = None
        self.moduleCount = 0
        self.dataCache = None
        self.dataList = []

    def addData(self, data):
        self.dataList.append(data)
        datalen = sum([len(x) for x in self.dataList])
        if not self.type:
            for qr_type in range(1,6):
                rsBlocks = _getRSBlocks(qr_type, self.ECC)
                totalDataCount = 0;
                for block in rsBlocks:
                    totalDataCount += block['data']
                if totalDataCount > datalen:
                    self.type = qr_type
                    break
        self.dataCache = None

    def make(self, *, test=False, maskPattern=0):
        self.moduleCount = self.type * 4 + 17
        self.matrix = QRBitMatrix(self.moduleCount, self.moduleCount)
                
        self.setupPositionProbePattern(0, 0)
        self.setupPositionProbePattern(self.moduleCount - 7, 0)
        self.setupPositionProbePattern(0, self.moduleCount - 7)
        self.setupPositionAdjustPattern()
        self.setupTimingPattern()
        self.setupTypeInfo(test, maskPattern)

        if (self.type >= 7):
            self.setupTypeNumber(test)

        if (self.dataCache == None):
            self.dataCache = QRCode.createData(self.type, self.ECC, self.dataList)
        self.mapData(self.dataCache, maskPattern)

    def setupPositionProbePattern(self, row, col):
        for r in range(-1, 8):
            if (row + r <= -1 or self.moduleCount <= row + r): continue
            for c in range(-1, 8):
                if (col + c <= -1 or self.moduleCount <= col + c): continue
                if ( (0 <= r and r <= 6 and (c == 0 or c == 6) )
                        or (0 <= c and c <= 6 and (r == 0 or r == 6) )
                        or (2 <= r and r <= 4 and 2 <= c and c <= 4) ):
                    self.matrix[row + r, col + c] = True
                else:
                    self.matrix[row + r, col + c] = False

    def setupTimingPattern(self):
        for r in range(8, self.moduleCount - 8):
            if (self.matrix[r,6] != None):
                continue
            self.matrix[r,6] = (r % 2 == 0)

        for c in range(8, self.moduleCount - 8):
            if (self.matrix[6,c] != None):
                continue
            self.matrix[6,c] = (c % 2 == 0)

    def setupPositionAdjustPattern(self):
        pos = QRUtil.getPatternPosition(self.type)

        for i in range(len(pos)):
            for j in range(len(pos)):
                row = pos[i]
                col = pos[j]

                if (self.matrix[row,col] != None):
                    continue

                for r in range(-2, 3):
                    for c in range(-2, 3):
                        if abs(r) == 2 or abs(c) == 2 or (r == 0 and c == 0):
                            self.matrix[row + r, col + c] = True
                        else:
                            self.matrix[row + r, col + c] = False

    def setupTypeNumber(self, test):
        bits = QRUtil.getBCHTypeNumber(self.type)

        for i in range(18):
            mod = (not test and ( (bits >> i) & 1) == 1)
            self.matrix[i // 3, i % 3 + self.moduleCount - 8 - 3] = mod

        for i in range(18):
            mod = (not test and ( (bits >> i) & 1) == 1)
            self.matrix[i % 3 + self.moduleCount - 8 - 3, i // 3] = mod

    def setupTypeInfo(self, test, maskPattern):
        data = (self.ECC << 3) | maskPattern
        bits = QRUtil.getBCHTypeInfo(data)

        #// vertical
        for i in range(15):
            mod = (not test and ( (bits >> i) & 1) == 1)
            if (i < 6):
                self.matrix[i, 8] = mod
            elif (i < 8):
                self.matrix[i + 1, 8] = mod
            else:
                self.matrix[self.moduleCount - 15 + i, 8] = mod

        #// horizontal
        for i in range(15):
            mod = (not test and ( (bits >> i) & 1) == 1);
            if (i < 8):
                self.matrix[8, self.moduleCount - i - 1] = mod
            elif (i < 9):
                self.matrix[8, 15 - i - 1 + 1] = mod
            else:
                self.matrix[8, 15 - i - 1] = mod

        #// fixed module
        self.matrix[self.moduleCount - 8, 8] = (not test)

    def mapData(self, data, maskPattern):
        inc = -1
        row = self.moduleCount - 1
        bitIndex = 7
        byteIndex = 0

        for col in range(self.moduleCount - 1, 0, -2):
            if (col == 6): col-=1

            while (True):
                for c in range(2):
                    if (self.matrix[row, col - c] == None):
                        dark = False
                        if (byteIndex < len(data)):
                            dark = ( ( (data[byteIndex] >> bitIndex) & 1) == 1)
                        mask = QRUtil.getMask(maskPattern, row, col - c)
                        if (mask):
                            dark = not dark
                        self.matrix[row, col - c] = dark
                        bitIndex-=1
                        if (bitIndex == -1):
                            byteIndex+=1
                            bitIndex = 7
                row += inc
                if (row < 0 or self.moduleCount <= row):
                    row -= inc
                    inc = -inc
                    break

    @staticmethod
    def createData(type, ECC, dataList):
        rsBlocks = _getRSBlocks(type, ECC)

        buffer = QRBitBuffer();

        for i in range(len(dataList)):
            data = dataList[i]
            buffer.put(_MODE_8BIT_BYTE, 4)
            buffer.put(len(data), 8)
            for i in range(len(data)):
                buffer.put(data[i], 8)

        #// calc num max data.
        totalDataCount = 0;
        for i in range(len(rsBlocks)):
            totalDataCount += rsBlocks[i]['data']

        if (buffer.getLengthInBits() > totalDataCount * 8):
            raise RuntimeError("Code length overflow: %d > %d" % (buffer.getLengthInBits(), totalDataCount * 8))

        #// end code
        if (buffer.getLengthInBits() + 4 <= totalDataCount * 8):
            buffer.put(0, 4)

        #// padding
        while (buffer.getLengthInBits() % 8 != 0):
            buffer.putBit(False)

        #// padding
        while (True):
            if (buffer.getLengthInBits() >= totalDataCount * 8):
                break
            buffer.put(_PAD0, 8)
            if (buffer.getLengthInBits() >= totalDataCount * 8):
                break
            buffer.put(_PAD1, 8)

        return QRCode.createBytes(buffer, rsBlocks)

    @staticmethod
    def createBytes(buffer, rsBlocks):
        offset = 0
        maxDcCount = 0
        maxEcCount = 0

        dcdata = [0] * len(rsBlocks)
        ecdata = [0] * len(rsBlocks)

        for r in range(len(rsBlocks)):

            dcCount = rsBlocks[r]['data']
            ecCount = rsBlocks[r]['total'] - dcCount

            maxDcCount = max(maxDcCount, dcCount)
            maxEcCount = max(maxEcCount, ecCount)

            dcdata[r] = [0 for x in range(dcCount)]

            for i in range(len(dcdata[r])):
                dcdata[r][i] = 0xff & buffer.buffer[i + offset]
            offset += dcCount

            rsPoly = QRUtil.getErrorCorrectPolynomial(ecCount)
            modPoly = QRPolynomial(dcdata[r], rsPoly.getLength() - 1)

            while True:
                if modPoly.getLength() - rsPoly.getLength() < 0:
                    break
                ratio = _glog(modPoly.get(0) ) - _glog(rsPoly.get(0) )
                num = [0 for x in range(modPoly.getLength())]
                for i in range(modPoly.getLength()):
                    num[i] = modPoly.get(i)
                for i in range(rsPoly.getLength()):
                    num[i] ^= _gexp(_glog(rsPoly.get(i) ) + ratio)
                modPoly = QRPolynomial(num, 0)

            ecdata[r] = [0 for x in range(rsPoly.getLength()-1)]
            for i in range(len(ecdata[r])):
                modIndex = i + modPoly.getLength() - len(ecdata[r])
                if (modIndex >= 0):
                    ecdata[r][i] = modPoly.get(modIndex)
                else:
                    ecdata[r][i] = 0

        totalCodeCount = 0
        for i in range(len(rsBlocks)):
            totalCodeCount += rsBlocks[i]['total']

        data = [None] * totalCodeCount
        index = 0

        for i in range(maxDcCount):
            for r in range(len(rsBlocks)):
                if (i < len(dcdata[r])):
                    data[index] = dcdata[r][i]
                    index+=1

        for i in range(maxEcCount):
            for r in range(len(rsBlocks)):
                if (i < len(ecdata[r])):
                    data[index] = ecdata[r][i]
                    index+=1

        return data

class QRUtil(object):
    PATTERN_POSITION_TABLE = [b'', b'\x06\x12', b'\x06\x16', b'\x06\x1a', b'\x06\x1e', b'\x06"', b'\x06\x16&', b'\x06\x18*', b'\x06\x1a.', b'\x06\x1c2']

    G15 = 0b10100110111
    G18 = 0b1111100100101
    G15_MASK = 0b101010000010010

    @staticmethod
    def getBCHTypeInfo(data):
        d = data << 10;
        while (QRUtil.getBCHDigit(d) - QRUtil.getBCHDigit(QRUtil.G15) >= 0):
            d ^= (QRUtil.G15 << (QRUtil.getBCHDigit(d) - QRUtil.getBCHDigit(QRUtil.G15) ) )

        return ( (data << 10) | d) ^ QRUtil.G15_MASK
    @staticmethod
    def getBCHTypeNumber(data):
        d = data << 12;
        while (QRUtil.getBCHDigit(d) - QRUtil.getBCHDigit(QRUtil.G18) >= 0):
            d ^= (QRUtil.G18 << (QRUtil.getBCHDigit(d) - QRUtil.getBCHDigit(QRUtil.G18) ) )
        return (data << 12) | d
    @staticmethod
    def getBCHDigit(data):
        digit = 0;
        while (data != 0):
            digit += 1
            data >>= 1
        return digit
    @staticmethod
    def getPatternPosition(type):
        return QRUtil.PATTERN_POSITION_TABLE[type - 1]
    @staticmethod
    def getMask(mask, i, j):
        if mask == 0: return (i + j) % 2 == 0
        if mask == 1: return i % 2 == 0
        if mask == 2: return j % 3 == 0
        if mask == 3: return (i + j) % 3 == 0
        if mask == 4: return (math.floor(i / 2) + math.floor(j / 3) ) % 2 == 0
        if mask == 5: return (i * j) % 2 + (i * j) % 3 == 0
        if mask == 6: return ( (i * j) % 2 + (i * j) % 3) % 2 == 0
        if mask == 7: return ( (i * j) % 3 + (i + j) % 2) % 2 == 0
        raise Exception("bad maskPattern:" + mask);
    @staticmethod
    def getErrorCorrectPolynomial(errorCorrectLength):
        a = QRPolynomial([1], 0);
        for i in range(errorCorrectLength):
            a = a.multiply(QRPolynomial([1, _gexp(i)], 0) )
        return a

class QRPolynomial:
    def __init__(self, num, shift):
        if (len(num) == 0):
            raise Exception(num.length + "/" + shift)

        offset = 0

        while offset < len(num) and num[offset] == 0:
            offset += 1

        self.num = [0 for x in range(len(num)-offset+shift)]
        for i in range(len(num) - offset):
            self.num[i] = num[i + offset]

    def get(self, index):
        return self.num[index]
    def getLength(self):
        return len(self.num)
    def multiply(self, e):
        num = [0 for x in range(self.getLength() + e.getLength() - 1)]

        for i in range(self.getLength()):
            for j in range(e.getLength()):
                num[i + j] ^= _gexp(_glog(self.get(i) ) + _glog(e.get(j) ) )

        return QRPolynomial(num, 0)

_QRRS_BLOCK_TABLE = (b'\x01\x1a\x10', b'\x01\x1a\x13', b'\x01\x1a\t', b'\x01\x1a\r', b'\x01,\x1c', b'\x01,"', b'\x01,\x10', b'\x01,\x16', b'\x01F,', b'\x01F7', b'\x02#\r', b'\x02#\x11', b'\x022 ', b'\x01dP', b'\x04\x19\t', b'\x022\x18', b'\x02C+', b'\x01\x86l', b'\x02!\x0b\x02"\x0c', b'\x02!\x0f\x02"\x10', b'\x04+\x1b', b'\x02VD', b'\x04+\x0f', b'\x04+\x13', b'\x041\x1f', b'\x02bN', b"\x04'\r\x01(\x0e", b'\x02 \x0e\x04!\x0f', b"\x02<&\x02='", b'\x02ya', b'\x04(\x0e\x02)\x0f', b'\x04(\x12\x02)\x13', b'\x03:$\x02;%', b'\x02\x92t', b'\x04$\x0c\x04%\r', b'\x04$\x10\x04%\x11')
    
def _getRSBlocks(qr_type, ECC):
    rsBlock = _QRRS_BLOCK_TABLE[(qr_type - 1) * 4 + ECC]

    length = len(rsBlock) // 3
    list = []
    for i in range(length):
        count = rsBlock[i * 3 + 0]
        totalCount = rsBlock[i * 3 + 1]
        dataCount  = rsBlock[i * 3 + 2]
        block = {'total' : totalCount, 'data' : dataCount}
        for j in range(count):
            list.append(block)
    return list

class QRBitMatrix:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        if width > 60:
            raise ValueError("Max 60 bits wide:", width)
        self.buffer = [0] * self.height * 2
        self.used = [0] * self.height * 2

    def __repr__(self):
        s = ""
        for y in range(self.height):
            for x in range(self.width):
                if self[x, y]:
                    s += 'X'
                else:
                    s += '.'
            s += '\n'
        return s

    def __getitem__(self, key):
        x, y = key
        if y > self.width: raise ValueError()
        i = 2*x + (y // 30)
        j = y % 30
        if not self.used[i] & (1 << j):
            return None
        return self.buffer[i] & (1 << j)

    def __setitem__(self, key, value):
        x, y = key
        if y > self.width: raise ValueError()
        i = 2*x + (y // 30)
        j = y % 30
        if value:
            self.buffer[i] |= 1 << j
        else:
            self.buffer[i] &= ~(1 << j)
        self.used[i] |= 1 << j # buffer item was set

class QRBitBuffer:
    def __init__(self):
        self.buffer = []
        self.length = 0

    def __repr__(self):
        return ".".join([str(n) for n in self.buffer])

    def get(self, index):
        i = index // 8
        return self.buffer[i] & (1 << (7 - index % 8))

    def put(self, num, length):
        for i in range(length):
            self.putBit(num & (1 << (length - i - 1)))

    def getLengthInBits(self):
        return self.length

    def putBit(self, bit):
        i = self.length // 8
        if len(self.buffer) <= i:
            self.buffer.append(0)
        if bit:
            self.buffer[i] |= (0x80 >> (self.length % 8) )
        self.length+=1
