# generated (Data v2, D190) — do not edit. load_table() reassembles the packed table and checks its SHA-256.
import base64, hashlib, importlib, json, lzma
LOADER_VERSION = "v2-lzma-b85-1"
N_PARTS = 15
SHA256 = "107b6b5534a83368f3a9620a8d96dc6fec1a14793aa0639a3787240b85346884"


def load_table():
    s = "".join(importlib.import_module("qr_data_v2_%02d" % i).DATA for i in range(N_PARTS))
    raw = lzma.decompress(base64.b85decode(s))
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise Exception("packed Data v2 table corrupted (hash mismatch)")
    return json.loads(raw)
