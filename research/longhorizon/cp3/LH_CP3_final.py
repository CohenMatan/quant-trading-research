"""LH-CP3 final evaluation (owner D244; protocol 6, 8-10): V5 header check on genuine pre-XBRL filings, Stage C P2
history classes and scenarios A-D, composition and selection bias, rule P review (ex-post), mechanical
classification. Reads the held-back validation (run once with the frozen rules), the committed manifest and header
fields; metadata only; no price, return or surprise value.

    PYTHONPATH=src python research/longhorizon/cp3/LH_CP3_final.py
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import lh_cp3_data as DATA
from LH_CP3_validation import RP

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
SAFE, V3, R, SC, INV = DATA.SAFE, DATA.V3, DATA.R, DATA.SC, DATA.INV
OUT = HERE / "LH_CP3_final.json"
YEARS = tuple(range(2013, 2022))


def v5(man, hdrs, bench_rate):
    rows = []
    for a in man["accessions"]:
        h = hdrs["headers"].get(a["accession"], {})
        rec = dict(stratum=a["stratum"], tier=a["tier"], form=a["form"], status=h.get("status", "not_retrieved"))
        if h.get("status") == "ok":
            per = h.get("period")
            rec["period_matches_submissions"] = per == a["report_date"].replace("-", "") if per else None
            rec["form_matches"] = h.get("form_type") == a["form"] if h.get("form_type") else None
            rec["fye_withheld"] = h.get("date_as_of_change_after_cutoff", False)
            rec["fye_present"] = bool(h.get("fiscal_year_end"))
            if per and h.get("fiscal_year_end"):
                pdn = V3.dn(f"{per[:4]}-{per[4:6]}-{per[6:]}")
                hq = R.h_fye(h["fiscal_year_end"], pdn, a["form"])
                rec["h_fye"] = hq
                lab = a["seq"] if a["tier"] == "L2" else None
                rec["vs_L2"] = None if (lab is None or not isinstance(hq, int)) else hq == lab
                rec["vs_seq"] = None if (a["seq"] in (None, "conflict") or not isinstance(hq, int)) else hq == a["seq"]
                rec["vs_cmp"] = None if (a["cmp"] in (None, "conflict") or not isinstance(hq, int)) else hq == a["cmp"]
        rows.append(rec)
    usable = [r for r in rows if r.get("vs_L2") is not None]
    dis = sum(1 for r in usable if not r["vs_L2"])
    rate = R.rate(dis, len(usable))
    if not any(r["status"] == "ok" for r in rows):
        status = "not evaluated"
    elif len(usable) < 60:
        status = "insufficient"
    else:
        status = "pass" if rate <= bench_rate + 0.05 else "fail"

    def tally(key):
        return dict(Counter(str(r.get(key)) for r in rows))
    return dict(status=status, usable=len(usable), disagree=dis, disagreement_rate=R.fmt(rate, 5),
                disagreement_upper95_cp=R.fmt(R.cp_upper(dis, len(usable)), 5) if usable else None,
                benchmark_rate=R.fmt(bench_rate, 5), threshold=R.fmt(bench_rate + 0.05, 5),
                retrieval=tally("status"), period_matches_submissions=tally("period_matches_submissions"),
                form_matches=tally("form_matches"), fye_present=tally("fye_present"), fye_withheld=tally("fye_withheld"),
                h_fye_outcome=tally("h_fye"), vs_seq=tally("vs_seq"), vs_cmp=tally("vs_cmp"),
                by_stratum={s: dict(n=sum(1 for r in rows if r["stratum"] == s),
                                    ok=sum(1 for r in rows if r["stratum"] == s and r["status"] == "ok"),
                                    usable_L2=sum(1 for r in rows if r["stratum"] == s and r.get("vs_L2") is not None),
                                    disagree_L2=sum(1 for r in rows if r["stratum"] == s and r.get("vs_L2") is False))
                            for s in sorted({r["stratum"] for r in rows})})


def history_classes(t, client, xb_by_cik, p2):
    recs, chains = p2["recs"], p2["chains"]
    regs, memo, out = {}, {}, []
    for rec in recs:
        key, D = rec["key"], rec["D"]
        ch = chains[key]
        if ch["rule_v_v"] == "valid":
            cls = "conditional_C" if ch["identity"] else "verified_valid"
        elif ch["rule_v_v"] == "invalid":
            cls = "verified_invalid"
        else:
            mk = (key, D)
            if mk not in memo:
                cik, c13 = key
                reg = regs.get(cik) or DATA.Reg(cik, client, xb_by_cik, t["f"][cik])
                regs[cik] = reg
                rr = reg.reconstruct(list(c13), D)
                lv = ch["labels_v"]
                conflict = any(lv[k] is None and rr[k][1] == "conflict" for k in range(13))
                l2 = [lv[k] if lv[k] is not None else (rr[k][0] if rr[k][1] == "L2" else None) for k in range(13)]
                l3 = [lv[k] if lv[k] is not None else (rr[k][0] if rr[k][1] in ("L2", "L3") else None) for k in range(13)]
                s2 = R.rule_v(R.label_status(l2), ch["transition"], ch["mapping_fail_v"])
                s3 = R.rule_v(R.label_status(l3), ch["transition"], ch["mapping_fail_v"])
                if conflict:
                    c = "unknown_conflict"
                elif s2 == "valid":
                    c = "conditional_C" if ch["identity"] else "conditional_B"
                elif s2 == "invalid":
                    c = "invalid_reconstructed"
                elif s3 == "valid":
                    c = "conditional_C"
                elif s3 == "invalid":
                    c = "invalid_reconstructed_L3"
                else:
                    c = "unknown"
                memo[mk] = c
            cls = memo[mk]
        out.append(cls)
    return out


def size_cuts(recs):
    by_j = defaultdict(list)
    for rec in recs:
        if rec["ok1"] and rec["ta"] is not None:
            by_j[rec["j"]].append(rec["ta"])
    return {j: np.percentile(v, [100 / 3, 200 / 3]) for j, v in by_j.items() if len(v) >= 3}


def groups(rec, cuts):
    from qr_xs_diag import ff12
    c = cuts.get(rec["j"])
    if rec["ta"] is None or c is None:
        size = "size:unknown"
    else:
        size = "size:T1_small" if rec["ta"] <= c[0] else ("size:T2" if rec["ta"] <= c[1] else "size:T3_large")
    a = rec["age"]
    age = "age:unknown" if a is None else ("age:<5y" if a < 5 else ("age:5-15y" if a < 15 else "age:>=15y"))
    d = rec["depth"]
    depth = "depth:<20" if d < 20 else ("depth:20-39" if d < 40 else "depth:>=40")
    return [size, age, f"ff12:{ff12(rec['sic'])}", "entrant" if rec["entrant"] else "not_entrant",
            "leaver" if rec["leaver"] else "stayer", f"year:{rec['year']}", depth, "all"]


def coverage(recs, classes, den, include):
    res = {}
    for c in ("C1", "C2", "C6"):
        num = Counter()
        for rec, cl in zip(recs, classes):
            okc = rec["ok1"] if c == "C1" else (rec["ok2"] if c == "C2" else rec["ok1"] and rec["ok2"])
            if okc and cl in include:
                num[rec["year"]] += 1
        by = {str(y): dict(den=den[y], num=num[y], share=round(num[y] / den[y], 4)) for y in range(2011, 2022)}
        mn = min(YEARS, key=lambda y: by[str(y)]["share"])
        res[c] = dict(by_year=by, min_year=mn, min_share=by[str(mn)]["share"],
                      floor_70_all_years=all(by[str(y)]["share"] >= 0.70 for y in YEARS),
                      years_below_70=[y for y in YEARS if by[str(y)]["share"] < 0.70])
    return res


def composition(recs, classes, include, cuts):
    tot, inc = Counter(), Counter()
    for rec, cl in zip(recs, classes):
        if not rec["ok1"] or rec["year"] < 2013:
            continue
        for g in groups(rec, cuts):
            tot[g] += 1
            inc[g] += cl in include
    return {g: dict(n=tot[g], included_share=round(inc[g] / tot[g], 4)) for g in sorted(tot)}


def rule_p_review(t, client, xb_by_cik):
    """Protocol 8 items 2-3: isolated off-cycle labels in all-registrant 13-period windows, classified ex-post."""
    lo, hi = V3.dn("2011-01-01"), V3.dn("2021-12-31")
    res = Counter()
    for cik, cols in sorted(t["f"].items(), key=lambda kv: int(kv[0])):
        reg = DATA.Reg(cik, client, xb_by_cik, cols)
        per = sorted(reg.orig)
        lab = {p: reg.label(p)[0] for p in per}
        for i0 in range(len(per)):
            if not (lo <= per[i0] <= hi):
                continue
            ch = V3.chain_back(per, i0, 13)
            if not ch or any(lab[p] is None for p in ch):
                continue
            ls = [lab[p] for p in ch]
            out, flags = RP.proposed_validity(ls, variant="strict")
            if out != "valid" or "isolated_tag_error" not in flags:
                continue
            a, off = RP._offsets(ls)
            k = off[0]
            pos = "boundary_newest" if k == 0 else ("boundary_oldest" if k == 12 else "interior")
            res[f"{pos}:windows"] += 1
            if pos == "interior":
                res["interior:reverting_by_construction"] += 1
                continue
            # extend 4 periods beyond the boundary (ex-post, <= CUT), contiguous only
            idx = per.index(ch[k])
            ext = per[idx + 1: idx + 5] if k == 0 else per[max(0, idx - 4): idx][::-1]
            seqp = [ch[k]] + ext
            if len(ext) < 4 or not all(80 <= abs(y - x) <= 100 for x, y in zip(seqp, seqp[1:])) or any(lab[p] is None for p in ext):
                res[f"{pos}:undetermined"] += 1
                continue
            step = 1 if k == 0 else -1                      # newer periods advance the cycle
            new_cycle = all(lab[q] == (ls[k] - 1 + step * (n + 1)) % 4 + 1 for n, q in enumerate(ext))
            exp_k = ((a - 1 - k) % 4) + 1
            old_cycle = all(lab[q] == (exp_k - 1 + step * (n + 1)) % 4 + 1 for n, q in enumerate(ext))
            res[f"{pos}:{'genuine_rebasing' if new_cycle else ('reverting_mistag' if old_cycle else 'other')}"] += 1
    return dict(res)


def main():
    from qr_data_v21 import load_table
    hb = json.loads((HERE / "LH_CP3_heldback.json").read_text())
    fr = json.loads((HERE / "LH_CP3_rules_freeze.json").read_text())
    if hashlib.sha256((HERE / "lh_cp3_rules.py").read_bytes()).hexdigest() != fr["lh_cp3_rules_sha256"] or \
            hb["rules_sha256"] != fr["lh_cp3_rules_sha256"]:
        raise SystemExit("STOP: rules differ from the frozen rules")
    man = json.loads((HERE / "LH_CP3_manifest.json").read_text())
    hdrs = json.loads((HERE / "LH_CP3_headers.json").read_text())
    t = load_table()
    client = SAFE.client()
    xb_by_cik = DATA.load_index()
    crit = dict(hb["criteria"])
    crit["V5"] = v5(man, hdrs, hb["criteria"]["V5_benchmark"]["disagreement_rate"])
    p2 = DATA.load_cache("p2.pkl")
    den, recs, chains = p2["den"], p2["recs"], p2["chains"]
    classes = history_classes(t, client, xb_by_cik, p2)
    st = {k: crit[k]["status"] for k in ("V1", "V2", "V3", "V4", "V5")}
    validated = all(v == "pass" for v in st.values())
    weak = sum(1 for k in ("V3", "V4", "V5") if st[k] in ("insufficient", "not evaluated"))
    if st["V1"] == "insufficient" or weak >= 2:
        r_valid_for_B = False
    else:
        r_valid_for_B = not any(v == "fail" for v in st.values())
    inc_A = {"verified_valid"}
    inc_B = inc_A | ({"conditional_B"} if r_valid_for_B else set())
    inc_C = inc_A | {"conditional_B", "conditional_C"}
    stage_c = json.loads((ROOT / "research/longhorizon/stage_c/LH_StageC_audit.json").read_text())["candidates"]
    scen = dict(A=coverage(recs, classes, den, inc_A), B=coverage(recs, classes, den, inc_B),
                C=coverage(recs, classes, den, inc_C),
                D={c: dict(by_year=stage_c[c]["by_year"]) for c in ("C1", "C2", "C6")})
    cuts = size_cuts(recs)
    comp = dict(all_c1_complete=composition(recs, classes, set(classes), cuts),
                A=composition(recs, classes, inc_A, cuts), B=composition(recs, classes, inc_B, cuts),
                C=composition(recs, classes, inc_C, cuts))
    # ---- class counts (C1-complete stock-months) and selection bias among LH-CP2 label-unknown histories
    cls_sm = Counter(cl for rec, cl in zip(recs, classes) if rec["ok1"])
    recovered_set = {"verified_valid", "verified_invalid", "conditional_B", "invalid_reconstructed"}
    unk = [(rec, cl) for rec, cl in zip(recs, classes) if rec["ok1"] and chains[rec["key"]]["lstatus"] == "unknown"]
    rec_n = sum(1 for _r, cl in unk if cl in recovered_set)
    resolution = rec_n / len(unk) if unk else None
    sb = defaultdict(Counter)
    for rec, cl in unk:
        k = "recovered" if cl in recovered_set else "unrecovered"
        for g in groups(rec, cuts):
            sb[g][k] += 1
    selection = {g: dict(recovered=v["recovered"], unrecovered=v["unrecovered"],
                         recovered_share=round(v["recovered"] / (v["recovered"] + v["unrecovered"]), 4))
                 for g, v in sorted(sb.items())}
    unk_cls = Counter(cl for _r, cl in unk)
    # ---- classification (protocol 10)
    if st["V1"] == "insufficient" or weak >= 2:
        cls = "D - INSUFFICIENT EVIDENCE"
    elif any(v == "fail" for v in st.values()):
        cls = "C - METHOD NOT VALIDATED"
    elif validated and resolution is not None and resolution >= 0.90:
        cls = "A - RECOVERY METHOD VALIDATED"
    else:
        cls = "B - PARTIAL RECOVERY"
    rpr = rule_p_review(t, client, xb_by_cik)
    out = dict(kind="LH-CP3 final evaluation (aggregates; metadata only; no returns)", decision="D244", cut_off=SAFE.CUT,
               rules_sha256=fr["lh_cp3_rules_sha256"],
               protocol_sha256=hashlib.sha256((HERE / "LH_CP3_protocol.md").read_bytes()).hexdigest(),
               manifest_sha256=hashlib.sha256((HERE / "LH_CP3_manifest.json").read_bytes()).hexdigest(),
               network_requests_this_script=client.fetched, returns_computed=False, surprise_values_computed=False,
               quantconnect_run=False, holdout_accessed=False,
               criteria=crit, criteria_status=st, r_star_admitted_to_scenario_B=r_valid_for_B,
               history_classes_c1_stock_months=dict(cls_sm),
               lh_cp2_unknown_c1_stock_months=len(unk), lh_cp2_unknown_classes=dict(unk_cls),
               resolution_share=R.fmt(resolution), scenarios=scen, composition=comp, selection_bias=selection,
               rule_p_review_boundary=rpr, classification=cls)
    SAFE.assert_no_post_cutoff(out)
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps(dict(classification=cls, criteria_status=st, resolution=out["resolution_share"],
                          classes=dict(cls_sm), unk=dict(unk_cls), rule_p=rpr), indent=1))


if __name__ == "__main__":
    main()
