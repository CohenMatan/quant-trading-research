"""H017 event table (Event Data v1, frozen; owner approval 2026-10-03). Infrastructure only: SEC filing metadata and
LEAN session dates. NO prices, NO reactions, NO returns are read or computed here.

Rules (P2-CP12 §19 "event data v1", unchanged):
  * events = original 8-K filings with Item 2.02 (or its predecessor 12), first SEC acceptance, 30-day de-duplication
    per registrant, amendments (8-K/A) ignored, no inferred dates (qresearch.sec_events.build_events);
  * acceptance times converted with the MEASURED per-registrant convention (research/phase2/earnings_audit/
    tz_conventions.json); a registrant whose convention is unresolved or was never measured gets UNKNOWN time
    (handled as after the close of the filing date: conservative, never earlier);
  * timing classes / event session E (sec_events.classify) on the LEAN session calendar;
  * securities: the E981-01 export of the frozen data-v1 universe; only identities VERIFIED by dated ticker evidence or
    identity v2 (SEC-corrected securities); weak / unverified / contradicted / no-CIK securities are excluded;
  * predecessor linking: the frozen dated-ticker rule (predecessor_recovery.py): another registrant with >= 2 XBRL
    instance prefixes equal to a ticker the security carried (+-3 months), filed within the security's span and outside
    the mapped registrant's own XBRL filing span (time-disjoint); used only if exactly ONE such registrant exists
    (ambiguous cases excluded). Time-disjoint succession is also enforced per event: a linked registrant's event is
    used only if its filing date lies OUTSIDE the mapped registrant's own SEC filing span (first..last filing date of
    any form), i.e. before the mapped registrant existed or after it stopped filing. This drops co-registrants that
    file the same combined 8-K at the same time (e.g. a utility holding company and its operating subsidiary);
  * foreign private issuers file no 8-K: they have no events (excluded by construction);
  * a security's events from several linked registrants are merged; an event within 30 days of the security's
    previous kept event (same first-acceptance rule) is a cross-registrant duplicate and is dropped (counted);
  * window: decision session E+1 in [2009-07-01, 2021-12-31] (history-only warm-up from 2009-07-01; nothing after
    2021-12-31: Holdout lock).

H017-specific timing (research/phase2/H017_spec.md): decision at the close of E+1, entry at the open of E+2.

Calendar: LEAN trading sessions (E976-04 equity dates 2008-07-01 .. 2021-12-31; identical to E981-01 from 2010) plus
2022-01-03. Early closes (13:00): sec_events.EARLY_CLOSE (2010-2021) plus the 2008-2009 NYSE early closes, needed only
for warm-up events (the same rule).

Outputs (all committed; the packed files are what QuantConnect loads):
  research/phase2/h017/event_table_v1.csv.gz    one row per event (sid, cik, accession, acceptance ET, class, E, E+1)
  research/phase2/h017/event_table_v1.json      manifest: rules, inputs (hashes), counts, payload SHA-256
  src/qresearch/lean/qr_h017_events.py + qr_h017_events_NN.py   packed payload (zlib + base64, < 64,000 chars/file)

    PYTHONPATH=src python research/phase2/h017/h017_event_table.py            build (refuses to change a frozen table)
    PYTHONPATH=src python research/phase2/h017/h017_event_table.py --verify   rebuild in memory and compare hashes
"""
from __future__ import annotations

import base64
import csv
import gzip
import hashlib
import io
import json
import sys
import zlib
from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research/phase2/earnings_audit"))
from qresearch import sec_events as S  # noqa: E402
from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402
import earnings_event_audit as A  # noqa: E402

HERE = Path(__file__).parent
CSV_OUT = HERE / "event_table_v1.csv.gz"
MANIFEST = HERE / "event_table_v1.json"
LEAN_DIR = ROOT / "src/qresearch/lean"
PACK_PREFIX = "qr_h017_events"
PART_CHARS = 60000
DECISION_FIRST, DECISION_LAST = date(2009, 7, 1), date(2021, 12, 31)
EPOCH = date(2008, 1, 1)                     # payload dates = days since EPOCH
OK_IDENTITY = ("verified (dated ticker evidence)", "verified (identity v2, SEC-corrected security)")
WARMUP_EARLY_CLOSE = {date(2008, 7, 3), date(2008, 11, 28), date(2008, 12, 24), date(2009, 11, 27),
                      date(2009, 12, 24)}
