"""P7-CP5e (D188) question B: dated SEC identity before each security's first identity-v2 row, from PUBLIC EDGAR
submissions only (rule pre-registered in P7_CP5e_preregistration.md; no vendor data).

For every security eligible at any review under E993-02 or E993-03 that has identity-v2 rows:
  D0 = first row's effective date, X = its CIK. Walk back through X's ORIGINAL periodic filings (10-K, 10-Q, 10-KT)
  filed before D0 while consecutive filings are <= 200 days apart; the proposed start is the earliest filing date of
  that unbroken chain, floored at 2008-07-01. Bounds (start moves later): a material former-name change of X
  (normalised name differs) inside the interval; a deregistration form (15-12B/15-12G/15-15D) of X inside the interval;
  another security whose identity-v2 link to X ends before D0 (a predecessor security).
  SAFE = chain reaches the floor and no bound; BOUNDED = start later than the floor but before D0; REJECT = a bound
  within 120 days before D0, the last periodic filing before D0 more than 200 days earlier, or no periodic filing
  before D0; AMBIGUOUS = no submissions file. Rows with D0 <= floor need no extension (NOT_NEEDED).
Output: research/phase7/cp5e/identity_extension.json (one evidence record per security + summary)."""
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(Path(__file__).parent)]
import qr_sec_data as D  # noqa: E402
from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402
import target_population as T  # noqa: E402

FLOOR = date(2008, 7, 1)
GAP = 200
NEAR = 120
ORIG = ("10-K", "10-Q", "10-KT", "10-K405")
DEREG = ("15-12B", "15-12G", "15-15D")
SUFFIX = re.compile(r"\b(INC|INCORPORATED|CORP|CORPORATION|CO|COMPANY|LTD|LIMITED|PLC|HOLDINGS?|GROUP|THE|NEW|DE|"
                    r"/[A-Z]{2}/?)\b")


def norm(n):
    s = re.sub(r"[^A-Z0-9 ]", " ", (n or "").upper().replace("/DE/", " ").replace("/NEW/", " "))
    s = SUFFIX.sub(" ", s)
    return " ".join(s.split())


def dd(s):
    return date.fromisoformat(s[:10])


def universe_sids():
    old, new = T.load()
    return sorted(set().union(*old.values()) | set().union(*new.values()))


def links_by_cik(sh):
    """CIK -> [(sid, span start, span end)] from the identity-v2 dated rows (end = next row with another CIK)."""
    out = defaultdict(list)
    for sid, rows in sh.items():
        for i, (eff, _sic, cik) in enumerate(rows):
            if cik in (None, ""):
                continue
            j = i + 1
            while j < len(rows) and rows[j][2] == cik:
                j += 1
            if i > 0 and rows[i - 1][2] == cik:
                continue
            end = dd(rows[j][0]) if j < len(rows) else date.max
            out[int(cik)].append((sid, dd(eff), end))
    return out


def evidence(sid, rows, sub, links):
    d0, x = dd(rows[0][0]), int(rows[0][2]) if rows[0][2] not in (None, "") else None
    rec = dict(sid=sid, cik=x, d0=str(d0))
    if x is None:
        return dict(rec, category="AMBIGUOUS", why="first row without CIK")
    if d0 <= FLOOR:
        return dict(rec, category="NOT_NEEDED", start=str(d0))
    if sub is None:
        return dict(rec, category="AMBIGUOUS", why="no submissions file")
    fl = filings_table(sub)
    per = sorted(dd(r["filingDate"]) for r in fl if r["form"] in ORIG and dd(r["filingDate"]) < d0)
    if not per:
        return dict(rec, category="REJECT", why="no periodic filing before D0 (new registrant)")
    if (d0 - per[-1]).days > GAP:
        return dict(rec, category="REJECT", why=f"last periodic filing {per[-1]} > {GAP} days before D0")
    j = len(per) - 1
    while j > 0 and (per[j] - per[j - 1]).days <= GAP and per[j - 1] >= FLOOR - timedelta(days=GAP):
        j -= 1
    chain_first = per[j]
    start = max(FLOOR, chain_first) if not (chain_first <= FLOOR) else FLOOR
    bounds = []
    # a change = a former name whose SUCCESSOR (the next name in time, or the current name) differs materially
    fns = sorted((fn for fn in sub.get("formerNames") or [] if fn.get("to")), key=lambda fn: fn["to"])
    for i, fn in enumerate(fns):
        to = dd(fn["to"])
        succ = fns[i + 1]["name"] if i + 1 < len(fns) else sub.get("name")
        if FLOOR <= to < d0 and norm(fn["name"]) != norm(succ):
            bounds.append(("name_change", to + timedelta(days=1), fn["name"]))
    for r in fl:
        if r["form"] in DEREG and start <= dd(r["filingDate"]) < d0:
            bounds.append(("deregistration", dd(r["filingDate"]) + timedelta(days=1), r["form"]))
    for s2, a, b in links.get(x, ()):
        if s2 != sid and a < d0 and b <= d0 and b > start:
            bounds.append(("predecessor_security", b, s2))
    nb = max([b[1] for b in bounds], default=start)
    start2 = max(start, nb)
    rec.update(chain_first=str(chain_first), chain_filings=len(per) - j, bounds=[[k, str(v), w] for k, v, w in bounds])
    if (d0 - start2).days <= NEAR and bounds:
        return dict(rec, category="REJECT", why="identity bound within 120 days before D0", start=str(start2))
    if start2 >= d0:
        return dict(rec, category="REJECT", why="no extension interval", start=str(start2))
    cat = "SAFE" if start2 == FLOOR and not bounds else "BOUNDED"
    return dict(rec, category=cat, start=str(start2))


def main():
    sec = D.load_table()
    sh = sec["sic_history"]
    links = links_by_cik(sh)
    client = SECClient()
    out, cnt = [], Counter()
    for sid in universe_sids():
        rows = sh.get(sid)
        if not rows:
            out.append(dict(sid=sid, category="NO_IDENTITY_ROW"))
            cnt["NO_IDENTITY_ROW"] += 1
            continue
        x = rows[0][2]
        sub = client.submissions(int(x)) if x not in (None, "") and dd(rows[0][0]) > FLOOR else None
        r = evidence(sid, rows, sub, links)
        out.append(r)
        cnt[r["category"]] += 1
    why = Counter(r.get("why") for r in out if r["category"] in ("REJECT", "AMBIGUOUS"))
    bnd = Counter(b[0] for r in out if r["category"] == "BOUNDED" for b in r.get("bounds", []))
    summ = dict(securities=len(out), categories=dict(cnt), reject_ambiguous_reasons={str(k): v for k, v in why.items()},
                bounded_by=dict(bnd), bounded_by_chain_start=sum(1 for r in out if r["category"] == "BOUNDED"
                                                                  and not r.get("bounds")),
                sec_requests=client.fetched)
    (Path(__file__).parent / "identity_extension.json").write_text(
        json.dumps(dict(summary=summ, rows=out), sort_keys=True, indent=0) + "\n")
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
