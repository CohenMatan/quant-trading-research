"""P13-CP5 (owner D238): H028 conditional-null STRUCTURAL audit on SYNTHETIC panels -> P13_CP5_audit.json.

Question: does the frozen H028 LOWVOL-conditional null (qr_h027.conditional_permuted: LOWVOL stays with the recipient,
the ten other features move together from a persistent qr_p7_pred.Tether donor) produce more score instability,
turnover or trading cost than an equivalent NO-SIGNAL real pipeline, solely because of universe churn and donor
re-matching?

SYNTHETIC ONLY: no market data, no QuantConnect run, no real return / wealth / IC of H028. Every world runs the FROZEN
code unchanged: qr_h027.conditional_permuted (null features), qr_h028.run_world_fixed (lambda = 100 Ridge per outer year
2015-2021 on every month whose 63-session label exits before the cutoff, scores = X @ beta, qr_h026.simulate: Top-15,
FF12 cap 3, monthly rebalance, $7 per order, 10 bps slippage per side). Synthetic returns have NO relation to any
feature (the 'real' selection is a no-signal real pipeline).

Everything below (calibration, scenarios, sizes, statistics, the audit criterion and the classification rule) is
fixed in this file and committed BEFORE any audit statistic is computed (pre-registration, P13-CP5 section 4).
Calibration uses only committed structural facts (no returns):
  * population size per review: 2011 3,209 rows / 12 reviews = 267; 2021 8,444 / 11 = 768 (E030-01 canary coverage);
  * tether re-formation share: E029-01 canary (3 seeds x 131 reviews): 186,864 recipient rows, 153,249 possible
    continuations, 0 broken -> about 17.6% of recipient-months after the first review are re-paired (entry or donor exit).

    PYTHONPATH=src python research/phase13/cp5/P13_CP5_audit.py
"""
import datetime
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean")]
import qr_h026 as H  # noqa: E402
import qr_h027 as G  # noqa: E402
import qr_h028 as F  # noqa: E402

# ------------------------------------------------------------------------------------------- pre-registered constants
N_MONTHS = 131                      # reviews 2011-01-31 .. 2021-11-30 (the H026/H027/H028 calendar)
N_FIRST, N_LAST = 267, 768          # committed population sizes (see docstring); geometric growth in between
N_NOCHURN = 475                     # S1: constant population = the committed mean (62,288 rows / 131 reviews)
REFORM_TARGET = 0.176               # committed E029-01 re-formation share (realistic churn, S2)
REENTRY_SHARE = 0.5                 # share of entries that are earlier members returning after >= 1 month away
P_EXIT_GRID = tuple(round(0.050 + 0.0025 * i, 4) for i in range(29))     # 0.050 .. 0.120
CAL_SEED = 0                        # calibration panel seed (ids only; never used for a statistic)
FEATS = H.FEATURES
LV = G.LOWVOL
FUND = ("GPA", "ACC", "AG", "CBOP", "CFP", "EQA")   # updated in the stock's filing month only (staggered quarterly)
RHO = {   # monthly-equivalent persistence of the latent feature paths (fundamentals: rho**3 per quarterly update)
    "moderate": dict(MOM=0.80, LOWVOL=0.80, GPA=0.95, ACC=0.88, BM=0.90, AG=0.88, REV1M=0.0, CBOP=0.90, HI52=0.78,
                     CFP=0.90, EQA=0.95),
    "strong": dict(MOM=0.92, LOWVOL=0.92, GPA=0.99, ACC=0.97, BM=0.97, AG=0.97, REV1M=0.0, CBOP=0.97, HI52=0.90,
                   CFP=0.97, EQA=0.99),
}
CORR = {("MOM", "HI52"): 0.55, ("LOWVOL", "HI52"): -0.35, ("LOWVOL", "EQA"): -0.25, ("LOWVOL", "GPA"): -0.10,
        ("LOWVOL", "BM"): 0.15, ("LOWVOL", "MOM"): -0.10, ("BM", "CFP"): 0.45, ("BM", "GPA"): -0.25,
        ("GPA", "EQA"): 0.20, ("GPA", "CFP"): 0.20, ("ACC", "CFP"): -0.35, ("AG", "CBOP"): -0.20, ("AG", "ACC"): 0.25,
        ("CBOP", "GPA"): 0.45, ("CBOP", "CFP"): 0.35, ("HI52", "BM"): -0.30}
