"""H012 statistical power study (owner request "C03 — Reassess H012 Statistical Screening", 2026-09-30).

Synthetic data and permitted pre-C03 evidence only. No H012/H013 candidate run, no C03 result, no
Validation / Walk-Forward / Holdout data. H012's rule and parameters are NOT changed: every scenario
trades the approved H012 v1.0 rule (monthly, target min(1, RV252/RV21), band 0.10, next-day application,
costs, exposure capped at 1) with Control A (e = 1) and Control B (mean of the previous 12 targets).

Questions: why D084 has low power; overlap and contribution of T1-T5; defensible alternatives; false
positives and power per scenario; sensitivity to dependence, fat tails and sample length; whether
reduced exposure or favourable markets are mistaken for timing skill; whether 8 (or 12) years can
evaluate H012 at all.

Market models (all synthetic):
  * two-state regime model (calm 12% vol / turbulent 35% vol, mean turbulent spell 60 days, entry
    probability 1/400 per day, Student-t(6) shocks), unconditional market Sharpe about 0.9. The
    annualised mean return in the turbulent state (mu_turb) sets how much genuine value volatility
    timing has; it is calibrated on 400,000-day paths so that the TRUE Sharpe gain of H012 over
    Control B is 0 (boundary null), +0.05 (weak), +0.10 (moderate), +0.20 (strong);
  * GARCH(1,1) with expected return proportional to variance (N1: timing has negative value);
  * uninformative timing: the exposure path is computed from an independent market path (N2);
  * favourable market: uninformative timing in a strong bull market (market Sharpe 1.5) (F1);
  * lucky episode: uninformative timing plus one -20% crash placed where the variation happened to be
    under-invested and Control B was not (F2) - an apparent advantage from one coincidence;
  * lower exposure: uninformative timing with the variation's exposure scaled to 70% (L).
Semi-real null: the REAL IS returns of the EW benchmark (E901-07) traded with exposure paths from SPY's
(E900-07) IS returns circularly shifted by >= 1 year (72 overlapping paths). The unshifted rule, which
would preview H012, is never computed.

    PYTHONPATH=src python research/cycles/C03_h012_power_study.py  -> research/cycles/C03_h012_power_study.json
Seeds: master 20261001 (scenario draws), bootstrap indices 20260930 (the proposed D084 seed).
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

sys.path.insert(0, "src")
sys.path.insert(0, str(Path(__file__).parent))
import C03_h012_screen_sim as D084  # noqa: E402  (the proposed D084 definitions, unchanged)

ANN = math.sqrt(252)
YEAR = 252
WARM = 700
SEED = 20261001
REPS = 400
BOOT_N = 2000                     # the D084 rule uses 10,000; 2,000 keeps the simulation tractable
T8, T12 = 2012, 3020
COST_ORDER = 15 * 7 / 1e5


# ---------------------------------------------------------------- H012 v1.0 engine (vectorised)
def engine(signal_r, basket_r, t_len, every=21, short=21, band=0.10, scale=1.0):
    """Daily net returns of V (variation), A (Control A) and B (Control B) over the last t_len days.
    Identical to C03_h012_screen_sim.run_rule (checked in main()); `scale` < 1 only for scenario L."""
    n = len(signal_r)
    start = n - t_len
    s = pd.Series(signal_r)
    tgt = np.minimum(1.0, s.rolling(252).std(ddof=1).to_numpy() / s.rolling(short).std(ddof=1).to_numpy()) * scale
    targets = [tgt[t] for t in range(start - 12 * every, start, every)]
    e_v, e_b = np.full(n, np.nan), np.full(n, np.nan)
    c_v, c_b = np.zeros(n), np.zeros(n)
    ev = eb = None
    dec = 0
    for t in [start] + list(range(start + every - 1, n, every)):
        tg, bn = tgt[t], float(np.mean(targets[-12:]))
        targets.append(tg)
        if ev is None or abs(tg - ev) > band:
            if ev is not None and t > start:
                c_v[t] += abs(tg - ev) * 0.001 + COST_ORDER
            dec += ev is not None
            ev = tg
        if eb is None or abs(bn - eb) > band:
            if eb is not None and t > start:
                c_b[t] += abs(bn - eb) * 0.001 + COST_ORDER
            eb = bn
        e_v[t], e_b[t] = ev, eb
    e_v, e_b = pd.Series(e_v).ffill().to_numpy(), pd.Series(e_b).ffill().to_numpy()
    i = np.arange(start + 1, n)
    return dict(V=e_v[i - 1] * basket_r[i] - c_v[i], A=basket_r[i].copy(), B=e_b[i - 1] * basket_r[i] - c_b[i],
                eV=e_v[i - 1], eB=e_b[i - 1], dec=dec)


# ---------------------------------------------------------------- market models
def t_shocks(rng, n, df):
    return rng.standard_normal(n) if df is None else rng.standard_t(df, n) / math.sqrt(df / (df - 2))


def regime_market(rng, n, mu_turb, dur=60, p_in=1 / 400, vc=0.12, vt=0.35, sr=0.9, df=6, ar=0.0):
    u = rng.random(n)
    st = np.zeros(n, dtype=bool)
    s = False
    for t in range(n):
        s = (u[t] < 1 - 1 / dur) if s else (u[t] < p_in)
        st[t] = s
    frac = p_in * dur / (1 + p_in * dur)
    tot_sd = math.sqrt(frac * vt ** 2 + (1 - frac) * vc ** 2)
    mu_c = (sr * tot_sd - frac * mu_turb) / (1 - frac)
    e = np.where(st, vt, vc) / ANN * t_shocks(rng, n, df)
    if ar:
        for t in range(1, n):
            e[t] += ar * e[t - 1]
    return np.where(st, mu_turb, mu_c) / 252 + e


def garch_market(rng, n, p=2.0, sr=0.9, alpha=0.08, beta=0.90, vol=0.16, df=6):
    v = vol ** 2 / 252
    om = v * (1 - alpha - beta)
    z = t_shocks(rng, n, df)
    s2, e = np.empty(n), np.empty(n)
    s2[0] = v
    for t in range(n):
        if t:
            s2[t] = om + alpha * e[t - 1] ** 2 + beta * s2[t - 1]
        e[t] = math.sqrt(s2[t]) * z[t]
    sig = np.sqrt(s2)
    m = (sr / ANN) * math.sqrt(np.mean(sig ** 2)) / np.mean(sig ** p)
    return m * sig ** p + e


def basket(rng, m):
    return m + rng.standard_normal(len(m)) * 0.05 / ANN     # 15 large caps: market + idiosyncratic


# ---------------------------------------------------------------- tests
def sr(x):
    return D084.sharpe(x)


_IDX = {}


def boot_idx(t_len):
    if t_len not in _IDX:
        _IDX[t_len] = D084.stationary_bootstrap_indices(np.random.default_rng(D084.BOOT_SEED), t_len, BOOT_N,
                                                        D084.BOOT_BLOCK)
    return _IDX[t_len]


def boot_q(rv, rb, qs=(0.025, 0.05)):
    idx = boot_idx(len(rv))
    a, b = rv[idx], rb[idx]
    d = (a.mean(1) / a.std(1, ddof=1) - b.mean(1) / b.std(1, ddof=1)) * ANN
    return {q: float(np.quantile(d, q)) for q in qs}


def hac(y, lag):
    t = len(y)
    psi = y.T @ y / t
    for k in range(1, lag + 1):
        g = y[k:].T @ y[:-k] / t
        psi += (1 - k / (lag + 1)) * (g + g.T)
    return psi


def lw_z(rv, rb, lag=21):
    """Ledoit-Wolf (2008) HAC delta-method z statistic of Sharpe(V) - Sharpe(B) (Bartlett kernel)."""
    mv, mb, gv, gb = rv.mean(), rb.mean(), (rv ** 2).mean(), (rb ** 2).mean()
    y = np.column_stack([rv - mv, rb - mb, rv ** 2 - gv, rb ** 2 - gb])
    grad = np.array([gv / (gv - mv ** 2) ** 1.5, -gb / (gb - mb ** 2) ** 1.5,
                     -0.5 * mv / (gv - mv ** 2) ** 1.5, 0.5 * mb / (gb - mb ** 2) ** 1.5])
    se = math.sqrt(grad @ hac(y, lag) @ grad / len(rv))
    d = mv / math.sqrt(gv - mv ** 2) - mb / math.sqrt(gb - mb ** 2)
    return d / se


def alpha_t(rv, ra, lag=21):
    """HAC t statistic of alpha in r_V = alpha + beta r_A + e (the Moreira-Muir 'managed vs unmanaged' test)."""
    x = np.column_stack([np.ones_like(ra), ra])
    b = np.linalg.lstsq(x, rv, rcond=None)[0]
    e = rv - x @ b
    xtx_inv = np.linalg.inv(x.T @ x / len(rv))
    s = hac(x * e[:, None], lag)
    v = xtx_inv @ s @ xtx_inv / len(rv)
    return b[0] / math.sqrt(v[0, 0])


def max_dd(r):
    e = np.cumprod(1 + r)
    return float((e / np.maximum.accumulate(e) - 1).min())


def evaluate(res, years, lengths_only=False):
    """All individual items and statistics for one simulated path."""
    rv, ra, rb = res["V"], res["A"], res["B"]
    q = boot_q(rv, rb)
    loyo = [sr(rv[years != y]) - sr(rb[years != y]) for y in np.unique(years)]
    thirds = [sr(a) - sr(b) for a, b in zip(np.array_split(rv, 3), np.array_split(rb, 3))]
    z21 = lw_z(rv, rb, 21)
    return dict(
        d_b=sr(rv) - sr(rb), d_a=sr(rv) - sr(ra),
        T1=res["dec"] >= D084.MIN_DECISIONS, T2=q[0.025] > 0, T2q05=q[0.05] > 0,
        T3=sr(rv) - sr(ra) > D084.MARGIN_A, T4=min(loyo) > 0, T5=sum(x > 0 for x in thirds) >= 2,
        LW=z21 > norm.ppf(0.95), LW63=lw_z(rv, rb, 63) > norm.ppf(0.95), z=z21,
        ALPHA=alpha_t(rv, ra) > norm.ppf(0.95),
        dd_better=max_dd(rv) > max_dd(ra) + 0.03, e_mean=float(res["eV"].mean()))


METHODS = {
    "M0 D084 as proposed (T1-T5, T2 at 2.5%)": lambda x: x["T1"] and x["T2"] and x["T3"] and x["T4"] and x["T5"],
    "M1 D084 with T2 at 5%": lambda x: x["T1"] and x["T2q05"] and x["T3"] and x["T4"] and x["T5"],
    "M2 core: T1 + T2 at 2.5% (T3-T5 diagnostic)": lambda x: x["T1"] and x["T2"],
    "M3 core: T1 + T2 at 5% one-sided": lambda x: x["T1"] and x["T2q05"],
    "M4 core: T1 + Ledoit-Wolf HAC test at 5% one-sided": lambda x: x["T1"] and x["LW"],
    "M5 T1 + T2 at 5% + T3 (materiality vs A)": lambda x: x["T1"] and x["T2q05"] and x["T3"],
}
ITEMS = ["T1", "T2", "T2q05", "T3", "T4", "T5", "LW", "LW63", "ALPHA"]


def summarise(rows):
    out = dict(n=len(rows), true_like_mean_d_b=float(np.mean([r["d_b"] for r in rows])),
               sd_d_b=float(np.std([r["d_b"] for r in rows], ddof=1)),
               mean_d_a=float(np.mean([r["d_a"] for r in rows])),
               items={k: float(np.mean([bool(r[k]) for r in rows])) for k in ITEMS},
               methods={k: float(np.mean([bool(f(r)) for r in rows])) for k, f in METHODS.items()},
               drawdown_better_than_A_by_3pts=float(np.mean([r["dd_better"] for r in rows])),
               mean_exposure=float(np.mean([r["e_mean"] for r in rows])))
    return out


# ---------------------------------------------------------------- calibration of true effects
def true_effect(mu_turb, n=400_000, seed=7, **kw):
    rng = np.random.default_rng(seed)
    m = regime_market(rng, n, mu_turb, **kw)
    r = engine(m, basket(rng, m), n - WARM)
    return sr(r["V"]) - sr(r["B"]), sr(r["V"]) - sr(r["A"])


def calibrate(target, **kw):
    """mu_turb whose TRUE Sharpe gain of V over B equals `target` (linear in mu_turb; checked)."""
    a, b = 0.4, -1.0
    fa, fb = true_effect(a, **kw)[0], true_effect(b, **kw)[0]
    mu = a + (target - fa) * (b - a) / (fb - fa)
    return float(mu), true_effect(mu, **kw)


# ---------------------------------------------------------------- scenarios
def years_of(t_len):
    return np.minimum(np.arange(t_len - 1) // YEAR, round(t_len / YEAR) - 1)


def path(rng, kind, t_len, mu=None, **kw):
    n = WARM + t_len
    if kind == "regime":
        m = regime_market(rng, n, mu, **kw)
        return engine(m, basket(rng, m), t_len)
    if kind == "N1":
        m = garch_market(rng, n, p=2.0)
        return engine(m, basket(rng, m), t_len)
    if kind in ("N2", "F1", "L", "F2"):
        m = regime_market(rng, n, 0.0, sr=1.5 if kind == "F1" else 0.9)
        sig = regime_market(rng, n, 0.0)                    # independent path: uninformative timing
        bas = basket(rng, m)
        res = engine(sig, bas, t_len, scale=0.7 if kind == "L" else 1.0)
        if kind == "F2":                                    # one coincidental crash while V was under-invested
            gap = res["eB"] - res["eV"]
            k = int(np.argmax(pd.Series(gap).rolling(15).min().fillna(-9).to_numpy()))
            if gap[k] <= 0.15:
                return None
            start = n - t_len + 1
            bas = bas.copy()
            bas[start + k - 14:start + k + 1] -= 0.20 / 15
            res = engine(sig, bas, t_len)
        return res
    raise ValueError(kind)


def run_scenario(rng, kind, t_len, reps, mu=None, **kw):
    yrs = years_of(t_len)
    rows = []
    while len(rows) < reps:
        res = path(rng, kind, t_len, mu, **kw)
        if res is not None:
            rows.append(evaluate(res, yrs))
    return rows


def overlap(rows):
    keys = ["T2", "T3", "T4", "T5", "LW"]
    m = np.array([[float(r[k]) for k in keys] for r in rows])
    c = np.corrcoef(m.T) if m.std(0).min() > 0 else None
    t2 = [r for r in rows if r["T2"]]
    return dict(pass_indicator_correlation=None if c is None else {f"{a}-{b}": round(float(c[i, j]), 3)
                                                                   for i, a in enumerate(keys) for j, b in enumerate(keys) if i < j},
                given_T2_passes_share_failing={k: (float(np.mean([not r[k] for r in t2])) if t2 else None)
                                               for k in ("T3", "T4", "T5")},
                n_T2_pass=len(t2))


def semi_real():
    from qresearch import metrics, results
    root = Path(__file__).resolve().parents[2]

    def series(eid):
        eq = results.read_csv_gz(root / "experiments" / eid / "equity.csv.gz")
        s = pd.Series(eq["equity"].to_numpy(float), index=eq["date"].astype(str))
        return metrics.returns_from_equity(s[(s.index >= "2010-01-04") & (s.index <= "2017-12-29")])
    j = pd.concat([series("E901-07"), series("E900-07")], axis=1, join="inner").dropna()
    ew, spy = j.iloc[:, 0].to_numpy(), j.iloc[:, 1].to_numpy()
    t = len(ew)
    years = np.array([int(d[:4]) for d in j.index])
    rows = []
    for shift in range(YEAR, t - YEAR + 1, 21):
        assert shift >= YEAR                        # the unshifted (informative) rule is never computed
        sig = np.roll(spy, shift)
        sig_full = np.concatenate([np.roll(sig, WARM)[:WARM], sig])
        res = engine(sig_full, np.concatenate([np.zeros(WARM), ew]), t + 1)
        rows.append(evaluate(res, years))
    return rows


def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    out = dict(status="analysis for the owner; nothing here is in force", seeds=dict(master=SEED, bootstrap=D084.BOOT_SEED),
               assumptions=dict(reps=REPS, bootstrap_resamples=BOOT_N, block=D084.BOOT_BLOCK, rule="H012 v1.0",
                                costs="10 bps x |change| + 15 x $7 per applied change on $100K",
                                market="regime: calm 12% / turbulent 35% vol, spell 60 d, entry 1/400, t(6); basket = market + 5% idio"))
    # engine = the D084 simulation's rule
    chk = np.random.default_rng(3)
    sig, bas = D084.synth(chk, "A1")
    r1, d1 = D084.run_rule(sig, bas)
    r2 = engine(sig, bas, D084.T_IS)
    assert d1 == r2["dec"] and all(np.allclose(r1[k], r2[k], atol=1e-12) for k in "VAB")
    cal = {}
    for name, target in (("Z0 boundary null", 0.0), ("W weak", 0.05), ("M moderate", 0.10), ("S strong", 0.20)):
        mu, (db, da) = calibrate(target)
        cal[name] = dict(mu_turb=mu, true_d_b=db, true_d_a=da)
    out["calibration_true_effects"] = cal
    print(json.dumps(cal), time.time() - t0, flush=True)

    scen = {}
    for name, c in cal.items():
        rows = run_scenario(rng, "regime", T8, REPS, c["mu_turb"])
        scen[name] = dict(summarise(rows), overlap=overlap(rows))
        print(name, json.dumps(scen[name]["methods"]), round(time.time() - t0), flush=True)
    for name, kind in (("N1 risk-return (GARCH, mu ~ variance)", "N1"), ("N2 uninformative timing", "N2"),
                       ("F1 favourable bull market, no timing", "F1"), ("F2 one lucky crash, no timing", "F2"),
                       ("L lower exposure (70%), no timing", "L")):
        rows = run_scenario(rng, kind, T8, REPS)
        scen[name] = summarise(rows)
        print(name, json.dumps(scen[name]["methods"]), round(time.time() - t0), flush=True)
    out["scenarios_8y"] = scen

    # sensitivity: dependence and fat tails (size at the recalibrated boundary null, power at moderate)
    sens = {}
    for label, kw in (("normal shocks", dict(df=None)), ("t(3) shocks", dict(df=3)),
                      ("short turbulent spells (20 d)", dict(dur=20, p_in=3 / 400)),
                      ("long turbulent spells (120 d)", dict(dur=120, p_in=1 / 800)),
                      ("return autocorrelation AR(1) 0.1", dict(ar=0.1))):
        z_mu, (z_db, _) = calibrate(0.0, **kw)
        m_mu, (m_db, _) = calibrate(0.10, **kw)
        z = summarise(run_scenario(rng, "regime", T8, REPS // 2, z_mu, **kw))
        m = summarise(run_scenario(rng, "regime", T8, REPS // 2, m_mu, **kw))
        sens[label] = dict(boundary_true_d_b=z_db, moderate_true_d_b=m_db,
                           size_at_boundary=z["methods"], power_moderate=m["methods"])
        print(label, json.dumps(sens[label]), round(time.time() - t0), flush=True)
    out["sensitivity_8y"] = sens

    # sample length: 8, 12, 25, 50 years (bootstrap methods up to 12 years; HAC-based at all lengths)
    lens = {}
    for years in (8, 12, 25, 50):
        t_len = years * YEAR - 4
        res_l = {}
        for name in ("Z0 boundary null", "W weak", "M moderate", "S strong"):
            reps = REPS // 2 if years <= 12 else REPS // 4
            yrs = years_of(t_len)
            rows = []
            for _ in range(reps):
                r = path(rng, "regime", t_len, cal[name]["mu_turb"])
                if years <= 12:
                    rows.append(evaluate(r, yrs))
                else:                                            # HAC only (bootstrap too costly)
                    rows.append(dict(d_b=sr(r["V"]) - sr(r["B"]), LW=lw_z(r["V"], r["B"]) > norm.ppf(0.95),
                                     T1=r["dec"] >= D084.MIN_DECISIONS))
            d = dict(sd_d_b=float(np.std([x["d_b"] for x in rows], ddof=1)),
                     M4_LW=float(np.mean([x["T1"] and x["LW"] for x in rows])))
            if years <= 12:
                d.update(M2=float(np.mean([METHODS["M2 core: T1 + T2 at 2.5% (T3-T5 diagnostic)"](x) for x in rows])),
                         M3=float(np.mean([METHODS["M3 core: T1 + T2 at 5% one-sided"](x) for x in rows])),
                         M0=float(np.mean([METHODS["M0 D084 as proposed (T1-T5, T2 at 2.5%)"](x) for x in rows])))
            res_l[name] = d
        lens[f"{years}y"] = res_l
        print(years, json.dumps(res_l), round(time.time() - t0), flush=True)
    out["sample_length"] = lens

    # years needed for 80% power (one-sided 5%), from the 8-year spread of the estimated gain (sd ~ 1/sqrt(T))
    sd8 = scen["M moderate"]["sd_d_b"]
    need = {}
    for name in ("W weak", "M moderate", "S strong"):
        delta = cal[name]["true_d_b"]
        need[name] = dict(true_d_b=delta,
                          years_for_80pct_power_5pct=round(8 * ((norm.ppf(0.95) + norm.ppf(0.80)) * sd8 / delta) ** 2, 1),
                          years_for_80pct_power_2_5pct=round(8 * ((norm.ppf(0.975) + norm.ppf(0.80)) * sd8 / delta) ** 2, 1))
    out["years_needed"] = dict(sd_d_b_8y=sd8, **need)

    sr_rows = semi_real()
    out["semi_real_null_72_paths"] = dict(summarise(sr_rows), note="overlapping shifts; paths not independent")
    print("semi-real", json.dumps(out["semi_real_null_72_paths"]["methods"]), flush=True)
    out["runtime_s"] = round(time.time() - t0)
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1, default=float) + "\n")


if __name__ == "__main__":
    main()
