"""P13-CP3 (owner D223): H028 long-horizon synthetic path robustness study -> P13_CP3_bootstrap.json.

DESCRIPTIVE ONLY. Offline resampling of the already-observed, already-seen 2015-2021 development returns. Not a null
test, not validation, cannot repair B4; every frequency is a conditional robustness statistic ("H028 beat SPY in x% of
synthetic paths generated from the observed 2015-2021 return blocks"), never a probability of future success.
H028 stays REJECTED. No QuantConnect run, no new data, no Holdout (nothing after 2021-12-31 exists in the source).

Committed BEFORE any aggregate result was computed (owner section 33). Nothing below changes after results.

1. Donor panel (owner 6-8). Source: experiments/E030-05/messages.txt QRHR block (the one real H028 run). Monthly
   returns = calendar-month close marks of the committed daily equity paths of H028, LV15 and SPY (last session of each
   month; the starting capital $100,000 first; the qr_h027.risk / P11-CP2 convention) -> 84 paired months 2015-01 ..
   2021-12, after each strategy's actual trading costs (SPY = the P13-CP1 benchmark: bought at the first open with $7 +
   0.10%, total return).
   Terminal-liquidation audit: the daily paths are mark-to-market BEFORE the final liquidation (qr_h026.simulate /
   spy_simulate apply it only to the reported terminal wealth), so the donor December-2021 return contains no
   liquidation by construction; the audit checks
     SPY:        committed = last mark x (1 - 0.001) - $7 exactly (|diff| <= 1e-6);
     H028, LV15: implied liquidation = last mark - committed must equal the expected sale cost
                 0.001 x last mark x (1 - final cash share) + $7 x final holdings within 0.0002 x last mark + $7
                 (allowing for intra-month drift of the cash share and one holding without a final sale);
   any failure -> STOP — BOOTSTRAP RETURN SERIES NOT CLEANLY RECONSTRUCTIBLE. The initial entry costs (January 2015)
   are ordinary first-month costs of the recorded paths and are NOT altered (disclosed only).
2. Methods (seeds: numpy default_rng(SeedSequence([method code, seed])), one generator per world):
   'year'  (code 1): 30 complete calendar-year blocks (2015..2021, 12 months each, order kept) drawn uniformly with
           replacement; 10,000 worlds, seeds 1..10,000.            <- PRIMARY
   'mb12'  (code 2): every contiguous 12-month block of the 84 months (73 starts, no circular wrap), 30 blocks drawn
           uniformly with replacement = 360 months; 10,000 worlds, seeds 1..10,000.
   'mb24'  (code 3): every contiguous 24-month block (61 starts), 15 blocks = 360 months; 10,000 worlds.
   'loo_Y' (code 10 + index of Y in 2015..2021): year blocks without year Y (6 donors); 5,000 worlds, seeds 1..5,000.
   'ex1820'(code 20): year blocks from 2015, 2016, 2017, 2019, 2021 only; 10,000 worlds, seeds 1..10,000.
   'seven' (code 30, seed 1): 100,000 samples of 7 year blocks from the 7 years; annualised log(H028/SPY) and
           log(H028/LV15) = mean of the sampled yearly log-relatives; median, 2.5th and 97.5th percentiles.
   Every block is drawn jointly for H028, LV15 and SPY (the same months for all three).
3. Metrics per world (log wealth = cumulative sum of log(1 + r); start $100,000):
   horizons 5 / 10 / 20 / 30 years (first 60 / 120 / 240 / 360 months): wealth ratios H028/SPY and H028/LV15;
   excess CAGR = (W_H028 / 1e5)^(1/T) - (W_SPY / 1e5)^(1/T); P(ratio > 1), P(ratio < 1), P(H028 >= 1.15 x SPY),
   P(excess CAGR >= 0.02); percentiles 5 / 25 / 50 / 75 / 95 of the ratios and 5 / 50 / 95 of excess CAGR.
   annual = the 30 consecutive non-overlapping 12-month segments (= the sampled years for 'year'); longest streak of
   years with H028 < benchmark (strict); P(streak >= 3 / 5 / 10); number of years H028 > benchmark.
   relative wealth = exp(log W_H028 - log W_bench) with 1 at month 0; relative MaxDD = min(rel / running max - 1);
   rolling 60-month relative growth over all 301 windows: P(any < 1), P(any <= 0.90), P(any <= 0.80);
   longest recovery = the longest run of months below the running relative high (a run still open at month 360 is
   counted to the end; the share of worlds whose longest run is open is reported).
   Distributions: median, 75th, 90th, 95th, 99th percentile and the extreme world.
4. Regime frequency ('year'): share of draws per donor year; per year, the correlation between its count in a world and
   the world's 30-year log(H028/SPY), and the median 30-year ratio for counts <= 2, 3-5, >= 6.
5. Reproducibility: seeds 1-100 of every method rerun independently; every per-world metric must be identical.
6. Final wording (owner 37), from the 30-year results:
   favorable_core = P(H028 > SPY) >= 0.80 under 'year', 'mb12' and 'mb24' AND P(H028 > LV15) >= 0.80 under 'year';
   robust = P(H028 > SPY) >= 0.50 under every loo_Y AND under 'ex1820';
   favorable_core and robust      -> "H028 REMAINS FAVORABLE ACROSS MOST RESAMPLED LONG-HORIZON PATHS";
   favorable_core and not robust  -> "H028 IS HIGHLY SENSITIVE TO PATH / REGIME COMPOSITION";
   otherwise                      -> "H028 LONG-HORIZON EVIDENCE IS MIXED".

    PYTHONPATH=src python research/phase13/cp3/P13_CP3_bootstrap.py
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7")]
from P7_CP3R_extract import joined, lines  # noqa: E402
import qr_p7_export as E  # noqa: E402

EXP = "E030-05"
CAP = 100_000.0
YEARS = (2015, 2016, 2017, 2018, 2019, 2020, 2021)
SERIES = ("h028", "lv15", "spy")
HORIZONS = (5, 10, 20, 30)
N_YEARS, N_MONTHS = 30, 360
METHODS = dict(year=(1, 10_000), mb12=(2, 10_000), mb24=(3, 10_000), ex1820=(20, 10_000))
LOO = {y: (10 + i, 5_000) for i, y in enumerate(YEARS)}
SEVEN = (30, 1, 100_000)
REPRO_SEEDS = 100
SLIP, COMM = 0.001, 7.0
PCT_DIST = (50, 75, 90, 95, 99)


def _plain(x):
    """JSON serialisation of numpy scalars (serialisation only)."""
    return x.item() if hasattr(x, "item") else str(x)


class NotReconstructible(Exception):
    pass


# ----------------------------------------------------------------------------------------------- donor panel
def load():
    ls = lines(EXP)
    st = json.loads(joined(ls, "QRG"))
    blob = joined(ls, "QRHR")
    sha = hashlib.sha256(blob.encode()).hexdigest()
    assert sha == st["real"]["blob_sha256"]
    return json.loads(E.unpack(blob)), sha


def panel(o):
    days = np.asarray(o["days"], float)
    lab = np.array([str(np.datetime64(int(d), "D"))[:7] for d in days])
    ends = [i for i in range(len(days)) if i == len(days) - 1 or lab[i + 1] != lab[i]]
    months = [lab[i] for i in ends]
    marks = {n: np.r_[CAP, np.asarray(o[f"daily_{n}"], float)[ends]] for n in SERIES}
    r = np.stack([marks[n][1:] / marks[n][:-1] - 1.0 for n in SERIES], axis=1)       # (84, 3)
    return months, r, marks


def audit(o, months, r, marks):
    out = dict(months=len(months), first=months[0], last=months[-1])
    ok = len(months) == 84 and months[0] == "2015-01" and months[-1] == "2021-12" and np.all(np.isfinite(r))
    rec = {}
    for k, n in enumerate(SERIES):
        recon = CAP * float(np.prod(1.0 + r[:, k]))
        committed = float(o[n]["wealth"])
        last = float(marks[n][-1])
        rec[n] = dict(reconstructed_pre_liquidation=recon, last_mark=last, committed=committed,
                      implied_liquidation=last - committed, compounding_matches_mark=abs(recon / last - 1) <= 1e-12)
        ok &= rec[n]["compounding_matches_mark"]
    exp_spy = marks["spy"][-1] * (1 - SLIP) - COMM
    rec["spy"]["expected_committed"] = float(exp_spy)
    rec["spy"]["liquidation_ok"] = abs(exp_spy - o["spy"]["wealth"]) <= 1e-6
    ok &= rec["spy"]["liquidation_ok"]
    for n, tr in (("h028", o["trades"]), ("lv15", o["lv15_trades"])):
        last = rec[n]["last_mark"]
        cs, hold = float(tr["cash_share"][-1]), int(tr["holdings"][-1])
        exp_liq = SLIP * last * (1 - cs) + COMM * hold
        tol = 0.0002 * last + COMM
        rec[n].update(final_cash_share=cs, final_holdings=hold, expected_liquidation=exp_liq, tolerance=tol,
                      liquidation_ok=abs(rec[n]["implied_liquidation"] - exp_liq) <= tol)
        ok &= rec[n]["liquidation_ok"]
    rec["note_initial_costs"] = dict(
        spy_entry_cost_share=(COMM + (CAP - COMM) / (1 + SLIP) * SLIP) / CAP,
        h028_first_month_costs=dict(commission=o["replay_months"]["h028"][0][3], slippage=o["replay_months"]["h028"][0][4]),
        kept="first-month entry costs are part of the recorded January-2015 returns and are not altered")
    out.update(reconciliation=rec, ok=bool(ok),
               donor_terminal_liquidation="excluded by construction (month-end marks are pre-liquidation)")
    if not ok:
        raise NotReconstructible("STOP — BOOTSTRAP RETURN SERIES NOT CLEANLY RECONSTRUCTIBLE")
    return out


# ----------------------------------------------------------------------------------------------- sampling
def rng_for(code, seed):
    return np.random.default_rng(np.random.SeedSequence([code, seed]))


def month_index(method, seed):
    """The 360 donor month indices (0..83) of one world (donor years fixed by the method itself)."""
    if method in ("year", "ex1820") or method.startswith("loo_"):
        code = METHODS[method][0] if method in METHODS else LOO[int(method[4:])][0]
        yrs = np.array([YEARS.index(y) for y in donors(method)])
        b = yrs[rng_for(code, seed).integers(0, yrs.size, N_YEARS)]
        return (b[:, None] * 12 + np.arange(12)[None, :]).ravel()
    L = 12 if method == "mb12" else 24
    starts = rng_for(METHODS[method][0], seed).integers(0, 84 - L + 1, N_MONTHS // L)
    return (starts[:, None] + np.arange(L)[None, :]).ravel()[:N_MONTHS]


def donors(method):
    if method == "ex1820":
        return tuple(y for y in YEARS if y not in (2018, 2020))
    if method.startswith("loo_"):
        return tuple(y for y in YEARS if y != int(method[4:]))
    return YEARS


def simulate(lr, method, seeds):
    idx = np.stack([month_index(method, s) for s in seeds])          # (W, 360)
    return lr[idx], idx                                                               # (W, 360, 3)


# ----------------------------------------------------------------------------------------------- metrics
def pct(x, qs):
    return {f"p{q}": float(np.percentile(x, q)) for q in qs}


def longest_run(mask):
    """Longest run of True along axis 1 for a (W, T) boolean array; also whether it is open at the end."""
    cur = np.zeros(mask.shape[0], int)
    best = np.zeros(mask.shape[0], int)
    for t in range(mask.shape[1]):
        cur = np.where(mask[:, t], cur + 1, 0)
        best = np.maximum(best, cur)
    open_end = mask[:, -1] & (cur == best)
    return best, open_end


def world_metrics(L):
    """Per-world metric arrays from log returns L (W, 360, 3) in SERIES order."""
    cum = np.cumsum(L, axis=1)
    m = {}
    for H in HORIZONS:
        t = 12 * H - 1
        ls, ll = cum[:, t, 0] - cum[:, t, 2], cum[:, t, 0] - cum[:, t, 1]
        m[f"log_rel_spy_{H}"], m[f"log_rel_lv15_{H}"] = ls, ll
        m[f"excess_cagr_{H}"] = np.exp(cum[:, t, 0] / H) - np.exp(cum[:, t, 2] / H)
    ann = L.reshape(L.shape[0], N_YEARS, 12, 3).sum(axis=2)
    for k, b in ((2, "spy"), (1, "lv15")):
        behind = ann[:, :, 0] < ann[:, :, k]
        m[f"streak_{b}"], _ = longest_run(behind)
        m[f"win_years_{b}"] = (ann[:, :, 0] > ann[:, :, k]).sum(axis=1)
        d = np.concatenate([np.zeros((L.shape[0], 1)), cum[:, :, 0] - cum[:, :, k]], axis=1)   # log relative, 361
        peak = np.maximum.accumulate(d, axis=1)
        m[f"rel_maxdd_{b}"] = np.exp((d - peak).min(axis=1)) - 1.0
        roll = d[:, 60:] - d[:, :-60]
        m[f"roll_min_{b}"] = roll.min(axis=1)
        under = d < peak - 1e-12
        m[f"recovery_{b}"], m[f"recovery_open_{b}"] = longest_run(under)
    return m


def summarise(m):
    out = {}
    for H in HORIZONS:
        ls, ll, ex = m[f"log_rel_spy_{H}"], m[f"log_rel_lv15_{H}"], m[f"excess_cagr_{H}"]
        out[f"{H}y"] = dict(
            p_beat_spy=float(np.mean(ls > 0)), p_beat_lv15=float(np.mean(ll > 0)),
            p_below_spy=float(np.mean(ls < 0)), p_below_lv15=float(np.mean(ll < 0)),
            p_ge_115_spy=float(np.mean(ls >= math.log(1.15))), p_excess_cagr_ge_2pts=float(np.mean(ex >= 0.02)),
            ratio_spy=pct(np.exp(ls), (5, 25, 50, 75, 95)), ratio_lv15=pct(np.exp(ll), (5, 25, 50, 75, 95)),
            excess_cagr=pct(ex, (5, 50, 95)))
    for b in ("spy", "lv15"):
        s = m[f"streak_{b}"]
        out[f"streak_{b}"] = dict(pct(s, PCT_DIST), max=int(s.max()), p_ge_3=float(np.mean(s >= 3)),
                                  p_ge_5=float(np.mean(s >= 5)), p_ge_10=float(np.mean(s >= 10)))
        w = m[f"win_years_{b}"]
        out[f"win_years_{b}"] = pct(w, (5, 25, 50, 75, 95))
        dd = m[f"rel_maxdd_{b}"]
        out[f"rel_maxdd_{b}"] = dict({f"p{q}": float(np.percentile(dd, 100 - q)) for q in PCT_DIST},
                                     worst=float(dd.min()))
        rm = m[f"roll_min_{b}"]
        out[f"rolling5y_{b}"] = dict(p_any_behind=float(np.mean(rm < 0)), p_any_trail_10=float(np.mean(rm <= math.log(0.9))),
                                     p_any_trail_20=float(np.mean(rm <= math.log(0.8))))
        rc = m[f"recovery_{b}"]
        out[f"recovery_{b}"] = dict({f"p{q}_months": float(np.percentile(rc, q)) for q in (50, 90, 95, 99)},
                                    max_months=int(rc.max()), share_open_at_end=float(np.mean(m[f"recovery_open_{b}"])))
    return out


def digest(m):
    keys = sorted(m)
    return hashlib.sha256(b"".join(np.ascontiguousarray(m[k]).tobytes() for k in keys)).hexdigest()


def run_method(lr, method, n):
    seeds = range(1, n + 1)
    L, idx = simulate(lr, method, seeds)
    m = world_metrics(L)
    rep = world_metrics(simulate(lr, method, range(1, REPRO_SEEDS + 1))[0])
    same = all(np.array_equal(rep[k], m[k][:REPRO_SEEDS]) for k in m)
    return m, idx, dict(worlds=n, seeds=[1, n], donors=list(donors(method)), summary=summarise(m),
                        world_metric_sha256=digest(m), repro_seeds_1_100_identical=bool(same))


def main():
    o, blob_sha = load()
    months, r, marks = panel(o)
    aud = audit(o, months, r, marks)
    lr = np.log1p(r)
    yearly = {str(y): dict(zip(SERIES, [float(np.expm1(lr[12 * i:12 * i + 12, k].sum())) for k in range(3)]))
              for i, y in enumerate(YEARS)}
    res = {}
    keep = {}
    for meth, (_, n) in METHODS.items():
        m, idx, res[meth] = run_method(lr, meth, n)
        if meth == "year":
            keep = dict(m=m, idx=idx)
    for y, (_, n) in LOO.items():
        _, _, res[f"loo_{y}"] = run_method(lr, f"loo_{y}", n)
    # 7-year resampling interval
    code, seed, n7 = SEVEN
    yl = np.array([[lr[12 * i:12 * i + 12, 0].sum() - lr[12 * i:12 * i + 12, k].sum() for k in (2, 1)]
                   for i in range(7)])                                                  # yearly log rel vs SPY, LV15
    pick = rng_for(code, seed).integers(0, 7, (n7, 7))
    ann = yl[pick].mean(axis=1)
    seven = {b: dict(observed=float(yl[:, j].mean()), median=float(np.median(ann[:, j])),
                     p2_5=float(np.percentile(ann[:, j], 2.5)), p97_5=float(np.percentile(ann[:, j], 97.5)),
                     share_negative=float(np.mean(ann[:, j] < 0)))
             for j, b in enumerate(("log_h028_vs_spy_annualised", "log_h028_vs_lv15_annualised"))}
    # regime frequency (primary)
    yr_idx = keep["idx"][:, ::12] // 12                                                 # (W, 30) year index
    counts = np.stack([(yr_idx == i).sum(axis=1) for i in range(7)], axis=1)
    l30 = keep["m"]["log_rel_spy_30"]
    regime = {}
    for i, y in enumerate(YEARS):
        c = counts[:, i]
        regime[str(y)] = dict(share_of_draws=float(c.sum() / counts.sum()), mean_count=float(c.mean()),
                              corr_count_vs_log_ratio_30y=float(np.corrcoef(c, l30)[0, 1]),
                              median_ratio_30y_count_le2=float(np.exp(np.median(l30[c <= 2]))) if (c <= 2).any() else None,
                              median_ratio_30y_count_3_5=float(np.exp(np.median(l30[(c >= 3) & (c <= 5)]))),
                              median_ratio_30y_count_ge6=float(np.exp(np.median(l30[c >= 6]))) if (c >= 6).any() else None)
    # final wording (rule fixed in the docstring)
    p = lambda k: res[k]["summary"]["30y"]["p_beat_spy"]  # noqa: E731
    core = all(p(k) >= 0.80 for k in ("year", "mb12", "mb24")) and res["year"]["summary"]["30y"]["p_beat_lv15"] >= 0.80
    robust = all(p(f"loo_{y}") >= 0.50 for y in YEARS) and p("ex1820") >= 0.50
    wording = ("H028 REMAINS FAVORABLE ACROSS MOST RESAMPLED LONG-HORIZON PATHS" if core and robust else
               "H028 IS HIGHLY SENSITIVE TO PATH / REGIME COMPOSITION" if core else
               "H028 LONG-HORIZON EVIDENCE IS MIXED")
    out = dict(source=dict(experiment=EXP, qrhr_blob_sha256=blob_sha), audit=aud,
               donor_panel=dict(months=months, returns={n: r[:, k].tolist() for k, n in enumerate(SERIES)}),
               donor_years=yearly, methods=res, seven_year=seven, regime_frequency=regime,
               rule=dict(favorable_core=bool(core), robust=bool(robust)),
               result="SYNTHETIC ROBUSTNESS RESULT — " + wording, formal_status="H028 REJECTED",
               reproducibility_all_identical=all(v["repro_seeds_1_100_identical"] for v in res.values()))
    path = HERE / "P13_CP3_bootstrap.json"
    path.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain) + "\n")
    print(json.dumps(dict(audit=aud, result=out["result"], rule=out["rule"],
                          reproducible=out["reproducibility_all_identical"]), indent=1, default=_plain))
    print("sha256", hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
