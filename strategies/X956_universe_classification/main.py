# X956 v1.1 — universe classification probe (infrastructure, not research). Places no orders.
# On the first trading day of each month, for every security that passes the CURRENT harness
# universe rule (is_us_common, listed exchange, MarketCap >= min, price >= min), record the
# Morningstar classification fields that can separate true common stock from funds, partnership /
# LLC units and trusts. One line per security and per change of those fields (point in time):
#   QRCL|date|sid|ticker|json(fields)
from AlgorithmImports import *
from qr_harness import QRAlgorithm, EXCHANGES, is_us_common
import json

FIELDS = {
    "company_reference": ("legal_name", "standard_name", "country_id", "is_limited_partnership", "is_reit",
                          "is_limited_liability_company", "industry_template_code", "company_status"),
    "security_reference": ("security_type", "share_class_description", "share_class_status", "is_primary_share",
                           "is_depositary_receipt", "is_direct_invest", "exchange_id"),
    "asset_classification": ("morningstar_sector_code", "morningstar_industry_group_code",
                             "morningstar_industry_code", "sic", "naics", "stock_type"),
}


def _get(obj, name):
    try:
        v = getattr(obj, name)
    except Exception:
        return "<n/a>"
    try:
        v = v.value if hasattr(v, "value") and not isinstance(v, (str, int, float, bool)) else v
    except Exception:
        pass
    return v if isinstance(v, (int, float, bool)) or v is None else str(v)


class UniverseClassification(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self.last_month = None
        self.seen = {}

    def _qr_select(self, fundamental):
        day = self.time.strftime("%Y-%m-%d")
        if day[:7] == self.last_month:
            return []
        self.last_month = day[:7]
        u = self._qr_u
        for f in fundamental:
            if not f.has_fundamental_data or not is_us_common(f, day):
                continue
            if f.security_reference.exchange_id not in EXCHANGES:
                continue
            if f.market_cap < float(u.get("min_market_cap", 2e9)) or f.price < float(u.get("min_price", 0)):
                continue
            rec = {}
            for part, names in FIELDS.items():
                obj = getattr(f, part)
                for n in names:
                    rec[f"{part[:3]}.{n}"] = _get(obj, n)
            sig = json.dumps(rec, sort_keys=True, default=str)
            sid = str(f.symbol.id)
            if self.seen.get(sid) != sig:
                self.seen[sid] = sig
                self._qr_log(f"QRCL|{day}|{sid}|{f.symbol.value}|{sig}")
        return []

    def qr_on_close(self, data):
        pass
