# qr_p7_score.py — Phase 7 Multi-Factor Conviction Score v1 (P7-CP2 pre-registration, research/phase7/P7_score_spec.md;
# owner D169). Pure python / numpy, no QuantConnect imports (tests/test_p7_score.py). DESIGN ONLY in P7-CP2: these
# functions are exercised on synthetic / mock companies; no historical score, return or threshold is computed here.
#
# Price series (owner rule 7; every feature states its series):
#   C  split-adjusted close  -> moving averages, trend state, SMA200 slope, sector / market breadth, SPY trend
#   P  total-return close    -> momentum (12-1), return volatility (60-day)
#   RAW prices               -> execution only (the harness), never in a feature
# All windows are BAR-based on the security's own valid bars inside its current security life (qr_p7.LIFE_GAP, D167).
#
# Thresholds the owner has NOT yet fixed (entry, exit, replacement buffer, maximum positions, regime exposure
# ceilings) are PARAMETERS of the planner below, never constants: they will be chosen by the P7-CP3 availability /
# mechanics studies, which may not use returns.
import math

import numpy as np

import qr_p7 as P7

# ----------------------------------------------------------------------------------------------- frozen constants
SMA_SHORT = 50                  # bars, split-adjusted closes
SMA_LONG = 200                  # bars, split-adjusted closes
SLOPE_LAG = 21                  # bars: SMA200 rising = SMA200(t) > SMA200(t - 21 bars)
MOM_LOOKBACK = 252              # bars, total-return closes (12-1 momentum: P[b-21] / P[b-252] - 1)
MOM_SKIP = 21
VOL_WINDOW = 60                 # daily total-return log returns
TREND_WINDOW = SMA_LONG + SLOPE_LAG              # 221 split-adjusted bars used by the trend features
TR_WINDOW = MOM_LOOKBACK + 1                     # 253 total-return bars used by momentum (volatility uses 61)
MIN_HISTORY = max(TREND_WINDOW, TR_WINDOW)       # 253 bars in the current life (hard disqualifier H3)
STALE_PRICE_SESSIONS = P7.MAX_LAST_BAR_AGE       # 5 (hard disqualifier H5)
LARGE_DISTRIBUTION = 0.10       # a distribution >= 10% of the reference price contaminates split-adjusted windows
YOY_MONTHS = 12                 # revenue growth baseline: the True TTM recorded at the review 12 months earlier
N_BANDS = 5                     # quintiles
BAND_FRACTION = (0.0, 0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0)      # quintile 1 (worst) .. 5 (best)
MIN_SECTOR_GROUP = 10           # fewer scorable / valid members in an FF12 group -> no within-sector information
SECTOR_BREADTH_BAND = 0.10      # sector breadth minus market breadth: >= +0.10 supportive, <= -0.10 weak
REGIME_BREADTH_HIGH = 0.60      # market breadth (share of eligible stocks above their SMA200)
REGIME_BREADTH_LOW = 0.40

POINTS = dict(trend=15, momentum=15, risk=10,                                  # Technical Quality 40
              profitability=15, cash_conversion=10, balance_sheet=10, growth=10,  # Fundamental Quality 45
              sector=15)                                                       # Sector Context 15
CATEGORIES = dict(technical=("trend", "momentum", "risk"),
                  fundamental=("profitability", "cash_conversion", "balance_sheet", "growth"),
                  sector=("sector",))
TREND_FRACTION = dict(strong=1.0, moderate=0.5, weak=0.0)
SECTOR_FRACTION = dict(supportive=1.0, neutral=0.5, weak=0.0)
# ranking scope of each percentile feature (owner rule 17): 'sector' = within the FF12 group of the scorable set
# (cross-sectional if the group has < MIN_SECTOR_GROUP members), 'market' = across the whole scorable set
RANK_SCOPE = dict(momentum="market", risk="market", profitability="sector", cash_conversion="market",
                  balance_sheet="sector", growth="market")
