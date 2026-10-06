"""P7-CP4 (D175): synthetic null calibration and power study for the Phase 7 predictive test (H022) under the FULL
frozen gate procedure (qr_p7_pred). NO REAL RETURN IS USED: the cross-sections are the REAL score tables of E993-02
(scores, eligibility, kept share class, PIT FF12 sector, risk band, momentum band, ADV20 -- no prices), so the score
distribution, its persistence, the changing universe (≈ 340-580 stocks / month), the sector structure and the 83
decision dates are the real ones; the RETURNS are synthetic:
    y_i,t = beta_i m_t + f_sector(i),t + sum_k g_k,t x_k,i,t + sigma_i,t e_i,t + kappa z_i,t
  m_t ~ N(0.8%, 3.5%) market; f_g,t ~ N(0, 2.5%) sector factors; beta_i ~ N(1, 0.25) fixed per security;
  three zero-mean STYLE factors the score itself loads on (so the IC swings month to month as in real data):
  x_k = normal scores of the stock's REAL momentum band, volatility band and fundamental subtotal at t, g_k,t ~ N(0,
  STYLE_SD) per standard deviation of exposure;
  sigma_i,t = idiosyncratic monthly volatility by the stock's REAL volatility band at t (risk points 10 / 7 / 3 / 0 ->
  4.5% / 5.5% / 6.5% / 8.5%), e ~ Student-t(5) scaled to unit variance (fat tails);
  z = normal score of the cross-sectional rank of the score; kappa = the planted monthly edge per standard deviation
  of z (kappa = 0: the null).
Outputs research/phase7/P7_power.json: the synthetic critical value, the size of the significance gate and of the full
procedure (real assignment of kappa = 0 data), the full-procedure false-promotion rate inside held-out null worlds,
pass probabilities by kappa with the realised mean IC and the 80+ group's annualised excess (economic translation),
and the 50% / 80% detectable effects. Seeds are fixed (SEED_BASE)."""
import gzip
import json
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
import qr_p7_export as E  # noqa: E402
import qr_p7_pred as R  # noqa: E402

SEED_BASE = 20261006
KAPPAS = (0.0, 0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.008, 0.010)
N_DATASETS = 200                    # synthetic datasets per kappa
NULL_DATASETS, NULL_WORLDS = 10, 200    # calibration null: 2,000 worlds over 10 kappa = 0 datasets
HOLDOUT_DATASETS, HOLDOUT_WORLDS = 5, 200   # held-out null worlds for the full-procedure false-promotion rate
SIGMA_BY_RISK = {10: 0.045, 7: 0.055, 3: 0.065, 0: 0.085}
STYLE_SD = 0.0055                   # monthly style-factor return per sd of exposure (momentum, low volatility, quality):
                                    # calibrated so that the monthly cross-sectional IC of the score has sd ~ 0.10 under
                                    # the null (typical of composite equity factors); sensitivities 0 (sd ~ 0.066) and
                                    # 0.009 (sd ~ 0.13)
SCENARIOS = dict(main=STYLE_SD, optimistic=0.0, pessimistic=0.009)
PAYLOAD = HERE / "P7_CP3R_E993_payload.json.gz"


def score_tables():
    """Real E993-02 score cross-sections (scores only): per review, eligible kept-class rows."""
    pay = json.loads(gzip.open(PAYLOAD).read())
    sids = pay["sids"]
    regimes = [x[7] for x in pay["regimes"]]
    out = []
    for m, (t, tk, enc) in enumerate(pay["reviews"][:-1]):          # 83 decisions: 2011-01-31 .. 2017-11-30
        rows = [r for r in E.decode_rows(enc) if E.eligible_flag(r["bits"], r["total"])]
        rows.sort(key=lambda r: sids[r["i"]])
        out.append(dict(ids=np.array([sids[r["i"]] for r in rows]), S=np.array([r["total"] for r in rows]),
                        sector=np.array([r["ff"] for r in rows]),
                        risk=np.array([r["points"][2] for r in rows]),
                        mom_pts=np.array([r["points"][1] for r in rows], float),
                        fund=np.array([sum(r["points"][3:7]) for r in rows], float),
                        size=np.log(np.array([max(r["adv_k"], 1) for r in rows], float)),
                        year=int(tk[:4]), regime=regimes[m], tk=tk))
    return out


