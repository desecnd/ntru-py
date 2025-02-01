import random
import math
    
# Constant polynomial equal to 1
POLY_1 = [1]
# Constant polynomial equal to 0 
# poly_deg(POLY_ZERO) == None
POLY_0 = []

def poly_degree(a: list[int]) -> int | None:
    # Go from top (len(a) - 1), down to bottom (0)
    for i in range(len(a) - 1, -1, -1):
        # Return first index that is non-zero
        if a[i] != 0:
            return i
    else:
        return None

def poly_truncate_zeros(a: list[int]) -> list[int]:
    deg = poly_degree(a)
    # Polynomial equal to 0 has undef
    if deg is None:
        return POLY_0
    else:
        return a[:deg + 1]

def poly_add_mod(a: list[int], b: list[int], m: int) -> list[int]:

    if len(a) >= len(b):
        c = [ x % m for x in a ] 
        for i in range(len(b)): c[i] = (c[i] + b[i]) % m
    else: 
        # b is larger than a
        c = [ x % m for x in b ] 
        for i in range(len(a)): c[i] = (c[i] + a[i]) % m

    return c

def poly_sub_mod(a: list[int], b: list[int], m: int) -> list[int]:
    """Subtract `b` from `a` modulo `m` with arbitrary polynomial degrees"""

    if len(a) >= len(b):
        c = [ x % m for x in a ] 
        for i in range(len(b)): c[i] = (c[i] - b[i]) % m
    else: 
        # b is larger than a, but we have to negate it first
        c = [ -x % m for x in b ] 
        for i in range(len(a)): c[i] = (c[i] + a[i]) % m

    return c

def poly_check_valid_lc(a: list[int]):
    if a == POLY_0 or a[-1] == 0:
        raise ValueError("Leading coefficient of a polynomial must be non-zero.")

def poly_make_monic_mod(a: list[int], m: int) -> list[int]:
    """Make polynomial `a` monic modulo `m`. If a is already monic then do nothing.

    :param a: Polynomial with leading coefficient != 0
    :type a: list[int]
    :param m: Modulus
    :type m: int
    :return: Polynomial `a` transformed to monic form (leading coefficient is 1)
    :rtype: list[int]
    :raises: ValueError when a is POLY_0 or leading coefficient is 0
    """

    # No special handling for 0 polynomial
    poly_check_valid_lc(a)

    # If a is already monic - do nothing
    if a[-1] == 1:
        return a

    # Leading coefficient inverse
    lc_inv = pow(a[-1], -1, m)

    # Multiply all coeffs by leading coefficient inverse
    return poly_mul_scalar_mod(a, lc_inv, m)


def poly_mul_mod(a: list[int], b: list[int], m: int):
    # Product of 2 polynomials of degree deg_a, and deg_b 
    # will have degree equal to at most deg_a + deg_b - 1
    c = [ 0 ] * (len(a) + len(b) - 1)
    for i, aa in enumerate(a):
        for j, bb in enumerate(b):
            c[i + j] += aa * bb
            c[i + j] %= m
    return c

def poly_xgcd(a: list[int], b: list[int], m: int) -> tuple[list[int], list[int], list[int]]:

    # Edge cases
    if a == POLY_0:
        return (b, POLY_0, POLY_1)
    if b == POLY_0:
        return (a, POLY_1, POLY_0)
    
    # Check leading coefficients of both polynomials
    poly_check_valid_lc(a)
    poly_check_valid_lc(b)
    
    # No need to deepcopy, as poly_div_mod does its own deepcopy
    r_last, r = (a, b)
    # s_ = 1, s = 0
    s_last, s = (POLY_1, POLY_0)
    # t_ = 0, t = 1
    t_last, t = (POLY_0, POLY_1)

    # Same as r == 0 or equivalent r == []
    while r != POLY_0:

        # Requires correct polynomial form (lc != 0)
        q, r_next = poly_div_mod(r_last, r, m)

        # X_last = X
        # X = X_last - q * X
        r_last, r = r[:], r_next 
        # Does not require correct polynomial form (possibly lc == 0)
        s_last, s = s[:], poly_sub_mod(s_last, poly_mul_mod(q, s, m), m)
        t_last, t = t[:], poly_sub_mod(t_last, poly_mul_mod(q, t, m), m)
    
    # r is already truncated in each poly_div_mod step but both
    # poly_sub_mod and poly_mul_mod do not check for padded zeros
    # therefore we have to truncate them manually
    s_last = poly_truncate_zeros(s_last) 
    t_last = poly_truncate_zeros(t_last) 

    # Transform GCD into monic polynomial, otherwise the result is not consistent
    d = poly_make_monic_mod(r_last, m)
    # if we make d monic, we also have to multiply s and t by the same 
    # inverse of leading coeficient, otherwise s*a + b*t = d no longer holds.
    lc_inv = pow(r_last[-1], -1, m)
    s = poly_mul_scalar_mod(s_last, lc_inv, m)
    t = poly_mul_scalar_mod(t_last, lc_inv, m)

    return d, s, t

