# qr_v3.py — DATA v3 (owner D229; research/phase14/data_v3/DATA_V3_spec.md): the guard-v3 rule, the H029 v3 view, the
# six H029 signal constructions, and the aggregate-only SEC validation / F7 split-comparability statistics. Pure
# Python + numpy (no QuantConnect imports); unit-tested offline (tests/test_p14_qr_v3.py) and uploaded next to the
# frozen Data v2.1 host X801 (qr_x801), whose store and rules it never changes:
#   * guard v3 (spec 4): a fed vendor version is BLOCKED for H029 when a guarded field matches (0.5%) a restated SEC
#     value that was not yet public on the version's first-seen day and no restated value public by then;
#   * V3Overlay (spec 4.3): H029's view of a security = the v2.1 store's visible history with every v3-blocked
#     version replaced by the latest earlier clean visible version of its period (or removed); the v2.1 store, and so
#     H028, is untouched;
#   * signals (spec 5): F1 same-quarter YoY revenue acceleration, F2 TTM gross-margin change, F4 TTM OCF / assets
#     change, F5 TTM ROA change, F7 SEC cover-count dilution (inverted; corruption bounds), F8 TTM asset-turnover change
#     -- the frozen qr_h029a Window / True-TTM rules; F3 and F6 do not exist here.
import base64
import hashlib
import importlib
import json
import lzma
import math
from datetime import date, timedelta

import numpy as np

import qr_h029a as Z

EPOCH = date(2000, 1, 1)
GUARD_PREFIX, VAL_PREFIX = "qr_data_v3", "qr_v3val"
GFIELDS = ("revenue_q", "gross_profit_q", "net_income_q", "operating_cash_flow_q", "total_assets")
MATCH_TOL = 0.005
SIGNALS = ("F1", "F2", "F4", "F5", "F7", "F8")
SEC_SIGNALS = ("F1", "F2", "F4", "F5", "F8")
RAW = ("rq0", "R0", "GP0", "NI0", "OCF0", "TA0")
MIN_SIGNALS = 5
F7_BOUNDS = (0.1, 10.0)
CATS = ("no_restatement", "restated_known", "blocked_future", "unmatched")
PERIODS = (("2011-2014", 2011, 2014), ("2015-2017", 2015, 2017), ("2018-2021", 2018, 2021))
MATERIAL = 0.20
DISAGREE = math.log(1.10)


def dn(d):
    return (d - EPOCH).days


def dd(n):
    return EPOCH + timedelta(days=int(n))


