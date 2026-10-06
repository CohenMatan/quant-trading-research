"""P7-CP1 item 34: independent verification of the deterministic cross-domain sample (E991-02 `A|` lines) against
the SEC's own filing history (data.sec.gov submissions; public-domain data, cached under data/sec_cache).

For every sampled (security, decision morning) with a fundamental record, find the SEC 10-K / 10-Q (or amendment /
transition report) of the registrant whose reportDate equals the record's period end and check:
  S1  the SEC original filing exists (report date within 7 days: 52/53-week filers' vendor period ends are normalised
      to the calendar month-end; or, where the SEC reportDate is unusable, a periodic filing on the vendor file date) (registrant from the E981-01 identifier export; the vendor CIK is current-status,
      D111, so a successor registrant may give "not found", which is reported, never forced);
  S2  the record became usable strictly AFTER the first SEC filing date of that period (no exposure before a public
      SEC 10-Q / 10-K);
  S3  the vendor file date is not before the SEC filing date;
  S4  the decision morning is after the SEC filing date.
Also the sampled SIC filing date is checked against the registrant's filing history (a periodic filing exists on that
date). Writes research/phase7/P7_sec_sample_check.json. No QuantConnect data is sent anywhere."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research" / "phase2" / "earnings_audit"))
from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402
import earnings_event_audit as EA  # noqa: E402

FORMS = {"10-K", "10-Q", "10-K/A", "10-Q/A", "10-KT", "10-QT", "10-KT/A", "10-QT/A", "10-K405"}


def main():
    a = json.loads((ROOT / "research/phase7/P7_audit_E991.json").read_text())["alignment"]
    U = EA.load_universe()
    sec = SECClient()
    subs = {}
    out = dict(samples=len(a), with_record=0, sec_found=0, not_found=0, no_cik=0, S2_violations=0,
               S3_vendor_before_sec=0, S4_violations=0, sic_filing_found=0, sic_checked=0, items=[])
    for x in a:
        if not x.get("fundamental_period_end"):
            continue
        out["with_record"] += 1
        u = U.get(x["sid"])
        ciks = u["ciks"] if u else []
        if not ciks:
            out["no_cik"] += 1
            out["items"].append(dict(sid=x["sid"], t=x["t"], result="no CIK"))
            continue
        rows = []
        for c in ciks:
            if c not in subs:
                d = sec.submissions(c)
                subs[c] = filings_table(d) if d else []
            rows += subs[c]
        pe = x["fundamental_period_end"]
        from datetime import date as _d

        def near(r):              # 52/53-week filers: the vendor normalises period ends to the calendar month-end
            try:
                return abs((_d.fromisoformat(r["reportDate"]) - _d.fromisoformat(pe)).days) <= 7
            except Exception:
                return False
        hits = sorted((r for r in rows if r.get("form") in FORMS and near(r)), key=lambda r: r["filingDate"])
        it_match = "reportDate within 7 days"
        if not hits:              # SEC metadata quirk (reportDate = filing date): match the periodic filing by date
            hits = [r for r in rows if r.get("form") in FORMS and r.get("filingDate") == x["fundamental_filed"]]
            it_match = "same filing date (SEC reportDate unusable)"
        it = dict(sid=x["sid"], ticker=x["ticker"], t=x["t"], period_end=pe, vendor_filed=x["fundamental_filed"],
                  usable_from=x["fundamental_usable_from"], decision_morning=x["decision_morning"])
        if not hits:
            out["not_found"] += 1
            it["result"] = "SEC filing for that period not found under the registrant"
        else:
            out["sec_found"] += 1
            f0 = hits[0]["filingDate"]
            it.update(sec_first_filed=f0, sec_form=hits[0]["form"], match=it_match)
            if not x["fundamental_usable_from"] > f0:
                out["S2_violations"] += 1
            if x["fundamental_filed"] < f0:
                out["S3_vendor_before_sec"] += 1
            if not x["decision_morning"] > f0:
                out["S4_violations"] += 1
            it["result"] = "ok" if x["fundamental_usable_from"] > f0 and x["decision_morning"] > f0 else "VIOLATION"
        if x.get("sic_filed"):
            out["sic_checked"] += 1
            if any(r.get("filingDate") == x["sic_filed"] for r in rows):
                out["sic_filing_found"] += 1
        out["items"].append(it)
    from datetime import date
    lags = []
    for it in out["items"]:
        if it.get("sec_first_filed"):
            lags.append((date.fromisoformat(it["vendor_filed"]) - date.fromisoformat(it["sec_first_filed"])).days)
            it["vendor_minus_sec_days"] = lags[-1]
    if lags:
        lags.sort()
        out["vendor_minus_sec_days"] = dict(min=lags[0], median=lags[len(lags) // 2], max=lags[-1],
                                            zero=sum(1 for v in lags if v == 0))
    (ROOT / "research/phase7/P7_sec_sample_check.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print({k: v for k, v in out.items() if k != "items"})


if __name__ == "__main__":
    main()
