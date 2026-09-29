"""X961 must run the unchanged C02 signal code: its sig0NN.py files are byte copies of the strategies'."""
import sys
import types

import pytest

from conftest import ROOT

PAIRS = {"sig006.py": "S006_breakout", "sig007.py": "S007_squeeze", "sig008.py": "S008_residual_rs",
         "sig009.py": "S009_volume_shock", "sig010.py": "S010_gap_hold", "sig011.py": "S011_seasonality"}
X961 = ROOT / "strategies/X961_signal_equivalence"


@pytest.mark.parametrize("copy", sorted(PAIRS))
def test_signal_copies_are_identical(copy):
    assert (X961 / copy).read_bytes() == (ROOT / "strategies" / PAIRS[copy] / "signals.py").read_bytes()


def test_canary_places_no_orders():
    src = (X961 / "main.py").read_text()
    assert "qr_rebalance" not in src and "qr_event_step" not in src and "market_order" not in src


def test_event_decisions_match_strategy_code(monkeypatch):
    """The canary's per-stock evaluation equals calling each strategy's functions as main.py does."""
    import numpy as np
    sys.path.insert(0, str(X961))
    fake = types.ModuleType("AlgorithmImports")
    monkeypatch.setitem(sys.modules, "AlgorithmImports", fake)
    harness = types.ModuleType("qr_harness")
    harness.QRAlgorithm = object
    monkeypatch.setitem(sys.modules, "qr_harness", harness)
    import importlib.util
    spec = importlib.util.spec_from_file_location("x961_main", X961 / "main.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    s6, s7 = mod.sig006, mod.sig007
    rng = np.random.default_rng(11)
    c = list(40 * np.exp(np.cumsum(rng.normal(0.0008, 0.012, 280))))
    o = [c[0]] + c[:-1]
    h = [max(a, b) * 1.004 for a, b in zip(o, c)]
    l = [min(a, b) * 0.996 for a, b in zip(o, c)]
    v = list(rng.integers(900_000, 1_100_000, 280).astype(float))
    d, ex = mod.SignalEquivalence._event_decisions(o, h, l, c, v)
    assert d["H006 v1.0"] == s6.breakout_strength(h, l, c, v, 55, 1.5, True)
    bw_ref = s7.contracted_bw(s7.bandwidth_series(c)[-252:], 0.10)
    exp = bw_ref if (bw_ref is not None and s7.expansion(h, l, c, v, use_trend=True)) else None
    assert d["H007 v1.0"] == exp
    assert ex[0] == s6.exit_signal(h, l, c, 20, 3.0, 60)
