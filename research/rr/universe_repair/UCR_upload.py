"""UCR-1 (owner D269): upload the point-in-time public SEC object ONCE to the Object Store key pinned in
qresearch.rr_ucr, after checking that the local file's SHA-256 equals the pinned value. The X806 host re-checks the
digest of what it reads and refuses anything else. The SCA-1 object (rr/sca_sec_v1.json) is already stored and is
not touched.

    PYTHONPATH=src python research/rr/universe_repair/UCR_upload.py"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import rr_ucr as P  # noqa: E402
from qresearch.qc_client import QCClient  # noqa: E402

if __name__ == "__main__":
    data = (ROOT / "data/sec_derived/ucr_sec_v1.json").read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if P.UCR_REFERENCE_SHA256 is None or sha != P.UCR_REFERENCE_SHA256:
        raise SystemExit(f"local SEC object {sha[:12]} is not the pinned object; nothing uploaded")
    QCClient().object_set(P.UCR_OBJECT_KEY, data)
    print(f"uploaded {len(data)} bytes to {P.UCR_OBJECT_KEY} (sha256 {sha[:12]}...)")
