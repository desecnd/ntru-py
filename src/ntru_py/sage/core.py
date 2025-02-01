#!/usr/bin/sage -python
# 
# Implementation of simple NTRUEncrypt following the 
# guide: https://latticehacks.cr.yp.to/ntru.html
#
# Minor difference is the treatment of `d` domain parameter as 
# a number of `+1`, therefore polynomials will have 2d nonzero coefficients 

from sage.all import ZZ, Integers, Integer, lift
import random

# Polynomial Ring 
# Rx(coeffs) yiels polynomial object to work with.
#
# Following is the same as "Rx.<x> = ZZ[]"" which is a SageMath syntax.
# In order to use this file as a valid python module, we need to 
# substitute it with preprocessed python syntax:
Rx = ZZ['x']; 
(x,) = Rx._first_ngens(1)

# Number of tries for finding polynomial f
MAX_ITERS = 10_000

def random_poly(N: int, d_pos: int, d_neg: int):
    assert (d_sum := d_pos + d_neg) <= N
    coeffs = [ 0 ] * N

    # Randomly select d_sum elements without replacement
    indices = random.sample(list(range(N)), k=d_sum)

    for idx in indices:
        # Positive only if no more negative indices to select or won a coin toss
        is_positive = (d_neg == 0) or (d_pos != 0 and random.randint(0, 1) == 0)

        if is_positive:
            coeffs[idx] = 1
            d_pos = max(0, d_pos - 1)
        else:
            coeffs[idx] = -1
            d_neg = max(0, d_neg - 1)

    return Rx(coeffs)

def random_message(N: int):
    """Generate random message `m` that is valid for NTRU encryption"""
    # Valid message has coefficients in set {-1, 0, 1}
    coeffs = [ random.randint(-1, 1) for _ in range(N) ]
    return Rx(coeffs)

def convolve(f, g, N: int):
    """Calculte result of f * g over NTRU ring Z[X]/(X^N - 1)"""
    assert max(f.degree(), g.degree()) < N
    return (f * g) % (x**N - 1)

def center_modulo(f, q: int):
    """Return polynomial with coefficients centered modulo q: in [-q//2, q//2]"""
    center_coeff = lambda x: (x + q//2) % q - q//2
    coeffs = [ center_coeff(fc) for fc in f ]
    return Rx(coeffs)

def positive_modulo(f, q: int):
    """Return coefficients of polynomial modulo q: in [0, q)"""
    return Rx([ (fc % q + q) % q for fc in f ])

def invert_modp(f, N: int, p: int):
    """Find fp^-1 such that f * fp^-1 = 1 and p is prime"""
    T = Rx.change_ring(Integers(p)).quotient(x**N - 1)
    return Rx(lift(1 / T(f)))

def invert_modq(f, N: int, q: int):
    """Find fp^-1 such that f * fp^-1 = 1 and q is a power of 2"""
    assert Integer(q).is_power_of(2)
    g = invert_modp(f, N, 2)
    while True:
        gf = convolve(g, f, N)
        r = positive_modulo(gf, q)
        if r == 1: 
            return g

        # 2 - r is actually shortened version from:
        #   g2 = g1 * (1 - 2 * [(f * g - 1) / 2]) = g1 * (2 - f * g1) = 2g1 - fg1^2
        # which comes from the fact that:
        #   f * g1 = 1 + 2r(x) 
        # If we multiply the result by (1 - 2r(x)) we will obtain:
        #   f * g1 * (1 - 2r(x)) = 1 + 4r(x)^2 
        # Which gives 1 mod 4 (exactly what we want)
        g2r = convolve(g, 2 - r, N)
        g = positive_modulo(g2r, q)

    assert convolve(f, g, N) == 1
    return g
    return None

def gen_keypair(N: int, p: int, q: int, d: int) -> tuple:
    """Generate (pk, sk) given NTRU domain parameters"""
    for _ in range(MAX_ITERS):
        try:
            # Find polynomial f that is invertible in Rp = Zp[X]/(X^N - 1) and Rq = Zq[X]/(X^N - 1)
            f = random_poly(N, d, d - 1)
            fp = invert_modp(f, N, p)
            fq = invert_modq(f, N, q)
            break
        except:
            pass
    else:
        raise RuntimeError(f"Cannot find polynomial f in {MAX_ITERS} iterations")

    # Randomly select polynomial g
    g = random_poly(N, d, d)
    # pk = h = p(f_q * g) % q
    # h = center_modulo(p * convolve(fq, g, N), q)
    h = positive_modulo(p * convolve(fq, g, N), q)


    # Return also additional info
    return h, f, fp, fq, g

def encrypt(m, pk, d: int, N: int, q: int):
    """Encrypt polynomial `m` given public key `pk` and NTRU Domain Parameters"""

    # Select random polynomial for encryption
    r = random_poly(N, d, d)

    # Convolve, Add and Center
    hr = convolve(pk, r, N)

    # Return ciphertext and randomly selected polynomial
    return positive_modulo(hr + m, q), r

def decrypt(c, f, fp, N: int, p: int, q: int):
    """Decrypt polymomial `c` given secret key `sk` and NTRU Domain Parameters"""

    # a = [ c * f ]q
    a = center_modulo(convolve(c, f, N), q)

    # Only one time we do center modulo p
    # m = [ a * fp ]p = [ [ c * f ]q * fp ]p
    m = center_modulo(convolve(a, fp, N), p)
    return m
