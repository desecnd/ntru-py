from ntru_py.ntc.ntc import PolyCoeffs, NtruTuple, unpack_ntru_tuple, pack_ntru_tuple
from pathlib import Path
import json

# Files created during the interaface usage:
# pk.json
# sk.json
# c.json
# m.json
# m_enc.json
# m_dec.json

def _store_json_file_content(fname: str, content: str):
    path = Path(fname)
    if not path.suffix == ".json":
        raise ValueError("File does not contain a valid json extension")

    # Just overwrite the file
    with open(fname, 'w') as json_file:
        json_file.write(content)

def _load_json_file_content(fname: str) -> str:
    path = Path(fname)
    if not path.exists() or not path.is_file():
        raise ValueError("File does not exits or is not a valid file")

    if not path.suffix == ".json":
        raise ValueError("File does not contain a valid json extension")

    with open(path) as json_file:
        content = json_file.read()

    return content

def _load_poly(ntru_tuple: NtruTuple, filename: str, poly_name: str) -> PolyCoeffs:
    content = json.loads(_load_json_file_content(filename))
    loaded_ntru_tuple = unpack_ntru_tuple(content)

    if loaded_ntru_tuple != ntru_tuple:
        raise ValueError(f"Loaded NTRU params tuple: '{loaded_ntru_tuple}' is different than currently used tuple: {ntru_tuple}.")

    poly: PolyCoeffs = content[poly_name]
    return poly

def _store_poly(filename: str, poly_name: str, poly: PolyCoeffs, ntru_tuple: NtruTuple):
    content_dict = pack_ntru_tuple(*ntru_tuple)
    content_dict[poly_name] = poly
    content_str = json.dumps(content_dict)

    _store_json_file_content(filename, content_str)

def load_sk(ntru_tuple: NtruTuple, filename: str = "sk.json") -> PolyCoeffs:
    return _load_poly(ntru_tuple, filename, "f")

def store_sk(f: PolyCoeffs, ntru_tuple: NtruTuple, filename: str = "sk.json"):
    _store_poly(filename, "f", f, ntru_tuple)

def load_pk(ntru_tuple: NtruTuple, filename: str = "pk.json") -> PolyCoeffs:
    return _load_poly(ntru_tuple, filename, "h")

def store_pk(h: PolyCoeffs, ntru_tuple: NtruTuple, filename: str = "pk.json"):
    _store_poly(filename, "h", h, ntru_tuple)

def load_message(ntru_tuple: NtruTuple, filename: str = "m.json") -> PolyCoeffs:
    return _load_poly(ntru_tuple, filename, "m")

def store_message(m: PolyCoeffs, ntru_tuple: NtruTuple, filename: str = "m.json"):
    _store_poly(filename, "m", m, ntru_tuple)

def load_ciphertext(ntru_tuple: NtruTuple, filename: str = "c.json") -> PolyCoeffs:
    return _load_poly(ntru_tuple, filename, "c")

def store_ciphertext(c: PolyCoeffs, ntru_tuple: NtruTuple, filename: str = "c.json"):
    _store_poly(filename, "c", c, ntru_tuple)
