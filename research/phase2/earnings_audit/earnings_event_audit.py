"""P2-CP12 Preparatory Study B: SEC 8-K earnings-release event audit, 2010-2021 (owner 2026-10-02).
Infrastructure / data work only: NO prices, NO returns, NO post-event performance, no trading rule.

Inputs
  * E981-01 (X981): every security ever eligible on a month start in the frozen data-v1 universe (>= $2B, price >= $5,
    ADV >= $5M, US common, SEC correction layer): sid, vendor CIK (current-status), SEC-correction CIK(s), dated
    tickers, eligible months, last date seen.
  * SEC submissions (data.sec.gov; cached): every 8-K / 8-K/A with items and acceptance time; other forms for the
    end-of-life classification and the missing-event analysis.
  * SEC XBRL filing index (data/sec_derived/xbrl_filings.json.gz): instance-document ticker prefixes with filing
    dates (point-in-time identity evidence, the identity-v2 rule T).
  * Trading sessions: the E981-01 equity calendar (dates only) plus 2022-01-03 as the next session after the window.

Event rules: qresearch.sec_events (timing classes, 30-day de-duplication, amendments ignored, visibility).

Outputs: research/phase2/earnings_audit/earnings_event_audit.json (+ a sample of the timestamp canary).

    PYTHONPATH=src python research/phase2/earnings_audit/earnings_event_audit.py
"""
from __future__ import annotations

import gzip
import json
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research/phase2/sec"))
from qresearch import sec_events as S  # noqa: E402
from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402
from e970_parse import lines  # noqa: E402

OUT = Path(__file__).with_suffix(".json")
YEARS = range(2010, 2022)
M0 = 2010 * 12