def _normal_score(S):
    r = R.rank01(S)
    return np.array([math.sqrt(2.0) * _erfinv(2.0 * x - 1.0) for x in r])


def _erfinv(x):
    a = 0.147
    ln = math.log(1.0 - x * x)
    t1 = 2.0 / (math.pi * a) + ln / 2.0
    return math.copysign(math.sqrt(math.sqrt(t1 * t1 - ln / a) - t1), x)


def synth(tables, kappa, seed, style_sd=STYLE_SD):
    rng = np.random.default_rng(seed)
    beta = {}
    dates = []
    for d in tables:
        n = d["ids"].size
        mkt = rng.normal(0.008, 0.035)
        fac = rng.normal(0.0, 0.025, 16)
        b = np.array([beta.setdefault(s, 1.0 + 0.25 * rng.normal()) for s in d["ids"]])
        sig = np.array([SIGMA_BY_RISK.get(int(k), 0.085) for k in d["risk"]])
        e = rng.standard_t(5, n) / math.sqrt(5.0 / 3.0)
        mom = d["mom_pts"] + rng.random(n)
        style = sum(rng.normal(0.0, style_sd) * _normal_score(x) for x in (mom, d["risk"] + rng.random(n),
                                                                            d["fund"] + rng.random(n)))
        y = b * mkt + fac[d["sector"] % 16] + style + sig * e + kappa * _normal_score(d["S"])
        dates.append(dict(ids=d["ids"], S=d["S"], sector=d["sector"], mom=mom,
                          size=d["size"], y=y, year=d["year"], regime=d["regime"]))
    return dates


def _null_job(args):
    tables, seed_data, seeds, style_sd = args
    prep = R.prepare(synth(tables, 0.0, seed_data, style_sd))
    return [R.run_world(prep, seed=s) for s in seeds]


def _real_job(args):
    tables, kappa, seed, style_sd = args
    return R.run_world(R.prepare(synth(tables, kappa, seed, style_sd)))


def summarise_world(w):
    return {k: w[k] for k in ("t_ic", "ic_mean", "hi_ann", "mono", "q5_minus_q1_ann", "halves", "block_max",
                              "t_ic_sector", "t_inc")}


