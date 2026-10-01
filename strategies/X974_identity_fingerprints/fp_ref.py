# generated (D111) — do not edit. load() reassembles the packed table and checks its SHA-256.
import base64, hashlib, importlib, json, zlib
N_PARTS = 3
SHA256 = "1ad4e6786d9d82ebbc6d05154045805a8ab2f68e3faeebb707d4700d7f0745e9"


def load_table():
    s = "".join(importlib.import_module("fp_ref_%02d" % i).DATA for i in range(N_PARTS))
    raw = zlib.decompress(base64.b64decode(s))
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise Exception("packed SEC table corrupted (hash mismatch)")
    return json.loads(raw)
