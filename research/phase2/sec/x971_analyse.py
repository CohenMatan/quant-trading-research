"""Analyse X971 (E971-02): QuantConnect-vs-SEC values, restatement / accession anomaly, market-cap method.
Inputs are ratios and identifiers only. Output: research/phase2/sec/x971_results.json (+ quarantine_release.json).

Value classes (vendor value / SEC as-first-filed value): match (|r-1| <= 0.5%), close (<= 2%), differs (<= 10%),
far (> 10%), n/a (one side missing). Version tag per field: which SEC filing's value the vendor value equals:
'first' (first filing that reported the period), 'later:<accession>' (only a later filing: amendment, restated
comparative or recast), 'none'.

Quarantine release rule (owner item 4: release only if historical validity is established): a quarantined record
is released only if (a) at least three of its whitelisted values have an SEC counterpart, including at least one
balance-sheet total and one flow; (b) every compared value matches the SEC original filing within 0.5%; and (c) no
value matches only a later filing. Otherwise it stays quarantined."""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).parent))
import e970_parse  # noqa: E402

OUT = Path(__file__).parent
FIELDS = ("revenue_ttm", "net_income_ttm", "total_assets", "stockholders_equity", "operating_cash_flow_ttm",
          "gross_profit_ttm", "operating_income_ttm", "revenue_q", "net_income_q")
INSTANT = ("total_assets", "stockholders_equity")


def cls(r):
    if r is None:
        return "n/a"
    d = abs(r - 1)
    return "match" if d <= 0.005 else "close" if d <= 0.02 else "differs" if d <= 0.10 else "far"


def parse_v(line):
    p = line.split("|")
    (cik, sid, tic, pe, fd, acc, seen, expo, quar, est, oacc, oform, ofiled) = p[1:14]
    ratios = {}
    for part in (p[14].split(";") if p[14] else []):
        k, v = part.split("=")
        ratios[k] = None if v == "na" else float(v)
    vers = {}
    for part in (p[15].split(";") if len(p) > 15 and p[15] else []):
        f, rest = part.split(":", 1)            # field:tag:n  (tag = first | none | later:acc/form/filed,...)
        tag, n = rest.rsplit(":", 1)
        vers[f] = (tag, int(n))
    return dict(cik=cik, sid=sid, ticker=tic, pe=pe, fd=fd, acc=acc, seen=seen, expo=expo, quarantined=quar == "1",
                estimated=est == "1", orig_accn=None if oacc == "None" else oacc, orig_form=oform, orig_filed=ofiled,
                ratios=ratios, versions=vers)


TTM = ("revenue_ttm", "net_income_ttm", "operating_cash_flow_ttm", "gross_profit_ttm", "operating_income_ttm")


def load_ref():
    from qresearch.sec_pack import unpack
    d = ROOT / "strategies" / "X971_sec_verification"
    return unpack({p.name: p.read_text() for p in d.glob("sec_ref*.py")}, "sec_ref")["sample"]


def semantic_ratios(v, ref):
    """Vendor / SEC ratios under the vendor's field semantics. X971 compared interim '*_ttm' values with a rolling
    TTM; the vendor's interim '*_ttm' is the latest completed fiscal year's total (as filed in the last 10-K), so
    the ratio is re-based on that 10-K value: r_fy = r_rolling x rolling / FY."""
    out = dict(v["ratios"])
    if v["orig_form"] != "10-Q" or v["cik"] not in ref:
        return out
    recs = ref[v["cik"]]["records"]
    o = next((r for r in recs if r[0] == v["orig_accn"]), None)
    if o is None:
        return out
    k10 = [r for r in recs if r[1] == "10-K" and r[2] <= o[2] and r[3] < o[3]]
    k = max(k10, key=lambda r: r[3]) if k10 else None
    for f in TTM:
        rr, ours, fy = v["ratios"].get(f), o[6].get(f), (k[6].get(f) if k else None)
        out[f] = rr * ours / fy if (rr is not None and ours and fy) else None
    return out