def scenario(tables, style_sd, workers=4):
    t0 = time.time()
    tables = score_tables()
    n_stocks = [d["ids"].size for d in tables]
    with ProcessPoolExecutor(workers) as ex:
        # 1) calibration null: 10 independent kappa = 0 datasets x 200 tethered worlds each
        jobs = [(tables, SEED_BASE + 1000 + k, range(1 + 200 * k, 201 + 200 * k), style_sd)
                for k in range(NULL_DATASETS)]
        cal = [w for ws in ex.map(_null_job, jobs) for w in ws]
        c_ic = R.critical_value(cal)
        # 2) held-out null worlds (different data and seeds): full-procedure false promotion
        jobs = [(tables, SEED_BASE + 2000 + k, range(100001 + 200 * k, 100201 + 200 * k), style_sd)
                for k in range(HOLDOUT_DATASETS)]
        hold = [w for ws in ex.map(_null_job, jobs) for w in ws]
        # 3) real-assignment evaluations by kappa
        res = {}
        for kappa in KAPPAS:
            jobs = [(tables, kappa, SEED_BASE + 10_000 * (1 + KAPPAS.index(kappa)) + j, style_sd)
                    for j in range(N_DATASETS)]
            res[kappa] = list(ex.map(_real_job, jobs, chunksize=8))
    out = dict(style_sd=style_sd, n_dates=len(tables),
               stocks_per_date=dict(min=min(n_stocks), median=float(np.median(n_stocks)), max=max(n_stocks)),
               c_ic_synthetic=c_ic, calibration_worlds=len(cal), holdout_worlds=len(hold),
               null_t_ic=dict(mean=float(np.mean([w["t_ic"] for w in cal])), sd=float(np.std([w["t_ic"] for w in cal])),
                              p95=float(np.percentile([w["t_ic"] for w in cal], 95)),
                              p99=float(np.percentile([w["t_ic"] for w in cal], 99))),
               holdout_false_promotion_full=R.false_promotion(hold, c_ic),
               holdout_false_g1=float(np.mean([w["t_ic"] > c_ic for w in hold])),
               holdout_gate_pass_rates={g: float(np.mean([R.promotion(w, c_ic)[g] for w in hold]))
                                        for g in ("G1_significant", "G2_economic", "G3_monotonic", "G4_stable")},
               by_kappa={})
    for kappa, ws in res.items():
        gs = [R.promotion(w, c_ic) for w in ws]
        out["by_kappa"][str(kappa)] = dict(
            kappa_bp_per_month=kappa * 1e4, datasets=len(ws),
            ic_mean=float(np.mean([w["ic_mean"] for w in ws])), ic_month_sd=float(np.mean([w["ic_se"] for w in ws]) *
                                                                             math.sqrt(len(tables))),
            t_ic_mean=float(np.mean([w["t_ic"] for w in ws])),
            hi_ann_mean=float(np.mean([w["hi_ann"] for w in ws])), hi_ann_sd=float(np.std([w["hi_ann"] for w in ws])),
            q5_minus_q1_ann_mean=float(np.mean([w["q5_minus_q1_ann"] for w in ws])),
            hi_n_mean=float(np.mean([w["hi_n_mean"] for w in ws])),
            pass_rates={g: float(np.mean([x[g] for x in gs])) for g in gs[0]})
    # detectable effects (linear interpolation of the full-procedure pass probability in kappa)
    ks = list(KAPPAS)
    pf = [out["by_kappa"][str(k)]["pass_rates"]["pass"] for k in ks]
    pg = [out["by_kappa"][str(k)]["pass_rates"]["G1_significant"] for k in ks]

    def mde(p, target):
        for (k0, a), (k1, b) in zip(zip(ks, p), zip(ks[1:], p[1:])):
            if a < target <= b:
                return k0 + (target - a) * (k1 - k0) / (b - a)
        return None

    def at(field, kappa):
        if kappa is None:
            return None
        lo = max(k for k in ks if k <= kappa)
        hi_ = min(k for k in ks if k >= kappa)
        a, b = out["by_kappa"][str(lo)][field], out["by_kappa"][str(hi_)][field]
        return a if hi_ == lo else a + (kappa - lo) * (b - a) / (hi_ - lo)
    for name, p in (("full_procedure", pf), ("significance_gate_only", pg)):
        d = {}
        for target in (0.5, 0.8):
            k = mde(p, target)
            d[f"mde{int(target * 100)}"] = dict(kappa_bp_per_month=None if k is None else k * 1e4,
                                                ic=at("ic_mean", k), hi_ann_80plus_excess=at("hi_ann_mean", k),
                                                q5_minus_q1_ann=at("q5_minus_q1_ann_mean", k))
        out[name] = d
    out["null_ic_month_sd"] = out["by_kappa"]["0.0"]["ic_month_sd"]
    out["runtime_s"] = round(time.time() - t0, 1)
    return out


def main(workers=4):
    tables = score_tables()
    res = dict(model=__doc__.split("Outputs")[0].strip(), seed_base=SEED_BASE, kappas=list(KAPPAS),
               datasets_per_kappa=N_DATASETS, calibration_worlds=NULL_DATASETS * NULL_WORLDS,
               holdout_worlds=HOLDOUT_DATASETS * HOLDOUT_WORLDS, scenarios={})
    for name, sd in SCENARIOS.items():
        res["scenarios"][name] = scenario(tables, sd, workers)
        o = res["scenarios"][name]
        print(name, json.dumps({k: o[k] for k in ("c_ic_synthetic", "null_ic_month_sd", "holdout_false_promotion_full",
                                                   "holdout_false_g1", "full_procedure", "runtime_s")}, default=float))
    txt = json.dumps(res, indent=1, sort_keys=True, default=float)
    for bad in ("cagr", "sharpe", "drawdown"):
        assert bad not in txt.lower()
    (HERE / "P7_power.json").write_text(txt + "\n")


if __name__ == "__main__":
    sys.exit(main())
