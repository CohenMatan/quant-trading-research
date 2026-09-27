import numpy as np
import pandas as pd

from qresearch.lookahead import truncation_violations
from conftest import ROOT, load_module

signals = load_module(ROOT / "strategies/S000_pipeline_demo/signals.py", "s000_signals")


def _prices(n=400, seed=1):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2001-01-01", periods=n)
    return pd.Series(100 * np.exp(np.cumsum(rng.normal(0, 0.02, n))), index=idx)


def s000_signal(closes: pd.Series) -> pd.Series:
    return closes.rolling(6).apply(lambda w: signals.trailing_return(list(w), 5), raw=True)


def test_s000_trailing_return_has_no_lookahead():
    assert truncation_violations(s000_signal, _prices(), n_checks=80) == []


def test_checker_detects_lookahead():
    def peeking(closes):
        return closes.shift(-1) / closes - 1.0   # uses tomorrow's close
    assert truncation_violations(peeking, _prices(), n_checks=30) != []


def test_checker_detects_full_sample_normalisation():
    def zscore_full(closes):
        r = closes.pct_change()
        return (r - r.mean()) / r.std()           # uses statistics of the whole sample
    assert truncation_violations(zscore_full, _prices(), n_checks=30) != []


def test_s000_selection_depends_only_on_the_signal_window():
    px = {f"S{i}": list(_prices(60, seed=i)) for i in range(30)}
    liq = {k: float(i) for i, k in enumerate(px)}
    picks = signals.select_entries(px, liq, set(), 5, lookback=5, pool=20)
    older_changed = {k: [x * 3 for x in v[:-6]] + v[-6:] for k, v in px.items()}
    assert picks == signals.select_entries(older_changed, liq, set(), 5, lookback=5, pool=20)
    last = sorted(px)[0]
    moved = dict(px, **{last: px[last][:-1] + [px[last][-1] * 0.5]})
    assert signals.select_entries(moved, liq, set(), 5, lookback=5, pool=30)[0] == last
    assert len(picks) == 5


def test_s000_selection_is_deterministic_and_respects_exclusions():
    windows = {"A": [10, 9], "B": [10, 9], "C": [10, 11], "D": [10, 8]}
    liq = {"A": 3.0, "B": 3.0, "C": 2.0, "D": 1.0}
    assert signals.select_entries(windows, liq, set(), 2, lookback=1, pool=10) == ["D", "A"]
    assert signals.select_entries(windows, liq, {"D"}, 2, lookback=1, pool=10) == ["A", "B"]
    assert signals.select_entries(windows, liq, set(), 2, lookback=1, pool=2) == ["A", "B"]
    assert signals.trailing_return([1.0], 5) is None


def test_lean_algorithm_uses_the_pure_signal_module(root):
    src = (root / "strategies/S000_pipeline_demo/main.py").read_text()
    assert "from signals import select_entries" in src
