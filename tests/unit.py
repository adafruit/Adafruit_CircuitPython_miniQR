import sys
import unittest
import random

sys.path.append(".")

import adafruit_miniqr

def enc(msg, args = {}):
    qr = adafruit_miniqr.QRCode(**args)
    qr.add_data(msg)
    qr.make()
    return qr.matrix

class TestMiniQR(unittest.TestCase):

    def test_example(self):
        # Confirm the simple test that is in the docs
        msg = b'https://www.adafruit.com'
        qr = adafruit_miniqr.QRCode()
        qr.add_data(msg)
        qr.make()
        with open("tests/test_example.gild") as f:
            self.assertEqual(f.read(), repr(qr.matrix))

    def test_qr_type(self):
        # Confirm that qr_type 1-9 increases the matrix size
        expected_size = [None, 21, 25, 29, 33, 37, 41, 45, 49, 53]
        for t in range(1, 10):
            m = enc(b'abc', dict(qr_type = t))
            self.assertEqual(m.width, m.height)
            self.assertEqual(m.width, expected_size[t])

    def test_qr_error_correct(self):
        # Confirm that error correct L,M,Q,H give different matrix
        matrices = set()
        for ec in adafruit_miniqr.L, adafruit_miniqr.M, adafruit_miniqr.Q, adafruit_miniqr.H:
            m = enc(b'abc', dict(error_correct = ec))
            matrices.add(m)
        self.assertEqual(len(matrices), 4)  # All 4 are unique

    def test_qr_pattern_mask(self):
        # Confirm that pattern_mask 0-7 gives different matrix
        matrices = set()
        qr = adafruit_miniqr.QRCode()
        qr.add_data('test_qr_pattern_mask/1Z')
        for m in range(8):
            qr.make(mask_pattern = m)
            matrices.add(tuple(qr.matrix.buffer))
        self.assertEqual(len(matrices), 8)  # All 8 are unique

    def test_qr_auto(self):
        # Confirm that increasing message size increases the matrix size monotonically
        sizes = []
        for i in range(14): # XXX size 41 crashes
            m = enc(b'aBc!1234' * i)
            sizes.append(m.width)
        self.assertTrue(len(set(sizes)) > 1)
        self.assertEqual(sizes, sorted(sizes))

    def test_qr_str(self):
        # Confirm that bytes and str give the same result
        for s in ("", "abc", "https://www.adafruit.com", "AbCd12"):
            a = enc(s.encode(), {})
            b = enc(s, {})
            self.assertEqual(a.buffer, b.buffer)

    def test_qr_all(self):
        for type in range(1, 10):
            for ec in adafruit_miniqr.L, adafruit_miniqr.M, adafruit_miniqr.Q, adafruit_miniqr.H:
                qr = adafruit_miniqr.QRCode(qr_type = type, error_correct = ec)
                qr.add_data('abc')
                for m in range(8):
                    qr.make(mask_pattern = m)

    def test_qr_maximum(self):
        msg = bytes([random.randrange(32, 127) for i in range(230)])
        m = enc(msg, dict(qr_type = 9))

if __name__ == "__main__":
    unittest.main()
