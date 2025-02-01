import unittest

from ntru_py.poly.core import *
from ntru_py.poly.ntc_api import poly_validate_testcase

class TestPoly(unittest.TestCase):

    def test_poly_xgcd(self):
        # Test when one of polynomials is 0

        a = [1, 5, 3]
        b = [5, 3, 2]
        m = 7

        # Empty argument b
        d, x, y = poly_xgcd(a, [], m)
        self.assertEqual(d, a)
        self.assertEqual(x, POLY_1)
        self.assertEqual(y, POLY_0)

        # Empty argument a
        d, x, y = poly_xgcd([], b, m)
        self.assertEqual(d, b)
        self.assertEqual(x, POLY_0)
        self.assertEqual(y, POLY_1)


    def test_poly_deg_and_truncate(self):

        # Incorrect polynomial representatin of:
        #  3x^3 + 2x^2 + x
        # which degree is equal to 3
        a = [0, 1, 2, 3, 0, 0]
        self.assertEqual(poly_degree(a), 3)
        self.assertEqual(poly_truncate_zeros(a), [0, 1, 2, 3])

        # Incorrect polynomial representation of:
        #  0 
        # which degree is equal to None
        b = [0, 0, 0, 0, 0]
        self.assertEqual(poly_degree(b), None)
        self.assertEqual(poly_truncate_zeros(b), POLY_0)

    def test_poly_sub_mod(self):

        m = 7
        a = [1, 4, 3, 5, 5]
        b = [6, 4, 6, 6, 4]

        ab_diff = [2, 0, 4, 6, 1]
        ba_diff = [5, 0, 3, 1, 6]

        # Make sure that subtraction works both ways
        self.assertEqual(ab_diff, poly_sub_mod(a, b, m))
        self.assertEqual(ba_diff, poly_sub_mod(b, a, m))

        # Make sure that negation works as expected
        self.assertEqual(ba_diff, poly_neg_mod(ab_diff, m))
        self.assertEqual(ab_diff, poly_neg_mod(ba_diff, m))

        # Make sure subtraction works for different lengts
        c = [5, 2]

        ac_diff = [3, 2, 3, 5, 5]
        ca_diff = [4, 5, 4, 2, 2]

        self.assertEqual(ac_diff, poly_sub_mod(a, c, m))
        self.assertEqual(ca_diff, poly_sub_mod(c, a, m))

    def test_wikipedia_example(self):
        N = 11
        p = 3
        q = 32

        m = [-1, 0, 0, 1, -1, 0, 0, 0, -1, 1, 1]
        f = [-1, 1, 1, 0, -1, 0, 1, 0, 0, 1, -1]
        g = [-1, 0, 1, 1, 0, 1, 0, 0, -1, 0, -1]

        fp = [1, 2, 0, 2, 2, 1, 0, 2, 1, 2]
        M = [ 0 ] * (N + 1); M[0], M[N] = (-1, 1)
        my_fp = poly_inv_modprime(f, M, p)
        self.assertEqual(fp, my_fp)

        fq = [5, 9, 6, 16, 4, 15, 16, 22, 20, 18, 30]
        self.assertTrue(2 ** 5 == q)
        my_fq = poly_inv_modexp(f, M, 2, 5)
        self.assertEqual(fq, my_fq)


        pfq = poly_mul_scalar_mod(fq, p, q)
        my_h = poly_circ_conv_mod(g, pfq, N, q)
        my_h = poly_truncate_zeros(my_h)

        # elements above 16 are truncated to -15 in Wikipedia Example
        # h = [8, -7, -10, -12, 12, -8, 15, -13, 12, -13, 16]
        # [ ((x + 16) % 32 - 16) % 32 for x in h ]
        h = [8, 25, 22, 20, 12, 24, 15, 19, 12, 19, 16]
        self.assertEqual(my_h, h)


        r = [-1, 0, 1, 1, 1, -1, 0, -1]

        hr = poly_circ_conv_mod(h, r, N, q)
        hr_m = poly_add_mod(hr, m, q)
        my_c = poly_truncate_zeros(hr_m)

        c = [14, 11, 26, 24, 14, 16, 30, 7, 25, 6, 19]
        self.assertEqual(c, my_c)

        my_m = ntru_decrypt(N, p, q, c, f)
        self.assertEqual(my_m, m)
