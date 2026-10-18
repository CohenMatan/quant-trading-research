"""Long-horizon Stage C (owner D242): OF-A data and point-in-time feasibility audit.

Implements `LH_StageC_protocol.md` (frozen and committed before this script produced any aggregate). NON-RETURN:
no price, no return, no QuantConnect run; no surprise value, percentile, ranking or predictive statistic is computed.
Offline sources only (cache-only SEC client with networking disabled); every SEC row filed after 2021-12-31 is
dropped at load. Output: aggregates only (counts, shares, quantiles) in LH_StageC_audit.json.

    PYTHONPATH=src python research/longhorizon/stage_c/LH_StageC_audit.py
"""
from __future__ import annotations

import bisect
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase2/sec")]
from qresearch import data_v3 as V3  # noqa: E402
from qresearch.sec_pit import TAGS, dur_class  # noqa: E402

CUT = "2021-12-31"
PROTOCOL = HERE / "LH_StageC_protocol.md"
OUT = HERE / "LH_StageC_audit.json"
M0 = 2010 * 12                         # E981-01 bit 0 = January 2010
PERIODS = (("2011-2014", 2011, 2014), ("2015-2017", 2015, 2017), ("2018-2021", 2018, 2021))
YEARS = tuple(range(2011, 2022))
FLOOR_YEARS = tuple(range(2013, 2022))
FLOOR, FLOOR_MIN = 0.70, 0.60
SENS_FLOORS = (0.60, 0.65, 0.70, 0.75, 0.80)
FRESH_RM2 = 91                          # one-quarter freshness rule (days from availability to D)
TIMELINESS_SESSIONS = 20
DISCOPS_TAGS = ("IncomeLossFromDiscontinuedOperationsNetOfTax",
                "IncomeLossFromDiscontinuedOperationsNetOfTaxAttributableToReportingEntity")
TCJA = (V3.dn("2017-10-01"), V3.dn("2018-01-31"))
CANDS = ("C1", "C2", "C3", "C4_REV", "C4_NI", "C5", "C6")
MISSING_ORDER = ("financial", "no_identity", "no_sic", "no_filing_table", "no_fresh_anchor", "chain_short_or_broken",
                 "value_missing", "invalid_denominator")


# ----------------------------------------------------------------------------------------------- pure helpers
def q_detail(facts: V3.Facts, con: str, p: int, d: int):
    """(value, method, max filed day used) exactly as V3.Facts.q_known (method 'direct' / 'ytd' / None)."""
    by = facts.flows[con]
    cur = [x for x in facts._near(by, p, V3.END_TOL) if x[0] <= d]
    direct = [x for x in cur if x[4] == 1]
    if direct:
        x = max(direct)
        return x[5], "direct", x[0]
    for cls in (4, 3, 2):
        c = [x for x in cur if x[4] == cls]
        if not c:
            continue
        x = max(c)
        prior = []
        for e in range(p - V3.PRIOR_END[1], p - V3.PRIOR_END[0] + 1):
            prior.extend(y for y in by.get(e, ()) if y[0] <= d and y[4] == cls - 1 and abs(y[3] - x[3]) <= V3.END_TOL)
        if not prior:
            return None, None, None
        y = max(prior)
        return x[5] - y[5], "ytd", max(x[0], y[0])
    return None, None, None


def quantiles(xs):
    """n, mean and the protocol quantiles (numpy linear interpolation); None when empty."""
    if not xs:
        return dict(n=0)
    a = np.asarray(xs, float)
    q = np.percentile(a, [10, 25, 50, 75, 90, 95])
    return dict(n=int(a.size), mean=round(float(a.mean()), 3), p10=float(q[0]), p25=float(q[1]), median=float(q[2]),
                p75=float(q[3]), p90=float(q[4]), p95=float(q[5]))


class Sessions:
    def __init__(self, days):
        self.s = sorted(days)

    def after(self, d):
        """First session strictly after date d."""
        i = bisect.bisect_right(self.s, d)
        return self.s[i] if i < len(self.s) else None

    def on_or_after(self, d):
        i = bisect.bisect_left(self.s, d)
        return self.s[i] if i < len(self.s) else None

    def between(self, a, b):
        """Number of sessions s with a < s <= b (negative if b < a)."""
        if b >= a:
            return bisect.bisect_right(self.s, b) - bisect.bisect_right(self.s, a)
        return -(bisect.bisect_right(self.s, a) - bisect.bisect_right(self.s, b))

    def idx(self, d):
        return bisect.bisect_left(self.s, d)


def match_releases(p0: date, fd: date, releases):
    """releases: sorted [(filing date, row)] of 8-K Item 2.02 (filed <= CUT). -> (class, candidates in (p0, fd],
    first release after fd within 10 days or None)."""
    cands = [r for r in releases if p0 < r[0] <= fd]
    after = [r for r in releases if fd < r[0] <= fd + timedelta(days=10)]
    if len(cands) == 1:
        cls = "unambiguous"
    elif len(cands) > 1:
        cls = "ambiguous"
    else:
        cls = "release_after_filing" if after else "no_release_found"
    return cls, cands, (after[0] if after else None)