CLS_CODE = {"BMO": "B", "DURING": "D", "AMC": "A", "NONSESSION": "N", "UNKNOWN": "U"}
CALENDAR_SOURCE = "experiments/E976-04/equity.csv.gz"
INPUTS = ("experiments/E981-01/messages.txt", CALENDAR_SOURCE, "research/phase2/earnings_audit/tz_conventions.json",
          "data/sec_derived/xbrl_filings.json.gz")


class Calendar(S.Calendar):
    def close_time(self, d):
        return S.EARLY_CLOSE_TIME if d in S.EARLY_CLOSE or d in WARMUP_EARLY_CLOSE else S.CLOSE


def calendar():
    rows = gzip.open(ROOT / CALENDAR_SOURCE).read().decode().splitlines()[1:]
    return Calendar([date.fromisoformat(r.split(",")[0]) for r in rows] + [date(2022, 1, 3)])


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def predecessor_links(U, xb):
    """sid -> (unique predecessor CIK or None, number of candidates) by the frozen dated-ticker rule."""
    by_prefix, span_of = defaultdict(list), defaultdict(list)
    for r in xb:
        if r.get("prefix") and r.get("filed"):
            ym = int(r["filed"][:4]) * 100 + int(r["filed"][5:7])
            by_prefix[r["prefix"].upper()].append((int(r["cik"]), ym))
            span_of[int(r["cik"])].append(ym)
    out = {}
    for sid, u in U.items():
        if not u["ciks"] or u["corrected"]:
            continue
        own = u["ciks"][0]
        own_span = (min(span_of[own]), max(span_of[own])) if span_of.get(own) else None
        cands = Counter()
        for t, a, b in u["tickers"]:
            for cik, ym in by_prefix.get(t, ()):
                if cik == own or not (A.ym_add(a, -3) <= ym <= A.ym_add(b, 3)):
                    continue
                if own_span and own_span[0] <= ym <= own_span[1]:
                    continue
                cands[cik] += 1
        c = sorted(k for k, n in cands.items() if n >= 2)
        if c:
            out[sid] = (c[0] if len(c) == 1 else None, len(c))
    return out


def registrant_events(cik, conv, sec, cal, cache):
    if cik in cache:
        return cache[cik]
    sub = sec.submissions(cik)
    if sub is None:
        cache[cik] = None
        return None
    rows = filings_table(sub)
    c = conv.get(cik, "UNMEASURED")
    if c in ("UTC", "ET"):
        r = S.build_events(cik, rows, cal, tz=c)
    else:                                   # unresolved / never measured: never guess a time of day
        r = S.build_events(cik, [dict(f, acceptanceDateTime="") for f in rows], cal, tz="UTC")
    r["convention"] = c if c in ("UTC", "ET") else ("UNRESOLVED" if c == "UNRESOLVED" else "UNMEASURED")
    cache[cik] = r
    return r


def filing_span(cik, sec):
    """(first, last) filing date of any form of a registrant, or None."""
    sub = sec.submissions(cik)
    if sub is None:
        return None
    ds = sorted(d for d in (S._d(f.get("filingDate")) for f in filings_table(sub)) if d is not None)
    return (ds[0], ds[-1]) if ds else None


def first_time(e):
    return e.acceptance or datetime.combine(e.filing_date, time(23, 59, 59))


