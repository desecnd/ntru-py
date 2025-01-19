import unittest

from ntru_py.sage import ( 
    Rx,
    center_modulo,
    convolve, 
    decrypt,
    encrypt,
    gen_keypair,
    invert_modp,
    invert_modq,
    random_message,
)

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
                pk, sk = gen_keypair(N, p, q, d) 
                m = random_message(N)
                c = encrypt(m, pk, d, N, q)
                m_dec = decrypt(c, sk, N, p, q)
                if m != m_dec:
                    return False
            else:
                return True

        self.assertTrue(_check_decryption(N=7, p=3, q=64, d=3, n_tests=100))
        self.assertTrue(_check_decryption(N=13, p=3, q=128, d=3, n_tests=100))
        self.assertTrue(_check_decryption(N=509, p=3, q=2048, d=11, n_tests=100))
