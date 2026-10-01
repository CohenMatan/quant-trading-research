# X968 v1.0 — universe-exclusion diagnostic (infrastructure; NO orders), prompted by the fundamental-data audit
# (E967-02: Visa, Time Warner and Chesapeake were never eligible). Monthly, for every Morningstar security with
# market cap >= $2B, records the FIRST harness rule that excludes it (same order as the harness), and the 25
# largest excluded names by market-cap rank with their reason. Counts, ranks, tickers and reasons only.
from AlgorithmImports import *
import json
from qr_harness import COMMON_STOCK, EXCHANGES, QRAlgorithm, _attr, non_common_reason

WATCH = ("V", "TWX", "CHK", "HTZ", "MA", "GOOGL", "BRK.B", "BRKB", "META", "FB", "PM", "ABBV", "KMI", "BX", "KKR")


def first_reason(f, day):
    sr = f.security_reference
    if sr.security_type != COMMON_STOCK:
        return "not_common_stock_type"
    if sr.is_depositary_receipt:
        return "depositary_receipt"
    if not (bool(sr.is_primary_share) or str(f.company_reference.country_id) == "USA"):
        return "not_primary_and_not_USA:" + str(f.company_reference.country_id)
    r = non_common_reason(f, day)
    if r is not None:
        return "D057:" + r
    if sr.exchange_id not in EXCHANGES:
        return "exchange:" + str(sr.exchange_id)
    return None


class UniverseExclusions(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self.month = None
        self.d = {"by_reason": {}, "by_reason_year": {}, "top_excluded": [], "watch": {}}

    def _qr_select(self, fundamental):
        fl = list(fundamental)
        super()._qr_select(fl)
        m = (self.time.year, self.time.month)
        if m == self.month:
            return []
        self.month = m
        day = self.time.strftime("%Y-%m-%d")
        rows = []
        for f in fl:
            if not f.has_fundamental_data or f.market_cap < 2e9:
                continue
            try:
                r = first_reason(f, day)
            except Exception as e:
                r = "error:" + type(e).__name__
            rows.append((float(f.market_cap), f.symbol.value, r))
            t = f.symbol.value
            if t in WATCH and (self.time.month == 1 or r is not None):
                w = self.d["watch"].setdefault(t, {})
                w[day[:7]] = r or "structurally eligible"
        rows.sort(reverse=True)
        y = str(self.time.year)
        for rank, (cap, t, r) in enumerate(rows, 1):
            if r is None:
                continue
            key = r.split(":")[0] if not r.startswith("D057") else r
            self.d["by_reason"][key] = self.d["by_reason"].get(key, 0) + 1
            by = self.d["by_reason_year"].setdefault(y, {})
            by[key] = by.get(key, 0) + 1
            if rank <= 300 and self.time.month == 1:
                self.d["top_excluded"].append(f"{day}|rank={rank}|{t}|{r}")
        return []

    def qr_select_universe(self, eligible):
        return []

    def qr_on_end(self):
        text = json.dumps(self.d, sort_keys=True)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRX68|summary|{i // 9000}|{text[i:i + 9000]}")