SECTORS = 12                        # FF12; sectors stay with the stock (as in the real data)
SECTOR_SD = 0.25                    # sector mean shift of each latent feature
RET_MU, MKT_SD, IDIO_SD = 0.008, 0.04, 0.08          # monthly; beta ~ U(0.6, 1.4); NO feature enters any return
LABEL_MONTHS = 3                    # 63-session label ~ the next three monthly holding returns
LABEL_DAYS = 91                     # label exit = review day + 91 calendar days
REGIMES = ("moderate", "strong")
SCENARIOS = {   # churn multiplier on the calibrated exit probability; persistence override for the ten OTHER features
    "S1_no_churn": dict(churn=0.0, other=None),
    "S2_realistic_churn": dict(churn=1.0, other=None),
    "S3_double_churn": dict(churn=2.0, other=None),
    "S4_other_noise": dict(churn=1.0, other=0.0),       # LOWVOL persistent, the ten others i.i.d. each month
    "S5_other_static": dict(churn=1.0, other=1.0),      # the ten-feature vectors never change
}
MAIN = "S2_realistic_churn"
SIZES = {"S2_realistic_churn": (5, 200)}            # (panel seeds 1..P, null worlds 1..W) per regime
SIZES.update({s: (3, 100) for s in SCENARIOS if s != MAIN})
DIAG_WORLDS = 100                                   # diagnostics on the five main panels per regime
METRICS = ("name_turnover", "total_cost", "top15_survival", "rank_autocorr")   # the four criterion metrics
WORSE = dict(name_turnover="above", total_cost="above", top15_survival="below", rank_autocorr="below")
BAND = (0.005, 0.995)
PASS_SEEDS, FAIL_SEEDS, STRONG_PANELS = 4, 3, 9     # >= 4 of 5 inside; same-direction failure >= 3 of 5; strong fail
#   in >= 9 of the 10 realistic panels (5 seeds x 2 regimes): real below EVERY null world (turnover or cost)
# Stylised defensive coefficient vector for the frozen-coefficient diagnostic (pre-registered, not fitted)
B_DEF = np.array([0.15 if f != "LOWVOL" else -1.0 for f in FEATS])


# ------------------------------------------------------------------------------------------- synthetic panel
def corr_chol():
    C = np.eye(len(FEATS))
    for (a, b), v in CORR.items():
        i, j = FEATS.index(a), FEATS.index(b)
        C[i, j] = C[j, i] = v
    return np.linalg.cholesky(C)          # raises if not positive definite


def month_ends():
    out, y, m = [], 2011, 1
    for _ in range(N_MONTHS + LABEL_MONTHS + 1):
        nxt = datetime.date(y + (m == 12), m % 12 + 1, 1)
        out.append((nxt - datetime.date(1970, 1, 1)).days - 1)
        y, m = nxt.year, nxt.month
    return out


def membership(rng, p_exit, churn):
    """Population ids per review (sorted). S1: constant N_NOCHURN, no entries / exits. Otherwise: geometric growth
    N_FIRST -> N_LAST; each member exits with probability p_exit; entries fill to the target size, REENTRY_SHARE of
    them (when available) are earlier members absent for >= 1 month, the rest brand-new stocks."""
    if not churn:
        return [list(range(N_NOCHURN))] * N_MONTHS, N_NOCHURN
    target = [int(round(N_FIRST * (N_LAST / N_FIRST) ** (t / (N_MONTHS - 1)))) for t in range(N_MONTHS)]
    nxt = N_FIRST
    mem = list(range(N_FIRST))
    out = [sorted(mem)]
    away = []                                   # former members (absent >= 1 month at the next draw)
    for t in range(1, N_MONTHS):
        ex = rng.random(len(mem)) < p_exit * churn
        stay = [s for s, e in zip(mem, ex) if not e]
        left = [s for s, e in zip(mem, ex) if e]
        need = max(target[t] - len(stay), 0)
        new = []
        for _ in range(need):
            if away and rng.random() < REENTRY_SHARE:
                new.append(away.pop(int(rng.integers(len(away)))))
            else:
                new.append(nxt)
                nxt += 1
        away.extend(left)
        mem = stay + new
        out.append(sorted(mem))
    return out, nxt


