"""Data Infrastructure v2 (D190) packer: a JSON-able object -> QuantConnect project modules, lzma (preset 9 extreme) +
base85 text split over `<prefix>_NN.py` files plus `<prefix>.py` whose load_table() reassembles it and verifies the
SHA-256 of the raw JSON. Loader version LOADER_VERSION. (The data-v1 packer qresearch.sec_pack stays unchanged; it is
pinned by the data v1 freeze.) Base85 uses no quote or backslash, so the parts are plain string literals."""
from __future__ import annotations

import base64
import hashlib
import json
import lzma

CHUNK = 63_000                    # QuantConnect project files: at most 64,000 characters each
LOADER_VERSION = "v2-lzma-b85-1"


def raw_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def pack(obj, prefix: str, chunk: int = CHUNK) -> dict[str, str]:
    raw = raw_bytes(obj)
    sha = hashlib.sha256(raw).hexdigest()
    txt = base64.b85encode(lzma.compress(raw, preset=9 | lzma.PRESET_EXTREME)).decode()
    parts = [txt[i:i + chunk] for i in range(0, len(txt), chunk)] or [""]
    files = {f"{prefix}_{i:02d}.py": f'# generated (Data v2, D190) — do not edit\nDATA = "{p}"\n'
             for i, p in enumerate(parts)}
    files[f"{prefix}.py"] = (
        "# generated (Data v2, D190) — do not edit. load_table() reassembles the packed table and checks its SHA-256.\n"
        "import base64, hashlib, importlib, json, lzma\n"
        f"LOADER_VERSION = \"{LOADER_VERSION}\"\nN_PARTS = {len(parts)}\nSHA256 = \"{sha}\"\n\n\n"
        "def load_table():\n"
        f"    s = \"\".join(importlib.import_module(\"{prefix}_%02d\" % i).DATA for i in range(N_PARTS))\n"
        "    raw = lzma.decompress(base64.b85decode(s))\n"
        "    if hashlib.sha256(raw).hexdigest() != SHA256:\n"
        "        raise Exception(\"packed Data v2 table corrupted (hash mismatch)\")\n"
        "    return json.loads(raw)\n")
    return files


def unpack(files: dict[str, str], prefix: str):
    """Offline inverse of pack() (tests, audits)."""
    head = files[f"{prefix}.py"]
    n = int(head.split("N_PARTS = ")[1].split("\n")[0])
    s = "".join(files[f"{prefix}_{i:02d}.py"].split('DATA = "')[1].rsplit('"', 1)[0] for i in range(n))
    raw = lzma.decompress(base64.b85decode(s))
    assert hashlib.sha256(raw).hexdigest() == head.split('SHA256 = "')[1].split('"')[0]
    return json.loads(raw)