def build():
    U = A.load_universe()
    cal = calendar()
    sess = cal.sessions
    pos = {d: i for i, d in enumerate(sess)}
    sec = SECClient()
    xb = json.load(gzip.open(ROOT / "data/sec_derived/xbrl_filings.json.gz"))
    pbc = defaultdict(list)
    for r in xb:
        if r.get("prefix") and r.get("filed"):
            pbc[int(r["cik"])].append((int(r["filed"][:4]) * 100 + int(r["filed"][5:7]), r["prefix"].upper()))
    conv = {int(k): v["convention"] for k, v in
            json.loads((ROOT / "research/phase2/earnings_audit/tz_conventions.json").read_text())["ciks"].items()}
    links = predecessor_links(U, xb)
    cache = {}
    rows, cnt = [], Counter()
    identity = Counter()
    conv_used = Counter()
    for sid in sorted(U):
        u = U[sid]
        idc = A.identity_check(u, pbc)
        identity[idc] += 1
        if idc not in OK_IDENTITY:
            continue
        ciks = list(u["ciks"])
        link = links.get(sid)
        if link is not None:
            if link[0] is None:
                cnt["securities_ambiguous_predecessor_excluded"] += 1
            else:
                ciks.append(link[0])
                cnt["securities_with_predecessor_link"] += 1
        evs = []
        own_span = filing_span(u["ciks"][0], sec) if link is not None and link[0] is not None else None
        for k, cik in enumerate(ciks):
            r = registrant_events(cik, conv, sec, cal, cache)
            if r is None:
                cnt["registrants_without_submissions"] += 1
                continue
            role = "predecessor" if (link is not None and link[0] == cik and k == len(ciks) - 1) else "mapped"
            for e in r["events"]:
                if role == "predecessor" and own_span is not None and own_span[0] <= e.filing_date <= own_span[1]:
                    cnt["linked_events_inside_mapped_span_not_used"] += 1
                    continue
                evs.append((first_time(e), e.accession, cik, role, r["convention"], e))
        evs.sort(key=lambda x: (x[0], x[1]))
        kept_t = None
        n_sec = 0
        for t, acc, cik, role, cv, e in evs:
            if kept_t is not None and (t - kept_t) < timedelta(days=S.DEDUP_DAYS):
                cnt["cross_registrant_duplicates_dropped"] += 1
                continue
            kept_t = t
            E = e.event_session
            if E is None or E not in pos or pos[E] + 1 >= len(sess):
                cnt["events_outside_calendar"] += 1
                continue
            D1 = sess[pos[E] + 1]
            if not (DECISION_FIRST <= D1 <= DECISION_LAST):
                cnt["events_outside_window"] += 1
                continue
            rows.append(dict(sid=sid, cik=cik, role=role, accession=acc,
                             acceptance_et=e.acceptance.strftime("%Y-%m-%dT%H:%M:%S") if e.acceptance else "",
                             filing_date=str(e.filing_date), tz=cv, cls=e.cls, event_session=str(E),
                             decision_session=str(D1), duplicates=len(e.duplicates)))
            conv_used[cv] += 1
            n_sec += 1
        cnt["securities_with_events" if n_sec else "verified_securities_without_events"] += 1
    rows.sort(key=lambda r: (r["event_session"], r["sid"]))
    return dict(rows=rows, counts=dict(cnt), identity=dict(identity), conventions=dict(conv_used),
                universe_securities=len(U), sec=dict(fetched=sec.fetched, cache_hits=sec.cache_hits))


def payload(rows):
    """Canonical LEAN payload: {"sids": [...], "events": [[sid index, E (days since EPOCH), class code], ...]}."""
    sids = sorted({r["sid"] for r in rows})
    ix = {s: i for i, s in enumerate(sids)}
    ev = [[ix[r["sid"]], (date.fromisoformat(r["event_session"]) - EPOCH).days, CLS_CODE[r["cls"]]] for r in rows]
    return json.dumps(dict(epoch=str(EPOCH), sids=sids, events=ev), separators=(",", ":"), sort_keys=True).encode()


