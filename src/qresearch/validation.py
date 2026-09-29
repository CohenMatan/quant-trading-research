"""Validation (VAL) gate and report figures for a promoted, frozen strategy (D036, D042, D056).

Gate (CP2 §6 as amended by D036; computed, never judged):
  VAL Sharpe >= 0.4 and >= 50% of the IS Sharpe; VAL Sharpe above the equal-weight benchmark's
  Sharpe over the same dates; VAL max drawdown <= 35%; >= 50 closed trades in VAL; drawdown in
  2020 Feb-Mar no more than 5 points worse than the benchmark's; Deflated Sharpe >= 0.90 on the
  IS and VAL daily returns combined with the registry trial count; PBO <= 0.30 (CSCV on IS, already
  computed at CP3 and passed in unchanged).

The exposure-aware comparison (owner, 2026-09-29) is descriptive, not a gate:
  - exposure-matched benchmark: benchmark daily return x the strategy's invested fraction at the
    previous close, i.e. the benchmark held with the same cash weight day by day;
  - regression of strategy daily returns on benchmark daily returns: beta and annualised alpha.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from . import gates, metrics, stats

COVID = ("2020-02-01", "2020-03-31")


def _series(df: pd.DataFrame, col: str = "equity") -> pd.Series:
    return pd.Series(df[col].to_numpy(float), index=df["date"].astype(str))


def exposure(equity_df: pd.DataFrame) -> pd.Series:
    """Invested fraction of equity at each close (1 - cash/equity)."""
    return 1.0 - _series(equity_df, "cash") / _series(equity_df, "equity")


def exposure_matched(bench: pd.Series, expo: pd.Series) -> pd.Series:
    """Equity curve of the benchmark scaled each day by the strategy's previous-close exposure;
    the rest is cash at 0%."""
    rb = bench.pct_change().iloc[1:]
    w = expo.reindex(bench.index).ffill().shift(1).iloc[1:]
    grown = (1.0 + rb * w).cumprod() * float(bench.iloc[0])
    return pd.concat([bench.iloc[:1], grown])


def alpha_beta(r: pd.Series, rb: pd.Series) -> dict:
    j = pd.concat([r, rb], axis=1, join="inner").dropna()
    x, y = j.iloc[:, 1].to_numpy(), j.iloc[:, 0].to_numpy()
    if len(j) < 3 or np.var(x) == 0:
        return dict(beta=float("nan"), alpha_ann=float("nan"), alpha_t=float("nan"))
    beta, a = np.polyfit(x, y, 1)
    resid = y - (a + beta * x)
    se_a = np.std(resid, ddof=2) / math.sqrt(len(y))
    return dict(beta=float(beta), alpha_ann=float(a * 252), alpha_t=float(a / se_a) if se_a > 0 else float("nan"))


def summary(eq: pd.Series) -> dict:
    r = metrics.returns_from_equity(eq)
    return dict(cagr=metrics.cagr(eq), sharpe=metrics.sharpe(r), max_dd=metrics.max_drawdown(eq),
                covid_dd=gates.episode_drawdown(eq, *COVID))


def val_gate(val_eq_df: pd.DataFrame, val_trades: pd.DataFrame, is_sharpe: float, ew: pd.Series,
             is_val_returns: np.ndarray, n_trials: int, var_sr: float, pbo: float) -> list[dict]:
    eq = _series(val_eq_df)
    ew = ew[(ew.index >= eq.index[0]) & (ew.index <= eq.index[-1])]
    m = metrics.compute_metrics(val_eq_df, val_trades)
    s, b = m["sharpe"], metrics.sharpe(metrics.returns_from_equity(ew))
    out = []

    def add(name, ok, value, need):
        out.append(dict(gate=name, ok=bool(ok), value=value, required=need))

    add("VAL Sharpe", s >= 0.4, round(s, 3), ">= 0.40")
    add("VAL Sharpe vs IS", s >= 0.5 * is_sharpe, round(s / is_sharpe, 3) if is_sharpe else float("nan"),
        f">= 0.50 x IS Sharpe {is_sharpe:.3f}")
    add("VAL Sharpe vs EW", s > b, round(s - b, 3), f"> EW Sharpe {b:.3f}")
    add("VAL max drawdown", m["max_drawdown"] >= -0.35, round(m["max_drawdown"], 3), ">= -0.35")
    add("VAL closed trades", m.get("n_trades", 0) >= 50, m.get("n_trades", 0), ">= 50")
    sd, bd = gates.episode_drawdown(eq, *COVID), gates.episode_drawdown(ew, *COVID)
    add("2020 Feb-Mar drawdown", sd >= bd - 0.05, round(sd, 3), f">= EW {bd:.3f} - 0.05")
    dsr = stats.deflated_sharpe(is_val_returns, max(n_trials, 1), var_sr)
    add("Deflated Sharpe (IS+VAL)", dsr >= 0.90, round(dsr, 3), f">= 0.90 (trials {n_trials})")
    add("PBO (CSCV on IS, from CP3)", pbo <= 0.30, round(pbo, 3), "<= 0.30")
    return out


def evaluate(val_id: str, is_id: str, ew_id: str, spy_id: str, pbo: float) -> dict:
    """All figures of the Validation report, from committed results only."""
    import json
    from . import config, registry, results
    from .cycle import cycle_experiments

    def load(eid):
        d = config.EXPERIMENTS_DIR / eid
        return (results.read_csv_gz(d / "equity.csv.gz"), results.read_csv_gz(d / "trades.csv.gz"),
                results.read_csv_gz(d / "fills.csv.gz"), json.loads((d / "config.json").read_text()))

    veq, vtr, vfi, vcfg = load(val_id)
    ieq, itr, ifi, _ = load(is_id)
    a, z = str(veq["date"].iloc[0]), str(veq["date"].iloc[-1])
    ew_full, spy_full = _series(load(ew_id)[0]), _series(load(spy_id)[0])
    ew = ew_full[(ew_full.index >= a) & (ew_full.index <= z)]
    spy = spy_full[(spy_full.index >= a) & (spy_full.index <= z)]
    v = _series(veq)
    m = metrics.compute_metrics(veq, vtr, vfi)
    expo = exposure(veq)
    years = (pd.Timestamp(z) - pd.Timestamp(a)).days / 365.25
    notional = float((vfi["quantity"].abs() * vfi["price"]).sum())
    fees = float(vfi["fee"].sum())
    costs = dict(commissions=fees, commission_drag_pa=fees / float(v.mean()) / years,
                 slippage_est=notional * vcfg["costs"]["slippage_bps"] / 1e4,
                 slippage_drag_pa=notional * vcfg["costs"]["slippage_bps"] / 1e4 / float(v.mean()) / years,
                 turnover_pa=notional / float(v.mean()) / years, orders=int(vfi["order_id"].nunique()))
    r_val = metrics.returns_from_equity(v)
    r_is = metrics.returns_from_equity(_series(ieq))
    is_sharpe = metrics.sharpe(r_is)
    final = cycle_experiments("C01")
    srs = [float(x["sharpe"]) / math.sqrt(252) for x in registry.read()
           if x["run_type"] == "original" and x["experiment_id"] in final and x["sharpe"]]
    var_sr = float(np.var(srs, ddof=1)) if len(srs) > 1 else 0.0
    n_trials = registry.trial_count()   # C01 Validation (E005-28) as reported; D069 applies from C02 on
    both = np.concatenate([r_is.to_numpy(), r_val.to_numpy()])
    gate = val_gate(veq, vtr, is_sharpe, ew, both, n_trials, var_sr, pbo)
    matched_ew = exposure_matched(ew, expo)
    matched_spy = exposure_matched(spy, expo)
    rew, rspy = metrics.returns_from_equity(ew), metrics.returns_from_equity(spy)
    yearly = {}
    for name, s in (("S005", v), ("EW", ew), ("SPY", spy)):
        e = s.copy(); e.index = pd.to_datetime(e.index)
        ends = e.resample("YE").last(); starts = ends.shift(1); starts.iloc[0] = e.iloc[0]
        yearly[name] = {str(k.year): float(x) for k, x in (ends / starts - 1).items()}
    # IS exposure-aware figures for context (same method)
    iexpo = exposure(ieq)
    ia, iz = str(ieq["date"].iloc[0]), str(ieq["date"].iloc[-1])
    ew_is = ew_full[(ew_full.index >= ia) & (ew_full.index <= iz)]
    return dict(
        period=(a, z), trials=n_trials, var_sr=var_sr, is_sharpe=is_sharpe,
        s005=dict(summary(v), n_trades=m.get("n_trades"), win_rate=m.get("win_rate"),
                  profit_factor=m.get("profit_factor"), avg_hold_days=m.get("avg_holding_days"),
                  invested_mean=float(expo.mean()), invested_min=float(expo.min()), invested_max=float(expo.max()),
                  covid_invested=float(expo[(expo.index >= COVID[0]) & (expo.index <= COVID[1])].mean())),
        ew=summary(ew), spy=summary(spy), yearly=yearly, costs=costs, gate=gate,
        relative=dict(vs_ew=alpha_beta(r_val, rew), vs_spy=alpha_beta(r_val, rspy),
                      corr_ew=float(pd.concat([r_val, rew], axis=1, join="inner").corr().iloc[0, 1])),
        exposure_matched=dict(ew=summary(matched_ew), spy=summary(matched_spy)),
        is_context=dict(invested_mean=float(iexpo.mean()), vs_ew=alpha_beta(r_is, metrics.returns_from_equity(ew_is)),
                        exposure_matched_ew=summary(exposure_matched(ew_is, iexpo)), s005=summary(_series(ieq)),
                        ew=summary(ew_is)),
    )


def main(argv=None) -> int:
    import json
    import sys
    from . import config
    args = argv or sys.argv[1:]
    val_id, is_id, ew_id, spy_id = args[:4]
    pbo = json.loads((config.REPO_ROOT / "research/cycles/C01_pbo.json").read_text())["H005"]["pbo"]
    out = evaluate(val_id, is_id, ew_id, spy_id, pbo)
    p = config.REPO_ROOT / "research" / "validation" / f"{val_id}_validation.json"
    p.write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(json.dumps(out, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
