"""P14-CP4 (owner D235): H029 structural turnover post-mortem -> P14_CP4_postmortem.json.

STRUCTURAL ONLY. No return of any kind is read, derived or shown:
  * from the committed null rows only the columns turn29, hhi29, turn30, hhi30 are extracted (the return / wealth /
    capture / risk columns are dropped on load and never used);
  * no QuantConnect run; no 2022+ data; no new null; no threshold.

Inputs (committed artifacts): P14_CP3b_null.json / _rows.json (sector null), P14_CP3_null_rows.json (original null),
P14_CP3b_canary.json (tether accounting, eligible counts), P14_CP1_audit.json (feature update cadence, E802-01).

Mechanism verification uses SYNTHETIC panels (no market data) run through the frozen qr_h029 / qr_h026 code: the
sector-stratified null is an exact relabelling of the real selection while donor pairs persist, so its turnover can
differ from the real turnover only through re-formed pairs (universe churn, sector changes, splices) and score ties.

    PYTHONPATH=src python research/phase14/cp4/P14_CP4_postmortem.py
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean")]
import qr_h029 as Q  # noqa: E402

CP3 = ROOT / "research/phase14/cp3"
STRUCT = ("turn29", "hhi29", "turn30", "hhi30")
K = 15
PRIMARY = {"F1": "F1Q", "F2": "F2", "F4": "F4B", "F5": "F5A", "F7": "F7", "F8": "F8"}   # P14-CP1 primary forms


def structural_columns(path):
    """Only the score-only selection-structure columns of committed null rows (return columns dropped on load)."""
    d = json.loads(path.read_text())
    ix = {f: d["fields"].index(f) for f in STRUCT}
    out = {f: np.array([w[i] for w in d["worlds"]], float) for f, i in ix.items()}
    del d
    return out


def q(x):
    x = np.asarray(x, float)
    return {"min": float(x.min()), "p0.5": float(np.percentile(x, 0.5)), "p5": float(np.percentile(x, 5)),
            "p50": float(np.median(x)), "p95": float(np.percentile(x, 95)), "p99.5": float(np.percentile(x, 99.5)),
            "max": float(x.max()), "mean": float(x.mean()), "sd": float(x.std(ddof=1))}


def pct(x, v):
    x = np.asarray(x, float)
    return float(100.0 * np.mean(x < v) + 50.0 * np.mean(x == v))


# ------------------------------------------------------------------------------------------- real-data aggregates
def reproduction():
    sec = structural_columns(CP3 / "P14_CP3b_null_rows.json")
    org = structural_columns(CP3 / "P14_CP3_null_rows.json")
    real = json.loads((CP3 / "P14_CP3b_null.json").read_text())["real_selection_structure"]
    real_o = json.loads((CP3 / "P14_CP3_null.json").read_text())["real_selection_structure"]
    assert all(abs(real[k] - real_o[k]) < 1e-15 for k in STRUCT), "real selection structure differs between nulls"
    out = {}
    for f in STRUCT:
        out[f] = dict(real=real[f], sector_null=q(sec[f]), original_null=q(org[f]),
                      real_pct_sector=pct(sec[f], real[f]), real_pct_original=pct(org[f], real[f]),
                      sector_worlds_at_or_below_real=int((sec[f] <= real[f]).sum()))
    t, m, mn = real["turn29"], float(np.median(sec["turn29"])), float(sec["turn29"].min())
    out["plain_english"] = dict(
        names_entering_per_rebalance=dict(real=t * K, sector_null_median=m * K, sector_null_min=mn * K),
        extra_names_per_rebalance_vs_median=(m - t) * K, extra_names_per_year_vs_median=(m - t) * K * 12,
        extra_names_per_rebalance_vs_min=(mn - t) * K, extra_names_per_year_vs_min=(mn - t) * K * 12,
        transitions=83, extra_names_over_83_transitions_vs_median=(m - t) * K * 83)
    return out, real


def cadence():
    a = json.loads((ROOT / "research/phase14/cp1/P14_CP1_audit.json").read_text())
    rows = {}
    for f, form in PRIMARY.items():
        u, s = a["update"][form], a["staleness"][form]["overall"]
        rows[f] = dict(form=form, share_of_stock_months_changed=u["share_changed"],
                       share_unchanged=1.0 - u["share_changed"], value_runs=u["runs"],
                       months_between_changes=dict(p25=u["run_p25"], p50=u["run_median"], p75=u["run_p75"]),
                       report_age_days=dict(p50=s["p50"], p75=s["p75"], p90=s["p90"], p95=s["p95"], max=s["max"]))
    return dict(source="P14_CP1_audit.json (E802-01, Data v2.1 view, 131 reviews 2011-2021, H029-A audit universe)",
                features=rows)


def tether_accounting(real_turn):
    c = json.loads((CP3 / "P14_CP3b_canary.json").read_text())["details"]
    n = np.asarray(c["h029_months"], float)
    nc = c["null_checks"]
    seeds = len(nc["seeds"])
    recip_t = float(n[1:].sum())
    possible, kept = nc["persist_possible"] / seeds, nc["persist_kept"] / seeds
    not_possible = recip_t - possible
    broken = possible - kept
    net = float(n[-1] - n[0])
    # not_possible = entries + (old recipients whose donor exited / pair crossed sectors); net = entries - exits
    disrupted_lo = (not_possible - net) / 2.0          # = exits if sector changes are 0 (lower bound on f)
    p = 1.0 - real_turn                                # lower bound of P(held at t-1 | held at t, eligible at t-1)
    est = float(np.mean([disrupted_lo / 83.0 * (p - K / nt) / nt for nt in n[1:]]))
    return dict(eligible_per_review=dict(mean=float(n.mean()), min=float(n.min()), max=float(n.max()), first=float(n[0]),
                                         last=float(n[-1])),
                per_seed=dict(recipients_after_first_review=recip_t, possible_pairs=possible, kept=kept,
                              broken_possible=broken, re_formed_not_possible=not_possible),
                per_review=dict(re_formed_total=(not_possible + broken) / 83.0, re_formed_by_eligibility_or_sector=not_possible / 83.0,
                                broken_possible_splices=broken / 83.0, net_universe_growth=net / 83.0,
                                disrupted_old_pairs_lower_bound=disrupted_lo / 83.0),
                share_of_recipients_re_formed_per_review=(not_possible + broken) / recip_t,
                canary_persistence_metric=dict(kept=nc["persist_kept"], possible=nc["persist_possible"],
                                               share=nc["persist_kept"] / nc["persist_possible"],
                                               note="'possible' = previous donor still eligible AND same sector "
                                                    "(amendment A5); re-formations forced by eligibility churn are "
                                                    "outside its denominator"),
                estimate=dict(formula="mean_t f (p - 15/n_t) / n_t, f = disrupted old pairs per review (lower bound), "
                                      "p = 1 - real turnover (lower bound)",
                              f=disrupted_lo / 83.0, p=p, extra_turnover=est))


# ------------------------------------------------------------------------------------------- synthetic verification
def panel(seed, months=84, n0=700, exits=18, entries=22, sectors=11, persist=0.9, cluster=1.0):
    """SYNTHETIC: persistent six-signal latent per stock updated quarterly (staggered), random exits / entries."""
    rng = np.random.default_rng(seed)
    lat, sec, phase, nxt = {}, {}, {}, [0]

    def add():
        s = f"S{nxt[0]:06d}"
        nxt[0] += 1
        lat[s], sec[s], phase[s] = rng.normal(size=6), int(rng.integers(sectors)), int(rng.integers(3))
        return s
    alive = [add() for _ in range(n0)]
    ms, Vs, Hs = [], [], []
    h28 = {}
    for t in range(months):
        if t:
            out = set(rng.choice(len(alive), exits, replace=False).tolist()) if exits else set()
            alive = [s for k, s in enumerate(alive) if k not in out] + [add() for _ in range(entries)]
        for s in alive:
            if (t + phase[s]) % 3 == 0:
                lat[s] = persist * lat[s] + np.sqrt(1 - persist ** 2) * rng.normal(size=6)
            h28[s] = 0.95 * h28.get(s, rng.normal()) + np.sqrt(1 - 0.95 ** 2) * rng.normal()
        ids = sorted(alive)
        sc = np.array([sec[s] for s in ids])
        ms.append(dict(ids=ids, sector=sc, open_ok=np.ones(len(ids), bool), day=t))
        Vs.append(np.array([lat[s] for s in ids]) + cluster * sc[:, None] / 5.0)
        Hs.append(np.array([h28[s] for s in ids]))
    return ms, Vs, Hs


def keyed_scores(ms, Vs, seed):
    """H029 scores plus a vanishing stock-intrinsic key that travels with each vector (removes score ties; verification
    only -- the frozen pick breaks ties by recipient id)."""
    if seed is None:
        maps = [dict(zip(m["ids"], m["ids"])) for m in ms]
        V = Vs
    else:
        maps = Q.donors(ms, seed)
        V = Q.tether_vectors(ms, Vs, seed)
    out = []
    for m, sc, d in zip(ms, Q.h029_scores(V), maps):
        key = np.array([int(d[s][1:]) for s in m["ids"]], float)
        out.append(sc + 1e-12 * key / (1.0 + key.max()))
    return out, maps


def sets(ms, scores):
    return [set(m["ids"][i] for i in Q.H.pick(m, s)) for m, s in zip(ms, scores)]


def decompose(ms, real_s, null_s, maps):
    """Exact: N_t - R_t = sum over B in S_t whose pair is re-formed of (1[A not in S'_{t-1}] - 1[B not in S_{t-1}])."""
    diff, by = 0, {"donor_new_entrant": 0, "donor_freed_recipient_exited": 0, "other_re_formed": 0}
    check = True
    for t in range(1, len(ms)):
        S, Sp, N, Np = real_s[t], real_s[t - 1], null_s[t], null_s[t - 1]
        prev_ids, cur_ids, cur, prv = set(ms[t - 1]["ids"]), set(ms[t]["ids"]), maps[t], maps[t - 1]
        inv = {b: a for a, b in cur.items()}
        prv_inv = {b: a for a, b in prv.items()}
        lhs = len(N - Np) - len(S - Sp)
        rhs = 0
        for b in S:
            a = inv[b]
            kept = a in prev_ids and prv.get(a) == b
            if kept:
                continue
            c = int(a not in Np) - int(b not in Sp)
            rhs += c
            if b not in prev_ids:
                by["donor_new_entrant"] += c
            elif prv_inv.get(b) not in cur_ids:
                by["donor_freed_recipient_exited"] += c
            else:
                by["other_re_formed"] += c
        check &= lhs == rhs
        diff += lhs
    return dict(exact_identity_holds=bool(check), total_extra_entries=diff, by_donor_type=by)


def synthetic():
    res = dict(note="SYNTHETIC panels (no market data, no returns) through the frozen qr_h029 / qr_h026 code")
    # 1. relabelling identity: no churn -> null turnover and HHI identical to the real ones in every world
    ident = {}
    for name, kw in (("no_churn_unclustered", dict(exits=0, entries=0, cluster=0.0)),
                     ("no_churn_sector_clustered_cap_binding", dict(exits=0, entries=0, cluster=1.0)),
                     ("churn_18_22_sector_clustered", dict(exits=18, entries=22, cluster=1.0))):
        ms, Vs, _ = panel(11, **kw)
        r, _m = keyed_scores(ms, Vs, None)
        rt, rh = Q.selection_structure(ms, r)
        nl = [Q.selection_structure(ms, keyed_scores(ms, Vs, s)[0]) for s in range(1, 11)]
        ident[name] = dict(real_turn=rt, real_hhi=rh, null_turn_min=min(x[0] for x in nl),
                           null_turn_max=max(x[0] for x in nl),
                           turn_identical_all_worlds=all(x[0] == rt for x in nl),
                           hhi_identical_all_worlds=all(abs(x[1] - rh) < 1e-12 for x in nl))
    res["relabelling_identity"] = ident
    # 2. exact decomposition of the null-minus-real entries (with churn)
    ms, Vs, _ = panel(12, exits=18, entries=22, cluster=1.0)
    r, _ = keyed_scores(ms, Vs, None)
    S = sets(ms, r)
    dec = []
    for s in (1, 2, 3):
        ns, mp = keyed_scores(ms, Vs, s)
        dec.append(decompose(ms, S, sets(ms, ns), mp))
    res["decomposition_seeds_1_3"] = dec
    # 3. the churn estimate vs simulated gap over a grid (frozen pick incl. its id tie-break)
    grid = []
    for exits, entries, persist in ((9, 11, 0.9), (18, 22, 0.9), (36, 40, 0.9), (18, 22, 0.7), (18, 22, 0.97)):
        ms, Vs, _ = panel(13, exits=exits, entries=entries, persist=persist, cluster=1.0)
        rt = Q.selection_structure(ms, Q.h029_scores(Vs))[0]
        nt = [Q.selection_structure(ms, Q.h029_scores(Q.tether_vectors(ms, Vs, s)))[0] for s in range(1, 21)]
        n = [len(m["ids"]) for m in ms]
        est = float(np.mean([exits * ((1 - rt) - K / x) / x for x in n[1:]]))
        grid.append(dict(exits=exits, entries=entries, quarterly_persistence=persist, real_turn=rt,
                         null_turn_median=float(np.median(nt)), null_turn_min=float(min(nt)),
                         gap_median=float(np.median(nt) - rt), estimate=est,
                         real_below_all_20_worlds=bool(rt < min(nt))))
    res["churn_estimate_grid"] = grid
    # 4. H030-style blend: half the score is the recipient's own persistent H028-like score
    ms, Vs, Hs = panel(14, exits=18, entries=22, cluster=1.0)
    def blend(V):
        return [Q.blend(h, s) for h, s in zip(Hs, Q.h029_scores(V))]
    r29 = Q.selection_structure(ms, Q.h029_scores(Vs))[0]
    r30 = Q.selection_structure(ms, blend(Vs))[0]
    n29, n30 = [], []
    for s in range(1, 41):
        V = Q.tether_vectors(ms, Vs, s)
        n29.append(Q.selection_structure(ms, Q.h029_scores(V))[0])
        n30.append(Q.selection_structure(ms, blend(V))[0])
    res["h030_style_blend"] = dict(
        h029=dict(real=r29, null_median=float(np.median(n29)), null_sd=float(np.std(n29, ddof=1)),
                  real_pct=pct(n29, r29), gap_in_null_sd=float((np.median(n29) - r29) / np.std(n29, ddof=1))),
        h030=dict(real=r30, null_median=float(np.median(n30)), null_sd=float(np.std(n30, ddof=1)),
                  real_pct=pct(n30, r30), gap_in_null_sd=float((np.median(n30) - r30) / np.std(n30, ddof=1))))
    return res


def main():
    rep, real = reproduction()
    out = dict(
        checkpoint="P14-CP4", decision="D235", structural_only=True,
        returns_read=False, holdout_accessed=False, quantconnect_runs=0, new_null=False, thresholds=None,
        reproduction=rep, feature_update_cadence=cadence(),
        tether_accounting=tether_accounting(real["turn29"]),
        sector_null_hhi_note="sector-null H029 HHI spread comes only from score ties (frozen pick breaks ties by "
                             "recipient id) and recipient open_ok; with tie-free scores the null HHI equals the real",
        synthetic=synthetic())
    gap = rep["turn29"]["sector_null"]["p50"] - rep["turn29"]["real"]
    out["tether_accounting"]["estimate"]["observed_gap_vs_sector_median"] = gap
    out["tether_accounting"]["estimate"]["share_of_gap"] = out["tether_accounting"]["estimate"]["extra_turnover"] / gap
    text = json.dumps(out, indent=1, sort_keys=True, default=float) + "\n"
    (HERE / "P14_CP4_postmortem.json").write_text(text)
    print("sha256", hashlib.sha256(text.encode()).hexdigest())
    print(json.dumps(dict(gap=gap, est=out["tether_accounting"]["estimate"]), indent=1, default=float))


if __name__ == "__main__":
    main()
