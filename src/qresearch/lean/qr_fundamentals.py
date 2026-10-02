# qr_fundamentals.py — point-in-time (PIT) fundamentals layer (D108). Uploaded next to the harness; reusable by
# any fundamental hypothesis. No QuantConnect imports: the logic is unit-tested offline (tests/test_pit_fundamentals.py).
#
# Question it answers: what fundamental information was available to the strategy on historical date T?
#   * WHITELIST only (statement totals + point-in-time market cap). Any other field -> FundamentalFieldError (hard
#     failure). Share counts, per-share values, vendor ratios and accession numbers are BLACKLISTED (audit D107).
#   * A report becomes visible on the first decision date strictly AFTER its filing date (the Morningstar object
#     already delivers a filing on the next day; this rule enforces it independently).
#   * Estimated filing dates (file date exactly period end + 45 days, documented vendor approximation) -> visible
#     only from period end + 90 calendar days (owner rule, D108). Annual and quarterly reports are treated alike:
#     +90 covers the latest regular 10-K deadline (non-accelerated filers) and every 10-Q deadline.
#   * Accession anomaly (the report's accession year is after the decision date's year, i.e. the value may come from
#     a later filing): QUARANTINED - never exposed while the anomaly holds; the previous clean report stays in use.
#   * Amendments (same period, later file date) replace the earlier record only from their own visibility date.
#   * Freshness: a record is usable only while (decision date - period end) <= max_age_days (default 200).
#   * Missing values (None / NaN / 0) are returned as None, never filled.
#   * True TTM (D113): '<base>_ttm4q' = sum of the four most recent visible consecutive quarters, gated by a
#     fiscal-year reconciliation; balance-sheet fields are snapshots of the latest visible report.
#   * SEC restatement guard (D111, optional): reports with a value first filed after the vendor date are blocked.
#   * SEC timing holds (D111, optional): for the few vendor reports whose availability would precede every public
#     SEC source (verified against EDGAR), the report is visible only from the day after that SEC date.
import math
from datetime import date, timedelta

APPROX_GAP_DAYS = 45
APPROX_AVAILABLE_AFTER_DAYS = 90
DEFAULT_MAX_AGE_DAYS = 200

IS_ = "financial_statements.income_statement."
BS_ = "financial_statements.balance_sheet."
CF_ = "financial_statements.cash_flow_statement."
# name -> (object path, period). Quarter ("q") and trailing-twelve-month ("ttm") flows; balance-sheet stocks at
# the report's quarter end. Only these may be read.
WHITELIST = {
    "revenue_ttm": (IS_ + "total_revenue", "twelve_months"), "revenue_q": (IS_ + "total_revenue", "three_months"),
    "gross_profit_ttm": (IS_ + "gross_profit", "twelve_months"), "gross_profit_q": (IS_ + "gross_profit", "three_months"),
    "cost_of_revenue_ttm": (IS_ + "cost_of_revenue", "twelve_months"),
    "operating_income_ttm": (IS_ + "operating_income", "twelve_months"),
    "operating_income_q": (IS_ + "operating_income", "three_months"),
    "net_income_ttm": (IS_ + "net_income", "twelve_months"), "net_income_q": (IS_ + "net_income", "three_months"),
    "total_assets": (BS_ + "total_assets", "three_months"),
    "stockholders_equity": (BS_ + "stockholders_equity", "three_months"),
    "total_debt": (BS_ + "total_debt", "three_months"),
    "operating_cash_flow_ttm": (CF_ + "operating_cash_flow", "twelve_months"),
    "operating_cash_flow_q": (CF_ + "operating_cash_flow", "three_months"),
    "free_cash_flow_ttm": (CF_ + "free_cash_flow", "twelve_months"),
    "free_cash_flow_q": (CF_ + "free_cash_flow", "three_months"),
}
# D111: the vendor's '*_ttm' fields on an INTERIM report hold the latest completed FISCAL YEAR's total (as filed in
# the 10-K), not a rolling twelve months. D113: true rolling values are built by PITStore.ttm() from the four most
# recent visible quarterly records ('<base>_ttm4q' names below); the vendor '*_ttm' fields remain readable only as
# fiscal-year values (used by the TTM consistency gate).
TTM_BASES = ("revenue", "gross_profit", "operating_income", "net_income", "operating_cash_flow", "free_cash_flow")
TTM4Q = {b + "_ttm4q": b for b in TTM_BASES}
SNAPSHOT_FIELDS = ("total_assets", "stockholders_equity", "total_debt")   # latest snapshot, never summed
TTM_GAP_DAYS = (80, 100)          # consecutive fiscal quarters (13/14-week quarters included)
TTM_FY_TOLERANCE = 0.01           # Q1+Q2+Q3+Q4 must equal the fiscal-year total within 1% (Q4 validity gate)
MARKET_CAP = "market_cap"            # point-in-time (audit D107); read from the object itself, not from a report
BLACKLIST = ("shares_outstanding", "share_class_level_shares_outstanding", "ordinary_shares_number", "share_issued",
             "basic_average_shares", "diluted_average_shares", "basic_eps", "diluted_eps", "book_value_per_share",
             "accession_number", "roa", "roe", "roic", "gross_margin", "operation_margin", "pe_ratio", "pb_ratio",
             "fiscal_year_end", "morningstar_sector_code", "morningstar_industry_code")


