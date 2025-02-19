import unittest

from sage.all import xgcd, Zmod

from ntru_py.sage import ( 
    # ntru sage core objects
    Rx,
    center_modulo,
    convolve, 
    decrypt,
    encrypt,
    gen_keypair,
    invert_modp,
    invert_modq,
    random_message,
    # ntc_api
    sage_generate_testcase,
    sage_validate_testcase,
)

from ntru_py.poly.core import *
from ntru_py.poly.ntc_api import *


class TestPolyNTC(unittest.TestCase):
    N_ITERS = 1

    def test_poly_random_small(self):
        random.seed(0x0123)
        for _ in range(self.N_ITERS):
            ntc = sage_generate_testcase('tiny')
            self.assertTrue(poly_validate_testcase(ntc))

    def test_poly_random_small(self):
        random.seed(0x4567)
        for _ in range(self.N_ITERS):
            ntc = sage_generate_testcase('small')
            self.assertTrue(poly_validate_testcase(ntc))

    def test_poly_random_128bit(self):
        random.seed(0x89ab)
        for _ in range(self.N_ITERS):
            ntc = sage_generate_testcase('128bit')
            self.assertTrue(poly_validate_testcase(ntc))

    def test_poly_random_192bit(self):
        random.seed(0xcdef)
        for _ in range(self.N_ITERS):
            ntc = sage_generate_testcase('192bit')
            self.assertTrue(poly_validate_testcase(ntc))

    def test_poly_random_256bit(self):
        random.seed(0xcafe)
        for _ in range(self.N_ITERS):
            ntc = sage_generate_testcase('256bit')
            self.assertTrue(poly_validate_testcase(ntc))

class TestNtruNTC(unittest.TestCase):

    N_ITERS = 1

    def test_deterministic_seed(self):

        # To tests should produce the same results
        random.seed(42)
        ntc1 = sage_generate_testcase('small')
        random.seed(42)
        ntc2 = sage_generate_testcase('small')

        self.assertEqual(ntc1, ntc2)

    def test_self_random_small(self):
        random.seed(0x0123)
        for _ in range(self.N_ITERS):
            ntc = sage_generate_testcase('tiny')
            self.assertTrue(sage_validate_testcase(ntc))

    def test_self_random_small(self):
        random.seed(0x4567)
        for _ in range(self.N_ITERS):
            ntc = sage_generate_testcase('small')
            self.assertTrue(sage_validate_testcase(ntc))

    def test_self_random_128bit(self):
        random.seed(0x89ab)
        for _ in range(self.N_ITERS):
            ntc = sage_generate_testcase('128bit')
            self.assertTrue(sage_validate_testcase(ntc))

    def test_self_random_192bit(self):
        random.seed(0xcdef)
        for _ in range(self.N_ITERS):
            ntc = sage_generate_testcase('192bit')
            self.assertTrue(sage_validate_testcase(ntc))

    def test_self_random_256bit(self):
        random.seed(0xcafe)
        for _ in range(self.N_ITERS):
            ntc = sage_generate_testcase('256bit')
            self.assertTrue(sage_validate_testcase(ntc))

class TestNtruCore(unittest.TestCase):

    def test_convolve(self):
        f = Rx([3, 1, 4])
        g = Rx([2, 7, 1])
        self.assertEqual(f + g, Rx([5, 8, 5]))
        self.assertEqual(f * g, Rx([6, 23, 18, 29, 4]))
        self.assertEqual(convolve(f, g, 3), Rx([35, 27, 18]))

        # conv with x -> rotate one right
        x = Rx([0, 1, 0]) 
        self.assertEqual(convolve(f, x, 3), Rx([4, 3, 1]))

        # conv with x^2 -> rotate two right
        x2 = Rx([0, 0, 1])
        self.assertEqual(convolve(f, x2, 3), Rx([1, 4, 3]))

    def test_center_modulo(self):
        u = Rx([3,1,4,1,5,9])
        self.assertEqual(center_modulo(u, 10), Rx([3, 1, 4, 1, -5, -1]))

        u = Rx([314, -159])
        self.assertEqual(center_modulo(u, 200), Rx([-86, 41]))

    def test_invert_modp(self):
        N = 7
        p = 3

        f = Rx([1, -1, 1, 1, -1])
        fp = invert_modp(f, N, p)
        self.assertEqual(fp, Rx([0, 1, 0, 0, 2, 0, 1]))
        self.assertEqual(convolve(fp, f, N) % p, Rx([1]))

    def test_invert_modq(self):
        N = 7 
        q = 256

        f = Rx([1, -1, 1, 1, -1])
        fq = invert_modq(f, N, q)
        self.assertEqual(convolve(f, fq, N) % q, Rx([1]))

    def test_enc_dec(self):

        def _check_decryption(N: int, p: int, q: int, d: int, n_tests: int = 100) -> bool:
            for _ in range(n_tests):
                h, f, fp, fq, g = gen_keypair(N, p, q, d) 
                m = random_message(N)
                c, _ = encrypt(m, h, d, N, q)
                m_dec = decrypt(c, f, fp, N, p, q)
                if m != m_dec:
                    return False
            else:
                return True
        
        n_tests = 10

        self.assertTrue(_check_decryption(N=7, p=3, q=64, d=3, n_tests=n_tests))
        self.assertTrue(_check_decryption(N=13, p=3, q=128, d=3, n_tests=n_tests))
        self.assertTrue(_check_decryption(N=509, p=3, q=2048, d=11, n_tests=n_tests))

import random

class TestPyVsSage(unittest.TestCase):

    N_ITERS = 1000
    p = 7
    Rt = Zmod(p)['t']; 
    (t,) = Rt._first_ngens(1)

    def _random_sagepoly(self, n: int):
        return self.Rt([random.randint(0, self.p - 1) for _ in range(n)])

    def sage2raw(self, f) -> list[int]:
        return [ int(x) for x in f ]

    def test_poly_div(self):
        random.seed(42)

        for _ in range(self.N_ITERS):
            a_sage = self._random_sagepoly(10)
            b_sage = 0
            while b_sage == 0:
                b_sage = self._random_sagepoly(10)

            q_sage = a_sage // b_sage
            r_sage = a_sage % b_sage

            a, b = list(map(self.sage2raw, [a_sage, b_sage]))

            q, r = poly_div_mod(a, b, self.p)

            self.assertEqual(r, self.sage2raw(r_sage))
            self.assertEqual(q, self.sage2raw(q_sage))

    def test_poly_xgcd(self):
        random.seed(42)

        for _ in range(self.N_ITERS):

            a_sage = self._random_sagepoly(10)
            b_sage = self._random_sagepoly(10)

            d_sage, x_sage, y_sage = xgcd(a_sage, b_sage)

            a, b = list(map(self.sage2raw, [a_sage, b_sage]))

            d, x, y = poly_xgcd(a, b, self.p)

            self.assertEqual(d, self.sage2raw(d_sage))
            self.assertEqual(x, self.sage2raw(x_sage))
            self.assertEqual(y, self.sage2raw(y_sage))

    def test_is_seed_deterministic(self):
        random.seed(42)
        a_sage = self._random_sagepoly(10)
        random.seed(42)
        b_sage = self._random_sagepoly(10)
        self.assertEqual(a_sage, b_sage)