def disclosure_category(cls, rel_date, rel_time, fd, f_time):
    """Protocol 6.8 categories 1-4."""
    if cls == "not_determinable" or cls == "release_after_filing":
        return 4
    if cls == "no_release_found":
        return 3
    earlier = rel_date < fd or (rel_date == fd and rel_time is not None and f_time is not None and rel_time < f_time)
    unknown_order = rel_date == fd and (rel_time is None or f_time is None)
    if cls == "unambiguous":
        return 1 if earlier else (2 if unknown_order else 4)
    return 2                                            # ambiguous candidates before / on the filing day


def periods_of(y):
    return [name for name, a, b in PERIODS if a <= y <= b]


# ----------------------------------------------------------------------------------------------- loaders
class _NoNet:
    def get(self, *a, **k):
        raise RuntimeError("network disabled for the Stage C audit (cache-only)")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_universe():
    from e970_parse import lines
    U = {}
    for ln in lines("E981-01"):
        if not ln.startswith("U|"):
            continue
        _, sid, vcik, ccik, corr, tk, mask, first, last, last_seen = ln.split("|")
        months = {M0 + i for i in range(144) if (int(mask, 16) >> i) & 1}
        ciks = [int(x) for x in ccik.split(",") if x] if corr == "1" and ccik else ([int(vcik)] if vcik.isdigit() else [])
        U[sid] = dict(months=months, ciks=ciks)
    return U


def load_sessions():
    rows = gzip.open(ROOT / "experiments/E981-01/equity.csv.gz").read().decode().splitlines()[1:]
    return Sessions([date.fromisoformat(r.split(",")[0]) for r in rows] + [date(2022, 1, 3)])


class Ident:
    def __init__(self, t):
        self.rows = {s: sorted(r) for s, r in t["sec_v1"]["sic_history"].items()}
        self.ext = t["ext"]

    def at(self, sid, D):
        """(cik str or None, sic int or None, source) as known on day-number D."""
        best = None
        for day, sic, cik in self.rows.get(sid, ()):
            if day <= D:
                best = (sic, cik)
            else:
                break
        if best is not None and best[1] not in (None, ""):
            return str(int(best[1])), (int(best[0]) if best[0] not in (None, "") else None), "v2"
        e = self.ext.get(sid)
        if e is not None and D >= e[0]:
            return str(int(e[1])), None, "ext"
        return None, None, None


def load_submissions(client, cik, conv):
    """Cache-only submissions of one CIK, filed <= CUT: (periodic rows, 8-K Item 2.02 rows) or None."""
    from qresearch.sec_edgar import filings_table
    from qresearch.sec_events import acceptance_et
    try:
        sub = client.submissions(int(cik))
    except RuntimeError:
        return None
    if sub is None:
        return None
    tz = conv.get(int(cik), "UNMEASURED")
    per, rel = [], []
    for r in filings_table(sub):
        fdate = r.get("filingDate") or ""
        if not fdate or fdate > CUT:                     # protocol 1.2: dropped at load
            continue
        t = acceptance_et(r.get("acceptanceDateTime"), tz) if tz in ("UTC", "ET") else None
        f = r.get("form")
        if f in ("10-Q", "10-K", "10-KT"):
            per.append((date.fromisoformat(fdate), r.get("reportDate") or "", t))
        elif f == "8-K" and "2.02" in [x.strip() for x in str(r.get("items") or "").split(",")]:
            rel.append((date.fromisoformat(fdate), dict(t=t, xbrl_numeric=int(r.get("isXBRLNumeric") or 0))))
    rel.sort(key=lambda x: (x[0], str(x[1]["t"])))
    return per, rel


def load_fye():
    """(cik, period day) -> fiscal-year-end code from the XBRL filing index (original 10-Q / 10-K, filed <= CUT)."""
    xb = json.load(gzip.open(ROOT / "data/sec_derived/xbrl_filings.json.gz"))
    out, codes = defaultdict(dict), defaultdict(set)
    for r in xb:
        if r.get("form") not in ("10-Q", "10-K") or not r.get("filed") or r["filed"] > CUT or not r.get("period"):
            continue
        pr = r["period"]
        try:
            p = V3.dn(f"{pr[:4]}-{pr[4:6]}-{pr[6:8]}")
        except ValueError:
            continue
        if r.get("fye"):
            out[str(int(r["cik"]))][p] = r["fye"]
            codes[str(int(r["cik"]))].add(r["fye"])
    return out, codes


def fye_at(fmap, cik, p):
    m = fmap.get(cik)
    if not m:
        return None
    for k in range(0, 8):
        for q in (p - k, p + k):
            if q in m:
                return m[q]
    return None


# ----------------------------------------------------------------------------------------------- accumulators
class Rate:
    """Numerator / denominator by year and period."""

    def __init__(self):
        self.n, self.d = Counter(), Counter()

    def add(self, year, ok):
        self.d[year] += 1
        if ok:
            self.n[year] += 1

    def out(self):
        res = {"by_year": {str(y): (round(self.n[y] / self.d[y], 4) if self.d[y] else None) for y in YEARS},
               "denominator_by_year": {str(y): self.d[y] for y in YEARS}}
        for name, a, b in PERIODS:
            n = sum(self.n[y] for y in range(a, b + 1))
            d = sum(self.d[y] for y in range(a, b + 1))
            res[name] = round(n / d, 4) if d else None
        n, d = sum(self.n.values()), sum(self.d.values())
        res["all"] = round(n / d, 4) if d else None
        return res


