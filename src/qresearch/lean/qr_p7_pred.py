# qr_p7_pred.py — Phase 7 predictive validation of the FROZEN Conviction Score v1 (H022; research/phase7/
# P7_predictive_spec.md; owner D175). Pure numpy; reuses qr_xs (ranks, Newey-West, critical values) and the H020
# identity-tethered null (qr_h020_stats.ChartTether, one stratum, no self-matching). FROZEN CANDIDATE, constants pinned by
# qresearch.p7pred. In P7-CP4 it is exercised ONLY on synthetic data (tests/test_p7_pred.py, research/phase7/
# P7_power.py): no real future return is computed anywhere.
#
# Question: do eligible stocks with a higher frozen Score v1 at a monthly review earn a higher subsequent total
# shareholder return than lower-scoring eligible stocks?
# One decision date = the month-end review session t (2011-01-31 .. 2017-11-30, 83 dates). Population = the stocks that
# are eligible and fully scorable at t (data-v1 universe, kept share class, no hard disqualifier H1-H7) -- exactly the
# population the frozen planner ranks. Per stock: S = total score (0..100), the stock's PIT FF12 sector, 12-1 momentum and
# log market cap (incremental diagnostic), and the response.
# Response (primary): total shareholder return from the OPEN of the first session after t to the CLOSE of the next
# review session t' (one month), from RAW prices x QuantConnect's split and dividend feeds (response(...)), minus the
# equal-weighted mean of the same responses over the population (cross-sectional demeaning: removes the market and
# isolates stock selection; ranks, hence the IC, are unchanged by it).
import math

import numpy as np

import qr_h020_stats as H
import qr_xs as X

HORIZON_MONTHS = 1                  # primary: next review session close
DIAG_HORIZONS = (2, 3)              # pre-registered diagnostics (overlapping)
NW_LAG = 2                          # monthly, non-overlapping responses (persistent scores -> mild autocorrelation)
ANN = 12.0
ENTRY = 80                          # the frozen portfolio entry threshold (economic group)
ECON_MIN = 0.03                     # 80+ group >= +3%/yr over the population average
MONO_MIN = 0.90                     # Spearman(quintile index, mean demeaned response)
N_Q = 5
BLOCKS = ((2011, 2012), (2013, 2014), (2015, 2016), (2017, 2017))
BLOCK_MAX_SHARE = 0.5
ALPHA = 0.01
CRIT_FLOOR = 2.326                  # c_ic is never below the normal one-sided 1% quantile (guards a too-narrow null)
R_NULL = 5000
MIN_STOCKS = 20
SECTOR_MIN = 5                      # sector-demeaning uses the FF12 group mean when the group has >= 5 stocks
SEEDS = tuple(range(1, R_NULL + 1))  # null world w uses seed w (deterministic; batches of 1,000)
STATUS = ("ok", "truncated", "no_bar_after_t", "unverified_split")


# ----------------------------------------------------------------------------------------------- responses
def response(raw_open, raw_close, mult, t, t_next, unverified_rows=()):
    """Total shareholder return of ONE security for the window (t, t_next] on the session calendar.
    raw_open / raw_close: RAW bars (NaN = no bar); mult: split multiplier x dividend multiplier per row (qr_xs_panel
    construction, factors of events after a row applied to that row), so mult[r] * price[r] is the total-return price.
    Entry: the first row e in (t, t_next] with a valid open and close (never row t: no same-close look-ahead).
    Exit: the close of t_next; if the security has no bar there (delisting, acquisition, halt), the LAST REAL CLOSE in
    [e, t_next] (cash afterwards). No bar at all in (t, t_next]: return 0 (the position could not be opened; status
    'no_bar_after_t'). An unverified split event inside (t, t_next] makes the total-return series unreliable: NaN
    ('unverified_split'; counted, excluded from that date). Returns (value, status)."""
    O, C, m = (np.asarray(a, float) for a in (raw_open, raw_close, mult))
    if any(t < int(e) <= t_next for e in unverified_rows):
        return float("nan"), "unverified_split"
    rows = np.arange(t + 1, t_next + 1)
    ok = np.isfinite(O[rows]) & (O[rows] > 0) & np.isfinite(C[rows]) & (C[rows] > 0)
    if not ok.any():
        return 0.0, "no_bar_after_t"
    e = int(rows[np.argmax(ok)])
    okc = np.isfinite(C[e:t_next + 1]) & (C[e:t_next + 1] > 0)
    x = e + int(np.flatnonzero(okc)[-1])
    val = (C[x] * m[x]) / (O[e] * m[e]) - 1.0
    return float(val), ("ok" if x == t_next else "truncated")


