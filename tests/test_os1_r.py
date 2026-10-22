"""H032 R1 / R2 (owner D282): pins of the frozen implementation / evaluation protocol and code (qresearch.os1r), the
S033 config rule and run configuration, the runner upload set (pinned X807 host byte-identical as qr_x807, the engine
copy, the trading layer, no compressed module), and the frozen evaluation rule OS1_R_eval on synthetic series and on
the end-to-end fake run (validity checks, fidelity numbers, O-gates, report)."""
import json
import math
import sys
from datetime import date

import numpy as np
import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "research/os"))
import OS1_R_eval as EV  # noqa: E402


def test_pins_and_config():
    from qresearch import experiment, os1, os1r as P
    assert P.PROTOCOL_SHA256 and P.file_sha256(P.PROTOCOL) == P.PROTOCOL_SHA256
    changed = [f for f, h in P.CODE_SHA256.items() if h is None or P.file_sha256(f) != h]
    assert not changed, f"pinned H032 R files changed: {changed}"
    assert os1.file_sha256(os1.SPEC) == os1.SPEC_SHA256                      # the H032 specification is unchanged
    assert P.file_sha256(os1.HOST) == os1.CODE_SHA256[os1.HOST]              # the canary host S033 subclasses
    import OS1_R_configs as C
    cfg = json.loads((ROOT / "experiments" / P.R1 / "config.json").read_text())
    experiment.validate(cfg)
    assert cfg == C.build(P.R1) and cfg["costs"]["slippage_bps"] == 10 and "slippage_stress_multiple" not in cfg["costs"]
    r2 = C.build(P.R2)["costs"]
    assert r2["slippage_bps"] == 10 and r2["slippage_stress_multiple"] == 2            # 20 bps per side
    from qresearch.holdout import HoldoutLockedError
    bad = [dict(cfg, experiment_id="E033-05"), dict(cfg, end="2022-06-30"), dict(cfg, start="2012-08-31"),
           dict(cfg, warmup_start="2010-01-04"), dict(cfg, costs=dict(cfg["costs"], slippage_stress_multiple=2)),
           dict(cfg, params=dict(cfg["params"], start_review="2012-08-31")), dict(cfg, hypothesis_id="H031"),
           dict(cfg, portfolio=dict(cfg["portfolio"], max_positions=20)), dict(cfg, cash=200000),
           {k: v for k, v in cfg.items() if k != "owner_approval_required"}]
    for b in bad:
        with pytest.raises((experiment.ConfigError, HoldoutLockedError)):
            experiment.validate(b)


def test_upload_set():
    from qresearch import run
    files = run.assemble_files({"strategy_dir": "strategies/S033_h032_os1", "experiment_id": "E033-01",
                                "start": "2012-07-31", "end": "2021-12-31", "cash": 100000, "universe": {},
                                "costs": {}, "portfolio": {}, "params": {}}, None, False)
    assert {"main.py", "qr_x807.py", "qr_os1.py", "qr_ucr.py", "qr_os1_books.py", "qr_os1_trade.py",
            "qr_harness.py"} <= set(files)
    assert files["qr_x807.py"] == (ROOT / "strategies/X807_os1_canary/main.py").read_text()
    assert not any(n.startswith(("qr_p3", "qr_data_v", "qr_sec_data", "qr_p7_export", "qr_h0")) for n in files)
    run.check_upload(files)


def test_statistics_helpers():
    rng = np.random.default_rng(1)
    x = rng.normal(0.01, 0.04, 400)
    y = 0.002 + 1.3 * x + rng.normal(0, 0.01, 400)
    a, b, ta, tb = EV.nw_ols(y, x, 2)
    assert a == pytest.approx(0.002, abs=0.002) and b == pytest.approx(1.3, abs=0.05) and tb > 20
    cap = EV.captures(np.array([0.02, -0.01, 0.03, -0.02]), np.array([0.01, -0.02, 0.02, -0.01]))
    assert cap["up"] == pytest.approx(0.025 / 0.015) and cap["down"] == pytest.approx(0.015 / 0.015)
    dates = ["2012-07-31", "2012-08-01", "2012-08-31", "2012-09-04", "2012-09-28"]
    assert EV.month_ends(dates) == [0, 2, 4]
    r, m = EV.monthly([100, 101, 102, 103, 104], dates)
    assert m == ["2012-08", "2012-09"] and r[0] == pytest.approx(0.02)


