# qr_p7_export.py — P7-CP3 (owner D171) score / data export helpers for the non-trading host X993. Pure python /
# numpy, no QuantConnect imports (tests/test_p7_export.py). Runs the FROZEN score v1 (qr_p7_score, hash-pinned in
# qresearch.p7score) on point-in-time inputs; nothing here changes a score definition. NO RETURN of any kind is computed
# or exported: the only price quantities are the frozen score's own features at each decision session.
import base64
import datetime as _dt
import math
import zlib

import numpy as np

import qr_p7 as P7
import qr_p7_score as S

SPAN = 420                 # calendar rows handed to technical_inputs (exactness fallback below)
# disqualifier / status bits of an exported row (raw flags: H6 / H7 are evaluated for every stock with the inputs,
# so overlaps can be counted; the frozen score applies them only to the data-scorable set)
BITS = ("H1_financial", "H1_no_sic", "H2", "H3", "H4", "H5", "H6", "H7", "duplicate_class", "H2_baseline_only",
        "baseline_in_store",
        # P7-CP3R (D173): store-wide revenue baseline
        "rescued", "baseline_life_reject", "baseline_cik_reject", "listed_lt_1y_at_baseline", "H2_old_rule",
        "alt_class_scored")
REASON_SHIFT = 20          # bits 20-22: why a rescued stock was outside the eligible universe at the baseline review
REASONS = {0: "eligible", 1: "not in QuantConnect's universe list", 2: "market cap < $2B", 3: "price < $5",
           4: "ADV20 < $5M or < 20 days of ADV history", 5: "not US common stock / exchange", 6: "unknown"}
BIT = {b: 1 << i for i, b in enumerate(BITS)}
DIMS = ("trend", "momentum", "risk", "profitability", "cash_conversion", "balance_sheet", "growth", "sector")
FUND_BASES = ("revenue", "gross_profit", "net_income", "operating_cash_flow")


# ----------------------------------------------------------------------------------------------- technical (exact)
def tech_at(C, P, t, unverified_rows=(), distributions=(), span=SPAN, gap=P7.LIFE_GAP):
    """The frozen technical_inputs + contamination of ONE security at calendar row t, computed on the slice
    [t - span, t] for speed, with an exactness guarantee: every score output depends only on the last TR_WINDOW
    (253) valid bars of the current life and on the contamination window (<= 253 valid bars). The slice result is
    therefore identical to the full-history result whenever the slice holds >= 253 valid bars up to t (the current
    life then either starts inside the slice after a detected gap, i.e. the same life, or holds >= 253 bars in both
    computations; the contamination window starts at the same bar), or when the slice starts at row 0. Otherwise the
    full history is used. Event rows are calendar rows (shifted to the slice).
    Returns (ti, contaminated, reasons, bars_until_clean, used_full)."""
    lo = max(0, int(t) - span)
    ti = S.technical_inputs(C[lo:t + 1], P[lo:t + 1], t - lo, gap)
    full = lo > 0 and ti["_b"] + 1 < S.TR_WINDOW       # fewer than 253 valid bars in the slice (or none)
    if full:
        lo = 0
        ti = S.technical_inputs(C[:t + 1], P[:t + 1], t, gap)
    # events before the slice start can never fall inside a window here (the window starts at or after the slice)
    un = [e - lo for e in unverified_rows if e - lo >= 0]
    di = [(e - lo, f) for e, f in distributions if e - lo >= 0]
    c, why, clear = S.contamination(ti, un, di)
    return ti, c, why, clear, full


# ----------------------------------------------------------------------------------------------- fundamentals
def fund_values(store, sid, today):
    """The seven-field inputs known on `today` (selection day) from the frozen PIT store: (rev, gp, ni, ocf) True TTM
    and (total assets, equity) from the current record (None if absent / stale)."""
    v = [store.ttm(sid, b, today) for b in FUND_BASES]
    r = store.record(sid, today)
    ta = r.values.get("total_assets") if r is not None else None
    eq = r.values.get("stockholders_equity") if r is not None else None
    return v + [ta, eq]