def locate_balance_sheet(v, verdict):
    """Which SEC balance sheet does the vendor's total-assets value equal? (implied from the ratio to the SEC
    original; public SEC data only)."""
    from qresearch.sec_edgar import SECClient
    from qresearch.sec_pit import index_facts
    r = v["ratios"].get("total_assets")
    if r is None or not v["orig_accn"]:
        return verdict
    A = [x for x in index_facts(SECClient().companyfacts(int(v["cik"]))).get("Assets", ()) if "start" not in x]
    orig = [x for x in A if x["accn"] == v["orig_accn"] and abs((date.fromisoformat(x["end"]) - date.fromisoformat(v["pe"])).days) <= 3]
    if not orig:
        return verdict
    hits = [x for x in A if abs(x["val"] / (r * orig[0]["val"]) - 1) <= 0.0005]
    if not hits:
        return "unresolved: balance-sheet values match no SEC filing (kept quarantined)"
    h = min(hits, key=lambda x: x["filed"])
    lag = (date.fromisoformat(h["end"]) - date.fromisoformat(v["pe"])).days
    if lag < 0 and h["filed"] <= v["fd"]:
        return ("mixed-period: income statement = original filing; balance sheet = an EARLIER period's, public "
                "before the vendor date (historically available, inconsistent; kept quarantined)")
    if lag > 0:
        return "UNSAFE: balance sheet from a LATER period (kept quarantined)"
    return verdict


