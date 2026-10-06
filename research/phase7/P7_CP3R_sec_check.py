"""P7-CP3R (D173) item 10: independent verification of the deterministic sample of RESCUED revenue baselines (40
stock-reviews exported by X993 v1.1 / E993-02, dates only) against the SEC's own filing history (data.sec.gov
submissions; public-domain data, cached under data/sec_cache).

For each sampled baseline (the four quarters of the revenue True TTM recorded at the review 12 months earlier) and each
quarter, find the registrant's 10-Q / 10-K (or amendment / transition report) whose reportDate is within 7 days of the
quarter end (52/53-week filers) and check:
  V1  the SEC original filing exists;
  V2  it was filed strictly BEFORE the baseline selection day (the value was public when the baseline was recorded);
  V3  the vendor file date used by the PIT store is not before the SEC filing date (no early exposure).
The registrant is the SEC CIK of the security's filings (PIT SIC table) plus the E981-01 identifier export, plus a
documented predecessor registrant where the first pass found no filing (PREDECESSORS).
Writes research/phase7/P7_CP3R_sec_check.json. No QuantConnect data is sent anywhere."""
import gzip
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research" / "phase2" / "earnings_audit"))
from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402
import earnings_event_audit as EA  # noqa: E402

# predecessor registrants found when a sampled baseline's filings were not under the current CIK (looked up on EDGAR,
# 2026-10-06): Zillow Group (CIK 1617640, 2015 holding-company reorganisation) <- Zillow, Inc. (CIK 1334814)
PREDECESSORS = {"Z UYE69C59FN8L": ("1334814",)}
FORMS = {"10-K", "10-Q", "10-K/A", "10-Q/A", "10-KT", "10-QT", "10-KT/A", "10-QT/A", "10-K405"}


def main():
    pay = json.loads(gzip.open(HERE / "P7_CP3R_E993_payload.json.gz").read())
    sample = pay["rescued_sample"]
    U = EA.load_universe()
    sec = SECClient()
    subs = {}
    out = dict(samples=len(sample), quarters=0, sec_found=0, not_found=0, no_cik=0, V2_violations=0,
               V3_vendor_before_sec=0, samples_all_quarters_verified=0, items=[])
    for x in sample:
        ciks = [c for c in [x.get("cik")] if c]
        u = U.get(x["sid"])
        for c in (u["ciks"] if u else []):
            if str(int(c)) not in [str(int(k)) for k in ciks]:
                ciks.append(c)
        for c in PREDECESSORS.get(x["sid"], ()):
            if c not in ciks:
                ciks.append(c)
        it = dict(sid=x["sid"], review=x["review"], baseline_selection=x["baseline_selection"], reason=x["reason"],
                  quarters=[])
        if not ciks:
            out["no_cik"] += 1
            it["result"] = "no CIK"
            out["items"].append(it)
            continue
        rows = []
        for c in ciks:
            c = str(int(c))
            if c not in subs:
                d = sec.submissions(c)
                subs[c] = filings_table(d) if d else []
            rows += subs[c]
        ok_all = True
        for pe, fd in zip(x["quarters"], x["filed"]):
            out["quarters"] += 1

            def near(r):
                try:
                    return abs((date.fromisoformat(r["reportDate"]) - date.fromisoformat(pe)).days) <= 7
                except Exception:
                    return False
            hits = sorted((r for r in rows if r.get("form") in FORMS and near(r)), key=lambda r: r["filingDate"])
            if not hits:
                hits = [r for r in rows if r.get("form") in FORMS and r.get("filingDate") == fd]
            q = dict(period_end=pe, vendor_filed=fd)
            if not hits:
                out["not_found"] += 1
                q["result"] = "SEC filing not found"
                ok_all = False
            else:
                out["sec_found"] += 1
                f0 = hits[0]["filingDate"]
                q.update(sec_first_filed=f0, sec_form=hits[0]["form"])
                v2 = f0 < x["baseline_selection"]
                v3 = fd >= f0
                out["V2_violations"] += int(not v2)
                out["V3_vendor_before_sec"] += int(not v3)
                q["result"] = "ok" if v2 and v3 else "VIOLATION"
                ok_all &= v2 and v3
            it["quarters"].append(q)
        out["samples_all_quarters_verified"] += int(ok_all)
        it["result"] = "ok" if ok_all else "see quarters"
        out["items"].append(it)
    (HERE / "P7_CP3R_sec_check.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print({k: v for k, v in out.items() if k != "items"})


if __name__ == "__main__":
    sys.exit(main())
