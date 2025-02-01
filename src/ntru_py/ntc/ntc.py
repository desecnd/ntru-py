from dataclasses import dataclass, asdict
import json

NtruTuple = tuple[int, int, int, int]

def unpack_ntru_tuple(ntru_params: dict) -> NtruTuple: 
    N = ntru_params["N"]
    p = ntru_params["p"]
    q = ntru_params["q"]
    d = ntru_params["d"]
    return (N, p, q, d)

def pack_ntru_tuple(N: int, p: int, q: int, d: int) -> dict:
    ntru_params = {
        "N": N, "p": p, "q": q, "d": d
    }
    return ntru_params

NTRU_PARAMS_TINY = {
    "N": 11, "p": 3, "q": 32, "d": 2,
}

NTRU_PARAMS_SMALL = {
    "N": 97, "p": 3, "q": 512, "d": 5,
}

NTRU_PARAMS_128bit = {
    "N": 509, "p": 3, "q": 2048, "d": 11,
}

NTRU_PARAMS_192bit = {
    "N": 677, "p": 3, "q": 2048, "d": 11,
}

NTRU_PARAMS_256bit = {
    "N": 821, "p": 3, "q": 4096, "d": 11,
}

NTRU_PARAMS = {
    "tiny": NTRU_PARAMS_TINY,
    "small": NTRU_PARAMS_SMALL,
    "128bit": NTRU_PARAMS_128bit,
    "192bit": NTRU_PARAMS_192bit,
    "256bit": NTRU_PARAMS_256bit,
}

NTRU_PARAM_TYPES = list(NTRU_PARAMS.keys())

# Representation of the polynomial as list of its coefficients
# 
# Length of the list (`len(PolyCoeffs)`) does not have to be equal to `N`,
# in some cases polynomial can be truncated to contain only the prefix
# 
# e.g. f = x^2 -x + 5   
# will always be stored as [5, -1, 1] for each N > 3
PolyCoeffs = list[int]

@dataclass
class NtruTestCase:
    """Class used for validating produced data between different implementations"""

    # Domain Parameters
    N: int
    p: int
    q: int
    d: int

    # Public Key
    h: PolyCoeffs 

    # Secret Key
    # f: polynomial with coeffs in {-1, 0, 1} such that:
    # * number of +1 is equal to d 
    # * number of -1 is equal to d - 1
    f: PolyCoeffs 

    # -- Plaintext and Ciphertext
    # Plaintext message - Centered polynomial modulo p with coefficients in range [-p//2 : p//2]
    m: PolyCoeffs 
    # Ciphertext - Polynomial modulo q with coefficients in range [0 : q)
    c: PolyCoeffs 

    # -- Inversion Data
    # * Coefficients of fp and fq are NOT centered - all coefficients 
    # Inverse of polynomial f in Fp[X]/(x^N - 1) with coefficients in range [0 : p)
    fp: PolyCoeffs 
    # Inverse of polynomial f in Fq[X]/(x^N - 1) with coefficients in range [0 : q) 
    fq: PolyCoeffs

    # -- Auxiliary Data 
    # r: polynomial with exactly `d` coeffs = +1 and `d` coeffs = -1, rest are = 0
    # * used during message encryption
    r: PolyCoeffs
    # g: polynomial with exactly `d` coeffs = +1 and `d` coeffs = -1, rest are = 0
    # * used during public key generation
    g: PolyCoeffs

def ntc_to_dict(ntc: NtruTestCase) -> dict:
    return asdict(ntc)

def ntc_from_dict(ntc_dict: dict) -> NtruTestCase:
    return NtruTestCase(**ntc_dict)

def ntc_to_str(ntc: NtruTestCase) -> str:
    return json.dumps(ntc_to_dict(ntc))

def ntc_from_str(ntc_str: str) -> NtruTestCase:
    return ntc_from_dict(json.loads(ntc_str))

