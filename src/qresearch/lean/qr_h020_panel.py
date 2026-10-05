# qr_h020_panel.py — H020 real-run plumbing (research/phase5/H020_spec.md v1 + H020_spec_addendum_1.md). Pure numpy, no
# QuantConnect imports (tests/test_h020_panel.py). Used by the X987 / S021 host at the end of a run whose last session is
# 2017-12-29. The chart score itself is qr_chart.snapshot (frozen, hash-pinned); nothing here changes a score rule.
#
# Price sets (one consistent set from RAW bars and QuantConnect's own event feeds, the H019 construction, D148):
#   chart bars  = RAW open / high / low / close x the split feed (split-adjusted, NOT dividend-adjusted); volume = RAW
#                 volume / the same split multiplier (split-adjusted shares);
#   TR closes / opens = RAW x the split feed x the dividend feed: total-shareholder-return prices (cash dividends
#                 reinvested at QuantConnect's reference price, splits, every other price-factor event).
# Decisions: the last market session of each ISO week, from the first week-end on or after 2010-01-04. A response window
# must end on or before the last calendar row (2017-12-29).
import hashlib

import numpy as np

import qr_chart as C

FIRST_DECISION_DAY = np.datetime64("2010-01-04").astype(np.int64)
H_PRIMARY, H_DIAG = 20, 65               # sessions: open t+1 -> close t+20 (4 weeks); t+65 (13 weeks)
MOM_SKIP, MOM_LOOK, MOM_STALE = 21, 252, 5   # Baseline A: TR close at t-21 / TR close at t-252 - 1 (H019 stale rule)
EXCLUSIONS = ("no_bar_at_t", "history_lt_504", "bad_bar_at_t", "snapshot_error", "mom_undefined", "no_response")


# ----------------------------------------------------------------------------------------------- calendar
def iso_week_ids(cal_days):
    """Session day numbers -> ISO year * 100 + ISO week (the qr_chart week_id convention)."""
    d = np.asarray(cal_days, np.int64).astype("datetime64[D]")
    out = np.empty(d.size, np.int64)
    for i, x in enumerate(d):
        y, w, _ = x.astype(object).isocalendar()
        out[i] = y * 100 + w
    return out


def week_end_rows(cal_days):
    """Rows of the last market session of each ISO week (the final row counts as a week end)."""
    wk = iso_week_ids(cal_days)
    return np.r_[np.flatnonzero(wk[1:] != wk[:-1]), wk.size - 1]


def decision_rows(cal_days, h, first_day=FIRST_DECISION_DAY):
    """Week-end rows on or after first_day whose h-session response window ends on or before the last row."""
    cal = np.asarray(cal_days, np.int64)
    we = week_end_rows(cal)
    return we[(cal[we] >= first_day) & (we + h <= cal.size - 1)]


# ----------------------------------------------------------------------------------------------- one stock
def clean_rows(o, h, l, c):
    """Rows where the split-adjusted bar is usable: O, H, L, C finite and > 0."""
    ok = np.ones(np.asarray(c).size, bool)
    for a in (o, h, l, c):
        a = np.asarray(a, float)
        ok &= np.isfinite(a) & (a > 0)
    return np.flatnonzero(ok)


def last_valid(rows, r, stale=None):
    i = int(np.searchsorted(rows, r, side="right")) - 1
    if i < 0 or (stale is not None and r - rows[i] > stale):
        return -1
    return i


def momentum(trc, rows, t):
    """12-1 momentum at decision row t: TR close at row t-21 / TR close at row t-252 - 1, each the stock's last valid
    close at or before that row within MOM_STALE sessions (H019 S1 convention); NaN if undefined."""
    a, b = last_valid(rows, t - MOM_SKIP, MOM_STALE), last_valid(rows, t - MOM_LOOK, MOM_STALE)
    if a < 0 or b < 0 or a <= b:
        return float("nan")
    return float(trc[rows[a]] / trc[rows[b]] - 1.0)


def response(trc, tro, rows, t, h):
    """Total-shareholder return from the OPEN of row t+1 to the close of row t+h. The stock must have a bar at t+1 (else
    NaN: excluded). A stock delisted or without a bar at t+h is valued at its last real close inside the window."""
    i = int(np.searchsorted(rows, t + 1))
    if i >= rows.size or rows[i] != t + 1:
        return float("nan")
    e = last_valid(rows, t + h)
    o = tro[t + 1]
    if not (np.isfinite(o) and o > 0):
        return float("nan")
    return float(trc[rows[e]] / o - 1.0)


