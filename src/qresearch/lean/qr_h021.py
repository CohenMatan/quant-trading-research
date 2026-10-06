# qr_h021.py — H021-A sector relative-momentum falsification test (research/phase6/H021A_spec.md). Pure numpy, no
# QuantConnect imports (tests/test_h021.py). The X989 / S022 host builds the total-return panel of the nine Select
# Sector SPDRs from RAW bars x QuantConnect's split and dividend feeds (qr_xs_panel, the H019 construction) and calls
# only this module. FROZEN with the spec (hash-pinned by qresearch.p6h021).
#
# Notation (rows = market sessions, columns = the 9 ETFs in UNIVERSE order):
#   P[r, i] = total-return close, O[r, i] = total-return open (RAW x split factors x dividend factors, every factor known
#             by 2017-12-31; every quantity below is a RATIO of one ETF's prices inside a window that ends on or before
#             the time it is used, so a factor dated after the window multiplies both ends equally: point-in-time).
#   me[k]   = row of the last session of calendar month k.
# Decision at month-end k (row d = me[k]):
#   signal   S[k, i] = P[me[k], i] / P[me[k-6], i] - 1          (trailing 6-month total return, no skip month)
#   response F_h[k, i] = P[me[k+h], i] / O[me[k]+1, i] - 1       (total return from the NEXT session's open to the
#                                                                 close of the h-th following month-end)
#            Y_h[k, i] = F_h[k, i] - mean_i F_h[k, i]             (sector-relative; h = 1 primary, 3 / 6 diagnostics)
import hashlib
import math

import numpy as np

UNIVERSE = ("XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY")
LOOKBACK = 6                       # months (pre-registered; no other lookback)
TOP_K = 3
FIRST_DECISION = (2000, 1)
LAST_DECISION = (2017, 11)
ECON_MIN = 0.03                    # P2: top-3 vs sector average >= +3.0%/yr
BLOCKS = ((2000, 2005), (2006, 2011), (2012, 2017))
BLOCK_MAX_SHARE = 0.5
ALPHA = 0.01
R_NULL = 5000
DIAG_HORIZONS = (3, 6)
DIAG_PERIODS = (((2010, 1), (2017, 11)), ((2005, 1), (2017, 11)))


# ----------------------------------------------------------------------------------------------- calendar
def month_end_rows(cal_days):
    """Sorted session day numbers -> (months [(y, m)], row of the last session of each month)."""
    d = np.asarray(cal_days, np.int64).astype("datetime64[D]")
    ym = d.astype("datetime64[M]")
    last = np.r_[np.flatnonzero(ym[1:] != ym[:-1]), d.size - 1]
    months = [(int(str(ym[r])[:4]), int(str(ym[r])[5:7])) for r in last]
    return months, np.asarray(last)


def decision_index(months, first=FIRST_DECISION, last=LAST_DECISION):
    """Indices k of the decision months first .. last (inclusive)."""
    return np.array([k for k, m in enumerate(months) if first <= m <= last], dtype=int)


# ----------------------------------------------------------------------------------------------- panel quantities
# Missing bars (spec section 4): a session on which an ETF has no bar carries its last total-return close forward (no
# trade = no price change); the entry open of a response is the open of the ETF's first bar AFTER the decision row.
def ffill(P):
    """Forward-fill each column over rows without a valid (finite, > 0) value."""
    P = np.array(P, float)
    for i in range(P.shape[1]):
        last = np.nan
        col = P[:, i]
        for r in range(col.size):
            if np.isfinite(col[r]) and col[r] > 0:
                last = col[r]
            else:
                col[r] = last
    return P


def entry_rows(O, me, ks):
    """E[j, i] = first row > me[k] where ETF i has a valid open (-1 if none)."""
    me = np.asarray(me)
    out = np.full((len(ks), O.shape[1]), -1, dtype=np.int64)
    for i in range(O.shape[1]):
        v = np.flatnonzero(np.isfinite(O[:, i]) & (O[:, i] > 0))
        pos = np.searchsorted(v, me[np.asarray(ks)] + 1)
        ok = pos < v.size
        out[ok, i] = v[pos[ok]]
    return out


