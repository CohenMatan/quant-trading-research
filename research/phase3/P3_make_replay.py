"""Phase 3 fidelity replay schedule (P3-CP2): the ENTRY DECISIONS (decision date, security id) of the completed control
books E982-02 (H017 canary, random-event seed 0) and E017-03..07 (random-event seeds 1-5), restricted to decisions on
or before 2017-12-31 (the Phase 3 search window ends there; 2018+ is never loaded by any Phase 3 engine run). Identifiers
only (no prices). Packed for QuantConnect like the H017 event table (zlib + base64, SHA-256 checked on load).

    PYTHONPATH=src python research/phase3/P3_make_replay.py
"""
import base64
import hashlib
import json
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research/phase2/sec"))
from e970_parse import lines  # noqa: E402

BOOKS = ("E982-02", "E017-03", "E017-04", "E017-05", "E017-06", "E017-07")
END = "2017-12-31"
LEAN = ROOT / "src/qresearch/lean"
PART = 60000


def main():
    entries = []
    for b, e in enumerate(BOOKS):
        for x in lines(e):
            if x.startswith("EN|"):
                _, d, sid, E, pos = x.split("|")
                if d <= END:
                    entries.append([b, d, sid])
    raw = json.dumps(dict(books=list(BOOKS), end=END, entries=entries), separators=(",", ":"), sort_keys=True).encode()
    digest = hashlib.sha256(raw).hexdigest()
    s = base64.b64encode(zlib.compress(raw, 9)).decode()
    parts = [s[i:i + PART] for i in range(0, len(s), PART)]
    for p in LEAN.glob("qr_p3_replay_*.py"):
        p.unlink()
    for i, part in enumerate(parts):
        (LEAN / f"qr_p3_replay_{i:02d}.py").write_text(f'# generated (Phase 3 fidelity replay) — do not edit\nDATA = "{part}"\n')
    (LEAN / "qr_p3_replay.py").write_text(
        "# generated (research/phase3/P3_make_replay.py) — do not edit. Control-book entry decisions for the fidelity\n"
        "# replay; load() reassembles the packed parts and checks the SHA-256.\n"
        "import base64, hashlib, importlib, json, zlib\n"
        f"N_PARTS = {len(parts)}\nSHA256 = \"{digest}\"\n\n\n"
        "def load_replay():\n"
        '    s = "".join(importlib.import_module("qr_p3_replay_%02d" % i).DATA for i in range(N_PARTS))\n'
        "    raw = zlib.decompress(base64.b64decode(s))\n"
        "    if hashlib.sha256(raw).hexdigest() != SHA256:\n"
        '        raise Exception("packed Phase 3 replay schedule corrupted (hash mismatch)")\n'
        "    return json.loads(raw)\n")
    print(len(entries), "entries", digest, len(parts), "parts")


if __name__ == "__main__":
    main()
