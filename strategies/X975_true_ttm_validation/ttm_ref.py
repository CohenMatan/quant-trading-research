# generated (D111) — do not edit. load() reassembles the packed table and checks its SHA-256.
import base64, hashlib, importlib, json, zlib
N_PARTS = 12
SHA256 = "242ce98251cdfe96c970252b8028f5cb92ae945bbe25a28e63a70ab94ff42742"


def load_table():
    s = "".join(importlib.import_module("ttm_ref_%02d" % i).DATA for i in range(N_PARTS))
    raw = zlib.decompress(base64.b64decode(s))
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise Exception("packed SEC table corrupted (hash mismatch)")
    return json.loads(raw)