HIGHER_IS_BETTER = dict(momentum=True, risk=False, profitability=True, cash_conversion=True, balance_sheet=True,
                        growth=True)
HARD_DQ = ("H1_sector_not_scorable", "H2_fundamentals_missing_or_stale", "H3_insufficient_history",
           "H4_corporate_event_contamination", "H5_stale_price", "H6_broken_long_term_trend",
           "H7_financial_impairment")
DATA_DQ = HARD_DQ[:5]           # define the ranking population (data-scorable set)
ECONOMIC_DQ = HARD_DQ[5:]       # make a stock ineligible after ranking
REGIMES = ("STRONG", "NORMAL", "WEAK", "RISK_OFF")


def pts(maximum, fraction):
    """Integer points: round half up (no false precision)."""
    return int(math.floor(maximum * fraction + 0.5))


# ----------------------------------------------------------------------------------------------- technical inputs
def _sma(c, b, n):
    return float(np.mean(c[b - n + 1:b + 1]))


def technical_inputs(C, P, t, gap=P7.LIFE_GAP):
    """Technical inputs of ONE security at session row t from its own valid bars (C split-adjusted close, P total-
    return close; rows with either missing are skipped) inside its current life. Returns a dict; values the history
    cannot support are None. Also returns the bar index helpers used by the contamination check."""
    C, P = np.asarray(C, float), np.asarray(P, float)
    v = P7.valid_rows(C, P)
    out = dict(bars=0, age=None, close=None, sma50=None, sma200=None, sma200_lag=None, mom_12_1=None, vol60=None,
               trend_state=None, broken_trend=None, _v=v, _b=-1, _s=0)
    b = int(np.searchsorted(v, t, side="right")) - 1
    if b < 0:
        return out
    ls = P7.life_starts(v, gap)
    s = int(ls[b])
    n = b - s + 1
    c, p = C[v], P[v]
    out.update(bars=n, age=int(t - v[b]), close=float(c[b]), _b=b, _s=s)
    if n >= SMA_SHORT:
        out["sma50"] = _sma(c, b, SMA_SHORT)
    if n >= TREND_WINDOW:
        out["sma200"] = _sma(c, b, SMA_LONG)
        out["sma200_lag"] = _sma(c, b - SLOPE_LAG, SMA_LONG)
        rising = out["sma200"] > out["sma200_lag"]
        falling = out["sma200"] < out["sma200_lag"]
        if out["close"] > out["sma50"] > out["sma200"] and rising:
            out["trend_state"] = "strong"
        elif out["close"] > out["sma200"] and rising:
            out["trend_state"] = "moderate"
        else:
            out["trend_state"] = "weak"
        out["broken_trend"] = bool(out["close"] < out["sma200"] and falling)
    if n >= TR_WINDOW:
        out["mom_12_1"] = float(p[b - MOM_SKIP] / p[b - MOM_LOOKBACK] - 1.0)
    if n >= VOL_WINDOW + 1:
        lr = np.log(p[b - VOL_WINDOW + 1:b + 1] / p[b - VOL_WINDOW:b])
        out["vol60"] = float(lr.std())
    return out


def contamination(ti, unverified_split_rows=(), distributions=()):
    """Corporate-event protection (owner rule 5). ti = technical_inputs(...). unverified_split_rows: calendar rows of
    split events that QuantConnect's own SCALED_RAW does not confirm; distributions: [(ex-row, amount / reference)].
    An event at row e contaminates a feature whose window spans bars [b-L+1, b] if v[b-L+1] < e <= v[b] (the price
    step at e lies inside the window). Unverified splits corrupt BOTH series (split factors enter C and P) -> every
    feature (longest window TR_WINDOW = 253 bars); a large distribution (>= LARGE_DISTRIBUTION) is not adjusted in
    the split-adjusted chart -> the trend features (TREND_WINDOW = 221 bars). Duration is therefore mechanical: the
    stock stays excluded until the event is no longer inside the affected window. Returns (contaminated, reasons,
    bars until clean)."""
    v, b = ti["_v"], ti["_b"]
    if b < 0:
        return False, [], 0
    reasons, clear = [], 0

    def check(e, L, why):
        nonlocal clear
        lo = max(b - L + 1, 0)
        if v[lo] < e <= v[b]:
            reasons.append(why)
            k = int(np.searchsorted(v, e))            # first bar at or after the event
            clear = max(clear, L - 1 - (b - k))       # bars until the window starts at or after the event bar
    for e in unverified_split_rows:
        check(int(e), TR_WINDOW, "unverified split")
    for e, frac in distributions:
        if frac >= LARGE_DISTRIBUTION:
            check(int(e), TREND_WINDOW, "large distribution")
    return bool(reasons), reasons, int(clear)


