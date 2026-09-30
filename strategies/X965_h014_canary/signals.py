"""S014 (H014, Phase 2) pure signal functions: numpy only, no QuantConnect imports, unit-tested offline.
Frozen by research/phase2/P2_spec.md §3-§5 (D094). Every array row is one stock; every window ends at
the completed bar T (the decision close); nothing reads a bar after T."""
import numpy as np

RSI_N = 14                 # Wilder RSI period
RSI_CHANGES = 250          # each day's RSI14 uses exactly the 250 close changes ending that day
RSI_DAYS = 9               # RSI14 is needed at T-8 ... T (pullback window up to 8, plus T)
MIN_BARS = RSI_CHANGES + RSI_DAYS    # 259 closes: the data requirement of every book
MODES = ("h014", "c1", "c2", "rand")


def rsi_weights(m=RSI_CHANGES, n=RSI_N):
    """Linear weights equal to Wilder's recursion over m changes, seeded by the simple mean of the first n:
    avg = seed (13/14)^(m-n) + sum_{i>=n} x_i (1/14)(13/14)^(m-1-i). The weights sum to 1."""
    a = (n - 1.0) / n
    w = np.empty(m)
    w[:n] = (1.0 / n) * a ** (m - n)
    w[n:] = (1.0 / n) * a ** (m - 1 - np.arange(n, m))
    return w


_W = rsi_weights()


def rsi_matrix(closes, days=RSI_DAYS):
    """closes: (n_stocks, >= RSI_CHANGES + days) array ending at T. Returns (n_stocks, days): RSI14 at
    T-days+1 ... T, each over its own 250 changes. RSI = 100 if the average loss is 0 (50 if both are 0)."""
    c = np.asarray(closes, float)[:, -(RSI_CHANGES + days):]
    d = np.diff(c, axis=1)                                          # (n, RSI_CHANGES + days - 1)
    win = np.lib.stride_tricks.sliding_window_view(d, RSI_CHANGES, axis=1)   # (n, days, 250)
    g = np.maximum(win, 0.0) @ _W
    l = np.maximum(-win, 0.0) @ _W
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + g / l)
    r = np.where(l > 0, r, np.where(g > 0, 100.0, 50.0))
    return r


def features(closes, high_prev):
    """closes: (n, MIN_BARS) adjusted closes ending at T; high_prev: (n,) adjusted High(T-1)."""
    c = np.asarray(closes, float)
    if c.ndim != 2 or c.shape[1] < MIN_BARS:
        raise ValueError(f"need a (n, >= {MIN_BARS}) close matrix")
    c = c[:, -MIN_BARS:]
    return dict(close=c[:, -1], ma50=c[:, -50:].mean(axis=1), ma200=c[:, -200:].mean(axis=1),
                rsi=rsi_matrix(c), mom=c[:, -22] / c[:, -253] - 1.0, high_prev=np.asarray(high_prev, float))


def trend(f):
    """U1 Close > MA200 and U2 MA50 > MA200."""
    return (f["close"] > f["ma200"]) & (f["ma50"] > f["ma200"])


def entry_mask(f, mode, rsi_pullback=40.0, window=5, rsi_recovery=45.0):
    """The book's entry signal at T. h014: trend + min RSI14(T-window..T-1) <= pullback + RSI14(T) > recovery
    + Close(T) > High(T-1). c1: trend. c2: trend + RSI14(T) <= pullback. rand: trend (random order)."""
    t = trend(f)
    rsi_t = f["rsi"][:, -1]
    if mode in ("c1", "rand"):
        return t
    if mode == "c2":
        return t & (rsi_t <= rsi_pullback)
    if mode == "h014":
        w = int(window)
        if not 1 <= w <= RSI_DAYS - 1:
            raise ValueError("pullback window must be 1..8 sessions")
        prior = f["rsi"][:, -1 - w:-1]
        return t & (prior.min(axis=1) <= rsi_pullback) & (rsi_t > rsi_recovery) & (f["close"] > f["high_prev"])
    raise ValueError(f"unknown mode {mode!r}")


def momentum_order(ids, mom):
    """Ids by 12-1 momentum, highest first; ties (and non-finite momentum, last) by id ascending."""
    key = [(-(m if np.isfinite(m) else -np.inf), i) for i, m in zip(ids, mom)]
    return [i for _, i in sorted(key)]


def exit_decision(held, close, ma200, variant, limit, entry_signal):
    """Exit rule at the close for one held stock. variant 'A': horizon `limit` with horizon roll;
    'B': cap `limit`, no roll. Returns 'ma200' | 'time' | 'roll' | None ('roll' = keep, restart the clock)."""
    if close < ma200:
        return "ma200"
    if held is None or held < int(limit):
        return None
    if variant == "A":
        return "roll" if entry_signal else "time"
    if variant == "B":
        return "time"
    raise ValueError(f"unknown exit variant {variant!r}")
