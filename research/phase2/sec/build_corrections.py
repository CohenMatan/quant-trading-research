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


STOP = {"INC", "CORP", "CORPORATION", "CO", "COMPANY", "LTD", "PLC", "THE", "HOLDINGS", "HOLDING", "GROUP", "NV", "SA"}


def ticker_in_name(ticker, name):
    """True if the ticker's letters appear in order in the registrant's name (e.g. PCP ~ PreCision CastParts,
    RSH ~ RadioSHack). Share-class suffixes after a dot are ignored. A weak signal on its own; used only together
    with the float, lifetime and uniqueness evidence."""
    t = "".join(ch for ch in ticker.split(".")[0].upper() if ch.isalpha())
    words = [w for w in "".join(ch if ch.isalnum() else " " for ch in (name or "").upper()).split() if w not in STOP]
    n = "".join(words)
    if not t or not n or t[0] != n[0]:
        return False                      # the ticker must start with the name's first letter
    i = 0
    for ch in n:
        if i < len(t) and ch == t[i]:
            i += 1
    return i == len(t)


def ticker_in_name_relaxed(ticker, name):
    """Tier-2 ticker evidence: all but one letter (not the first) of a ticker of 3+ letters in order in the name
    (TWX ~ Time Warner, FWLT ~ Foster Wheeler). Used only with a tight Form 25/15 end (see decide)."""
    if ticker_in_name(ticker, name):
        return True
    t = "".join(ch for ch in ticker.split(".")[0].upper() if ch.isalpha())
    return len(t) >= 3 and any(ticker_in_name(t[:i] + t[i + 1:], name) for i in range(1, len(t)))


def decide(cands, pairs, nofund):
    """Per registrant: the matched security and the evidence, or the reason it stays unresolved.
    Repaired only if exactly ONE security satisfies all of:
      E1 every evaluated public-float date gives float / (cover shares x raw close) in [0.45, 1.05];
      E2 the security's trading ended within [-45, +200] days of the registrant's equity end (pair construction);
      E3 one of the security's tickers is an in-order letter subsequence of a registrant name in force then;
      E4 at least two float dates evaluated, or one plus a Form 25/15 within 30 days of the last trade;
    and no other registrant claims that security under the same rule (uniqueness both ways).
    Tier 2 (only for registrants without a tier-1 candidate): E3 relaxed (one non-initial ticker letter may be
    absent) but E4 strict: a Form 25/15 within 30 days of the last trade."""
    ok = defaultdict(list)
    ok2 = defaultdict(list)
    for cik, sids in pairs.items():
        c = cands.get(cik)
        if c is None:
            continue
        end = date.fromisoformat(c["end"]) if c["end"] else None
        for sid, st in sids.items():
            if not (st["n_eval"] >= 1 and st["n_in"] == st["n_eval"]):
                continue
            tick = sorted({t for t, a, b in nofund[sid]["tickers"]} | {sid.split()[0]})
            tmatch = [t for t in tick if any(ticker_in_name(t, n) for n in c["names"])]
            ls = nofund[sid]["last_seen"]
            tight = end is not None and c["end_source"] in ("form25", "form15") and abs((ls - end).days) <= 30
            if tmatch and (st["n_eval"] >= 2 or tight):
                ok[cik].append((sid, tmatch, tight))
            elif tight:
                rmatch = [t for t in tick if any(ticker_in_name_relaxed(t, n) for n in c["names"])]
                if rmatch:
                    ok2[cik].append((sid, rmatch, tight))
    tier = {}
    for cik in set(ok) | set(ok2):
        if ok.get(cik):
            tier[cik] = 1
        else:
            ok[cik] = ok2[cik]
            tier[cik] = 2
    claimed = defaultdict(list)
    for cik, lst in ok.items():
        for sid, _, _ in lst:
            claimed[sid].append(cik)
    res = {}
    for cik, c in cands.items():
        ev = {"pairs_tested": len(pairs.get(cik, {})),
              "float_pass": sorted(s for s, st in pairs.get(cik, {}).items() if st["n_eval"] >= 1 and st["n_in"] == st["n_eval"]),
              "all_rules_pass": [x[0] for x in ok.get(cik, [])]}
        if c["non_common_name"] or c["non_common_sic"]:
            res[cik] = ("unresolved", "not an operating-company common stock (name/SIC)", None, ev)
        elif not c["end"] or c["end"] >= "2021-10-01":
            res[cik] = ("unresolved", "equity still listed after 2021 (not the D043 population; native-cover check)", None, ev)
        elif not c["float_obs"]:
            res[cik] = ("unresolved", "no public-float observation with a single-class cover count", None, ev)
        elif not ok.get(cik):
            res[cik] = ("unresolved", "no QuantConnect security passes all identity rules", None, ev)
        elif len(ok[cik]) > 1:
            res[cik] = ("unresolved", f"ambiguous: {len(ok[cik])} securities pass", None, ev)
        else:
            sid, tmatch, tight = ok[cik][0]
            if len(claimed[sid]) > 1:
                res[cik] = ("unresolved", f"ambiguous: security passes for {len(claimed[sid])} registrants", sid, ev)
                continue
            st = pairs[cik][sid]
            conf = ("high" if (st["n_eval"] >= 2 and tight) else "medium") if tier[cik] == 1 else "medium (tier 2)"
            ev.update(st=st, ticker_evidence=tmatch, last_seen=str(nofund[sid]["last_seen"]), equity_end=c["end"],
                      end_source=c["end_source"], end_tight=tight)
            res[cik] = ("repaired", conf, sid, ev)
    return res


def main(exp="E971-02"):
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
    holds = json.loads((OUT / "timing_holds.json").read_text())
    releases = json.loads((OUT / "quarantine_release.json").read_text())
    for name, text in pack({"corrections": table, "timing_holds": holds, "quarantine_releases": releases},
                           "qr_sec_data").items():
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