def panel(seed, regime, scen):
    """One synthetic panel = a list of H026 'months' dicts (ids, sector, X, label, exit_day, cutoff_day, test_year,
    open_ok, r_oo, r_oc, alive_next, alive_end, daily, days, spy_*)."""
    sc = SCENARIOS[scen]
    rng = np.random.default_rng([13, 5, REGIMES.index(regime), list(SCENARIOS).index(scen), seed])
    p_exit = calibrated_p_exit()
    mem, n_all = membership(rng, p_exit, sc["churn"])
    L = corr_chol()
    rho = np.array([RHO[regime][f] for f in FEATS], float)
    fund = np.array([f in FUND for f in FEATS])
    if sc["other"] is not None:
        oth = np.arange(len(FEATS)) != LV
        rho[oth] = sc["other"]
        fund = fund & ~oth                      # S4 / S5: the ten others follow the override every month
    rq = rho ** 3
    k = len(FEATS)
    z = (L @ rng.standard_normal((k, n_all))).T
    sector = rng.integers(0, SECTORS, n_all)
    phase = rng.integers(0, 3, n_all)
    shift = rng.normal(0.0, SECTOR_SD, (SECTORS, k))
    beta_m = rng.uniform(0.6, 1.4, n_all)
    T = N_MONTHS + LABEL_MONTHS
    mkt = rng.normal(0.0, MKT_SD, T)
    ret = RET_MU + beta_m[None, :] * mkt[:, None] + rng.normal(0.0, IDIO_SD, (T, n_all))
    days = month_ends()
    months = []
    for t in range(N_MONTHS):
        if t:
            e = (L @ rng.standard_normal((k, n_all))).T
            upd = (phase[:, None] == t % 3) & fund[None, :]
            mon = ~fund[None, :]
            r_m = np.where(mon, rho, np.where(upd, rq, 1.0))
            z = r_m * z + np.sqrt(1.0 - r_m ** 2) * e
        ids = np.array(mem[t], dtype=np.int64)
        raw = z[ids] + shift[sector[ids]]
        X = H.feature_matrix(raw)
        lab = H.centred_percentile(ret[t:t + LABEL_MONTHS, ids].sum(0))
        r = ret[t, ids]
        day = days[t]
        months.append(dict(ids=ids.tolist(), sector=sector[ids].tolist(), X=X, label=lab, exit_day=day + LABEL_DAYS,
                           cutoff_day=day, day=day, test_year=int(str(np.datetime64(day, "D"))[:4]),
                           open_ok=np.ones(ids.size, bool), r_oo=r, r_oc=r, alive_next=np.ones(ids.size, bool),
                           alive_end=np.ones(ids.size, bool), daily=r[None, :], days=np.array([day + 15]),
                           spy_oo=RET_MU + float(mkt[t]), spy_oc=RET_MU + float(mkt[t]),
                           spy_daily=np.array([RET_MU + float(mkt[t])])))
    return months


_P_EXIT = {}


def calibrated_p_exit():
    """The grid exit probability whose tether re-formation share on the calibration membership (ids only, CAL_SEED,
    tether seeds 1-3, as the committed E029-01 canary) is closest to REFORM_TARGET."""
    if "p" not in _P_EXIT:
        best = None
        for p in P_EXIT_GRID:
            mem, _ = membership(np.random.default_rng([13, 5, 99, CAL_SEED]), p, 1.0)
            share = np.mean([reform(mem, s)["reform_share"] for s in (1, 2, 3)])
            if best is None or abs(share - REFORM_TARGET) < abs(best[1] - REFORM_TARGET):
                best = (p, share)
        _P_EXIT["p"], _P_EXIT["share"] = best
    return _P_EXIT["p"]


def reform(mem, seed):
    """Donor re-mapping audit of the frozen tether on a sequence of id lists: recipient rows after the first review,
    possible continuations (recipient and its previous donor both present), kept, and the causes of re-formation."""
    T = G.R.Tether(seed)
    prev = None
    c = dict(rows=0, possible=0, kept=0, new_recipient=0, donor_exited=0, splice=0)
    per = []
    for ids in mem:
        d = dict(zip(ids, T.step(ids)))
        if prev is not None:
            pos = set(ids)
            m = dict(rows=0, reformed=0)
            for s in ids:
                c["rows"] += 1
                m["rows"] += 1
                if s not in prev:
                    c["new_recipient"] += 1
                    m["reformed"] += 1
                elif prev[s] not in pos:
                    c["donor_exited"] += 1
                    m["reformed"] += 1
                else:
                    c["possible"] += 1
                    if d[s] == prev[s]:
                        c["kept"] += 1
                    else:
                        c["splice"] += 1
                        m["reformed"] += 1
            per.append(m["reformed"] / m["rows"])
        prev = d
    c["reform_share"] = 1.0 - c["kept"] / c["rows"] if c["rows"] else 0.0
    c["monthly_reform_median"] = float(np.median(per)) if per else 0.0
    return c


