"""H017 evaluation (qresearch.p2h017) and freezes: the spec and the event table are hash-pinned; Amendment 3 is
unchanged; the month-clustered t; the PbNQ rule (all seven, in order; an item not evaluated fails); the conditional-run
rules; the decision tree (C needs G4', B needs PbNQ, everything else is A); no H017 config reaches the Holdout."""
import json

import numpy as np
import pandas as pd
import pytest

from conftest import ROOT
from qresearch import p2h017 as H, wealth


def test_spec_is_frozen_and_hash_pinned():
    assert len(H.SPEC_SHA256) == 64
    assert H.spec_hash() == H.SPEC_SHA256          # any change to H017_spec.md -> STOP and ask the owner


def test_event_table_is_frozen_and_hash_pinned():
    import gzip
    import hashlib
    import importlib.util
    m = H.event_manifest()
    assert m["payload_sha256"] == H.EVENT_TABLE_SHA256
    cb = gzip.decompress((ROOT / "research/phase2/h017/event_table_v1.csv.gz").read_bytes())
    assert hashlib.sha256(cb).hexdigest() == m["csv_sha256"]
    spec = importlib.util.spec_from_file_location("qr_h017_events", ROOT / "src/qresearch/lean/qr_h017_events.py")
    mod = importlib.util.module_from_spec(spec)
    import sys
    sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
    try:
        spec.loader.exec_module(mod)
        t = mod.load_events()                     # reassembles the packed parts and checks the pinned SHA-256
    finally:
        sys.path.remove(str(ROOT / "src/qresearch/lean"))
    assert mod.SHA256 == H.EVENT_TABLE_SHA256
    raw = json.dumps(t, separators=(",", ":"), sort_keys=True).encode()
    assert hashlib.sha256(raw).hexdigest() == H.EVENT_TABLE_SHA256
    assert len(t["events"]) == m["counts"]["events"]
    assert m["counts"]["last_decision"] <= "2021-12-31" and m["window"]["decision_last"] == "2021-12-31"


def test_event_table_canary_passed():
    c = json.loads((ROOT / "research/phase2/h017/h017_event_table_canary.json").read_text())
    assert c["all_ok"] and c["table"] == H.EVENT_TABLE_SHA256
    assert c["checks"]["3_edgar_sample"]["matches"] == c["checks"]["3_edgar_sample"]["sample"] == 50


def test_amendment3_unchanged():
    assert wealth.spec_hash() == wealth.AMENDMENT3_SHA256


def test_clustered_t_matches_aggregated_version():
    rng = np.random.default_rng(5)
    x = rng.normal(0.01, 0.1, 600)
    months = rng.integers(0, 40, 600)
    a = H.clustered_t(x, months)
    n_m = pd.Series(1, index=months).groupby(level=0).sum().to_dict()
    s_m = pd.Series(x, index=months).groupby(level=0).sum().to_dict()
    b = H.clustered_from_sums(n_m, s_m)
    assert a["mean"] == pytest.approx(b["mean"]) and a["se"] == pytest.approx(b["se"]) and a["t"] == pytest.approx(b["t"])
    # one observation per cluster -> the iid SE with an M/(M-1) correction
    c = H.clustered_t(x, np.arange(600))
    assert c["se"] == pytest.approx(x.std(ddof=1) / np.sqrt(600), rel=1e-9)


def test_event_rule():
    assert H.event_rule(dict(mean=0.01, t=2.5), dict(mean=0.002))["ok"]
    assert not H.event_rule(dict(mean=0.01, t=1.9), dict(mean=0.002))["ok"]
    assert not H.event_rule(dict(mean=0.001, t=2.5), dict(mean=0.002))["ok"]
    assert not H.event_rule(dict(mean=-0.01, t=2.5), dict(mean=-0.02))["ok"]
    assert not H.event_rule(dict(mean=float("nan"), t=2.5), dict(mean=0.0))["ok"]


def gates_like(w1=True, excess=0.02, g=0.03, se=0.02, w2=False, w3=True, r=(True, True, True, True)):
    core = w1 and w2 and w3 and r[0] and r[1] and r[2]
    return dict(W1=dict(ok=w1, excess=excess), W2=dict(g=g, se=se, ok=w2), W3=dict(ok=w3), R1=dict(ok=r[0]),
                R2=dict(ok=r[1]), R3=dict(ok=r[2]), R4=dict(ok=r[3]), core_ok=core)


