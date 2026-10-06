"""P7-CP1: extract the published aggregates of the data audits E991-01 (X991 v1.1; E991-01 = v1.0) and E992-03 (X992 v1.2; E992-01 = v1.0, E992-02 = v1.1) into
research/phase7/P7_audit_E991.json / P7_audit_E992.json (+ the alignment sample lines). Counts, ages, dates and
availability ratios only; no price, no vendor value, no return."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def lines(exp):
    q = json.loads((ROOT / "experiments" / exp / "result.json").read_text())["qc_statistics"]
    return "".join(q[f"qr_msgs_{i:02d}"] for i in range(int(q["qr_msgs_n"]))).split("\n")


def chunks(ls, tag):
    parts = sorted((int(x.split("|", 2)[1]), x.split("|", 2)[2]) for x in ls if x.startswith(tag + "|"))
    return json.loads("".join(p for _, p in parts))


def main():
    a = lines("E991-02")
    out = dict(audit=chunks(a, "QRP7F"), alignment=[json.loads(x[2:]) for x in a if x.startswith("A|")],
               duplicates=[x for x in a if x.startswith("DUP|")])
    (HERE / "P7_audit_E991.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    b = lines("E992-03")
    out2 = dict(audit=chunks(b, "QRP7P"), alignment_price=[json.loads(x[3:]) for x in b if x.startswith("AP|")])
    (HERE / "P7_audit_E992.json").write_text(json.dumps(out2, indent=1, sort_keys=True) + "\n")
    print("ok", len(out["alignment"]), len(out2["alignment_price"]))


if __name__ == "__main__":
    sys.exit(main())
