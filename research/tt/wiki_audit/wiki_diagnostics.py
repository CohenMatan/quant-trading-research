"""POST-HOC diagnostics for the WIKI audit (D300). Written AFTER the frozen gates were computed.

These do not change any gate, threshold or classification in WIKI_AUDIT_result.json. They only explain the three
failing gates (A4, A5, A6) and check whether WIKI price histories end where the SEC records an exit (owner item 5).
Aggregates only: no ticker, row or price series is printed or written.

Usage:  python research/tt/wiki_audit/wiki_diagnostics.py data/wiki/<file>.csv
Output: research/tt/wiki_audit/WIKI_DIAGNOSTICS_posthoc.json
"""
from __future__ import annotations

import gzip
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import sec_reference as sr  # noqa: E402
import wiki_audit as wa  # noqa: E402

OUT = HERE / "WIKI_DIAGNOSTICS_posthoc.json"


def filing_spans(filings) -> dict:
    """prefix -> {cik: (first, last) periodic filing date in 2010-2017}."""
    out = defaultdict(dict)
    for r in filings:
        if r["form"] in sr.PERIODIC and "2010-01-01" <= r["filed"] <= "2017-12-31" and r["prefix"]:
            p, c = r["prefix"].upper(), int(r["cik"])
            a, b = out[p].get(c, (r["filed"], r["filed"]))
            out[p][c] = (min(a, r["filed"]), max(b, r["filed"]))
    return out


def ambiguity(cl, spans) -> dict:
    """Split AMBIGUOUS registrant-months: prefix shared in the month vs R2 multi-CIK prefix; the latter into
    concurrent co-filers (other CIK files in an overlapping period: subsidiary / co-registrant pattern) vs
    sequential use (time-disjoint: genuine ticker reuse)."""
    c = Counter()
    for r in cl:
        if r["cls"] != "AMBIGUOUS":
            continue
        if r["prefix_shared"]:
            c["prefix_missing_or_shared_in_month"] += 1
            continue
        mine = spans[r["prefix"]].get(r["cik"])
        others = [v for k, v in spans[r["prefix"]].items() if k != r["cik"]]
        overlap = mine and any(not (b < mine[0] or a > mine[1]) for a, b in others)
        c["r2_multi_cik_concurrent_cofiler" if overlap else "r2_multi_cik_sequential_reuse"] += 1
    return dict(c)


def unexplained_ratio(df) -> dict:
    """Magnitude and proximity of adj/raw ratio changes not on a split / dividend row (frozen definition 5.2 iv)."""
    t = df["ticker"]
    same = t.eq(t.shift(1))
    split = df["split_ratio"].fillna(1.0)
    div = df["ex-dividend"].fillna(0.0)
    ev = (split != 1.0) | (div > 0)
    ratio = df["adj_close"] / df["close"]
    rel = (ratio / ratio.shift(1) - 1).abs()
    chg = (rel > 1e-4) & same
    unexp = chg & ~ev
    near = unexp & (ev.shift(1, fill_value=False) & t.eq(t.shift(1)) | ev.shift(-1, fill_value=False) & t.eq(t.shift(-1)))
    m = rel[unexp]
    yr = df["date"].str[:4]
    return {"unexplained": int(unexp.sum()),
            "magnitude_bins": {"1e-4..1e-3": int(((m > 1e-4) & (m <= 1e-3)).sum()),
                               "1e-3..1e-2": int(((m > 1e-3) & (m <= 1e-2)).sum()),
                               ">1e-2": int((m > 1e-2).sum())},
            "within_1_session_of_event": int(near.sum()),
            "tickers_affected": int(t[unexp].nunique()),
            "by_year": unexp.groupby(yr).sum().astype(int).to_dict()}


def decay_2017(cl, first_filed) -> dict:
    """Non-matched 2017 registrant-months by whether the registrant's first XBRL periodic filing is 2016+ (new
    listings that the WIKI community may never have added) or earlier."""
    out = Counter()
    for r in cl:
        if r["ym"] // 100 != 2017 or r["cls"] == "MATCHED":
            continue
        new = first_filed.get(r["cik"], "9999") >= "2016-01-01"
        out[f"{r['cls']}|{'first_filed_2016+' if new else 'older'}"] += 1
    return dict(out)


def exit_timing(cl, df) -> dict:
    """For registrants that stopped filing (leavers) with any MATCHED month: WIKI's last bar month vs the SEC exit
    month. 'Confirmed market exit' = R3 exit evidence (ACQUIRED / FAILED / DELISTED-OTHER); 'stopped filing only'
    = UNKNOWN."""
    last = df.groupby("ticker")["date"].max()
    seen = {}
    for r in cl:
        if r["left"] and r["cls"] == "MATCHED":
            seen[r["cik"]] = (r["prefix"], r["exit_ym"], r["exit_type"])
    out = defaultdict(Counter)
    for cik, (p, ex, typ) in seen.items():
        lb = last.get(p)
        grp = "confirmed_exit" if typ in ("ACQUIRED", "FAILED", "DELISTED-OTHER") else "stopped_filing_only"
        if lb is None:
            out[grp]["no_bars"] += 1
            continue
        d = sr.months_between(ex, int(lb[:4]) * 100 + int(lb[5:7]))
        out[grp]["wiki_ends_within_+-3m_of_exit" if abs(d) <= 3 else
                 ("wiki_ends_>3m_before_exit" if d < -3 else "wiki_continues_>3m_after_exit")] += 1
    return {k: dict(v) for k, v in out.items()}


def main(path: str):
    man = json.loads(wa.MANIFEST.read_text())
    if wa.sha256(Path(path)) != man["sha256"]:
        raise SystemExit("file SHA-256 does not match WIKI_MANIFEST.json")
    df, _ = wa.load_wiki(Path(path))
    sessions = wa.reference_sessions(df)
    fr = json.load(gzip.open(wa.FRAME, "rt"))
    bars, per_m = wa.month_bars(df, sessions)
    cl = wa.classify(fr["rows"], fr["prefix_ciks"], set(df["ticker"].unique()), bars, per_m)
    filings = sr.load_filings()
    first = {}
    for r in filings:
        if r["form"] in sr.PERIODIC:
            c = int(r["cik"])
            first[c] = min(first.get(c, r["filed"]), r["filed"])
    matched = {r["prefix"] for r in cl if r["cls"] == "MATCHED"}
    res = {"status": "POST-HOC DIAGNOSTICS — do not alter the frozen A1-A7 result",
           "ambiguous_breakdown": ambiguity(cl, filing_spans(filings)),
           "unexplained_ratio_changes_matched_tickers": unexplained_ratio(df[df["ticker"].isin(matched)].reset_index(drop=True)),
           "non_matched_2017": decay_2017(cl, first),
           "leaver_exit_timing": exit_timing(cl, df)}
    OUT.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
