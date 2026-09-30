"""H012 alternative screening items (owner request 2026-09-30, "Option 2"): definition and calibration.

PROPOSED, NOT IN FORCE. Written before any H012 (S012) candidate result; uses no C03 result and no
Validation data. The functions below are the exact proposed definitions (research/cycles/
C03_h012_screen_proposal.md); after approval they move unchanged into src/qresearch with tests.

Part 1 (synthetic): daily market returns from a GARCH(1,1) with Student-t shocks (volatility
clustering), a 15-stock large-cap basket = market + idiosyncratic noise, and the H012 v1.0 rule
(monthly target min(1, RV252/RV21), band 0.10, next-day application, costs), with Control A (e = 1)
and Control B (mean of the previous 12 targets). Scenarios:
  N1 risk-return proportional (mu_t = k sigma_t^2): volatility timing has NO value (the constant
     exposure is optimal) - a null;
  N2 uninformative timing: the exposure path comes from an independent volatility path (no
     information about the traded returns), while the market itself would reward timing - a null;
  A1 constant expected return (Moreira-Muir): genuine timing value;
  A2 constant conditional Sharpe (mu_t = s sigma_t): smaller genuine timing value;
  A3 as A1 with stronger volatility clustering (alpha 0.12, beta 0.87): a larger genuine timing value.
Part 2 (semi-real null, pre-C03 derived results only): the REAL IS daily returns of the EW
benchmark (E901-07) traded with exposure paths computed from SPY's (E900-07) IS returns circularly
shifted by at least one year, i.e. realistic but uninformative timing. The unshifted rule (which
would preview H012) is never computed.

    PYTHONPATH=src python research/cycles/C03_h012_screen_sim.py -> research/cycles/C03_h012_screen_sim.json
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")

T_IS, WARM = 2012, 600
YEAR = 252
ANN = math.sqrt(252)

# ---------------------------------------------------------------- the proposed definitions
MIN_DECISIONS = 8          # T1: applied exposure changes in IS (non-degeneracy; one per IS year)
BOOT_N, BOOT_BLOCK, BOOT_SEED, BOOT_Q = 10_000, 63, 20260930, 0.025   # T2
MARGIN_A = 0.05            # T3: pre-declared materiality margin of H012.md
THIRDS_MIN = 2             # T5: of 3


def sharpe(r):
    r = np.asarray(r, float)
    sd = r.std(ddof=1)
    return float(r.mean() / sd * ANN) if sd > 0 else float("nan")


def stationary_bootstrap_indices(rng, t, n, mean_block):
    """Politis-Romano stationary bootstrap: n index paths of length t; each step starts a new block
    (uniform random start) with probability 1/mean_block, else continues circularly."""
    idx = np.empty((n, t), dtype=np.int64)
    idx[:, 0] = rng.integers(0, t, n)
    new = rng.random((n, t)) < 1.0 / mean_block
    starts = rng.integers(0, t, (n, t))
    for j in range(1, t):
        idx[:, j] = np.where(new[:, j], starts[:, j], (idx[:, j - 1] + 1) % t)
    return idx


def boot_sharpe_diff(rv, rb, n=BOOT_N, block=BOOT_BLOCK, seed=BOOT_SEED, q=BOOT_Q):
    """q-quantile of the paired stationary-bootstrap distribution of Sharpe(V) - Sharpe(B) (annual).
    Days are resampled jointly for V and B, so common market movements cancel."""
    rv, rb = np.asarray(rv, float), np.asarray(rb, float)
    idx = stationary_bootstrap_indices(np.random.default_rng(seed), len(rv), n, block)
    a, b = rv[idx], rb[idx]
    d = a.mean(1) / a.std(1, ddof=1) - b.mean(1) / b.std(1, ddof=1)
    return float(np.quantile(d * ANN, q))


def boot_quantiles(rv, rb, n, seed, block=BOOT_BLOCK, qs=(0.025, 0.05, 0.10)):
    """Simulation helper: several quantiles from one bootstrap (same definition as boot_sharpe_diff)."""
    idx = stationary_bootstrap_indices(np.random.default_rng(seed), len(rv), n, block)
    a, b = np.asarray(rv)[idx], np.asarray(rb)[idx]
    d = (a.mean(1) / a.std(1, ddof=1) - b.mean(1) / b.std(1, ddof=1)) * ANN
    return {q: float(np.quantile(d, q)) for q in qs}


def h012_timing_items(rv, ra, rb, years, n_decisions, boot=None):
    """The five proposed H012 items replacing the four trade-level screen items.
    rv, ra, rb: aligned daily net returns of the variation, Control A and its Control B over IS;
    years: calendar year of each return; n_decisions: applied exposure changes in IS."""
    rv, ra, rb, years = (np.asarray(x) for x in (rv, ra, rb, years))
    d_b, d_a = sharpe(rv) - sharpe(rb), sharpe(rv) - sharpe(ra)
    lo = boot(rv, rb) if boot else boot_sharpe_diff(rv, rb)
    loyo = [sharpe(rv[years != y]) - sharpe(rb[years != y]) for y in np.unique(years)]
    thirds = [sharpe(p) - sharpe(q) for p, q in zip(np.array_split(rv, 3), np.array_split(rb, 3))]
    out = [
        dict(item="T1 applied exposure decisions", ok=n_decisions >= MIN_DECISIONS, value=int(n_decisions),
             required=f">= {MIN_DECISIONS}"),
        dict(item="T2 timing vs Control B: bootstrap lower bound", ok=lo > 0, value=lo,
             required="2.5% quantile of Sharpe(V) - Sharpe(B) > 0 (stationary bootstrap, block 63)"),
        dict(item="T3 timing vs Control A", ok=d_a > MARGIN_A, value=d_a, required=f"Sharpe(V) - Sharpe(A) > {MARGIN_A}"),
        dict(item="T4 not one year: leave-one-year-out vs Control B", ok=min(loyo) > 0, value=min(loyo),
             required="Sharpe(V) - Sharpe(B) > 0 with any one IS year removed"),
        dict(item="T5 subperiods vs Control B", ok=sum(x > 0 for x in thirds) >= THIRDS_MIN,
             value=sum(x > 0 for x in thirds), required=f">= {THIRDS_MIN} of 3 IS thirds with Sharpe(V) > Sharpe(B)"),
    ]
    return out, dict(d_b=d_b, d_a=d_a)


# ---------------------------------------------------------------- the H012 rule (v1.0) on a return path
def rv(x, n):
    return x[-n:].std(ddof=1) * ANN


def run_rule(signal_r, basket_r, cost=True, short=21, band=0.10, every=21):
    """Daily returns of V, A, B over the last T_IS days. signal_r: the SPY-like returns the rule sees;
    basket_r: traded returns (same length). Rescale every `every` days (month-end proxy); applied from
    the next day. Costs: 10 bps x |change| x basket + 15 orders x $7 on $100K per applied change."""
    n = len(signal_r)
    start = n - T_IS
    targets = []
    # targets on the rescale dates before the start (Control B's first year, as in D083)
    for t in range(start - 12 * every, start, every):
        targets.append(min(1.0, rv(signal_r[:t + 1], 252) / rv(signal_r[:t + 1], short)))
    ev = eb = None
    rets = {"V": [], "A": [], "B": []}
    dec = 0
    for t in range(start, n):
        # returns of day t earned with exposures set at t-1's close
        if ev is not None:
            rets["V"].append(ev * basket_r[t])
            rets["B"].append(eb * basket_r[t])
            rets["A"].append(basket_r[t])
        if t == start or (t - start) % every == every - 1:
            tgt = min(1.0, rv(signal_r[:t + 1], 252) / rv(signal_r[:t + 1], short))
            b_new = float(np.mean(targets[-12:]))
            targets.append(tgt)
            for key, new in (("V", tgt), ("B", b_new)):
                cur = ev if key == "V" else eb
                if cur is None or abs(new - cur) > band:
                    if cur is not None and cost and rets[key]:
                        rets[key][-1] -= abs(new - cur) * 0.001 + 15 * 7 / 1e5
                    if key == "V":
                        dec += cur is not None
                        ev = new
                    else:
                        eb = new
    return {k: np.array(v) for k, v in rets.items()}, dec


# ---------------------------------------------------------------- synthetic market
def garch_path(rng, n, sharpe_ann=0.9, vol_ann=0.16, alpha=0.08, beta=0.90, mean="const"):
    v = vol_ann ** 2 / 252
    omega = v * (1 - alpha - beta)
    z = rng.standard_t(6, n) / math.sqrt(6 / 4)
    s2 = np.empty(n)
    e = np.empty(n)
    s2[0] = v
    for t in range(n):
        if t:
            s2[t] = omega + alpha * e[t - 1] ** 2 + beta * s2[t - 1]
        e[t] = math.sqrt(s2[t]) * z[t]
    sr_d = sharpe_ann / ANN
    if mean == "const":            # A1 (Moreira-Muir): expected return unrelated to volatility
        mu = np.full(n, sr_d * math.sqrt(v))
    elif mean == "prop_var":       # N1: mu = k sigma^2 (constant exposure optimal)
        mu = sr_d / math.sqrt(v) * s2
    elif mean == "prop_vol":       # A2: mu = s sigma (constant conditional Sharpe)
        mu = sr_d * np.sqrt(s2) * math.sqrt(v) / np.sqrt(s2).mean()
    else:
        raise ValueError(mean)
    return mu + e


def synth(rng, scenario):
    n = WARM + T_IS
    mean = {"N1": "prop_var", "N2": "const", "A1": "const", "A2": "prop_vol", "A3": "const"}[scenario]
    kw = dict(alpha=0.12, beta=0.87) if scenario == "A3" else {}
    m = garch_path(rng, n, mean=mean, **kw)
    basket = m + rng.standard_normal(n) * 0.05 / ANN
    signal = garch_path(rng, n, mean="const") if scenario == "N2" else m
    return signal, basket


def full_pass(items):
    return all(i["ok"] for i in items)


def part1(reps, rng):
    years = np.minimum(np.arange(T_IS - 1) // YEAR, 7)
    out = {}
    for sc in ("N1", "N2", "A1", "A2", "A3"):
        rows = []
        for _ in range(reps):
            sig, bas = synth(rng, sc)
            r, dec = run_rule(sig, bas)
            qs = boot_quantiles(r["V"], r["B"], n=1000, seed=int(rng.integers(1 << 31)))
            items, dd = h012_timing_items(r["V"], r["A"], r["B"], years, dec, boot=lambda a, b: qs[0.025])
            rows.append(dict(items=[i["ok"] for i in items], **dd, sr_v=sharpe(r["V"]),
                             alt={q: [i["ok"] for i in items[:1]] + [qs[q] > 0] + [i["ok"] for i in items[2:]]
                                  for q in (0.05, 0.10)}))
        ok = np.array([x["items"] for x in rows])
        out[sc] = dict(reps=reps, pass_rate_by_item=dict(zip(["T1", "T2", "T3", "T4", "T5"], ok.mean(0).round(4).tolist())),
                       pass_all_five=float(ok.all(1).mean()),
                       pass_all_and_sharpe_05=float(np.mean([x["items"] == [True] * 5 and x["sr_v"] >= 0.5 for x in rows])),
                       mean_d_b=float(np.mean([x["d_b"] for x in rows])), mean_d_a=float(np.mean([x["d_a"] for x in rows])),
                       sd_d_b=float(np.std([x["d_b"] for x in rows])),
                       alternatives_T2_level={f"q={q}": dict(T2=float(np.mean([x["alt"][q][1] for x in rows])),
                                                            all_five=float(np.mean([all(x["alt"][q]) for x in rows])))
                                              for q in (0.05, 0.10)})
        print(sc, json.dumps(out[sc]))
    return out


def part1_blocks(reps, rng):
    """T2 alone under the nulls, for mean block lengths 5, 21, 63, 126 (calibration of the bootstrap)."""
    out = {}
    for sc in ("N1", "N2"):
        res = {L: [] for L in (5, 21, 63, 126)}
        for _ in range(reps):
            sig, bas = synth(rng, sc)
            r, _ = run_rule(sig, bas)
            for L in res:
                res[L].append(boot_sharpe_diff(r["V"], r["B"], n=1000, block=L, seed=int(rng.integers(1 << 31))) > 0)
        out[sc] = {f"block_{L}": float(np.mean(v)) for L, v in res.items()}
        print(sc, out[sc])
    return out


def part2():
    from qresearch import metrics, results
    root = Path(__file__).resolve().parents[2]

    def series(eid):
        eq = results.read_csv_gz(root / "experiments" / eid / "equity.csv.gz")
        s = pd.Series(eq["equity"].to_numpy(float), index=eq["date"].astype(str))
        return metrics.returns_from_equity(s[(s.index >= "2010-01-04") & (s.index <= "2017-12-29")])
    ew, spy = series("E901-07"), series("E900-07")
    j = pd.concat([ew, spy], axis=1, join="inner").dropna()
    ew_r, spy_r = j.iloc[:, 0].to_numpy(), j.iloc[:, 1].to_numpy()
    t = len(ew_r)
    years = np.array([int(d[:4]) for d in j.index])
    rows = []
    for shift in range(YEAR, t - YEAR + 1, 21):
        assert shift >= YEAR                      # the unshifted (informative) rule is never computed
        sig = np.roll(spy_r, shift)
        # prepend the circular history the rule needs, then trade the real EW days
        sig_full = np.concatenate([np.roll(sig, WARM)[:WARM], sig])
        bas_full = np.concatenate([np.zeros(WARM), ew_r])
        global T_IS
        keep = T_IS
        T_IS = t + 1
        try:
            r, dec = run_rule(sig_full, bas_full)
        finally:
            T_IS = keep
        items, dd = h012_timing_items(r["V"], r["A"], r["B"], years, dec,
                                      boot=lambda a, b: boot_sharpe_diff(a, b, n=2000))
        rows.append(dict(shift=shift, items=[i["ok"] for i in items], **dd))
    ok = np.array([x["items"] for x in rows])
    return dict(paths=len(rows), note="overlapping shifts: paths are NOT independent",
                pass_rate_by_item=dict(zip(["T1", "T2", "T3", "T4", "T5"], ok.mean(0).round(4).tolist())),
                pass_all_five=float(ok.all(1).mean()),
                d_b_quantiles=np.quantile([x["d_b"] for x in rows], [0.05, 0.5, 0.95]).round(3).tolist())


def main(reps=300):
    rng = np.random.default_rng(20260930)
    out = dict(proposal="research/cycles/C03_h012_screen_proposal.md", status="PROPOSED, not in force",
               part1_synthetic=part1(reps, rng), part1_bootstrap_block_calibration=part1_blocks(reps, rng),
               part2_semi_real_null=part2())
    print(json.dumps(out["part2_semi_real_null"], indent=1))
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