def share(c, k, tot):
    return round(c[k] / tot, 4) if tot else None


# ----------------------------------------------------------------------------------------------- main audit
def main():
    from qr_data_v21 import load_table
    from qr_xs_diag import ff12
    from qresearch.sec_edgar import SECClient
    t = load_table()
    ident = Ident(t)
    U = load_universe()
    S = load_sessions()
    revs = []
    for T, D in V3.review_days():
        trade = S.after(T)
        revs.append(dict(T=T, D=D, Dn=V3.dn(str(D)), trade=trade, m=T.year * 12 + T.month - 1 + 1, year=T.year))
    conv = {int(k): v["convention"] for k, v in
            json.loads((ROOT / "research/phase2/earnings_audit/tz_conventions.json").read_text())["ciks"].items()}
    client = SECClient(cache_dir=ROOT / "data/sec_cache", user_agent="offline-audit", session=_NoNet())
    fmap, fcodes = load_fye()

    # ---- stock-months -> registrant (identity at D), grouped by CIK
    sm_all, sm_nf = Rate(), Rate()
    ident_cov, ident_src = Rate(), Counter()
    reason_all = {c: Counter() for c in CANDS}
    by_cik = defaultdict(list)                 # cik -> [(sid, review index)]
    e981_agree = Counter()
    nf_rows = []                               # (sid, j, cik or None, sic, reason or None)
    for sid, u in U.items():
        for j, r in enumerate(revs):
            if r["m"] not in u["months"]:
                continue
            cik, sic, src = ident.at(sid, r["Dn"])
            ident_cov.add(r["year"], cik is not None)
            ident_src[src or "none"] += 1
            if cik is not None:
                e981_agree["agree" if int(cik) in u["ciks"] else ("differ" if u["ciks"] else "e981_no_cik")] += 1
            fin = sic is not None and 6000 <= sic <= 6999
            sm_all.add(r["year"], True)
            if fin:
                continue
            reason = None if cik is not None and sic is not None else ("no_identity" if cik is None else "no_sic")
            nf_rows.append((sid, j, cik, sic, reason))
            if reason is None:
                by_cik[cik].append((sid, j, sic, reason))
    first_m = {sid: min(u["months"]) for sid, u in U.items() if u["months"]}
    last_m = {sid: max(u["months"]) for sid, u in U.items() if u["months"]}
    DEC21 = 2021 * 12 + 11

    # ---- per-stock-month results
    cand = {c: Rate() for c in CANDS}
    cand_sens = {k: Rate() for k in ("C1_chain9", "C1_chain17", "C2_chain9", "C2_chain17", "C1_allow2missing",
                                     "C2_allow2missing", "C3_noncontiguous", "C5_noncontiguous", "C4_TA_addon")}
    sec_comp = {c: defaultdict(set) for c in CANDS}          # company coverage: period -> sids covered
    sec_seen = defaultdict(set)                               # period -> sids in U_NF
    sec_months = defaultdict(Counter)                         # (sid, period) -> [n, complete C1, C2]
    field_anchor = {f: Rate() for f in ("revenue", "net_income", "gross_profit")}
    field_chain = {(f, k): Rate() for f in ("revenue", "net_income", "gross_profit") for k in (1, 5, 6, 9, 13, 17)}
    field_span = {f: [None, None] for f in ("revenue", "net_income", "gross_profit")}
    q4 = {f: Counter() for f in ("revenue", "net_income", "gross_profit")}
    anchor_any, fresh200, stale91 = Rate(), Counter(), Counter()
    pit_viol, pit_checked = 0, 0
    chain_fye = {c: Counter() for c in CANDS}
    vintage = {c: Counter() for c in ("C1", "C2")}
    noncomp = Counter()
    surv = {c: defaultdict(Counter) for c in ("C1", "C2", "C3", "C5")}
    events = {}                                               # (cik, p0) -> first use dict
    sm_records = []                                            # (j, sid, TA, sic, oks, leaver, newcomer, amend/late)
    gaps = Counter()
    cache_missing = Counter()
    amend_late = {}
    nf_total = len(nf_rows)
    for sid, j, cik, sic, reason in nf_rows:
        if reason is not None:
            y = revs[j]["year"]
            sm_nf.add(y, True)
            for c in CANDS:
                cand[c].add(y, False)
                reason_all[c][reason] += 1
            for k in cand_sens:
                cand_sens[k].add(y, False)
            for f in field_anchor:
                field_anchor[f].add(y, False)
                for k in (1, 5, 6, 9, 13, 17):
                    field_chain[(f, k)].add(y, False)
            anchor_any.add(y, False)
            for name in periods_of(y):
                sec_seen[name].add(sid)
                sec_months[(sid, name)]["n"] += 1
            sm_records.append((j, sid, None, sic, {}, sid in last_m and last_m[sid] < DEC21,
                               first_m.get(sid, 0) > M0 + 12 and revs[j]["m"] - first_m[sid] < 12, None))
    for ci, (cik, items) in enumerate(sorted(by_cik.items(), key=lambda kv: int(kv[0]))):
        cols = t["f"].get(cik)
        cf = None
        try:
            cf = client.companyfacts(int(cik))
        except RuntimeError:
            cf = None
        if cf is None:
            cache_missing["companyfacts"] += 1
        fx = V3.Facts(cf) if cf else V3.Facts({})
        orig = V3.originals(cols) if cols else {}
        pers = sorted(orig)
        for a, b in zip(pers, pers[1:]):
            if V3.dn("2009-01-01") <= a <= V3.dn(CUT):
                g = b - a
                gaps["all"] += 1
                if not (V3.GAP[0] <= g <= V3.GAP[1]):
                    gaps["outside_80_100"] += 1
                if 95 <= g <= 100:
                    gaps["14_week_95_100"] += 1
        if cols:
            pe, al = 0, False
            per_codes = defaultdict(set)
            for i in range(len(cols[0])):
                pe += cols[0][i]
                per_codes[pe].add((cols[2][i], cols[1][i]))
            for p, rows in per_codes.items():
                origs = [off for code, off in rows if code in (1, 2)]
                if not origs or min(origs) > 90:
                    al = True
            amend_late[cik] = al
        memo, tl_memo, disc_idx = {}, {}, None
        us = ((cf or {}).get("facts") or {}).get("us-gaap") or {}
        disc = defaultdict(list)
        for tag in DISCOPS_TAGS:
            for f in ((us.get(tag) or {}).get("units") or {}).get("USD", ()):
                if f.get("filed", "9999") <= CUT and f.get("val"):
                    disc[V3.dn(f["end"])].append(V3.dn(f["filed"]))

        def Q(con, p, vd):
            k = (con, p, vd)
            if k not in memo:
                memo[k] = q_detail(fx, con, p, vd)
            return memo[k]

        def first_last(field, p):
            k = (field, p)
            if k not in tl_memo:
                tl_memo[k] = V3.field_timeline(fx, field, p)
            return tl_memo[k]

        for sid, j, sic, _reason in items:
            r = revs[j]
            y, D = r["year"], r["Dn"]
            vd = D - 1
            sm_nf.add(y, True)
            for name in periods_of(y):
                sec_seen[name].add(sid)
                sec_months[(sid, name)]["n"] += 1
            vis = sorted(p for p, fd in orig.items() if fd + 1 <= D)
            res = {}
            if not cols:
                rsn = "no_filing_table"
            elif not vis:
                rsn = "no_fresh_anchor"
            else:
                rsn = None
            if vis:
                p_last = vis[-1]
                anchor_any.add(y, D - p_last <= V3.MAX_AGE)
                fresh200["with_visible"] += 1
                if D - p_last > V3.MAX_AGE:
                    fresh200["stale_200"] += 1
                if D - (orig[p_last] + 1) > FRESH_RM2:
                    stale91["stale_91"] += 1
                stale91["with_visible"] += 1
                if D - p_last > V3.MAX_AGE:
                    rsn = "no_fresh_anchor"
            else:
                anchor_any.add(y, False)
            if rsn is not None:
                for c in CANDS:
                    cand[c].add(y, False)
                    reason_all[c][rsn] += 1
                for k in cand_sens:
                    cand_sens[k].add(y, False)
                for f in field_anchor:
                    field_anchor[f].add(y, False)
                    for k in (1, 5, 6, 9, 13, 17):
                        field_chain[(f, k)].add(y, False)
                sm_records.append((j, sid, None, sic, {}, sid in last_m and last_m[sid] < DEC21,
                                   first_m.get(sid, 0) > M0 + 12 and r["m"] - first_m[sid] < 12, amend_late.get(cik)))
                continue
            i0 = len(vis) - 1
            p0 = vis[i0]
            chains = {n: V3.chain_back(vis, i0, n) for n in (1, 5, 6, 9, 13, 17)}

            def vals(con, ps):
                out = []
                for p in ps:
                    v, m, mf = Q(con, p, vd)
                    nonlocal_check(mf)
                    out.append(v)
                return out
            used_max = [None]

            def nonlocal_check(mf):
                if mf is not None:
                    used_max[0] = mf if used_max[0] is None else max(used_max[0], mf)

            # field-level coverage
            for f, con in (("revenue", "revenue"), ("net_income", "net_income"), ("gross_profit", "gross_profit")):
                v0, m0, _ = Q(con, p0, vd)
                field_anchor[f].add(y, v0 is not None)
                if v0 is not None:
                    q4[f]["known"] += 1
                    if m0 == "ytd":
                        q4[f]["ytd"] += 1
                    lo, hi = field_span[f]
                    field_span[f] = [p0 if lo is None else min(lo, p0), p0 if hi is None else max(hi, p0)]
                for k in (1, 5, 6, 9, 13, 17):
                    ch = chains[k]
                    field_chain[(f, k)].add(y, bool(ch) and all(v is not None for v in vals(con, ch)))
            c13, c5, c6, c9, c17 = chains[13], chains[5], chains[6], chains[9], chains[17]
            ni13 = vals("net_income", c13) if c13 else None
            rv13 = vals("revenue", c13) if c13 else None
            ok = {}

            def judge(name, chain, vlist, extra_ok=True):
                if not chain:
                    reason_all[name]["chain_short_or_broken"] += 1
                    return False
                if any(v is None for v in vlist):
                    reason_all[name]["value_missing"] += 1
                    return False
                if not extra_ok:
                    reason_all[name]["invalid_denominator"] += 1
                    return False
                return True
            ok["C1"] = judge("C1", c13, ni13 or [])
            ok["C2"] = judge("C2", c13, rv13 or [])
            ni5 = vals("net_income", [c5[0], c5[4]]) if c5 else []
            ok["C3"] = judge("C3", c5, ni5)
            rv6 = vals("revenue", [c6[0], c6[1], c6[4], c6[5]]) if c6 else []
            ni6 = vals("net_income", [c6[0], c6[1], c6[4], c6[5]]) if c6 else []
            ok["C4_REV"] = judge("C4_REV", c6, rv6)
            ok["C4_NI"] = judge("C4_NI", c6, ni6)
            gp5 = vals("gross_profit", [c5[0], c5[4]]) if c5 else []
            ta4 = fx.ta_known(c5[4], vd) if c5 else None
            ok["C5"] = judge("C5", c5, gp5 + [ta4], extra_ok=(ta4 is not None and ta4 > 0))
            ok["C6"] = ok["C1"] and ok["C2"]
            if not ok["C6"]:
                reason_all["C6"]["chain_short_or_broken" if not c13 else "value_missing"] += 1
            for c in CANDS:
                cand[c].add(y, ok[c])
                if ok[c]:
                    for name in periods_of(y):
                        sec_comp[c][name].add(sid)
            for name in periods_of(y):
                sec_months[(sid, name)]["C1"] += ok["C1"]
                sec_months[(sid, name)]["C2"] += ok["C2"]
            # sensitivities (descriptive)
            for con, key in (("net_income", "C1"), ("revenue", "C2")):
                for n in (9, 17):
                    ch = chains[n]
                    cand_sens[f"{key}_chain{n}"].add(y, bool(ch) and all(v is not None for v in vals(con, ch)))
                cand_sens[f"{key}_allow2missing"].add(y, bool(c13) and sum(v is None for v in vals(con, c13)) <= 2)
            q4cand = [p for p in vis[:i0] if 350 <= p0 - p <= 380]
            nc_ni = bool(q4cand) and all(v is not None for v in vals("net_income", [p0, q4cand[-1]]))
            nc_gp = bool(q4cand) and all(v is not None for v in vals("gross_profit", [p0, q4cand[-1]]))
            nc_ta = fx.ta_known(q4cand[-1], vd) if q4cand else None
            cand_sens["C3_noncontiguous"].add(y, nc_ni)
            cand_sens["C5_noncontiguous"].add(y, nc_gp and nc_ta is not None and nc_ta > 0)
            ta4c6 = fx.ta_known(c6[4], vd) if c6 else None
            cand_sens["C4_TA_addon"].add(y, ok["C4_REV"] and ta4c6 is not None and ta4c6 > 0)
            # PIT assertion: every used fact filed before D
            pit_checked += 1
            if used_max[0] is not None and used_max[0] >= D:
                pit_viol += 1
            # chain integrity: fiscal-year-end codes of q0 vs its comparison quarters, each candidate's own chain
            for c in CANDS:
                if not ok[c]:
                    continue
                ch, pos = (c13, (0, 4, 12)) if c in ("C1", "C2", "C6") else ((c6, (0, 4, 1, 5)) if c.startswith("C4")
                                                                            else (c5, (0, 4)))
                codes = [fye_at(fmap, cik, ch[k]) for k in pos]
                if any(x is None for x in codes):
                    chain_fye[c]["codes_missing"] += 1
                else:
                    chain_fye[c]["with_codes"] += 1
                    chain_fye[c]["changed"] += len(set(codes)) > 1
            # vintage on complete C1 / C2 chains
            for c, con, fld in (("C1", "net_income", "net_income_q"), ("C2", "revenue", "revenue_q")):
                if not ok[c]:
                    continue
                recast = later = False
                for p in c13:
                    tl = first_last(fld, p)
                    if len(tl) > 1:
                        if any(dd <= vd for dd, _ in tl[1:]):
                            recast = True
                        if any(dd > vd for dd, _ in tl[1:]):
                            later = True
                vintage[c]["complete"] += 1
                vintage[c]["recast_known_by_D"] += recast
                vintage[c]["later_restated_after_D"] += later
                if any(TCJA[0] <= p <= TCJA[1] for p in c13):
                    noncomp[f"{c}_chain_contains_tax_reform_quarter"] += 1
                if c == "C1" and any(v is not None and v <= 0 for v in ni13):
                    noncomp["C1_chain_any_NI_le_0"] += 1
            v0 = Q("net_income", p0, vd)[0]
            if v0 is not None:
                noncomp["anchor_NI_known"] += 1
                noncomp["anchor_NI_le_0"] += v0 <= 0
                hit = any(fdn <= vd for e in range(p0 - 7, p0 + 8) for fdn in disc.get(e, ()))
                noncomp["anchor_discontinued_ops_fact"] += hit
            # survivorship records
            ta0 = fx.ta_known(p0, vd)
            sm_records.append((j, sid, ta0, sic, {c: ok[c] for c in ("C1", "C2", "C3", "C5")},
                               sid in last_m and last_m[sid] < DEC21,
                               first_m.get(sid, 0) > M0 + 12 and r["m"] - first_m[sid] < 12, amend_late.get(cik)))
            # events (first use while eligible)
            key = (cik, p0)
            if key not in events:
                events[key] = dict(cik=cik, p0=p0, fd=orig[p0], j=j)
            else:
                events[key]["j"] = min(events[key]["j"], j)
        if ci % 250 == 0:
            print("registrants", ci, len(by_cik), flush=True)

    # ---- survivorship splits
    by_rev = defaultdict(list)
    for rec in sm_records:
        if rec[2] is not None:
            by_rev[rec[0]].append(rec[2])
    cuts = {j: (np.percentile(v, [100 / 3, 200 / 3]) if len(v) >= 3 else None) for j, v in by_rev.items()}
    for j, sid, ta0, sic, oks, leaver, newcomer, al in sm_records:
        if ta0 is None or cuts.get(j) is None:
            size = "size:unknown"
        else:
            a, b = cuts[j]
            size = "size:T1_small" if ta0 <= a else ("size:T2" if ta0 <= b else "size:T3_large")
        groups = [size, f"ff12:{ff12(sic)}" if sic is not None else "ff12:unknown",
                  "leaver" if leaver else "stayer", "newcomer_first12m" if newcomer else "not_newcomer",
                  "amendment_or_late_filer" if al else "regular_filer"]
        for c in ("C1", "C2", "C3", "C5"):
            for g in groups:
                surv[c][g]["n"] += 1
                surv[c][g]["complete"] += bool(oks.get(c))

    # ---- events: release matching and delays
    ev_stats = defaultdict(list)
    ev_cnt = Counter()
    cat = Counter()
    within = Counter()
    sub_cache = {}
    last_sel = revs[-1]["D"]
    for key, e in sorted(events.items(), key=lambda kv: (int(kv[0][0]), kv[0][1])):
        cik, p0 = e["cik"], V3.dd(e["p0"])
        fd = V3.dd(e["fd"])
        A = fd + timedelta(days=1)
        ev_cnt["events"] += 1
        first_rev = next((k for k, r in enumerate(revs) if r["D"] >= A), None)
        timely = first_rev is not None and first_rev == e["j"]
        if first_rev is None:
            ev_cnt["after_last_review"] += 1
        ev_cnt["first_use_timely"] += timely
        if cik not in sub_cache:
            sub_cache[cik] = load_submissions(client, cik, conv)
        sub = sub_cache[cik]
        if sub is None:
            ev_cnt["not_determinable_no_submissions"] += 1
            cat[4] += 1
            continue
        per, rel = sub
        f_rows = [x for x in per if x[0] == fd and x[1] and abs(V3.dn(x[1]) - e["p0"]) <= 7]
        f_time = f_rows[0][2] if f_rows else None
        ev_cnt["periodic_row_matched"] += bool(f_rows)
        cls, cands, after = match_releases(p0, fd, rel)
        ev_cnt[f"match:{cls}"] += 1
        rd = rt = None
        if cands:
            rd, info = cands[0]
            rt = info["t"]
            ev_cnt["matched_release_xbrl_numeric"] += info["xbrl_numeric"]
            ev_cnt["matched_release_n"] += 1
        c = disclosure_category(cls, rd, rt, fd, f_time)
        cat[c] += 1
        year = A.year
        tag = cls if cls in ("unambiguous", "ambiguous") else None
        if tag:
            ev_stats[f"{tag}:A_days"].append((rd - p0).days)
            ev_stats[f"{tag}:A_sessions"].append(S.between(p0, rd))
            ev_stats[f"{tag}:B_days"].append((fd - rd).days)
            ev_stats[f"{tag}:B_sessions"].append(S.between(rd, fd))
            if rd == fd:
                ev_cnt[f"{tag}:same_day"] += 1
                if rt is not None and f_time is not None:
                    ev_cnt[f"{tag}:same_day_release_first" if rt < f_time else f"{tag}:same_day_filing_first"] += 1
                else:
                    ev_cnt[f"{tag}:same_day_unknown_order"] += 1
            e1 = S.idx(S.after(fd)) - S.idx(S.after(rd))
            ev_stats[f"{tag}:E1_sessions_from_release_trade"].append(e1)
            ev_stats[f"{tag}:E1_sessions_from_release_date"].append(S.between(rd, S.after(fd)))
            if tag == "unambiguous":
                ev_stats[f"by_year:{year}:B_days"].append((fd - rd).days)
        if first_rev is not None and timely:
            rv = revs[first_rev]
            s0 = S.on_or_after(A)
            wait_sessions = S.idx(rv["trade"]) - S.idx(s0)
            ev_stats["D_days"].append((rv["D"] - A).days)
            ev_stats["D_sessions"].append(wait_sessions)
            for k in (5, 10, 20, 30):
                within[k] += wait_sessions <= k
            within["n"] += 1
            ev_stats[f"by_year:{year}:D_sessions"].append(wait_sessions)
            if tag:
                ev_stats[f"{tag}:E2_sessions"].append(S.between(rd, rv["trade"]))
                ev_stats[f"{tag}:E2_days"].append((rv["trade"] - rd).days)
                if tag == "unambiguous":
                    ev_stats[f"by_year:{year}:E2_sessions"].append(S.between(rd, rv["trade"]))
        ev_stats["C_days_rule"].append(1)

    # ---- assemble
    nf_n = sum(sm_nf.d.values())
    out = dict(
        kind="Long-horizon Stage C OF-A data / PIT feasibility audit - aggregates only (NON-RETURN)",
        decision="D242", protocol_sha256=sha(PROTOCOL), cut_off=CUT, holdout_accessed=False,
        returns_computed=False, surprise_values_computed=False, quantconnect_run=False, network_requests=client.fetched,
        sources={"E981-01/result.json": sha(ROOT / "experiments/E981-01/result.json"),
                 "E981-01/equity.csv.gz": sha(ROOT / "experiments/E981-01/equity.csv.gz"),
                 "data_freeze_v3.json": sha(ROOT / "research/phase14/data_v3/data_freeze_v3.json"),
                 "data_freeze_v21.json": sha(ROOT / "research/phase11/data_v21/data_freeze_v21.json"),
                 "data_v3_reference.json": sha(ROOT / "research/phase14/data_v3/data_v3_reference.json"),
                 "tz_conventions.json": sha(ROOT / "research/phase2/earnings_audit/tz_conventions.json"),
                 "xbrl_filings.json.gz": sha(ROOT / "data/sec_derived/xbrl_filings.json.gz"),
                 "event_table_v1.csv.gz": sha(ROOT / "research/phase2/h017/event_table_v1.csv.gz")},
        population=dict(universe_securities=len(U), reviews=len(revs), stock_months_all=sum(sm_all.d.values()),
                        stock_months_non_financial=nf_n, by_year_all={str(y): sm_all.d[y] for y in YEARS},
                        by_year_non_financial={str(y): sm_nf.d[y] for y in YEARS},
                        identity_coverage_all=ident_cov.out(), identity_source=dict(ident_src),
                        e981_cik_vs_identity=dict(e981_agree), identity_ciks=len(by_cik),
                        cache_missing=dict(cache_missing)),
        candidates={c: cand[c].out() for c in CANDS},
        candidate_missing_reasons={c: dict(reason_all[c]) for c in CANDS},
        candidate_sensitivities={k: v.out() for k, v in cand_sens.items()},
        company_coverage={c: {name: (round(len(sec_comp[c][name]) / len(sec_seen[name]), 4) if sec_seen[name] else None)
                              for name, _, _ in PERIODS} for c in CANDS},
        company_majority_months={c: {name: _majority(sec_months, name, c) for name, _, _ in PERIODS}
                                 for c in ("C1", "C2")},
        fields={f: dict(anchor_value_known=field_anchor[f].out(),
                        chains={str(k): field_chain[(f, k)].out() for k in (1, 5, 6, 9, 13, 17)},
                        anchor_period_span=[str(V3.dd(x)) if x is not None else None for x in field_span[f]],
                        q4_ytd_derived_share=share(q4[f], "ytd", q4[f]["known"]))
                for f in field_anchor},
        anchor_fresh_200d=anchor_any.out(),
        freshness=dict(with_visible=fresh200["with_visible"],
                       stale_200d_share=share(fresh200, "stale_200", fresh200["with_visible"]),
                       stale_91d_from_availability_share=share(stale91, "stale_91", stale91["with_visible"])),
        gaps=dict(gaps, outside_share=share(gaps, "outside_80_100", gaps["all"]),
                  week14_share=share(gaps, "14_week_95_100", gaps["all"])),
        fiscal_year_end=dict(registrants_with_codes=sum(1 for k in by_cik if fcodes.get(k)),
                             registrants_multiple_codes=sum(1 for k in by_cik if len(fcodes.get(k, ())) > 1),
                             chain={c: dict(v) for c, v in chain_fye.items()}),
        vintage={c: dict(v) for c, v in vintage.items()},
        non_comparable=dict(noncomp),
        pit=dict(checked=pit_checked, violations=pit_viol),
        survivorship={c: {g: dict(n=v["n"], complete_share=round(v["complete"] / v["n"], 4) if v["n"] else None)
                          for g, v in sorted(surv[c].items())} for c in surv},
        events=dict(counts=dict(ev_cnt), disclosure_category={str(k): cat[k] for k in (1, 2, 3, 4)},
                    within_sessions={str(k): (round(within[k] / within["n"], 4) if within["n"] else None)
                                     for k in (5, 10, 20, 30)},
                    delays={k: quantiles(v) for k, v in sorted(ev_stats.items()) if not k.startswith("by_year")},
                    by_year={k: quantiles(v) for k, v in sorted(ev_stats.items()) if k.startswith("by_year")}),
        data_v3_guard=_guard_summary(),
        floors=dict(label="PROVISIONAL FEASIBILITY THRESHOLD - OWNER REVIEW REQUIRED", floor=FLOOR,
                    years=list(FLOOR_YEARS), sensitivity={c: {str(f): all((cand[c].d[y] and cand[c].n[y] / cand[c].d[y] >= f)
                                                                       for y in FLOOR_YEARS) for f in SENS_FLOORS}
                                                          for c in CANDS}),
    )
    out["judgements"] = judge_all(out)
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps(out["judgements"], indent=1))


