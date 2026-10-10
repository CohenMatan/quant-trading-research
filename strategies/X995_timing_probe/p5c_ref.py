# generated (D111) — do not edit. load() reassembles the packed table and checks its SHA-256.
import base64, hashlib, importlib, json, zlib
N_PARTS = 24
SHA256 = "6f2007480484a1a8e03265d36144c32424931d284fd5355a782e642dabd8dbb8"


def load_table():
    s = "".join(importlib.import_module("p5c_ref_%02d" % i).DATA for i in range(N_PARTS))
    raw = zlib.decompress(base64.b64decode(s))
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise Exception("packed SEC table corrupted (hash mismatch)")
    return json.loads(raw)
