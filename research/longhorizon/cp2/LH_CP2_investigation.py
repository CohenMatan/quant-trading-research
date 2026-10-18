"""LH-CP2 (owner D243): fiscal-calendar anomaly resolution. Implements LH_CP2_protocol.md (frozen before this script
produced any aggregate). Offline SEC metadata only, through the cut-off-enforcing loaders in lh_cp2_safe; no price, no
return, no surprise value, no QuantConnect. Output: aggregates + a few metadata-only examples (LH_CP2_investigation.json).

    PYTHONPATH=src python research/longhorizon/cp2/LH_CP2_investigation.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(HERE), str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase2/sec")]
import lh_cp2_safe as SAFE  # noqa: E402

_spec = importlib.util.spec_from_file_location("lh_stage_c_audit", ROOT / "research/longhorizon/stage_c/LH_StageC_audit.py")
SC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SC)
V3 = SC.V3
OUT = HERE / "LH_CP2_investigation.json"
PROTOCOL = HERE / "LH_CP2_protocol.md"
FLOOR_YEARS = tuple(range(2013, 2022))
TRANSITION_FORMS = ("10-KT", "10-QT", "10-KT/A", "10-QT/A")
FP_NUM = {"Q1": 1, "Q2": 2, "Q3": 3, "FY": 4, "Q4": 4}


# ----------------------------------------------------------------------------------------------- pure rules (tested)
def circ_days(a, b):
    try:
        da = (date(2001, int(a[:2]), int(a[2:])) - date(2001, 1, 1)).days
        db = (date(2001, int(b[:2]), int(b[2:])) - date(2001, 1, 1)).days
    except (ValueError, TypeError):
        return None
    d = abs(da - db)
    return min(d, 365 - d)


def code_group(codes):
    """Protocol 3: EQUAL / S7 / S31 / QA / OTHER / NOCODE (the committed diagnostic's bands)."""
    if any(c is None for c in codes):
        return "NOCODE"
    if len(set(codes)) == 1:
        return "EQUAL"
    m = max(circ_days(codes[0], c) or 0 for c in codes[1:])     # exactly the committed diagnostic's rule
    if m <= 7:
        return "S7"
    if m <= 31:
        return "S31"
    return "QA" if min(abs(m - 91), abs(m - 182)) <= 15 else "OTHER"


def label_status(labels):
    """Protocol 5: labels L_0 (newest) .. L_12 as 1..4 or None -> consistent / broken / unknown."""
    if any(x is None for x in labels):
        return "unknown"
    cycle = all(labels[k] == labels[k + 1] % 4 + 1 for k in range(len(labels) - 1))
    same = all(labels[k] == labels[k + 4] for k in range(len(labels) - 4))
    return "consistent" if cycle and same else "broken"


def categorize(group, transition, mapping_fail, identity_change, lstatus):
    """Protocol 6 (first match) for a code-changed chain."""
    if transition:
        return "F"
    if mapping_fail:
        return "D"
    if identity_change:
        return "E"
    if lstatus == "broken":
        return "B"
    if lstatus == "unknown":
        return "G"
    return "A" if group == "S7" else "C"


def rule_v(lstatus, transition, mapping_fail):
    """Protocol 9: period-validity rule V -> valid / invalid / unknown (unknown is excluded)."""
    if lstatus == "broken" or transition or mapping_fail:
        return "invalid"
    if lstatus == "unknown":
        return "unknown"
    return "valid"


# ----------------------------------------------------------------------------------------------- metadata per CIK
class Meta:
    """Cut-off-safe filing metadata of one registrant."""

    def __init__(self, cik, client, xb_by_cik, fv21):
        self.cik = cik
        self.xb = sorted(xb_by_cik.get(cik, ()), key=lambda r: (r[0], r[2]))   # (period day, form, filed day, accn, fye, name)
        cf = SAFE.companyfacts(client, cik)
        self.fp, self.ends = defaultdict(Counter), defaultdict(set)
        if cf:
            for tags in cf["facts"].values():
                for body in tags.values():
                    for facts in body["units"].values():
                        for f in facts:
                            a = f.get("accn")
                            if not a:
                                continue
                            if f.get("fp"):
                                self.fp[a][f["fp"]] += 1
                            if f.get("start"):
                                self.ends[a].add(V3.dn(f["end"]))
        rows = SAFE.submissions(client, cik) or []
        self.trans = [(V3.dn(r["reportDate"]), V3.dn(r["filingDate"])) for r in rows
                      if r.get("form") in TRANSITION_FORMS and r.get("reportDate")]
        self.first_filing = min((r["filingDate"] for r in rows), default=None)
        self.has_sub = bool(rows)
        self.orig = V3.originals(fv21) if fv21 else {}
        amend = set()
        if fv21:
            pe = 0
            for i in range(len(fv21[0])):
                pe += fv21[0][i]
                if fv21[2][i] in (3, 4):
                    amend.add(pe)
        self.amend = amend

    def filing(self, p):
        c = [r for r in self.xb if abs(r[0] - p) <= 7 and r[1] in ("10-Q", "10-K")]
        return min(c, key=lambda r: r[2]) if c else None

    def label(self, p):
        r = self.filing(p)
        if r is None or not self.fp.get(r[3]):
            return None
        return FP_NUM.get(self.fp[r[3]].most_common(1)[0][0])

    def mapping_fail(self, p):
        r = self.filing(p)
        if r is None:
            return False                      # no accession -> label unknown (G), not a mapping failure
        if not any(abs(e - p) <= 7 for e in self.ends.get(r[3], ())):
            return True
        fd = self.orig.get(p)
        return fd is not None and abs(r[2] - fd) > 3

    def transition(self, chain, D):
        lo, hi = chain[-1] - 7, chain[0] + 7
        return any(lo <= rd <= hi and fd <= D - 1 for rd, fd in self.trans)


def chain_meta(m: Meta, chain, D, fmap):
    codes = [SC.fye_at(fmap, m.cik, chain[k]) for k in (0, 4, 12)]
    labels = [m.label(p) for p in chain]
    ls = label_status(labels)
    mf = any(m.mapping_fail(p) for p in chain)
    tr = m.transition(chain, D)
    return dict(group=code_group(codes), lstatus=ls, mapping_fail=mf, transition=tr,
                amended=any(p in m.amend for p in chain), labels=labels, codes=codes)


# ----------------------------------------------------------------------------------------------- main
def main():
    from qr_data_v21 import load_table
    from qr_xs_diag import ff12
    t = load_table()
    ident = SC.Ident(t)
    U = SC.load_universe()
    revs = []
    for T, D in V3.review_days():
        revs.append(dict(T=T, D=D, Dn=V3.dn(str(D)), m=T.year * 12 + T.month - 1 + 1, year=T.year))
    client = SAFE.client()
    fmap, _codes = SC.load_fye()
    xb = SAFE.xbrl_filings()
    xb_by_cik = defaultdict(list)
    names = {}
    for r in xb:
        p = r.get("period") or ""
        if len(p) != 8:                          # no period: unusable (the committed fye_at skips these too)
            continue
        try:
            pdn = V3.dn(f"{p[:4]}-{p[4:6]}-{p[6:8]}")
        except ValueError:
            continue
        k = str(int(r["cik"]))
        xb_by_cik[k].append((pdn, r.get("form"), V3.dn(r["filed"]), r.get("accn"), r.get("fye"), r.get("name")))
        names[k] = r.get("name")

    # ---- P1: re-run the committed diagnostic unchanged and compare
    committed_path = ROOT / "research/longhorizon/stage_c/LH_StageC_fye_diagnostic.json"
    committed = json.loads(committed_path.read_text())
    _d = importlib.util.spec_from_file_location("lh_fye_diag", ROOT / "research/longhorizon/stage_c/LH_StageC_fye_diagnostic.py")
    DIAG = importlib.util.module_from_spec(_d)
    _d.loader.exec_module(DIAG)
    tmp = HERE / "_p1_rerun.json"
    DIAG.OUT = tmp                               # never overwrite the committed artifact
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        DIAG.main()
    rerun = json.loads(tmp.read_text())
    tmp.unlink()
    p1_identical = rerun == committed

    # ---- P2: rebuild the Stage C U_NF population (frozen functions) and C1 / C2 / C6 completeness
    den = Counter()
    items_by_cik = defaultdict(list)
    first_m = {sid: min(u["months"]) for sid, u in U.items() if u["months"]}
    last_m = {sid: max(u["months"]) for sid, u in U.items() if u["months"]}
    DEC21 = 2021 * 12 + 11
    for sid, u in U.items():
        for j, r in enumerate(revs):
            if r["m"] not in u["months"]:
                continue
            cik, sic, _src = ident.at(sid, r["Dn"])
            if sic is not None and 6000 <= sic <= 6999:
                continue
            den[r["year"]] += 1
            if cik is not None and sic is not None:
                items_by_cik[cik].append((sid, j, sic))
    recs = []                                    # complete stock-months: (year, j, sid, cik, chain, okC1, okC2, sic, TA, flags)
    metas, chains = {}, {}
    for ci, (cik, items) in enumerate(sorted(items_by_cik.items(), key=lambda kv: int(kv[0]))):
        cols = t["f"].get(cik)
        if not cols:
            continue
        cf = SAFE.companyfacts(client, cik)
        fx = V3.Facts(cf) if cf else V3.Facts({})
        orig = V3.originals(cols)
        memo = {}

        def known(con, p, vd):
            k = (con, p, vd)
            if k not in memo:
                memo[k] = SC.q_detail(fx, con, p, vd)[0] is not None
            return memo[k]
        meta = None
        for sid, j, sic in items:
            r = revs[j]
            D, y = r["Dn"], r["year"]
            vd = D - 1
            vis = sorted(p for p, fd in orig.items() if fd + 1 <= D)
            if not vis or D - vis[-1] > V3.MAX_AGE:
                continue
            c13 = V3.chain_back(vis, len(vis) - 1, 13)
            if not c13:
                continue
            ok1 = all(known("net_income", p, vd) for p in c13)
            ok2 = all(known("revenue", p, vd) for p in c13)
            if not (ok1 or ok2):
                continue
            if meta is None:
                meta = Meta(cik, client, xb_by_cik, cols)
                metas[cik] = meta
            key = (cik, tuple(c13))
            if key not in chains:
                chains[key] = dict(chain_meta(meta, c13, D, fmap), D=D, sms=0, identity=False, years=set(),
                                   sids=set())
            ch = chains[key]
            ch["sms"] += 1
            ch["years"].add(y)
            ch["sids"].add(sid)
            c_id, _s, _src = ident.at(sid, c13[-1])
            if (c_id is not None and c_id != cik) or (U[sid]["ciks"] and int(cik) not in U[sid]["ciks"]):
                ch["identity"] = True
            ta = fx.ta_known(c13[0], vd)
            age = None
            if meta.first_filing:
                age = (r["D"] - date.fromisoformat(meta.first_filing)).days / 365.25
            recs.append(dict(year=y, j=j, sid=sid, key=key, ok1=ok1, ok2=ok2, sic=sic, ta=ta, age=age,
                             entrant=first_m.get(sid, 0) > SC.M0 + 12 and r["m"] - first_m[sid] < 12,
                             leaver=last_m.get(sid, DEC21) < DEC21))
        if ci % 250 == 0:
            print("registrants", ci, len(items_by_cik), flush=True)

    # reproduction check against the frozen Stage C aggregates
    stage_c = json.loads((ROOT / "research/longhorizon/stage_c/LH_StageC_audit.json").read_text())["candidates"]
    cov = {c: Counter() for c in ("C1", "C2", "C6")}
    for rec in recs:
        cov["C1"][rec["year"]] += rec["ok1"]
        cov["C2"][rec["year"]] += rec["ok2"]
        cov["C6"][rec["year"]] += rec["ok1"] and rec["ok2"]
    repro = {c: {str(y): round(cov[c][y] / den[y], 4) if den[y] else None for y in range(2011, 2022)} for c in cov}
    repro_ok = all(repro[c][str(y)] == stage_c[c]["by_year"][str(y)] for c in cov for y in range(2011, 2022))
    if not repro_ok:
        OUT.write_text(json.dumps(dict(stop="P2 reproduction failed", repro=repro), indent=1) + "\n")
        raise SystemExit("STOP: P2 does not reproduce the frozen Stage C coverage (protocol 2)")

    # ---- classification of unique chains
    for key, ch in chains.items():
        ch["category"] = (categorize(ch["group"], ch["transition"], ch["mapping_fail"], ch["identity"], ch["lstatus"])
                          if ch["group"] in ("S7", "S31", "QA", "OTHER") else None)
        ch["rule_v"] = rule_v(ch["lstatus"], ch["transition"], ch["mapping_fail"])
    # C1-complete basis (the Stage C gate's C1 population) for shares
    c1_sm = Counter()
    c1_keys = set()
    for rec in recs:
        if rec["ok1"]:
            c1_sm[rec["key"]] += 1
            c1_keys.add(rec["key"])
    tot_sm = sum(c1_sm.values())
    groups = Counter()
    groups_sm = Counter()
    cats = defaultdict(Counter)
    cats_sm = defaultdict(Counter)
    detail = defaultdict(lambda: dict(registrants=set(), securities=set(), years=Counter(), sectors=Counter(),
                                      entrant_sm=0, leaver_sm=0, sm=0))
    lstat = Counter()
    lstat_sm = Counter()
    for key in c1_keys:
        ch = chains[key]
        groups[ch["group"]] += 1
        groups_sm[ch["group"]] += c1_sm[key]
        lstat[(ch["group"] == "EQUAL", ch["lstatus"])] += 1
        lstat_sm[(ch["group"] == "EQUAL", ch["lstatus"])] += c1_sm[key]
        if ch["category"]:
            cats[ch["group"]][ch["category"]] += 1
            cats_sm[ch["group"]][ch["category"]] += c1_sm[key]
            d = detail[ch["category"]]
            d["registrants"].add(key[0])
            d["securities"] |= ch["sids"]
    for rec in recs:
        if not rec["ok1"]:
            continue
        cat = chains[rec["key"]]["category"]
        if cat:
            d = detail[cat]
            d["sm"] += 1
            d["years"][rec["year"]] += 1
            d["sectors"][ff12(rec["sic"])] += 1
            d["entrant_sm"] += rec["entrant"]
            d["leaver_sm"] += rec["leaver"]
    n_ent = sum(r["entrant"] for r in recs if r["ok1"])
    n_lv = sum(r["leaver"] for r in recs if r["ok1"])
    n_c1 = sum(1 for r in recs if r["ok1"])

    # per-category concentration and comparability answers
    cat_out = {}
    for cat, d in sorted(detail.items()):
        reg_sm = Counter()
        for rec in recs:
            if rec["ok1"] and chains[rec["key"]]["category"] == cat:
                reg_sm[rec["key"][0]] += 1
        top5 = sum(v for _, v in reg_sm.most_common(5))
        cks = [k for k in c1_keys if chains[k]["category"] == cat]
        q0q4 = sum(1 for k in cks if None not in chains[k]["labels"][:5] and chains[k]["labels"][0] == chains[k]["labels"][4])
        cat_out[cat] = dict(unique_chains=len(cks), stock_months=d["sm"], registrants=len(d["registrants"]),
                            securities=len(d["securities"]), top5_registrants_share=round(top5 / d["sm"], 4) if d["sm"] else None,
                            years=dict(sorted((str(k), v) for k, v in d["years"].items())),
                            sectors=dict(d["sectors"].most_common()),
                            entrant_share=round(d["entrant_sm"] / d["sm"], 4) if d["sm"] else None,
                            leaver_share=round(d["leaver_sm"] / d["sm"], 4) if d["sm"] else None,
                            q0_q4_same_fiscal_quarter_share=round(q0q4 / len(cks), 4) if cks else None,
                            all_seasonal_pairs_valid_share=round(sum(chains[k]["lstatus"] == "consistent" for k in cks) / len(cks), 4) if cks else None,
                            amended_share=round(sum(chains[k]["amended"] for k in cks) / len(cks), 4) if cks else None)

    # ---- coverage effects (protocol 8)
    def excl_flags(ch):
        return dict(X1=ch["lstatus"] == "broken" or ch["transition"], X2=ch["mapping_fail"], X3=ch["lstatus"] == "unknown")

    scen = {"X1": ("X1",), "X2": ("X2",), "X3": ("X3",), "X1+X2": ("X1", "X2"), "X1+X2+X3 (=rule V)": ("X1", "X2", "X3")}
    coverage = {}
    for name, xs in scen.items():
        res = {}
        for c in ("C1", "C2", "C6"):
            num = Counter()
            for rec in recs:
                okc = rec["ok1"] if c == "C1" else (rec["ok2"] if c == "C2" else rec["ok1"] and rec["ok2"])
                if okc and not any(excl_flags(chains[rec["key"]])[x] for x in xs):
                    num[rec["year"]] += 1
            by = {str(y): round(num[y] / den[y], 4) for y in range(2011, 2022)}
            res[c] = dict(by_year=by, min_2013_2021=min(by[str(y)] for y in FLOOR_YEARS),
                          floor_70_all_years=all(by[str(y)] >= 0.70 for y in FLOOR_YEARS))
        coverage[name] = res
    # imbalance of the rule-V exclusion among C1-complete stock-months
    cuts = {}
    by_j = defaultdict(list)
    for rec in recs:
        if rec["ok1"] and rec["ta"] is not None:
            by_j[rec["j"]].append(rec["ta"])
    for j, v in by_j.items():
        cuts[j] = np.percentile(v, [100 / 3, 200 / 3]) if len(v) >= 3 else None
    imb = defaultdict(Counter)
    for rec in recs:
        if not rec["ok1"]:
            continue
        ex = any(excl_flags(chains[rec["key"]]).values())
        if rec["ta"] is None or cuts.get(rec["j"]) is None:
            size = "size:unknown"
        else:
            a, b = cuts[rec["j"]]
            size = "size:T1_small" if rec["ta"] <= a else ("size:T2" if rec["ta"] <= b else "size:T3_large")
        age = "age:unknown" if rec["age"] is None else ("age:<5y" if rec["age"] < 5 else ("age:5-15y" if rec["age"] < 15 else "age:>=15y"))
        for g in (size, age, f"ff12:{ff12(rec['sic'])}", "entrant" if rec["entrant"] else "not_entrant",
                  "leaver" if rec["leaver"] else "stayer", "all"):
            imb[g]["n"] += 1
            imb[g]["excluded"] += ex
    imbalance = {g: dict(n=v["n"], excluded_share=round(v["excluded"] / v["n"], 4)) for g, v in sorted(imb.items())}

    # ---- P1 OTHER chains (the committed diagnostic's 1.3%) classified with the same rules (unique chains)
    lo, hi = V3.dn("2011-01-01"), V3.dn("2021-12-31")
    p1 = defaultdict(Counter)
    p1_examples = []
    for cik, cols in t["f"].items():
        orig = V3.originals(cols)
        vis = sorted(orig)
        cand = []
        for i0 in range(len(vis)):
            if not (lo <= vis[i0] <= hi):
                continue
            ch = V3.chain_back(vis, i0, 13)
            if not ch:
                continue
            codes = [SC.fye_at(fmap, cik, ch[k]) for k in (0, 4, 12)]
            g = code_group(codes)
            if g in ("NOCODE",):
                continue
            p1["_all"][g] += 1
            if g != "EQUAL":
                cand.append((ch, g))
        if not cand:
            continue
        m = metas.get(cik) or Meta(cik, client, xb_by_cik, cols)
        for ch, g in cand:
            D = orig[ch[0]] + 1                  # the chain's own availability day (metadata filed before it)
            cm = chain_meta(m, ch, D, fmap)
            cat = categorize(g, cm["transition"], cm["mapping_fail"], False, cm["lstatus"])
            p1[g][cat] += 1
            if g == "OTHER":
                h = hashlib.sha256(f"{cik}|{ch[0]}".encode()).hexdigest()
                p1_examples.append((h, cat, cik, ch, cm))
    examples = {}
    for h, cat, cik, ch, cm in sorted(p1_examples):
        if cat in examples:
            continue
        m = metas.get(cik) or Meta(cik, client, xb_by_cik, t["f"][cik])
        rows = []
        for k, p in enumerate(ch):
            f = m.filing(p)
            rows.append(dict(k=k, period_end=str(V3.dd(p)), form=f[1] if f else None,
                             filed=str(V3.dd(f[2])) if f else None, fp_label=cm["labels"][k],
                             fye_code=f[4] if f else None))
        examples[cat] = dict(cik=cik, name=names.get(cik), codes_q0_q4_q12=cm["codes"], label_status=cm["lstatus"],
                             transition_form_in_span=cm["transition"], mapping_fail=cm["mapping_fail"], periods=rows)

    out = dict(
        kind="LH-CP2 fiscal-calendar anomaly investigation - aggregates + metadata-only examples (no returns)",
        decision="D243", protocol_sha256=hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(), cut_off=SAFE.CUT,
        network_requests=client.fetched, returns_computed=False, surprise_values_computed=False,
        quantconnect_run=False, holdout_accessed=False,
        p1_reproduction=dict(identical_to_committed=p1_identical, committed=committed),
        p1_changed_chain_categories={g: dict(v) for g, v in p1.items()},
        p2_reproduction=dict(identical_to_stage_c=repro_ok, coverage=repro, denominators={str(y): den[y] for y in range(2011, 2022)}),
        p2_c1_basis=dict(unique_chains=len(c1_keys), stock_months=tot_sm,
                         groups_unique=dict(groups), groups_stock_months=dict(groups_sm),
                         categories_unique={g: dict(v) for g, v in cats.items()},
                         categories_stock_months={g: dict(v) for g, v in cats_sm.items()},
                         label_status_unique={f"{'EQUAL' if e else 'CHANGED'}:{s}": v for (e, s), v in lstat.items()},
                         label_status_stock_months={f"{'EQUAL' if e else 'CHANGED'}:{s}": v for (e, s), v in lstat_sm.items()},
                         c1_complete_stock_months=n_c1, entrant_share=round(n_ent / n_c1, 4), leaver_share=round(n_lv / n_c1, 4)),
        categories=cat_out,
        rule_v=dict(unique={k: sum(1 for kk in c1_keys if chains[kk]["rule_v"] == k) for k in ("valid", "invalid", "unknown")},
                    stock_months={k: sum(c1_sm[kk] for kk in c1_keys if chains[kk]["rule_v"] == k) for k in ("valid", "invalid", "unknown")}),
        coverage_effects=coverage,
        exclusion_imbalance=imbalance,
        examples=examples,
    )
    out["classification"] = classify(out)
    SAFE.assert_no_post_cutoff(out)
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps(out["classification"], indent=1))