def csv_bytes(rows):
    buf = io.StringIO()
    cols = ["sid", "cik", "role", "accession", "acceptance_et", "filing_date", "tz", "cls", "event_session",
            "decision_session", "duplicates"]
    w = csv.DictWriter(buf, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return buf.getvalue().encode()


def pack(raw):
    s = base64.b64encode(zlib.compress(raw, 9)).decode()
    return [s[i:i + PART_CHARS] for i in range(0, len(s), PART_CHARS)]


def write_pack(parts, digest):
    for p in LEAN_DIR.glob(f"{PACK_PREFIX}_*.py"):
        p.unlink()
    for i, part in enumerate(parts):
        (LEAN_DIR / f"{PACK_PREFIX}_{i:02d}.py").write_text(f'# generated (H017 event table v1) — do not edit\nDATA = "{part}"\n')
    (LEAN_DIR / f"{PACK_PREFIX}.py").write_text(
        "# generated (H017 event table v1, research/phase2/h017/h017_event_table.py) — do not edit.\n"
        "# load() reassembles the packed table and checks its SHA-256.\n"
        "import base64, hashlib, importlib, json, zlib\n"
        f"N_PARTS = {len(parts)}\n"
        f'SHA256 = "{digest}"\n\n\n'
        "def load_events():\n"
        f'    s = "".join(importlib.import_module("{PACK_PREFIX}_%02d" % i).DATA for i in range(N_PARTS))\n'
        "    raw = zlib.decompress(base64.b64decode(s))\n"
        "    if hashlib.sha256(raw).hexdigest() != SHA256:\n"
        '        raise Exception("packed H017 event table corrupted (hash mismatch)")\n'
        "    return json.loads(raw)\n")


def manifest(res, raw, cb):
    rows = res["rows"]
    by_year = Counter(r["decision_session"][:4] for r in rows)
    cls = Counter(r["cls"] for r in rows)
    return dict(
        name="H017 event table v1 (Event Data v1)", built_utc_date=str(date.today()),
        builder="research/phase2/h017/h017_event_table.py",
        payload_sha256=hashlib.sha256(raw).hexdigest(), csv_sha256=hashlib.sha256(cb).hexdigest(),
        packed_files=f"src/qresearch/lean/{PACK_PREFIX}.py + {PACK_PREFIX}_NN.py",
        inputs={p: sha(p) for p in INPUTS}, sec_events_sha256=sha("src/qresearch/sec_events.py"),
        window=dict(decision_first=str(DECISION_FIRST), decision_last=str(DECISION_LAST)),
        rules=dict(dedup_days=S.DEDUP_DAYS, earnings_items=list(S.EARNINGS_ITEMS), amendments="ignored",
                   identity=list(OK_IDENTITY), predecessor="unique, time-disjoint dated-ticker link only",
                   unknown_time="UNRESOLVED or unmeasured registrant conventions -> UNKNOWN (after the close of the "
                                "filing date)", warmup_early_closes=sorted(str(d) for d in WARMUP_EARLY_CLOSE)),
        counts=dict(events=len(rows), securities=len({r["sid"] for r in rows}),
                    registrants=len({r["cik"] for r in rows}), events_by_decision_year=dict(sorted(by_year.items())),
                    events_by_class=dict(cls), events_by_convention=res["conventions"],
                    events_by_role=dict(Counter(r["role"] for r in rows)),
                    first_decision=rows[0]["decision_session"] if rows else None,
                    last_decision=max(r["decision_session"] for r in rows) if rows else None,
                    **res["counts"]),
        universe=dict(securities=res["universe_securities"], identity=res["identity"]))


def main(argv):
    res = build()
    raw = payload(res["rows"])
    cb = csv_bytes(res["rows"])
    m = manifest(res, raw, cb)
    if "--verify" in argv:
        old = json.loads(MANIFEST.read_text())
        ok = old["payload_sha256"] == m["payload_sha256"] and old["csv_sha256"] == m["csv_sha256"]
        print(json.dumps(dict(reproduced=ok, payload=m["payload_sha256"], frozen=old["payload_sha256"],
                              csv=m["csv_sha256"], frozen_csv=old["csv_sha256"]), indent=1))
        raise SystemExit(0 if ok else 1)
    if MANIFEST.exists() and json.loads(MANIFEST.read_text())["payload_sha256"] != m["payload_sha256"] \
            and "--force" not in argv:
        raise SystemExit("event table v1 is frozen and the rebuild differs; refusing to overwrite (use --verify)")
    CSV_OUT.write_bytes(gzip.compress(cb, mtime=0))
    write_pack(pack(raw), m["payload_sha256"])
    MANIFEST.write_text(json.dumps(m, indent=1) + "\n")
    print(json.dumps({k: m[k] for k in ("payload_sha256", "counts", "universe")}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
