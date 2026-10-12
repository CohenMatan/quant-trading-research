"""Data v3 (owner D229; research/phase14/data_v3/DATA_V3_spec.md): offline construction of the guard-v3 reference
table and the SEC validation reference from public SEC company facts. Pure functions (no network, no QuantConnect).

Section numbers refer to the pre-registered spec.
  * As-known value of period p on day d (section 3.3): only facts filed on or before d. A quarterly flow is the
    latest-filed three-month fact ending within +-7 days of p, else the year-to-date difference (longest class ending
    at p minus the class one quarter shorter with the same start, ending 60-120 days before p). A year-to-date value
    is never taken as a quarter. Total assets: the latest-filed instant within +-3 days.
  * Timeline (3.4): the as-known value on every distinct filing day; a value is kept when it differs by more than
    STORE_TOL from every value kept before it; kept values after the first are 'restated values'.
  * SEC-side signals (7.2): F1, F2, F4, F5, F8 from SEC as-known quarterly values, anchored on the latest Data v2.1
    filing-table period whose original 10-Q / 10-K is public and at most 200 days old.
Days are integers since 2000-01-01 (the Data v2 convention)."""
from __future__ import annotations

import base64
import hashlib
import json
import lzma
from datetime import date, timedelta

from .sec_pit import TAGS, dur_class

EPOCH = date(2000, 1, 1)
END = "2021-12-31"
STORE_TOL = 0.015                  # spec 3.4: restated values differ by more than 1.5% from every earlier kept value
FIELDS = ("revenue_q", "gross_profit_q", "net_income_q", "operating_cash_flow_q", "total_assets")
CONCEPTS = ("revenue", "gross_profit", "net_income", "operating_cash_flow")
END_TOL, TA_TOL = 7, 3
PRIOR_END = (60, 120)              # the shorter year-to-date fact ends 60-120 days before p
GAP = (80, 100)                    # consecutive quarters (frozen True-TTM rule)
MAX_AGE = 200                      # freshness of the anchor (frozen)
CHUNK = 63_900                     # QuantConnect project files hold at most 64,000 characters
MAX_PARTS = 4                      # spec 3.7
SIGNALS = ("F1", "F2", "F4", "F5", "F8")
RAW = ("rq0", "R0", "GP0", "NI0", "OCF0", "TA0")


def dn(s) -> int:
    return (date.fromisoformat(str(s)[:10]) - EPOCH).days


def dd(n: int) -> date:
    return EPOCH + timedelta(days=int(n))


def g4(x):
    """Four significant digits (the frozen Data v2 code: mantissa x 100 + exponent); |x| < 1 -> 0 (not stored)."""
    if not x or abs(x) < 1.0:
        return 0
    sgn = -1 if x < 0 else 1
    m, e = f"{abs(x):.3e}".split("e")
    return sgn * (int(m.replace(".", "")) * 100 + int(e))


