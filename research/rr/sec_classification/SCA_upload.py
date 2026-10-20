"""SCA-1 (owner D267): upload the public SEC reference JSON ONCE to the Object Store key pinned in qresearch.rr_sca,
after checking that the local file's SHA-256 equals the pinned value. The X805 host re-checks the digest of what it
reads and refuses anything else.

    PYTHONPATH=src python research/rr/sec_classification/SCA_upload.py"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import rr_sca as P  # noqa: E402
from qresearch.qc_client import QCClient  # noqa: E402

if __name__ == "__main__":
    data = (ROOT / "data/sec_derived/sca_sec_v1.json").read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if P.SEC_REFERENCE_SHA256 is None or sha != P.SEC_REFERENCE_SHA256:
        raise SystemExit(f"local SEC reference {sha[:12]} is not the pinned object; nothing uploaded")
    QCClient().object_set(P.OBJECT_KEY, data)
    print(f"uploaded {len(data)} bytes to {P.OBJECT_KEY} (sha256 {sha[:12]}...)")
