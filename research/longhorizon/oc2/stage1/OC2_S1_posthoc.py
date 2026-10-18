"""OC-2 Stage 1 POST-HOC, NON-GATING diagnostics (owner D248 §4 / §6). Written after OC2_S1_audit.json existed and
labelled as such; they can never change the frozen gate (protocol §7). Metadata and committed aggregates only.

1. Identity history: share of SEC-side complete-chain stock-months whose Data v2.1 identity rows show a different
   CIK at any row dated within the 730 days before D (a vendor-side 8-quarter span could then mix registrants; the
   SEC-side chain cannot, because it is built from one CIK's filings).
2. Vendor-side usable cross-section per review (committed P14-CP1 F5-A coverage x non-financial eligible count).
3. Vendor-vs-SEC F5 availability in the committed P14-CP2 validation sample.

    PYTHONPATH=src python research/longhorizon/oc2/stage1/OC2_S1_posthoc.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase2/sec"),
                str(ROOT / "research/longhorizon/stage_c"), str(HERE)]
from qresearch import data_v3 as V3  # noqa: E402

OUT = HERE / "OC2_S1_posthoc.json"


def main():
    import LH_StageC_audit as SC
    import OC2_S1_audit as A
    from qr_data_v21 import load_table
    t = load_table()
    ident = SC.Ident(t)
    U = SC.load_universe()
    revs = [dict(T=T, Dn=V3.dn(str(D)), m=T.year * 12 + T.month, year=T.year,
                 primary=(T.year, T.month) >= A.PRIMARY_FROM) for T, D in V3.review_days()]
    tot, chg = Counter(), Counter()
    for sid, u in U.items():
        rows = ident.rows.get(sid, ())
        for r in revs:
            if not r["primary"] or r["m"] not in u["months"]:
                continue
            cik, sic, _ = ident.at(sid, r["Dn"])
            if cik is None or sic is None or 6000 <= sic <= 6999:
                continue
            tot[r["year"]] += 1
            seen = {str(int(c)) for day, _s, c in rows if r["Dn"] - 730 <= day <= r["Dn"] and c not in (None, "")}
            chg[r["year"]] += len(seen) > 1
    p1 = json.loads((ROOT / "research/phase14/cp1/P14_CP1_audit.json").read_text())
    cov = p1["coverage"]["F5A"]["monthly"]
    nf = p1["monthly_counts"]["nf_eligible"]
    valid = [round(c * n) for c, n in zip(cov, nf)]
    prim = [i for i, r in enumerate(revs) if r["primary"]]
    by_year = {}
    for y in A.Y:
        v = [valid[i] for i in prim if revs[i]["year"] == y]
        by_year[str(y)] = dict(mean=round(sum(v) / len(v), 1), min=min(v), max=max(v))
    p2 = json.loads((ROOT / "research/phase14/cp2/P14_CP2_audit.json").read_text())
    av = p2["validation"]["F5"]["availability"]
    out = dict(kind="OC-2 Stage 1 post-hoc NON-GATING diagnostics (metadata / committed aggregates only)",
               decision="D248",
               identity_cik_change_within_730d={str(y): round(chg[y] / tot[y], 4) for y in sorted(tot)},
               identity_population={str(y): tot[y] for y in sorted(tot)},
               vendor_side_valid_per_review=dict(
                   by_year=by_year, overall_mean=round(sum(valid[i] for i in prim) / len(prim), 1),
                   min=min(valid[i] for i in prim), max=max(valid[i] for i in prim),
                   note="P14-CP1 F5-A coverage (Data v2.1 store, before guard v3) x P14-CP1 nf_eligible"),
               vendor_vs_sec_F5_availability=dict(
                   counts=av, vendor_missing_given_sec_valid=round(av["sec_only"] / (av["both"] + av["sec_only"]), 4),
                   sec_missing_given_vendor_valid=round(av["vendor_only"] / (av["both"] + av["vendor_only"]), 4)))
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