def response_slow(raw_c, raw_o, splits, divs, t, h, rows):
    """Independent recomputation of response() from RAW prices and the event lists (no multiplier arrays): price ratio x
    1 / prod(split factors of events inside the window) x 1 / prod(1 - distribution / reference) of dividends inside.
    splits = [(first row on/after the event, factor)], divs = [(row, amount, reference)]. An event at row b affects the
    window iff t+1 < b <= end row."""
    i = int(np.searchsorted(rows, t + 1))
    if i >= rows.size or rows[i] != t + 1:
        return float("nan")
    e = rows[last_valid(rows, t + h)]
    g = raw_c[e] / raw_o[t + 1]
    for b, f in splits:
        if t + 1 < b <= e:
            g /= f
    for b, amt, ref in divs:
        if t + 1 < b <= e and ref > 0 and 0 < amt < ref:
            g /= 1.0 - amt / ref
    return float(g - 1.0)


def stock_snapshot(o, h, l, c, v, wk_cal, rows, t):
    """qr_chart snapshot of one stock at decision row t from its own usable bars up to t (the last HIST_SESSIONS of
    them: the snapshot reads no more). Returns (snapshot, own bars up to t) or (None, n) if no bar at t / < 504 bars."""
    i = int(np.searchsorted(rows, t))
    if i >= rows.size or rows[i] != t:
        return None, -1
    n = i + 1
    if n < C.MIN_SESSIONS:
        return None, n
    sel = rows[max(0, n - C.HIST_SESSIONS):n]
    vv = np.nan_to_num(np.asarray(v, float)[sel], nan=0.0)
    return C.snapshot(o[sel], h[sel], l[sel], c[sel], vv, wk_cal[sel]), n


def cond_bits(snap):
    b = 0
    for i, k in enumerate(C.CONDITIONS):
        if snap["conditions"][k]:
            b |= 1 << i
    return b


def dq_bits(snap):
    b = 0
    for i, k in enumerate(C.DISQUALIFIERS):
        if snap["disqualifiers"][k]:
            b |= 1 << i
    return b


def unpack(bits, n):
    """int array of bit masks -> (len, n) bool array."""
    bits = np.asarray(bits, np.int64)
    return ((bits[:, None] >> np.arange(n)) & 1).astype(bool)


SCALE_FREE = ("conditions", "disqualifiers", "score", "disqualified", "weekly_state", "daily_state", "atr_pct",
              "atr_ratio", "vol_ratio", "risk", "distribution_days", "categories")


def scale_free(snap):
    """The facts of a snapshot that do not depend on the price or volume scale (what a later split factor cannot move):
    used to compare the panel snapshot with an independent point-in-time recomputation."""
    out = {k: snap[k] for k in SCALE_FREE}
    bs, bo = snap["base"], snap["breakout"]
    out["base"] = None if bs is None else {k: bs[k] for k in ("length", "valid", "depth", "pullbacks", "contracting")}
    out["breakout"] = None if bo is None else {k: bo[k] for k in ("age", "ext", "clv", "relvol")}
    return out


def compare_scale_free(a, b, rtol=1e-9):
    """(exact facts identical, max relative float difference) of two scale_free() dicts."""
    exact = True
    worst = 0.0

    def walk(x, y):
        nonlocal exact, worst
        if isinstance(x, dict):
            if not isinstance(y, dict) or set(x) != set(y):
                exact = False
                return
            for k in x:
                walk(x[k], y[k])
        elif isinstance(x, (list, tuple)):
            if not isinstance(y, (list, tuple)) or len(x) != len(y):
                exact = False
                return
            for p, q in zip(x, y):
                walk(p, q)
        elif isinstance(x, (bool, np.bool_, str)) or x is None or isinstance(x, (int, np.integer)):
            if x != y:
                exact = False
        else:
            x, y = float(x), float(y)
            if np.isfinite(x) or np.isfinite(y):
                d = abs(x - y) / max(abs(x), abs(y), 1e-300)
                worst = max(worst, d)
    walk(a, b)
    return exact, worst


