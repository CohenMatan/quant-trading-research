# generated (D111) — do not edit. load() reassembles the packed table and checks its SHA-256.
import base64, hashlib, importlib, json, zlib
N_PARTS = 42
SHA256 = "76b18bccd265fa70cc83b689ddc4c6d482c0c78708395681fd6aa924ab4354fb"


def load_table():
    s = "".join(importlib.import_module("p5c_ref_%02d" % i).DATA for i in range(N_PARTS))
    raw = zlib.decompress(base64.b64decode(s))
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise Exception("packed SEC table corrupted (hash mismatch)")
    return json.loads(raw)