def _synthetic(edge):
    """A daily grid 2012-07-31 .. 2021-12-31 with SPY, LEAN = SPY plus a steady edge, and controls."""
    d = np.arange(np.datetime64("2012-07-31"), np.datetime64("2022-01-01"))
    dates = [str(x) for x in d[np.is_busday(d)]]
    rng = np.random.default_rng(3)
    rs = rng.normal(0.0005, 0.01, len(dates) - 1)
    spy = np.concatenate([[1.0], np.cumprod(1 + rs)])
    lean = 1e5 * np.concatenate([[1.0], np.cumprod(1 + rs + edge / 252 + rng.normal(0, 0.002, len(rs)))])
    eq = {"LEAN": lean, "SPY": spy, "B1": lean.copy()}
    for name in ("VB1", "B0", "MOM") + tuple(f"{k}_{s}" for k, v in EV.SEEDS.items() for s in v):
        eq[name] = 1e5 * np.concatenate([[1.0], np.cumprod(1 + rs + rng.normal(0, 0.002, len(rs)))])
    me = [dates[i] for i in EV.month_ends(dates)][1:]
    ew = [(t if t != me[-1] else "end", 0.008, 0.008, 300, 0, 250, 0) for t in me]
    return dict(dates=dates, ew=ew, meta=dict(books=[], first_review_traded="2012-07-31")), eq


def test_gates_on_synthetic_series():
    out, eq = _synthetic(0.08)
    g = EV.gates(out, eq)
    assert g["O1"]["passed"] and g["O1"]["excess"] > 0.05 and g["O2"]["ratio"] > 1
    assert g["O4"]["alpha_monthly"] > 0 and g["O5"]["beaten"] == {"B2": 5, "RND": 5, "BETA": 5}
    assert set(g) == {"O1", "O2", "O3", "O4", "O5", "O6", "O7", "O9"}
    out2, eq2 = _synthetic(-0.08)
    g2 = EV.gates(out2, eq2)
    assert not g2["O1"]["passed"] and not g2["O2"]["passed"] and not g2["O7"]["passed"]
    f = EV.fidelity(out, eq)
    assert f["passed"] and f["terminal_relative"] == 0 and f["max_month_abs"] == 0
    eq3 = dict(eq, B1=eq["LEAN"] * np.linspace(1, 1.02, len(eq["LEAN"])))
    f3 = EV.fidelity(out, eq3)
    assert not f3["passed"] and f3["terminal_relative"] == pytest.approx(0.02)


def test_eval_on_fake_end_to_end_run():
    import test_os1_trade as TT
    mp = pytest.MonkeyPatch()
    try:
        a = TT._run(mp)
    finally:
        mp.undo()
    out, eq = EV.parse(a._qr_msgs)
    r = dict(status="completed", integrity=[], harness_summary=a._qr_stats)
    v = EV.validity(r, out, eq)
    assert v["I1"]["passed"] and v["I3"]["passed"] and v["I4"]["passed"]
    assert v["F"]["passed"] and v["F"]["max_month_abs"] == pytest.approx(0, abs=1e-9)
    assert not v["I2"]["passed"]                       # the fake market starts in 2010, not on the frozen start review
    g = EV.gates(out, eq)
    assert set(g) == {"O1", "O2", "O3", "O4", "O5", "O6", "O7", "O9"}
    rep = EV.report(r, out, eq, "E033-FAKE")
    assert rep["positions"]["max"] <= 15 and set(rep["table"]) >= {"LEAN", "SPY", "B1", "VB1", "B0"}
