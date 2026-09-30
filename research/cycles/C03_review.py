"""C01+C02 structured review (owner request 2026-09-30). IS derived results only; no VAL/Holdout.

    PYTHONPATH=src python research/cycles/C03_review.py research/cycles/C03_review_evidence.json
"""
import json, math, sys
import numpy as np, pandas as pd
sys.path.insert(0, "src")
from qresearch import results, metrics, validation, cycle

IDS = cycle.cycle_experiments("C01") + [f"E001-{i}" for i in range(16, 21)] + cycle.cycle_experiments("C02")
EW = results.read_csv_gz("experiments/E901-07/equity.csv.gz")
ew_all = pd.Series(EW["equity"].to_numpy(float), index=EW["date"].astype(str))
rows = []
rets = {}
for e in IDS:
    d = f"experiments/{e}"
    cfg = json.load(open(f"{d}/config.json"))
    eq = results.read_csv_gz(f"{d}/equity.csv.gz"); tr = results.read_csv_gz(f"{d}/trades.csv.gz")
    fi = results.read_csv_gz(f"{d}/fills.csv.gz")
    s = pd.Series(eq["equity"].to_numpy(float), index=eq["date"].astype(str))
    ew = ew_all[(ew_all.index >= s.index[0]) & (ew_all.index <= s.index[-1])]
    r, rew = metrics.returns_from_equity(s), metrics.returns_from_equity(ew)
    rets[e] = r
    years = len(s) / 252
    expo = validation.exposure(eq)
    bps = cfg["costs"]["slippage_bps"] * cfg["costs"].get("slippage_stress_multiple", 1) / 1e4
    fi["notional"] = (fi["quantity"].abs() * fi["price"]).astype(float)
    cost_by_day = (fi.groupby(fi["date"].astype(str))["fee"].sum() + fi.groupby(fi["date"].astype(str))["notional"].sum() * bps)
    cost_by_day = cost_by_day.reindex(s.index).fillna(0.0)
    gross_r = (r + (cost_by_day / s.shift(1)).reindex(r.index).fillna(0.0))
    ab = validation.alpha_beta(r, rew)
    closed = tr[tr["status"] == "closed"]
    mean_eq = float(s.mean())
    comm = float(fi["fee"].sum()) / mean_eq / years
    slip = float(fi["notional"].sum()) * bps / mean_eq / years
    m_ew = validation.exposure_matched(ew, expo)
    rows.append(dict(
        exp=e, hyp=cfg["hypothesis_id"], ver=cfg["strategy_version"], cycle=cfg.get("cycle", ""),
        slots=cfg["params"].get("slots"), exposure=float(expo.mean()),
        sharpe=metrics.sharpe(r), gross_sharpe=metrics.sharpe(gross_r), ew_sharpe=metrics.sharpe(rew),
        ew_matched_sharpe=metrics.sharpe(metrics.returns_from_equity(m_ew)),
        cagr=metrics.cagr(s), vol=float(r.std() * math.sqrt(252)), ew_vol=float(rew.std() * math.sqrt(252)),
        corr_ew=float(pd.concat([r, rew], axis=1).corr().iloc[0, 1]), beta=ab["beta"], alpha_ann=ab["alpha_ann"],
        alpha_t=ab["alpha_t"], comm_pa=comm, slip_pa=slip, cost_pa=comm + slip,
        trades_pa=len(closed) / years, avg_ret_trade=float(closed["ret"].mean()) if len(closed) else float("nan"),
        avg_hold=float((pd.to_datetime(closed["exit_date"]) - pd.to_datetime(closed["entry_date"])).dt.days.mean()) if len(closed) else float("nan"),
        idle_cash_drag_pa=float((1 - expo.mean()) * (ew.iloc[-1] / ew.iloc[0]) ** (1 / years) - (1 - expo.mean())) if False else float((1 - expo.mean()) * ((ew.iloc[-1] / ew.iloc[0]) ** (1 / years) - 1)),
        forced_share=float(closed["exit_tag"].astype(str).str.contains("forced", na=False).mean()) if len(closed) else 0.0,
    ))
D = pd.DataFrame(rows)
D["passes_sharpe_vs_ew_net"] = D["sharpe"] >= D["ew_sharpe"] + 0.1
D["passes_sharpe_vs_ew_gross"] = D["gross_sharpe"] >= D["ew_sharpe"] + 0.1
pd.set_option("display.width", 300); pd.set_option("display.max_columns", 40)
cols = ["exp", "hyp", "ver", "slots", "exposure", "sharpe", "gross_sharpe", "ew_sharpe", "ew_matched_sharpe", "vol", "ew_vol",
        "corr_ew", "beta", "alpha_ann", "alpha_t", "cost_pa", "comm_pa", "slip_pa", "trades_pa", "avg_ret_trade",
        "avg_hold", "idle_cash_drag_pa", "forced_share", "passes_sharpe_vs_ew_gross"]
print(D[cols].round(3).to_string(index=False))
R = pd.concat(rets, axis=1, join="inner")
C = R.corr()
h = D.set_index("exp")["hyp"]
within, across = [], []
for i, a in enumerate(C.columns):
    for b in C.columns[i + 1:]:
        (within if h[a] == h[b] else across).append(C.loc[a, b])
print("\nmean corr within hypothesis", round(np.mean(within), 2), "across hypotheses", round(np.mean(across), 2),
      "min/max across", round(min(across), 2), round(max(across), 2))
# first principal component share
ev = np.linalg.eigvalsh(C.to_numpy())[::-1]
print("PC1 share of variance across all", len(C), "variations:", round(ev[0] / ev.sum(), 2))
print("\nmeans:", D[["exposure", "sharpe", "gross_sharpe", "ew_sharpe", "vol", "ew_vol", "corr_ew", "beta", "cost_pa",
                    "idle_cash_drag_pa"]].mean().round(3).to_dict())
print("gross passes Sharpe vs EW+0.1:", D.loc[D.passes_sharpe_vs_ew_gross, "exp"].tolist())
json.dump(dict(rows=D.to_dict(orient="records"), within=float(np.mean(within)), across=float(np.mean(across)),
               pc1=float(ev[0] / ev.sum())), open(sys.argv[1], "w"), indent=1, default=float)
