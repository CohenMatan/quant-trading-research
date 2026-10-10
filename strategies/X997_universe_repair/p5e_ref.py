# generated (D111) — do not edit. load() reassembles the packed table and checks its SHA-256.
import base64, hashlib, importlib, json, zlib
N_PARTS = 13
SHA256 = "1ece9c48bb2b7319ae9559fef3ed0836c3959788b8a76af661b92445b2676be4"


def load_table():
    s = "".join(importlib.import_module("p5e_ref_%02d" % i).DATA for i in range(N_PARTS))
    raw = zlib.decompress(base64.b64decode(s))
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise Exception("packed SEC table corrupted (hash mismatch)")
    return json.loads(raw)