def ug4(c):
    if not c:
        return 0.0
    a = abs(int(c))
    return (-1 if c < 0 else 1) * (a // 100) * 10.0 ** (a % 100 - 3)


# ----------------------------------------------------------------------------------------------- facts index
class Facts:
    """Company facts of one registrant, indexed for as-known lookups. Each flow fact: (filed day, accession,
    -tag priority, start day, duration class, value); instants likewise with start None and class 0."""

    def __init__(self, cf: dict, end: str = END):
        self.flows = {c: {} for c in CONCEPTS}
        self.ta = {}
        if not cf:
            return
        us = (cf.get("facts") or {}).get("us-gaap") or {}
        for con in CONCEPTS:
            for pr, tag in enumerate(TAGS[con]):
                for f in ((us.get(tag) or {}).get("units") or {}).get("USD", ()):
                    if "start" not in f or f.get("filed", "9999") > end:
                        continue
                    cls = dur_class(f["start"], f["end"])
                    if cls is None:
                        continue
                    self.flows[con].setdefault(dn(f["end"]), []).append(
                        (dn(f["filed"]), f["accn"], -pr, dn(f["start"]), cls, float(f["val"])))
        for f in ((us.get("Assets") or {}).get("units") or {}).get("USD", ()):
            if "start" in f or f.get("filed", "9999") > end:
                continue
            self.ta.setdefault(dn(f["end"]), []).append((dn(f["filed"]), f["accn"], 0, None, 0, float(f["val"])))

    @staticmethod
    def _near(by, e, tol):
        out = []
        for k in range(e - tol, e + tol + 1):
            out.extend(by.get(k, ()))
        return out

    def relevant(self, con, p):
        """Facts that can enter the as-known quarterly value of p (ending near p, or prior year-to-date pieces)."""
        by = self.flows[con]
        out = self._near(by, p, END_TOL)
        for e in range(p - PRIOR_END[1], p - PRIOR_END[0] + 1):
            out.extend(by.get(e, ()))
        return out

    def q_known(self, con, p, d):
        """Quarterly value of period p as known on day d (facts filed <= d), or None."""
        by = self.flows[con]
        cur = [x for x in self._near(by, p, END_TOL) if x[0] <= d]
        direct = [x for x in cur if x[4] == 1]
        if direct:
            return max(direct)[5]
        for cls in (4, 3, 2):
            c = [x for x in cur if x[4] == cls]
            if not c:
                continue
            x = max(c)
            prior = []
            for e in range(p - PRIOR_END[1], p - PRIOR_END[0] + 1):
                prior.extend(y for y in by.get(e, ()) if y[0] <= d and y[4] == cls - 1 and abs(y[3] - x[3]) <= END_TOL)
            return None if not prior else x[5] - max(prior)[5]
        return None

    def ta_known(self, p, d):
        c = [x for x in self._near(self.ta, p, TA_TOL) if x[0] <= d]
        return max(c)[5] if c else None


def timeline(values):
    """[(day, value)] in day order -> kept [(day, value)] (first = original; later = restated, > STORE_TOL apart)."""
    kept = []
    for d, v in values:
        if v is None:
            continue
        if not kept or all((abs(v / w - 1.0) > STORE_TOL) if w else (v != w) for _, w in kept):
            kept.append((d, v))
    return kept


def field_timeline(facts: Facts, field: str, p: int):
    if field == "total_assets":
        rel = Facts._near(facts.ta, p, TA_TOL)
        days = sorted({x[0] for x in rel})
        return timeline([(d, facts.ta_known(p, d)) for d in days])
    con = field[:-2]
    days = sorted({x[0] for x in facts.relevant(con, p)})
    return timeline([(d, facts.q_known(con, p, d)) for d in days])


def guard_rows(facts: Facts, periods):
    """[(p, field index, filed - p, g4 restated value)] for every restated value of every period / field."""
    out = []
    for p in sorted(periods):
        for fi, f in enumerate(FIELDS):
            tl = field_timeline(facts, f, p)
            for d, v in tl[1:]:
                c = g4(v)
                if c:
                    out.append((p, fi, d - p, c))
    return out


def columnar(rows_by_cik):
    """{cik: [(p, fi, off, g4)]} -> 5 delta-coded columns (cik delta, period delta reset per registrant, field,
    offset, value)."""
    C = [[], [], [], [], []]
    pc = 0
    for cik in sorted(rows_by_cik, key=int):
        pp = 0
        for p, fi, off, v in rows_by_cik[cik]:
            C[0].append(int(cik) - pc)
            pc = int(cik)
            C[1].append(p - pp)
            pp = p
            C[2].append(fi)
            C[3].append(off)
            C[4].append(v)
    return C


def decolumnar(C):
    out, cik, p = {}, 0, 0
    for dc, dp, fi, off, v in zip(*C):
        if dc:
            cik += dc
            p = 0
        p += dp
        out.setdefault(str(cik), {}).setdefault(p, []).append((fi, off, v))
    return out


def raw_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def pack_parts(obj, prefix: str, chunk: int = CHUNK):
    """lzma + base85 parts '<prefix>_NN.py' (DATA string) with NO loader file; returns (files, sha256 of raw)."""
    raw = raw_bytes(obj)
    txt = base64.b85encode(lzma.compress(raw, preset=9 | lzma.PRESET_EXTREME)).decode()
    parts = [txt[i:i + chunk] for i in range(0, len(txt), chunk)] or [""]
    files = {f"{prefix}_{i:02d}.py": f'# generated (Data v3, D229) - do not edit\nDATA = "{p}"\n'
             for i, p in enumerate(parts)}
    return files, hashlib.sha256(raw).hexdigest()


def unpack_parts(files: dict, prefix: str):
    n = len([k for k in files if k.startswith(prefix + "_")])
    s = "".join(files[f"{prefix}_{i:02d}.py"].split('DATA = "')[1].rsplit('"', 1)[0] for i in range(n))
    return json.loads(lzma.decompress(base64.b85decode(s)))


# ----------------------------------------------------------------------------------------------- calendar
def easter(y):
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    return date(y, (h + l_ - 7 * m + 114) // 31, (h + l_ - 7 * m + 114) % 31 + 1)


def month_end_session(y, m):
    """Last NYSE session of a month (weekday, not Good Friday, not Memorial Day; the only holidays that can fall on a
    month's last weekday 2011-2021). Checked against every committed review date (P14-CP2)."""
    d = date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)
    gf = easter(y) - timedelta(days=2)
    while True:
        memorial = d.month == 5 and d.weekday() == 0 and (d + timedelta(days=7)).month == 6
        if d.weekday() < 5 and d != gf and not memorial:
            return d
        d -= timedelta(days=1)


def review_days():
    """The 131 reviews 2011-01 .. 2021-11 and their selection days (calendar day after the session)."""
    out = []
    for y in range(2011, 2022):
        for m in range(1, 13):
            if (y, m) > (2021, 11):
                break
            t = month_end_session(y, m)
            out.append((t, t + timedelta(days=1)))
    return out


# ----------------------------------------------------------------------------------------------- SEC-side signals
def originals(cols):
    """Data v2.1 filing-table columns of one registrant -> {period day: earliest original 10-Q / 10-K filing day}."""
    out, pe = {}, 0
    for i in range(len(cols[0])):
        pe += cols[0][i]
        if cols[2][i] in (1, 2):
            fd = pe + cols[1][i]
            out[pe] = min(out.get(pe, fd), fd)
    return out


def chain_back(periods, i0, n):
    if i0 - n + 1 < 0:
        return None
    seg = periods[i0 - n + 1:i0 + 1]
    for a, b in zip(seg, seg[1:]):
        if not (GAP[0] <= b - a <= GAP[1]):
            return None
    return seg[::-1]                 # p0, p1, ...


def sec_signals(facts: Facts, orig: dict, D: int, values_asof=None):
    """(anchor period day or None, {signal: value or None}, {raw: value or None}) as known on decision day D (facts
    filed <= D - 1). values_asof (descriptive restatement study): read values as known on that day instead, with the
    anchor and chain still decided on D."""
    vd = D - 1 if values_asof is None else values_asof
    vis = sorted(p for p, fd in orig.items() if fd + 1 <= D)
    none = ({s: None for s in SIGNALS}, {r: None for r in RAW})
    if not vis or D - vis[-1] > MAX_AGE:
        return (None,) + none
    i0 = len(vis) - 1
    p0 = vis[i0]
    q = {}

    def Q(con, p):
        k = (con, p)
        if k not in q:
            q[k] = facts.q_known(con, p, vd)
        return q[k]

    def ttm(con, ps):
        vals = [Q(con, p) for p in ps]
        return None if any(v is None for v in vals) else sum(vals)

    sig, raw = {}, {}
    c6 = chain_back(vis, i0, 6)
    if c6:
        r = [Q("revenue", c6[k]) for k in (0, 1, 4, 5)]
        sig["F1"] = None if any(v is None or v <= 0 for v in r) else (r[0] / r[2] - 1.0) - (r[1] / r[3] - 1.0)
    else:
        sig["F1"] = None
    c8 = chain_back(vis, i0, 8)
    T = {}
    if c8:
        for con in CONCEPTS:
            T[(con, 0)], T[(con, 4)] = ttm(con, c8[0:4]), ttm(con, c8[4:8])
        ta0, ta4 = facts.ta_known(c8[0], vd), facts.ta_known(c8[4], vd)
    else:
        ta0 = ta4 = None

    def ratio_change(num, den0, den4):
        a0, a4 = T.get((num, 0)), T.get((num, 4))
        if None in (a0, a4, den0, den4) or den0 <= 0 or den4 <= 0:
            return None
        return a0 / den0 - a4 / den4

    R0, R4 = T.get(("revenue", 0)), T.get(("revenue", 4))
    sig["F2"] = ratio_change("gross_profit", R0, R4) if c8 else None
    sig["F4"] = ratio_change("operating_cash_flow", ta0, ta4) if c8 else None
    sig["F5"] = ratio_change("net_income", ta0, ta4) if c8 else None
    sig["F8"] = ratio_change("revenue", ta0, ta4) if c8 else None
    c4 = chain_back(vis, i0, 4)
    raw["rq0"] = Q("revenue", p0)
    for key, con in (("R0", "revenue"), ("GP0", "gross_profit"), ("NI0", "net_income"), ("OCF0", "operating_cash_flow")):
        raw[key] = ttm(con, c4) if c4 else None
    raw["TA0"] = facts.ta_known(p0, vd)
    return p0, sig, raw


def sample_key(cik) -> str:
    return hashlib.sha256(f"P14CP2-SEC-sample|{int(cik)}".encode()).hexdigest()
