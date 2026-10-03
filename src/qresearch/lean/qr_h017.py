# qr_h017.py — H017 (earnings-event continuation) pure decision logic (research/phase2/H017_spec.md, frozen). No
# QuantConnect imports: unit-tested offline (tests/test_h017.py). Used identically by the candidate, the random-event
# controls, the canary and the same-universe EW book (S017, one code path; only the ranking of entries differs).
#
#   reaction    AR = [Close(E+1)/Close(E-1) - 1] - [SPY Close(E+1)/SPY Close(E-1) - 1]   (adjusted closes)
#   breakpoint  90th percentile (linear interpolation) of AR over all universe events whose decision session lies in
#               the previous 252 sessions, strictly before today; at least 400 such events, else no signal
#   signal      AR >= breakpoint and AR > 0
#   capacity    10 slots; signals ranked by AR (highest first, ties by security id) fill the free slots; the rest is
#               dropped (no queue, no replacement); events of held (or pending) stocks are ignored
#   random      the same capacity rule; at most k_t entries (k_t = the day's candidate signal count) chosen among all
#               universe events of the day by the fixed key SHA-256("seed|security id|event date")
#   holding     the exit order is placed at the close of the 59th session after the entry session (sessions held = 59)
#               and executes at the open of entry + 60 sessions
import hashlib
import math
from collections import deque

HOLD_SESSIONS = 60
TOP_QUANTILE = 0.90
LOOKBACK_SESSIONS = 252
MIN_HISTORY_EVENTS = 400
SLOTS = 10


def reaction(c_m1, c_p1, spy_m1, spy_p1):
    """Two-session SPY-adjusted reaction, or None if any close is missing or not positive."""
    for x in (c_m1, c_p1, spy_m1, spy_p1):
        if x is None or not (x > 0) or math.isinf(x):
            return None
    return (c_p1 / c_m1 - 1.0) - (spy_p1 / spy_m1 - 1.0)


def quantile(values, q):
    """Linear-interpolation quantile (numpy's default 'linear' method) of a non-empty sequence."""
    x = sorted(values)
    h = (len(x) - 1) * float(q)
    lo = int(math.floor(h))
    hi = min(lo + 1, len(x) - 1)
    return x[lo] + (h - lo) * (x[hi] - x[lo])


class Breakpoints:
    """Trailing point-in-time reaction history: (decision session index, AR) of universe events, added in
    non-decreasing session order. threshold(t) uses only events with t - LOOKBACK <= index < t."""

    def __init__(self, lookback=LOOKBACK_SESSIONS, q=TOP_QUANTILE, min_events=MIN_HISTORY_EVENTS):
        self.lookback, self.q, self.min_events = int(lookback), float(q), int(min_events)
        self.hist = deque()
        self.last_index = None

    def add(self, index, ar):
        if self.last_index is not None and index < self.last_index:
            raise ValueError("reaction history must be added in session order")
        self.last_index = index
        self.hist.append((int(index), float(ar)))

    def sample(self, t):
        while self.hist and self.hist[0][0] < t - self.lookback:
            self.hist.popleft()
        return [a for i, a in self.hist if i < t]

    def threshold(self, t):
        """(breakpoint or None, sample size, newest sample index or None) for decisions on session t."""
        s = self.sample(t)
        newest = max((i for i, _ in self.hist if i < t), default=None)
        if len(s) < self.min_events:
            return None, len(s), newest
        return quantile(s, self.q), len(s), newest


DECILE_QS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)


def breakpoints_of(sample, qs):
    """Quantiles of a non-empty sample (linear interpolation), one per q in `qs`."""
    return [quantile(sample, q) for q in qs]


def decile_of(ar, bps):
    """Reaction decile 1..10: 1 + the number of breakpoints p10..p90 that AR is at or above (E983-01, spec §8)."""
    return 1 + sum(1 for b in bps if ar >= b)


def tercile_of(x, bps):
    """Tercile 1..3 from the two breakpoints (1/3, 2/3)."""
    return 1 + sum(1 for b in bps if x >= b)


def qualifies(ar, thr):
    return thr is not None and ar is not None and ar >= thr and ar > 0


def rank_signals(signals):
    """[(key, AR)] -> keys by AR, highest first; ties by key ascending."""
    return [k for k, _ in sorted(signals, key=lambda x: (-x[1], x[0]))]


def random_key(seed, key, event_date):
    """Frozen pseudo-random key of an event (independent of any price): SHA-256 of 'seed|security id|event date'."""
    return int(hashlib.sha256(f"{int(seed)}|{key}|{event_date}".encode()).hexdigest()[:16], 16)


def rank_random(events, seed):
    """[(key, event date 'YYYY-MM-DD')] -> keys ordered by their fixed random key for `seed`; ties by key."""
    return [k for k, d in sorted(events, key=lambda x: (random_key(seed, x[0], x[1]), x[0]))]


def plan_entries(ranked, blocked, free, cap):
    """Entries of one decision close: walk `ranked` (best first), skip blocked keys (held or pending: their events are
    ignored), take at most min(free, cap). Everything else is dropped (never queued)."""
    n = max(0, min(int(free), int(cap)))
    out = []
    for k in ranked:
        if len(out) >= n:
            break
        if k in blocked or k in out:
            continue
        out.append(k)
    return out


def free_slots(n_slots, n_held, n_pending_buys):
    """Slots free at a close: holdings after the exits executed so far (positions with an exit order placed at this
    close still occupy their slot until it executes) minus entries already pending."""
    return max(0, int(n_slots) - int(n_held) - int(n_pending_buys))


def exit_due(sessions_held, hold=HOLD_SESSIONS):
    """True at the close where the fixed-horizon exit order must be placed (it executes at the next open)."""
    return sessions_held is not None and sessions_held >= hold - 1


def ew_member(last_decision_index, t, lookback=LOOKBACK_SESSIONS):
    """EW-H017 universe membership (verified domestic event filer at t): an event of the security had its decision
    session within the trailing `lookback` sessions (t - lookback < index <= t)."""
    return last_decision_index is not None and t - lookback < last_decision_index <= t


def bar_date(t):
    """Session date of a LEAN daily bar from its end time (16:00 same day, or 00:00 of the next day)."""
    from datetime import timedelta
    return (t - timedelta(hours=1)).date()
