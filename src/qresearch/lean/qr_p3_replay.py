# generated (research/phase3/P3_make_replay.py) — do not edit. Control-book entry decisions for the fidelity
# replay; load() reassembles the packed parts and checks the SHA-256.
import base64, hashlib, importlib, json, zlib
N_PARTS = 1
SHA256 = "16862615d96b2f4c890d58af28b6b2b322505f8a623988698f2b33abf7785969"


def load_replay():
    s = "".join(importlib.import_module("qr_p3_replay_%02d" % i).DATA for i in range(N_PARTS))
    raw = zlib.decompress(base64.b64decode(s))
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise Exception("packed Phase 3 replay schedule corrupted (hash mismatch)")
    return json.loads(raw)
