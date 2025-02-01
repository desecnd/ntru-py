from ntru_py.ntc.ntc import NtruTestCase
from ntru_py.poly.core import *

import math

def poly_validate_testcase(ntc: NtruTestCase) -> bool:

    # M = x^N - 1
    M = [ 0 ] * (ntc.N + 1)
    M[ntc.N], M[0] = (1, -1)

    # Test inversion
    # a) mod p
    my_fp = poly_inv_modprime(ntc.f, M, ntc.p)
    if my_fp != ntc.fp:
        raise ValueError("Fp differ")

    # b) mod q
    q_exp = int(math.log2(ntc.q))
    if 2 ** q_exp != ntc.q:
        raise ValueError("q is not a power of 2")

    my_fq = poly_inv_modexp(ntc.f, M, 2, q_exp)
    if my_fq != ntc.fq:
        raise ValueError("Fq differ")

    # Test encryption
    hr = poly_mul_mod_mod(ntc.h, ntc.r, M, ntc.q)
    hr_m = poly_add_mod(hr, ntc.m, ntc.q)
    my_c = poly_cast_mod(hr_m, ntc.q)
    my_c = poly_truncate_zeros(my_c)
    if my_c != ntc.c:
        raise ValueError("Ciphertexts c differ")

    # Test decryption
    my_m = ntru_decrypt(ntc.N, ntc.p, ntc.q, ntc.c, ntc.f)
    if my_m != ntc.m:
        raise ValueError("Messages m differ")

    return True
