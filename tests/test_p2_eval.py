"""P2_eval.py end to end on SYNTHETIC runs in a temporary experiments directory (no H014 result exists when
this test is written): selection, gates, trigger, diagnostics and the output structure; plus the rule that a
missing run fails its gate instead of being guessed."""
import importlib.util
import json
import shutil

import numpy as np
import pandas as pd
import pytest

from conftest import ROOT
from qresearch import config, results


def _mod():
    spec = importlib.util.spec_from_file_location("p2eval", ROOT / "research/phase2/P2_eval.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _write_run(d, eid, r, cfg, n_orders=400):
    d = d / eid
    d.mkdir(parents=True)
    eq = 100000 * np.cumprod(1 + r.to_numpy())
    dates = list(r.index)
    e = pd.DataFrame(dict(date=dates, equity=eq, cash=eq * 0.1, npos=11, nelig=900))
    results.write_gz(d / "equity.csv.gz", results.canonical_csv(e))
    idx = np.linspace(0, len(dates) - 60, n_orders // 2).astype(int)
    tr = pd.DataFrame(dict(symbol_id=[f"S{i} X" for i in range(len(idx))], symbol=[f"S{i}" for i in range(len(idx))],
                           entry_date=[dates[i] for i in idx], exit_date=[dates[i + 50] for i in idx], status="closed",
                           cost=8000.0, proceeds=8100.0, fees=14.0, pnl=86.0, ret=0.0108, n_fills=2, max_qty=100.0,
                           exit_tag="s014"))
    results.write_gz(d / "trades.csv.gz", results.canonical_csv(tr))
    fi = pd.DataFrame(dict(order_id=range(n_orders), symbol_id="S X", symbol="S",
                           date=[dates[i] for i in np.linspace(0, len(dates) - 1, n_orders).astype(int)],
                           quantity=100.0, price=80.0, fee=7.0, tag="s014|sig=x"))
    results.write_gz(d / "fills.csv.gz", results.canonical_csv(fi))
    (d / "config.json").write_text(json.dumps(cfg))
    (d / "result.json").write_text(json.dumps(dict(status="completed", harness_summary={"skipped_min_position": 0})))


@pytest.fixture
def fake(tmp_path):
    exp = tmp_path / "experiments"
    exp.mkdir()
    for b in ("E901-07", "E900-07"):
        shutil.copytree(config.EXPERIMENTS_DIR / b, exp / b)
    ew = results.read_csv_gz(exp / "E901-07" / "equity.csv.gz")
    s = pd.Series(ew["equity"].to_numpy(float), index=ew["date"].astype(str))
    r_ew = s.pct_change().dropna()
    rng = np.random.default_rng(7)
    noise = lambda k, sd=0.004: pd.Series(np.random.default_rng(k).normal(0, sd, len(r_ew)), index=r_ew.index)  # noqa: E731
    books = {}
    for i in range(1, 24):
        eid = f"E014-{i:02d}"
        cfg = json.loads((config.EXPERIMENTS_DIR / eid / "config.json").read_text()) if i <= 14 else None
        if i == 1:
            r = r_ew * 0.8 + 0.0003 + noise(1)       # a strong synthetic candidate A
        elif i == 2:
            r = r_ew * 0.8 + 0.0001 + noise(2)       # B weaker
        elif i <= 12:
            r = r_ew + noise(i)                      # controls ~ EW
        elif i <= 14:
            r = r_ew * 0.8 + 0.0003 + noise(1)
        else:
            base = json.loads((config.EXPERIMENTS_DIR / "E014-01" / "config.json").read_text())
            cfg = dict(base, experiment_id=eid, robustness_of="E014-01", description=f"synthetic perturbation {eid}")
            if i <= 17:
                cfg["costs"] = dict(base["costs"], slippage_stress_multiple={15: 2, 16: 4, 17: 6}[i])
            r = r_ew * 0.8 + 0.00025 + noise(i)
        books[eid] = r
        _write_run(exp, eid, r, cfg)
    return exp


def test_p2_eval_end_to_end_on_synthetic_runs(fake, monkeypatch, tmp_path):
    m = _mod()
    monkeypatch.setattr(m, "EXP", fake)
    m._CACHE.clear()
    out_path = tmp_path / "P2_results.json"
    m.main(out_path)
    out = json.loads(out_path.read_text())
    assert out["spec_hash_ok"]
    assert out["selection"]["chosen"] == "A" and out["selection"]["chosen_id"] == "E014-01"
    g = out["gates"]["A"]
    assert g["G1"]["ok"] and g["G2"]["ok"] and g["robustness_trigger"] == g["G3"]["ok"]
    assert set(g["G4"]["items"]) == {"G4a", "G4b", "G4c"}
    assert out["gates"]["B"]["classification"]["development-qualified"] is False
    d = out["diagnostics_not_gates"]
    assert set(d["dsr"]) == {"P2 candidates", "P2 broad", "cumulative"}
    assert d["pbo_candidates"]["pbo"] is not None and "C1" in d["bootstrap_sharpe_diff"]
    assert set(d["yearly"]) >= {"H014 A", "EW", "SPY"}
    for e in [f"E014-{i:02d}" for i in range(1, 15)]:
        b = out["books"][e]
        assert {"exposure_mean", "cash_mean", "slot_usage", "costs"} <= set(b)
    assert out["may_request_holdout"] == out["development_qualified"] == g["ok"]


def test_missing_robustness_runs_fail_g4(fake, monkeypatch, tmp_path):
    m = _mod()
    for i in range(15, 24):
        shutil.rmtree(fake / f"E014-{i}")
    monkeypatch.setattr(m, "EXP", fake)
    m._CACHE.clear()
    import numpy as _np  # noqa: F401
    ew = m.p2spec.equity_series(m.load("E901-07")["eq"])
    spy = m.p2spec.equity_series(m.load("E900-07")["eq"])
    g = m.gates_for("A", m.p2spec.returns(ew), m.p2spec.returns(spy), ew, spy, with_robustness=True)
    assert not g["G4"]["ok"] and not g["ok"]
