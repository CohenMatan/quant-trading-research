"""H025 SEC event ledger builder (owner D204; frozen rules research/phase10/H025_spec.md; NO prices, NO returns).

Stages (each deterministic; inputs cached under data/sec_cache, outside Git, re-acquirable by re-running):
    PYTHONPATH=src python research/phase10/h025_ledger.py --fetch      download data sets + EDGAR headers (SEC only)
    PYTHONPATH=src python research/phase10/h025_ledger.py              build the SEC ledger + feasibility counts
    PYTHONPATH=src python research/phase10/h025_ledger.py --verify     independent rebuild (brute force) + hash compare

Outputs (committed; they contain public SEC facts only):
    research/phase10/ledger/h025_sec_ledger.csv.gz     one row per triggered cluster / single-insider control event
    research/phase10/ledger/h025_sec_filings.csv.gz    every qualifying filing used (timing status, values)
    research/phase10/ledger/h025_sec_ledger.json       manifest: rules, input hashes, counts, SHA-256 of the payload
    src/qresearch/lean/qr_h025_events.py (+ _NN parts) packed payload QuantConnect loads (zlib + base64)
"""
from __future__ import annotations

import argparse
import base64
import csv
import gzip
import hashlib
import io
import json
import sys
import zlib
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

from qresearch import h025_form4 as F
from qresearch.sec_edgar import SECClient

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research" / "phase10" / "ledger"
LEAN = ROOT / "src" / "qresearch" / "lean"
DS_URL = "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/{y}q{q}_form345.zip"
QUARTERS = [(2010, 4)] + [(y, q) for y in range(2011, 2018) for q in range(1, 5)]
CALENDAR_SOURCE = "experiments/E976-04/equity.csv.gz"        # LEAN sessions (verified again in-host)
LAST_SESSION = date(2017, 12, 29)                            # nothing after 2017 (development period only)
WINDOW_FROM = date(2011, 2, 1)                               # first review 2011-01-31 must be strictly earlier
HOLD = 20
SPAN_DAYS = 17                                               # header prefilter: 10-day window + 7-day lag slack
MAX_LAG_DAYS = 7                                             # acceptance date >= filing date - 7 (verified)
CHUNK = 60000
FIELDS = ("event_id", "kind", "issuer_cik", "symbol_as_filed", "trigger_et", "trigger_date", "entry_session",
          "exit_session", "window_status", "n_insiders", "insider_ciks", "insider_names", "insider_roles",
          "insider_values", "cluster_value", "ceo_cfo", "director_only", "n_qualifying_filings", "n_purchase_lines",
          "accessions", "acceptance_et", "transaction_dates", "shares", "prices", "line_values", "median_delay_days",
          "later_accessions", "near_cluster")


def sessions():
    rows = gzip.open(ROOT / CALENDAR_SOURCE).read().decode().splitlines()[1:]
    return F.Sessions([d for d in (date.fromisoformat(r.split(",")[0]) for r in rows) if d <= LAST_SESSION])


def ds_paths(client):
    return [(y, q, DS_URL.format(y=y, q=q)) for y, q in QUARTERS]


def load(client):
    parts, hashes = [], {}
    for y, q, url in ds_paths(client):
        raw = client.get_bytes(url, allow_missing=False)
        hashes[f"{y}q{q}"] = hashlib.sha256(raw).hexdigest()
        parts.append(F.read_quarter(raw))
    return F.merge_quarters(parts), hashes