# ----------------------------------------------------------------------------------------------- per date
def rank01(x):
    x = np.asarray(x, float)
    return (X.avg_rank(x) - 0.5) / x.size


def quintile_labels(S):
    """Score quintiles 1..5 of the population by average rank (the frozen qr_p7_score convention:
    q = floor(5 (r - 0.5) / n) + 1)."""
    r = X.avg_rank(np.asarray(S, float))
    n = r.size
    return np.minimum(N_Q, np.floor(N_Q * (r - 0.5) / n).astype(int) + 1)


def sector_demean(y, sector):
    y = np.asarray(y, float)
    out = y - y.mean()
    sec = np.asarray(sector)
    for g in np.unique(sec):
        ix = sec == g
        if ix.sum() >= SECTOR_MIN:
            out[ix] = y[ix] - y[ix].mean()
    return out


def prepare(dates, horizon="y"):
    """dates: chronological dicts with numpy arrays ids (sorted strings), S (int score), sector, mom, size (log market
    cap), the response arrays 'y' (primary) / 'y2' / 'y3' (diagnostics), and scalars year, regime. Everything that does
    not depend on the null world is computed once. Rows with a non-finite response are dropped (only 'unverified_split'
    produces NaN); a date with fewer than MIN_STOCKS rows is skipped."""
    out = []
    for d in dates:
        y = np.asarray(d[horizon], float)
        ok = np.isfinite(y)
        if ok.sum() < MIN_STOCKS:
            continue
        S = np.asarray(d["S"], float)[ok]
        yd = y[ok] - float(y[ok].mean())
        ys = sector_demean(y[ok], np.asarray(d["sector"])[ok])
        out.append(dict(ids=np.asarray(d["ids"])[ok].tolist(), S=S, rq=X.avg_rank(S), Q=quintile_labels(S),
                        hi=(S >= ENTRY), yd=yd, ry=X.avg_rank(yd), rys=X.avg_rank(ys), rysdm=rank01(ys),
                        rmom=rank01(np.asarray(d["mom"], float)[ok]), rsize=rank01(np.asarray(d["size"], float)[ok]),
                        year=int(d["year"]), regime=d.get("regime")))
    return out


def _pearson(a, b):
    a, b = a - a.mean(), b - b.mean()
    den = math.sqrt(float((a * a).sum() * (b * b).sum()))
    return float((a * b).sum() / den) if den > 0 else 0.0


def date_stats(p, ix=None):
    """Statistics of one prepared date; ix re-indexes the SCORE side (S, its rank, quintile and 80+ flag) for a null
    world. Responses, sector, momentum and size always stay with the stock."""
    rq = p["rq"] if ix is None else p["rq"][ix]
    Q = p["Q"] if ix is None else p["Q"][ix]
    hi = p["hi"] if ix is None else p["hi"][ix]
    yd = p["yd"]
    ic = _pearson(rq, p["ry"])                                  # Spearman (ranks; demeaning does not change them)
    ic_sector = _pearson(rq, p["rys"])                          # sector-demeaned response (diagnostic)
    # secondary incremental-information diagnostic: Fama-MacBeth rank regression of the sector-demeaned response on
    # rank(score), rank(12-1 momentum) and rank(log market cap); the market is removed by demeaning, sectors by the
    # sector demeaning
    b = X.ols_slopes(np.column_stack([(rq - 0.5) / rq.size, p["rmom"], p["rsize"]]), p["rysdm"])
    cnt = np.bincount(Q, minlength=N_Q + 1)[1:]
    sm = np.bincount(Q, weights=yd, minlength=N_Q + 1)[1:]
    qm = [float(sm[k] / cnt[k]) if cnt[k] else float("nan") for k in range(N_Q)]
    return dict(ic=ic, ic_sector=ic_sector, inc=float(b[0]), q=qm, n_hi=int(hi.sum()),
                hi=float(yd[hi].mean()) if hi.any() else float("nan"))


