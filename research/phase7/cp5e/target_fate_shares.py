"""P7-CP5e (D188) items 2-8: what happened to the frozen target securities, and how often public SEC cover-page share
counts are available for them, from PUBLIC SEC data only (EDGAR submissions and XBRL company facts, cached) and our
own membership tables. Only filings dated on or before 2017-12-31 are used (no 2018+ information).

Fate (securities not in the data-v1 universe at 2017-12-29), by the registrant (identity-v2 CIK at the security's
last target review):
  acquired_or_merged  a deregistration (15-12B/15-12G/15-15D) or exchange removal (25/25-NSE) filed after the last
                      target review and by 2017-12-31, with merger evidence from 365 days before that review onwards
                      (DEFM14A/DEFM14C/PREM14A/SC 14D9/SC TO-T/425, or an 8-K item 2.01);
  delisted_other      such a form without merger evidence;
  alive_end_2017      still filing 10-K/10-Q in 2017-H2 (fell below a universe filter, or other reason);
  stopped_unknown     stopped filing without either; no_cik when no identity row exists.
Share counts: for each target stock-month (review t), a single-class cover count from a 10-K/10-Q filed by t
(usable from filed + 1 day) with cover date within 135 days of t (the D111 rule), registrant = identity-v2 CIK at t.
Output: research/phase7/cp5e/target_fate_shares.json."""
import json
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(Path(__file__).parent)]
import qr_sec_data as D  # noqa: E402
from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402
from qresearch.sec_pit import build_company  # noqa: E402

END = date(2017, 12, 31)
MAX_AGE = 135
MERGER = ("DEFM14A", "DEFM14C", "PREM14A", "SC 14D9", "SC TO-T", "425")
GONE = ("15-12B", "15-12G", "15-15D", "25", "25-NSE")


def dd(s):
    return date.fromisoformat(str(s)[:10])


def cik_on(rows, t):
    out = None
    for eff, _s, c in rows or ():
        if dd(eff) <= t:
            out = c
    return int(out) if out not in (None, "") else None


def main():
    tp = json.loads((Path(__file__).parent / "target_population.json").read_text())
    sec = D.load_table()
    sh = sec["sic_history"]
    client = SECClient()
    per = tp["per_review"]
    last_review = {}
    for t, v in per.items():
        for s in v:
            last_review[s] = max(last_review.get(s, t), t)
    old_last = max(per)
    from target_population import load
    old, _ = load()
    survivors = old[max(old)]
    facts_cache, subs_cache = {}, {}

    def shares(cik):
        if cik not in facts_cache:
            cf = client.companyfacts(cik)
            sub = client.submissions(cik)
            recs = build_company(cf, sub) if cf else []
            facts_cache[cik] = sorted((dd(r["filed"]), dd(r["cover_date"]), r["cover_shares"]) for r in recs
                                      if r.get("cover_shares") and r.get("cover_date") and dd(r["filed"]) <= END)
        return facts_cache[cik]

    def subs(cik):
        if cik not in subs_cache:
            s = client.submissions(cik)
            subs_cache[cik] = [r for r in filings_table(s) if dd(r["filingDate"]) <= END] if s else None
        return subs_cache[cik]

    fate = Counter()
    fate_rows = {}
    for sid in tp["sids"]:
        if sid in survivors:
            fate_rows[sid] = "in_universe_end_2017"
            continue
        lr = dd(last_review[sid])
        cik = cik_on(sh.get(sid), lr)
        if cik is None:
            fate_rows[sid] = "no_cik"
            continue
        fl = subs(cik)
        if fl is None:
            fate_rows[sid] = "no_submissions"
            continue
        gone = [dd(r["filingDate"]) for r in fl if r["form"] in GONE and dd(r["filingDate"]) > lr]
        merger = any((r["form"] in MERGER or (r["form"] == "8-K" and "2.01" in str(r.get("items") or "")))
                     and dd(r["filingDate"]) >= lr - timedelta(days=365) for r in fl)
        alive = any(r["form"] in ("10-K", "10-Q") and dd(r["filingDate"]) >= date(2017, 7, 1) for r in fl)
        if gone:
            fate_rows[sid] = "acquired_or_merged" if merger else "delisted_other"
        elif alive:
            fate_rows[sid] = "alive_end_2017"
        else:
            fate_rows[sid] = "stopped_unknown"
    fate = Counter(fate_rows.values())
    sm = Counter()
    by_year = {}
    for t, v in per.items():
        td = dd(t) + timedelta(days=1)                      # the selection day reflecting review session t
        y = by_year.setdefault(t[:4], Counter())
        for s in v:
            cik = cik_on(sh.get(s), td)
            k = "no_cik"
            if cik is not None:
                usable = [(f, c, n) for f, c, n in shares(cik) if f + timedelta(days=1) <= td]
                if not usable:
                    k = "no_cover_count"
                else:
                    f, c, n = max(usable, key=lambda x: (x[1], x[0]))
                    k = "fresh" if (td - c).days <= MAX_AGE else "stale"
            sm[k] += 1
            y[k] += 1
            y["later_disappearing_" + k] += int(s not in survivors)
    out = dict(fate=dict(fate), share_counts=dict(sm),
               share_counts_fresh_pct=round(100 * sm["fresh"] / sum(sm.values()), 2),
               share_counts_by_year={k: dict(v) for k, v in sorted(by_year.items())},
               targets=len(tp["sids"]), stock_months=sum(len(v) for v in per.values()), sec_requests=client.fetched)
    (Path(__file__).parent / "target_fate_shares.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
