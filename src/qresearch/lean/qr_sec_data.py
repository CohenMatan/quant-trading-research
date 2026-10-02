# generated (D111) — do not edit. load() reassembles the packed table and checks its SHA-256.
import base64, hashlib, importlib, json, zlib
N_PARTS = 17
SHA256 = "348c633be9ea6dd2fd7a8e8dc939063edc3bb6fa4ea8f8ade9b2abbcb0a9c5c5"


def load_table():
    s = "".join(importlib.import_module("qr_sec_data_%02d" % i).DATA for i in range(N_PARTS))
    raw = zlib.decompress(base64.b64decode(s))
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise Exception("packed SEC table corrupted (hash mismatch)")
    return json.loads(raw)
