"""P7-CP5c (D184): OFFLINE feasibility of an SEC-only point-in-time fundamentals layer (public SEC data + our own
eligibility tables; no QuantConnect run, no price, no return, no score).

For every eligible, non-financial stock-month of the X993 exports (E993-02 = LEAN 18131 universe, E993-03 = LEAN
18178 universe), the security's SEC registrant (identity v2: SEC-dated CIK in force at the review; the correction
layer's CIK for repaired securities) is looked up; its periodic filings (10-K / 10-Q and amendments) are rebuilt from
SEC XBRL company facts AS FIRST FILED (qresearch.sec_pit.build_company) and fed, in filing order, into the FROZEN
point-in-time store (qr_fundamentals.PITStore: usable from the day after the SEC filing date, freshness 200 days,
True TTM of four consecutive quarters reconciled to the fiscal-year total). At each review the frozen seven inputs
(qr_p7_export.fund_values) and the store-wide revenue ledger (True TTM recorded live at every review; baseline = the
value recorded 12 months earlier) give the frozen H2 test (qr_p7_score.fundamental_inputs). Also: SEC filing delays
(filing date - period end) for the estimated-date question.
Output: research/phase7/cp5c/sec_only_coverage.json"""
import gzip
import json
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7")]
import qr_p7_export as E  # noqa: E402
import qr_p7_score as S  # noqa: E402
import qr_sec_data as D  # noqa: E402
from qr_fundamentals import DEFAULT_MAX_AGE_DAYS, PITStore  # noqa: E402
from P7_CP3R_extract import joined, lines  # noqa: E402
from qresearch.sec_edgar import SECClient  # noqa: E402
from qresearch.sec_pit import build_company  # noqa: E402

NONFIN_BAD = E.BIT["H1_financial"] | E.BIT["H1_no_sic"] | E.BIT["duplicate_class"]


def tables(pay):
    sids = pay["sids"]
    return {t: {sids[r["i"]]: r for r in E.decode_rows(enc)} for t, tk, enc in pay["reviews"]}


