"""Evaluation of the pre-registered X962 portfolio-structure diagnostics (E962-01..24).
Written and committed BEFORE any diagnostic ran (research/cycles/C03_portfolio_diagnostics_plan.md).
IS 2010-01-04..2017-12-29 derived results only.

    PYTHONPATH=src python research/cycles/C03_diagnostics_eval.py research/cycles/C03_diagnostics_results.json
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from qresearch import metrics, results, validation  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
IDS = [f"E962-{i:02d}" for i in range(1, 25)]
EW_ID, SPY_ID = "E901-07", "E900-07"


def _series(df, col="equity"):
    return pd.Series(df[col].to_numpy(float), index=df["date"].astype(str))


def run_metrics(eid, ew_all, spy_all):
    d = ROOT / "experiments" / eid
    cfg = json.loads((d / "config.json").read_text())
    res = json.loads((d / "result.json").read_text())
    if not res["status"].startswith("completed"):
        return dict(exp=eid, status=res["status"])
    eq = results.read_csv_gz(d / "equity.csv.gz")
    tr = results.read_csv_gz(d / "trades.csv.gz")
    fi = results.read_csv_gz(d / "fills.csv.gz")
    s = _series(eq)
    ew = ew_all[(ew_all.index >= s.index[0]) & (ew_all.index <= s.index[-1])]
    spy = spy_all[(spy_all.index >= s.index[0]) & (spy_all.index <= s.index[-1])]
    r, rew, rspy = (metrics.returns_from_equity(x) for x in (s, ew, spy))
    years = len(s) / 252.0
    mean_eq = float(s.mean())
    notional = float((fi["quantity"].abs() * fi["price"]).sum())
    comm = float(fi["fee"].sum()) / mean_eq / years
    slip = notional * cfg["costs"]["slippage_bps"] / 1e4 / mean_eq / years
    expo = validation.exposure(eq)
    ab = validation.alpha_beta(r, rew)
    rho = float(pd.concat([r, rew], axis=1, join="inner").corr().iloc[0, 1])
    vol = float(r.std() * math.sqrt(252))
    closed = tr[tr["status"] == "closed"]
    npos = eq["npos"].to_numpy(float) if "npos" in eq else np.full(len(eq), np.nan)
    sh, sh_ew = metrics.sharpe(r), metrics.sharpe(rew)
    return dict(
        exp=eid, status=res["status"], series=cfg["diagnostic_series"], slots=cfg["params"]["slots"],
        cash=cfg["cash"], hold=cfg["params"]["hold"], seed=cfg["params"]["seed"],
        cagr=metrics.cagr(s), sharpe=sh, max_dd=metrics.max_drawdown(s), vol=vol,
        ew_sharpe=sh_ew, spy_sharpe=metrics.sharpe(rspy), ew_cagr=metrics.cagr(ew), ew_max_dd=metrics.max_drawdown(ew),
        sharpe_minus_ew=sh - sh_ew,
        commission_pa=comm, slippage_pa=slip, cost_pa=comm + slip, turnover_pa=notional / mean_eq / years,
        exposure=float(expo.mean()), idle_cash=float(1 - expo.mean()),
        avg_positions=float(np.nanmean(npos)), trades=int(len(closed)),
        corr_ew=rho, beta_ew=ab["beta"], alpha_ew_pa=ab["alpha_ann"], alpha_t=ab["alpha_t"],
        idio_vol=vol * math.sqrt(max(1 - rho ** 2, 0.0)),
        ew_matched_sharpe=metrics.sharpe(metrics.returns_from_equity(validation.exposure_matched(ew, expo))),
    )


def cell_summary(rows):
    df = pd.DataFrame([r for r in rows if r.get("status", "").startswith("completed")])
    keys = ["series", "slots", "cash", "hold"]
    num = [c for c in df.columns if c not in keys + ["exp", "status", "seed"]]
    out = []
    for k, g in df.groupby(keys, sort=False):
        rec = dict(zip(keys, [str(k[0]), int(k[1]), int(k[2]), int(k[3])]), n_seeds=len(g))
        for c in num:
            rec[c] = float(g[c].mean())
            rec[c + "_min"] = float(g[c].min())
            rec[c + "_max"] = float(g[c].max())
        out.append(rec)
    return out


def rules(cells):
    """Pre-registered readings (plan §4). They describe structure; none changes a gate."""
    def cell(slots, cash, hold):
        for c in cells:
            if (c["slots"], c["cash"], c["hold"]) == (slots, cash, hold):
                return c
    s10, s15, s19 = cell(10, 100000, 20), cell(15, 100000, 20), cell(19, 100000, 20)
    a250, a1m, b30 = cell(15, 250000, 20), cell(15, 1000000, 20), cell(30, 250000, 20)
    h5, h60 = cell(15, 100000, 5), cell(15, 100000, 60)
    out = {}
    if s10 and s19:
        d = s19["sharpe"] - s10["sharpe"]
        spread = max(s10["sharpe_max"] - s10["sharpe_min"], s19["sharpe_max"] - s19["sharpe_min"])
        out["R1_diversification_19_vs_10"] = dict(delta_sharpe=d, seed_spread=spread,
                                                  material=bool(d > 0.10 and d > spread / 2))
    if s15 and a1m:
        out["R2_account_size_cost"] = dict(cost_100k=s15["cost_pa"], cost_250k=a250["cost_pa"] if a250 else None,
                                           cost_1m=a1m["cost_pa"], commission_100k=s15["commission_pa"],
                                           commission_1m=a1m["commission_pa"],
                                           delta_sharpe_1m_vs_100k=a1m["sharpe"] - s15["sharpe"])
    if s10:
        out["R3_structural_handicap_C02_setting"] = dict(null_sharpe=s10["sharpe"], ew_sharpe=s10["ew_sharpe"],
                                                         handicap=s10["ew_sharpe"] - s10["sharpe"],
                                                         gate_bar=s10["ew_sharpe"] + 0.10)
    if h5 and h60 and s15:
        out["R4_holding_period_cost_curve"] = {str(h): dict(cost_pa=c["cost_pa"], sharpe=c["sharpe"])
                                               for h, c in ((5, h5), (20, s15), (60, h60))}
    if b30 and a250:
        out["R5_breadth_30_vs_15_at_250k"] = dict(delta_sharpe=b30["sharpe"] - a250["sharpe"],
                                                  idio_vol_15=a250["idio_vol"], idio_vol_30=b30["idio_vol"])
    return out


def main(out_path):
    ew_all = _series(results.read_csv_gz(ROOT / "experiments" / EW_ID / "equity.csv.gz"))
    spy_all = _series(results.read_csv_gz(ROOT / "experiments" / SPY_ID / "equity.csv.gz"))
    rows = [run_metrics(e, ew_all, spy_all) for e in IDS if (ROOT / "experiments" / e / "result.json").exists()]
    cells = cell_summary(rows)
    out = dict(runs=rows, cells=cells, readings=rules(cells), benchmarks=dict(ew=EW_ID, spy=SPY_ID))
    Path(out_path).write_text(json.dumps(out, indent=1, default=float) + "\n")
    pd.set_option("display.width", 250)
    print(pd.DataFrame(cells)[["series", "slots", "cash", "hold", "n_seeds", "cagr", "sharpe", "sharpe_min",
                               "sharpe_max", "max_dd", "cost_pa", "exposure", "avg_positions", "corr_ew",
                               "idio_vol", "sharpe_minus_ew"]].round(3).to_string(index=False))
    print(json.dumps(out["readings"], indent=1, default=float))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "research/cycles/C03_diagnostics_results.json")
