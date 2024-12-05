# Requires python 3.11+ 
from typing import Self 

class PolyNTRU:
    """Truncated Polynomial of N-th degree with Integer Coefficients and Circular Multiplication (Mod x^N - 1)"""

    def __init__(self, coeffs: list[int]):
        self.coeffs = coeffs

    @property
    def deg(self) -> int:
        """Degree of the polynomial"""
        return len(self.coeffs)

    def __eq__(self, other) -> bool:
        # Two polynomials are equal if they have equal coefficients
        return self.coeffs == other.coeffs

    def __add__(self, other) -> Self:
        # TODO: graceful exit
        assert self.deg == other.deg

        new_coeffs = [
            a + b for a, b in zip(self.coeffs, other.coeffs)
        ]
        return PolyNTRU(new_coeffs)

    def __mul__(self, other) -> Self:
        """Return circular convolution of `self` and `other`. Result is equal to regular polynomial multiplication modulo x^n - 1"""

        n = self.deg

        new_coeffs = [ 0 ] * n
        for i, a in enumerate(self.coeffs):
            for j, b in enumerate(other.coeffs):
                new_coeffs[(i + j) % n] += a * b

        return PolyNTRU(new_coeffs)


    def center(self, modulus: int) -> Self:
        """Return polynomial centered according to `modulus` m - with coeffcients in range `[-m/2, m/2)` if m is even or `[-(m-1)/2,(m-1)/2]` if m is odd."""

        new_coeffs = [
            (((c + modulus // 2) % modulus) - modulus // 2) for c in self.coeffs
        ]
        return PolyNTRU(new_coeffs)

    def reduced(self, modulus: int) -> Self:
        pass


    def inverse(self, modulus: int) -> Self:
        pass

import random
def random_polyntru(n: int, d_pos: int, d_neg: int) -> PolyNTRU:
    if (d_sum := d_pos + d_neg) > n:
        raise ValueError("Sum of positive and negative counts should not exceed degree N")

    coeffs = [ 0 ] * n

    # Randomly select d_sum elements without replacement
    indices = random.sample(list(range(n)), k=d_sum)

    for idx in indices:
        # Positive only if no more negative indices to select or won a coin toss
        is_positive = (d_neg == 0) or (d_pos != 0 and random.randint(0, 1) == 0)

        if is_positive:
            coeffs[idx] = 1
            d_pos = max(0, d_pos - 1)
        else:
            coeffs[idx] = -1
            d_neg = max(0, d_neg - 1)

    return PolyNTRU(coeffs)


if __name__ == '__main__':

    f = PolyNTRU([3, 1, 4])
    g = PolyNTRU([2, 7, 1])

    assert f + g == PolyNTRU([5, 8, 5])
    assert f * g == PolyNTRU([35, 27, 18])

    f = PolyNTRU([3,1,4,1,5,9])
    assert f.center(10) == PolyNTRU([3, 1, 4, 1, -5, -1])

    f = random_polyntru(10, 1, 5)