# ------------------------------------------------------------------------------------------- structural statistics
def spearman(a, b):
    ra, rb = H.avg_rank(a), H.avg_rank(b)
    return float(np.corrcoef(ra, rb)[0, 1])


def structure(ms_out, scores, h):
    """Structural statistics of one portfolio path over the outer months (2015-01 .. 2021-11)."""
    picks = h["picks"]
    K = H.K
    new = [len(set(picks[t]) - set(picks[t - 1])) for t in range(1, len(picks))]
    surv = [len(set(picks[t]) & set(picks[t - 1])) / len(picks[t - 1]) for t in range(1, len(picks)) if picks[t - 1]]
    rac, dsc, dtop = [], [], []
    for t in range(1, len(ms_out)):
        a, b = ms_out[t - 1], ms_out[t]
        pa = {s: i for i, s in enumerate(a["ids"])}
        pb = {s: i for i, s in enumerate(b["ids"])}
        com = [s for s in a["ids"] if s in pb]
        ia = np.array([pa[s] for s in com])
        ib = np.array([pb[s] for s in com])
        sa, sb = np.asarray(scores[t - 1])[ia], np.asarray(scores[t])[ib]
        rac.append(spearman(sa, sb))
        qa, qb = H.centred_percentile(sa), H.centred_percentile(sb)
        dsc.append(float(np.mean(np.abs(qb - qa))))
        held = [k for k, s in enumerate(com) if s in set(picks[t - 1])]
        if held:
            dtop.append(float(np.mean(np.abs(qb[held] - qa[held]))))
    return dict(name_turnover=float(np.mean(new)) / K, new_names=float(np.mean(new)), top15_survival=float(np.mean(surv)),
                rank_autocorr=float(np.mean(rac)), score_change=float(np.mean(dsc)), top15_rank_change=float(np.mean(dtop)),
                trades=int(h["trades"]), commissions=float(h["commissions"]), slippage=float(h["slippage"]),
                total_cost=float(h["commissions"] + h["slippage"]), value_turnover=float(np.mean(h["turnover"])),
                wealth=float(h["wealth"]))


def coef_stats(w):
    B = np.array([w["coef"][(Y, F.LAMBDA)][1] for Y in H.OUTER_YEARS])
    cos = [float(B[i] @ B[i + 1] / (np.linalg.norm(B[i]) * np.linalg.norm(B[i + 1]))) for i in range(len(B) - 1)]
    l1 = np.abs(B).sum(1)
    return dict(coef_cos_consecutive=float(np.mean(cos)), lowvol_l1_share=float(np.mean(np.abs(B[:, LV]) / l1)),
                coef_l2=float(np.mean(np.linalg.norm(B, axis=1))))


def run_full(months, Xs, seed):
    w = F.run_world_fixed(months, Xs, full=True, seed=seed)
    ms_out = [months[i] for i in w["idx"]]
    st = structure(ms_out, w["scores"], w["h"])
    st.update(coef_stats(w))
    st["S_WEALTH_synthetic"] = float(w["rec"]["S_WEALTH"])
    zc = F.replay(ms_out, w["scores"], comm=0.0, slip=0.0)          # zero-cost diagnostic: same scores, no costs
    st["zero_cost_orders"] = int(sum(m["orders"] for m in zc["months"]))
    return st, w


def fixed_coef(months, Xs, B_by_year):
    """Frozen-coefficient diagnostic: scores = X @ beta with beta fixed per outer year (no refit), frozen simulate."""
    first = {Y: H.year_months(months, Y) for Y in H.OUTER_YEARS}
    idx = [i for Y in H.OUTER_YEARS for i in first[Y]]
    ms_out = [months[i] for i in idx]
    sc = [Xs[i] @ B_by_year[months[i]["test_year"]] for i in idx]
    h = H.simulate(ms_out, sc, keep_trades=True)
    return structure(ms_out, sc, h)


def band(real, null):
    v = np.asarray(null, float)
    lo, hi = (float(np.quantile(v, q)) for q in BAND)
    pos = "inside" if lo <= real <= hi else ("below" if real < lo else "above")
    return dict(real=real, null_q005=lo, null_q995=hi, null_min=float(v.min()), null_max=float(v.max()),
                null_median=float(np.median(v)), gap_median=float(np.median(v) - real),
                real_pct=float(np.mean(v < real) + 0.5 * np.mean(v == real)), position=pos,
                real_below_all=bool(real < v.min()), real_above_all=bool(real > v.max()))