def main(limit=None):
    old = tables(json.loads(gzip.open(ROOT / "research/phase7/P7_CP3R_E993_payload.json.gz").read()))
    new = tables(json.loads(E.unpack(joined(lines("E993-03"), "QRP7X"))))
    sec = D.load_table()
    hist = sec["sic_history"]
    rep = {s: int(c["cik"][0]) for s, c in sec["corrections"].items() if c.get("status") == "repaired"}

    def cik_on(sid, day):
        if sid in rep:
            return rep[sid]
        out = None
        for eff, _sic, c in hist.get(sid, ()):
            if eff <= day and c not in (None, ""):
                out = int(c)
        return out

    reviews = sorted(old)
    pop = {"old": defaultdict(set), "new": defaultdict(set)}
    vendor_h2 = {"old": Counter(), "new": Counter()}
    for lab, tab in (("old", old), ("new", new)):
        for t in reviews:
            for sid, r in tab.get(t, {}).items():
                if r["bits"] & NONFIN_BAD:
                    continue
                pop[lab][t].add(sid)
                vendor_h2[lab]["rows"] += 1
                vendor_h2[lab]["h2"] += int(bool(r["bits"] & E.BIT["H2"]))
    sids = sorted({s for lab in pop for t in pop[lab] for s in pop[lab][t]})
    if limit:
        sids = sids[:int(limit)]
    client = SECClient()
    res = {"old": Counter(), "new": Counter()}
    by_year = {"old": defaultdict(Counter), "new": defaultdict(Counter)}
    delays = defaultdict(list)
    nocik, nofacts = 0, 0
    reasons = Counter()
    for n_s, sid in enumerate(sids):
        ts = sorted({t for lab in pop for t in pop[lab] if sid in pop[lab][t]})
        cik = cik_on(sid, ts[0])
        if cik is None:
            nocik += 1
            for lab in pop:
                for t in ts:
                    if sid in pop[lab][t]:
                        res[lab]["no_cik"] += 1
                        by_year[lab][t[:4]]["no_cik"] += 1
            continue
        cf, sub = client.companyfacts(cik), client.submissions(cik)
        recs = sorted(build_company(cf, sub), key=lambda r: (r["filed"], r["accn"])) if cf else []
        if not recs:
            nofacts += 1
        for r in recs:
            if "2009-01-01" <= r["period_end"] <= "2017-12-31":
                delays[r["form"].split("/")[0]].append((date.fromisoformat(r["filed"]) - date.fromisoformat(r["period_end"])).days)
        store = PITStore(DEFAULT_MAX_AGE_DAYS)
        ledger = {}
        i = 0
        # every month-end review from 2010-01 (ledger) .. 2017-12; reviews of the export are the scored ones
        months = sorted({t for t in reviews} | {f"2010-{m:02d}-28" for m in range(1, 13)})
        for t in months:
            day = date.fromisoformat(t)
            sel = day + timedelta(days=1)                  # the selection day reflecting session t
            while i < len(recs) and date.fromisoformat(recs[i]["filed"]) < sel:
                r = recs[i]
                store.observe(sid, date.fromisoformat(r["period_end"]), date.fromisoformat(r["filed"]),
                              {k: v for k, v in r["values"].items()}, None, sel)
                i += 1
            vals = E.fund_values(store, sid, sel)
            ledger[(day.year, day.month)] = vals[0]
            if t not in pop["old"] and t not in pop["new"]:
                continue
            base = ledger.get((day.year - 1, day.month))
            fi, why = S.fundamental_inputs(*vals, base)
            for lab in pop:
                if sid in pop[lab].get(t, ()):
                    k = "pass" if fi is not None else "h2"
                    res[lab][k] += 1
                    by_year[lab][t[:4]][k] += 1
                    # diagnostic upper bound: H2 passed if gross profit were available (derivation not frozen)
                    if fi is None and vals[1] is None and vals[0] is not None:
                        fi_gp, _ = S.fundamental_inputs(vals[0], vals[0], *vals[2:], base)
                        res[lab]["pass_if_gp_derivable"] += int(fi_gp is not None)
                    if fi is None and lab == "new":
                        reasons[why.split(":")[0] + (":" + why.split(":")[1].split(",")[0] if ":" in why else "")] += 1
        if n_s % 200 == 0:
            print(n_s, len(sids), dict(res["new"]), client.fetched, flush=True)

    def q(v, p):
        v = sorted(v)
        return v[min(len(v) - 1, int(p * len(v)))] if v else None
    delay = {f: dict(n=len(v), median=statistics.median(v) if v else None, p90=q(v, 0.9), p99=q(v, 0.99), max=max(v) if v else None,
                     share_gt_45=sum(x > 45 for x in v) / len(v) if v else None, share_gt_90=sum(x > 90 for x in v) / len(v) if v else None,
                     share_negative=sum(x < 0 for x in v) / len(v) if v else None)
             for f, v in delays.items() if f in ("10-Q", "10-K", "10-KT")}
    out = dict(securities=len(sids), no_cik=nocik, no_sec_facts=nofacts, sec_requests=client.fetched,
               vendor=dict({k: dict(v, h2_share=v["h2"] / v["rows"]) for k, v in vendor_h2.items()}),
               sec_only={k: dict(v, pass_share=v["pass"] / max(1, v["pass"] + v["h2"] + v["no_cik"]),
                                  pass_share_if_gp_derivable=(v["pass"] + v["pass_if_gp_derivable"]) /
                                  max(1, v["pass"] + v["h2"] + v["no_cik"])) for k, v in res.items()},
               sec_only_by_year={k: {y: dict(c, pass_share=c["pass"] / max(1, c["pass"] + c["h2"] + c["no_cik"])) for y, c in sorted(v.items())}
                                 for k, v in by_year.items()},
               h2_reasons_new_universe=dict(reasons.most_common(12)), sec_filing_delay_days=delay)
    (Path(__file__).parent / "sec_only_coverage.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps({k: out[k] for k in ("securities", "no_cik", "no_sec_facts", "vendor", "sec_only")}, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:])