def ug4(c):
    if not c:
        return 0.0
    a = abs(int(c))
    return (-1 if c < 0 else 1) * (a // 100) * 10.0 ** (a % 100 - 3)


def near(x, ref):
    return x is not None and ref is not None and ref != 0 and abs(x / ref - 1.0) <= MATCH_TOL


def load_parts(prefix, sha256):
    """Reassemble '<prefix>_NN' modules (lzma + base85) and verify the SHA-256 of the raw JSON."""
    s, i = [], 0
    while True:
        try:
            s.append(importlib.import_module("%s_%02d" % (prefix, i)).DATA)
        except ImportError:
            break
        i += 1
    raw = lzma.decompress(base64.b85decode("".join(s)))
    if hashlib.sha256(raw).hexdigest() != sha256:
        raise Exception(f"Data v3: packed table {prefix} corrupted or not the pinned one")
    return json.loads(raw), i


# ----------------------------------------------------------------------------------------------- guard v3
class Guard3:
    """The guard-v3 reference: {cik: {SEC period day: [(field index, filed - period days, g4 restated value)]}}."""

    def __init__(self, C):
        self.ref = {}
        cik = p = 0
        n = 0
        for dc, dp, fi, off, v in zip(*C):
            if dc:
                cik += dc
                p = 0
            p += dp
            self.ref.setdefault(str(cik), {}).setdefault(p, []).append((int(fi), int(off), ug4(v)))
            n += 1
        self.n = n

    def rows(self, cik, sec_pe):
        if cik is None or sec_pe is None:
            return None
        return self.ref.get(str(cik), {}).get(int(sec_pe))

    def check(self, cik, sec_pe, vals, today):
        """(blocked, {field: category}) for one vendor version first seen on `today` (a date)."""
        rows = self.rows(cik, sec_pe)
        cats = {}
        if not rows:
            return False, {f: "no_restatement" for f in GFIELDS if vals.get(f) is not None}
        td = dn(today)
        blocked = False
        for fi, f in enumerate(GFIELDS):
            v = vals.get(f)
            if v is None:
                continue
            mine = [(sec_pe + off, L) for i, off, L in rows if i == fi]
            if not mine:
                cats[f] = "no_restatement"
                continue
            fut = any(near(v, L) for d, L in mine if d + 1 > td)
            known = any(near(v, L) for d, L in mine if d + 1 <= td)
            if fut and not known:
                cats[f] = "blocked_future"
                blocked = True
            elif known:
                cats[f] = "restated_known"
            else:
                cats[f] = "unmatched"
        return blocked, cats


# ----------------------------------------------------------------------------------------------- the v3 view
class V3Overlay:
    """Retains the fed versions of periods that have guard-v3 timelines (the only periods that can hold a v3-blocked
    version) and which of them are blocked. view() never changes the v2.1 store."""

    def __init__(self):
        self.ret = {}          # sid -> {period_end: [Record, ...]} in fed order
        self.blocked = set()   # id(Record) of v3-blocked fed versions
        self.bsids = set()     # securities with at least one blocked version
        self.keep = []         # the blocked Records themselves (their ids stay unique for the run)
        self.check = dict(views=0, changed=0, replaced=0, removed=0, newer_replacement=0)

    def fed(self, sid, rec, retain, blocked):
        if retain or rec.period_end in self.ret.get(sid, {}):
            self.ret.setdefault(sid, {}).setdefault(rec.period_end, []).append(rec)
        if blocked:
            self.blocked.add(id(rec))
            self.keep.append(rec)
            self.bsids.add(sid)

    def view(self, hist, current, sid, today):
        """(history dict, current record) of the v3 view on `today` (spec 4.3); the v2.1 objects themselves when
        nothing differs. `hist` / `current` are the v2.1 store's after record() promoted today's reports. A period
        changes only when its v2.1 record is v3-blocked: it is then replaced by the latest earlier clean visible
        version of the period (ties: later fed), or removed."""
        self.check["views"] += 1
        if sid not in self.bsids:
            return hist, current
        h3 = None
        for pe, recs in self.ret.get(sid, {}).items():
            cur = hist.get(pe)
            if cur is None or id(cur) not in self.blocked:
                continue
            best = None
            for r in recs:
                if r.available <= today and id(r) not in self.blocked and not r.partial and (
                        best is None or r.file_date >= best.file_date):
                    best = r
            if h3 is None:
                h3 = dict(hist)
            if best is None:
                del h3[pe]
                self.check["removed"] += 1
            else:
                h3[pe] = best
                self.check["replaced"] += 1
                self.check["newer_replacement"] += int(best.file_date > cur.file_date)
        if h3 is None:
            return hist, current
        self.check["changed"] += 1
        full = [r for r in h3.values() if not r.partial and r.available <= today]
        cur3 = max(full, key=lambda r: (r.period_end, r.file_date)) if full else None
        return h3, cur3


# ----------------------------------------------------------------------------------------------- H029 signals
def signals(w):
    """{F1, F2, F4, F5, F8: (value or None, reason)} on a qr_h029a.Window of the v3 view (spec 5). F7 is separate."""
    out = {}
    if not w.ok:
        return {f: (None, "no_fresh_report") for f in SEC_SIGNALS}
    sp6, sp8 = w.span(6), w.span(8)
    if sp6 != "ok":
        out["F1"] = (None, sp6)
    else:
        r = [w.q("revenue", k) for k in (0, 1, 4, 5)]
        if any(x is None for x in r):
            out["F1"] = (None, "field_missing")
        elif any(x <= 0 for x in r):
            out["F1"] = (None, "denominator")
        else:
            out["F1"] = ((r[0] / r[2] - 1.0) - (r[1] / r[3] - 1.0), "ok")
    if sp8 != "ok":
        for f in ("F2", "F4", "F5", "F8"):
            out[f] = (None, sp8)
        return out
    T = lambda b, k: w.ttm(b, k)[0]  # noqa: E731
    out["F2"] = Z._ratio_change(T("gross_profit", 0), T("revenue", 0), T("gross_profit", 4), T("revenue", 4))
    t0, t4 = w.snap("total_assets", 0), w.snap("total_assets", 4)
    for f, num in (("F4", "operating_cash_flow"), ("F5", "net_income"), ("F8", "revenue")):
        a0, a4 = T(num, 0), T(num, 4)
        if None in (a0, a4):
            out[f] = (None, "ttm_missing")
        elif t0 is None or t4 is None:
            out[f] = (None, "field_missing")
        else:
            out[f] = Z._ratio_change(a0, t0, a4, t4)
    return out


def vendor_raw(w):
    """Anchor raw values of the v3 view (validation only): quarterly revenue, TTMs, total assets."""
    if not w.ok:
        return None, {k: None for k in RAW}
    raw = dict(rq0=w.q("revenue", 0), TA0=w.snap("total_assets", 0))
    for k, b in (("R0", "revenue"), ("GP0", "gross_profit"), ("NI0", "net_income"), ("OCF0", "operating_cash_flow")):
        raw[k] = w.ttm(b, 0)[0]
    return w.q0.period_end, raw


def f7(filings, splits, today):
    """(oriented F7 or None, reason, S1 cover date or None, latest filing date). The frozen qr_h029a.dilution
    construction (same S0 / S1 choice and D111 split restatement) plus the corruption bounds of spec 5."""
    use = sorted((f for f in filings if f.available <= today and f.shares and f.cover_date is not None),
                 key=lambda x: (x.cover_date, x.filed, x.accn))
    if not use:
        return None, "no_cover_count", None, None
    f0 = use[-1]
    if (today - f0.cover_date).days > Z.SHARE_MAX_AGE:
        return None, "no_cover_count", None, f0.filed
    target = f0.cover_date.toordinal() - Z.YEAR_DAYS
    c = [f for f in use if abs(f.cover_date.toordinal() - target) <= Z.YEAR_TOL]
    if not c:
        return None, "no_prior_count", None, f0.filed
    f1 = min(c, key=lambda x: (abs(x.cover_date.toordinal() - target), -x.filed.toordinal()))

    def prev(f):
        p = [x for x in use if x.cover_date < f.cover_date]
        return max(p, key=lambda x: (x.cover_date, x.filed)) if p else None
    s0, s1 = Z._adjust(f0, prev(f0), splits, today), Z._adjust(f1, prev(f1), splits, today)
    if not (s0 > 0 and s1 > 0):
        return None, "no_cover_count", f1.cover_date, f0.filed
    ratio = s0 / s1
    if not (F7_BOUNDS[0] <= ratio <= F7_BOUNDS[1]):
        return None, "corrupted", f1.cover_date, f0.filed
    return -(ratio - 1.0), "ok", f1.cover_date, f0.filed


# ----------------------------------------------------------------------------------------------- scores
def centred(x):
    """qr_h026.centred_percentile: 2 (average rank - 1)/(n - 1) - 1 over the finite entries (NaN stays NaN)."""
    x = np.asarray(x, float)
    out = np.full(x.size, np.nan)
    ok = np.isfinite(x)
    n = int(ok.sum())
    if n == 1:
        out[ok] = 0.0
    elif n > 1:
        out[ok] = 2.0 * (Z.avg_rank(x[ok]) - 1.0) / (n - 1) - 1.0
    return out


def h029_score(V):
    """(n, 6) oriented signal values (NaN = missing) -> (score, valid count): the mean of the centred percentiles of
    the valid signals, equal weights, at least MIN_SIGNALS of 6 (else NaN). No fitted weight of any kind."""
    V = np.asarray(V, float)
    P = np.column_stack([centred(V[:, j]) for j in range(V.shape[1])]) if V.size else np.zeros((0, 6))
    cnt = np.isfinite(P).sum(1)
    with np.errstate(invalid="ignore"):
        sc = np.where(cnt >= MIN_SIGNALS, np.nansum(P, 1) / np.maximum(cnt, 1), np.nan)
    return sc, cnt


def cdf_mid(others, x):
    """Mid-rank empirical CDF of x among `others` (a sorted finite array): (#< + 0.5 #==) / n."""
    n = others.size
    if n == 0 or x is None or not math.isfinite(x):
        return float("nan")
    lo = int(np.searchsorted(others, x, "left"))
    hi = int(np.searchsorted(others, x, "right"))
    return (lo + 0.5 * (hi - lo)) / n


def raw_class(v, s):
    if v is None or s is None:
        return "missing"
    if s == 0 or v == 0:
        return "zero"
    if (v > 0) != (s > 0):
        return "sign"
    r = abs(v / s - 1.0)
    return "match" if r <= 0.005 else ("minor" if r <= 0.02 else ("moderate" if r <= 0.10 else "major"))


def period_of(year):
    for name, a, b in PERIODS:
        if a <= year <= b:
            return name
    return None


def panel_digest(ids, V):
    h = hashlib.sha256()
    h.update(json.dumps([list(ids), [[None if not math.isfinite(x) else float(f"{x:.12g}") for x in row]
                                     for row in np.asarray(V, float).tolist()]], separators=(",", ":")).encode())
    return h.hexdigest()