def poly_mul_scalar_mod(a: list[int], v: int, m: int):
    return [ aa * v % m for aa in a ]

def poly_inv_modprime(a: list[int], M: list[int], p: int) -> list[int]:
    """Calculate `a^-1` in QuotientRing with modulus `M` over field of integers modulo prime `p` - `Z/pZ`"""
    d, a_inv, _ = poly_xgcd(a, M, p)

    if len(d) != 1:
        raise ValueError("Polynomials are not coprime")
    else:
        # Returned polynomial is Monic, so if len == 1, d[0] is 1
        assert d == POLY_1

    # Make sure that the (a * a_inv % Q) % p is equal to 1
    # so the element inversion is calculated correctly
    assert POLY_1 == poly_div_mod(poly_mul_mod(a, a_inv, p), M, p)[1]

    return a_inv 

def poly_cast_mod(a: list[int], m: int) -> list[int]:
    return [ x % m for x in a ]

def poly_mul_mod_mod(a: list[int], b: list[int], M: list[int], m: int) -> list[int]:
    ab = poly_mul_mod(a, b, m)
    _, ab_r = poly_div_mod(ab, M, m)
    return ab_r 

def poly_circ_conv_mod(a: list[int], b: list[int], N: int, m: int) -> list[int]:
    """Circular convolution modulo (X^N - 1)"""
    new_coeffs = [ 0 ] * N
    for i, aa in enumerate(a):
        for j, bb in enumerate(b):
            new_coeffs[(i + j) % N] += aa * bb
            new_coeffs[(i + j) % N] %= m
    return new_coeffs

def poly_neg_mod(a: list[int], m: int) -> list[int]:
    return [ -x % m for x in a ]

def poly_inv_modexp(a: list[int], M: list[int], p: int, e: int):
    # inverse in Fp^1 
    b = poly_inv_modprime(a, M, p)
    m = p ** e

    for _ in range(e):
        # r = a * b % M = 1 + p * h(x)  (mod M(x))
        r = poly_div_mod(poly_mul_mod(a, b, m), M, m)[1]

        # c = 2 - r 
        c = poly_sub_mod([2], r, m)

        # a * b = a * b * (2 - r) = 1 - p^2 * h(x)^2 = 1 (mod p^2)
        # Same as b = conv_mod(a, b, m)
        b = poly_div_mod(poly_mul_mod(b, c, m), M, m)[1]

    # Make sure that the calculated inversion is valid
    assert POLY_1 == poly_div_mod(poly_mul_mod(a, b, m), M, m)[1]

    return b