def main(exp="E971-02"):
    sys.path.insert(0, str(ROOT / "src"))
    lines = e970_parse.lines(exp)
    ref = load_ref()
    V = [parse_v(l) for l in lines if l.startswith("V|")]
    for v in V:
        v["rolling_ttm_ratios"] = dict(v["ratios"])
        v["ratios"] = semantic_ratios(v, ref)
    sample = json.loads((OUT / "x971_sample.json").read_text())
    res = {"n_vendor_reports_compared": len(V)}
    # ---------------------------------------------------------------- values vs SEC original filing
    by_kind = defaultdict(lambda: defaultdict(Counter))
    for v in V:
        kind = "quarantined" if v["quarantined"] else "estimated" if v["estimated"] else "normal"
        if v["orig_accn"] is None:
            by_kind[kind]["_no_sec_original"]["n"] += 1
            continue
        for f in FIELDS:
            by_kind[kind][f][cls(v["ratios"].get(f))] += 1
    res["value_classes_vs_sec_original"] = {k: {f: dict(c) for f, c in d.items()} for k, d in by_kind.items()}
    core = ("revenue_ttm", "net_income_ttm", "total_assets", "stockholders_equity")
    rate = {}
    for f in FIELDS:
        c = Counter()
        for v in V:
            if v["orig_accn"] and not v["quarantined"]:
                c[cls(v["ratios"].get(f))] += 1
        n = sum(x for k, x in c.items() if k != "n/a")
        rate[f] = {"compared": n, "match_0.5pct": c["match"] / n if n else None,
                   "within_2pct": (c["match"] + c["close"]) / n if n else None, "far_gt_10pct": c["far"] / n if n else None}
    res["match_rates_non_quarantined"] = rate
    by_form = {}
    for form in ("10-K", "10-Q"):
        for f in FIELDS:
            c = Counter(cls(v["ratios"].get(f)) for v in V if v["orig_accn"] and not v["quarantined"]
                        and v["orig_form"] == form)
            n = sum(x for k, x in c.items() if k != "n/a")
            by_form[f"{form}|{f}"] = {"compared": n, "match_0.5pct": round(c["match"] / n, 4) if n else None,
                                      "within_2pct": round((c["match"] + c["close"]) / n, 4) if n else None}
    res["match_rates_by_form_vendor_semantics"] = by_form
    c = Counter()
    for v in V:
        if v["orig_form"] == "10-Q" and not v["quarantined"]:
            c[cls(v["rolling_ttm_ratios"].get("revenue_ttm"))] += 1
    res["interim_ttm_vs_rolling_ttm_revenue (definition check)"] = dict(c)
    # which filing does a mismatching vendor value correspond to?
    vt = Counter()
    for v in V:
        if v["quarantined"]:
            continue
        for f, (tag, n) in v["versions"].items():
            vt[("first" if tag == "first" else "later" if tag.startswith("later") else tag)] += 1
    res["vendor_value_source_non_quarantined"] = dict(vt)
    # ---------------------------------------------------------------- quarantined records (accession anomaly)
    q = []
    release = {}
    qc = Counter()
    for v in V:
        if not v["quarantined"]:
            continue
        compared = {f: r for f, r in v["ratios"].items() if r is not None}
        tags = {f: t for f, (t, n) in v["versions"].items()}
        firsts = [f for f, t in tags.items() if t == "first"]
        later_only = [f for f, t in tags.items() if t.startswith("later")]
        nones = [f for f, t in tags.items() if t == "none"]
        n_inst = sum(1 for f in firsts if f in INSTANT)
        n_flow = sum(1 for f in firsts if f not in INSTANT)
        if not tags:
            verdict = "unresolved: no SEC filing in XBRL reports this period (pre-XBRL period or CIK mismatch)"
        elif later_only:
            verdict = "restated: vendor value equals a LATER filing's value"
        elif not nones and len(firsts) >= 3 and n_inst >= 1 and n_flow >= 1:
            verdict = "valid: values equal the original filing; only the accession reference is later"
        elif not nones:
            verdict = "unresolved: too few values to verify"
        else:
            verdict = "unresolved: some values match no SEC filing"
        if verdict.startswith("unresolved: some"):
            verdict = locate_balance_sheet(v, verdict)
        qc[verdict] += 1
        q.append({k: v[k] for k in ("ticker", "cik", "sid", "pe", "fd", "acc", "orig_accn", "orig_form", "orig_filed")}
                 | {"ratios": compared, "version_tags": tags, "verdict": verdict})
        if verdict.startswith("valid"):
            release.setdefault(v["sid"], []).append([v["pe"], v["fd"]])
    res["quarantine"] = {"records": len(q), "verdicts": dict(qc), "detail": q}
    (OUT / "quarantine_release.json").write_text(json.dumps(release, indent=1, sort_keys=True) + "\n")
    # ---------------------------------------------------------------- PIT exposure of sample reports vs SEC filing
    X = {}
    for l in lines:
        if l.startswith("X|"):
            _, sid, pe, fd, day = l.split("|")
            X[(sid, pe, fd)] = day
    ex = Counter()
    for v in V:
        if v["orig_filed"] in (None, "None") or v["quarantined"]:
            continue
        d = X.get((v["sid"], v["pe"], v["fd"]))
        if d is None:
            ex["never exposed in sample window (superseded / stale / timing unknown)"] += 1
            continue
        gap = (date.fromisoformat(d) - date.fromisoformat(v["orig_filed"])).days
        ex["exposed after SEC filing date" if gap >= 1 else "exposed ON/BEFORE SEC filing date"] += 1
    res["sample_exposure_vs_sec_filing"] = dict(ex)
    # ---------------------------------------------------------------- market-cap method (K lines)
    K = [l.split("|") for l in lines if l.startswith("K|")]
    kc = Counter()
    ratios = []
    agree = Counter()
    for p in K:
        r = None if p[4] == "na" else float(p[4])
        if r is None:
            kc["no SEC count usable (none filed yet, multi-class/ambiguous, or older than 135 days)"] += 1
            continue
        kc["computed"] += 1
        ratios.append(r)
        agree[f"vendor>=2B:{p[5]}|sec>=2B:{p[6]}"] += 1
    ratios.sort()
    q_ = lambda x: ratios[int(x * (len(ratios) - 1))] if ratios else None
    res["market_cap_method"] = {
        "company_months": len(K), "classes": dict(kc),
        "ratio_quantiles(sec/vendor)": {k: q_(x) for k, x in (("p01", .01), ("p05", .05), ("p25", .25), ("p50", .5),
                                                               ("p75", .75), ("p95", .95), ("p99", .99))},
        "within_2pct": sum(1 for r in ratios if abs(r - 1) <= .02) / len(ratios) if ratios else None,
        "within_5pct": sum(1 for r in ratios if abs(r - 1) <= .05) / len(ratios) if ratios else None,
        "threshold_agreement_at_2B": dict(agree),
    }
    splits = [l for l in lines if l.startswith("SPLIT|")]
    cnt = json.loads([l for l in lines if l.startswith("C|")][-1][2:])
    # X971 logged the vendor factor ratio as sf(cover)/sf(today), the reciprocal of the live multiplier; compare
    # the live multiplier with its reciprocal (the canary's own 'split_disagree' count used the inverted ratio)
    chk = Counter()
    for p in K:
        if p[9] != "na" and p[10] != "na":
            sfr, live = float(p[9]), float(p[10])
            if abs(live - 1) > 1e-9 or abs(sfr - 1) > 1e-9:
                chk["agree" if abs(sfr * live - 1) <= 0.01 else "disagree"] += 1
    res["splits"] = {"live_split_events_on_sample": len(splits),
                     "company_months_with_split_adjustment": dict(chk),
                     "note": "canary count 'split_disagree' used an inverted vendor ratio (canary formula)",
                     "canary_split_disagree_raw": cnt.get("split_disagree")}
    res["run_counts"] = cnt
    res["sample_composition"] = dict(Counter(w for s in sample.values() for w in s["why"]))
    (OUT / "x971_results.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: v for k, v in r.items() if k != "quarantine"}, indent=1, default=str)[:6000])
    print(json.dumps(r["quarantine"]["verdicts"], indent=1))
