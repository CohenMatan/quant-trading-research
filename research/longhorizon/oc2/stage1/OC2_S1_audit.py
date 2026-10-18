"""OC-2 Stage 1 (owner D248): Data v3 / PIT / fiscal-period integrity audit of the frozen F5 definition.

Implements `OC2_S1_protocol.md` (frozen and committed in 819a7a1 before this script produced any aggregate).
NON-RETURN and NO-VALUE: no F5 value, accounting amount, ratio, ranking, price or return is computed. Only metadata
(period ends, filing dates, forms, XBRL fact start / end / filing dates, identity rows, SIC, universe membership) is
used; fact values are never read (the value slot of `data_v3.Facts` tuples is not accessed). Offline, cache-only
SEC client with networking disabled; SEC rows filed after 2021-12-31 are dropped at load. Output: aggregates only.

    PYTHONPATH=src python research/longhorizon/oc2/stage1/OC2_S1_audit.py
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase2/sec"),
                str(ROOT / "research/longhorizon/stage_c"), str(ROOT / "research/longhorizon/oc_cp2")]
from qresearch import data_v3 as V3  # noqa: E402

CUT = "2021-12-31"
PROTOCOL = HERE / "OC2_S1_protocol.md"
PROTOCOL_SHA = "91da6f278d916ee25cc04d1d7fea8d428f67e34b214384b842ec043316fb836e"
OUT = HERE / "OC2_S1_audit.json"
YEARS = tuple(range(2011, 2022))
Y = tuple(range(2012, 2022))
PRIMARY_FROM = (2012, 2)
REG_TOL = 8.0                      # protocol 4 L0 / L4: |L - 365.25| <= 8
W53_DIFF = 5
ANNUAL, AMEND = (2,), (3, 4)
NI = "net_income"
GATES = dict(risk_pass=0.02, risk_fail=0.05, cov_pass=0.60, cov_fail=0.50, ver_pass=0.70, agr=0.90)
FROZEN_CODE = ("research/phase14/data_v3/DATA_V3_spec.md", "research/phase14/data_v3/data_freeze_v3.json",
               "research/phase11/data_v21/data_freeze_v21.json", "src/qresearch/lean/qr_v3.py",
               "src/qresearch/lean/qr_h029a.py", "src/qresearch/lean/qr_fundamentals.py", "src/qresearch/data_v3.py",
               "research/phase14/cp1/P14_CP1_audit.json", "research/phase14/cp2/P14_CP2_audit.json",
               "experiments/E981-01/result.json")


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


# ----------------------------------------------------------------------------------------------- pure metadata rules
def regular(L):
    return L is not None and abs(L - 365.25) <= REG_TOL


def annual_positions(chain, annual):
    """Positions k (0 = newest) whose original form class is annual; regular iff exactly two, 4 apart."""
    pos = [k for k, p in enumerate(chain) if annual.get(p)]
    return pos, (len(pos) == 2 and pos[1] - pos[0] == 4)


def q_method(fx, p, vd):
    """Data v3 `q_known` decision for net income from fact DATES only: 'direct' / 'ytd4' / 'ytd' / 'none'.
    Tuples are (filed, accn, -prio, start, class, value); index 5 (value) is never read."""
    by = fx.flows[NI]
    cur = [x for x in fx._near(by, p, V3.END_TOL) if x[0] <= vd]
    if any(x[4] == 1 for x in cur):
        return "direct"
    for cls in (4, 3, 2):
        c = [x for x in cur if x[4] == cls]
        if not c:
            continue
        x = max(c, key=lambda z: z[:5])
        for e in range(p - V3.PRIOR_END[1], p - V3.PRIOR_END[0] + 1):
            if any(y[0] <= vd and y[4] == cls - 1 and abs(y[3] - x[3]) <= V3.END_TOL for y in by.get(e, ())):
                return "ytd4" if cls == 4 else "ytd"
        return "none"
    return "none"


def ta_present(fx, p, vd):
    return any(x[0] <= vd for x in fx._near(fx.ta, p, V3.TA_TOL))


def classify(L0, L4, ap_regular, tf, id_change):
    if not regular(L0) or (L4 is not None and not regular(L4)) or id_change:
        return "NON_COMPARABLE_RISK"
    if not ap_regular or tf:
        return "FY_CHANGE_WINDOW_VALID"
    return "COMPARABLE"                      # split into VERIFIED / UNVERIFIED by DUR and TA


# ----------------------------------------------------------------------------------------------- accumulators
class Rate:
    def __init__(self):
        self.n, self.d = Counter(), Counter()

    def add(self, y, ok):
        self.d[y] += 1
        self.n[y] += bool(ok)

    def out(self):
        return {str(y): (round(self.n[y] / self.d[y], 4) if self.d[y] else None) for y in YEARS}


def load_transition_forms(client, cik):
    """[(filed day, report day, form)] of original 10-KT / 10-QT filings filed <= CUT (cache only)."""
    from qresearch.sec_edgar import filings_table
    try:
        sub = client.submissions(int(cik))
    except RuntimeError:
        return None
    if sub is None:
        return None
    out = []
    for r in filings_table(sub):
        f, fd, rd = r.get("form"), r.get("filingDate") or "", r.get("reportDate") or ""
        if f in ("10-KT", "10-QT") and fd and fd <= CUT and rd:
            out.append((V3.dn(fd), V3.dn(rd), f))
    return out


def main():
    import LH_StageC_audit as SC
    from qr_data_v21 import load_table
    from qr_xs_diag import ff12
    from qresearch.sec_edgar import SECClient
    from OC_CP2_power import window_from_coverage
    assert hashlib.sha256(PROTOCOL.read_bytes()).hexdigest() == PROTOCOL_SHA, "protocol changed after freeze"
    t = load_table()
    ident = SC.Ident(t)
    U = SC.load_universe()
    revs = []
    for T, D in V3.review_days():
        revs.append(dict(T=T, D=D, Dn=V3.dn(str(D)), m=T.year * 12 + T.month - 1 + 1, year=T.year,
                         primary=(T.year, T.month) >= PRIMARY_FROM))
    client = SECClient(cache_dir=ROOT / "data/sec_cache", user_agent="offline-audit", session=SC._NoNet())
    fmap, _codes = SC.load_fye()

    # ---- population: identified non-financial stock-months, grouped by CIK
    pop = Counter()
    pop_y = defaultdict(Counter)
    e981_counts = Counter()
    by_cik = defaultdict(list)
    for sid, u in U.items():
        for j, r in enumerate(revs):
            if r["m"] not in u["months"]:
                continue
            e981_counts[j] += 1
            cik, sic, _src = ident.at(sid, r["Dn"])
            pop["all"] += 1
            if sic is not None and 6000 <= sic <= 6999:
                pop["financial"] += 1
                continue
            if cik is None or sic is None:
                pop["no_identity" if cik is None else "no_sic"] += 1
                if r["primary"] or r["year"] == 2011:
                    pop_y[r["year"]]["no_identity_or_sic"] += 1
                continue
            pop["audit"] += 1
            by_cik[cik].append((sid, j, sic))

    reasons = defaultdict(Counter)              # year -> missing reason / complete
    cls_y = defaultdict(Counter)                # year -> class
    flags_y = defaultdict(Counter)
    dur_y = defaultdict(Counter)
    L0s, L4s = Counter(), Counter()
    pit_viol, late_filed = 0, Counter()
    amd = Rate()
    complete_by_rev = defaultdict(dict)         # j -> {sid: p0}
    sector_y = defaultdict(Counter)
    cache_missing = Counter()
    for cik, items in sorted(by_cik.items(), key=lambda kv: int(kv[0])):
        cols = t["f"].get(cik)
        try:
            cf = client.companyfacts(int(cik))
        except RuntimeError:
            cf = None
        if cf is None:
            cache_missing["companyfacts"] += 1
        fx = V3.Facts(cf) if cf else V3.Facts({})
        orig = V3.originals(cols) if cols else {}
        annual, amend_only = {}, []
        if cols:
            pe, codes = 0, defaultdict(list)
            for i in range(len(cols[0])):
                pe += cols[0][i]
                codes[pe].append((cols[2][i], pe + cols[1][i]))
            for p, rows in codes.items():
                annual[p] = any(c in ANNUAL for c, _ in rows)
                if not any(c in (1, 2) for c, _ in rows):
                    amend_only.append((p, min(fd for _, fd in rows)))
        tforms = load_transition_forms(client, cik)
        if tforms is None:
            cache_missing["submissions"] += 1
            tforms = []
        fy = fmap.get(cik, {})
        for sid, j, sic in items:
            r = revs[j]
            if not (r["primary"] or r["year"] == 2011):
                continue                     # 2012-01: outside the primary window and not 2011 context
            y, D = r["year"], r["Dn"]
            vd = D - 1
            vis = sorted(p for p, fd in orig.items() if fd + 1 <= D)
            if not cols:
                reasons[y]["no_filing_table"] += 1
                continue
            if not vis or D - vis[-1] > V3.MAX_AGE:
                reasons[y]["no_fresh_anchor"] += 1
                continue
            i0 = len(vis) - 1
            p0 = vis[i0]
            amd.add(y, any(p0 - 730 < p <= p0 and fd + 1 <= D for p, fd in amend_only))
            if i0 + 1 < 8:
                reasons[y]["short_history"] += 1
                continue
            seg = vis[i0 - 7:i0 + 1]
            gaps = [b - a for a, b in zip(seg, seg[1:])]
            if any(g < V3.GAP[0] for g in gaps):
                reasons[y]["gap_short"] += 1
                continue
            if any(g > V3.GAP[1] for g in gaps):
                reasons[y]["gap_long"] += 1
                continue
            c8 = V3.chain_back(vis, i0, 8)
            reasons[y]["complete"] += 1
            # ---- PIT and ordering
            pit_viol += sum(1 for p in c8 if orig[p] + 1 > D)
            late_filed[y] += any(orig[c8[k]] > orig[c8[k - 1]] for k in range(1, 8))
            # ---- window lengths
            L0 = c8[0] - c8[4]
            p8 = vis[i0 - 8] if i0 >= 8 else None
            L4 = (c8[4] - p8) if (p8 is not None and V3.GAP[0] <= c8[7] - p8 <= V3.GAP[1]) else None
            L0s[L0] += 1
            if L4 is not None:
                L4s[L4] += 1
            w53 = L4 is not None and abs(L0 - L4) >= W53_DIFF
            # ---- fiscal structure
            _pos, ap_reg = annual_positions(c8, annual)
            tf = any(fd <= vd and c8[7] - 100 <= rd <= c8[0] for fd, rd, _f in tforms)
            codes8 = {SC.fye_at({cik: fy}, cik, p) for p in c8} - {None}
            # ---- identity inside the span
            cik7, _s7, _src7 = ident.at(sid, orig[c8[7]])
            id_change = cik7 is not None and cik7 != cik
            id_unknown = cik7 is None
            # ---- SEC-verifiable durations and TA instants
            meth = [q_method(fx, p, vd) for p in c8]
            ver = all(m != "none" for m in meth) and ta_present(fx, c8[0], vd) and ta_present(fx, c8[4], vd)
            for m in meth:
                dur_y[y][m] += 1
            c = classify(L0, L4, ap_reg, tf, id_change)
            if c == "COMPARABLE":
                c = "COMPARABLE_VERIFIED" if ver else "COMPARABLE_UNVERIFIED"
            elif c == "FY_CHANGE_WINDOW_VALID":
                flags_y[y]["fy_change_verified" if ver else "fy_change_unverified"] += 1
            cls_y[y][c] += 1
            for k, v in (("L4_unmeasured", L4 is None), ("W53_mismatch", w53), ("annual_break", not ap_reg),
                         ("transition_form", tf), ("fye_code_change", len(codes8) > 1), ("id_change", id_change),
                         ("id_unknown", id_unknown), ("derived_q4_in_span", "ytd4" in meth),
                         ("L0_irregular", not regular(L0)), ("L4_irregular", L4 is not None and not regular(L4)),
                         ("verified", ver)):
                flags_y[y][k] += bool(v)
            complete_by_rev[j][sid] = p0
            if r["primary"]:
                sector_y[y][ff12(sic)] += 1

    # ---- per-year shares (2012 = its primary-window reviews Feb..Dec; 2011 = context)
    out_years = {}
    for y in YEARS:
        rs = reasons[y]
        tot = sum(rs.values()) + pop_y[y]["no_identity_or_sic"]
        aud = sum(rs.values())
        comp = rs["complete"]
        cl = cls_y[y]
        risk = cl["NON_COMPARABLE_RISK"] / comp if comp else None
        verified = (cl["COMPARABLE_VERIFIED"] + flags_y[y]["fy_change_verified"]) / comp if comp else None
        out_years[str(y)] = dict(
            audit_stock_months=aud, no_identity_or_sic=pop_y[y]["no_identity_or_sic"],
            complete_share=round(comp / aud, 4) if aud else None,
            missing_reasons={k: round(v / aud, 4) for k, v in sorted(rs.items())} if aud else {},
            classes={k: round(v / comp, 4) for k, v in sorted(cl.items())} if comp else {},
            non_comparable_risk=round(risk, 4) if risk is not None else None,
            verified_share=round(verified, 4) if verified is not None else None,
            flags={k: round(v / comp, 4) for k, v in sorted(flags_y[y].items())} if comp else {},
            duration_methods={k: round(v / sum(dur_y[y].values()), 4) for k, v in sorted(dur_y[y].items())},
            late_filed_chain=round(late_filed[y] / comp, 4) if comp else None,
            identified_share=round(aud / tot, 4) if tot else None)

    # ---- Stage 2 population statistics (primary window)
    prim = [j for j, r in enumerate(revs) if r["primary"]]
    counts = [len(complete_by_rev[j]) for j in prim]
    refresh, entry, exit_, refresh_by_cal = [], [], [], defaultdict(list)
    for a, b in zip(prim, prim[1:]):
        A, B = complete_by_rev[a], complete_by_rev[b]
        both = set(A) & set(B)
        if both:
            sh = sum(1 for s in both if A[s] != B[s]) / len(both)
            refresh.append(sh)
            refresh_by_cal[revs[b]["T"].month].append(sh)
        if B:
            entry.append(len(set(B) - set(A)) / len(B))
        if A:
            exit_.append(len(set(A) - set(B)) / len(A))

    def mean(x):
        return round(sum(x) / len(x), 4) if x else None
    stage2 = dict(
        reviews=len(prim), first=str(revs[prim[0]]["T"]), last=str(revs[prim[-1]]["T"]),
        complete_per_review=dict(mean=round(sum(counts) / len(counts), 1), min=min(counts), max=max(counts),
                                 by_year={str(y): round(sum(len(complete_by_rev[j]) for j in prim
                                                            if revs[j]["year"] == y) /
                                                        max(1, sum(1 for j in prim if revs[j]["year"] == y)), 1)
                                          for y in Y}),
        anchor_refresh_share=dict(mean=mean(refresh),
                                  by_calendar_month={str(k): mean(v) for k, v in sorted(refresh_by_cal.items())}),
        entry_share=mean(entry), exit_share=mean(exit_),
        ff12_mean_per_review={str(y): {k: round(v / max(1, sum(1 for j in prim if revs[j]["year"] == y)), 1)
                                       for k, v in sorted(sector_y[y].items())} for y in Y})

    # 2012 primary-window-only figures (Feb..Dec)
    prim12 = {j for j in prim if revs[j]["year"] == 2012}
    c12 = sum(len(complete_by_rev[j]) for j in prim12)

    # ---- committed evidence (re-read, not recomputed)
    p2 = json.loads((ROOT / "research/phase14/cp2/P14_CP2_audit.json").read_text())
    p1 = json.loads((ROOT / "research/phase14/cp1/P14_CP1_audit.json").read_text())
    an = p2["validation"]["anchor"]
    rf = p2["validation"]["raw_field_agreement"]

    def match_share(d):
        nm = sum(v for k, v in d.items() if k != "missing")
        return round(d["match"] / nm, 4) if nm else None
    committed = dict(
        p14_cp2_pit=p2["pit"], pit_all_zero=all(v == 0 for v in p2["pit"].values()),
        anchor_agreement=round(an["agree"] / sum(an.values()), 4), anchor=an,
        NI0_match_share=match_share(rf["NI0"]), TA0_match_share=match_share(rf["TA0"]),
        F5_validation=p2["validation"]["F5"], guard_net_income=p2["guard"]["provenance"]["net_income_q"],
        guard_total_assets=p2["guard"]["provenance"]["total_assets"],
        guard_blocked_net_income_by_year=p2["guard"]["blocked_by_field_year"]["net_income_q"],
        data_v3_F5_coverage=p2["coverage"]["F5"], p14_cp1_F5A=dict(level=p1["coverage"]["F5A"]["level"],
                                                                  breadth=p1["coverage"]["F5A"]["breadth"]))
    win = window_from_coverage()
    v21 = p1["monthly_counts"]["all_eligible"]
    univ = {str(y): dict(e981_mean=round(sum(e981_counts[j] for j, r in enumerate(revs) if r["year"] == y) /
                                         sum(1 for r in revs if r["year"] == y), 1),
                         data_v21_mean=round(sum(v21[j] for j, r in enumerate(revs) if r["year"] == y) /
                                             sum(1 for r in revs if r["year"] == y), 1)) for y in YEARS}

    # ---- gates (protocol 7)
    yy = [out_years[str(y)] for y in Y]
    risks = [r["non_comparable_risk"] for r in yy]
    covs = [r["complete_share"] for r in yy]
    vers = [r["verified_share"] for r in yy]
    g = {}
    g["G-DEF"] = "PASS"                                         # Part A, OC2_S1_static.md
    g["G-PIT"] = "PASS" if pit_viol == 0 and committed["pit_all_zero"] else "FAIL"
    g["G-RISK"] = ("FAIL" if max(risks) > GATES["risk_fail"] else
                   "CONDITIONAL" if max(risks) > GATES["risk_pass"] else "PASS")
    g["G-COV"] = ("FAIL" if min(covs) < GATES["cov_fail"] else
                  "CONDITIONAL" if min(covs) < GATES["cov_pass"] else "PASS")
    g["G-VER"] = "CONDITIONAL" if min(vers) < GATES["ver_pass"] else "PASS"
    g["G-AGR"] = ("PASS" if min(committed["anchor_agreement"], committed["NI0_match_share"],
                              committed["TA0_match_share"]) >= GATES["agr"] else "CONDITIONAL")
    g["G-WIN"] = "PASS" if win["first_review"] == "2012-02" else "CONDITIONAL"
    vals = set(g.values())
    cls = ("FAIL — NOT SUPPORTED" if "FAIL" in vals else
           "CONDITIONAL" if "CONDITIONAL" in vals else "PASS — PIT-SAFE AND SUFFICIENT")

    out = dict(
        kind="OC-2 Stage 1 data / PIT / fiscal-period integrity audit (aggregates only; no values, no returns)",
        decision="D248", protocol_sha256=PROTOCOL_SHA, script_sha256=sha(Path(__file__).relative_to(ROOT)),
        inputs_sha256={p: sha(p) for p in FROZEN_CODE}, population=dict(pop), cache_missing=dict(cache_missing),
        years=out_years, primary_2012_complete_stock_months=c12, pit_violations=pit_viol,
        amendment_only_period_share=amd.out(),
        window_length_days=dict(L0=dict(sorted(Counter({k: v for k, v in L0s.items()}).items())),
                                L4=dict(sorted(L4s.items()))),
        stage2_population=stage2, committed_evidence=committed, window_rule=win, universe_counts=univ,
        gates=g, thresholds=GATES, classification=cls)
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(dict(gates=g, classification=cls, risk=risks, cov=covs, ver=vers), indent=1))


if __name__ == "__main__":
    main()
