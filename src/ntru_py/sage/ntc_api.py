from ntru_py.ntc.ntc import NtruTestCase, NTRU_PARAMS

from .core import * 

def sage_generate_testcase(param_set: str) -> NtruTestCase:

    allowed_sets = list(NTRU_PARAMS.keys())
    if param_set not in allowed_sets:
        raise ValueError(f"Incorrect param set string provided {param_set}. Possible values are: {allowed_sets}")

    N, p, q, d = NTRU_PARAMS[param_set].values()

    h, f, fp, fq, g = gen_keypair(N, p, q, d) 
    m = random_message(N)
    c, r = encrypt(m, h, d, N, q)
    assert m == decrypt(c, f, fp, N, p, q)

    raw_coeffs = lambda f: [ int(c) for c in f ]

    ntc = NtruTestCase(
        N, p, q, d, 
        raw_coeffs(h), 
        raw_coeffs(f),
        raw_coeffs(m), 
        raw_coeffs(c),
        raw_coeffs(fp),
        raw_coeffs(fq),
        raw_coeffs(r),
        raw_coeffs(g),
    ) 

    return ntc


def sage_validate_testcase(ntc: NtruTestCase) -> bool:
    """Run validation test for NtruTestCase and return whether it was successful"""

    N, p, q, d = ntc.N, ntc.p, ntc.q, ntc.d
    h, f, m, c, fp, fq, r, g = list(map(Rx, 
        [ntc.h, ntc.f, ntc.m, ntc.c, ntc.fp, ntc.fq, ntc.r, ntc.g]
    ))

    # 1. Test if fp is a proper inverse of f 
    # Can give negative modulo result
    if (convolve(f, fp, N) % p + p) % p != Rx([1]):
        raise ValueError("Convolution f * fp is not equal 1")
        return False

    # 2. Test if message m and secret key f have valid input space
    if not all(x in [-1, 0, 1] for x in m):
        raise ValueError("Mesage m has coefficients outside of range [-1 : 1]")
        return False

    if not all(x in [-1, 0, 1] for x in f):
        raise ValueError("Secret key f has coefficients outside of range [-1 : 1]")

    # 3. Test if private key has valid number of +1 and -1
    d_pos = sum(int(x == 1) for x in ntc.f)
    d_neg = sum(int(x == -1) for x in ntc.f)
    # d_zero = sum(int(c == 0) for c in ntc.f)
    # cnt_zero = d_zero == (N - 2 * d + 1)
    if not (d_pos == d and d_neg == d - 1):
        raise ValueError("Wrong number of +1, -1 in polynomial f")
        return False

    # 4. Test if all polynomial coefficients are centered 
    if not all(x in range(0, q) for x in h):
        raise ValueError("Coefficients of public h outside of [0, q)")
        return False

    # Test for valid encryption of the message
    # Encryption is not deterministic!
    # if c != encrypt(m, h, d, N, q):
    #     raise ValueError("Encryption result of m is not equal given ciphertext c")

    # Test for valid decryption of the message
    if m != decrypt(c, f, fp, N, p, q):
        raise ValueError("Decryption result of c is not equal given message m")
        return False

    return True
