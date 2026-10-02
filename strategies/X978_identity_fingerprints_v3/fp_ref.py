# generated (D111) — do not edit. load() reassembles the packed table and checks its SHA-256.
import base64, hashlib, importlib, json, zlib
N_PARTS = 1
SHA256 = "c3ccae7ca23b53485d91f93be7298e2bc38e4bd15f8630ea5165ac9e5c679bdb"


def load_table():
    s = "".join(importlib.import_module("fp_ref_%02d" % i).DATA for i in range(N_PARTS))
    raw = zlib.decompress(base64.b64decode(s))
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise Exception("packed SEC table corrupted (hash mismatch)")
    return json.loads(raw)
