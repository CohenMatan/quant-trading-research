"""P7-CP5c (D184): build the X995 probe's packed SEC reference table (public SEC data only).
  * the P2-CP6 X971 sample exactly as committed (strategies/X971_sec_verification/sec_ref*.py, unpacked);
  * the pre-registered supplementary sample S2 (research/phase7/cp5c/sample_s2.json): for each company the SEC
    periodic filings (10-K / 10-Q and amendments, statement totals AS FIRST FILED, filing dates) and, for every SEC
    period end, every filing that later reported that period (period_versions: original, amendments, restated
    comparatives) -- the restatement-vintage reference.
Identity-fingerprint inputs (X971 P lines) are dropped (float_obs, pairs empty).
Output: strategies/X995_timing_probe/p5c_ref*.py and research/phase7/cp5c/x995_ref_summary.json."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from qresearch.sec_edgar import SECClient  # noqa: E402
from qresearch.sec_pack import pack, unpack  # noqa: E402
from qresearch.sec_pit import build_company, index_facts, period_versions  # noqa: E402

STRAT = ROOT / "strategies" / "X995_timing_probe"
X971 = ROOT / "strategies" / "X971_sec_verification"


def compact(vals):
    return {k: v for k, v in vals.items() if v is not None}


def main():
    files = {p.name: p.read_text() for p in X971.glob("sec_ref*.py")}
    base = unpack(files, "sec_ref")
    sample = dict(base["sample"])
    s2 = json.loads((Path(__file__).parent / "sample_s2.json").read_text())
    client = SECClient()
    added, nofacts = 0, 0
    for x in s2["sample"]:
        cik = int(x["cik"])
        cf = client.companyfacts(cik)
        sub = client.submissions(cik)
        key = str(cik)
        if key in sample:                     # already in the X971 sample (excluded by construction)
            sample[key]["sids"] = sorted(set(sample[key]["sids"]) | {x["sid"]})
            continue
        if not cf:
            sample[key] = {"sids": [x["sid"]], "why": ["S2:" + x["category"]], "records": [], "versions": {},
                           "note": "no XBRL company facts"}
            nofacts += 1
            continue
        facts = index_facts(cf)
        recs = [r for r in build_company(cf, sub) if "2008-06-30" <= r["period_end"] <= "2021-12-31"]
        pes = sorted({r["period_end"] for r in recs if r["period_end"] <= "2017-12-31"})
        sample[key] = {
            "sids": [x["sid"]], "why": ["S2:" + x["category"]], "name": cf.get("entityName"),
            "records": [[r["accn"], r["form"], r["filed"], r["period_end"], r["cover_date"], r["cover_shares"],
                         compact(r["values"])] for r in recs],
            "versions": {pe: [[v["accn"], v["form"], v["filed"], v["values"]] for v in period_versions(facts, pe)]
                         for pe in pes},
        }
        added += 1
    table = {"sample": sample, "float_obs": {}, "pairs": {}}
    for p in STRAT.glob("p5c_ref*.py"):
        p.unlink()
    out = pack(table, "p5c_ref")
    for name, text in out.items():
        (STRAT / name).write_text(text)
    summ = dict(companies=len(sample), x971_companies=len(base["sample"]), s2_added=added, s2_no_facts=nofacts,
                sec_requests=client.fetched, cache_hits=client.cache_hits, parts=len(out) - 1,
                records=sum(len(c.get("records", ())) for c in sample.values()))
    (Path(__file__).parent / "x995_ref_summary.json").write_text(json.dumps(summ, indent=1) + "\n")
    print(summ)


if __name__ == "__main__":
    main()
