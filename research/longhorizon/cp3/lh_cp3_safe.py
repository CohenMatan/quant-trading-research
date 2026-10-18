"""LH-CP3 (owner D244): cut-off enforcement for the targeted EDGAR header requests (protocol 1 and 7).

* header_url() refuses to build a URL unless the accession is in the committed manifest, its local filing date is
  <= 2021-12-31 and it is an original 10-Q / 10-K.
* parse_header() checks FILED AS OF DATE <= CUT and the accession match BEFORE any other field is extracted; the
  company-data block is withheld when DATE AS OF CHANGE is after the cut-off; nothing after the end of the header is
  read. Local SEC records come through the LH-CP2 loaders (research/longhorizon/cp2/lh_cp2_safe.py)."""
from __future__ import annotations

import re

CUT = "2021-12-31"
CUT_COMPACT = CUT.replace("-", "")
ALLOWED_FORMS = ("10-Q", "10-K", "10-K405")
END_MARKERS = (b"</SEC-HEADER>", b"</IMS-HEADER>")
MAX_BYTES = 64 * 1024
_ACCN = re.compile(r"^\d{10}-\d{2}-\d{6}$")


class CutoffError(ValueError):
    pass


def header_url(cik, accession, manifest) -> str:
    """manifest: {accession: {"filed": 'YYYY-MM-DD', "form": ..., "cik": ...}} (the committed sample manifest)."""
    if not _ACCN.match(str(accession)):
        raise CutoffError(f"malformed accession {accession!r}")
    row = manifest.get(accession)
    if row is None:
        raise CutoffError("accession not in the committed manifest")
    if not row.get("filed") or row["filed"] > CUT:
        raise CutoffError("filing date missing or after the cut-off")
    if row.get("form") not in ALLOWED_FORMS:
        raise CutoffError(f"form {row.get('form')!r} is not an original 10-Q / 10-K")
    if int(row["cik"]) != int(cik):
        raise CutoffError("CIK does not match the manifest")
    return (f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/"
            f"{accession}.hdr.sgml")


def fallback_url(cik, accession, manifest) -> str:
    u = header_url(cik, accession, manifest)          # same checks
    return u[: -len(".hdr.sgml")] + ".txt"


def truncate_header(raw: bytes) -> bytes:
    """Only the header: everything after the first end-of-header marker (or MAX_BYTES) is discarded."""
    raw = raw[:MAX_BYTES]
    cut = min((raw.find(m) + len(m) for m in END_MARKERS if raw.find(m) >= 0), default=len(raw))
    return raw[:cut]


def _field(text, name):
    m = re.search(rf"^\s*{re.escape(name)}:\s*(.+?)\s*$", text, re.M)
    return m.group(1) if m else None


def parse_header(raw: bytes, accession: str) -> dict:
    """-> dict(status, fields). status 'ok' | 'discarded:<reason>'. Checks the cut-off and the accession first."""
    text = truncate_header(raw or b"").decode("latin-1")
    filed = _field(text, "FILED AS OF DATE")
    accn = _field(text, "ACCESSION NUMBER")
    if not filed or not re.fullmatch(r"\d{8}", filed):
        return dict(status="discarded:no_filed_date", fields={})
    if filed > CUT_COMPACT:
        return dict(status="discarded:filed_after_cutoff", fields={})
    if accn != accession:
        return dict(status="discarded:accession_mismatch", fields={})
    changed = _field(text, "DATE AS OF CHANGE")
    company_ok = not (changed and re.fullmatch(r"\d{8}", changed) and changed > CUT_COMPACT)
    f = dict(accession=accn, filed=filed,
             submission_type=_field(text, "CONFORMED SUBMISSION TYPE"),
             period=_field(text, "CONFORMED PERIOD OF REPORT"),
             acceptance=_acceptance(text),
             date_as_of_change_after_cutoff=not company_ok,
             date_as_of_change=changed if company_ok else None)
    if company_ok:
        f["cik"] = _field(text, "CENTRAL INDEX KEY")
        f["fiscal_year_end"] = _field(text, "FISCAL YEAR END")
        f["form_type"] = _field(text, "FORM TYPE")
        f["former_name_change_dates"] = sorted(d for d in re.findall(r"DATE OF NAME CHANGE:\s*(\d{8})", text)
                                               if d <= CUT_COMPACT)
    return dict(status="ok", fields=f)


def _acceptance(text):
    m = re.search(r"<ACCEPTANCE-DATETIME>(\d{14})", text)
    return m.group(1) if m else None
