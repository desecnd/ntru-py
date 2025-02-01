#!/usr/local/bin/sage -python
from ntru_py.ntc.ntc import NTRU_PARAM_TYPES, NTRU_PARAMS, unpack_ntru_tuple
from ntru_py.sage import gen_keypair, random_message, encrypt, decrypt, invert_modp,Rx
from ntru_py.ntc.ntc_json import *
import sys

VALID_CMDS = ['keygen', 'message', 'encrypt', 'decrypt'] 
# Commands list:
# encrypt m pk -> c.json
# decrypt c sk -> c_dec.json 
# message -> m.json
# keygen -> pk.json sk.json

def cmd_keygen(ntru_tuple: NtruTuple) -> tuple[PolyCoeffs, PolyCoeffs]:
    h, f, _, _, _ = gen_keypair(*ntru_tuple)
    h = [ int(x) for x in h ]
    f = [ int(x) for x in f ]
    return h, f

def cmd_encrypt(ntru_tuple: NtruTuple, m: PolyCoeffs, h: PolyCoeffs) -> PolyCoeffs:
    m = Rx(m)
    h = Rx(h)
    N, _, q, d = ntru_tuple
    c, _ = encrypt(m, h, d, N, q)
    c = [ int(x) for x in c ]
    return c

def cmd_decrypt(ntru_tuple: NtruTuple, c: PolyCoeffs, f: PolyCoeffs) -> PolyCoeffs:
    N, p, q, d = ntru_tuple
    c = Rx(c)
    f = Rx(f)
    fp = invert_modp(f, N, p) 
    m = decrypt(c, f, fp, N, p, q) 
    m = [ int(x) for x in m ]
    return m

def cmd_message(ntru_tuple: NtruTuple) -> PolyCoeffs:
    """Generate random polynomial suitable for encryption with coefffs [-p//2: p//2]"""

    N, p, q, d = ntru_tuple
    m = random_message(N)
    m = [ int(x) for x in m ]
    return m


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: ./cli-ntru.py ntru-type cmd [params]")
        print("> types:", NTRU_PARAM_TYPES)
        print("> cmds:", VALID_CMDS)
        exit(1)

    ntru_type = sys.argv[1]
    cmd = sys.argv[2]

    if ntru_type not in NTRU_PARAM_TYPES:
        print(f"Incorrect ntru-type value '{ntru_type}'. Possible values are: {NTRU_PARAM_TYPES}")
        exit(1)

    if cmd not in VALID_CMDS:
        print(f"Incorrect cmd: {cmd}. Possible values are: {VALID_CMDS}")


    ntru_dict = NTRU_PARAMS[ntru_type]
    ntru_tuple = unpack_ntru_tuple(ntru_dict)


    if cmd == 'keygen':
        if len(sys.argv) < 3:
            print("usage: ./prog.py <ntru-type> keygen [pk.json] [sk.json]")
            exit(1)
        
        h, f = cmd_keygen(ntru_tuple)

        pk_fname = sys.argv[3] if len(sys.argv) >= 4 else "pk.json"
        sk_fname = sys.argv[4] if len(sys.argv) >= 5 else "sk.json"

        store_pk(h, ntru_tuple, pk_fname)
        store_sk(f, ntru_tuple, sk_fname)

    if cmd == 'message':
        if len(sys.argv) != 3:
            print("usage: ./prog.py <ntru-type> message [message]")
            exit(1)

        m = cmd_message(ntru_tuple)

        store_message(m, ntru_tuple)
        
    if cmd == 'encrypt':
        if len(sys.argv) != 5:
            print("usage: ./prog.py <ntru-type> encrypt <m.json> <pk.json>")
            exit(1)

        m = load_message(ntru_tuple, sys.argv[3])
        h = load_pk(ntru_tuple, sys.argv[4])

        c = cmd_encrypt(ntru_tuple, m, h)

        store_ciphertext(c, ntru_tuple)

    if cmd == 'decrypt':
        if len(sys.argv) != 5:
            print("usage: ./prog.py <ntru-type> decrypt <c.json> <sk.json>")
            exit(1)

        c: PolyCoeffs = load_ciphertext(ntru_tuple, sys.argv[3])
        f: PolyCoeffs = load_sk(ntru_tuple, sys.argv[4])

        # ... 
        m = cmd_decrypt(ntru_tuple, c, f)

        store_message(m, ntru_tuple, "c_dec.json")

