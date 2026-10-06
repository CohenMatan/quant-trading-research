"""P7-CP3 (D171): extract the E993-01 export (X993 v1.0) into research/phase7/P7_CP3_E993_stats.json (host checks and
run statistics) and research/phase7/P7_CP3_E993_payload.json.gz (score tables: integer points, disqualifier bits,
ADV20 in $K, FF12 codes, breadth / regime states, weekly disqualifier states). Verifies the payload hash published by
the host and that no return-like field exists. No price, no vendor value, no return."""
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
import qr_p7_export as E  # noqa: E402


def lines(exp):
    q = json.loads((ROOT / "experiments" / exp / "result.json").read_text())["qc_statistics"]
    return "".join(q[f"qr_msgs_{i:02d}"] for i in range(int(q["qr_msgs_n"]))).split("\n")


def joined(ls, tag):
    parts = sorted((int(x.split("|", 2)[1]), x.split("|", 2)[2]) for x in ls if x.startswith(tag + "|"))
    assert [p[0] for p in parts] == list(range(len(parts))), f"{tag}: missing chunks"
    return "".join(p for _, p in parts)


def main(exp="E993-01"):
    ls = lines(exp)
    st = json.loads(joined(ls, "QRP7S"))
    blob = joined(ls, "QRP7X")
    assert hashlib.sha256(blob.encode()).hexdigest() == st["payload_sha256"], "payload hash mismatch"
    text = E.unpack(blob)
    pay = json.loads(text)
    for bad in ("return", "forward", "alpha", "future", "cagr", "sharpe"):
        assert bad not in text.lower(), bad
    (HERE / "P7_CP3_E993_stats.json").write_text(json.dumps(st, indent=1, sort_keys=True) + "\n")
    with gzip.GzipFile(HERE / "P7_CP3_E993_payload.json.gz", "wb", mtime=0) as f:
        f.write(text.encode())
    print("ok", len(pay["reviews"]), len(pay["weekly"]), st["payload_chars"])


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
