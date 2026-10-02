"""Index of every XBRL filing 2009-06..2021-12 from the SEC's monthly XBRL RSS archives (D113). Public SEC data.

Per filing: CIK, accession, form, filing date, acceptance time, period, ASSIGNED SIC (the SEC's industry code for
the registrant AS OF THAT FILING — historical, not current-status), fiscal-year end, company name as filed, and
the XBRL instance document's file name. Filers name the instance '<prefix>-<period>.xml'; the prefix is usually the
registrant's trading symbol, so it is dated ticker EVIDENCE (never proof on its own).

Output: data/sec_derived/xbrl_filings.json.gz (outside Git; rebuilt from the cached archives by re-running)."""
from __future__ import annotations

import gzip
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from qresearch.sec_edgar import SECClient  # noqa: E402

OUT = ROOT / "data" / "sec_derived" / "xbrl_filings.json.gz"
# the archives use http://www.sec.gov/Archives/edgar up to 2019 and https://... from 2020 (D113a: the first index
# silently dropped every 2020-2021 filing because only the http namespace was searched)
NAMESPACES = ("http://www.sec.gov/Archives/edgar", "https://www.sec.gov/Archives/edgar")
INSTANCE = re.compile(r"^([A-Za-z][A-Za-z0-9.]{0,9})-(\d{8})(?:\.xml|_htm\.xml)$")
SCHEMA = re.compile(r"^([A-Za-z][A-Za-z0-9.]{0,9})-(\d{8})\.xsd$")


def iso(mmddyyyy):
    m, d, y = mmddyyyy.split("/")
    return f"{y}-{m}-{d}"


def instance_prefix(files, E):
    """(prefix, file) from the instance document's name; for inline XBRL filings (no separate instance listed,
    common from 2019) from the extension schema's name '<prefix>-<period>.xsd', which follows the same convention."""
    for f in files:
        name, typ = f.get(E + "file", ""), f.get(E + "type", "")
        if typ in ("EX-101.INS",) or name.endswith(".xml") and "_" not in name.split("-")[0]:
            m = INSTANCE.match(name)
            if m and typ in ("EX-101.INS", ""):
                return m.group(1).upper(), name
    for f in files:
        m = INSTANCE.match(f.get(E + "file", ""))
        if m and f.get(E + "type", "") == "EX-101.INS":
            return m.group(1).upper(), f.get(E + "file")
    for f in files:
        m = SCHEMA.match(f.get(E + "file", ""))
        if m and f.get(E + "type", "") == "EX-101.SCH":
            return m.group(1).upper(), f.get(E + "file")
    return None, None


def parse(raw: bytes):
    out = []
    root = ET.fromstring(raw)
    for item in root.iter("item"):
        x = None
        for ns in NAMESPACES:
            NS, E = {"edgar": ns}, "{%s}" % ns
            x = item.find("edgar:xbrlFiling", NS)
            if x is not None:
                break
        if x is None:
            continue
        g = lambda k: (x.findtext(f"edgar:{k}", default="", namespaces=NS) or "").strip()
        files = x.findall("edgar:xbrlFiles/edgar:xbrlFile", NS)
        pref, inst = instance_prefix(files, E)
        out.append({"cik": int(g("cikNumber") or 0), "accn": g("accessionNumber"), "form": g("formType"),
                    "filed": iso(g("filingDate")) if g("filingDate") else None,
                    "accepted": g("acceptanceDatetime")[:8] or None, "period": g("period") or None,
                    "sic": int(g("assignedSic")) if g("assignedSic").isdigit() else None, "fye": g("fiscalYearEnd"),
                    "name": g("companyName"), "instance": inst, "prefix": pref})
    if not out and b"<item>" in raw:
        raise ValueError("XBRL RSS archive has items but none parsed (namespace/format change?)")
    return out


def main():
    client = SECClient()
    rows = []
    for y in range(2009, 2022):
        for m in range(1, 13):
            if (y, m) < (2009, 6):
                continue
            raw = client.xbrl_rss(y, m)
            got = parse(raw) if raw else []
            if not got:
                raise RuntimeError(f"no XBRL filings parsed for {y}-{m:02d}")     # every month must contribute
            rows += got
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(gzip.compress(json.dumps(rows).encode()))
    n_pref = sum(1 for r in rows if r["prefix"])
    print(len(rows), "filings;", n_pref, "with an instance prefix;", len({r['cik'] for r in rows}), "registrants")
    return rows


def load():
    return json.loads(gzip.decompress(OUT.read_bytes()))


if __name__ == "__main__":
    main()
