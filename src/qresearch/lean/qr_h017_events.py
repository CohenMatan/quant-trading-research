# generated (H017 event table v1, research/phase2/h017/h017_event_table.py) — do not edit.
# load() reassembles the packed table and checks its SHA-256.
import base64, hashlib, importlib, json, zlib
N_PARTS = 7
SHA256 = "ebb287536bca42874d36b73443dc0e0c5e02fc78245351e36d7b1c37334a5c70"


def load_events():
    s = "".join(importlib.import_module("qr_h017_events_%02d" % i).DATA for i in range(N_PARTS))
    raw = zlib.decompress(base64.b64decode(s))
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise Exception("packed H017 event table corrupted (hash mismatch)")
    return json.loads(raw)
