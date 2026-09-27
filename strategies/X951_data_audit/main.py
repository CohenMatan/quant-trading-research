# X951 — data audit (infrastructure, not research). Places no orders.
#
# On the first trading day of each month it logs one QRAUDIT_M line (JSON) measured on the full
# fundamental ("coarse") universe of that day:
#   n_all           securities delivered (every listed US equity with a price, incl. ETFs)
#   n_fund          of n_all: has Morningstar fundamental data
#   n_common        of n_fund: common stock, primary share, not an ADR, NYSE/Nasdaq/AMEX
#   n_ge2b          of n_common: MarketCap >= $2B
#   n_elig          harness eligible count (n_ge2b after price / dollar-volume filters)
#   dv_p10          10th percentile of daily dollar volume among the n_ge2b names
#   n_zero_common   of n_common: MarketCap <= 0 although price > $1 and dollar volume > $1M
#   n_zero_liquid   of n_zero_common: dollar volume >= dv_p10 (plausibly large, missing cap)
#   n_nofund_liquid not in n_fund but dollar volume >= dv_p10 (plausibly large; includes ETFs)
#   dv_share_ge2b   share of total dollar volume traded in n_ge2b names
#   dv_share_nocap  share of total dollar volume in names with no fundamentals or MarketCap <= 0
#   n_other_ex      common primary MarketCap >= $2B listed elsewhere (excluded)
#   n_adr           depositary receipts with MarketCap >= $2B (excluded)
# Plus: once a year, examples of liquid names without a MarketCap; known-name market-cap
# snapshots; first/last dates with a positive MarketCap for known failed/acquired companies.
from AlgorithmImports import *
from qr_harness import QRAlgorithm, COMMON_STOCK, EXCHANGES
import json

# (first selection on/after date, ticker at that time, approximate public market cap in $B)
# Reference values are approximate (close × shares outstanding from public filings); tolerance ±30%.
SNAPSHOTS = [
    ("2000-01-03", "MSFT", 602), ("2000-01-03", "GE", 508), ("2000-01-03", "WCOM", 151),
    ("2001-01-02", "ENE", 62), ("2008-01-02", "XOM", 504), ("2008-01-02", "LEH", 35),
    ("2008-01-02", "BSC", 10.4), ("2012-09-20", "AAPL", 659), ("2014-06-10", "AAPL", 561),
]
TRACKED = ("ENE", "WCOM", "LEH", "BSC", "LU", "WB", "MER", "CFC", "WM", "GM")


class DataAudit(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 600
        self.last_month = None
        self.last_year = None
        self.pending = sorted(SNAPSHOTS)
        self.track_sid = {}        # ticker -> SID (first sighting under that ticker)
        self.track = {}            # ticker -> dict(first_seen, last_seen, first_cap, last_cap)

    def _qr_select(self, fundamental):
        fundamental = list(fundamental)
        day = self.time.strftime("%Y-%m-%d")
        self._track(fundamental, day)
        while self.pending and self.pending[0][0] <= day:
            d, tick, ref = self.pending.pop(0)
            hit = [f for f in fundamental if f.symbol.value == tick]
            if hit:
                f = hit[0]
                self._qr_log(f"QRAUDIT_SNAP|{d}|{day}|{tick}|mcap={f.market_cap/1e9:.2f}|ref={ref}|price={f.price}|fund={f.has_fundamental_data}")
            else:
                self._qr_log(f"QRAUDIT_SNAP|{d}|{day}|{tick}|mcap=NOT_FOUND|ref={ref}")
        super()._qr_select(fundamental)
        if day[:7] != self.last_month:
            self.last_month = day[:7]
            self._month_stats(fundamental, day)
        return []   # the audit subscribes to nothing (SPY only, from the harness)

    def _track(self, fundamental, day):
        for f in fundamental:
            v = f.symbol.value
            if v in TRACKED and v not in self.track_sid:
                self.track_sid[v] = str(f.symbol.id)
                self.track[v] = dict(first_seen=day, last_seen=day, first_cap=None, last_cap=None)
        sids = {sid: t for t, sid in self.track_sid.items()}
        for f in fundamental:
            t = sids.get(str(f.symbol.id))
            if t is None:
                continue
            r = self.track[t]
            r["last_seen"] = day
            if f.market_cap > 0:
                r["first_cap"] = r["first_cap"] or day
                r["last_cap"] = day

    def _month_stats(self, fundamental, day):
        n = dict(n_all=len(fundamental), n_fund=0, n_common=0, n_ge2b=0, n_zero_common=0,
                 n_zero_liquid=0, n_nofund_liquid=0, n_other_ex=0, n_adr=0)
        big_dv, dv_total, dv_big, dv_nocap = [], 0.0, 0.0, 0.0
        zero_common, nofund = [], []
        for f in fundamental:
            dv = float(f.dollar_volume)
            dv_total += dv
            if not f.has_fundamental_data:
                dv_nocap += dv
                nofund.append((dv, f.symbol.value))
                continue
            n["n_fund"] += 1
            sr = f.security_reference
            mc = float(f.market_cap)
            if mc <= 0:
                dv_nocap += dv
            if sr.is_depositary_receipt and mc >= 2e9:
                n["n_adr"] += 1
            if sr.security_type != COMMON_STOCK or not sr.is_primary_share or sr.is_depositary_receipt:
                continue
            if sr.exchange_id not in EXCHANGES:
                if mc >= 2e9:
                    n["n_other_ex"] += 1
                continue
            n["n_common"] += 1
            if mc >= 2e9:
                n["n_ge2b"] += 1
                big_dv.append(dv)
                dv_big += dv
            elif mc <= 0 and f.price > 1 and dv > 1e6:
                n["n_zero_common"] += 1
                zero_common.append((dv, f.symbol.value))
        big_dv.sort()
        p10 = big_dv[len(big_dv) // 10] if big_dv else 0.0
        n["n_zero_liquid"] = sum(1 for dv, _ in zero_common if dv >= p10)
        n["n_nofund_liquid"] = sum(1 for dv, _ in nofund if dv >= p10)
        n["n_elig"] = len(self.qr_eligible)
        n["dv_p10"] = round(p10)
        n["dv_share_ge2b"] = round(dv_big / dv_total, 4) if dv_total else 0.0
        n["dv_share_nocap"] = round(dv_nocap / dv_total, 4) if dv_total else 0.0
        self._qr_log(f"QRAUDIT_M|{day}|" + json.dumps(n, sort_keys=True))
        if day[:4] != self.last_year:
            self.last_year = day[:4]
            top_zero = [t for _, t in sorted(zero_common, reverse=True)[:8]]
            top_nofund = [t for _, t in sorted(nofund, reverse=True)[:12]]
            self._qr_log(f"QRAUDIT_EX|{day}|zero_cap_common={','.join(top_zero)}|no_fundamentals={','.join(top_nofund)}")

    def qr_on_end(self):
        self.log("QRAUDIT_TRACK|" + json.dumps(self.track, sort_keys=True))