STAT_KEYS = METRICS + ("new_names", "score_change", "top15_rank_change", "trades", "commissions", "slippage",
                       "value_turnover", "coef_cos_consecutive", "lowvol_l1_share", "zero_cost_orders")


def scenario(scen, regime, log):
    P, W = SIZES[scen]
    out = []
    for p in range(1, P + 1):
        t0 = time.time()
        ms = panel(p, regime, scen)
        real, wr = run_full(ms, [m["X"] for m in ms], None)
        nulls = [run_full(ms, G.conditional_permuted(ms, s), s)[0] for s in range(1, W + 1)]
        rf = reform([m["ids"] for m in ms], 1)
        rec = dict(panel_seed=p, worlds=W, reform=rf, real=real,
                   bands={k: band(real[k], [n[k] for n in nulls]) for k in STAT_KEYS},
                   null_S_synthetic_median=float(np.median([n["S_WEALTH_synthetic"] for n in nulls])),
                   null_cost_median=float(np.median([n["total_cost"] for n in nulls])),
                   null_wealth_median=float(np.median([n["wealth"] for n in nulls])))
        if scen == MAIN:
            rec["diagnostics"] = diagnostics(ms, wr, p, regime)
        out.append(rec)
        log(f"{scen} {regime} panel {p}: {time.time() - t0:.0f}s")
    return out


def diagnostics(ms, wr, p, regime):
    """On each main panel (DIAG_WORLDS worlds): one mechanism changed at a time."""
    seeds = range(1, DIAG_WORLDS + 1)
    Xr = [m["X"] for m in ms]
    B_real = {Y: wr["coef"][(Y, F.LAMBDA)][1] for Y in H.OUTER_YEARS}
    B_def = {Y: B_DEF for Y in H.OUTER_YEARS}
    com = json.loads((ROOT / "research/phase13/cp1/P13_CP1_result.json").read_text())["coefficients"]
    B_com = {Y: np.array(com[str(Y)]["beta"], float) for Y in H.OUTER_YEARS}
    out = {}
    for name, B in (("frozen_coef_real_fit", B_real), ("frozen_coef_defensive", B_def),
                    ("frozen_coef_committed_h028", B_com)):
        r = fixed_coef(ms, Xr, B)
        nl = [fixed_coef(ms, G.conditional_permuted(ms, s), B) for s in seeds]
        out[name] = {k: band(r[k], [n[k] for n in nl]) for k in METRICS + ("new_names",)}
    # LOWVOL anchoring: all eleven features from the donor (the frozen H026 tether permutation) -- diagnostic only
    r, _ = run_full(ms, Xr, None)
    nl = [run_full(ms, H.permuted(ms, s), s)[0] for s in seeds]
    out["anchoring_all_eleven_moved"] = {k: band(r[k], [n[k] for n in nl]) for k in METRICS + ("new_names",)}
    return out


# ------------------------------------------------------------------------------------------- criterion
def criterion(res):
    """The pre-registered audit rule on the main realistic scenario (S2), per regime and metric."""
    out = dict(per_regime={}, strong_fail={})
    for rg in REGIMES:
        panels = res[MAIN][rg]
        per = {}
        for k in METRICS:
            pos = [pp["bands"][k]["position"] for pp in panels]
            inside = pos.count("inside")
            worse = pos.count(WORSE[k])
            better = len(pos) - inside - worse
            per[k] = dict(positions=pos, inside=inside, passes=inside >= PASS_SEEDS,
                          directional_failure=("null_worse" if worse >= FAIL_SEEDS else
                                               "null_better" if better >= FAIL_SEEDS else None))
        out["per_regime"][rg] = per
    for k in ("name_turnover", "total_cost"):
        n = sum(pp["bands"][k]["real_below_all"] for rg in REGIMES for pp in res[MAIN][rg])
        out["strong_fail"][k] = dict(panels_real_below_every_world=int(n), strong=n >= STRONG_PANELS)
    strong = any(v["strong"] for v in out["strong_fail"].values())
    all_pass = all(out["per_regime"][rg][k]["passes"] and out["per_regime"][rg][k]["directional_failure"] is None
                   for rg in REGIMES for k in METRICS)
    both = [k for k in METRICS if all(out["per_regime"][rg][k]["directional_failure"] for rg in REGIMES)]
    # AMENDMENT 1 (committed before any audit result was read): owner section 19 literally -- a same-direction failure
    # in >= 3 of 5 main panel seeds makes the null structurally suspect; it is applied in EACH regime (the first
    # commit required it in both regimes, which would have weakened the owner's rule)
    either = [(rg, k) for rg in REGIMES for k in METRICS if out["per_regime"][rg][k]["directional_failure"]]
    if strong or either:
        cls = "B"
    elif all_pass:
        cls = "A"
    else:
        cls = "C"
    out.update(directional_failure_in_both_regimes=both, directional_failures=either, classification=cls, label={
        "A": "H028 NULL STRUCTURAL AUDIT — PASS / HISTORICAL CONDITIONAL-NULL EVIDENCE REMAINS STRUCTURALLY SUPPORTED",
        "B": "H028 NULL STRUCTURAL AUDIT — FAIL / HISTORICAL CONDITIONAL-NULL SIGNIFICANCE IS STRUCTURALLY SUSPECT",
        "C": "H028 NULL STRUCTURAL AUDIT — INCONCLUSIVE"}[cls])
    return out