def fund_inputs(vals, rev_prev):
    """frozen fundamental_inputs on the store values and the ledger baseline. Returns (fi, why, baseline_only):
    baseline_only = H2 caused only by the missing revenue baseline (every other input present and valid)."""
    rev, gp, ni, ocf, ta, eq = vals
    fi, why = S.fundamental_inputs(rev, gp, ni, ocf, ta, eq, rev_prev)
    base_only = False
    if fi is None and rev_prev is None:
        fi2, _ = S.fundamental_inputs(rev, gp, ni, ocf, ta, eq, 1.0)
        base_only = fi2 is not None
    return fi, why, base_only


# ----------------------------------------------------------------------------------------------- revenue baseline
class RevenueLedger:
    """P7-CP3R (D173): the company PIT revenue True TTM recorded LIVE at every month-end review for every company in
    the PIT store (not only eligible ones). Keyed by the (year, month) of the review session; each value is what the
    frozen store returned on the selection day reflecting that session, with its quarter period ends / filing dates
    (date ordinals) for audit. Values are never recomputed later, so later filings cannot alter them."""

    def __init__(self):
        self.v = {}            # (y, m) -> {sid: (value, (period end ordinals), (filed ordinals))}
        self.day = {}          # (y, m) -> (review session date, selection date)

    def record(self, ym, session, today, store, sids):
        d = {}
        for sid in sids:
            v, det = store.ttm_detail(sid, "revenue", today)
            if v is not None:
                d[sid] = (v, tuple(_ord(x) for x in det["quarters"]), tuple(_ord(x) for x in det["filed"]))
        self.v[ym] = d
        self.day[ym] = (session, today)

    def prior(self, ym):
        return (ym[0] - 1, ym[1])

    def baseline(self, ym, sid):
        """(value, detail, (session, selection day)) recorded at the review 12 months earlier, or (None, None, day)."""
        p = self.prior(ym)
        x = self.v.get(p, {}).get(sid)
        return (x[0], x, self.day.get(p)) if x else (None, None, self.day.get(p))

    def drop(self, ym):
        self.v.pop(ym, None)


def _ord(iso):
    y, m, d = (int(t) for t in str(iso)[:10].split("-"))
    return _dt.date(y, m, d).toordinal()


def baseline_check(life_start_row, base_row, cik_base, cik_now):
    """Same-company continuity of a store-wide revenue baseline: the security's current price life must have started
    on or before the baseline review session (security-life rule, D167), and the SEC registrant CIK (PIT SIC table) must
    not differ where it is known at both dates. Returns (ok, reason)."""
    if life_start_row is None or base_row is None or life_start_row > base_row:
        return False, "life"
    if cik_base is not None and cik_now is not None and cik_base != cik_now:
        return False, "cik"
    return True, ""


# ----------------------------------------------------------------------------------------------- one review
def sic_bits(sic):
    if sic is None:
        return BIT["H1_no_sic"]
    return BIT["H1_financial"] if 6000 <= int(sic) <= 6999 else 0