def poly_div_mod(a: list[int], b: list[int], m: int) -> tuple[list[int], list[int]]:
    """Divide polynomials over field of integers modulo `m` - `Z/mZ` and return quotient and reminder 

    :param a: Polynomial in ascending order with non-zero leading coefficient
    :type a: list[int]
    :param b: Polynomial in ascending order with non-zero leading coefficient
    :type b: list[int]
    :param m: Modulus of the field 
    :type m: int
    """

    # Case when a = qb + r , for a < b, then: q = 0, r = a
    if len(a) < len(b):
        return POLY_0, a

    # Check leading coefficient
    poly_check_valid_lc(b)

    deg_a = len(a) - 1
    deg_b = len(b) - 1

    # DeepCopy a into r
    r = [ coeff for coeff in a ]

    # Polynomial `q` will be populated in reverse throughout the algorithm
    q = [ 0 ] * (deg_a - deg_b + 1)

    # Modular inverse of the leading coefficient of b (highest term) modulo m.
    # It is used for division and it will not change throughout the iterations as b is constant.
    u = pow(b[-1], -1, m)

    # We reduce the degree of r each iteration
    # In ith iteration we "eliminate" the r[d] coefficient
    for deg_r in range(deg_a, deg_b - 1, -1):

        # We can skip this case, as it will be redundant computations
        if r[deg_r] == 0:
            continue

        # in i-th iteration we are eliminating r[deg_r] and calculating q[deg_r - deg_b] = q[deg_q]
        deg_q = deg_r - deg_b

        # Calculate the quotient of highest terms of r and b
        v = r[deg_r] * u % m

        # Clear the highest term of the reminder
        r[deg_r] = 0

        # Mutplication by v * x^deg_r is the same as multiplication of each coefficient of `b` 
        # by value `v` and then shift by `deg_r` up.
        #
        # We are omitting b_i == deg_b on purpose as it is already implemented above as r[deg_r] = 0
        for bi in range(deg_b):
            # Calculate shifted results
            r[bi + deg_q] -= b[bi] * v
            r[bi + deg_q] %= m

        # Append the coefficient to q
        q[deg_q] = v

    # r should have all coefficients above degree of b equal to 0
    assert all(x == 0 for x in r[deg_b:])

    # remove all padding zeros from r
    i_r = deg_b - 1
    while i_r >= 0:
        if r[i_r] != 0:
            break
        i_r -= 1
        
    return q, r[:i_r + 1]

def poly_center_mod(f: int, m: int):
    center_coeff = lambda x: (x + m//2) % m - m//2
    coeffs = [ center_coeff(fc) for fc in f ]
    return coeffs

def ntru_random_poly(N: int, d_pos: int, d_neg: int):
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

    return coeffs

def ntru_random_message(N: int, p: int):
    m = [ random.randint(-(p//2), p//2) for _ in range(N) ]
    return poly_truncate_zeros(m)

def ntru_encrypt(N: int, q: int, d: int, m: list[int], h: list[int]) -> list[int]:
    # Select random polynomial for encryption
    r = ntru_random_poly(N, d, d)

    hr = poly_circ_conv_mod(h, r, N, q)
    hr_m = poly_add_mod(hr, m, q)

    return poly_truncate_zeros(hr_m)


def ntru_decrypt(N: int, p: int, q: int, c: list[int], f: list[int]) -> list[int]:
    # a = [ c * f ]q
    a = poly_circ_conv_mod(c, f, N, q)
    a = poly_center_mod(a, q)

    # Create NTRU quotient ring modulus M(x)
    # for creating inversion
    M = [ 0 ] * (N + 1)
    M[N], M[0] = (1, -1)
    fp = poly_inv_modprime(f, M, p)

    b = poly_circ_conv_mod(a, fp, N, p)
    m = poly_center_mod(b, p)
    return poly_truncate_zeros(m)


def ntru_keygen(N: int, p: int, q: int, d: int, n_iters: int = 10000) -> tuple[list[int], list[int]]:
    q_exp = int(math.log2(q))
    if 2 ** q_exp != q: 
        raise ValueError("Given NTRU parameter q is not a power of 2.")

    # Create NTRU quotient ring modulus M(x)
    M = [ 0 ] * (N + 1)
    M[N], M[0] = (1, -1)

    for _ in range(n_iters):
        try:
            f = ntru_random_poly(N, d, d - 1)
            fq = poly_inv_modexp(f, M, 2, q_exp)
            fp = poly_inv_modprime(f, M, p)
            break
        except:
            pass
    else:
        raise ValueError(f"Cannot find polynomial f that has inverses fp, fq in {n_iters} iterations. Try to change parameters or increase the number of iterations.")
        
    g = ntru_random_poly(N, d, d)
    # h = p f_q * g 
    pfq = poly_mul_scalar_mod(fq, p, q)
    h = poly_circ_conv_mod(g, pfq, N, q)

    hf_trunc = tuple(map(poly_truncate_zeros, [h, f]))
    return hf_trunc