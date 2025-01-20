from ntru_py.ntc import NtruTestCase

from .core import * 

def generate_testcase(test_size: str, seed: int = None) -> NtruTestCase:
    """Run tests for  small / medium / big"""

    if test_size == 'small':
        N, p, q, d = (7, 3, 32, 2)
    elif test_size == 'medium':
        N, p, q, d = (91, 3, 512, 5)
    elif test_size == 'big':
        N, p, q, d = (509, 3, 2048, 11)
    else:
        raise ValueError("Incorrect value provided")

    random.seed(seed)

    pk, sk = gen_keypair(N, p, q, d) 
    m = random_message(N)
    c = encrypt(m, pk, d, N, q)
    assert m == decrypt(c, sk, N, p, q)

    raw_coeffs = lambda f: [ int(c) for c in f ]

    f, fp = sk
    ntc = NtruTestCase(
        N, p, q, d, 
        raw_coeffs(pk), 
        raw_coeffs(f),
        raw_coeffs(fp), 
        raw_coeffs(m), 
        raw_coeffs(c)
    ) 

    return ntc


def validate_testcase(ntc: NtruTestCase) -> bool:
    """Run validation test for NtruTestCase and return whether it was successful"""

    N, p, q, d = ntc.N, ntc.p, ntc.q, ntc.d
    h, f, fp, m, c = list(map(Rx, [ntc.h, ntc.f, ntc.fp, ntc.m, ntc.c]))

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
    if not all(x in range(-q // 2, q // 2) for x in h):
        raise ValueError("Coefficients of public h outside of [-q//2, q//2)")
        return False

    # Test for valid encryption of the message
    # Encryption is not deterministic!
    # if c != encrypt(m, h, d, N, q):
    #     raise ValueError("Encryption result of m is not equal given ciphertext c")

    # Test for valid decryption of the message
    if m != decrypt(c, (f, fp), N, p, q):
        raise ValueError("Decryption result of c is not equal given message m")
        return False

    return True
