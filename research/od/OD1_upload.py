"""OD-1 (owner D308): upload the OD-1 fundamental extension object ONCE to the Object Store key pinned in
qresearch.od1, after checking that the local file's SHA-256 equals the pinned value and that its parent is the pinned
UCR-1 object. The X808 host re-checks the digest of what it reads. The UCR-1 and H032 objects are already stored and
are not touched.

    PYTHONPATH=src python research/od/OD1_upload.py"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import od1 as P, os1  # noqa: E402
from qresearch.qc_client import QCClient  # noqa: E402

if __name__ == "__main__":
    data = (ROOT / "data/sec_derived/od1_sec_v1.json").read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if P.OD1_REFERENCE_SHA256 is None or sha != P.OD1_REFERENCE_SHA256:
        raise SystemExit(f"local OD-1 object {sha[:12]} is not the pinned object; nothing uploaded")
    if json.loads(data)["meta"]["parent_sha256"] != os1.UCR_REFERENCE_SHA256:
        raise SystemExit("the OD-1 object's parent is not the pinned UCR-1 object; nothing uploaded")
    QCClient().object_set(P.OD1_OBJECT_KEY, data)
    print(f"uploaded {len(data)} bytes to {P.OD1_OBJECT_KEY} (sha256 {sha[:12]}...)")
