# H025 SEC event ledger (owner D204; research/phase10/h025_ledger.py). Public SEC Form 4 facts only.
# Generated file: do not edit. PAYLOAD_SHA256 = SHA-256 of the decoded CSV payload.
import base64
import hashlib
import lzma
PAYLOAD_SHA256 = '92632242eca7706421560002a20b297c79fab87f2c51ba3f7569f8147c0441ee'
N_PARTS = 6


def payload():
    import importlib
    b = ''.join(importlib.import_module('qr_h025_events_%02d' % i).DATA for i in range(N_PARTS))
    raw = lzma.decompress(base64.b85decode(b))
    if hashlib.sha256(raw).hexdigest() != PAYLOAD_SHA256:
        raise Exception('H025 event ledger payload hash mismatch')
    return raw.decode()
