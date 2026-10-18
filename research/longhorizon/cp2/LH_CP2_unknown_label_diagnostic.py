"""POST-HOC DIAGNOSTIC (written after the frozen LH-CP2 investigation reported 'C - INSUFFICIENT EVIDENCE' because
fiscal labels are unknown for 13.4% of C1-complete stock-months; NOT used for that classification). Metadata only,
cut-off-safe loaders: for every contiguous 13-period filing-table chain (anchor 2011-2021) of every Data v2.1
registrant, why is a period's fiscal label unknown?  'pre_xbrl' = the period's original filing day precedes the
registrant's first filing in the SEC XBRL index; 'no_index_row' = the registrant had XBRL filings by then but this
period has none in the index; 'no_fp' = an index row exists but no companyfacts fact carries its accession.

    PYTHONPATH=src python research/longhorizon/cp2/LH_CP2_unknown_label_diagnostic.py
"""
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location("lh_cp2_inv", HERE / "LH_CP2_investigation.py")
INV = importlib.util.module_from_spec(spec)
spec.loader.exec_module(INV)
SAFE, V3 = INV.SAFE, INV.V3
OUT = HERE / "LH_CP2_unknown_label_diagnostic.json"


def main():
    from qr_data_v21 import load_table
    t = load_table()
    client = SAFE.client()
    xb_by_cik = defaultdict(list)
    for r in SAFE.xbrl_filings():
        p = r.get("period") or ""
        if len(p) != 8:
            continue
        try:
            pdn = V3.dn(f"{p[:4]}-{p[4:6]}-{p[6:8]}")
        except ValueError:
            continue
        xb_by_cik[str(int(r["cik"]))].append((pdn, r.get("form"), V3.dn(r["filed"]), r.get("accn"), r.get("fye"), r.get("name")))
    lo, hi = V3.dn("2011-01-01"), V3.dn("2021-12-31")
    chains, why, by_year = Counter(), Counter(), defaultdict(Counter)
    for n, (cik, cols) in enumerate(sorted(t["f"].items(), key=lambda kv: int(kv[0]))):
        orig = V3.originals(cols)
        vis = sorted(orig)
        first_xbrl = min((r[2] for r in xb_by_cik.get(cik, ()) if r[1] in ("10-Q", "10-K")), default=None)
        m = None
        for i0 in range(len(vis)):
            if not (lo <= vis[i0] <= hi):
                continue
            ch = V3.chain_back(vis, i0, 13)
            if not ch:
                continue
            if m is None:
                m = INV.Meta(cik, client, xb_by_cik, cols)
            labels = [m.label(p) for p in ch]
            chains["all"] += 1
            if None not in labels:
                continue
            chains["label_unknown"] += 1
            reasons = set()
            for p, lab in zip(ch, labels):
                if lab is not None:
                    continue
                if m.filing(p) is not None:
                    reasons.add("no_fp")
                elif first_xbrl is None or orig[p] < first_xbrl:
                    reasons.add("pre_xbrl")
                else:
                    reasons.add("no_index_row")
            key = "pre_xbrl_only" if reasons == {"pre_xbrl"} else ("+".join(sorted(reasons)))
            why[key] += 1
            by_year[str(V3.dd(ch[0]).year)][key] += 1
        if n % 500 == 0:
            print("registrants", n, flush=True)
    out = dict(kind="POST-HOC DIAGNOSTIC - not used for the frozen LH-CP2 classification (metadata only)",
               chains=dict(chains), unknown_reasons=dict(why),
               unknown_share=round(chains["label_unknown"] / chains["all"], 4),
               pre_xbrl_only_share_of_unknown=round(why["pre_xbrl_only"] / chains["label_unknown"], 4),
               unknown_reasons_by_anchor_year={y: dict(v) for y, v in sorted(by_year.items())},
               network_requests=client.fetched, cut_off=SAFE.CUT)
    SAFE.assert_no_post_cutoff(out)
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in ("chains", "unknown_reasons", "unknown_share", "pre_xbrl_only_share_of_unknown")}, indent=1))


if __name__ == "__main__":
    main()