def ym_add(ym, k):
    y, m = divmod(ym // 100 * 12 + ym % 100 - 1 + k, 12)
    return y * 100 + m + 1


def load_universe():
    U = {}
    for ln in lines("E981-01"):
        if not ln.startswith("U|"):
            continue
        _, sid, vcik, ccik, corr, tk, mask, first, last, last_seen = ln.split("|")
        months = [M0 + i for i in range(144) if (int(mask, 16) >> i) & 1]
        tickers = []
        for part in tk.split(";"):
            t, rng = part.rsplit(":", 1)
            a, b = rng.split("-")
            tickers.append((t.upper(), int(a), int(b)))
        ciks = [int(x) for x in ccik.split(",") if x] if corr == "1" and ccik else ([int(vcik)] if vcik.isdigit() else [])
        U[sid] = dict(sid=sid, vcik=int(vcik) if vcik.isdigit() else None, ciks=ciks, corrected=corr == "1",
                      tickers=tickers, months=months, first=int(first), last=int(last), last_seen=last_seen)
    return U


def quarters(months):
    """Calendar quarters (year, q) with at least one eligible month start."""
    return sorted({(m // 12, (m % 12) // 3) for m in months})


def calendar():
    eq = gzip.open(ROOT / "experiments/E981-01/equity.csv.gz").read().decode().splitlines()[1:]
    sess = [date.fromisoformat(r.split(",")[0]) for r in eq]
    return S.Calendar(sess + [date(2022, 1, 3)])


def identity_check(u, prefixes_by_cik):
    """Point-in-time identity evidence for (security, CIK): XBRL instance prefixes equal to a ticker the security
    carried within +-3 months of the filing (identity-v2 rule T)."""
    if u["corrected"]:
        return "verified (identity v2, SEC-corrected security)"
    if not u["ciks"]:
        return "no CIK"
    match = other = 0
    span = (ym_add(u["first"], -3), ym_add(u["last"], 3))
    for cik in u["ciks"]:
        for filed_ym, pfx in prefixes_by_cik.get(cik, ()):
            if not (span[0] <= filed_ym <= span[1]):
                continue
            ok = any(pfx == t and ym_add(a, -3) <= filed_ym <= ym_add(b, 3) for t, a, b in u["tickers"])
            match += ok
            other += not ok
    if match >= 2:
        return "verified (dated ticker evidence)"
    if match == 1:
        return "weak (one dated ticker match)"
    if other >= 2:
        return "contradicted (prefixes never match the security's tickers)"
    return "unverified (no XBRL prefix evidence in span)"


def end_status(u, rows):
    if u["last"] == 202112:
        return "continuing (eligible at end-2021)"
    if u["last_seen"] >= "2021-12-30":
        return "left the universe, still trading"
    end = date.fromisoformat(u["last_seen"])
    bk = acq = False
    for f in rows:
        try:
            fd = date.fromisoformat(str(f["filingDate"])[:10])
        except ValueError:
            continue
        items = S.items_of(f)
        form = str(f.get("form", ""))
        if "1.03" in items and abs((fd - end).days) <= 365:
            bk = True
        if (end - timedelta(days=540)) <= fd <= (end + timedelta(days=30)) and (
                form in ("SC 14D9", "DEFM14A", "PREM14A", "SC TO-T", "S-4") or "5.01" in items or "2.01" in items):
            acq = True
    if bk:
        return "bankruptcy (8-K Item 1.03)"
    if acq:
        return "acquired / merged"
    return "delisted / other"


def main():
    U = load_universe()
    cal = calendar()
    sec = SECClient()
    xb = json.load(gzip.open(ROOT / "data/sec_derived/xbrl_filings.json.gz"))
    prefixes_by_cik = defaultdict(list)
    for r in xb:
        if r.get("prefix") and r.get("filed"):
            prefixes_by_cik[int(r["cik"])].append((int(r["filed"][:4]) * 100 + int(r["filed"][5:7]), r["prefix"].upper()))
    ciks = sorted({c for u in U.values() for c in u["ciks"]})
    subs, names = {}, {}
    for i, cik in enumerate(ciks):
        d = sec.submissions(cik)
        if d is None:
            continue
        subs[cik] = filings_table(d)
        names[cik] = d.get("name", "")
        if i % 500 == 0:
            print("submissions", i, len(ciks), "fetched", sec.fetched, flush=True)
    tzc = json.loads((Path(__file__).parent / "tz_conventions.json").read_text())["ciks"]
    conv = {int(k): v["convention"] for k, v in tzc.items()}
    events = {}
    lag_days = Counter()
    hour_hist = Counter()
    dup_by_year, amend_by_year, cls_by_year = Counter(), Counter(), defaultdict(Counter)
    same_day_dups = 0
    for cik, rows in subs.items():
        c = conv.get(cik, "UNRESOLVED")
        if c == "UNRESOLVED":                       # never guess a time: such events become UNKNOWN-time
            rows_tz = [dict(f, acceptanceDateTime="") for f in rows]
            r = S.build_events(cik, rows_tz, cal, tz="UTC")
        else:
            r = S.build_events(cik, rows, cal, tz=c)
        events[cik] = r["events"]
        for e in r["events"]:
            if e.acceptance and e.report_date and 2010 <= e.filing_date.year <= 2021:
                lag_days[min((e.acceptance.date() - e.report_date).days, 8)] += 1
                hour_hist[e.acceptance.hour] += 1
        for e in r["events"]:
            y = e.filing_date.year
            if 2010 <= y <= 2021:
                cls_by_year[y][e.cls] += 1
                dup_by_year[y] += len(e.duplicates)
        for a in r["amendments"]:
            y = int(a.split("-")[1]) + 2000 if a.split("-")[1].isdigit() else None
            if y and 2010 <= y <= 2021:
                amend_by_year[y] += 1
        # same-day duplicates
        acc_dates = Counter(str(f.get("acceptanceDateTime"))[:10] for f in rows
                            if str(f.get("form")) == "8-K" and S.is_earnings_filing(f))
        same_day_dups += sum(v - 1 for v in acc_dates.values() if v > 1)
    # ---- coverage
    cov_year = defaultdict(lambda: Counter())
    by_status = defaultdict(Counter)
    by_identity = defaultdict(Counter)
    missing_cat = defaultdict(Counter)
    missing_examples = Counter()
    id_status = {}
    end_stat = {}
    for sid, u in U.items():
        idc = identity_check(u, prefixes_by_cik)
        id_status[sid] = idc
        rows = [f for c in u["ciks"] for f in subs.get(c, [])]
        st = end_status(u, rows)
        end_stat[sid] = st
        evq = Counter()
        for c in u["ciks"]:
            for e in events.get(c, []):
                if e.event_session is not None:
                    evq[(e.event_session.year, (e.event_session.month - 1) // 3)] += 1
        filed_q = defaultdict(set)
        for f in rows:
            try:
                fd = date.fromisoformat(str(f["filingDate"])[:10])
            except ValueError:
                continue
            filed_q[(fd.year, (fd.month - 1) // 3)].add(str(f.get("form", "")) + "|" + ",".join(S.items_of(f)))
        qs = quarters(u["months"])
        for (y, q) in qs:
            c = cov_year[y]
            c["expected"] += 1
            hit = evq.get((y, q), 0) > 0
            c["observed"] += hit
            by_status[st]["expected"] += 1
            by_status[st]["observed"] += hit
            by_identity[idc]["expected"] += 1
            by_identity[idc]["observed"] += hit
            if hit:
                continue
            prev, nxt = (y, q - 1) if q else (y - 1, 3), (y, q + 1) if q < 3 else (y + 1, 0)
            forms = filed_q.get((y, q), set())
            if not u["ciks"]:
                cat = "no CIK for the security"
            elif idc.startswith("contradicted"):
                cat = "CIK contradicted by dated ticker evidence"
            elif evq.get(prev, 0) > 1 or evq.get(nxt, 0) > 1:
                cat = "timing shift (two events in an adjacent quarter)"
            elif not forms and not filed_q.get(prev) and not filed_q.get(nxt):
                cat = "registrant has no SEC filings around the quarter (successor/predecessor CIK)"
            elif any(x.startswith(("10-Q", "10-K")) for x in forms) and any(
                    x.startswith("8-K|") and ("7.01" in x or "8.01" in x) for x in forms):
                cat = "periodic report filed; results possibly released under 8-K Item 7.01/8.01"
            elif any(x.startswith(("10-Q", "10-K")) for x in forms):
                cat = "periodic report filed without any earnings 8-K"
            elif any(x.startswith(("20-F", "6-K", "40-F", "10-KT")) for x in forms | filed_q.get(prev, set())):
                cat = "foreign or transition-period filer"
            else:
                cat = "other (no earnings 8-K, no periodic report in the quarter)"
            missing_cat[y][cat] += 1
            missing_examples[(sid, ",".join(str(x) for x in u["ciks"]), cat)] += 1
    coverage = {y: dict(eligible_securities=sum(1 for u in U.values() if any(m // 12 == y for m in u["months"])),
                        expected_security_quarters=cov_year[y]["expected"], observed=cov_year[y]["observed"],
                        coverage=cov_year[y]["observed"] / cov_year[y]["expected"]) for y in YEARS}
    # ---- company-level (unique CIK) coverage
    cik_q = defaultdict(set)
    for sid, u in U.items():
        for c in u["ciks"][:1]:
            for q in quarters(u["months"]):
                cik_q[c].add(q)
    comp = Counter()
    for c, qs in cik_q.items():
        evq = {(e.event_session.year, (e.event_session.month - 1) // 3) for e in events.get(c, []) if e.event_session}
        comp["expected"] += len(qs)
        comp["observed"] += len(qs & evq)
    # ---- timestamp canary: EDGAR index page 'Accepted' (Eastern) vs converted JSON time
    rnd = random.Random(20261003)
    pool = [(c, e) for c, evs in events.items() for e in evs if e.acceptance and 2010 <= e.filing_date.year <= 2021]
    by_y = defaultdict(list)
    for c, e in pool:
        by_y[e.filing_date.year].append((c, e))
    sample = [x for y in sorted(by_y) for x in rnd.sample(by_y[y], min(17, len(by_y[y])))]
    canary = []
    for c, e in sample:
        acc = e.accession
        b = sec.get_bytes(f"https://www.sec.gov/Archives/edgar/data/{c}/{acc.replace('-', '')}/{acc}-index.htm") or b""
        m = re.search(rb'Accepted</div>\s*<div class="info">([^<]+)<', b)
        page = m.group(1).decode().strip() if m else None
        canary.append(dict(cik=c, accession=acc, convention=conv.get(c), json_et=str(e.acceptance), index_page=page,
                           match=page == e.acceptance.strftime("%Y-%m-%d %H:%M:%S")))
    # ---- filing date vs acceptance date (EDGAR assigns the next business day after 17:30 ET)
    late = Counter()
    for c, evs in events.items():
        for e in evs:
            if e.acceptance and 2010 <= e.filing_date.year <= 2021:
                same = e.acceptance.date() == e.filing_date
                late["same_date" if same else ("after_1730" if e.acceptance.time() >= S.time(17, 30) else
                                               "differs_before_1730")] += 1
    out = dict(
        universe=dict(securities=len(U), with_cik=sum(1 for u in U.values() if u["ciks"]),
                      corrected=sum(1 for u in U.values() if u["corrected"]), unique_ciks=len(ciks),
                      ciks_with_submissions=len(subs)),
        identity=dict(Counter(id_status.values())),
        coverage_by_year=coverage,
        coverage_company_level=dict(expected=comp["expected"], observed=comp["observed"],
                                    coverage=comp["observed"] / max(comp["expected"], 1)),
        coverage_by_end_status={k: dict(v, coverage=v["observed"] / max(v["expected"], 1)) for k, v in by_status.items()},
        coverage_by_identity={k: dict(v, coverage=v["observed"] / max(v["expected"], 1)) for k, v in by_identity.items()},
        securities_by_end_status=dict(Counter(end_stat.values())),
        timing_by_year={y: dict(cls_by_year[y]) for y in YEARS},
        timing_total=dict(sum((cls_by_year[y] for y in YEARS), Counter())),
        duplicates_by_year={y: dup_by_year[y] for y in YEARS}, same_day_duplicate_filings=same_day_dups,
        amendments_by_year={y: amend_by_year[y] for y in YEARS},
        missing_by_year={y: dict(missing_cat[y]) for y in YEARS},
        missing_total=dict(sum((missing_cat[y] for y in YEARS), Counter())),
        missing_top=[dict(sid=s, ciks=c, category=k, quarters=n, name=names.get(int(c.split(",")[0]), "") if c else "")
                     for (s, c, k), n in missing_examples.most_common(40)],
        timestamp_canary=dict(sample=len(canary), matches=sum(x["match"] for x in canary),
                              with_index_page=sum(x["index_page"] is not None for x in canary), rows=canary),
        tz_conventions=dict(Counter(conv.values())),
        acceptance_minus_report_date_days={k: lag_days[k] for k in sorted(lag_days)},
        acceptance_hour_et={h: hour_hist[h] for h in sorted(hour_hist)},
        filing_date_vs_acceptance=dict(late),
        sec_requests=dict(fetched=sec.fetched, cache_hits=sec.cache_hits))
    OUT.write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps({k: out[k] for k in ("universe", "identity", "coverage_company_level", "timing_total",
                                          "missing_total", "filing_date_vs_acceptance")}, indent=1, default=str))
    print("coverage", {y: round(v["coverage"], 3) for y, v in coverage.items()})
    print("canary", out["timestamp_canary"]["matches"], "/", out["timestamp_canary"]["sample"])


if __name__ == "__main__":
    main()