def summarise(series, years, regimes=None, lag=NW_LAG, ann=ANN):
    yrs = np.asarray(years)
    ic = np.array([d["ic"] for d in series])
    m_ic, se_ic, t_ic = X.nw_tstat(ic, lag)
    ics = np.array([d["ic_sector"] for d in series])
    m_s, se_s, t_s = X.nw_tstat(ics, lag)
    inc = np.array([d["inc"] for d in series])
    m_inc, se_inc, t_inc = X.nw_tstat(inc, lag)
    Qm = np.array([d["q"] for d in series], float)
    qmean = [float(np.nanmean(Qm[:, k])) for k in range(N_Q)]
    hi = np.array([d["hi"] for d in series])
    mono = X.spearman(np.arange(1, N_Q + 1, dtype=float), np.array(qmean))
    half = ic.size // 2
    out = dict(n_dates=int(ic.size), ic_mean=m_ic, ic_se=se_ic, t_ic=t_ic,
               ic_sector_mean=m_s, t_ic_sector=t_s, inc_mean=m_inc, t_inc=t_inc,
               q_mean_ann=[x * ann for x in qmean], q5_minus_q1_ann=(qmean[-1] - qmean[0]) * ann,
               hi_ann=float(np.nanmean(hi) * ann) if np.isfinite(hi).any() else float("nan"),
               hi_months=int(np.isfinite(hi).sum()), hi_n_mean=float(np.mean([d["n_hi"] for d in series])),
               mono=mono, halves=[float(ic[:half].mean()), float(ic[half:].mean())],
               block_max=X.block_share_max(ic, yrs, BLOCKS),
               years={int(y): float(ic[yrs == y].mean()) for y in sorted(set(yrs.tolist()))})
    if regimes is not None:
        rg = np.asarray(regimes)
        out["regime_ic"] = {str(r): [float(ic[rg == r].mean()), int((rg == r).sum())]
                            for r in sorted(set(rg.tolist()), key=str)}
    return out


# ----------------------------------------------------------------------------------------------- gates
def promotion(s, c_ic):
    """All four gates are required (intersection): the significance gate is the only studentised one; its critical
    value c_ic is the (1 - ALPHA) quantile of the null t_ic over the full procedure's null worlds."""
    g = dict(
        G1_significant=bool(s["t_ic"] > c_ic and s["ic_mean"] > 0),
        G2_economic=bool(np.isfinite(s["hi_ann"]) and s["hi_ann"] >= ECON_MIN),
        G3_monotonic=bool(np.isfinite(s["mono"]) and s["mono"] >= MONO_MIN and s["q5_minus_q1_ann"] > 0),
        G4_stable=bool(all(h > 0 for h in s["halves"]) and s["block_max"] <= BLOCK_MAX_SHARE),
    )
    g["pass"] = all(g.values())
    return g


def diagnostics_flags(s):
    """Pre-registered, NON-GATING interpretation flags."""
    return dict(sector_driven=bool(s["t_ic"] > 0 and s["t_ic_sector"] < 0.5 * s["t_ic"]),
                no_increment_beyond_momentum_size=bool(s["t_inc"] <= 0))


# ----------------------------------------------------------------------------------------------- null
class Tether(H.ChartTether):
    """The H020 identity-tethered within-date permutation with ONE stratum and no self-matching: every receiving stock
    gets the score side of a partner stock and keeps that partner while both stay in the population, so a receiver's
    null score history is another stock's real score history (distribution per date, persistence, 80+ counts and
    universe changes preserved); returns, sectors, momentum and size stay with the receiver."""

    def step(self, eligible, strata=None):
        return super().step(eligible, [0] * len(eligible))


def run_world(prep, seed=None, lag=NW_LAG, ann=ANN, keep_series=False):
    """The complete evaluation for one world: seed None = the real assignment; otherwise the tethered null. Every
    statistic and gate input is recomputed in each world (full-procedure null)."""
    T = Tether(seed) if seed is not None else None
    series, years, regimes = [], [], []
    for p in prep:
        ix = None
        if T is not None:
            pos = {s: i for i, s in enumerate(p["ids"])}
            ix = np.array([pos[s] for s in T.step(p["ids"])])
        series.append(date_stats(p, ix))
        years.append(p["year"])
        regimes.append(p["regime"])
    out = summarise(series, years, regimes, lag, ann)
    if keep_series:
        out["_series"] = series
    return out


def critical_value(null_worlds, alpha=ALPHA):
    """c_ic = max(the k-th largest null t_ic, k = ceil(alpha x R) (R = 5,000 -> the 50th largest), CRIT_FLOOR)."""
    return max(X.critical_value([w["t_ic"] for w in null_worlds], alpha), CRIT_FLOOR)


def false_promotion(null_worlds, c_ic):
    """Share of null worlds passing ALL gates with the frozen c_ic (the procedure's false-promotion rate)."""
    return float(np.mean([promotion(w, c_ic)["pass"] for w in null_worlds])) if null_worlds else float("nan")