# ----------------------------------------------------------------------------------------------- fundamental inputs
def fundamental_inputs(rev, gp, ni, ocf, assets, equity, rev_prev):
    """Derived fundamentals from the seven approved fields (True TTM flows, PIT snapshots). rev_prev = the revenue
    True TTM recorded at the review YOY_MONTHS earlier (as known then). Returns (inputs or None, missing reason)."""
    vals = dict(revenue=rev, gross_profit=gp, net_income=ni, operating_cash_flow=ocf, total_assets=assets,
                equity=equity, revenue_prev=rev_prev)
    miss = [k for k, x in vals.items() if x is None or not math.isfinite(x)]
    if miss:
        return None, "missing: " + ",".join(miss)
    if assets <= 0 or rev <= 0 or rev_prev <= 0:
        return None, "invalid denominator (assets / revenue <= 0)"
    return dict(gpa=gp / assets, cash_conversion=(ocf - ni) / assets, eqa=equity / assets,
                rev_growth=rev / rev_prev - 1.0,
                impaired=bool(equity <= 0 or (ni <= 0 and ocf <= 0))), ""


# ----------------------------------------------------------------------------------------------- normalisation
def quintiles(values):
    """values: {key: float}. Quintile 1..5 by average rank (ties share a rank): q = floor(5 (r - 0.5) / n) + 1."""
    keys = sorted(values)
    x = np.array([values[k] for k in keys], float)
    n = x.size
    if n == 0:
        return {}
    order = np.argsort(x, kind="mergesort")
    r = np.empty(n)
    i = 0
    xs = x[order]
    while i < n:
        j = i
        while j + 1 < n and xs[j + 1] == xs[i]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    q = np.minimum(N_BANDS, np.floor(N_BANDS * (r - 0.5) / n).astype(int) + 1)
    return {k: int(qq) for k, qq in zip(keys, q)}


def scoped_quintiles(values, groups, scope):
    """Quintiles within FF12 groups ('sector') or across the set ('market'); a group with fewer than MIN_SECTOR_GROUP
    members is ranked cross-sectionally."""
    if scope == "market":
        return quintiles(values)
    out = {}
    mk = quintiles(values)
    by = {}
    for k in values:
        by.setdefault(groups[k], []).append(k)
    for g, ks in by.items():
        if len(ks) < MIN_SECTOR_GROUP:
            out.update({k: mk[k] for k in ks})
        else:
            out.update(quintiles({k: values[k] for k in ks}))
    return out


def sector_state(sector_breadth, market_breadth, n_valid):
    """Sector context of a stock: its FF12 group's breadth (share of eligible members above their SMA200) relative to
    the market breadth. Fewer than MIN_SECTOR_GROUP members with a state -> neutral (no information)."""
    if n_valid < MIN_SECTOR_GROUP or sector_breadth is None or market_breadth is None:
        return "neutral"
    d = sector_breadth - market_breadth
    if d >= SECTOR_BREADTH_BAND - 1e-12:
        return "supportive"
    if d <= -SECTOR_BREADTH_BAND + 1e-12:
        return "weak"
    return "neutral"


