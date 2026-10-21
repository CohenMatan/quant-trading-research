"""H032 / OS-1 revised (owner D278 item 6): upload the H032 extension SEC object ONCE to the Object Store key pinned in
qresearch.os1, after checking that the local file's SHA-256 equals the pinned value and that its parent is the pinned
UCR-1 object. The X807 host re-checks the digest of what it reads and refuses anything else. The original UCR-1 object
(rr/ucr_sec_v1.json) is already stored and is not touched.

    PYTHONPATH=src python research/os/OS1_upload.py"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import os1 as P  # noqa: E402
from qresearch.qc_client import QCClient  # noqa: E402

if __name__ == "__main__":
    data = (ROOT / "data/sec_derived/os1_sec_v1.json").read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if P.OS1_REFERENCE_SHA256 is None or sha != P.OS1_REFERENCE_SHA256:
        raise SystemExit(f"local SEC extension object {sha[:12]} is not the pinned object; nothing uploaded")
    if json.loads(data)["meta"]["parent_sha256"] != P.UCR_REFERENCE_SHA256:
        raise SystemExit("the extension object's parent is not the pinned UCR-1 object; nothing uploaded")
    QCClient().object_set(P.OS1_OBJECT_KEY, data)
    print(f"uploaded {len(data)} bytes to {P.OS1_OBJECT_KEY} (sha256 {sha[:12]}...)")
