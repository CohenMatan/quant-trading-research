"""Build the dated SEC correction layer for the D043 survivorship gap (D111) from the X971 identity fingerprints.

Identity evidence for a (QuantConnect security without fundamentals, SEC registrant) pair — all historical:
  E1 public-float consistency: at each 10-K public-float date, float / (cover shares x QuantConnect raw close) must
     lie in [0.45, 1.05] (float = market value held by non-affiliates <= market cap; a wrong pair gives arbitrary
     ratios); every evaluated date must pass;
  E2 lifetime: the security was liquid at the float dates, and its trading ended within [-45, +200] days of the
     registrant's equity end (Form 25 delisting, Form 15 deregistration or last periodic report), or both continue;
  E3 uniqueness: exactly one security passes for the registrant, and the security passes for no other registrant.
Status: 'repaired' if E1 (>= 2 dates, or 1 date plus a Form 25/15 end within 30 days of the last trade), E2, E3
and the US-common checks hold; otherwise 'unresolved' (never used) with the reason.

US-common checks (historical names, SEC form types): 10-K/10-Q filer (20-F/40-F foreign issuers are not
candidates); no partnership/LLC/trust/fund name in force during the period; SIC not a fund/blank-check/royalty
trust code. Listing exchange is checked live in the X972 canary (QuantConnect primary exchange).

Outputs: src/qresearch/lean/qr_sec_data*.py (packed table), research/phase2/sec/corrections.json (audit table:
every correction with its source filings, dates, method and status), research/phase2/sec/unresolved.json."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from qresearch.sec_edgar import SECClient  # noqa: E402
from qresearch.sec_pack import pack  # noqa: E402
from qresearch.sec_pit import build_company  # noqa: E402
import e970_parse  # noqa: E402

OUT = Path(__file__).parent
LEAN = ROOT / "src" / "qresearch" / "lean"


def load_pairs(exp):
    out = defaultdict(dict)
    for line in e970_parse.lines(exp):
        p = line.split("|")
        if p[0] == "P":
            cik, sid, n, k, rs = p[1], p[2], int(p[3]), int(p[4]), [float(x) for x in p[5].split(",")]
            out[cik][sid] = {"n_eval": n, "n_in": k, "ratios": rs}
    return out


def decide(cands, pairs, nofund):
    """Per registrant: the matched security and the evidence, or the reason it stays unresolved."""
    passing = defaultdict(list)
    for cik, sids in pairs.items():
        for sid, st in sids.items():
            if st["n_eval"] >= 1 and st["n_in"] == st["n_eval"]:
                passing[cik].append(sid)
    claimed = defaultdict(list)
    for cik, sids in passing.items():
        for sid in sids:
            claimed[sid].append(cik)
    res = {}
    for cik, c in cands.items():
        sids = passing.get(cik, [])
        ev = {"pairs_tested": len(pairs.get(cik, {})), "passing": sids}
        if c["non_common_name"] or c["non_common_sic"]:
            res[cik] = ("unresolved", "not an operating-company common stock (name/SIC)", None, ev)
            continue
        if not c["float_obs"]:
            res[cik] = ("unresolved", "no public-float observation with a single-class cover count", None, ev)
            continue
        if not sids:
            res[cik] = ("unresolved", "no QuantConnect security passes the float test", None, ev)
            continue
        if len(sids) > 1:
            res[cik] = ("unresolved", f"ambiguous: {len(sids)} securities pass", None, ev)
            continue
        sid = sids[0]
        if len(claimed[sid]) > 1:
            res[cik] = ("unresolved", f"ambiguous: security passes for {len(claimed[sid])} registrants", None, ev)
            continue
        st = pairs[cik][sid]
        ls = nofund[sid]["last_seen"]
        end = date.fromisoformat(c["end"]) if c["end"] else None
        tight = end is not None and c["end_source"] in ("form25", "form15") and abs((ls - end).days) <= 30
        if st["n_eval"] >= 2:
            conf = "high" if (tight or st["n_eval"] >= 3) else "medium"
        elif tight:
            conf = "medium"
        else:
            res[cik] = ("unresolved", "only one float date and no Form 25/15 within 30 days of the last trade",
                        sid, ev)
            continue
        ev.update(st=st, last_seen=str(ls), equity_end=c["end"], end_source=c["end_source"], end_tight=tight)
        res[cik] = ("repaired", conf, sid, ev)
    return res


def main(exp="E971-01"):
    t = e970_parse.load()
    cj = json.loads((OUT / "candidates.json").read_text())
    cands = cj["candidates"]
    pairs = load_pairs(exp)
    dec = decide(cands, pairs, t["nofund"])
    client = SECClient()
    table, audit, unresolved = {}, {}, {}
    for cik, (status, why, sid, ev) in sorted(dec.items()):
        c = cands[cik]
        if status != "repaired":
            unresolved[cik] = {"name": c["name"], "reason": why, "security": sid, "equity_end": c["end"],
                               "max_float": max((o[1] for o in c["float_obs"]), default=None), "evidence": ev}
            continue
        recs = build_company(client.companyfacts(int(cik)), client.submissions(int(cik)))
        recs = [r for r in recs if r["filed"] <= "2021-12-31"]
        rows = [[r["accn"], r["form"], r["filed"], r["period_end"], r["cover_date"], r["cover_shares"],
                 {k: v for k, v in r["values"].items() if v is not None}] for r in recs]
        table[sid] = {"cik": int(cik), "name": c["name"], "status": "repaired", "confidence": why,
                      "method": "SEC XBRL cover shares x QuantConnect raw close (live split adjustment); "
                                "statement totals as first filed", "filings": rows}
        audit[sid] = {"cik": int(cik), "names": c["names"], "confidence": why, "evidence": ev,
                      "effective_from": min((r[2] for r in rows if r[5]), default=None),
                      "effective_to_last_trade": ev["last_seen"],
                      "filings": [{"accn": r[0], "form": r[1], "filed": r[2], "period_end": r[3], "cover_date": r[4],
                                   "cover_shares": r[5]} for r in rows]}
    for p in LEAN.glob("qr_sec_data*.py"):
        p.unlink()
    for name, text in pack(table, "qr_sec_data").items():
        (LEAN / name).write_text(text)
    (OUT / "corrections.json").write_text(json.dumps(audit, indent=1, sort_keys=True) + "\n")
    (OUT / "unresolved.json").write_text(json.dumps(unresolved, indent=1, sort_keys=True) + "\n")
    summary = defaultdict(int)
    for cik, (status, why, sid, ev) in dec.items():
        summary[f"{status}|{why if status == 'repaired' else why.split(':')[0]}"] += 1
    print(dict(summary))
    return dec


if __name__ == "__main__":
    main()
