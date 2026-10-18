"""LH-CP3 Part A (owner D244; protocol 2 and 9): offline recovery of missing fiscal labels through LOCAL SEC submissions
(L1), before any network request. Metadata only (cut-off-safe loaders, 0 network requests); no price, return or
surprise value. Bases kept apart: (i) Stage C P2 eligible stock-months (C1-complete), (ii) P2 eligible unique chains,
(iii) all-registrant unique 13-period chains (anchors 2011-2021; the LH-CP2 diagnostic population).

    PYTHONPATH=src python research/longhorizon/cp3/LH_CP3_part_a.py
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import lh_cp3_data as DATA

HERE = Path(__file__).parent
SAFE, V3, R, INV, SC = DATA.SAFE, DATA.V3, DATA.R, DATA.INV, DATA.SC
OUT = HERE / "LH_CP3_part_a.json"
PROTOCOL = HERE / "LH_CP3_protocol.md"


def reason(reg, p, first_xbrl):
    """LH-CP2 post-hoc reason for an unknown L0 label (same definitions)."""
    if reg.meta.filing(p) is not None:
        return "no_fp"
    if first_xbrl is None or reg.orig.get(p, 0) < first_xbrl:
        return "pre_xbrl"
    return "no_index_row"


def main():
    from qr_data_v21 import load_table
    t = load_table()
    client = SAFE.client()
    xb_by_cik = DATA.load_index()
    fmap, _ = SC.load_fye()
    den, recs, chains, regs = DATA.build_p2(client, t, xb_by_cik, fmap)
    ok, repro = DATA.check_repro(den, recs)
    if not ok:
        OUT.write_text(json.dumps(dict(stop="P2 reproduction failed", repro=repro), indent=1) + "\n")
        raise SystemExit("STOP: P2 does not reproduce the frozen Stage C coverage")

    # ---- per chain: verified labels (L0 + L1) and classes
    period_cls = {}                                   # (cik, p) -> (L0 label?, L1 class, reason)
    for key, ch in chains.items():
        cik, c13 = key
        reg = regs[cik]
        fx = min((r[2] for r in reg.meta.xb if r[1] in ("10-Q", "10-K")), default=None)
        labs, srcs = [], []
        for p in c13:
            lab, src = reg.label(p)
            labs.append(lab)
            srcs.append(src)
            if (cik, p) not in period_cls:
                period_cls[(cik, p)] = (src, reason(reg, p, fx) if src != "L0" else None)
        ch["labels_v"] = labs
        ch["srcs_v"] = srcs
        ch["lstatus_v"] = R.label_status(labs)
        mf_l1 = any(s == "Invalid" for s in srcs)
        ch["mapping_fail_v"] = ch["mapping_fail"] or mf_l1
        ch["rule_v_v"] = R.rule_v(ch["lstatus_v"], ch["transition"], ch["mapping_fail_v"])

    # ---- period-level recovery (unique registrant-periods in P2 chains whose L0 label is unknown)
    per = Counter()
    per_reason = defaultdict(Counter)
    for (cik, p), (src, rsn) in period_cls.items():
        if src == "L0":
            per["L0_known"] += 1
            continue
        per["L0_unknown"] += 1
        cls = "Verified" if src == "L1" else src
        per[cls] += 1
        per_reason[rsn][cls] += 1
    rec_rate = per["Verified"] / per["L0_unknown"] if per["L0_unknown"] else None

    # ---- chain / stock-month bases (C1-complete = the LH-CP2 basis)
    c1 = Counter()
    for rec in recs:
        if rec["ok1"]:
            c1[rec["key"]] += 1
    tot_sm = sum(c1.values())
    st_cp2_u, st_cp2_sm, st_v_u, st_v_sm, rv_u, rv_sm = (Counter() for _ in range(6))
    for key, n in c1.items():
        ch = chains[key]
        st_cp2_u[ch["lstatus"]] += 1
        st_cp2_sm[ch["lstatus"]] += n
        st_v_u[ch["lstatus_v"]] += 1
        st_v_sm[ch["lstatus_v"]] += n
        rv_u[ch["rule_v_v"]] += 1
        rv_sm[ch["rule_v_v"]] += n
    by_year = defaultdict(Counter)
    for rec in recs:
        if rec["ok1"]:
            ch = chains[rec["key"]]
            by_year[rec["year"]]["c1_complete"] += 1
            by_year[rec["year"]]["unknown_cp2"] += ch["lstatus"] == "unknown"
            by_year[rec["year"]]["unknown_after_l1"] += ch["lstatus_v"] == "unknown"

    # ---- all-registrant unique chains (LH-CP2 diagnostic population), after L1
    lo, hi = V3.dn("2011-01-01"), V3.dn("2021-12-31")
    allc = Counter()
    for n_r, (cik, cols) in enumerate(sorted(t["f"].items(), key=lambda kv: int(kv[0]))):
        orig = V3.originals(cols)
        vis = sorted(orig)
        reg = regs.get(cik)
        for i0 in range(len(vis)):
            if not (lo <= vis[i0] <= hi):
                continue
            ch = V3.chain_back(vis, i0, 13)
            if not ch:
                continue
            if reg is None:
                reg = DATA.Reg(cik, client, xb_by_cik, cols)
            l0 = [reg.meta.label(p) for p in ch]
            lv = [reg.label(p)[0] for p in ch]
            allc["all"] += 1
            allc["unknown_l0"] += None in l0
            allc["unknown_after_l1"] += None in lv
        if n_r % 500 == 0:
            print("all registrants", n_r, flush=True)

    # ---- metadata-only examples (one per L1 class, deterministic)
    ex = {}
    for (cik, p), (src, rsn) in sorted(period_cls.items(), key=lambda kv: hashlib.sha256(f"{kv[0][0]}|{kv[0][1]}".encode()).hexdigest()):
        cls = "Verified" if src == "L1" else src
        if src == "L0" or cls in ex:
            continue
        reg = regs[cik]
        r = reg.sub_row(p)
        ex[cls] = dict(cik=cik, period_end=str(V3.dd(p)), lh_cp2_reason=rsn,
                       submissions_row=None if r is None else dict(form=r[1], filed=str(V3.dd(r[2])), accession=r[3], isXBRL=r[4]),
                       data_v21_original_filing=str(V3.dd(reg.orig[p])) if p in reg.orig else None,
                       recovered_label=reg.label(p)[0])

    out = dict(
        kind="LH-CP3 Part A - local submissions recovery (aggregates + metadata-only examples; no returns)",
        decision="D244", protocol_sha256=hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(), cut_off=SAFE.CUT,
        network_requests=client.fetched, returns_computed=False, surprise_values_computed=False, quantconnect_run=False,
        holdout_accessed=False,
        p2_reproduction=dict(identical_to_stage_c=ok, denominators={str(y): den[y] for y in range(2011, 2022)}),
        periods_unique=dict(counts=dict(per), recovery_rate_verified=round(rec_rate, 4) if rec_rate is not None else None,
                            by_lh_cp2_reason={k: dict(v) for k, v in per_reason.items()}),
        p2_c1_basis=dict(stock_months=tot_sm, unique_chains=len(c1),
                         label_status_lh_cp2=dict(unique=dict(st_cp2_u), stock_months=dict(st_cp2_sm)),
                         label_status_after_l1=dict(unique=dict(st_v_u), stock_months=dict(st_v_sm)),
                         rule_v_after_l1=dict(unique=dict(rv_u), stock_months=dict(rv_sm)),
                         unknown_share_lh_cp2=round(st_cp2_sm["unknown"] / tot_sm, 4),
                         unknown_share_after_l1=round(st_v_sm["unknown"] / tot_sm, 4),
                         by_year={str(y): dict(v) for y, v in sorted(by_year.items())}),
        all_registrant_chains=dict(allc, unknown_share_l0=round(allc["unknown_l0"] / allc["all"], 4),
                                   unknown_share_after_l1=round(allc["unknown_after_l1"] / allc["all"], 4)),
        examples=ex,
    )
    SAFE.assert_no_post_cutoff(out)
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    DATA.save_cache("p2.pkl", dict(den=den, recs=recs, chains=chains))
    print(json.dumps({k: out[k] for k in ("periods_unique", "all_registrant_chains")}, indent=1))
    print(json.dumps(out["p2_c1_basis"], indent=1)[:3000])


if __name__ == "__main__":
    main()
