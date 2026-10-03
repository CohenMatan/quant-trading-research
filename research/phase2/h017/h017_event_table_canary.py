"""H017 event-table integrity canary (P2-CP13 §27.1; owner 2026-10-03 "event integrity" checks). Metadata only: NO
prices, NO reactions, NO returns.

Checks on the frozen table (research/phase2/h017/event_table_v1.*):
  1. hashes: CSV and payload match the manifest; the packed LEAN files reassemble to the payload; the frozen pin in
     qresearch.p2h017 equals the manifest;
  2. time-zone rules: every acceptance time re-derived from the raw SEC string with the registrant's measured
     convention (UNMEASURED/UNRESOLVED -> no time); timing class and event session re-derived;
  3. a stratified random sample of 50 events (seeded) re-checked against the EDGAR filing index pages ("Accepted",
     US Eastern);
  4. de-duplication: no two events of a security within 30 days (first acceptance);
  5. amendments excluded: every accession is an ORIGINAL 8-K with Item 2.02/12 in the registrant's submissions;
  6. foreign private issuers excluded: every event is an original 8-K (check 5); foreign private issuers are exempt
     from Form 8-K and report on 6-K / 20-F / 40-F, so an 8-K Item 2.02 filing is itself evidence of domestic filing at
     that time, and no event comes from a 6-K / 20-F / 40-F. For information, events of registrants that filed a
     20-F / 40-F annual report within a year of the event (filer-status transitions, e.g. NXP and Signet moving to
     domestic filing; Venator and PartnerRe becoming foreign filers later) are listed by name;
  7. identities: every security is verified (dated ticker evidence or identity v2);
  8. predecessor links: unique (one linked registrant per security) and time-disjoint (event filed outside the mapped
     registrant's filing span);
  9. window: no decision session after 2021-12-31 or before 2009-07-01; every event session is a LEAN session;
 10. reproducibility: an in-memory rebuild from the cached SEC data gives the identical payload.

    PYTHONPATH=src python research/phase2/h017/h017_event_table_canary.py -> h017_event_table_canary.json
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import importlib
import io
import json
import random
import re
import sys
import zlib
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
sys.path.insert(0, str(Path(__file__).parent))
from qresearch import p2h017, sec_events as S  # noqa: E402
from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402
import h017_event_table as T  # noqa: E402

OUT = Path(__file__).with_name("h017_event_table_canary.json")
SAMPLE, SEED = 50, 20261003


def main():
    man = json.loads(T.MANIFEST.read_text())
    cb = gzip.decompress(T.CSV_OUT.read_bytes())
    df = pd.read_csv(io.BytesIO(cb), dtype=str, keep_default_na=False)
    raw = T.payload(df.to_dict("records"))
    mod = importlib.import_module(T.PACK_PREFIX)
    packed = mod.load_events()
    chk = {}
    chk["1_hashes"] = dict(csv=hashlib.sha256(cb).hexdigest() == man["csv_sha256"],
                           payload=hashlib.sha256(raw).hexdigest() == man["payload_sha256"],
                           packed=json.dumps(packed, separators=(",", ":"), sort_keys=True).encode() == raw,
                           packed_pin=mod.SHA256 == man["payload_sha256"],
                           frozen_pin=p2h017.EVENT_TABLE_SHA256 == man["payload_sha256"],
                           max_part_chars=max(len(importlib.import_module(f"{T.PACK_PREFIX}_{i:02d}").DATA)
                                              for i in range(mod.N_PARTS)))
    chk["1_hashes"]["ok"] = all(v for k, v in chk["1_hashes"].items() if k != "max_part_chars") and \
        chk["1_hashes"]["max_part_chars"] < 64000
    sec = SECClient()
    cal = T.calendar()
    conv = {int(k): v["convention"] for k, v in
            json.loads((ROOT / "research/phase2/earnings_audit/tz_conventions.json").read_text())["ciks"].items()}
    subs = {}

    def rows_of(cik):
        if cik not in subs:
            subs[cik] = {f["accessionNumber"]: f for f in filings_table(sec.submissions(cik))}
        return subs[cik]
    tz_bad, cls_bad, amend_bad, foreign_bad = [], [], [], []
    for r in df.itertuples():
        cik = int(r.cik)
        f = rows_of(cik).get(r.accession)
        if f is None or str(f.get("form")) != "8-K" or not S.is_earnings_filing(f):
            amend_bad.append(r.accession)
            continue
        c = conv.get(cik)
        acc = S.acceptance_et(f.get("acceptanceDateTime"), c) if c in ("UTC", "ET") else None
        exp = acc.strftime("%Y-%m-%dT%H:%M:%S") if acc else ""
        if exp != r.acceptance_et or (r.tz != (c if c in ("UTC", "ET") else r.tz)):
            tz_bad.append(r.accession)
        k = S.classify(acc, date.fromisoformat(r.filing_date), cal)
        if k["cls"] != r.cls or str(k["event_session"]) != r.event_session:
            cls_bad.append(r.accession)
    annual = defaultdict(list)
    for cik in {int(x) for x in df["cik"]}:
        for f in rows_of(cik).values():
            if str(f.get("form")) in ("20-F", "40-F", "20-F/A", "40-F/A"):
                annual[cik].append(S._d(f.get("filingDate")))
    transition = defaultdict(list)
    for r in df.itertuples():
        fd = date.fromisoformat(r.filing_date)
        if any(d is not None and abs((d - fd).days) <= 365 for d in annual.get(int(r.cik), ())):
            transition[int(r.cik)].append(r.filing_date)
    foreign_bad = [r.accession for r in df.itertuples() if str(rows_of(int(r.cik)).get(r.accession, {}).get("form"))
                   in ("6-K", "20-F", "40-F")]
    chk["2_timezone_rules"] = dict(rederived=len(df), acceptance_mismatches=len(tz_bad), class_mismatches=len(cls_bad),
                                   conventions=dict(Counter(df["tz"])), ok=not tz_bad and not cls_bad,
                                   examples=tz_bad[:5] + cls_bad[:5])
    # ---- 3. EDGAR index-page sample
    rnd = random.Random(SEED)
    pool = df[df["acceptance_et"] != ""]
    by_y = defaultdict(list)
    for r in pool.itertuples():
        by_y[r.decision_session[:4]].append(r)
    ys = sorted(by_y)
    sample = []
    while len(sample) < SAMPLE:
        for y in ys:
            if len(sample) < SAMPLE:
                sample.append(rnd.choice(by_y[y]))
    rows = []
    for r in sample:
        a = r.accession
        b = sec.get_bytes(f"https://www.sec.gov/Archives/edgar/data/{int(r.cik)}/{a.replace('-', '')}/{a}-index.htm") or b""
        m = re.search(rb'Accepted</div>\s*<div class="info">([^<]+)<', b)
        page = m.group(1).decode().strip() if m else None
        rows.append(dict(sid=r.sid, cik=int(r.cik), accession=a, tz=r.tz, table=r.acceptance_et.replace("T", " "),
                         index_page=page, match=page == r.acceptance_et.replace("T", " ")))
    chk["3_edgar_sample"] = dict(sample=len(rows), with_page=sum(x["index_page"] is not None for x in rows),
                                 matches=sum(x["match"] for x in rows), ok=all(x["match"] for x in rows), rows=rows)
    # ---- 4. de-duplication at security level
    viol = 0
    for sid, g in df.groupby("sid"):
        t = sorted(datetime.fromisoformat(x) if x else datetime.combine(date.fromisoformat(fd), datetime.max.time())
                   for x, fd in zip(g["acceptance_et"], g["filing_date"]))
        viol += sum(1 for a, b in zip(t, t[1:]) if (b - a) < timedelta(days=S.DEDUP_DAYS))
    chk["4_dedup"] = dict(violations=viol, ok=viol == 0)
    chk["5_amendments_excluded"] = dict(non_original_or_non_earnings=len(amend_bad), ok=not amend_bad)
    chk["6_foreign_excluded"] = dict(events_from_foreign_forms=len(foreign_bad), non_8k_events=len(amend_bad),
                                     ok=not foreign_bad and not amend_bad,
                                     info_transition_registrants={str(sec.submissions(c).get("name")): v
                                                                  for c, v in sorted(transition.items())},
                                     info_transition_events=sum(len(v) for v in transition.values()))
    # ---- 7/8. identities and predecessor links
    U = T.A.load_universe()
    xb = json.load(gzip.open(ROOT / "data/sec_derived/xbrl_filings.json.gz"))
    pbc = defaultdict(list)
    for r in xb:
        if r.get("prefix") and r.get("filed"):
            pbc[int(r["cik"])].append((int(r["filed"][:4]) * 100 + int(r["filed"][5:7]), r["prefix"].upper()))
    ids = Counter(T.A.identity_check(U[s], pbc) for s in df["sid"].unique())
    chk["7_identities"] = dict(by_status=dict(ids), ok=set(ids) <= set(T.OK_IDENTITY))
    links = T.predecessor_links(U, xb)
    pred = df[df["role"] == "predecessor"]
    nonunique = disjoint_bad = 0
    for sid, g in pred.groupby("sid"):
        if g["cik"].nunique() != 1 or links.get(sid, (None,))[0] != int(g["cik"].iloc[0]):
            nonunique += 1
        span = T.filing_span(U[sid]["ciks"][0], sec)
        if span is not None:
            disjoint_bad += int(((g["filing_date"] >= str(span[0])) & (g["filing_date"] <= str(span[1]))).sum())
    mapped_bad = int(sum(int(c) not in U[s]["ciks"] for s, c in zip(df.loc[df["role"] == "mapped", "sid"],
                                                                         df.loc[df["role"] == "mapped", "cik"])))
    chk["8_predecessor_links"] = dict(securities_linked=int(pred["sid"].nunique()), events=len(pred),
                                      non_unique=nonunique, inside_mapped_span=disjoint_bad,
                                      mapped_rows_with_foreign_cik=mapped_bad,
                                      ok=nonunique == 0 and disjoint_bad == 0 and mapped_bad == 0)
    sess = set(cal.sessions)
    chk["9_window"] = dict(first_decision=df["decision_session"].min(), last_decision=df["decision_session"].max(),
                           after_2021=int((df["decision_session"] > "2021-12-31").sum()),
                           before_warmup=int((df["decision_session"] < "2009-07-01").sum()),
                           event_session_not_lean_session=int(sum(date.fromisoformat(x) not in sess
                                                                  for x in df["event_session"])),
                           ok=bool(df["decision_session"].max() <= "2021-12-31" and
                                   df["decision_session"].min() >= "2009-07-01"))
    res = T.build()
    chk["10_reproducible"] = dict(rebuild_payload=hashlib.sha256(T.payload(res["rows"])).hexdigest(),
                                  ok=hashlib.sha256(T.payload(res["rows"])).hexdigest() == man["payload_sha256"])
    out = dict(table=man["payload_sha256"], events=len(df), securities=int(df["sid"].nunique()),
               all_ok=all(v["ok"] for v in chk.values()), checks=chk)
    OUT.write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps({k: v["ok"] for k, v in chk.items()}, indent=1), "\nall_ok", out["all_ok"])
    print("edgar", chk["3_edgar_sample"]["matches"], "/", chk["3_edgar_sample"]["sample"])


if __name__ == "__main__":
    main()
