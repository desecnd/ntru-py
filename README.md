# NTRU Python Implementation

> [!WARNING]
> Package contains cryptographic scheme which is not suitable for real-world applications. It should be treated only as an educational reference.

This package is a pure Python implementation of [NTRU](https://en.wikipedia.org/wiki/NTRU) cryptosystem made as an educational excercise to understand the system better and as a project for the _Post-Quantum Cryptography_ course on Adam Mickiewicz University in Poznan.

Supplementary to the main python implementation (`poly` directory), package contains `sage` directory which is an implementation based on [LatticeHacks](https://latticehacks.cr.yp.to/ntru.html) guide to NTRU cryptosystem - its main purpose is to provide a point of reference for comparison.

In addition to the implementation, the other goal of the project was partially to develop the `NTC` (_NTRU-Test-Case_) - an easy-to-port JSON interface which was made available to other students. This allowed for simpler comparison and verification of raw (polynomial-based) NTRU implementations and easier debugging. 

> [!NOTE]
> Implementation was based on NTRU version defined in [IEEE 1363.1-2008](https://ieeexplore.ieee.org/document/4800404) standard, however it lacks important elements, such as the conversion between the polynomials and bytes - only algorithms which lay in the heart of NTRU described in [HPS98](https://www.ntru.org/f/hps98.pdf) were implemented. 

## NTC - NtruTestCase

Following is a quick guide for using the JSON interface.

```bash
# Generate (pk_256bit.json, sk_256bit.json) pair of keys and store in current directory
$ ./cli-ntru.py 256bit keygen
# Generate random message for encryption and store it in `m.json` file
$ ./cli-ntru.py 256bit message
# Encrypt message inside `m.json` with public key inside `pk_256bit.json` and create ciphertext `c.json`
$ ./cli-ntru.py 256bit encrypt m.json pk_256bit.json
# Decrypt message inside `c.json` with secret key inside `sk_256bit.json`
$ ./cli-ntru.py 256bit decrypt c.json sk_256bit.json
# Make sure that m == Dec(Enc(m))
$ diff m.json c_dec.json 
$
# Or compare the file hashes if done remotely
$ sha256sum m.json 
6d6838c229cb16279bd95a66aa4b9073ce845c47c70fb7fe0cb286852f7fab0f  m.json
$ sha256sum c_dec.json
6d6838c229cb16279bd95a66aa4b9073ce845c47c70fb7fe0cb286852f7fab0f  c_dec.json
```

### keygen

New pair of public key and private key (`pk_<type>.json` and `sk_<type>.json`) can be generated using `keygen` command:

```bash
# Create new pair (public_key, secret_key) for "tiny" set of parameters
$ ./cli-ntru.py tiny keygen

# Two files generated: pk_<type>.json and sk_<type>.json
$ ls .
pk_tiny.json    sk_tiny.json

# Both NTRU params as well as the polynomial are stored inside .json file:
$ cat pk_tiny.json
{"N": 11, "p": 3, "q": 32, "d": 2, "h": [3, 6, 0, 9, 23, 18, 5, 10, 27, 15, 12]}

$ cat sk_tiny.json
{"N": 11, "p": 3, "q": 32, "d": 2, "f": [1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 1]}
```

### message

Generate new message for encryption and store it as a `m.json`

```bash
$ ./cli-ntru.py tiny message
# m.json craeted after successful execution
$ cat m.json
{"N": 11, "p": 3, "q": 32, "d": 2, "m": [0, 1, 0, 0, 0, 1, 1, -1, 0, 0, -1]}
```

### encrypt

Encrypt plaintext stored in `m.json` with `pk.json` file and return `c.json` ciphertext

```bash
# Encrypt using 'tiny' parameter set, message stored under `m.json` with public key `pk_tiny.json`
$ ./cli-ntru.py tiny encrypt m.json pk_tiny.json 
$ cat c.json
{"N": 11, "p": 3, "q": 32, "d": 2, "c": [6, 23, 16, 12, 1, 12, 23, 14, 10, 11, 1]}
```

### decrypt

Decrypt ciphertext stored in `c.json` with `sk.json` file and return `c_dec.json` plaintext that should be equal to `m.json`:

```bash
# Decrypt using 'tiny' parameter set, ciphertext stored in `c.json` using secret key `sk_tiny.json`
$ ./cli-ntru.py tiny decrypt c.json sk_tiny.json 
$ cat c_dec.json 
{"N": 11, "p": 3, "q": 32, "d": 2, "m": [0, 1, 0, 0, 0, 1, 1, -1, 0, 0, -1]}
```

There should be no difference between `m.json` and `c_dec.json`:

```bash
# Compare m with Dec(Enc(m))
$ diff m.json c_dec.json 
$ # no output -> no difference
```

## Comparison with Sage

In order to verify the implementation one can run the scripts to `A)` generate the testcases in assets and `B)` verify them with `sage` implementation. 


A) Generate with `sage`:

```bash
# Store results in 'assets' directory
$ sage -python ./scripts/export_sage.py 
```

B) Validate with `poly` (python):

```bash
$ python3 ./scripts/validate_poly.py 
[+] Valid testcase - assets/ntc_128bit_00.json
[+] Valid testcase - assets/ntc_128bit_01.json
[+] Valid testcase - assets/ntc_128bit_02.json
[+] Valid testcase - assets/ntc_128bit_03.json
[+] Valid testcase - assets/ntc_128bit_04.json
[+] Valid testcase - assets/ntc_128bit_05.json
```

## SageMath Unit Tests

SageMath tests require that `sage.all` to be accessible within `python3` environment. In order to run `test_sage`, pytest must be present in sage `venv` and executed as a module inside sage python.

```bash
# Install pytest inside sage-python environment
sage -python -m pip install pytest

# Run tests using sage-python pytest module
sage -python -m pytest
```

Running the `export_ntc` script with SageMath can be done by adding `src` to `PYTHONPATH`:

```bash
# In root directory of the project
PYTHONPATH=`pwd`/src sage -python ./scripts/export_ntc.py 
```
