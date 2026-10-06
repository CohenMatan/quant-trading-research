# qr_p7_export.py — P7-CP3 (owner D171) score / data export helpers for the non-trading host X993. Pure python /
# numpy, no QuantConnect imports (tests/test_p7_export.py). Runs the FROZEN score v1 (qr_p7_score, hash-pinned in
# qresearch.p7score) on point-in-time inputs; nothing here changes a score definition. NO RETURN of any kind is computed
# or exported: the only price quantities are the frozen score's own features at each decision session.
import base64
import math
import zlib

import numpy as np

import qr_p7 as P7
import qr_p7_score as S

SPAN = 420                 # calendar rows handed to technical_inputs (exactness fallback below)
# disqualifier / status bits of an exported row (raw flags: H6 / H7 are evaluated for every stock with the inputs,
# so overlaps can be counted; the frozen score applies them only to the data-scorable set)
BITS = ("H1_financial", "H1_no_sic", "H2", "H3", "H4", "H5", "H6", "H7", "duplicate_class", "H2_baseline_only",
        "baseline_in_store")
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
    rows = {}
    for s, e in elig.items():
        bits = sic_bits(e["sic"])
        if e.get("base_only"):
            bits |= BIT["H2_baseline_only"]
        if e.get("base_store"):
            bits |= BIT["baseline_in_store"]
        if s not in kept:
            rows[s] = (bits | BIT["duplicate_class"], None, None)
            continue
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
                rows=rows, kept=kept)


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
