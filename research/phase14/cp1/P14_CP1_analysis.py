"""P14-CP1 (owner D227): offline analysis of the H029-A audit run E802-01 -> P14_CP1_audit.json.

Applies the rules pre-registered in research/phase14/H029A_audit_spec.md (committed d2b6b54, before any data) to the
aggregate export of X802. Written before E802-01 finished. DATA QUALITY ONLY: the export contains counts, quantiles and
input-to-input rank correlations; no return, price path or performance figure exists anywhere in it.

    PYTHONPATH=src python research/phase14/cp1/P14_CP1_analysis.py
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7")]
import qr_h029a as Z  # noqa: E402
import qr_p7_export as E  # noqa: E402
from P7_CP3R_extract import joined, lines  # noqa: E402

EXP = "E802-01"
FAMILY_ORDER = ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8")
FIELDS = dict(F1=("revenue",), F1Q=("revenue",), F2=("gross_profit", "revenue"), F3=("operating_income", "revenue"),
              F4A=("operating_cash_flow", "revenue"), F4B=("operating_cash_flow", "total_assets"),
              F5A=("net_income", "total_assets"), F5B=("gross_profit", "total_assets"),
              F6=("total_debt", "total_assets"), F7=("sec_cover_shares",), F8=("revenue", "total_assets"))
NOT_APPROVED = {"operating_income", "total_debt"}                 # D113 (and total debt: zero read as missing)
GUARDED = {"revenue", "total_assets"}                            # Data v2.1 restatement guard fields
UNGUARDED_APPROVED = {"gross_profit", "net_income", "operating_cash_flow"}
LEVELS = ((0.85, "STRONG"), (0.70, "USABLE"), (0.50, "WEAK"), (0.0, "UNUSABLE"))
PER = [p for p, _, _ in Z.PERIODS]


def load():
    ls = lines(EXP)
    st = json.loads(joined(ls, "QRZ"))
    blob = joined(ls, "QRZA")
    assert hashlib.sha256(blob.encode()).hexdigest() == st["audit_blob"]["sha256"], "blob hash mismatch"
    text = E.unpack(blob)
    for bad in ("return", "sharpe", "cagr", "wealth", "alpha", "forward"):
        assert bad not in text.lower(), bad
    return st, json.loads(text)


def level(m):
    return next(name for th, name in LEVELS if m >= th)


def coverage(agg):
    rv = agg["reviews"]
    yrs = np.array([int(d[:4]) for d in rv])
    nfe = np.asarray(agg["monthly"]["nf_eligible"], float)
    ale = np.asarray(agg["monthly"]["all_eligible"], float)
    out = {}
    for f in Z.FORMS:
        nv = np.asarray(agg["monthly"][f]["nf_valid"], float)
        av = np.asarray(agg["monthly"][f]["all_valid"], float)
        c, ca = nv / nfe, av / ale
        per = {}
        for p, a, b in Z.PERIODS:
            k = (yrs >= a) & (yrs <= b)
            per[p] = dict(median=float(np.median(c[k])), mean=float(c[k].mean()), min=float(c[k].min()),
                          all_universe_median=float(np.median(ca[k])))
        out[f] = dict(median=float(np.median(c)), mean=float(c.mean()), min=float(c.min()), max=float(c.max()),
                      months_below_50=int((c < 0.5).sum()), all_universe_median=float(np.median(ca)),
                      level=level(float(np.median(c))), periods=per,
                      breadth=dict(eligible_median=float(np.median(nfe)), valid_median=float(np.median(nv)),
                                   valid_min=int(nv.min()), valid_p5=float(np.percentile(nv, 5))),
                      monthly=[round(x, 4) for x in c.tolist()])
    return out


def sector_cov(agg):
    names = agg["ff12_names"]
    out, tot_nf = {}, {}
    for p in PER:
        for g, d in agg["sector"].get(p, {}).items():
            name = "no_SIC" if int(g) < 0 else names[int(g)]
            e = out.setdefault(name, dict(eligible=0, nf=0, valid=[0] * len(Z.FORMS), periods={}))
            e["eligible"] += d["eligible"]
            e["nf"] += d["nf"]
            e["valid"] = [a + b for a, b in zip(e["valid"], d["valid"])]
            e["periods"][p] = dict(eligible=d["eligible"],
                                   coverage={f: d["valid"][j] / d["eligible"] if d["eligible"] else None
                                             for j, f in enumerate(Z.FORMS)})
    nf_total = sum(e["nf"] for e in out.values())
    for name, e in out.items():
        e["share_of_nf"] = e["nf"] / nf_total if nf_total else 0.0
        e["coverage"] = {f: e["valid"][j] / e["eligible"] if e["eligible"] else None for j, f in enumerate(Z.FORMS)}
    return out


def flags(f, cov, sec, agg):
    c = cov[f]
    weak_sectors = [n for n, e in sec.items() if n not in ("Money", "no_SIC") and e["share_of_nf"] >= 0.03
                    and e["coverage"][f] is not None and e["coverage"][f] < 0.5]
    why = agg["why"][f]
    nf_sm = sum(sum(why[p]) for p in PER)
    den = sum(why[p][Z.W["denominator"]] for p in PER)
    return dict(low_month=c["months_below_50"] > 0.10 * len(c["monthly"]),
                small_cross_section=c["breadth"]["valid_p5"] < 100,
                weak_sectors=weak_sectors, weak_sector=bool(weak_sectors),
                availability_trend=(c["periods"]["2018-2021"]["median"] - c["periods"]["2011-2014"]["median"]) >= 0.10,
                pathology=(den / nf_sm if nf_sm else 0.0) > 0.02, denominator_share=den / nf_sm if nf_sm else 0.0)


def tail_ratio(d):
    q = d["overall"]
    iqr = q["p75"] - q["p25"]
    return (q["p99"] - q["p1"]) / iqr if iqr > 0 else float("inf")


def primary_forms(cov, agg):
    out = {}
    for fam, forms in Z.FAMILIES.items():
        if len(forms) == 1:
            out[fam] = dict(primary=forms[0], alternative=None, rule="single form")
            continue
        a, b = forms
        ca, cb = cov[a]["median"], cov[b]["median"]
        if abs(ca - cb) > 0.01:
            p = a if ca > cb else b
            rule = f"coverage {ca:.4f} vs {cb:.4f}"
        else:
            ta, tb = tail_ratio(agg["dist"][a]), tail_ratio(agg["dist"][b])
            p = a if ta <= tb else b
            rule = f"coverage within 1 pp ({ca:.4f} vs {cb:.4f}); tail ratio {ta:.2f} vs {tb:.2f}"
        out[fam] = dict(primary=p, alternative=b if p == a else a, rule=rule)
    return out


def classify(form, cov, fl):
    fields = set(FIELDS[form])
    c = cov[form]
    if c["level"] == "UNUSABLE":
        return "D", [f"median monthly coverage {c['median']:.1%} < 50% (UNUSABLE)"]
    reasons_c = []
    bad = sorted(fields & NOT_APPROVED)
    if bad:
        reasons_c.append("required field not approved by D113: " + ", ".join(bad)
                         + (" (a reported zero is read as missing)" if "total_debt" in bad else ""))
    if c["level"] == "WEAK":
        reasons_c.append(f"coverage WEAK ({c['median']:.1%})")
    if fl["low_month"]:
        reasons_c.append(f"LOW-MONTH: {c['months_below_50']} reviews below 50%")
    if fl["small_cross_section"]:
        reasons_c.append(f"SMALL CROSS-SECTION: 5th percentile {c['breadth']['valid_p5']:.0f} < 100")
    if reasons_c:
        return "C", reasons_c
    handling = []
    if c["level"] != "STRONG":
        handling.append(f"coverage {c['level']} ({c['median']:.1%})")
    if form == "F7":
        handling.append("SEC cover counts: split restatement rule, 4-significant-digit storage, cover-date matching")
    unguarded = sorted(fields & UNGUARDED_APPROVED)
    if unguarded:
        handling.append("PIT RESTATEMENT RISK (partial): " + ", ".join(unguarded)
                        + " not field-guarded (report version still blocked via revenue / total assets)")
    if fl["weak_sector"]:
        handling.append("WEAK SECTOR: " + ", ".join(fl["weak_sectors"]))
    if fl["availability_trend"]:
        handling.append("AVAILABILITY TREND: 2018-2021 coverage >= 10 points above 2011-2014")
    if fl["pathology"]:
        handling.append(f"PATHOLOGY: {fl['denominator_share']:.1%} of U_NF stock-months invalid by denominator")
    if handling:
        return "B", handling
    return "A", ["STRONG coverage, approved and field-guarded inputs only, no flag"]


def combined(agg, forms):
    """Median monthly U_NF coverage of each transparent rule over the given primary forms, from validity patterns."""
    idx = [Z.FORMS.index(f) for f in forms]
    n = len(idx)
    out = {}
    for m in range(n, int(math.ceil(n / 2)) - 1, -1):
        cov = []
        for d, nfe in zip(agg["reviews"], agg["monthly"]["nf_eligible"]):
            pats = agg["patterns"][d]
            ok = sum(c for b, c in pats.items() if sum((int(b) >> i) & 1 for i in idx) >= m)
            cov.append(ok / nfe)
        cov = np.asarray(cov)
        yrs = np.array([int(x[:4]) for x in agg["reviews"]])
        out[f"at_least_{m}_of_{n}"] = dict(median=float(np.median(cov)), min=float(cov.min()),
                                           periods={p: float(np.median(cov[(yrs >= a) & (yrs <= b)]))
                                                    for p, a, b in Z.PERIODS},
                                           rule="all present" if m == n else f"average of available (>= {m})")
    return out


def min_count(agg, forms):
    idx = [Z.FORMS.index(f) for f in forms]
    tot = sum(agg["monthly"]["nf_eligible"])
    out = {}
    for k in range(len(idx), 0, -1):
        ok = sum(c for d in agg["reviews"] for b, c in agg["patterns"][d].items()
                 if sum((int(b) >> i) & 1 for i in idx) >= k)
        out[f">={k}"] = ok / tot
    return out


def bias(agg, forms, m):
    """U_NF stock-months meeting the rule (>= m of the forms) vs not: mean log market cap / price / ADV and FF12 mix."""
    idx = [Z.FORMS.index(f) for f in forms]
    names = agg["ff12_names"]
    out = {}
    for p in PER:
        acc = {True: [0, 0.0, 0.0, 0.0, {}], False: [0, 0.0, 0.0, 0.0, {}]}
        for b, e in agg["pattern_periods"].get(p, {}).items():
            k = sum((int(b) >> i) & 1 for i in idx) >= m
            a = acc[k]
            for j in range(4):
                a[j] += e[j]
            for g, c in e[4].items():
                a[4][g] = a[4].get(g, 0) + c
        res = {}
        for k, a in acc.items():
            if a[0]:
                res["valid" if k else "invalid"] = dict(
                    stock_months=a[0], mean_log_mcap=a[1] / a[0], mean_log_price=a[2] / a[0], mean_log_adv=a[3] / a[0],
                    sector_share={("no_SIC" if int(g) < 0 else names[int(g)]): c / a[0] for g, c in a[4].items()})
        if "valid" in res and "invalid" in res:
            v, i = res["valid"], res["invalid"]
            res["valid_minus_invalid"] = dict(log_mcap=v["mean_log_mcap"] - i["mean_log_mcap"],
                                              log_price=v["mean_log_price"] - i["mean_log_price"],
                                              log_adv=v["mean_log_adv"] - i["mean_log_adv"])
        out[p] = res
    return out


def main():
    st, agg = load()
    cov = coverage(agg)
    sec = sector_cov(agg)
    fl = {f: flags(f, cov, sec, agg) for f in Z.FORMS}
    prim = primary_forms(cov, agg)
    cls = {}
    for fam in FAMILY_ORDER:
        p = prim[fam]["primary"]
        c, why = classify(p, cov, fl[p])
        cls[fam] = dict(form=p, cls=c, reasons=why)
    alt = {f: dict(zip(("cls", "reasons"), classify(f, cov, fl[f]))) for f in Z.FORMS}
    ab = [fam for fam in FAMILY_ORDER if cls[fam]["cls"] in ("A", "B")]
    ab_forms = [prim[fam]["primary"] for fam in ab]
    comb = combined(agg, ab_forms) if ab_forms else {}
    primary8 = [prim[fam]["primary"] for fam in FAMILY_ORDER]
    mc8 = min_count(agg, primary8)
    best = max(comb.values(), key=lambda r: r["median"])["median"] if comb else 0.0
    gate = dict(families_A_or_B=len(ab), families=ab, combined_rules=comb, best_rule_median=best,
                condition_1=len(ab) >= 5, condition_2=best >= 0.70)
    gate["result"] = "H029 DATA FEASIBILITY — PASS" if gate["condition_1"] and gate["condition_2"] else \
        "H029 DATA FEASIBILITY — FAIL"
    corr = agg["corr"]
    redundant = sorted(k for k, v in corr.items() if v.get("months") and v["median_abs"] >= 0.80)
    ov = agg["h028_overlap"]
    bias_rules = {}
    if ab_forms:
        n = len(ab_forms)
        for m in (n, int(math.ceil(n / 2))):
            bias_rules[f"at_least_{m}_of_{n}"] = bias(agg, ab_forms, m)
    bias_forms = {f: bias(agg, [f], 1) for f in Z.FORMS}
    out = dict(source=dict(experiment=EXP, audit_blob_sha256=st["audit_blob"]["sha256"]),
               run=dict(wall_s=st.get("wall_s"), max_rss_mb=st.get("max_rss_mb"), memory_stages=st.get("memory_stages"),
                        live_feature_s=st.get("live_feature_s"), f7=st.get("f7"), pit_audit=st.get("pit_audit"),
                        store_stats=st.get("store_stats"), checks=st.get("checks"),
                        h026_population=st.get("h026_population")),
               reviews=len(agg["reviews"]), coverage=cov, sector=sec, flags=fl, primary=prim, classification=cls,
               alternatives=alt, gate=gate, min_count_primary8=mc8,
               combined_all_primary8=combined(agg, primary8), redundancy=dict(high=redundant, pairs=corr),
               h028_overlap=ov, lowvol={f: ov.get(f"{f}|LOWVOL") for f in Z.FORMS},
               staleness=agg["staleness"], period_age=agg["period_age"], update=agg["update"], dist=agg["dist"],
               pathology=agg["pathology"], seasonality=agg["seasonality"], ttm=agg["ttm"], revised=agg["revised"],
               why=agg["why"], pit=agg["pit"], bias_rules=bias_rules, bias_forms=bias_forms,
               monthly_counts=dict(nf_eligible=agg["monthly"]["nf_eligible"], all_eligible=agg["monthly"]["all_eligible"],
                                   nf_nosic=agg["monthly"]["nf_nosic"]))
    path = HERE / "P14_CP1_audit.json"
    path.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(dict(gate=gate["result"], classes={k: (v["form"], v["cls"]) for k, v in cls.items()},
                          best=best), indent=1))
    print("sha256", hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
