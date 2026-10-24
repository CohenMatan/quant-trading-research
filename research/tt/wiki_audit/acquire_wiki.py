"""Download WIKI/PRICES from the official Nasdaq Data Link bulk-export route and write WIKI_MANIFEST.json (D298).

Requirements, both set by the owner in the environment settings and picked up by a NEW session:
  - network access to data.nasdaq.com, plus the host of the export link it returns (historically Amazon S3);
  - a free Nasdaq Data Link API key in the environment variable NASDAQ_DATA_LINK_API_KEY.

The key is never printed, logged or written to disk; the manifest records the URL without it.
The raw file goes to data/wiki/ (git-ignored). Nothing is parsed or printed beyond size, row count and SHA-256.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
OUT_DIR = ROOT / "data" / "wiki"
MANIFEST = HERE / "WIKI_MANIFEST.json"
EXPORT_URL = "https://data.nasdaq.com/api/v3/datatables/WIKI/PRICES.json"
PAGE_URL = "https://data.nasdaq.com/databases/WIKIP"


def export_link(session, key: str, wait: float = 30.0, tries: int = 40) -> tuple[str, str]:
    """Bulk-export link and snapshot time; polls while Nasdaq is still generating the file."""
    for _ in range(tries):
        r = session.get(EXPORT_URL, params={"qopts.export": "true", "api_key": key}, timeout=60)
        if r.status_code != 200:
            raise SystemExit(f"export request refused: HTTP {r.status_code}")   # never echo the URL (it carries the key)
        f = r.json()["datatable_bulk_download"]["file"]
        if f.get("status") == "fresh" and f.get("link"):
            return f["link"], f.get("data_snapshot_time") or ""
        time.sleep(wait)
    raise SystemExit("export file not ready")


def write_manifest(csv_path: Path, snapshot: str, out: Path = MANIFEST) -> dict:
    h, rows = hashlib.sha256(), 0
    with open(csv_path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
            rows += b.count(b"\n")
    m = {"source": PAGE_URL, "route": EXPORT_URL + "?qopts.export=true (API key not recorded)",
         "acquired_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "data_snapshot_time": snapshot,
         "file": str(csv_path.relative_to(ROOT)), "format": "CSV (from the bulk-export zip)",
         "bytes": csv_path.stat().st_size, "row_count": rows - 1, "sha256": h.hexdigest()}
    out.write_text(json.dumps(m, indent=1) + "\n")
    return m


def main():
    import requests
    key = os.environ.get("NASDAQ_DATA_LINK_API_KEY")
    if not key:
        raise SystemExit("NASDAQ_DATA_LINK_API_KEY is not set")
    s = requests.Session()
    link, snap = export_link(s, key)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    zpath = OUT_DIR / "WIKI_PRICES.zip"
    with s.get(link, stream=True, timeout=600) as r:
        if r.status_code != 200:
            raise SystemExit(f"download refused: HTTP {r.status_code}")
        with open(zpath, "wb") as fh:
            for b in r.iter_content(1 << 20):
                fh.write(b)
    with zipfile.ZipFile(zpath) as z:
        names = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(names) != 1:
            raise SystemExit("unexpected archive contents")
        z.extract(names[0], OUT_DIR)
    m = write_manifest(OUT_DIR / names[0], snap)
    print(json.dumps({k: m[k] for k in ("bytes", "row_count", "sha256")}))


if __name__ == "__main__":
    sys.exit(main())