def score_review(elig, state200, tech, ff12):
    """elig: {sid: dict(sic, cik, adv, fund=(fi, why), base_only, base_store)}; state200: {sid: True/False/None}
    (above own SMA200; None = < 200 current-life bars or stale); tech: callable sid -> (ti, contaminated, ...);
    ff12: callable sic -> group. Returns dict(records, context, breadth, rows, kept) where rows = {sid: (bits, total,
    points tuple or None)} for EVERY eligible security (duplicate classes included, flagged)."""
    mb, up, known, n_el, _ = P7.breadth(state200, list(elig))
    grp = {s: ff12(e["sic"]) for s, e in elig.items()}
    members = {}
    for s, g in grp.items():
        members.setdefault(g, []).append(s)
    ctx, sect = {}, {}
    for g, ms in sorted(members.items()):
        sb, _, kn, n, _ = P7.breadth(state200, ms)
        ctx[g] = S.sector_state(sb if kn else None, mb if known else None, kn)
        sect[g] = (sb if kn else None, kn, n)
    kept = S.select_share_classes({s: (e["cik"], e["adv"]) for s, e in elig.items()})
    stocks, techs = {}, {}
    for s in sorted(kept):
        e = elig[s]
        ti, cont = tech(s)[:2]
        techs[s] = ti
        stocks[s] = dict(ff12=grp[s], sic=e["sic"], tech=ti, contaminated=cont, fund=e["fund"])
    rec = S.score_date(stocks, ctx)
    # P7-CP3R (D173): score each non-chosen class of a multi-class company with that class substituted (same ranking
    # population otherwise); used only to keep an already-held class (owner rule 23)
    alt = {}
    groups = {}
    for s_, e in elig.items():
        if e["cik"] is not None:
            groups.setdefault(e["cik"], []).append(s_)
    for cik, mem in sorted(groups.items()):
        if len(mem) < 2:
            continue
        chosen = [m for m in mem if m in kept]
        for a in sorted(m for m in mem if m not in kept):
            st2 = {k: v for k, v in stocks.items() if k not in chosen}
            e = elig[a]
            ti, cont = tech(a)[:2]
            techs[a] = ti
            st2[a] = dict(ff12=grp[a], sic=e["sic"], tech=ti, contaminated=cont, fund=e["fund"])
            alt[a] = S.score_date(st2, ctx)[a]
    rows = {}
    for s, e in elig.items():
        bits = sic_bits(e["sic"])
        if e.get("base_only"):
            bits |= BIT["H2_baseline_only"]
        if e.get("base_store"):
            bits |= BIT["baseline_in_store"]
        for b in ("rescued", "baseline_life_reject", "baseline_cik_reject", "listed_lt_1y_at_baseline", "H2_old_rule"):
            if e.get(b):
                bits |= BIT[b]
        bits |= int(e.get("reason", 0)) << REASON_SHIFT
        if s not in kept:
            bits |= BIT["duplicate_class"]
            if s not in alt:
                rows[s] = (bits, None, None)
                continue
            bits |= BIT["alt_class_scored"]
            r = alt[s]
        else:
            r = rec[s]
        ti, fi = techs[s], e["fund"][0]
        for code, b in (("H2", "H2_fundamentals_missing_or_stale"), ("H3", "H3_insufficient_history"),
                        ("H4", "H4_corporate_event_contamination"), ("H5", "H5_stale_price")):
            if b in r["dq"]:
                bits |= BIT[code]
        if ti.get("broken_trend"):
            bits |= BIT["H6"]
        if fi is not None and fi["impaired"]:
            bits |= BIT["H7"]
        if r["total"] is not None:          # consistency with the frozen economic disqualifiers
            assert (("H6_broken_long_term_trend" in r["dq"]) == bool(bits & BIT["H6"])
                    and ("H7_financial_impairment" in r["dq"]) == bool(bits & BIT["H7"]))
            rows[s] = (bits, r["total"], tuple(r["points"][d] for d in DIMS))
        else:
            rows[s] = (bits, None, None)
    return dict(records=rec, context=ctx, sectors=sect, breadth=(mb if known else None, up, known, n_el),
                rows=rows, kept=kept, alt=alt)


def eligible_flag(bits, total):
    """A row is a candidate-eligible stock (no hard disqualifier, kept class) with a total."""
    bad = BIT["H1_financial"] | BIT["H1_no_sic"] | BIT["H2"] | BIT["H3"] | BIT["H4"] | BIT["H5"] | BIT["H6"] | \
        BIT["H7"] | BIT["duplicate_class"]
    return total is not None and not (bits & bad)


# ----------------------------------------------------------------------------------------------- encoding
def encode_rows(rows, sid_index, adv, ff12_of, ff12_names):
    """One review -> text: 'i,bits,advK,ff,total,p1..p8' per row (scored) or 'i,bits,advK,ff' (not scored)."""
    out = []
    gi = {g: i for i, g in enumerate(ff12_names)}
    for s in sorted(rows, key=lambda x: sid_index[x]):
        bits, tot, pts = rows[s]
        a = int(round(adv[s] / 1000.0))
        head = f"{sid_index[s]},{bits},{a},{gi[ff12_of[s]]}"
        out.append(head if tot is None else head + f",{tot}," + ",".join(str(p) for p in pts))
    return ";".join(out)


def decode_rows(text):
    rows = []
    for part in text.split(";") if text else []:
        x = [int(v) for v in part.split(",")]
        rows.append(dict(i=x[0], bits=x[1], adv_k=x[2], ff=x[3], total=x[4] if len(x) > 4 else None,
                         points=tuple(x[5:13]) if len(x) > 4 else None))
    return rows


def pack(text):
    return base64.b64encode(zlib.compress(text.encode(), 9)).decode()


def unpack(b64):
    return zlib.decompress(base64.b64decode(b64)).decode()


def finite(x):
    return x is not None and isinstance(x, (int, float)) and math.isfinite(x)