def test_pbnq_requires_all_seven_rules():
    ev = dict(ok=True)
    assert H.pbnq(gates_like(), True, ev)["ok"]
    assert not H.pbnq(gates_like(w1=False), True, ev)["ok"]
    assert not H.pbnq(gates_like(excess=0.009), True, ev)["ok"]
    assert not H.pbnq(gates_like(g=0.019, se=0.02), True, ev)["ok"]       # g/SE < 1
    assert not H.pbnq(gates_like(w2=True), True, ev)["ok"]                # W2 passes -> qualified path, not PbNQ
    assert not H.pbnq(gates_like(w3=False), True, ev)["ok"]
    for i in range(4):
        r = [True] * 4
        r[i] = False
        assert not H.pbnq(gates_like(r=tuple(r)), True, ev)["ok"]
    assert not H.pbnq(gates_like(), False, ev)["ok"]
    assert not H.pbnq(gates_like(), None, ev)["ok"]                       # 2x slippage not run -> fails
    assert not H.pbnq(gates_like(), True, None)["ok"]                     # E983-01 not run -> fails
    assert not H.pbnq(gates_like(), True, dict(ok=False))["ok"]


def test_decision_tree():
    pb_ok = H.pbnq(gates_like(), True, dict(ok=True))
    pb_no = H.pbnq(gates_like(w1=False), True, dict(ok=True))
    full = gates_like(w2=True)
    assert H.decide(full, dict(ok=True), pb_no)["case"] == "C"
    assert H.decide(full, dict(ok=False), pb_no)["case"] == "A"          # W1-R4 pass but G4' fails -> A
    assert H.decide(full, None, pb_no)["case"] == "A"
    assert H.decide(gates_like(), None, pb_ok)["case"] == "B"
    assert H.decide(gates_like(w1=False), None, pb_no)["case"] == "A"
    nr4 = gates_like(w2=True, r=(True, True, True, False))
    assert H.decide(nr4, dict(ok=True), pb_no)["case"] == "A"


def test_conditional_runs():
    assert H.conditional_runs(gates_like()) == {H.SLIP_2X: True, "E017-10..17": False}
    assert H.conditional_runs(gates_like(w2=True)) == {H.SLIP_2X: True, "E017-10..17": True}
    assert H.conditional_runs(gates_like(w1=False)) == {H.SLIP_2X: False, "E017-10..17": False}
    assert H.conditional_runs(gates_like(excess=0.005)) == {H.SLIP_2X: False, "E017-10..17": False}


def test_run_ids_and_holdout_lock():
    assert H.CANDIDATE == "E017-01" and H.RANDOM == ("E017-03", "E017-04", "E017-05", "E017-06", "E017-07")
    assert len(H.PERTURBATIONS) == 6 and H.CANARY not in H.APPROVAL_REQUIRED and H.CANDIDATE in H.APPROVAL_REQUIRED
    for eid in (H.CANARY, *H.APPROVAL_REQUIRED):
        cfg = json.loads((ROOT / "experiments" / eid / "config.json").read_text())
        assert cfg["end"] <= "2021-12-31" and cfg["start"] == H.COMMON_START and cfg["warmup_start"] == H.WARMUP_START


def test_gates_use_the_frozen_amendment3_on_aligned_returns():
    idx = pd.Index([f"2010-03-{d:02d}" for d in range(1, 31)])
    rng = np.random.default_rng(1)
    eqs = {k: pd.Series(100 * np.cumprod(1 + rng.normal(0.0005, 0.01, 30)), index=idx)
           for k in ("H", "SPY", "EW", "a", "b", "c", "d", "e")}
    R = H.aligned_returns(eqs)
    g = H.gates(R, "H", "SPY", "EW", ["a", "b", "c", "d", "e"], 0.01, True, True)
    ref = wealth.evaluate_gates(R["H"], R["SPY"], R["EW"], [R[k] for k in "abcde"], dates=list(R.index),
                                cost_pa=0.01)
    assert g["W1"] == ref["W1"] and g["W2"] == ref["W2"] and g["qualified"] == ref["qualified"]
