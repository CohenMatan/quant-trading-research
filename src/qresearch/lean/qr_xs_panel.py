# qr_xs_panel.py — H019 point-in-time daily panel assembly helpers (research/phase4/P4_xs_spec.md section 1).
# Pure numpy, no QuantConnect imports (tests/test_xs_panel.py). Used by the X985 / S020 host at the end of a run whose
# last session is 2017-12-29:
#   tr_close / tr_open  = SCALED_RAW history requested at the end of 2017: total-return (split + dividend + spin-off)
#                         adjusted prices whose adjustment uses only corporate actions up to the end of 2017; a factor
#                         that LEAN dates on a stock's last session for an ex-date after it (first session of 2018, or
#                         after a delisting) is a constant per stock and is divided out;
#   split_close         = |prc| / cfacpr, CRSP-style: the total-return closes with the CASH-dividend factor (dividend
#                         events up to 2017) removed, so splits, spin-offs and other price-factor distributions stay
#                         adjusted and ordinary cash dividends do not (CRSP: a spin-off's price factor is the
#                         distribution value / the ex-date price; cash dividends have no price factor).
#   The split feed (RAW x split events) is kept only as a diagnostic of the price factors (split_multiplier,
#   factor_steps).
# Every signal input and return is a RATIO of prices of one stock inside a window that ends at or before the decision
# (or at the end of the return window), so adjusting with the corporate actions up to 2017-12-31 gives exactly the
# values known at each session: a later factor multiplies both ends of every ratio equally.
import numpy as np

NS_DAY = 86_400 * 10 ** 9
NS_HOUR = 3_600 * 10 ** 9
SPLIT_TOL = 0.03          # |(c_before / c_after) / f - 1| tolerance for a split boundary (c = SCALED_RAW / RAW)
SPLIT_SEARCH = 5          # valid rows searched on each side when the event date does not match the price jump


def _ns(t):
    """datetime64 values of any unit (pandas 2 may use us / s) or int64 ns -> int64 ns since the epoch."""
    t = np.asarray(t)
    if t.dtype.kind == "M":
        return t.astype("datetime64[ns]").astype(np.int64)
    return t.astype(np.int64)


def session_days(t_ns):
    """Daily bar timestamps (datetime64, exchange-local wall clock) -> session day numbers. LEAN stamps a daily bar
    with its END time (midnight after the session); a stamp before 09:00 therefore belongs to the previous day."""
    t = _ns(t_ns)
    day = t // NS_DAY
    hour = (t % NS_DAY) // NS_HOUR
    return day - (hour < 9).astype(np.int64)


def event_days(t_ns):
    """Corporate-action event timestamps -> calendar day numbers (no shift: the event is stamped on its own day)."""
    return _ns(t_ns) // NS_DAY


def month_ends(cal_days):
    """Calendar (sorted session day numbers) -> (months [(y, m)], last-session row of each month)."""
    d = np.asarray(cal_days, np.int64).astype("datetime64[D]")
    ym = d.astype("datetime64[M]")
    last = np.r_[np.flatnonzero(ym[1:] != ym[:-1]), d.size - 1]
    months = []
    for r in last:
        s = str(ym[r])
        months.append((int(s[:4]), int(s[5:7])))
    return months, last.tolist()


