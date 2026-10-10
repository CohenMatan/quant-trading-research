# generated (D111) — do not edit. load() reassembles the packed table and checks its SHA-256.
import base64, hashlib, importlib, json, zlib
N_PARTS = 15
SHA256 = "d385ea83ee102dbe1b2ef60c0f744175e3d97330295d21788dcac942a9e728e1"


def load_table():
    s = "".join(importlib.import_module("p5d_ref_%02d" % i).DATA for i in range(N_PARTS))
    raw = zlib.decompress(base64.b64decode(s))
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise Exception("packed SEC table corrupted (hash mismatch)")
    return json.loads(raw)
