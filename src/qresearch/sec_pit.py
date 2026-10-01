"""Point-in-time records from SEC XBRL company facts (D111). Pure functions; no network, no QuantConnect.

One record per periodic filing (10-K, 10-Q and their amendments), built ONLY from facts that were public on that
filing's date:
  * the filing's own facts (its accession number) for its own reporting period: values AS FIRST FILED;
  * for trailing-twelve-month and fourth-quarter arithmetic, values from filings made on or before that filing
    date (the latest one known then) — never from a later filing.

Cover-page shares (dei:EntityCommonStockSharesOutstanding):
  * an INSTANT count of shares outstanding at the cover date (`end`), the latest practicable date before filing;
    not weighted-average (income-statement weighted shares are never used);
  * reported as of that date: NOT restated for later splits (verified on AAPL 2014/2020 and in the canaries);
  * one non-dimensional value means a single class; multi-class registrants report per-class values with the
    class-of-stock axis, which the company-facts API omits — such filings are flagged `multi_class_unknown`
    (no market cap is reconstructed from them; D111 share-count policy).
"""
from __future__ import annotations

from datetime import date, timedelta

PERIODIC_FORMS = ("10-K", "10-Q", "10-K/A", "10-Q/A", "10-KT", "10-KT/A")

TAGS = {
    "revenue": ("Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
                "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueGoodsNet",
                "SalesRevenueServicesNet", "RevenuesNetOfInterestExpense"),
    "gross_profit": ("GrossProfit",),
    "cost_of_revenue": ("CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold", "CostOfServices"),
    "operating_income": ("OperatingIncomeLoss",),
    "net_income": ("NetIncomeLoss", "NetIncomeLossAvailableToCommonStockholdersBasic", "ProfitLoss"),
    "total_assets": ("Assets",),
    "stockholders_equity": ("StockholdersEquity",
                            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"),
    "operating_cash_flow": ("NetCashProvidedByUsedInOperatingActivities",
                            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"),
    "capex": ("PaymentsToAcquirePropertyPlantAndEquipment",),
}
# Bank fallback for revenue only when no revenue tag exists: interest and dividend income + non-interest income.
BANK_REVENUE = ("InterestAndDividendIncomeOperating", "NoninterestIncome")
FLOWS = ("revenue", "gross_profit", "cost_of_revenue", "operating_income", "net_income", "operating_cash_flow",
         "capex")
STOCKS = ("total_assets", "stockholders_equity")
SHARES_TAG = "EntityCommonStockSharesOutstanding"


def d(s):
    return date.fromisoformat(s) if isinstance(s, str) else s


def dur_class(start, end):
    n = (d(end) - d(start)).days
    if 80 <= n <= 100:
        return 1
    if 170 <= n <= 190:
        return 2
    if 260 <= n <= 285:
        return 3
    if 350 <= n <= 380:
        return 4
    return None


def near(a, b, tol=7):
    return abs((d(a) - d(b)).days) <= tol


def index_facts(cf: dict) -> dict:
    """concept -> list of facts (USD or shares), each with parsed dates; concepts from us-gaap and dei."""
    out = {}
    if not cf:
        return out
    for tax in ("us-gaap", "dei"):
        for tag, body in (cf.get("facts", {}).get(tax) or {}).items():
            units = body.get("units", {})
            facts = units.get("USD") or units.get("shares")
            if facts:
                out[tag] = facts
    return out


def periodic_filings(facts: dict, sub_rows: list[dict] | None) -> list[dict]:
    """Periodic filings (accession, form, filing date, period end) sorted by filing date. The period end is the
    submissions reportDate when available, else the latest balance-sheet date reported in the filing."""
    meta = {}
    for tag, fl in facts.items():
        for f in fl:
            if f.get("form") in PERIODIC_FORMS:
                m = meta.setdefault(f["accn"], {"accn": f["accn"], "form": f["form"], "filed": f["filed"],
                                                "fy": f.get("fy"), "fp": f.get("fp"), "ends": set()})
                if tag in ("Assets", "StockholdersEquity") and "start" not in f:
                    m["ends"].add(f["end"])
    rep = {}
    for r in sub_rows or []:
        rep[r["accessionNumber"]] = r
    out = []
    for a, m in meta.items():
        r = rep.get(a)
        pe = (r or {}).get("reportDate") or (max(m["ends"]) if m["ends"] else None)
        if not pe:
            continue
        out.append({"accn": a, "form": m["form"], "filed": m["filed"], "period_end": pe, "fy": m["fy"],
                    "fp": m["fp"], "acceptance": (r or {}).get("acceptanceDateTime")})
    out.sort(key=lambda x: (x["filed"], x["accn"]))
    return out


def _own(facts, tags, accn):
    for t in tags:
        rows = [f for f in facts.get(t, ()) if f["accn"] == accn]
        if rows:
            return t, rows
    return None, []


def _flow_fact(rows, pe, cls, shift_years=0):
    tgt = d(pe) - timedelta(days=365 * shift_years)
    for f in rows:
        if "start" in f and near(f["end"], tgt) and dur_class(f["start"], f["end"]) == cls:
            return f
    return None


def _flow(rows, pe, cls, shift_years=0):
    f = _flow_fact(rows, pe, cls, shift_years)
    return None if f is None else f["val"]


def _known(facts, tags, filed, cls, end=None, start=None):
    """Latest value known on `filed` (from any filing made on or before it) for a flow of duration class `cls`
    ending near `end` and/or starting near `start`."""
    for t in tags:
        cand = [f for f in facts.get(t, ()) if f["filed"] <= filed and "start" in f
                and dur_class(f["start"], f["end"]) == cls
                and (end is None or near(f["end"], end)) and (start is None or near(f["start"], start))]
        if cand:
            return max(cand, key=lambda f: (f["filed"], f["accn"]))["val"]
    return None


def _ytd_class(rows, pe):
    """Longest fiscal year-to-date duration class reported for the current period in this filing."""
    best = None
    for f in rows:
        if "start" in f and near(f["end"], pe):
            c = dur_class(f["start"], f["end"])
            if c and (best is None or c > best):
                best = c
    return best


def record_for(facts: dict, filing: dict) -> dict:
    """Whitelist-equivalent values for one filing, using only information public on its filing date."""
    accn, pe, filed = filing["accn"], filing["period_end"], filing["filed"]
    vals = {}
    src = {}
    for name in FLOWS:
        tags = TAGS[name]
        tag, rows = _own(facts, tags, accn)
        if not rows:
            vals[name + "_ttm"] = vals[name + "_q"] = None
            continue
        src[name] = tag
        ytd = _ytd_class(rows, pe)
        cur_f = _flow_fact(rows, pe, ytd) if ytd else None
        cur = None if cur_f is None else cur_f["val"]
        q = _flow(rows, pe, 1)
        ttm = None
        if ytd == 4 and cur is not None:
            ttm = cur
            if q is None:
                nine = _known(facts, (tag,), filed, 3, start=cur_f["start"])
                q = cur - nine if nine is not None else None
        elif ytd in (1, 2, 3) and cur is not None:
            prev_ytd = _flow(rows, pe, ytd, shift_years=1)
            if prev_ytd is None:
                prev_ytd = _known(facts, (tag,), filed, ytd, end=d(pe) - timedelta(days=365))
            prev_fy = _known(facts, (tag,), filed, 4, end=d(cur_f["start"]) - timedelta(days=1))
            if prev_ytd is not None and prev_fy is not None:
                ttm = cur + prev_fy - prev_ytd
            if q is None:
                if ytd == 1:
                    q = cur
                else:
                    prior = _known(facts, (tag,), filed, ytd - 1, start=cur_f["start"])
                    q = cur - prior if prior is not None else None
        vals[name + "_ttm"], vals[name + "_q"] = ttm, q
    if vals.get("revenue_ttm") is None and vals.get("revenue_q") is None:
        parts = [_own(facts, (t,), accn)[1] for t in BANK_REVENUE]
        if all(parts):
            ytd = _ytd_class(parts[0], pe)
            if ytd == 4:
                a, b = _flow(parts[0], pe, 4), _flow(parts[1], pe, 4)
                if a is not None and b is not None:
                    vals["revenue_ttm"] = a + b
                    src["revenue"] = "+".join(BANK_REVENUE)
    for name in STOCKS:
        tag, rows = _own(facts, TAGS[name], accn)
        v = None
        for f in rows:
            if "start" not in f and near(f["end"], pe, 3):
                v = f["val"]
                break
        vals[name] = v
        if tag:
            src[name] = tag
    ocf, cap = vals.get("operating_cash_flow_ttm"), vals.get("capex_ttm")
    vals["free_cash_flow_ttm"] = (ocf - cap) if (ocf is not None and cap is not None) else None
    vals.pop("capex_ttm", None)
    vals.pop("capex_q", None)
    vals.pop("cost_of_revenue_q", None)
    vals.pop("free_cash_flow_q", None)
    vals["total_debt"] = None          # not reconstructed from SEC tags (component definitions vary; D111)
    return {"values": {k: (float(v) if v is not None and v != 0 else None) for k, v in vals.items()},
            "tags": src}


def cover_shares(facts: dict, filing: dict):
    """(cover date, shares) for the filing's own cover page, or (None, None). Only the filing's own
    non-dimensional value whose date lies between the period end - 10 days and the filing date."""
    rows = [f for f in facts.get(SHARES_TAG, ()) if f["accn"] == filing["accn"]]
    rows = [f for f in rows if d(filing["period_end"]) - timedelta(days=10) <= d(f["end"]) <= d(filing["filed"])]
    if not rows:
        return None, None
    if len({f["end"] for f in rows}) > 1 or len(rows) > 1:
        vals = {f["val"] for f in rows}
        if len(vals) > 1:
            return None, None          # ambiguous: several values on one cover -> unresolved
    f = rows[0]
    return f["end"], float(f["val"])


def build_company(cf: dict, sub: dict | None) -> list[dict]:
    """All periodic-filing records of one company: identifiers, dates, cover shares and values as first filed."""
    from .sec_edgar import filings_table
    facts = index_facts(cf)
    rows = filings_table(sub) if sub else None
    out = []
    for fl in periodic_filings(facts, rows):
        rec = record_for(facts, fl)
        cd, sh = cover_shares(facts, fl)
        out.append({**fl, "cover_date": cd, "cover_shares": sh, **rec})
    return out


VERSION_FIELDS = {     # field -> (concept key in TAGS, kind): instants at the period end, flows of one quarter or year
    "total_assets": ("total_assets", "instant"), "stockholders_equity": ("stockholders_equity", "instant"),
    "revenue_q": ("revenue", 1), "net_income_q": ("net_income", 1),
    "revenue_fy": ("revenue", 4), "net_income_fy": ("net_income", 4), "operating_cash_flow_fy": ("operating_cash_flow", 4),
}


def period_versions(facts: dict, period_end: str) -> list[dict]:
    """Every filing that reported a value for this period (original, amendments, later filings' comparatives,
    8-K recasts): accession, form, filing date and the values AS REPORTED IN THAT FILING. Used to classify vendor
    values as original / restated / other (restatement and accession-anomaly audit)."""
    out = {}
    for field, (concept, kind) in VERSION_FIELDS.items():
        for tag in TAGS[concept]:
            hit = False
            for f in facts.get(tag, ()):
                if not near(f["end"], period_end, 3):
                    continue
                if kind == "instant":
                    if "start" in f:
                        continue
                elif "start" not in f or dur_class(f["start"], f["end"]) != kind:
                    continue
                v = out.setdefault(f["accn"], {"accn": f["accn"], "form": f["form"], "filed": f["filed"], "values": {}})
                v["values"].setdefault(field, float(f["val"]))
                hit = True
            if hit:
                break
    return sorted(out.values(), key=lambda x: (x["filed"], x["accn"]))
