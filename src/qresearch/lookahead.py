"""Look-ahead detection by truncation.

A signal function maps a history (Series/DataFrame indexed by date) to a Series of signal values
on the same index. It is free of look-ahead iff, for every date t, the value it gives at t on the
full history equals the value it gives at t when the history is cut off at t.
"""
from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd


def truncation_violations(signal_fn: Callable[[pd.Series | pd.DataFrame], pd.Series],
                          history: pd.Series | pd.DataFrame, n_checks: int = 50,
                          seed: int = 0, atol: float = 1e-12) -> list:
    """Return the dates where signal(full)[t] != signal(history[:t])[t] (empty list = pass)."""
    full = signal_fn(history)
    rng = np.random.default_rng(seed)
    positions = sorted(set(rng.integers(1, len(history), size=n_checks).tolist()) | {len(history) - 1})
    bad = []
    for pos in positions:
        t = history.index[pos]
        cut = signal_fn(history.iloc[: pos + 1])
        a, b = full.loc[t], cut.loc[t]
        both_nan = pd.isna(a) and pd.isna(b)
        if not both_nan and (pd.isna(a) or pd.isna(b) or abs(float(a) - float(b)) > atol):
            bad.append(t)
    return bad
