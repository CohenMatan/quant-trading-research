"""OS-CP1b (owner D276): offline coverage study of the proposed OS-1 quality filters. Public SEC data only, from
the local cache (no network, no QuantConnect data, NO RETURNS, no strategy result of any kind).

Population (SEC side, point-in-time at each month-end t, 2010-01 .. 2021-11): registrants of the UCR-1 object
`rr/ucr_sec_v1.json` (local copy data/sec_derived/ucr_sec_v1.json) that are alive at t (latest periodic filing filed
before t and at most 200 days old), common by their latest filing, and have a point-in-time public float >= $2B
(qr_ucr rules; float is a lower bound of market cap, so this is a conservative 'large company' proxy). A second band
(float $0.5-2B) is reported separately.

Inputs at t, from filings filed strictly before t (values as first filed, qresearch.sec_pit):
  NSI  : cover-share counts ~12 months apart (+/-45 days), ratio inside [2/3, 3/2] (split adjustment is in-cloud
         only; here a split shows up as an out-of-bound ratio and is counted as missing).
  TTM  : True TTM = sum of the four latest consecutive quarterly values (quarter gaps 80-100 days), the latest
         quarter filed at most 200 days before t; prior TTM = the four quarters before those.
         REVG = TTM revenue / prior TTM revenue - 1; FCF = TTM (operating cash flow - capex), capex tag
         PaymentsToAcquirePropertyPlantAndEquipment (sec_pit); OCF and NI TTM reported for comparison.
  FY   : fallback definitions from the latest completed fiscal years (10-K totals) instead of rolling quarters.
Groups: SIC of the latest filing known at t (financial sub-groups, utilities, other), FF12 for non-financials, and
'later disappearing' (no periodic filing after 2021-06-30 in the filing index; descriptive label only).
Output: research/os/os_cp1b_filter_coverage.json (counts and shares only).

    PYTHONPATH=src python research/os/os_cp1b_filter_coverage.py
"""
import bisect
import gzip
import json
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean")]
import qr_ucr as U  # noqa: E402
from qr_xs_diag import ff12  # noqa: E402
from qresearch import sec_pit as P  # noqa: E402

CACHE = ROOT / "data/sec_cache/data.sec.gov/api/xbrl/companyfacts"
OUT = Path(__file__).with_name("os_cp1b_filter_coverage.json")
FRESH = 200
GAP = (80, 100)
BOUND = (2 / 3, 3 / 2)


def month_ends():
    out = []
    for y in range(2010, 2022):
        for m in range(1, 13):
            if (y, m) > (2021, 11):
                break
            nxt = date(y + (m == 12), m % 12 + 1, 1)
            out.append(nxt - timedelta(days=1))
    return out


def group(sic):
    if sic is None:
        return "unknown_sic"
    s = int(sic)
    if 6000 <= s <= 6199:
        return "banks"
    if 6300 <= s <= 6411:
        return "insurance"
    if s == 6798:
        return "reit"
    if 6200 <= s <= 6799:
        return "other_financial"
    if 4900 <= s <= 4999:
        return "utilities"
    return "non_financial"


def quarters(records):
    """period_end -> (filed ordinal, values) of the FIRST filing reporting that period (as first filed)."""
    q = {}
    for r in sorted(records, key=lambda r: (r["filed"], r["accn"])):
        pe = r["period_end"]
        if pe not in q:
            q[pe] = (date.fromisoformat(r["filed"]).toordinal(), date.fromisoformat(pe).toordinal(), r["values"],
                     r["form"])
    return sorted(q.values(), key=lambda x: x[1])


def chain(qs, t):
    """Up to 8 consecutive quarters (newest first) known before t, newest filed <= FRESH days before t."""
    known = [x for x in qs if x[0] < t]
    if not known or t - max(x[0] for x in known) > FRESH:
        return []
    known.sort(key=lambda x: x[1])
    out = [known[-1]]
    for x in reversed(known[:-1]):
        if len(out) == 8:
            break
        gap = out[-1][1] - x[1]
        if gap < GAP[0]:
            continue
        if gap > GAP[1]:
            break
        out.append(x)
    return out


def ttm(qs4, key):
    vals = [x[2].get(key) for x in qs4]
    if len(qs4) < 4 or any(v is None for v in vals):
        return None
    return sum(vals)


def fy_vals(records, t):
    """Latest two completed fiscal-year totals known before t (10-K / 10-KT records), as first filed."""
    fy = {}
    for r in sorted(records, key=lambda r: (r["filed"], r["accn"])):
        if r["form"].startswith("10-K") and date.fromisoformat(r["filed"]).toordinal() < t:
            fy.setdefault(r["period_end"], r["values"])
    ends = sorted(fy)
    if not ends or t - date.fromisoformat(ends[-1]).toordinal() > 456:
        return None, None
    prev = None
    if len(ends) >= 2 and 330 <= date.fromisoformat(ends[-1]).toordinal() - date.fromisoformat(ends[-2]).toordinal() <= 400:
        prev = fy[ends[-2]]
    return fy[ends[-1]], prev


