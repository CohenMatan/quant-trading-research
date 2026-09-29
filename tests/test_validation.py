"""D056: Validation gate and exposure-aware comparison."""
import numpy as np
import pandas as pd

from qresearch import validation


def _eq(rets, start="2018-01-02", cash_frac=0.0):
    d = pd.bdate_range(start, periods=len(rets) + 1).strftime("%Y-%m-%d")
    e = 100_000 * np.cumprod(np.r_[1.0, 1.0 + np.asarray(rets)])
    return pd.DataFrame({"date": d, "equity": e, "cash": e * cash_frac})


def test_exposure_matched_benchmark_scales_returns_by_previous_exposure():
    b = _eq([0.01, -0.02, 0.03])
    bench = pd.Series(b["equity"].to_numpy(), index=b["date"])
    expo = pd.Series([0.5, 0.5, 1.0, 1.0], index=b["date"])
    m = validation.exposure_matched(bench, expo)
    r = m.pct_change().dropna().round(10).tolist()
    assert r == [0.005, -0.01, 0.03]            # weight of the previous close


def test_alpha_beta_recovers_known_values():
    rng = np.random.default_rng(1)
    rb = pd.Series(rng.normal(0, 0.01, 2000))
    r = 0.5 * rb + 0.0002
    ab = validation.alpha_beta(r, rb)
    assert abs(ab["beta"] - 0.5) < 1e-9 and abs(ab["alpha_ann"] - 0.0504) < 1e-9


def test_val_gate_pass_and_fail_paths():
    rng = np.random.default_rng(2)
    good = _eq(rng.normal(0.0008, 0.005, 1000))
    ew = _eq(rng.normal(0.0003, 0.01, 1000))
    ews = pd.Series(ew["equity"].to_numpy(), index=ew["date"])
    trades = pd.DataFrame({"status": ["closed"] * 60, "ret": [0.01] * 60, "pnl": [10.0] * 60,
                           "entry_date": good["date"].iloc[:60].to_numpy(),
                           "exit_date": good["date"].iloc[1:61].to_numpy()})
    r = good["equity"].pct_change().dropna().to_numpy()
    chk = {c["gate"]: c["ok"] for c in validation.val_gate(good, trades, 1.0, ews, r, 1, 0.0, 0.71)}
    assert chk["VAL Sharpe"] and chk["VAL Sharpe vs EW"] and chk["VAL closed trades"]
    assert chk["PBO (CSCV on IS, from CP3)"] is False           # the known CP3 value fails, unchanged
    chk2 = {c["gate"]: c["ok"] for c in validation.val_gate(good, trades.iloc[:10], 100.0, ews, r, 1, 0.0, 0.1)}
    assert not chk2["VAL closed trades"] and not chk2["VAL Sharpe vs IS"] and chk2["PBO (CSCV on IS, from CP3)"]