RULE = """Per regime (moderate, strong) and metric (name turnover, total trading cost, Top-15 one-month survival,
score-rank autocorrelation): the synthetic real value is compared with the null [0.5%, 99.5%] band of its own panel.
A metric PASSES in a regime if inside in >= 4 of 5 panel seeds; a DIRECTIONAL FAILURE is the same side outside in
>= 3 of 5 seeds. STRONG FAIL: real turnover (or real cost) below EVERY null world in >= 9 of the 10 realistic panels.
Classification (Amendment 1, committed before any result was read): B (structurally suspect) if a strong fail, or a
directional failure of any criterion metric in EITHER regime (owner section 19 applied to each regime's 5 seeds);
A (structurally supported) if every metric passes in both regimes with no directional failure; C (inconclusive)
otherwise. In every case H028 remains REJECTED, no corrected p-value is computed and no replacement null is proposed."""


def main():
    t0 = time.time()
    log = lambda s: print(f"[{time.time() - t0:7.0f}s] {s}", flush=True)  # noqa: E731
    p = calibrated_p_exit()
    log(f"calibrated p_exit {p} (re-formation share {_P_EXIT['share']:.4f})")
    res = {}
    for scen in SCENARIOS:
        res[scen] = {rg: scenario(scen, rg, log) for rg in REGIMES}
    crit = criterion(res)
    body = dict(checkpoint="P13-CP5", decision="D238", synthetic_only=True, quantconnect_runs=0, returns_read=False,
                holdout_accessed=False, new_null=False, frozen_code_sha256={
                    f: hashlib.sha256((ROOT / "src/qresearch/lean" / f).read_bytes()).hexdigest()
                    for f in ("qr_h026.py", "qr_h027.py", "qr_h028.py", "qr_p7_pred.py", "qr_h020_stats.py")},
                calibration=dict(p_exit=p, reform_share_calibration=_P_EXIT["share"], reform_target=REFORM_TARGET,
                                 n_first=N_FIRST, n_last=N_LAST, n_nochurn=N_NOCHURN, reentry_share=REENTRY_SHARE),
                sizes={k: dict(panel_seeds=v[0], null_worlds=v[1]) for k, v in SIZES.items()},
                rule=RULE, criterion=crit, results=res)
    txt = json.dumps(body, indent=1, sort_keys=True, default=float)
    (HERE / "P13_CP5_audit.json").write_text(txt + "\n")
    log(f"done: {crit['label']}; sha256 {hashlib.sha256(txt.encode()).hexdigest()[:16]}")


def reclassify():
    """Recompute the criterion from the stored results with the amended rule (the run that produced the results
    imported the first-committed rule; both are kept in the JSON)."""
    path = HERE / "P13_CP5_audit.json"
    body = json.loads(path.read_text())
    if "criterion_first_commit" not in body:
        body["criterion_first_commit"] = body["criterion"]
    body["criterion"] = criterion(body["results"])
    body["rule"] = RULE
    txt = json.dumps(body, indent=1, sort_keys=True, default=float)
    path.write_text(txt + "\n")
    print(body["criterion"]["label"], hashlib.sha256(txt.encode()).hexdigest()[:16])


if __name__ == "__main__":
    reclassify() if "--reclassify" in sys.argv else main()
