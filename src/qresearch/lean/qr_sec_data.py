# generated (D111) — do not edit. load() reassembles the packed table and checks its SHA-256.
import base64, hashlib, importlib, json, zlib
N_PARTS = 19
SHA256 = "37124e67afa61ab8d1838f2cdd0349a9317b8294216c0f6de11936e5dbb45541"


def load_table():
    s = "".join(importlib.import_module("qr_sec_data_%02d" % i).DATA for i in range(N_PARTS))
    raw = zlib.decompress(base64.b64decode(s))
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise Exception("packed SEC table corrupted (hash mismatch)")
    return json.loads(raw)
