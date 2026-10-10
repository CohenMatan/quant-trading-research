"""P7-CP5c (D184): how often SEC values for a period change after the original filing (restatement / recast
vintages), from public SEC data only (the X995 reference table: for every period end of the 480 sample companies,
every filing that reported the period with its own values and filing date). A layer that attached a CURRENT
(restated) value to the ORIGINAL filing date would leak the later information; this measures how often that would
matter. Output: research/phase7/cp5c/restatement_vintages.json"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from qresearch.sec_pack import unpack  # noqa: E402

FIELDS = ("revenue_q", "revenue_fy", "net_income_q", "net_income_fy", "operating_cash_flow_fy", "total_assets",
          "stockholders_equity")


def main():
    d = ROOT / "strategies" / "X995_timing_probe"
    t = unpack({p.name: p.read_text() for p in d.glob("p5c_ref*.py")}, "p5c_ref")["sample"]
    c = {f: Counter() for f in FIELDS}
    lag = []
    for cik, comp in t.items():
        for pe, vers in comp["versions"].items():
            if not ("2009-06-30" <= pe <= "2017-12-31"):
                continue
            vers = sorted(vers, key=lambda v: (v[2], v[0]))
            for f in FIELDS:
                vals = [(v[2], v[1], v[3].get(f)) for v in vers if v[3].get(f)]
                if not vals:
                    continue
                first = vals[0][2]
                later = [x for x in vals[1:] if abs(x[2] / first - 1) > 0.005]
                c[f]["periods"] += 1
                c[f]["changed_later_gt_0.5pct"] += int(bool(later))
                c[f]["changed_later_gt_5pct"] += int(any(abs(x[2] / first - 1) > 0.05 for x in later))
                if later:
                    lag.append((later[0][0] >= vals[0][0]))
    out = {f: dict(v, share_changed=v["changed_later_gt_0.5pct"] / v["periods"] if v["periods"] else None,
                   share_changed_gt_5pct=v["changed_later_gt_5pct"] / v["periods"] if v["periods"] else None)
           for f, v in c.items()}
    out["_note"] = ("'changed' = a LATER SEC filing reported the same period with a value differing from the first "
                    "filing (restatement, reclassification, discontinued-operations recast, segment re-presentation)")
    (Path(__file__).parent / "restatement_vintages.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
