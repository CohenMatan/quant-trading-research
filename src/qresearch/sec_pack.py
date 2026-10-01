"""Pack a JSON-able object into QuantConnect project modules (D111): zlib + base64 text split over several .py
files (`<prefix>_00.py`, ...) plus `<prefix>.py` whose load() reassembles and verifies it (SHA-256)."""
from __future__ import annotations

import base64
import hashlib
import json
import zlib

CHUNK = 62_000             # QuantConnect project files: at most 64,000 characters each


def pack(obj, prefix: str, chunk: int = CHUNK) -> dict[str, str]:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    sha = hashlib.sha256(raw).hexdigest()
    b64 = base64.b64encode(zlib.compress(raw, 9)).decode()
    parts = [b64[i:i + chunk] for i in range(0, len(b64), chunk)] or [""]
    files = {f"{prefix}_{i:02d}.py": f'# generated (D111) — do not edit\nDATA = "{p}"\n' for i, p in enumerate(parts)}
    files[f"{prefix}.py"] = (
        "# generated (D111) — do not edit. load() reassembles the packed table and checks its SHA-256.\n"
        "import base64, hashlib, importlib, json, zlib\n"
        f"N_PARTS = {len(parts)}\nSHA256 = \"{sha}\"\n\n\n"
        "def load_table():\n"
        f"    s = \"\".join(importlib.import_module(\"{prefix}_%02d\" % i).DATA for i in range(N_PARTS))\n"
        "    raw = zlib.decompress(base64.b64decode(s))\n"
        "    if hashlib.sha256(raw).hexdigest() != SHA256:\n"
        "        raise Exception(\"packed SEC table corrupted (hash mismatch)\")\n"
        "    return json.loads(raw)\n")
    return files


def unpack(files: dict[str, str], prefix: str):
    """Offline inverse of pack() (tests, audits)."""
    ns: dict = {}
    head = files[f"{prefix}.py"]
    n = int(head.split("N_PARTS = ")[1].split("\n")[0])
    s = "".join(files[f"{prefix}_{i:02d}.py"].split('DATA = "')[1].rsplit('"', 1)[0] for i in range(n))
    raw = zlib.decompress(base64.b64decode(s))
    assert hashlib.sha256(raw).hexdigest() == head.split('SHA256 = "')[1].split('"')[0]
    del ns
    return json.loads(raw)
