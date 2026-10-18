"""LH-CP3 targeted EDGAR header requests (owner D244; protocol 7). Only the accessions of the committed manifest; the
URL builder refuses anything filed after 2021-12-31 or not an original 10-Q / 10-K; at most 150 HTTP requests in total
(retries and fallbacks included), at most 2 per second; a 403 / block stops the network portion. Only the header is
kept (the body after </SEC-HEADER> is discarded unread). The User-Agent carries the owner-authorised contact from the
existing runtime configuration (never written to the repository or the log).

    PYTHONPATH=src python research/longhorizon/cp3/LH_CP3_fetch_headers.py
"""
from __future__ import annotations

import gzip
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

import lh_cp3_safe as HS

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
MANIFEST = HERE / "LH_CP3_manifest.json"
LOG = HERE / "LH_CP3_request_log.json"
HEADERS = HERE / "LH_CP3_headers.json"
CACHE = ROOT / "data/sec_cache/lh_cp3_headers"
BUDGET = 150
MIN_INTERVAL = 0.6


class Budget(Exception):
    pass


class Blocked(Exception):
    pass


def reparse():
    """Re-parse the cached headers only (no network; the request log is left untouched)."""
    man = json.loads(MANIFEST.read_text())
    headers = {}
    for a in man["accessions"]:
        cp = CACHE / f"{a['accession']}.hdr.gz"
        if not cp.exists():
            headers[a["accession"]] = dict(status="not_retrieved")
            continue
        ph = HS.parse_header(gzip.decompress(cp.read_bytes()), a["accession"])
        headers[a["accession"]] = dict(status=ph["status"], source="cache", **ph["fields"])
    HEADERS.write_text(json.dumps(dict(kind="LH-CP3 extracted EDGAR header fields (metadata only)", decision="D244",
                                       manifest_sha256=hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
                                       parsed_from="cache (reparse; 0 requests)", headers=headers),
                                  indent=1, sort_keys=True) + "\n")
    print({s: sum(1 for h in headers.values() if h["status"] == s) for s in {h["status"] for h in headers.values()}})


def main():
    import sys
    if "--reparse" in sys.argv:
        return reparse()
    if LOG.exists():
        raise SystemExit("STOP: a request log already exists (the network portion ran); use --reparse")
    from qresearch.sec_edgar import contact_user_agent
    ua = contact_user_agent()
    if "@" not in ua:
        raise SystemExit("STOP: no authorised SEC contact configured (not inventing one)")
    man = json.loads(MANIFEST.read_text())
    m_hash = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
    rows = {a["accession"]: a for a in man["accessions"]}
    sess = requests.Session()
    state = dict(n=0, last=0.0)
    log, headers = [], {}
    stopped = None

    def get(url, accn, filed, stream=False):
        for attempt in range(3):
            if state["n"] >= BUDGET:
                raise Budget()
            wait = MIN_INTERVAL - (time.monotonic() - state["last"])
            if wait > 0:
                time.sleep(wait)
            state["last"] = time.monotonic()
            state["n"] += 1
            t0 = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            try:
                r = sess.get(url, headers={"User-Agent": ua, "Accept-Encoding": "gzip, deflate"}, timeout=60,
                             stream=True)
            except requests.RequestException as e:
                log.append(dict(n=state["n"], accession=accn, url=url, filed=filed, status=f"error:{type(e).__name__}",
                                bytes=0, time_utc=t0))
                time.sleep(2 ** (attempt + 1))
                continue
            body = b""
            if r.status_code == 200:
                for chunk in r.iter_content(8192):
                    body += chunk
                    if any(mk in body for mk in HS.END_MARKERS) or len(body) >= HS.MAX_BYTES:
                        break
                body = HS.truncate_header(body)
            r.close()
            log.append(dict(n=state["n"], accession=accn, url=url, filed=filed, status=r.status_code, bytes=len(body),
                            time_utc=t0))
            if r.status_code == 200:
                return body
            if r.status_code == 404:
                return None
            if r.status_code == 403:
                raise Blocked(f"HTTP 403 for {accn}")
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(2 ** (attempt + 1))
                continue
            return None
        return None

    CACHE.mkdir(parents=True, exist_ok=True)
    try:
        for a in man["accessions"]:
            accn, cik, filed = a["accession"], a["cik"], a["filed"]
            cp = CACHE / f"{accn}.hdr.gz"
            if cp.exists():
                raw = gzip.decompress(cp.read_bytes())
                src = "cache"
            else:
                url = HS.header_url(cik, accn, rows)                # cut-off / manifest checks before the URL exists
                raw = get(url, accn, filed)
                src = "hdr.sgml"
                if raw is None:
                    raw = get(HS.fallback_url(cik, accn, rows), accn, filed, stream=True)
                    src = "txt-bounded"
                if raw is not None:
                    cp.write_bytes(gzip.compress(raw))
            if raw is None:
                headers[accn] = dict(status="not_retrieved")
                continue
            ph = HS.parse_header(raw, accn)
            headers[accn] = dict(status=ph["status"], source=src, **ph["fields"])
    except Budget:
        stopped = "request budget (150) reached"
    except Blocked as e:
        stopped = f"SEC blocked the request ({e}); network portion stopped"
    out_log = dict(kind="LH-CP3 EDGAR header request log (no credentials, no contact address)", decision="D244",
                   manifest_sha256=m_hash, budget=BUDGET, min_interval_s=MIN_INTERVAL, requests=state["n"],
                   stopped=stopped, log=log)
    LOG.write_text(json.dumps(out_log, indent=1, sort_keys=True) + "\n")
    HEADERS.write_text(json.dumps(dict(kind="LH-CP3 extracted EDGAR header fields (metadata only)", decision="D244",
                                       manifest_sha256=m_hash, headers=headers), indent=1, sort_keys=True) + "\n")
    print(json.dumps(dict(requests=state["n"], stopped=stopped,
                          statuses={s: sum(1 for h in headers.values() if h["status"] == s)
                                    for s in {h["status"] for h in headers.values()}}), indent=1))


if __name__ == "__main__":
    main()