def headers(client, filings, keys, owners_of):
    """accession -> parsed header (issuer directory first, then the reporting owner's directory)."""
    out = {}
    for a in sorted(keys):
        f = filings[a]
        raw = client.get_bytes(F.header_url(f.issuer_cik, a))
        if raw is None:
            raw = client.get_bytes(F.header_url(f.owner_cik, a))
        out[a] = None if raw is None else F.parse_header(raw)
    return out


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def build(verify=False):
    client = SECClient()
    data, ds_hash = load(client)
    line_counts = Counter()
    filings = F.qualifying_filings(data, line_counts)
    cand = F.header_candidates(filings, SPAN_DAYS)
    hdr = headers(client, filings, cand, None)
    cal = sessions()
    timing = Counter()
    by_issuer = defaultdict(list)
    for a in sorted(cand):
        f = filings[a]
        st = F.timing_status(f, hdr[a], MAX_LAG_DAYS)
        timing[st] += 1
        if st == "ok":
            f.acceptance = hdr[a]["acceptance"]
            by_issuer[f.issuer_cik].append(f)
    lag = Counter((filings[a].filing_date - hdr[a]["acceptance"].date()).days for a in cand
                  if hdr[a] and hdr[a]["acceptance"] and hdr[a]["filing_date"] == filings[a].filing_date)
    events, mismatch = [], 0
    for cik in sorted(by_issuer):
        fs = by_issuer[cik]
        cl = F.build_events(fs, cal, WINDOW_FROM, LAST_SESSION, "cluster")
        sg = F.build_events(fs, cal, WINDOW_FROM, LAST_SESSION, "single")
        if verify:
            for kind, evs in (("cluster", cl), ("single", sg)):
                ref = F.brute_force_triggers(fs, cal, kind)
                got = [(e.trigger, e.entry, tuple(e.insiders)) for e in evs]
                mismatch += int(ref != got)
        ci = [cal.idx[e.entry] for e in cl]
        for e in sg:                         # single-insider control: no cluster entry within 19 sessions
            i = cal.idx[e.entry]
            e.near = any(abs(i - j) < HOLD for j in ci)
        for e in cl:
            e.near = False
        events += cl + sg
    rows = [row(e, filings, cal) for e in sorted(events, key=lambda e: (e.trigger, e.issuer_cik, e.kind))]
    filing_rows = [frow(filings[a], hdr[a], F.timing_status(filings[a], hdr[a], MAX_LAG_DAYS)) for a in sorted(cand)]
    return dict(rows=rows, filing_rows=filing_rows, line_counts=line_counts, timing=timing, lag=lag, ds_hash=ds_hash,
                data=data, filings=filings, cand=cand, mismatch=mismatch, client=client)