# ----------------------------------------------------------------------------------------------- the score
def score_date(stocks, sector_context):
    """Score one decision date. stocks: {sid: dict(ff12, sic, tech=technical_inputs, contaminated=bool,
    fund=(inputs, reason))}; sector_context: {ff12: 'supportive' | 'neutral' | 'weak'}.
    Returns {sid: record} with dq (list of hard disqualifiers), points by dimension, category subtotals, total
    (None if not data-scorable), eligible (no hard disqualifier) and an explanation."""
    rec = {}
    for sid, s in stocks.items():
        ti, (fi, why) = s["tech"], s["fund"]
        dq = []
        if s.get("sic") is None or 6000 <= int(s["sic"]) <= 6999:
            dq.append("H1_sector_not_scorable")
        if fi is None:
            dq.append("H2_fundamentals_missing_or_stale")
        if ti["bars"] < MIN_HISTORY or ti["mom_12_1"] is None or ti["vol60"] is None or ti["trend_state"] is None:
            dq.append("H3_insufficient_history")
        if s.get("contaminated"):
            dq.append("H4_corporate_event_contamination")
        if ti["age"] is None or ti["age"] > STALE_PRICE_SESSIONS:
            dq.append("H5_stale_price")
        rec[sid] = dict(dq=dq, why=why, ff12=s.get("ff12"))
    pop = [k for k, r in rec.items() if not r["dq"]]                 # the data-scorable ranking population
    raw = {d: {} for d in RANK_SCOPE}
    for k in pop:
        ti, fi = stocks[k]["tech"], stocks[k]["fund"][0]
        raw["momentum"][k] = ti["mom_12_1"]
        raw["risk"][k] = -ti["vol60"]                                  # lower volatility ranks higher
        raw["profitability"][k] = fi["gpa"]
        raw["cash_conversion"][k] = fi["cash_conversion"]
        raw["balance_sheet"][k] = fi["eqa"]
        raw["growth"][k] = fi["rev_growth"]
    groups = {k: stocks[k].get("ff12") for k in pop}
    qs = {d: scoped_quintiles(raw[d], groups, RANK_SCOPE[d]) for d in raw}
    for k, r in rec.items():
        if r["dq"]:
            r.update(total=None, eligible=False, points=None, subtotals=None)
            continue
        ti, fi = stocks[k]["tech"], stocks[k]["fund"][0]
        p = dict(trend=pts(POINTS["trend"], TREND_FRACTION[ti["trend_state"]]),
                 sector=pts(POINTS["sector"], SECTOR_FRACTION[sector_context.get(stocks[k].get("ff12"), "neutral")]))
        for d in RANK_SCOPE:
            p[d] = pts(POINTS[d], BAND_FRACTION[qs[d][k] - 1])
        sub = {c: sum(p[d] for d in ds) for c, ds in CATEGORIES.items()}
        dq = []
        if ti["broken_trend"]:
            dq.append("H6_broken_long_term_trend")
        if fi["impaired"]:
            dq.append("H7_financial_impairment")
        r.update(points=p, subtotals=sub, total=sum(sub.values()), quintiles={d: qs[d][k] for d in qs},
                 trend_state=ti["trend_state"], dq=dq, eligible=not dq)
    return rec


def explain(r):
    """Human-readable breakdown of one record (owner rule 23)."""
    if r.get("total") is None:
        return "NOT SCORABLE: " + ", ".join(r["dq"]) + (f" ({r['why']})" if r.get("why") else "")
    s = r["subtotals"]
    lines = [f"Technical:   {s['technical']:>3} / 40   (trend {r['trend_state']} {r['points']['trend']}, momentum "
             f"Q{r['quintiles']['momentum']} {r['points']['momentum']}, risk Q{r['quintiles']['risk']} "
             f"{r['points']['risk']})",
             f"Fundamental: {s['fundamental']:>3} / 45   (GP/A Q{r['quintiles']['profitability']} "
             f"{r['points']['profitability']}, cash conversion Q{r['quintiles']['cash_conversion']} "
             f"{r['points']['cash_conversion']}, equity/assets Q{r['quintiles']['balance_sheet']} "
             f"{r['points']['balance_sheet']}, revenue growth Q{r['quintiles']['growth']} {r['points']['growth']})",
             f"Sector:      {s['sector']:>3} / 15",
             f"Total:       {r['total']:>3} / 100" + ("" if r["eligible"] else "   INELIGIBLE: " + ", ".join(r["dq"]))]
    return "\n".join(lines)


