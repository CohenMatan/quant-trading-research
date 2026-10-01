# qr_sec_corrections.py — dated SEC correction layer for the D043 survivorship gap (D111). Uploaded next to the
# harness; used only when an experiment sets universe.sec_corrections (opt-in, never silent). No QuantConnect
# imports: the logic is unit-tested offline (tests/test_sec_corrections.py).
#
# For securities that QuantConnect prices but gives NO fundamentals (D043), the table (generated offline from SEC
# EDGAR XBRL by research/phase2/sec/build_corrections.py) supplies, per security id:
#   * the matched SEC registrant (CIK), the match evidence and a confidence/status;
#   * every periodic filing (10-K/10-Q and amendments): accession, form, filing date, period end, the cover-page
#     share count and its cover date, and whitelisted statement totals AS FIRST FILED.
# Point-in-time rules:
#   * a filing is usable from the day AFTER its filing date (same rule as the Morningstar PIT layer);
#   * market cap on day T = cover shares (latest cover date among filings usable on T) x split multiplier for splits
#     with ex-date after the cover date and on/before T (observed live, never from a later file) x raw close; a split
#     between the cover date and the filing date is applied only if the previous filing's count shows the reported
#     count does not already reflect it (some registrants report the post-split count);
#   * a cover count older than MAX_SHARE_AGE_DAYS on T gives NO market cap (unresolved; never extrapolated);
#   * filings without an unambiguous single-class cover count never give a market cap;
#   * outside the table's effective range nothing is returned.
import math
from datetime import date, timedelta

MAX_SHARE_AGE_DAYS = 135     # quarterly cadence (~91 days) + late-filing allowance; older -> unresolved


def _d(s):
    return s if isinstance(s, date) else date.fromisoformat(s)


class SECFiling:
    __slots__ = ("accn", "form", "filed", "period_end", "cover_date", "shares", "values", "available")

    def __init__(self, row):
        accn, form, filed, pe, cd, sh, vals = row
        self.accn, self.form = accn, form
        self.filed, self.period_end = _d(filed), _d(pe)
        self.cover_date = _d(cd) if cd else None
        self.shares = float(sh) if sh else None
        self.values = dict(vals or {})
        self.available = self.filed + timedelta(days=1)


class SECCorrections:
    def __init__(self, table, max_share_age_days=MAX_SHARE_AGE_DAYS):
        self.max_age = int(max_share_age_days)
        self.meta = {}
        self.filings = {}
        table = table or {}
        if "corrections" in table:            # packed D111 table: {"corrections": ..., "timing_holds": ...}
            self.timing_holds = table.get("timing_holds", {})
            self.quarantine_releases = table.get("quarantine_releases", {})
            table = table["corrections"]
        else:
            self.timing_holds, self.quarantine_releases = {}, {}
        for sid, c in table.items():
            if c.get("status") != "repaired":
                continue                      # unresolved / rejected matches never reach the universe
            self.meta[sid] = {k: v for k, v in c.items() if k != "filings"}
            self.filings[sid] = sorted((SECFiling(r) for r in c["filings"]), key=lambda f: (f.filed, f.accn))
        self.splits = {}                      # sid -> [(ex_date, split_factor)] observed live

    def has(self, sid):
        return sid in self.filings

    def sids(self):
        return list(self.filings)

    def observe_split(self, sid, ex_date, factor):
        """Record a split event as it happens (LEAN split factor: 0.5 for a 2-for-1 split)."""
        lst = self.splits.setdefault(sid, [])
        if (ex_date, factor) not in lst:
            lst.append((ex_date, float(factor)))

    def usable(self, sid, today):
        return [f for f in self.filings.get(sid, ()) if f.available <= today]

    def shares_on(self, sid, today):
        """(filing, shares adjusted for splits after its cover date) usable on `today`, or (None, None)."""
        cands = [f for f in self.usable(sid, today) if f.shares and f.cover_date is not None]
        if not cands:
            return None, None
        f = max(cands, key=lambda x: (x.cover_date, x.filed, x.accn))
        if (today - f.cover_date).days > self.max_age:
            return f, None
        prev = [x for x in cands if x.cover_date < f.cover_date]
        prev = max(prev, key=lambda x: (x.cover_date, x.filed)) if prev else None
        mult = 1.0
        for ex, fac in self.splits.get(sid, ()):
            if not (f.cover_date < ex <= today and fac > 0):
                continue
            m = 1.0 / fac
            if ex <= f.filed and prev is not None:
                # split between the cover date and the filing: some registrants already report the post-split
                # count (FCX 10-K 2011). Decide from the previous count, which predates the split.
                r = f.shares / prev.shares
                if abs(math.log(r) - math.log(m)) < abs(math.log(r)):
                    continue                     # the count already reflects this split
            mult *= m
        return f, f.shares * mult

    def market_cap(self, sid, today, raw_price):
        if not raw_price or raw_price <= 0:
            return None
        _, sh = self.shares_on(sid, today)
        return None if sh is None else sh * float(raw_price)

    def feed(self, sid, today, store, key=None):
        """Feed every SEC filing usable on `today` into a qr_fundamentals.PITStore (same rules as vendor data)."""
        for f in self.usable(sid, today):
            store.observe(key or sid, f.period_end, f.filed, f.values, None, today)
