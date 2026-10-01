# generated (D111) — do not edit. load() reassembles the packed table and checks its SHA-256.
import base64, hashlib, importlib, json, zlib
N_PARTS = 41
SHA256 = "40932531c7433cab9a29b7b9e0d9157867f08ef5e902a6fcc2e3ee3527a3a76d"


def load_table():
    s = "".join(importlib.import_module("sec_ref_%02d" % i).DATA for i in range(N_PARTS))
    raw = zlib.decompress(base64.b64decode(s))
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise Exception("packed SEC table corrupted (hash mismatch)")
    return json.loads(raw)
