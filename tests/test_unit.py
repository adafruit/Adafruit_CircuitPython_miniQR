# SPDX-FileCopyrightText: 2024 James Bowman
#
# SPDX-License-Identifier: MIT

import random
import unittest

import adafruit_miniqr


def enc(msg, **args):
    _q = adafruit_miniqr.QRCode(**args)
    _q.add_data(msg)
    _q.make()
    return _q.matrix


class TestMiniQR(unittest.TestCase):
    def test_example(self):
        # Confirm the simple test that is in the docs
        msg = b"https://www.adafruit.com"
        _qr = adafruit_miniqr.QRCode()
        _qr.add_data(msg)
        _qr.make()
        with open("tests/test_example.gild") as _f:
            self.assertEqual(_f.read(), repr(_qr.matrix))

    def test_qr_type(self):
        # Confirm that qr_type 1-9 increases the matrix size
        expected_size = [None, 21, 25, 29, 33, 37, 41, 45, 49, 53]
        for _t in range(1, 10):
            _m = enc(b"abc", qr_type=_t)
            self.assertEqual(_m.width, _m.height)
            self.assertEqual(_m.width, expected_size[_t])

    def test_qr_error_correct(self):
        # Confirm that error correct L,M,Q,H give different matrix
        matrices = set()
        for _ec in (
            adafruit_miniqr.L,
            adafruit_miniqr.M,
            adafruit_miniqr.Q,
            adafruit_miniqr.H,
        ):
            _m = enc(b"abc", error_correct=_ec)
            matrices.add(_m)
        self.assertEqual(len(matrices), 4)  # All 4 are unique

    def test_qr_pattern_mask(self):
        # Confirm that pattern_mask 0-7 gives different matrix
        matrices = set()
        _qr = adafruit_miniqr.QRCode()
        _qr.add_data("test_qr_pattern_mask/1Z")
        for _m in range(8):
            _qr.make(mask_pattern=_m)
            matrices.add(tuple(_qr.matrix.buffer))
        self.assertEqual(len(matrices), 8)  # All 8 are unique

    def test_qr_auto(self):
        # Confirm that increasing message size increases the matrix size monotonically
        sizes = []
        for i in range(29):
            msg = b"aBc!1234" * i
            _m = enc(msg)
            sizes.append(_m.width)
        self.assertTrue(len(set(sizes)) > 1)
        self.assertEqual(sizes, sorted(sizes))

    def test_qr_str(self):
        # Confirm that bytes and str give the same result
        for _s in ("", "abc", "https://www.adafruit.com", "AbCd12"):
            _a = enc(_s.encode())
            _b = enc(_s)
            self.assertEqual(_a.buffer, _b.buffer)

    def test_qr_all(self):
        for _ty in range(1, 10):
            for _ec in (
                adafruit_miniqr.L,
                adafruit_miniqr.M,
                adafruit_miniqr.Q,
                adafruit_miniqr.H,
            ):
                _qr = adafruit_miniqr.QRCode(qr_type=_ty, error_correct=_ec)
                _qr.add_data("abc")
                for _m in range(8):
                    _qr.matrix = None
                    _qr.make(mask_pattern=_m)
                    self.assertTrue(_qr.matrix is not None)

    def test_qr_maximum(self):
        msg = bytes([random.randrange(32, 127) for i in range(230)])
        _a = enc(msg)
        self.assertTrue(_a is not None)


if __name__ == "__main__":
    unittest.main()
