"""OS-1 / H032 (owner D278 item 2): offline verification, BEFORE any freeze, that the approved fiscal-year
definitions can be computed from the SAME 10-K (prior-year revenue comparative in the same filing) with adequate
coverage. Public SEC data only (the UCR-1 object + the H032 extension object built by build_os1_sec.py); counts only,
NO RETURNS, no QuantConnect.

Population: identical to the OS-CP1b study (research/os/os_cp1b_filter_coverage.py): UCR-1 registrants alive at the
month-end t (latest periodic filing <= 200 days old), common by their latest filing, point-in-time public float
>= $2B; non-financial = SIC of the latest periodic filing filed before t outside 6000-6799 (H032 rule).

Definitions (the approved H032 definitions, extension object rows k = [filed, period_end, ocf, rev, rev_prior]):
  the latest ORIGINAL 10-K / 10-KT filed strictly before t, with period_end < filed and t - period_end <= 456 days;
  F-OCF input present  : its ocf is not null;
  F-REV input present  : rev and rev_prior (same filing, same tag) not null and rev_prior > 0;
  NSI present          : as in the OS-CP1b study (cover counts ~12 months apart, ratio inside [2/3, 3/2]).
  Joint                : all three.

PRE-REGISTERED ADEQUACY CRITERION (fixed in this file before it is run; committed first):
  A1  pooled 2013-2021: same-filing joint coverage >= the consecutive-filing joint coverage of the OS-CP1b study
      (cov_joint_fy_alt, same population) - 5 percentage points;
  A2  every year 2013-2021: same-filing joint coverage >= 70%.
  Both hold -> ADEQUATE (proceed to the H032 freeze). Otherwise -> NOT ADEQUATE: STOP and report to the owner; no other
  revenue definition is substituted (D278 item 2).
Also reported (never gating): the 2010-2012 years, the $0.5-2B float band, the reasons a row lacks the comparative, and
point-in-time checks on the object (period_end < filed for every row used).
Output: research/os/os1_verify_comparatives.json

    PYTHONPATH=src python research/os/os1_verify_comparatives.py
"""
import bisect
import json
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(Path(__file__).parent)]
import qr_ucr as U  # noqa: E402
from os_cp1b_filter_coverage import month_ends, nsi_ok  # noqa: E402

OUT = Path(__file__).with_name("os1_verify_comparatives.json")
STALE = 456
A1_TOL, A2_MIN = 5.0, 70.0


def financial(sic):
    return sic is not None and 6000 <= int(sic) <= 6799


def main():
    ucr = json.loads((ROOT / "data/sec_derived/ucr_sec_v1.json").read_text())
    ext = json.loads((ROOT / "data/sec_derived/os1_sec_v1.json").read_text())["r"]
    ref = U.RepairRef(ucr)
    prior = json.loads((ROOT / "research/os/os_cp1b_filter_coverage.json").read_text())
    months = [m.toordinal() for m in month_ends()]
    C = defaultdict(lambda: defaultdict(int))
    pit_bad = 0
    for i, cik in enumerate(ref.ciks):
        e = ext[cik]
        p = sorted(ucr["r"][cik]["p"], key=lambda x: x[0])
        if len(p) != len(e["s"]):
            raise SystemExit(f"CIK {cik}: s not parallel to p")
        pday = [date.fromisoformat(x[0]).toordinal() for x in p]
        k = [(date.fromisoformat(r[0]).toordinal(), r) for r in e["k"]]
        kday = [a for a, _ in k]
        for t in months:
            cur = ref.current(i, t)
            if cur is None or not cur[1]:
                continue
            F = ref.float_(i, t)
            if F is None or F < 5e8:
                continue
            band = "float_ge_2B" if F >= 2e9 else "float_0.5_2B"
            j = bisect.bisect_left(pday, t) - 1
            sic = e["s"][j] if j >= 0 else None
            if financial(sic):
                continue
            y = date.fromordinal(t).year
            c = C[(band, y)]
            c["n"] += 1
            nsi = nsi_ok(ref, i, t)
            q = bisect.bisect_left(kday, t) - 1
            row = k[q][1] if q >= 0 else None
            reason = None
            if row is None:
                reason = "no_annual_report"
            elif row[1] is None:
                reason = "no_period"
            else:
                pe = date.fromisoformat(row[1]).toordinal()
                if pe >= k[q][0]:
                    pit_bad += 1
                    reason = "period_not_before_filing"
                elif t - pe > STALE:
                    reason = "stale"
            ocf = reason is None and row[2] is not None
            rev = reason is None and row[3] is not None and row[4] is not None and row[4] > 0
            if reason is None and not rev:
                reason = "no_current_revenue" if row[3] is None else (
                    "no_same_filing_comparative" if row[4] is None else "prior_not_positive")
            c["nsi"] += int(nsi)
            c["ocf"] += int(ocf)
            c["rev"] += int(rev)
            c["joint"] += int(nsi and ocf and rev)
            if reason:
                c["why_" + reason] += 1
    pct = lambda a, b: round(100.0 * a / b, 2) if b else None
    years = {}
    for (band, y), c in sorted(C.items()):
        years.setdefault(band, {})[str(y)] = dict(n=c["n"], nsi=pct(c["nsi"], c["n"]), ocf=pct(c["ocf"], c["n"]),
                                                  rev=pct(c["rev"], c["n"]), joint=pct(c["joint"], c["n"]),
                                                  why={k[4:]: v for k, v in c.items() if k.startswith("why_")})
    base = defaultdict(lambda: [0, 0])
    for cell in prior["cells"]:
        if cell["group"] == "non_financial" and cell["band"] == "float_ge_2B" and 2013 <= cell["year"] <= 2021:
            base[cell["year"]][0] += cell["cov_joint_fy_alt"]
            base[cell["year"]][1] += cell["n"]
    pooled_prior = pct(sum(v[0] for v in base.values()), sum(v[1] for v in base.values()))
    main_ = {y: C[("float_ge_2B", y)] for y in range(2013, 2022)}
    pooled_same = pct(sum(c["joint"] for c in main_.values()), sum(c["n"] for c in main_.values()))
    a1 = pooled_same is not None and pooled_prior is not None and pooled_same >= pooled_prior - A1_TOL
    a2 = all(pct(c["joint"], c["n"]) >= A2_MIN for c in main_.values())
    out = dict(study="OS1 same-filing comparative verification", decision="D278",
               criterion=dict(A1=f"pooled 2013-2021 joint >= consecutive-filing joint - {A1_TOL} points",
                              A2=f"every year 2013-2021 joint >= {A2_MIN}%"),
               pooled_2013_2021=dict(same_filing_joint=pooled_same, consecutive_filing_joint=pooled_prior),
               A1=a1, A2=a2, verdict="ADEQUATE" if (a1 and a2) else "NOT ADEQUATE",
               pit_period_not_before_filing=pit_bad, years=years)
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in ("pooled_2013_2021", "A1", "A2", "verdict", "pit_period_not_before_filing")}, indent=1))


if __name__ == "__main__":
    main()