def _majority(sec_months, name, c):
    xs = [(v["n"], v[c]) for (sid, nm), v in sec_months.items() if nm == name and v["n"]]
    return round(sum(1 for n, k in xs if k >= 0.5 * n) / len(xs), 4) if xs else None


def _guard_summary():
    ref = json.loads((ROOT / "research/phase14/data_v3/data_v3_reference.json").read_text())
    g = ref.get("guard", {})
    return {k: g[k] for k in sorted(g) if not isinstance(g[k], (dict, list)) or len(json.dumps(g[k])) < 2000}


def judge_all(o):
    """Protocol section 8, applied mechanically."""
    pop = o["population"]
    ident_all = o["population"]["identity_coverage_all"]["all"] or 0.0
    ev = o["events"]["counts"]
    n_ev = ev.get("events", 0)
    sub_ok = 1.0 - (ev.get("not_determinable_no_submissions", 0) / n_ev) if n_ev else 0.0
    cf_ok = 1.0 - (pop["cache_missing"].get("companyfacts", 0) / pop["identity_ciks"]) if pop["identity_ciks"] else 0.0
    D_cls = ident_all < 0.80 or sub_ok < 0.80 or cf_ok < 0.80
    ts_ok = (ev.get("periodic_row_matched", 0) / (n_ev - ev.get("not_determinable_no_submissions", 0))
             if n_ev - ev.get("not_determinable_no_submissions", 0) else 0.0) >= 0.90
    res = {}
    for c in CANDS:
        by = o["candidates"][c]["by_year"]
        yrs = [by[str(y)] or 0.0 for y in FLOOR_YEARS]
        depth = "PASS" if all(v >= FLOOR for v in yrs) else "FAIL"
        pit = "PASS" if o["pit"]["violations"] == 0 else "FAIL"
        if c == "C3":
            pit = "UNKNOWN (market-cap input in-host only)" if pit == "PASS" else pit
        ch = o["fiscal_year_end"]["chain"][c]
        tot = ch.get("with_codes", 0) + ch.get("codes_missing", 0)
        if not tot or ch.get("with_codes", 0) / tot < 0.5:
            chain = "UNKNOWN"
        else:
            chain = "PASS" if ch.get("changed", 0) / ch["with_codes"] <= 0.01 else "FAIL"
        ts = "PASS" if ts_ok else "UNKNOWN"
        nofail = pit != "FAIL" and chain != "FAIL"
        if pit == "PASS" and depth == "PASS" and ts == "PASS" and chain == "PASS":
            suit = "FEASIBLE"
        elif nofail and (depth == "PASS" or all(v >= FLOOR_MIN for v in yrs)):
            suit = "CONDITIONAL"
        else:
            suit = "NOT FEASIBLE"
        res[c] = dict(pit=pit, depth=depth, timestamp=ts, chain=chain, min_year_coverage=round(min(yrs), 4),
                      without_purchase="CONDITIONAL" if c == "C3" else "YES", suitability=suit)
    un = ev.get("match:unambiguous", 0)
    e2 = o["events"]["delays"].get("unambiguous:E2_sessions", {})
    earlier_share = (o["events"]["disclosure_category"]["1"] / n_ev) if n_ev else 0.0
    material = earlier_share >= 0.5 and (e2.get("median") or 0) > TIMELINESS_SESSIONS
    fam = ("C1", "C2", "C5", "C6")
    if D_cls:
        cls = "D - INSUFFICIENT EVIDENCE"
    elif any(res[c]["suitability"] == "FEASIBLE" for c in fam) and not material:
        cls = "A - DATA FEASIBLE"
    elif any(res[c]["suitability"] in ("FEASIBLE", "CONDITIONAL") for c in fam):
        cls = "B - CONDITIONALLY FEASIBLE"
    else:
        cls = "C - NOT FEASIBLE"
    return dict(candidates=res, timeliness=dict(earlier_disclosure_share=round(earlier_share, 4),
                                                unambiguous_events=un, median_E2_sessions=e2.get("median"),
                                                material_design_issue=material,
                                                label="PROVISIONAL - OWNER REVIEW REQUIRED"),
                evidence=dict(identity_coverage=round(ident_all, 4), submissions_coverage=round(sub_ok, 4),
                              companyfacts_coverage=round(cf_ok, 4), timestamp_rows_ok=ts_ok),
                classification=cls)


if __name__ == "__main__":
    main()