class FundamentalFieldError(KeyError):
    """Raised when a strategy requests a field that is not on the approved whitelist (D108)."""


def check_field(name):
    if name in WHITELIST or name == MARKET_CAP or name in TTM4Q:
        return
    why = "BLACKLISTED (unsafe, D107)" if any(b in name for b in BLACKLIST) else "not on the approved whitelist"
    raise FundamentalFieldError(f"fundamental field {name!r} is {why}")


def clean(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return None if (not math.isfinite(x) or x == 0.0) else x


def accession_year(acc):
    s = str(acc or "").strip()
    parts = s.split("-")
    if len(parts) != 3 or len(parts[1]) != 2 or not parts[1].isdigit():
        return None
    yy = int(parts[1])
    return 2000 + yy if yy < 50 else 1900 + yy


def is_estimated_file_date(period_end, file_date):
    return (period_end is not None and file_date is not None
            and (file_date - period_end).days == APPROX_GAP_DAYS)


def available_from(period_end, file_date):
    """First calendar date on which a report may be used (strictly after filing; +90 days if the file date is the
    vendor's estimate). None if the timing is unknown (never available)."""
    if period_end is None or file_date is None:
        return None
    if is_estimated_file_date(period_end, file_date):
        return period_end + timedelta(days=APPROX_AVAILABLE_AFTER_DAYS)
    if file_date < period_end:
        return None                               # impossible timing: never trusted
    return file_date + timedelta(days=1)


class Record:
    __slots__ = ("period_end", "file_date", "available", "values", "estimated", "accession_year")

    def __init__(self, period_end, file_date, values, accession_year_=None):
        self.period_end, self.file_date, self.values = period_end, file_date, dict(values)
        self.estimated = is_estimated_file_date(period_end, file_date)
        self.available = available_from(period_end, file_date)
        self.accession_year = accession_year_


class PITStore:
    """Per-symbol point-in-time fundamentals. Feed it the vendor's latest report each day (observe); read only via
    get()/record(), which return what was historically available on the given decision date."""

    def __init__(self, max_age_days=DEFAULT_MAX_AGE_DAYS, holds=None, releases=None, blocked=None):
        self.max_age = int(max_age_days)
        self.holds = holds or {}  # key -> {period end ISO: first visible date ISO} (D111 SEC timing holds)
        # key -> [[period end ISO, file date ISO], ...]: quarantined reports whose values were verified against the
        # SEC original filing (D111). Only these leave quarantine; every other anomaly stays hidden.
        self.releases = {k: {tuple(x) for x in v} for k, v in (releases or {}).items()}
        # key -> [[period end ISO, file date ISO], ...]: vendor reports carrying a value first filed AFTER the
        # vendor's file date (restatement look-ahead found by the SEC restatement guard, D111): never exposed.
        self.blocked = {k: {tuple(x) for x in v} for k, v in (blocked or {}).items()}
        self.current = {}      # key -> Record exposed (visible) most recently
        self.seen = set()      # (key, period_end, file_date) already observed (each report counted once)
        self.pending = {}      # key -> list of Records seen but not yet visible
        self.hist = {}         # key -> {period_end: Record} visible versions (latest visible filing per period)
        self.stats = {"observed_new": 0, "estimated": 0, "quarantined": 0, "timing_unknown": 0,
                      "amendments": 0, "delayed_until_available": 0}

    def observe(self, key, period_end, file_date, values, accession_year_, today):
        """Record the vendor's latest report as seen on `today` (it may not be usable yet)."""
        cur = self.current.get(key)
        pend = self.pending.setdefault(key, [])
        sig = (key, period_end, file_date)
        if sig in self.seen:
            return
        self.seen.add(sig)
        rec = Record(period_end, file_date, values, accession_year_)
        self.stats["observed_new"] += 1
        hold = self.holds.get(key, {}).get(str(period_end)) if period_end is not None else None
        if hold is not None and rec.available is not None:
            h = date.fromisoformat(hold)
            if h > rec.available:
                rec.available = h
                self.stats["sec_timing_hold"] = self.stats.get("sec_timing_hold", 0) + 1
        if rec.available is None:
            self.stats["timing_unknown"] += 1
            return
        if (str(period_end), str(file_date)) in self.blocked.get(key, ()):
            self.stats["restatement_blocked"] = self.stats.get("restatement_blocked", 0) + 1
            return                                  # carries later (restated) information: never exposed
        if accession_year_ is not None and accession_year_ > today.year:
            if (str(period_end), str(file_date)) in self.releases.get(key, ()):
                self.stats["quarantine_released"] = self.stats.get("quarantine_released", 0) + 1
            else:
                self.stats["quarantined"] += 1      # value may come from a later filing: never exposed
                return
        if rec.estimated:
            self.stats["estimated"] += 1
        if any(r.period_end == period_end for r in ([cur] if cur else []) + pend):
            self.stats["amendments"] += 1
        if rec.available > today:
            self.stats["delayed_until_available"] += 1
        pend.append(rec)

    def _promote(self, key, today):
        pend = self.pending.get(key) or []
        ready = [r for r in pend if r.available <= today]
        if not ready:
            return
        h = self.hist.setdefault(key, {})
        for r in ready:                    # amendments replace a period only from their own availability date
            old = h.get(r.period_end)
            if old is None or r.file_date >= old.file_date:
                h[r.period_end] = r
        best = max(ready, key=lambda r: (r.period_end, r.file_date))
        cur = self.current.get(key)
        if cur is None or (best.period_end, best.file_date) >= (cur.period_end, cur.file_date):
            self.current[key] = best
        self.pending[key] = [r for r in pend if r.available > today]

    def record(self, key, today):
        """The report historically available on `today`, or None (none yet, or stale beyond max_age)."""
        self._promote(key, today)
        r = self.current.get(key)
        if r is None or r.available > today or (today - r.period_end).days > self.max_age:
            return None                    # defensive: never expose a record before its availability date
        return r

    def get(self, key, name, today):
        check_field(name)
        if name in TTM4Q:
            return self.ttm(key, TTM4Q[name], today)
        r = self.record(key, today)
        return None if r is None else r.values.get(name)

    def _chain(self, recs, i, n):
        """The n consecutive quarterly records ending at index i (oldest first), or None."""
        if i - n + 1 < 0:
            return None
        seg = recs[i - n + 1:i + 1]
        for a, b in zip(seg, seg[1:]):
            gap = (b.period_end - a.period_end).days
            if not (TTM_GAP_DAYS[0] <= gap <= TTM_GAP_DAYS[1]):
                return None
        return seg

    def ttm_detail(self, key, base, today):
        """True rolling twelve-month value of `base` on `today` with its components, or (None, reason).
        Rules (D113): the four most recent VISIBLE quarterly records (quarantined/blocked reports never enter;
        amendments only from their availability), consecutive, each with a '<base>_q' value, newest within the
        freshness limit; and the fiscal-year-end quarter inside the window must reconcile: its fiscal year's four
        quarterly values sum to the fiscal-year total reported on that same record within 1% (this validates a
        derived Q4). No interpolation, no backward filling."""
        self._promote(key, today)
        recs = sorted(self.hist.get(key, {}).values(), key=lambda r: r.period_end)
        recs = [r for r in recs if r.available <= today]
        if len(recs) < 4:
            return None, "fewer than four visible quarters"
        if (today - recs[-1].period_end).days > self.max_age:
            return None, "stale"
        win = self._chain(recs, len(recs) - 1, 4)
        if win is None:
            return None, "quarters not consecutive"
        qs = [r.values.get(base + "_q") for r in win]
        if any(q is None for q in qs):
            return None, "missing quarterly value"
        idx = len(recs) - 1
        for k in range(4):                  # find the fiscal-year-end quarter inside the window and reconcile it
            j = idx - k
            fy = recs[j].values.get(base + "_ttm")
            chain = self._chain(recs, j, 4)
            if fy is None or chain is None or j < 1:
                continue
            prev_fy = recs[j - 1].values.get(base + "_ttm")
            if prev_fy is not None and abs(prev_fy - fy) <= 1e-9 * max(abs(fy), 1.0):
                continue                   # not a fiscal-year-end report: its fiscal-year value did not change
            vals = [r.values.get(base + "_q") for r in chain]
            if any(v is None for v in vals):
                continue
            tot = sum(vals)
            if abs(tot - fy) <= TTM_FY_TOLERANCE * abs(fy):
                return sum(qs), {"quarters": [str(r.period_end) for r in win],
                                 "filed": [str(r.file_date) for r in win], "fy_check_period": str(recs[j].period_end)}
        return None, "no fiscal-year reconciliation inside the window"

    def ttm(self, key, base, today):
        v, _ = self.ttm_detail(key, base, today)
        return v


def read_values(f, getter):
    """Whitelisted values of a vendor Fundamental object `f`; getter(obj, path) resolves dotted paths."""
    out = {}
    for name, (path, per) in WHITELIST.items():
        try:
            out[name] = clean(getattr(getter(f, path), per))
        except Exception:
            out[name] = None
    return out


def financial_format(values):
    """PIT-safe 'financial-format' classification from the report itself (no current-status metadata): a company
    whose filing has revenue but reports neither gross profit nor cost of revenue nor operating income is reported in
    a bank/insurer/financial template. Evaluated on each report as filed (D108)."""
    if not values:
        return None
    if values.get("revenue_ttm") is None:
        return None
    return (values.get("gross_profit_ttm") is None and values.get("cost_of_revenue_ttm") is None
            and values.get("operating_income_ttm") is None)
