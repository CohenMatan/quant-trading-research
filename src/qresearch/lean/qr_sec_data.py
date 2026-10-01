# generated (D111) — do not edit. load() reassembles the packed table and checks its SHA-256.
import base64, hashlib, importlib, json, zlib
N_PARTS = 3
SHA256 = "0b61dce4f7294cc92581e0b101db4ce010bf2f0a219681779e31d125425bb638"


def load_table():
    s = "".join(importlib.import_module("qr_sec_data_%02d" % i).DATA for i in range(N_PARTS))
    raw = zlib.decompress(base64.b64decode(s))
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise Exception("packed SEC table corrupted (hash mismatch)")
    return json.loads(raw)