# ----------------------------------------------------------------------------------------------- share classes
def select_share_classes(cands):
    """cands: {sid: (company_key, adv20)}. One class per company: the highest point-in-time ADV20; ties -> the
    lexicographically smallest security id. A security without a company key stands alone."""
    best = {}
    for sid, (key, adv) in cands.items():
        k = key if key is not None else ("sid", sid)
        cur = best.get(k)
        if cur is None or (-adv, sid) < (-cur[1], cur[0]):
            best[k] = (sid, adv)
    return {v[0] for v in best.values()}


# ----------------------------------------------------------------------------------------------- market regime
def spy_trend(C_spy, t):
    """SPY trend state from split-adjusted closes: 'up' (close > SMA200 and SMA200 rising), 'down' (close < SMA200 and
    SMA200 falling) or 'mixed'; None without TREND_WINDOW bars."""
    ti = technical_inputs(C_spy, C_spy, t)
    if ti["sma200"] is None:
        return None
    if ti["close"] > ti["sma200"] and ti["sma200"] > ti["sma200_lag"]:
        return "up"
    if ti["close"] < ti["sma200"] and ti["sma200"] < ti["sma200_lag"]:
        return "down"
    return "mixed"


def breadth_level(b):
    if b is None:
        return None
    return "high" if b >= REGIME_BREADTH_HIGH else ("low" if b < REGIME_BREADTH_LOW else "mid")


REGIME_TABLE = {("up", "high"): "STRONG", ("up", "mid"): "NORMAL", ("up", "low"): "WEAK",
                ("mixed", "high"): "NORMAL", ("mixed", "mid"): "WEAK", ("mixed", "low"): "WEAK",
                ("down", "high"): "WEAK", ("down", "mid"): "WEAK", ("down", "low"): "RISK_OFF"}


def regime(trend, breadth):
    """Market regime from two independent market-level inputs: SPY trend and PIT market breadth (share of eligible
    stocks above their own SMA200). It never enters a stock's score; it only caps exposure (planner)."""
    if trend is None or breadth is None:
        return None
    return REGIME_TABLE[(trend, breadth_level(breadth))]


