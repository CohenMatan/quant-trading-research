"""SEC EDGAR access for the point-in-time fundamentals verification and the D043 survivorship repair (D111).

Public-domain SEC data only (no QuantConnect data). Every response is cached on disk under /data/sec_cache (outside
Git, re-acquirable by re-running) so each URL is fetched at most once; requests are throttled well below the SEC
fair-access limit of 10 per second and carry a project User-Agent. The SEC contact address the owner authorised
(2026-10-02, D113) is appended at run time from the environment variable SEC_CONTACT_EMAIL or the local file
~/.config/qresearch/sec_contact; it is never written into code, data files, logs or Git.

Hosts:
  * data.sec.gov  — submissions (filing history: form, filing date, acceptance time, report date, accession) and
                    XBRL APIs (companyfacts: every filing that reported each fact, with its filing date; frames).
  * www.sec.gov   — archives (monthly XBRL RSS: per-filing assigned SIC and instance file names; insider Form 4
                    XML: issuerTradingSymbol). Needs the contact address (403 "undeclared automated tool" without
                    it, D111).
"""
from __future__ import annotations

import gzip
import json
import time
from pathlib import Path

import requests

from . import config

USER_AGENT = "QuantTradingResearch PIT-audit private-research-project"
CONTACT_FILE = Path.home() / ".config" / "qresearch" / "sec_contact"


def contact_user_agent() -> str:
    """Project User-Agent plus the owner-authorised contact address (runtime only; never persisted)."""
    import os
    email = os.environ.get("SEC_CONTACT_EMAIL") or (CONTACT_FILE.read_text().strip() if CONTACT_FILE.exists() else "")
    return f"QuantTradingResearch PIT-audit {email}" if email else USER_AGENT
CACHE_DIR = config.REPO_ROOT / "data" / "sec_cache"
MIN_INTERVAL_S = 0.125         # <= 8 requests per second (SEC fair-access limit: 10)


class SECError(RuntimeError):
    pass


class SECClient:
    def __init__(self, cache_dir: Path = CACHE_DIR, user_agent: str | None = None, session=None, sleep=time.sleep):
        self.cache_dir = Path(cache_dir)
        self.user_agent = user_agent or contact_user_agent()
        self.session = session or requests.Session()
        self._sleep = sleep
        self._last = 0.0
        self.fetched = 0           # network requests made by this client
        self.cache_hits = 0

    def _path(self, url: str) -> Path:
        rel = url.split("://", 1)[1].replace("?", "_").replace("&", "_")
        return self.cache_dir / (rel + ".gz")

    def get_bytes(self, url: str, allow_missing: bool = True) -> bytes | None:
        """Raw response body at `url` (cached on disk). None for a 404 when allow_missing."""
        p = self._path(url)
        if p.exists():
            self.cache_hits += 1
            raw = gzip.decompress(p.read_bytes())
            return None if raw == b"null" else raw
        for attempt in range(5):
            wait = MIN_INTERVAL_S - (time.monotonic() - self._last)
            if wait > 0:
                self._sleep(wait)
            self._last = time.monotonic()
            r = self.session.get(url, headers={"User-Agent": self.user_agent, "Accept-Encoding": "gzip, deflate"},
                                 timeout=120)
            self.fetched += 1
            if r.status_code == 200:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(gzip.compress(r.content))
                return r.content
            if r.status_code == 404 and allow_missing:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(gzip.compress(b"null"))
                return None
            if r.status_code in (429, 500, 502, 503, 504):
                self._sleep(2 ** attempt)
                continue
            raise SECError(f"SEC request failed: HTTP {r.status_code} for {url}")
        raise SECError(f"SEC request failed after retries: {url}")

    def get_json(self, url: str, allow_missing: bool = True):
        """JSON at `url` (cached). Returns None for a 404 when allow_missing (e.g. a CIK without XBRL facts)."""
        raw = self.get_bytes(url, allow_missing)
        return None if raw is None else json.loads(raw)

    # ------------------------------------------------------------------ endpoints
    def companyfacts(self, cik: int):
        return self.get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json")

    def submissions(self, cik: int) -> dict | None:
        """Filing history with the older pages merged in (columns: accessionNumber, filingDate, reportDate,
        acceptanceDateTime, form, ...)."""
        d = self.get_json(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json")
        if d is None:
            return None
        cols = dict(d["filings"]["recent"])
        for f in d["filings"].get("files", []):
            more = self.get_json(f"https://data.sec.gov/submissions/{f['name']}")
            if more:
                for k in cols:
                    cols[k] = list(cols[k]) + list(more.get(k, [None] * len(more["accessionNumber"])))
        d["filings_all"] = cols
        return d

    def xbrl_rss(self, year: int, month: int) -> bytes | None:
        """Monthly EDGAR XBRL RSS archive (every XBRL filing of the month: CIK, form, filing date, acceptance time,
        period, assigned SIC, fiscal-year end, file list incl. the instance document name)."""
        return self.get_bytes(f"https://www.sec.gov/Archives/edgar/monthly/xbrlrss-{year}-{month:02d}.xml")

    def frame(self, taxonomy: str, tag: str, unit: str, period: str):
        return self.get_json(f"https://data.sec.gov/api/xbrl/frames/{taxonomy}/{tag}/{unit}/{period}.json")


def filings_table(sub: dict) -> list[dict]:
    """Rows of a submissions record: one dict per filing."""
    cols = sub["filings_all"]
    keys = list(cols)
    return [dict(zip(keys, vals)) for vals in zip(*(cols[k] for k in keys))]
