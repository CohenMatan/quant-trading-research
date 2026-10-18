"""POST-HOC DIAGNOSTIC (written after the frozen Stage C audit reported 'chain FAIL'; NOT used for the protocol
classification). Metadata only (SEC XBRL filing index, Data v2.1 filing tables): explains why fiscal-year-end codes
differ between q0 and its comparison quarters on contiguous chains. No accounting value, no return.

    PYTHONPATH=src python research/longhorizon/stage_c/LH_StageC_fye_diagnostic.py
"""
import importlib.util
import json
from collections import Counter
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("lh_a", HERE / "LH_StageC_audit.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
V3 = A.V3
OUT = HERE / "LH_StageC_fye_diagnostic.json"


def circ_days(a, b):
    """Circular day distance between two MMDD codes (non-leap reference year)."""
    try:
        da = (date(2001, int(a[:2]), int(a[2:])) - date(2001, 1, 1)).days
        db = (date(2001, int(b[:2]), int(b[2:])) - date(2001, 1, 1)).days
    except ValueError:
        return None
    d = abs(da - db)
    return min(d, 365 - d)


def main():
    from qr_data_v21 import load_table
    t = load_table()
    fmap, _ = A.load_fye()
    lo, hi = V3.dn("2011-01-01"), V3.dn("2021-12-31")
    cnt, dist = Counter(), Counter()
    for cik, cols in t["f"].items():
        orig = V3.originals(cols)
        vis = sorted(orig)
        for i0 in range(len(vis)):
            if not (lo <= vis[i0] <= hi):
                continue
            for n, pos in ((13, (0, 4, 12)), (5, (0, 4))):
                ch = V3.chain_back(vis, i0, n)
                if not ch:
                    continue
                codes = [A.fye_at(fmap, cik, ch[k]) for k in pos]
                if any(c is None for c in codes):
                    cnt[f"chain{n}:codes_missing"] += 1
                    continue
                cnt[f"chain{n}:with_codes"] += 1
                if len(set(codes)) == 1:
                    continue
                cnt[f"chain{n}:changed"] += 1
                m = max(circ_days(codes[0], c) or 0 for c in codes[1:])
                if m is None:
                    continue
                band = "<=7d" if m <= 7 else ("8-31d" if m <= 31 else ">31d")
                cnt[f"chain{n}:changed_{band}"] += 1
                if n == 13 and m > 31:
                    dist[min(("~3m", abs(m - 91)), ("~6m", abs(m - 182)), key=lambda x: x[1])[0]
                         if min(abs(m - 91), abs(m - 182)) <= 15 else "other"] += 1
    out = dict(kind="POST-HOC DIAGNOSTIC - not used for the frozen Stage C classification (metadata only)",
               chains_over_filing_table_periods_2011_2021=dict(cnt),
               chain13_over31d_shift_shape=dict(dist),
               note="changed_<=7d = fiscal-year-end code drift typical of 52/53-week fiscal years; >31d = a different "
                    "fiscal-year-end month on a contiguous chain")
    for n in (13, 5):
        w = cnt[f"chain{n}:with_codes"]
        if w:
            out[f"chain{n}_shares"] = {k: round(cnt[f"chain{n}:{k}"] / w, 4) for k in
                                       ("changed", "changed_<=7d", "changed_8-31d", "changed_>31d")}
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