def signal(P, me, ks, L=LOOKBACK):
    """S[j, i] for decisions ks: Pf[me[k]] / Pf[me[k-L]] - 1 (Pf = forward-filled total-return closes)."""
    me = np.asarray(me)
    ks = np.asarray(ks)
    Pf = ffill(P)
    return Pf[me[ks]] / Pf[me[ks - L]] - 1.0


def forward(P, O, me, ks, h=1):
    """F[j, i] = Pf[me[k+h]] / O[entry] - 1 (raw, not demeaned); entry = the first bar after the decision row."""
    me = np.asarray(me)
    ks = np.asarray(ks)
    Pf = ffill(P)
    E = entry_rows(O, me, ks)
    if (E < 0).any() or (E > me[ks + h][:, None]).any():
        raise ValueError("H021: no entry bar inside a response window")
    return Pf[me[ks + h]] / O[E, np.arange(O.shape[1])[None, :]] - 1.0


def relative(F):
    return F - F.mean(axis=1, keepdims=True)


# ----------------------------------------------------------------------------------------------- statistics
def avg_rank(x):
    o = np.argsort(x, kind="mergesort")
    xs = x[o]
    r = np.empty(x.size)
    i = 0
    while i < x.size:
        j = i
        while j + 1 < x.size and xs[j + 1] == xs[i]:
            j += 1
        r[o[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def spearman_rows(A, B):
    ra = np.apply_along_axis(avg_rank, 1, A)
    rb = np.apply_along_axis(avg_rank, 1, B)
    ra = ra - ra.mean(axis=1, keepdims=True)
    rb = rb - rb.mean(axis=1, keepdims=True)
    den = np.sqrt((ra * ra).sum(axis=1) * (rb * rb).sum(axis=1))
    return np.where(den > 0, (ra * rb).sum(axis=1) / np.where(den > 0, den, 1.0), 0.0)


def nw_t(x, lag):
    """Mean, Newey-West (Bartlett) standard error, t. lag 0 = non-overlapping responses."""
    x = np.asarray(x, float)
    T = x.size
    e = x - x.mean()
    v = float(e @ e) / T
    for l in range(1, min(lag, T - 1) + 1):
        v += 2.0 * (1.0 - l / (lag + 1.0)) * float(e[l:] @ e[:-l]) / T
    se = math.sqrt(max(v, 0.0) / T)
    return float(x.mean()), se, (float(x.mean()) / se if se > 0 else 0.0)


def evaluate(S, Y, years, h=1, k=TOP_K):
    """The complete H021-A evaluation of one world. S, Y: (T, 9); years: decision years (T,)."""
    years = np.asarray(years)
    ic = spearman_rows(S, Y)
    m_ic, se_ic, t_ic = nw_t(ic, h - 1)
    order = np.argsort(-S, axis=1, kind="mergesort")           # highest signal first
    top = np.take_along_axis(Y, order[:, :k], 1).mean(axis=1)
    mid = np.take_along_axis(Y, order[:, k:2 * k], 1).mean(axis=1)
    bot = np.take_along_axis(Y, order[:, 2 * k:3 * k], 1).mean(axis=1)
    ann = 12.0 / h
    half = ic.size // 2
    tot = float(ic.sum())
    shares = {}
    for a, b in BLOCKS:
        sel = (years >= a) & (years <= b)
        shares[f"{a}-{b}"] = (float(ic[sel].sum()) / tot) if tot > 0 else math.inf
    out = dict(dates=int(ic.size), ic_mean=m_ic, ic_se=se_ic, t_ic=t_ic,
               top_ann=float(top.mean()) * ann, mid_ann=float(mid.mean()) * ann, bot_ann=float(bot.mean()) * ann,
               top_minus_bottom_ann=float((top - bot).mean()) * ann,
               halves=[float(ic[:half].mean()), float(ic[half:].mean())],
               block_ic_sum={f"{a}-{b}": float(ic[(years >= a) & (years <= b)].sum()) for a, b in BLOCKS},
               block_share=shares, ic_sum=tot)
    return out, ic


def gates(s, c):
    """Frozen gates P1-P4 (all required)."""
    g = dict(
        P1_statistical=bool(s["t_ic"] > c),
        P2_economic=bool(s["top_ann"] >= ECON_MIN),
        P3_monotonic=bool(s["top_ann"] > s["mid_ann"] > s["bot_ann"]),
        P4_stable=bool(all(x > 0 for x in s["halves"]) and s["ic_sum"] > 0 and
                       max(s["block_share"].values()) <= BLOCK_MAX_SHARE),
    )
    g["qualified"] = all(g.values())
    return g


# ----------------------------------------------------------------------------------------------- null
def derangement(seed, n=len(UNIVERSE)):
    """Deterministic fixed-point-free permutation for null world `seed` (rejection sampling)."""
    rng = np.random.default_rng(seed)
    while True:
        p = rng.permutation(n)
        if not np.any(p == np.arange(n)):
            return p


def null_world(S, Y, years, seed):
    """Identity-tethered derangement null: sector i receives the ENTIRE signal history of sector p(i); returns and
    dates are untouched. The complete procedure is re-run."""
    p = derangement(seed, S.shape[1])
    return evaluate(S[:, p], Y, years)[0]


def critical_value(null_t, alpha=ALPHA):
    v = np.sort(np.asarray(null_t, float))[::-1]
    k = max(1, int(math.ceil(alpha * v.size)))
    return float(v[k - 1])


# ----------------------------------------------------------------------------------------------- fidelity helpers
def digest(*arrays):
    h = hashlib.sha256()
    for a in arrays:
        h.update(np.ascontiguousarray(np.asarray(a, float)).tobytes())
    return h.hexdigest()


def slow_total_return(raw_c, raw_o, splits, divs, start, end, from_open=False):
    """Independent total return computed day by day from RAW prices and the event lists (no multiplier arrays).
    Window: from the CLOSE of session `start` (or its OPEN if from_open) to the close of session `end`. On each later
    session r with a bar: gross = raw_c[r] / (raw_c[prev] * f_r * d_r), where f_r is the split factor of a split whose
    first row is r and d_r = prod(1 - amount / reference) over the distributions whose ex-row is r (QuantConnect's own
    price-factor convention: factors apply to the rows BEFORE the event). splits = {row: f}; divs = {row: (amount,
    reference)} or {row: [(amount, reference), ...]}. A close window whose start session has no bar starts from the
    ETF's last bar before it (the carried-forward close, spec section 4)."""
    def ok(x):
        return np.isfinite(x) and x > 0
    if from_open:
        if not (ok(raw_o[start]) and ok(raw_c[start])):
            raise ValueError("slow_total_return: no bar at the entry session")
        g = raw_c[start] / raw_o[start]
    else:
        while start > 0 and not ok(raw_c[start]):
            start -= 1
        g = 1.0
    prev = raw_c[start]
    acc_f, acc_d = 1.0, 1.0                 # factors of events on sessions without a bar carry to the next bar
    for r in range(start + 1, end + 1):
        acc_f *= splits.get(r, 1.0)
        items = divs.get(r, [])
        for amt, ref in ([items] if isinstance(items, tuple) else items):
            if ref > 0 and 0 < amt < ref:
                acc_d *= 1.0 - amt / ref
        if not ok(raw_c[r]):
            continue
        g *= raw_c[r] / (prev * acc_f * acc_d)
        prev = raw_c[r]
        acc_f, acc_d = 1.0, 1.0
    return g - 1.0


def step_consistency(P, A):
    """Max |e[r] / e[prev] - 1| over consecutive rows where both series have a valid value, e = P / A. Zero when P and
    an independently adjusted series A (QuantConnect's ADJUSTED mode) differ only by a constant: the same total-return
    steps. Returns (max deviation, row of the max, valid rows)."""
    P, A = np.asarray(P, float), np.asarray(A, float)
    v = np.flatnonzero(np.isfinite(P) & np.isfinite(A) & (P > 0) & (A > 0))
    if v.size < 2:
        return 0.0, -1, int(v.size)
    e = P[v] / A[v]
    d = np.abs(e[1:] / e[:-1] - 1.0)
    i = int(np.argmax(d))
    return float(d[i]), int(v[i + 1]), int(v.size)
