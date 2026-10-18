"""LH-CP3 hidden-label validation (owner D244; protocol 5-6). Pseudo-XBRL starts on registrants with known labels:
filings before the pseudo-start lose their facts and labels (as for a genuine pre-XBRL filing) and the frozen
reconstruction rules try to recover the labels. Registrant split: --split dev (development / debugging) or
--split heldback (ONCE, with the frozen rules hash asserted). Metadata only; no price, return or surprise value.

    PYTHONPATH=src python research/longhorizon/cp3/LH_CP3_validation.py --split dev
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path

import lh_cp3_data as DATA

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
SAFE, V3, R, SC = DATA.SAFE, DATA.V3, DATA.R, DATA.SC
_rp = importlib.util.spec_from_file_location("lh_cp2_rule_proposal", ROOT / "research/longhorizon/cp2/lh_cp2_rule_proposal.py")
RP = importlib.util.module_from_spec(_rp)
_rp.loader.exec_module(RP)
CUTD = V3.dn(SAFE.CUT)
FREEZE = HERE / "LH_CP3_rules_freeze.json"


def month_end_near(p, tol=3):
    d = V3.dd(p)
    from datetime import timedelta
    nxt = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
    last = nxt - timedelta(days=1)
    return min((last - d).days, (d - (d.replace(day=1) - timedelta(days=1))).days) <= tol


def genuine_change_positions(labels_newest_first):
    """Positions (newest-first index) of off-cycle labels when rule P (strict) calls the window a persistent
    re-basing / multiple off-cycle (protocol 5 'genuine fiscal change')."""
    out, flags = RP.proposed_validity(labels_newest_first, variant="strict")
    if out == "invalid" and flags and flags[0] in ("persistent_rebasing", "multiple_off_cycle"):
        _a, off = RP._offsets(labels_newest_first)
        return off
    return []


def universe_map():
    U = SC.load_universe()
    DEC21 = 2021 * 12 + 11
    st = defaultdict(set)
    for sid, u in U.items():
        if not u["months"]:
            continue
        fm, lm = min(u["months"]), max(u["months"])
        for c in u["ciks"]:
            st[str(c)].add("entrant" if fm > SC.M0 + 12 else ("leaver" if lm < DEC21 else "stayer"))
            if lm < DEC21:
                st[str(c)].add("leaver")
    return st


def registrant_status(st):
    if not st:
        return "not_in_universe"
    if "entrant" in st:
        return "entrant"
    if "leaver" in st:
        return "leaver"
    return "stayer"


def evaluate(split, limit=None):
    from qr_data_v21 import load_table
    t = load_table()
    client = SAFE.client()
    xb_by_cik = DATA.load_index()
    umap = universe_map()
    trials = []          # dict per hidden period
    hist = []            # dict per evaluable pseudo-history
    v4 = {}              # cik -> (first4_off, first4_n, later_off, later_n)
    bench = Counter()    # H-FYE vs L0 (XBRL era)
    bench_reg = {}
    regs_seen = 0
    ciks = [c for c in sorted(t["f"], key=int) if R.split(c) == split]
    if limit:
        ciks = ciks[:limit]
    for n_r, cik in enumerate(ciks):
        cols = t["f"][cik]
        reg = DATA.Reg(cik, client, xb_by_cik, cols)
        orig = reg.orig
        if not orig:
            continue
        per = sorted(orig)
        truth = {p: reg.label(p)[0] for p in per}
        lab_days = [orig[p] for p in per if truth[p] is not None]
        if not lab_days:
            continue
        regs_seen += 1
        f1 = min(lab_days)
        status = registrant_status(umap.get(cik, set()))
        w5253 = any(not month_end_near(p) for p in per)
        trans_reg = bool(reg.trans)
        # genuine change anywhere (13-period windows of the registrant's labelled contiguous sequence)
        gen_reg = False
        for i0 in range(len(per)):
            ch = V3.chain_back(per, i0, 13)
            if ch and all(truth[p] is not None for p in ch) and genuine_change_positions([truth[p] for p in ch]):
                gen_reg = True
                break
        # ---- V4: first four labelled filings vs later (oldest -> newest over the full sequence)
        seq = [truth[p] for p in per]
        iso_truth = {per[i] for i in R.isolated_off_cycle(seq)}          # addendum 1 (non-gating truth audit)
        labelled_idx = [i for i, x in enumerate(seq) if x is not None]
        first4 = set(labelled_idx[:4])
        off = set(R.isolated_off_cycle(seq))
        chk = [i for i in range(1, len(seq) - 1) if None not in (seq[i - 1], seq[i], seq[i + 1])]
        v4[cik] = (sum(1 for i in chk if i in first4 and i in off), sum(1 for i in chk if i in first4),
                   sum(1 for i in chk if i not in first4 and i in off), sum(1 for i in chk if i not in first4))
        # ---- V5 benchmark: H-FYE from XBRL-index codes vs L0 labels
        bk = [0, 0, 0]
        for pdn, form, fd, accn, fye, _n in reg.meta.xb:
            if form not in ("10-Q", "10-K"):
                continue
            l0 = reg.meta.label(pdn)
            if l0 is None:
                continue
            h = R.h_fye(fye, pdn, form)
            if isinstance(h, int):
                bk[0] += 1
                bk[1] += h != l0
            else:
                bk[2] += 1
        bench["usable"] += bk[0]
        bench["disagree"] += bk[1]
        bench["unusable"] += bk[2]
        bench_reg[cik] = (bk[1], bk[0])
        # ---- pseudo-histories
        j = 3
        while True:
            S = f1 + round(j * 365.25)
            if S + 400 > CUTD:
                break
            for off_d in (400, 765):
                D = S + off_d
                if D > CUTD:
                    continue
                vis = [p for p in per if orig[p] + 1 <= D]
                if not vis or D - vis[-1] > V3.MAX_AGE:
                    continue
                ch = V3.chain_back(vis, len(vis) - 1, 13)
                if not ch:
                    continue
                tl = [truth[p] for p in ch]
                hidden = [orig[p] < S for p in ch]
                if None in tl or not any(hidden):
                    continue
                rec = reg.reconstruct(ch, D, hidden_from=S)
                T = reg.meta.transition(ch, D)
                m_true = any(reg.meta.mapping_fail(p) for p in ch)
                m_rec = any(reg.meta.mapping_fail(p) for p, h in zip(ch, hidden) if not h)
                rl = [x if not h else r[0] if r[1] == "L2" else None for x, h, r in zip(tl, hidden, rec)]
                rl3 = [x if not h else r[0] for x, h, r in zip(tl, hidden, rec)]
                true_st = R.rule_v(R.label_status(tl), T, m_true)
                rec_st = R.rule_v(R.label_status(rl), T, m_rec)
                rec3_st = R.rule_v(R.label_status(rl3), T, m_rec)
                gpos = genuine_change_positions(tl)
                trans_hidden = any(min(p for p, h in zip(ch, hidden) if h) - 7 <= tp <= max(p for p, h in zip(ch, hidden) if h) + 7
                                   for tp in reg.transitions(D))
                change_hidden = bool(gpos and any(hidden[k] for k in gpos)) or trans_hidden
                rp_s = RP.proposed_validity(rl, T, m_rec, "strict")[0]
                rp_a = RP.proposed_validity(rl, T, m_rec, "assume")[0]
                nh = sum(hidden)
                hist.append(dict(cik=cik, S=S, D=D, nh=nh, true=true_st, rec=rec_st, rec3=rec3_st,
                                 change_hidden=change_hidden, gen=bool(gpos), rp_strict=rp_s, rp_assume=rp_a,
                                 isolated_true=RP.proposed_validity(tl, T, m_true, "strict")[1][:1] == ("isolated_tag_error",)))
                for k, (p, h) in enumerate(zip(ch, hidden)):
                    if not h:
                        continue
                    lab, tier, s, c = rec[k]
                    r = reg.sub_row(p)
                    form_bad = (r is not None) and ((r[1] == "10-Q" and tl[k] == 4) or (r[1] in R.K_FORMS and tl[k] != 4))
                    trials.append(dict(cik=cik, p=p, S=S, D=D, truth=tl[k], lab=lab, tier=tier, seq=s, cmp=c,
                                       truth_suspect=bool(form_bad or p in iso_truth),
                                       form=r[1] if r else None, year=V3.dd(p).year, sy=V3.dd(S).year, nh=nh,
                                       w5253=w5253, trans=trans_reg or gen_reg, status=status))
            j += 1
        if n_r % 250 == 0:
            print(split, n_r, len(ciks), len(trials), flush=True)
    return dict(trials=trials, hist=hist, v4=v4, bench=bench, bench_reg=bench_reg, regs=regs_seen,
                network=client.fetched)


def summarise(res):
    trials, hist = res["trials"], res["hist"]

    def method_stats(get):
        by_reg = defaultdict(lambda: [0, 0])
        c = Counter()
        for tr in trials:
            lab = get(tr)
            if lab in (None, "conflict"):
                c["abstained"] += 1
                continue
            ok = lab == tr["truth"]
            c["correct" if ok else "incorrect"] += 1
            by_reg[tr["cik"]][0] += not ok
            by_reg[tr["cik"]][1] += 1
        acc = c["correct"] + c["incorrect"]
        regs_err = sum(1 for v in by_reg.values() if v[0])
        return dict(attempted=len(trials), correct=c["correct"], incorrect=c["incorrect"], abstained=c["abstained"],
                    precision=R.fmt(R.rate(c["correct"], acc)), recall=R.fmt(R.rate(c["correct"], len(trials))),
                    error_rate=R.fmt(R.rate(c["incorrect"], acc)),
                    error_rate_upper95_cluster=R.fmt(R.cluster_upper({k: tuple(v) for k, v in by_reg.items()}), 5),
                    registrants_with_accepted=len(by_reg), registrants_with_error=regs_err,
                    registrant_error_share_upper95_cp=R.fmt(R.cp_upper(regs_err, len(by_reg)), 5))

    # addendum 1: non-gating truth-audited view (trials whose TRUE label is form-inconsistent or isolated off-cycle
    # in the registrant's own L0/L1 sequence are set aside; defined from the truth labels only)
    all_trials = trials
    trials = [tr for tr in all_trials if not tr["truth_suspect"]]
    audited = {"R*_L2": method_stats(lambda tr: tr["lab"] if tr["tier"] == "L2" else None),
               "M-SEQ": method_stats(lambda tr: tr["seq"]), "M-CMP": method_stats(lambda tr: tr["cmp"])}
    audited["truth_suspect_trials"] = len(all_trials) - len(trials)
    trials = all_trials
    meth = {"R*_L2": method_stats(lambda tr: tr["lab"] if tr["tier"] == "L2" else None),
            "R*_L2_or_L3": method_stats(lambda tr: tr["lab"] if tr["tier"] in ("L2", "L3") else None),
            "M-SEQ": method_stats(lambda tr: tr["seq"]),
            "M-CMP": method_stats(lambda tr: tr["cmp"])}
    tiers = Counter(tr["tier"] for tr in trials)

    def strata(key):
        g = defaultdict(lambda: Counter())
        for tr in trials:
            k = key(tr)
            if tr["tier"] == "L2":
                g[k]["accepted"] += 1
                g[k]["incorrect"] += tr["lab"] != tr["truth"]
            else:
                g[k]["abstained"] += 1
        return {str(k): dict(v, error_rate=R.fmt(R.rate(v["incorrect"], v["accepted"]))) for k, v in sorted(g.items(), key=lambda kv: str(kv[0]))}

    st = dict(form=strata(lambda tr: tr["form"]), period_year=strata(lambda tr: tr["year"]),
              w5253=strata(lambda tr: tr["w5253"]), fiscal_transition_registrant=strata(lambda tr: tr["trans"]),
              hidden_depth=strata(lambda tr: "1-4" if tr["nh"] <= 4 else ("5-8" if tr["nh"] <= 8 else "9-12")),
              pseudo_start_year=strata(lambda tr: tr["sy"]), universe_status=strata(lambda tr: tr["status"]))
    # ---- history level
    hc = Counter((h["true"], h["rec"]) for h in hist)
    fv_reg = defaultdict(bool)
    for h in hist:
        if h["change_hidden"]:
            fv_reg[h["cik"]] |= h["rec"] == "valid"
    v3_n, v3_k = len(fv_reg), sum(fv_reg.values())
    rp = Counter((h["true"], h["rp_strict"], h["rp_assume"]) for h in hist)
    # ---- V1..V4
    m = meth["R*_L2"]
    v4 = res["v4"]
    f_off, f_n = sum(v[0] for v in v4.values()), sum(v[1] for v in v4.values())
    l_off, l_n = sum(v[2] for v in v4.values()), sum(v[3] for v in v4.values())
    f_rate, l_rate = R.rate(f_off, f_n), R.rate(l_off, l_n)
    f_up = R.cluster_upper({k: (v[0], v[1]) for k, v in v4.items() if v[1]})
    v4_regs = sum(1 for v in v4.values() if v[1])
    bench = res["bench"]
    crit = dict(
        V1=dict(value=m["error_rate_upper95_cluster"], threshold=0.005, n_registrants=m["registrants_with_accepted"],
                status="insufficient" if m["registrants_with_accepted"] < 300 else
                ("pass" if m["error_rate_upper95_cluster"] is not None and m["error_rate_upper95_cluster"] <= 0.005 else "fail")),
        V2=dict(value=m["registrant_error_share_upper95_cp"], threshold=0.02, n_registrants=m["registrants_with_accepted"],
                status="insufficient" if m["registrants_with_accepted"] < 300 else
                ("pass" if m["registrant_error_share_upper95_cp"] is not None and m["registrant_error_share_upper95_cp"] <= 0.02 else "fail")),
        V3=dict(false_valid_registrants=v3_k, registrants=v3_n, value=R.fmt(R.cp_upper(v3_k, v3_n), 5), threshold=0.10,
                status="insufficient" if v3_n < 20 else ("pass" if R.cp_upper(v3_k, v3_n) <= 0.10 else "fail")),
        V4=dict(first4_rate=R.fmt(f_rate, 5), later_rate=R.fmt(l_rate, 5), first4_upper95_cluster=R.fmt(f_up, 5),
                first4_n=f_n, later_n=l_n, registrants=v4_regs,
                bound=R.fmt(max(2 * (l_rate or 0), (l_rate or 0) + 0.005), 5),
                status="insufficient" if v4_regs < 200 else
                ("pass" if f_rate is not None and f_rate <= max(2 * (l_rate or 0), (l_rate or 0) + 0.005) and f_up <= 0.02 else "fail")),
        V5_benchmark=dict(usable=bench["usable"], disagree=bench["disagree"], unusable=bench["unusable"],
                          disagreement_rate=R.fmt(R.rate(bench["disagree"], bench["usable"]), 5)))
    return dict(registrants=res["regs"], trials=len(trials), histories=len(hist), tiers=dict(tiers), methods=meth,
                addendum1_truth_audited_non_gating=audited,
                strata=st, history_true_vs_reconstructed={f"{a}->{b}": v for (a, b), v in sorted(hc.items())},
                history_l2l3_true_vs_reconstructed={f"{a}->{b}": v for (a, b), v in sorted(Counter((h['true'], h['rec3']) for h in hist).items())},
                rule_p_on_pseudo_histories={f"true:{a}|P-strict:{b}|P-assume:{c}": v for (a, b, c), v in sorted(rp.items())},
                criteria=crit, network_requests=res["network"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=("dev", "heldback"), required=True)
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    if a.split == "heldback":
        fr = json.loads(FREEZE.read_text())
        h = hashlib.sha256((HERE / "lh_cp3_rules.py").read_bytes()).hexdigest()
        if h != fr["lh_cp3_rules_sha256"]:
            raise SystemExit("STOP: lh_cp3_rules.py differs from the frozen rules")
        out_p = HERE / "LH_CP3_heldback.json"
    else:
        out_p = HERE / ("LH_CP3_development.json" if not a.limit else "_dev_limit.json")
    res = evaluate(a.split, a.limit)
    out = dict(kind=f"LH-CP3 hidden-label validation - {a.split} registrants (aggregates; metadata only; no returns)",
               decision="D244", split=a.split, cut_off=SAFE.CUT,
               rules_sha256=hashlib.sha256((HERE / "lh_cp3_rules.py").read_bytes()).hexdigest(),
               protocol_sha256=hashlib.sha256((HERE / "LH_CP3_protocol.md").read_bytes()).hexdigest(),
               returns_computed=False, quantconnect_run=False, holdout_accessed=False, **summarise(res))
    if a.split == "dev":
        errs = [tr for tr in res["trials"] if tr["tier"] == "L2" and tr["lab"] != tr["truth"]]
        out["dev_error_examples"] = [dict(cik=e["cik"], period_end=str(V3.dd(e["p"])), truth=e["truth"], lab=e["lab"],
                                          seq=e["seq"], cmp=e["cmp"], form=e["form"]) for e in errs[:40]]
    SAFE.assert_no_post_cutoff(out)
    out_p.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    DATA.save_cache(f"validation_{a.split}.pkl", res)
    print(json.dumps(dict(methods=out["methods"], criteria=out["criteria"], tiers=out["tiers"]), indent=1))


if __name__ == "__main__":
    main()