def row(e, filings, cal):
    fs = [filings[a] for a in e.qualifying_accessions]
    ei = cal.idx[e.entry]
    xi = ei + HOLD - 1
    exit_ = cal.s[xi] if xi < len(cal.s) else None
    if e.trigger.date() < WINDOW_FROM:
        ws = "before_window"
    elif exit_ is None or exit_ > LAST_SESSION:
        ws = "exit_after_2017"
    else:
        ws = "in_window"
    roles = []
    for o in e.insiders:
        g = next(f for f in fs if f.owner_cik == o)
        roles.append(("D" if g.director else "") + ("O" if g.officer else "") + ("T" if g.ten_pct else "") +
                     ("C" if any(h.ceo_cfo for h in fs if h.owner_cik == o) else ""))
    lines = [(f.accession, ln) for f in fs for ln in f.lines]
    delays = sorted((f.acceptance.date() - min(td for td, *_ in f.lines)).days for f in fs)
    med = delays[len(delays) // 2] if len(delays) % 2 else (delays[len(delays) // 2 - 1] + delays[len(delays) // 2]) / 2
    return dict(
        event_id=e.event_id, kind=e.kind, issuer_cik=e.issuer_cik, symbol_as_filed=e.symbol,
        trigger_et=e.trigger.isoformat(sep=" "), trigger_date=e.trigger.date().isoformat(),
        entry_session=e.entry.isoformat(), exit_session=exit_.isoformat() if exit_ else "", window_status=ws,
        n_insiders=len(e.insiders), insider_ciks=";".join(str(o) for o in e.insiders),
        insider_names=";".join(next(f.owner_name for f in fs if f.owner_cik == o) for o in e.insiders),
        insider_roles=";".join(roles), insider_values=";".join(f"{e.insider_values[o]:.2f}" for o in e.insiders),
        cluster_value=f"{e.cluster_value:.2f}", ceo_cfo=int(any(f.ceo_cfo for f in fs)),
        director_only=int(all(f.director and not f.officer for f in fs)),
        n_qualifying_filings=len(fs), n_purchase_lines=len(lines),
        accessions=";".join(f.accession for f in fs),
        acceptance_et=";".join(f.acceptance.isoformat(sep=" ") for f in fs),
        transaction_dates=";".join(f"{ln[0]}" for _, ln in lines), shares=";".join(f"{ln[1]:g}" for _, ln in lines),
        prices=";".join(f"{ln[2]:g}" for _, ln in lines), line_values=";".join(f"{ln[3]:.2f}" for _, ln in lines),
        median_delay_days=med, later_accessions=";".join(e.later), near_cluster=int(getattr(e, "near", False)))


def frow(f, h, st):
    return dict(accession=f.accession, issuer_cik=f.issuer_cik, owner_cik=f.owner_cik, filing_date=str(f.filing_date),
                acceptance_et=(h["acceptance"].isoformat(sep=" ") if h and h["acceptance"] else ""),
                timing_status=st, value=f"{f.value:.2f}", n_lines=len(f.lines),
                roles=("D" if f.director else "") + ("O" if f.officer else "") + ("T" if f.ten_pct else ""))


def csv_bytes(rows, fields):
    s = io.StringIO()
    w = csv.DictWriter(s, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return s.getvalue().encode()


LEAN_FIELDS = ("event_id", "kind", "issuer_cik", "symbol_as_filed", "trigger_et", "trigger_date", "entry_session",
               "exit_session", "window_status", "n_insiders", "cluster_value", "ceo_cfo", "director_only",
               "n_qualifying_filings", "median_delay_days", "near_cluster")


def lean_payload(rows):
    """Packed events QuantConnect loads (identity / eligibility are decided in-host from Data v2)."""
    return csv_bytes([{k: r[k] for k in LEAN_FIELDS} for r in rows], LEAN_FIELDS)


def pack(payload: bytes):
    b = base64.b64encode(zlib.compress(payload, 9)).decode()
    parts = [b[i:i + CHUNK] for i in range(0, len(b), CHUNK)]
    files = {}
    head = ["# H025 SEC event ledger (owner D204; research/phase10/h025_ledger.py). Public SEC Form 4 facts only.",
            "# Generated file: do not edit. PAYLOAD_SHA256 = SHA-256 of the decoded CSV payload.", "import base64",
            "import hashlib", "import zlib", f"PAYLOAD_SHA256 = '{_sha(payload)}'", f"N_PARTS = {len(parts)}", "",
            "", "def payload():", "    import importlib",
            "    b = ''.join(importlib.import_module('qr_h025_events_%02d' % i).DATA for i in range(N_PARTS))",
            "    raw = zlib.decompress(base64.b64decode(b))",
            "    if hashlib.sha256(raw).hexdigest() != PAYLOAD_SHA256:",
            "        raise Exception('H025 event ledger payload hash mismatch')", "    return raw.decode()", ""]
    files["qr_h025_events.py"] = "\n".join(head)
    for i, p in enumerate(parts):
        files[f"qr_h025_events_{i:02d}.py"] = f"DATA = '{p}'\n"
    return files


def feasibility(res):
    rows = res["rows"]
    cl = [r for r in rows if r["kind"] == "cluster"]
    inw = [r for r in cl if r["window_status"] == "in_window"]
    by_year = Counter(r["trigger_date"][:4] for r in inw)
    ins = Counter(min(int(r["n_insiders"]), 5) for r in inw)
    vals = sorted(float(r["cluster_value"]) for r in inw)

    def q(p):
        return round(vals[min(len(vals) - 1, int(p * (len(vals) - 1) + 0.5))], 2) if vals else None
    buckets = Counter("100k-250k" if v < 250e3 else "250k-1m" if v <= 1e6 else ">1m" for v in vals)
    inwin = [r for r in res["filing_rows"]]
    return dict(
        datasets=len(res["ds_hash"]), form4_filings_inspected=sum(1 for s in res["data"]["subs"].values()
                                                                  if s["form"] == F.FORM),
        all_submissions=len(res["data"]["subs"]), code_p_lines=sum(res["line_counts"].values()),
        line_reasons=dict(sorted(res["line_counts"].items())), qualifying_filings=len(res["filings"]),
        qualifying_issuers=len({f.issuer_cik for f in res["filings"].values()}),
        header_candidates=len(res["cand"]), timing_status=dict(sorted(res["timing"].items())),
        filing_minus_acceptance_days=dict(sorted(res["lag"].items())),
        clusters_all=len(cl), clusters_by_window=dict(Counter(r["window_status"] for r in cl)),
        clusters_in_window=len(inw), clusters_in_window_issuers=len({r["issuer_cik"] for r in inw}),
        clusters_in_window_by_year=dict(sorted(by_year.items())),
        insiders_per_event=dict(sorted((str(k) if k < 5 else "5+", v) for k, v in ins.items())),
        cluster_value_quantiles=dict(p05=q(.05), p25=q(.25), p50=q(.5), p75=q(.75), p95=q(.95)),
        cluster_value_buckets=dict(buckets),
        singles_in_window=sum(1 for r in rows if r["kind"] == "single" and r["window_status"] == "in_window"),
        singles_in_window_not_near_cluster=sum(1 for r in rows if r["kind"] == "single" and r["window_status"] ==
                                                "in_window" and not int(r["near_cluster"])),
        brute_force_mismatches=res["mismatch"], filings_rows=len(inwin))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    if a.fetch:
        from concurrent.futures import ThreadPoolExecutor
        import qresearch.sec_edgar as SE
        data, _ = load(SECClient())
        filings = F.qualifying_filings(data)
        cand = sorted(F.header_candidates(filings, SPAN_DAYS))
        print(f"{len(cand)} headers", flush=True)
        workers = 6
        SE.MIN_INTERVAL_S = 0.125 * workers         # per client: <= 8 requests per second in total
        clients = [SECClient() for _ in range(workers)]

        def job(k):
            c = clients[k]
            for acc in cand[k::workers]:
                f = filings[acc]
                if c.get_bytes(F.header_url(f.issuer_cik, acc)) is None:
                    c.get_bytes(F.header_url(f.owner_cik, acc))
            return c.fetched, c.cache_hits
        with ThreadPoolExecutor(workers) as ex:
            print("done", list(ex.map(job, range(workers))), flush=True)
        return
    res = build(verify=True)
    ledger = csv_bytes(res["rows"], FIELDS)
    fil = csv_bytes(res["filing_rows"], ("accession", "issuer_cik", "owner_cik", "filing_date", "acceptance_et",
                                         "timing_status", "value", "n_lines", "roles"))
    payload = lean_payload(res["rows"])
    feas = feasibility(res)
    man = dict(
        spec="research/phase10/H025_spec.md", decision="D204", calendar_source=CALENDAR_SOURCE,
        calendar_sha256=_sha((ROOT / CALENDAR_SOURCE).read_bytes()), datasets_sha256=res["ds_hash"],
        rules=dict(form=F.FORM, code=F.CODE, acquired=F.ACQUIRED, ownership=F.DIRECT,
                   min_insider_usd=F.MIN_INSIDER_USD, min_cluster_usd=F.MIN_CLUSTER_USD, min_insiders=F.MIN_INSIDERS,
                   window_calendar_days=F.WINDOW_DAYS, cooldown_sessions=F.COOLDOWN_SESSIONS, hold_sessions=HOLD,
                   single_min_usd=F.SINGLE_MIN_USD, window_from=str(WINDOW_FROM), last_session=str(LAST_SESSION),
                   span_days=SPAN_DAYS, max_lag_days=MAX_LAG_DAYS),
        sec_ledger_csv_sha256=_sha(ledger), sec_filings_csv_sha256=_sha(fil), lean_payload_sha256=_sha(payload),
        feasibility=feas)
    if a.verify:
        old = json.loads((OUT / "h025_sec_ledger.json").read_text())
        same = all(old[k] == man[k] for k in ("sec_ledger_csv_sha256", "sec_filings_csv_sha256", "lean_payload_sha256"))
        print(json.dumps(dict(rebuild_identical=same, brute_force_mismatches=res["mismatch"],
                              sec_ledger_csv_sha256=man["sec_ledger_csv_sha256"]), indent=1))
        sys.exit(0 if same and res["mismatch"] == 0 else 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "h025_sec_ledger.csv.gz").write_bytes(gzip.compress(ledger, mtime=0))
    (OUT / "h025_sec_filings.csv.gz").write_bytes(gzip.compress(fil, mtime=0))
    (OUT / "h025_sec_ledger.json").write_text(json.dumps(man, indent=1, sort_keys=True) + "\n")
    for name, text in pack(payload).items():
        (LEAN / name).write_text(text)
    print(json.dumps(feas, indent=1))


if __name__ == "__main__":
    main()