def nsi_ok(ref, i, t):
    s = ref.shares(i, t)
    if s is None:
        return False
    s1, e1 = s
    best = None
    for day, val, end in zip(ref.s_day[i], ref.s_val[i], ref.s_end[i]):
        if day >= t:
            break
        dev = abs(end - (e1 - 365))
        if dev <= 45 and (best is None or dev < best[0]):
            best = (dev, val)
    return best is not None and BOUND[0] <= s1 / best[1] <= BOUND[1]


def main():
    doc = json.loads((ROOT / "data/sec_derived/ucr_sec_v1.json").read_text())
    ref = U.RepairRef(doc)
    idx = json.load(gzip.open(ROOT / "data/sec_derived/xbrl_filings.json.gz", "rt"))
    sic_hist, last_filed = defaultdict(list), {}
    for r in idx:
        c = str(r["cik"])
        if r["form"] in P.PERIODIC_FORMS:
            sic_hist[c].append((date.fromisoformat(r["filed"]).toordinal(), r.get("sic")))
            last_filed[c] = max(last_filed.get(c, ""), r["filed"])
    for v in sic_hist.values():
        v.sort(key=lambda x: x[0])
    months = [m.toordinal() for m in month_ends()]
    cut = date(2021, 6, 30).isoformat()
    C = defaultdict(lambda: defaultdict(int))       # (band, year, group, dis) -> counter
    S = defaultdict(lambda: defaultdict(int))       # (year, ff12) -> counter for non-financial float >= $2B
    no_facts = 0
    for i, cik in enumerate(ref.ciks):
        p = CACHE / f"CIK{int(cik):010d}.json.gz"
        if not p.exists():
            no_facts += 1
            continue
        cf = json.load(gzip.open(p, "rt"))
        recs = P.build_company(cf, None)
        qs = quarters(recs)
        dis = "disappearing" if last_filed.get(cik, "") <= cut else "survivor"
        sh = sic_hist.get(cik, [])
        for t in months:
            cur = ref.current(i, t)
            if cur is None or not cur[1]:
                continue
            F = ref.float_(i, t)
            if F is None or F < 5e8:
                continue
            band = "float_ge_2B" if F >= 2e9 else "float_0.5_2B"
            k = bisect.bisect_left([x[0] for x in sh], t) - 1
            sic = sh[k][1] if k >= 0 else None
            g = group(sic)
            y = date.fromordinal(t).year
            c = C[(band, y, g, dis)]
            c["n"] += 1
            nsi = nsi_ok(ref, i, t)
            ch = chain(qs, t)
            q4, p4 = ch[:4], ch[4:8]
            rev, revp = ttm(q4, "revenue_q"), ttm(p4, "revenue_q")
            fcf, ocf, ni = ttm(q4, "free_cash_flow_q"), ttm(q4, "operating_cash_flow_q"), ttm(q4, "net_income_q")
            revg = (rev / revp - 1) if (rev is not None and revp and revp > 0) else None
            fy, fyp = fy_vals(recs, t)
            fy_rev = fy and fy.get("revenue_ttm")
            fyp_rev = fyp and fyp.get("revenue_ttm")
            fy_revg = (fy_rev / fyp_rev - 1) if (fy_rev is not None and fyp_rev and fyp_rev > 0) else None
            fy_fcf = fy and fy.get("free_cash_flow_ttm")
            fy_ocf = fy and fy.get("operating_cash_flow_ttm")
            flags = dict(nsi=nsi, revg=revg is not None, fcf=fcf is not None, ocf=ocf is not None, ni=ni is not None,
                         fy_revg=fy_revg is not None, fy_fcf=fy_fcf is not None,
                         ocf_no_capex=(ocf is not None and fcf is None))
            for kk, v in flags.items():
                c["cov_" + kk] += int(bool(v))
            joint = nsi and revg is not None and fcf is not None
            joint_fy = nsi and fy_revg is not None and fy_fcf is not None
            c["cov_joint_ttm"] += int(joint)
            c["cov_joint_fy"] += int(joint_fy)
            c["cov_joint_ttm_or_fy"] += int(nsi and (revg is not None or fy_revg is not None)
                                             and (fcf is not None or fy_fcf is not None))
            if fcf is not None:
                c["pass_fcf"] += int(fcf > 0)
            if revg is not None:
                c["pass_revg"] += int(revg > 0)
            if ocf is not None:
                c["pass_ocf"] += int(ocf > 0)
            if ni is not None:
                c["pass_ni"] += int(ni > 0)
            if joint:
                both = fcf > 0 and revg > 0
                c["pass_both_given_joint"] += int(both)
            if band == "float_ge_2B" and g == "non_financial":
                s = S[(y, ff12(sic))]
                s["n"] += 1
                s["joint"] += int(joint)
                if joint:
                    s["pass_both"] += int(fcf > 0 and revg > 0)
        if i % 500 == 0:
            print(i, len(ref.ciks), flush=True)
    out = dict(meta=dict(study="OS-CP1b", decision="D276", population="ucr_sec_v1 registrants, alive, common, PIT float",
                         months=len(months), registrants=len(ref.ciks), without_companyfacts=no_facts,
                         note="counts are registrant-months; no returns"),
               cells=[dict(band=b, year=y, group=g, life=d, **v) for (b, y, g, d), v in sorted(C.items())],
               ff12=[dict(year=y, ff12=f, **v) for (y, f), v in sorted(S.items())])
    OUT.write_text(json.dumps(out, indent=0, sort_keys=True) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