# ----------------------------------------------------------------------------------------------- score table
class ScoreTable:
    """Per decision k (primary or 13-week): the eligible cross-section with the chart side and the baselines.
    rec[k] = dict(ids (int column indices, sorted), Q, G, bits, dq, cat (n x 4), trend, mom, y, y13, sector, mcap)."""

    def __init__(self, cal, rows_dec, elig, mcap, sector, O, H, L, Cl, V, TRC, TRO, progress=None):
        self.cal = np.asarray(cal, np.int64)
        D, N = Cl.shape
        self.rows = np.asarray(rows_dec)
        K = self.rows.size
        self.wk = iso_week_ids(self.cal)
        self.excl = {e: np.zeros(K, np.int64) for e in EXCLUSIONS}
        self.eligible = np.zeros(K, np.int64)
        Qa = np.full((K, N), -9, np.int8)
        Ga = np.full((K, N), -9, np.int8)
        Ba = np.zeros((K, N), np.int32)
        Da = np.zeros((K, N), np.int8)
        CAT = np.zeros((K, N, 4), np.int8)
        TR = np.zeros((K, N), bool)
        MOM = np.full((K, N), np.nan)
        Y = np.full((K, N), np.nan)
        Y13 = np.full((K, N), np.nan)
        NB = np.zeros((K, N), np.int32)
        for k in range(K):
            self.eligible[k] = int(elig[k].sum())
        for j in range(N):
            ks = np.flatnonzero(elig[:, j])
            if ks.size == 0:
                continue
            rows = clean_rows(O[:, j], H[:, j], L[:, j], Cl[:, j])
            trows = np.flatnonzero(np.isfinite(TRC[:, j]) & (TRC[:, j] > 0))
            for k in ks:
                t = int(self.rows[k])
                if not (np.isfinite(Cl[t, j]) and Cl[t, j] > 0):
                    self.excl["no_bar_at_t"][k] += 1
                    continue
                try:
                    snap, n = stock_snapshot(O[:, j], H[:, j], L[:, j], Cl[:, j], V[:, j], self.wk, rows, t)
                except Exception:
                    self.excl["snapshot_error"][k] += 1
                    continue
                if snap is None:
                    self.excl["bad_bar_at_t" if n == -1 else "history_lt_504"][k] += 1
                    continue
                NB[k, j] = n
                Qa[k, j] = C.quality_level(snap)
                Ga[k, j] = C.score_group(snap)
                Ba[k, j] = cond_bits(snap)
                Da[k, j] = dq_bits(snap)
                CAT[k, j] = [snap["categories"][x] for x in "WBTR"]
                TR[k, j] = bool(Cl[t, j] > snap["ma"]["ma40w"])
                MOM[k, j] = momentum(TRC[:, j], trows, t)
                Y[k, j] = response(TRC[:, j], TRO[:, j], trows, t, H_PRIMARY)
                if t + H_DIAG <= D - 1:
                    Y13[k, j] = response(TRC[:, j], TRO[:, j], trows, t, H_DIAG)
            if progress is not None:
                progress(j, N)
        self.Q, self.G, self.bits, self.dq, self.cat = Qa, Ga, Ba, Da, CAT
        self.trend, self.mom, self.y, self.y13, self.nbars = TR, MOM, Y, Y13, NB
        self.scored = Qa != -9
        for k in range(K):
            self.excl["mom_undefined"][k] = int((self.scored[k] & ~np.isfinite(MOM[k])).sum())
            self.excl["no_response"][k] = int((self.scored[k] & np.isfinite(MOM[k]) & ~np.isfinite(Y[k])).sum())
        self.mcap = mcap
        self.sector = sector

    def dates(self, horizon="y", max_row=None):
        """Chronological decision dicts for qr_h020_stats.prepare: the scored stocks with momentum defined (and, for
        the horizon, a response; prepare() drops NaN responses). max_row limits decisions (13-week window)."""
        out = []
        for k, t in enumerate(self.rows):
            if max_row is not None and t > max_row:
                continue
            j = np.flatnonzero(self.scored[k] & np.isfinite(self.mom[k]))
            d = np.datetime64(int(self.cal[t]), "D")
            out.append(dict(k=k, row=int(t), day=str(d), year=int(str(d)[:4]), ids=j,
                            Q=self.Q[k, j].astype(int), G=self.G[k, j].astype(int), mom=self.mom[k, j],
                            trend=self.trend[k, j], y=self.y[k, j], y13=self.y13[k, j]))
        return out

    def chart_digest(self):
        """SHA-256 of the chart side (ids, Q, G, condition / disqualifier bits, trend): dividend-independent."""
        hh = hashlib.sha256()
        hh.update(self.rows.astype(np.int64).tobytes())
        for a in (self.scored, self.Q, self.G, self.bits, self.dq, self.trend):
            hh.update(np.ascontiguousarray(a).tobytes())
        return hh.hexdigest()

    def response_digest(self):
        """SHA-256 of the baseline / response side (momentum, 4- and 13-week total returns): depends on dividends."""
        hh = hashlib.sha256()
        for a in (self.mom, self.y, self.y13):
            hh.update(np.ascontiguousarray(np.where(np.isfinite(a), a, -9e9)).tobytes())
        return hh.hexdigest()
