"""LH-CP3 EDGAR header sample manifest (owner D244; protocol 7). Deterministic, pre-registered strata over the
population of non-XBRL original filings whose labels are still unknown after Part A and which belong to label-unknown
C1- / C2-complete Stage C P2 histories of 2013-2014 stock-months. Uses the FROZEN rules (R* outcome per accession)
and is committed (SHA-256 recorded) before any EDGAR request. No network access here.

    PYTHONPATH=src python research/longhorizon/cp3/LH_CP3_manifest.py
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import lh_cp3_data as DATA
from LH_CP3_validation import month_end_near

HERE = Path(__file__).parent
SAFE, V3, R = DATA.SAFE, DATA.V3, DATA.R
OUT = HERE / "LH_CP3_manifest.json"
FREEZE = HERE / "LH_CP3_rules_freeze.json"
CAP = 2
QUOTAS = [("base", 60), ("single_source", 10), ("conflict_or_none", 10), ("w5253", 10), ("transition_registrant", 10),
          ("entrant", 10), ("leaver", 10)]


def ygroup(filed_day):
    y = V3.dd(filed_day).year
    return "<=2009" if y <= 2009 else ("2010" if y == 2010 else ">=2011")


def main():
    fr = json.loads(FREEZE.read_text())
    if hashlib.sha256((HERE / "lh_cp3_rules.py").read_bytes()).hexdigest() != fr["lh_cp3_rules_sha256"]:
        raise SystemExit("STOP: rules not frozen")
    from qr_data_v21 import load_table
    t = load_table()
    client = SAFE.client()
    xb_by_cik = DATA.load_index()
    p2 = DATA.load_cache("p2.pkl")
    recs, chains = p2["recs"], p2["chains"]
    use = defaultdict(list)                        # chain key -> recs (2013-2014, C1 or C2 complete)
    for rec in recs:
        if rec["year"] in (2013, 2014) and (rec["ok1"] or rec["ok2"]) and chains[rec["key"]]["lstatus_v"] == "unknown":
            use[rec["key"]].append(rec)
    regs, pop = {}, {}
    for key, rs in sorted(use.items(), key=lambda kv: (int(kv[0][0]), kv[0][1])):
        cik, c13 = key
        reg = regs.get(cik) or DATA.Reg(cik, client, xb_by_cik, t["f"][cik])
        regs[cik] = reg
        Dmin = min(r["D"] for r in rs)
        rec_out = reg.reconstruct(list(c13), Dmin)
        for k, p in enumerate(c13):
            if chains[key]["labels_v"][k] is not None:
                continue
            r = reg.sub_row(p)
            if r is None or r[4] != 0 or r[1] not in ("10-Q", "10-K", "10-K405") or V3.dd(r[2]).isoformat() > SAFE.CUT:
                continue
            if r[2] > Dmin - 1:
                continue
            a = r[3]
            e = pop.setdefault(a, dict(accession=a, cik=cik, form=r[1], filed=str(V3.dd(r[2])), period=str(V3.dd(p)), report_date=str(V3.dd(r[0])),
                                       tier=rec_out[k][1], seq=rec_out[k][2], cmp=rec_out[k][3],
                                       w5253=any(not month_end_near(q) for q in reg.orig),
                                       transition_registrant=bool(reg.trans), entrant=False, leaver=False))
            e["entrant"] |= any(x["entrant"] for x in rs)
            e["leaver"] |= any(x["leaver"] for x in rs)
    order = sorted(pop, key=lambda a: hashlib.sha256(f"LH-CP3-sample|{a}".encode()).hexdigest())
    chosen, per_reg, strata_n = [], Counter(), {}

    def take(pred, n, label):
        got = 0
        for a in order:
            if got >= n:
                break
            e = pop[a]
            if a in {c["accession"] for c in chosen} or per_reg[e["cik"]] >= CAP or not pred(e):
                continue
            chosen.append(dict(e, stratum=label))
            per_reg[e["cik"]] += 1
            got += 1
        strata_n[label] = dict(quota=n, drawn=got, eligible=sum(1 for a in order if pred(pop[a])))

    for form in ("10-K", "10-Q"):
        for yg in ("<=2009", "2010", ">=2011"):
            take(lambda e, f=form, y=yg: e["tier"] == "L2" and (e["form"] in ("10-K", "10-K405")) == (f == "10-K")
                 and ygroup(V3.dn(e["filed"])) == y, 10, f"base:{form}:{yg}")
    take(lambda e: e["tier"] == "L3", 10, "single_source")
    take(lambda e: e["tier"] in ("conflict", "none"), 10, "conflict_or_none")
    take(lambda e: e["w5253"], 10, "w5253")
    take(lambda e: e["transition_registrant"], 10, "transition_registrant")
    take(lambda e: e["entrant"], 10, "entrant")
    take(lambda e: e["leaver"], 10, "leaver")
    pop_summary = dict(accessions=len(pop), registrants=len({e["cik"] for e in pop.values()}),
                       tiers=dict(Counter(e["tier"] for e in pop.values())),
                       forms=dict(Counter(e["form"] for e in pop.values())),
                       filed_year_groups=dict(Counter(ygroup(V3.dn(e["filed"])) for e in pop.values())))
    out = dict(kind="LH-CP3 pre-registered EDGAR header sample manifest (metadata only)", decision="D244",
               cut_off=SAFE.CUT, rules_sha256=fr["lh_cp3_rules_sha256"],
               protocol_sha256=hashlib.sha256((HERE / "LH_CP3_protocol.md").read_bytes()).hexdigest(),
               seed_rule="sha256('LH-CP3-sample|' + accession)", registrant_cap=CAP, population=pop_summary,
               strata=strata_n, n=len(chosen), accessions=chosen, network_requests=client.fetched)
    SAFE.assert_no_post_cutoff(out)
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps(dict(population=pop_summary, strata=strata_n, n=len(chosen)), indent=1))


if __name__ == "__main__":
    main()
