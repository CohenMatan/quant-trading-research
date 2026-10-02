# generated (D111) — do not edit. load() reassembles the packed table and checks its SHA-256.
import base64, hashlib, importlib, json, zlib
N_PARTS = 19
SHA256 = "1d39676a131ed75a2ec1187fe835a07c1a49a73f14933f9fdceb98337997cadd"


def load_table():
    s = "".join(importlib.import_module("qr_sec_data_%02d" % i).DATA for i in range(N_PARTS))
    raw = zlib.decompress(base64.b64decode(s))
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise Exception("packed SEC table corrupted (hash mismatch)")
    return json.loads(raw)