def split_multiplier(raw, scaled, events, tol=SPLIT_TOL, search=SPLIT_SEARCH, detail=None):
    """raw / scaled: one stock's RAW and SCALED_RAW closes on the calendar (NaN = no bar). events: [(b, f)] with b =
    the first calendar row on or after the split's event day and f = the LEAN split factor (price multiplier for the
    rows before the split, e.g. 1/7 for 7:1). Each boundary is verified against the jump of c = scaled / raw between
    consecutive valid rows (c_before / c_after = f x any dividend factor); when the event day does not match, the
    boundary is moved to the nearest valid-row pair within +-search rows that matches; otherwise it stays at b and is
    counted as unverified. Returns (multiplier per row, stats)."""
    raw, scaled = np.asarray(raw, float), np.asarray(scaled, float)
    D = raw.size
    valid = np.flatnonzero(np.isfinite(raw) & np.isfinite(scaled) & (raw > 0) & (scaled > 0))
    c = np.full(D, np.nan)
    c[valid] = scaled[valid] / raw[valid]
    mult = np.ones(D)
    st = dict(n=0, aligned=0, realigned=0, unverified=0, outside=0)

    def dev(i, f):
        if 1 <= i < valid.size:
            return abs(c[valid[i - 1]] / c[valid[i]] / f - 1.0)
        return np.inf

    for b, f in sorted(events):
        st["n"] += 1
        i = int(np.searchsorted(valid, b))
        if valid.size == 0 or i == 0 or i == valid.size:
            st["outside"] += 1                       # before the first or after the last bar: no ratio is affected
            mult[:b] *= f
            continue
        best = i
        if dev(i, f) <= tol:
            st["aligned"] += 1
        else:
            cand = [j for j in range(i - search, i + search + 1) if 1 <= j < valid.size]
            j = min(cand, key=lambda x: dev(x, f))
            if dev(j, f) <= tol:
                best = j
                st["realigned"] += 1
            else:
                st["unverified"] += 1
                if detail is not None:      # (event row, factor, c_before / c_after at the event, best row, its ratio)
                    detail.append((int(b), float(f), float(c[valid[i - 1]] / c[valid[i]]), int(valid[j]),
                                   float(c[valid[j - 1]] / c[valid[j]])))
        mult[:valid[best]] *= f
    return mult, st


def residual_jumps(Q, P, lo=0.75, hi=1.02, detail=None):
    """Checks of the split adjustment for one stock: d = P / Q is the dividend-only factor, non-decreasing in time with
    small steps. Counts consecutive valid-row steps d_before / d_after above hi (impossible for dividends: an
    unexplained split or data revision) or below lo (a > 25% distribution or a missed reverse split)."""
    Q, P = np.asarray(Q, float), np.asarray(P, float)
    v = np.flatnonzero(np.isfinite(Q) & np.isfinite(P) & (Q > 0) & (P > 0))
    if v.size < 2:
        return 0, 0
    d = P[v] / Q[v]
    r = d[:-1] / d[1:]
    if detail is not None:              # (row after the step, d_before / d_after, Q_after / Q_before, P_after / P_before)
        for i in np.flatnonzero((r > hi) | (r < lo)):
            detail.append((int(v[i + 1]), float(r[i]), float(Q[v[i + 1]] / Q[v[i]]), float(P[v[i + 1]] / P[v[i]])))
    return int((r > hi).sum()), int((r < lo).sum())


def dividend_multiplier(D, events):
    """Cash-dividend factor per row: events = [(b, distribution, reference price)] with b = the first calendar row on or
    after the ex-dividend day; rows before b are multiplied by (1 - distribution / reference), QuantConnect's own price-
    factor convention (the reference price is the close before the ex-date)."""
    m = np.ones(D)
    for b, amt, ref in events:
        if ref > 0 and 0 < amt < ref:
            m[:b] *= 1.0 - amt / ref
    return m


def cfacpr_close(P, div_mult):
    """CRSP-style |prc| / cfacpr closes from QuantConnect total-return closes: remove the cash-dividend factor, keep the
    split and spin-off (other price-factor distribution) adjustments, as CRSP's cumulative price factor does."""
    return np.asarray(P, float) / np.asarray(div_mult, float)


def factor_steps(q, q_split, small=0.002, big=0.25, detail=None):
    """Steps of e = q / q_split between consecutive valid rows, where q = the cfacpr-style close and q_split = RAW x the
    split events: e moves only at price-factor events that are not in the split history (spin-offs, stock distributions,
    splits missing from the split feed) and at a misaligned cash dividend. Returns (n small steps: small < |log| <=
    log(1 / (1 - big)), n big steps)."""
    q, qs = np.asarray(q, float), np.asarray(q_split, float)
    v = np.flatnonzero(np.isfinite(q) & np.isfinite(qs) & (q > 0) & (qs > 0))
    if v.size < 2:
        return 0, 0
    e = q[v] / qs[v]
    lr = np.abs(np.log(e[:-1] / e[1:]))
    lim = -np.log(1.0 - big)
    sm, bg = (lr > small) & (lr <= lim), lr > lim
    if detail is not None:              # (row after the step, e_before / e_after)
        for i in np.flatnonzero(sm | bg):
            detail.append((int(v[i + 1]), float(e[i] / e[i + 1])))
    return int(sm.sum()), int(bg.sum())
