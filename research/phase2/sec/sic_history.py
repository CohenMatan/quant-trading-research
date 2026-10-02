"""Historical industry classification per security from SEC-assigned SIC codes (D113, owner item 10).

The SEC assigns each registrant a SIC code; the monthly XBRL RSS records it AS OF EACH FILING (it changes over time,
e.g. American Tower 4899 -> 6798 when it became a REIT in 2012). For each security the table lists the SIC carried
by each periodic filing of the registrant(s) behind it, effective from the day after the filing date.

Registrant behind a security:
  * native securities: the vendor CIK — only for filings made while the vendor CIK was actually the filer; where the
    vendor CIK is a later successor, the registrant whose filings carry the security's ticker (instance-name prefix
    = the security's QuantConnect ticker within +-3 months, >= 2 filings, unique) — the same evidence as identity v2;
    the predecessor must not be a company QuantConnect covers itself, must have stopped filing within 120 days
    after the vendor CIK's first filing, and must carry market-cap evidence for this security (E971-02 'Q': SEC
    cover shares x close within 3% of the security's point-in-time market cap on >= 2 float dates and >= half of
    them). D113a: instance prefixes alone attached shells to real securities (e.g. 'Global Gard' to GG); without
    a qualifying predecessor the filing-structure rule decides until the vendor CIK's first filing;
  * repaired securities: their linked registrant(s).
Never current-status metadata. Output: {sid: [[effective_date, sic, cik], ...]} (changes only)."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))
import e970_parse  # noqa: E402
import rss_index  # noqa: E402
from identity_v2 import ym, ym_add  # noqa: E402

OUT = Path(__file__).parent


def market_cap_evidence():
    """(cik, sid) pairs whose SEC cover shares x QuantConnect close matched the security's point-in-time market cap
    within 3% on >= 2 float dates and >= half of them (E971-02 'Q' lines)."""
    out = set()
    for l in e970_parse.lines("E971-02"):
        if l.startswith("Q|"):
            _, c, s, n, k = l.split("|")
            if int(k) >= 2 and int(k) >= 0.5 * int(n):
                out.add((int(c), s))
    return out


def build(links):
    """links: {sid: [cik, ...]} for repaired securities."""
    t = e970_parse.load()
    rows = [r for r in rss_index.load() if r["form"] in ("10-K", "10-Q", "10-K/A", "10-Q/A") and r["sic"]
            and "2009-06-01" <= r["filed"] <= "2021-12-31"]
    by_cik = defaultdict(list)
    by_prefix = defaultdict(list)
    for r in rows:
        by_cik[r["cik"]].append(r)
        if r["prefix"]:
            by_prefix[r["prefix"].replace(".", "")].append(r)
    native_cik = {n["cik"] for n in t["native"].values() if n["cik"]}
    qev = market_cap_evidence()
    out, source = {}, defaultdict(int)
    for sid, n in t["native"].items():
        ev = list(by_cik.get(n["cik"], ()))
        # ticker-evidenced registrant(s) for periods before the vendor CIK filed (successor CIKs)
        first_own = min((r["filed"] for r in ev), default="9999")
        cand = defaultdict(list)
        for tk in n["tickers"]:
            for r in by_prefix.get(tk.replace(".", "").upper(), ()):
                if r["cik"] != n["cik"] and r["filed"] < first_own and ym_add(n["first"], -3) <= ym(r["filed"]) <= ym_add(n["last"], 3):
                    cand[r["cik"]].append(r)
        # a predecessor is a registrant that STOPPED filing when the vendor CIK took over (successions): never a
        # company QuantConnect covers itself, never one still filing more than 120 days after the vendor CIK's
        # first filing (D113a: Arlington Asset 'AI' was attached to C3.ai's 'AI' by the earlier rule)
        stop_by = (date.fromisoformat(first_own) + timedelta(days=120)).isoformat() if first_own != "9999" else "9999"
        good = [c for c, lst in cand.items() if len({x["filed"] for x in lst}) >= 2 and c not in native_cik
                and max(r["filed"] for r in by_cik[c]) <= stop_by and (c, sid) in qev]
        if len(good) == 1:
            ev += cand[good[0]]
            source["native+ticker-evidenced predecessor"] += 1
        else:
            source["native vendor CIK only" if ev else "native: no SEC filing found"] += 1
        out[sid] = timeline(ev)
    for sid, ciks in links.items():
        ev = [r for c in ciks for r in by_cik.get(int(c), ())]
        out[sid] = timeline(ev)
        source["repaired"] += 1
    return out, dict(source)


def timeline(ev):
    tl = []
    for r in sorted(ev, key=lambda r: (r["filed"], r["accn"])):
        eff = (date.fromisoformat(r["filed"]) + timedelta(days=1)).isoformat()
        if not tl or tl[-1][1] != r["sic"]:
            tl.append([eff, r["sic"], r["cik"]])
    return tl


if __name__ == "__main__":
    corr = json.loads((OUT / "corrections.json").read_text())
    tl, src = build({sid: [x["cik"] for x in v] for sid, v in corr.items()})
    print(src, sum(1 for v in tl.values() if v))
