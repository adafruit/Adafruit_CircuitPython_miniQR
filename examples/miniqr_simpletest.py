import sys
import hashlib
import adafruit_miniqr

# For drawing filled rectangles to the console:
out = sys.stdout
WHITE = "\x1b[1;47m  \x1b[40m"
BLACK = "  "

def print_QR(matrix):
    # white 4-pixel border at top
    for _ in range(4):
        for _ in range(matrix.width+8):
            out.write(WHITE)
        print()
    for y in range(matrix.height):
        out.write(WHITE*4)   # 4-pixel border to left
        for x in range(matrix.width):
            if matrix[x, y]:
                out.write(BLACK)
            else:
                out.write(WHITE)
        out.write(WHITE*4)   # 4-pixel bporder to right
        print()
    # white 4-pixel border at bottom
    for _ in range(4):
        for _ in range(matrix.width+8):
            out.write(WHITE)
        print()

qr = adafruit_miniqr.QRCode(qr_type=3, error_correct=adafruit_miniqr.H)
qr.add_data(b'https://www.adafruit.com')
qr.make()

matrix = qr.matrix
matrix_s = str(matrix)
print(matrix_s)
hashed = hashlib.md5(matrix_s.encode('utf-8')).hexdigest()
print(hashed)
if hashed != "7b260ec364d4938cc7b7a18af07cfc61":
    raise Exception("wrong hash")

print_QR(qr.matrix)