def classify(o):
    """Protocol 10, mechanical."""
    b = o["p2_c1_basis"]
    sm = b["stock_months"]
    unk_sm = sum(v for k, v in b["label_status_stock_months"].items() if k.endswith(":unknown"))
    other_u = sum(b["categories_unique"].get("OTHER", {}).values())
    other_g = b["categories_unique"].get("OTHER", {}).get("G", 0)
    if unk_sm / sm > 0.10 or (other_u and other_g / other_u > 0.25):
        cls = "C - INSUFFICIENT EVIDENCE"
    else:
        rv = o["coverage_effects"]["X1+X2+X3 (=rule V)"]
        below = [c for c in ("C1", "C2", "C6") if not rv[c]["floor_70_all_years"]]
        hidden = b["label_status_stock_months"].get("EQUAL:broken", 0) / sm
        if below or hidden > 0.01:
            cls = "B - MATERIAL UNRESOLVED PROBLEMS"
        else:
            cls = "A - ANOMALIES SUFFICIENTLY EXPLAINED"
    return dict(classification=cls, label_unknown_share=round(unk_sm / sm, 4),
                other_unresolved_share=round(other_g / other_u, 4) if other_u else None,
                hidden_fiscal_change_share=round(b["label_status_stock_months"].get("EQUAL:broken", 0) / sm, 4),
                rule_v_below_floor=[c for c in ("C1", "C2", "C6")
                                    if not o["coverage_effects"]["X1+X2+X3 (=rule V)"][c]["floor_70_all_years"]])


if __name__ == "__main__":
    main()