# ----------------------------------------------------------------------------------------------- mechanics (parameters)
def plan_review(holdings, records, adv, entry, exit_, buffer, max_positions, regime_cap_positions,
                frozen=frozenset(), universe=None):
    """One scheduled (monthly) review. holdings: set of held sids; records: score_date output; adv: {sid: ADV20};
    entry / exit_ / buffer / max_positions / regime_cap_positions: NOT frozen (chosen later without returns);
    frozen: holdings under corporate-event contamination (kept, not score-evaluated); universe: eligible set (a
    holding that left it is sold). Returns dict(sell=[...], buy=[...], reasons={sid: why}).
    Rules: (1) sell holdings with an economic / data hard disqualifier (except H4 -> frozen), that left the universe,
    or whose score < exit_; (2) cut to the regime cap: sell the lowest-scoring holdings; (3) buy the best eligible
    candidates with score >= entry into free slots; (4) replace: while no slot is free, the best remaining candidate
    replaces the weakest non-frozen holding only if its score >= that holding's score + buffer. No forced filling."""
    assert exit_ < entry, "hysteresis: the exit threshold must be below the entry threshold"
    sell, reasons = [], {}
    keep = []
    for h in sorted(holdings):
        r = records.get(h)
        if universe is not None and h not in universe:
            sell.append(h)
            reasons[h] = "left the eligible universe"
        elif h in frozen:
            keep.append(h)
            reasons[h] = "frozen (corporate-event contamination)"
        elif r is None or r.get("total") is None:
            sell.append(h)
            reasons[h] = "hard disqualifier: " + ", ".join(r["dq"] if r else ["no data"])
        elif not r["eligible"]:
            sell.append(h)
            reasons[h] = "hard disqualifier: " + ", ".join(r["dq"])
        elif r["total"] < exit_:
            sell.append(h)
            reasons[h] = f"score {r['total']} < exit {exit_}"
        else:
            keep.append(h)

    def sc(h):
        r = records.get(h)
        return r["total"] if r and r.get("total") is not None else float("inf")     # frozen: never the weakest
    cap = min(max_positions, regime_cap_positions)
    while len(keep) > cap:
        w = min((h for h in keep if h not in frozen), key=lambda h: (sc(h), adv.get(h, 0.0), h), default=None)
        if w is None:
            break
        keep.remove(w)
        sell.append(w)
        reasons[w] = "regime exposure cap"
    cands = sorted((k for k, r in records.items() if r.get("eligible") and r["total"] >= entry and k not in holdings),
                   key=lambda k: (-records[k]["total"], -adv.get(k, 0.0), k))
    buy = []
    for k in cands:
        if len(keep) + len(buy) < cap:
            buy.append(k)
            reasons[k] = f"entry (score {records[k]['total']} >= {entry})"
            continue
        pool = [h for h in keep if h not in frozen]
        if not pool:
            break
        w = min(pool, key=lambda h: (sc(h), adv.get(h, 0.0), h))
        if records[k]["total"] >= sc(w) + buffer:
            keep.remove(w)
            sell.append(w)
            reasons[w] = f"replaced by {k} ({records[k]['total']} >= {sc(w)} + {buffer})"
            buy.append(k)
            reasons[k] = f"replacement (score {records[k]['total']})"
        else:
            break                                   # candidates are sorted: no later one can clear the buffer
    return dict(sell=sell, buy=buy, reasons=reasons)


def weekly_check(holdings, records, frozen=frozenset()):
    """Between scheduled reviews: holdings are checked ONLY for hard disqualifiers (no score-based exit, no entry).
    A frozen holding (corporate-event contamination) skips the trend disqualifier H6, which its contaminated window
    cannot measure."""
    out = {}
    for h in sorted(holdings):
        r = records.get(h)
        dq = list(r["dq"]) if r else ["no data"]
        if h in frozen:
            dq = [d for d in dq if d not in ("H4_corporate_event_contamination", "H6_broken_long_term_trend",
                                             "H3_insufficient_history")]
        if dq:
            out[h] = dq
    return out


def tunable_constants():
    """Every judgment constant of the frozen score (owner rule 40); window lengths are listed separately."""
    return dict(windows=dict(SMA_SHORT=SMA_SHORT, SMA_LONG=SMA_LONG, SLOPE_LAG=SLOPE_LAG, MOM_LOOKBACK=MOM_LOOKBACK,
                             MOM_SKIP=MOM_SKIP, VOL_WINDOW=VOL_WINDOW, YOY_MONTHS=YOY_MONTHS),
                judgment=dict(LARGE_DISTRIBUTION=LARGE_DISTRIBUTION, N_BANDS=N_BANDS,
                              MIN_SECTOR_GROUP=MIN_SECTOR_GROUP, SECTOR_BREADTH_BAND=SECTOR_BREADTH_BAND,
                              REGIME_BREADTH_HIGH=REGIME_BREADTH_HIGH, REGIME_BREADTH_LOW=REGIME_BREADTH_LOW,
                              STALE_PRICE_SESSIONS=STALE_PRICE_SESSIONS),
                weights=dict(POINTS), level_tables=dict(BAND_FRACTION=BAND_FRACTION, TREND_FRACTION=TREND_FRACTION,
                                                        SECTOR_FRACTION=SECTOR_FRACTION))
