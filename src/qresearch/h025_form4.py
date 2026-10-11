"""H025 Insider Cluster Buying: SEC Form 4 parser and online cluster ledger (owner D204; research/phase10/H025_spec.md).

Offline, public SEC data only (no QuantConnect data, no prices, no returns). Inputs:
  * SEC "Insider Transactions Data Sets" (quarterly zips of every Form 3/4/5 XML filing, structured by the SEC's
    Division of Economic and Risk Analysis): SUBMISSION (accession, filing date, document type, issuer CIK / name /
    trading symbol as filed), REPORTINGOWNER (owner CIK, name, relationship, officer title), NONDERIV_TRANS (security
    title, transaction date, code, shares, price, acquired/disposed, direct/indirect ownership);
  * the EDGAR header of each relevant filing (<accession>.hdr.sgml: ACCEPTANCE-DATETIME, US Eastern wall-clock time,
    the time the SEC accepted the filing and made it public).
Everything is cached under data/sec_cache (outside Git; re-acquirable with research/phase10/h025_ledger.py).

The rules below are the frozen H025 definitions (spec sections 3-8); tests/test_p10_h025_form4.py exercises each one.
"""
from __future__ import annotations

import bisect
import csv
import gzip
import io
import re
import zipfile
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

# ----------------------------------------------------------------------------------------------- frozen constants
FORM = "4"                                  # original Form 4 only (4/A amendments and Form 5 never count)
CODE = "P"                                  # open-market or private purchase
ACQUIRED = "A"
DIRECT = "D"
MIN_INSIDER_USD = 25_000.0                  # each qualifying insider's aggregate inside the window
MIN_CLUSTER_USD = 100_000.0                 # sum over the qualifying insiders
MIN_INSIDERS = 2
WINDOW_DAYS = 10                            # acceptance calendar dates in [D - 9, D]
COOLDOWN_SESSIONS = 20                      # next event's entry session >= previous entry session + 20
SINGLE_MIN_USD = 100_000.0                  # single-insider control (diagnostic only)
OPEN = time(9, 30)
# security title = common equity (lower-cased title; pre-registered before any count)
TITLE_INCLUDE = re.compile(r"common|ordinary|capital stock|\bshares?\b")
TITLE_EXCLUDE = re.compile(r"prefer|\bpref\b|depositary|\bads\b|\badr\b|warrant|right|option|\bnotes?\b|debenture|"
                           r"convertible|\bunits?\b|partner|401\s*\(?k|\bfund\b|\bplan\b|phantom|deferred")
CEO_CFO = re.compile(r"\bceo\b|\bcfo\b|chief executive|chief financial|principal executive|principal financial",
                     re.I)
HEADER_ACCEPT = re.compile(rb"<ACCEPTANCE-DATETIME>\s*(\d{14})")
HEADER_FORM = re.compile(rb"<TYPE>\s*([^\s<]+)")
HEADER_DATE = re.compile(rb"<FILING-DATE>\s*(\d{8})")


def roles(relationship: str) -> tuple[bool, bool, bool]:
    """(director, officer, ten_percent_owner) from the data set's concatenated relationship field (e.g.
    'Director,Officer', 'DirectorOther', 'TenPercentOwner')."""
    r = relationship or ""
    return "Director" in r, "Officer" in r, "TenPercentOwner" in r


def common_title(title: str) -> bool:
    t = re.sub(r"\s+", " ", (title or "").strip().lower())
    return bool(TITLE_INCLUDE.search(t)) and not TITLE_EXCLUDE.search(t)


def _num(s):
    try:
        v = float(s)
    except (TypeError, ValueError):
        return None
    return v if v == v else None


def _ddmmmyyyy(s):
    try:
        return datetime.strptime(s.strip(), "%d-%b-%Y").date()
    except (ValueError, AttributeError):
        return None


# ----------------------------------------------------------------------------------------------- data set reader
def read_quarter(raw_zip: bytes) -> dict:
    """One quarterly data set -> dict(subs, owners, lines) restricted to what H025 reads."""
    z = zipfile.ZipFile(io.BytesIO(raw_zip))

    def rows(name):
        with z.open(name) as f:
            yield from csv.DictReader(io.TextIOWrapper(f, "utf-8", errors="replace"), delimiter="\t",
                                      quoting=csv.QUOTE_NONE)
    subs = {}
    for r in rows("SUBMISSION.tsv"):
        subs[r["ACCESSION_NUMBER"]] = dict(form=r["DOCUMENT_TYPE"].strip(), filing_date=_ddmmmyyyy(r["FILING_DATE"]),
                                           issuer_cik=int(r["ISSUERCIK"]) if r["ISSUERCIK"].strip().isdigit() else None,
                                           issuer_name=r["ISSUERNAME"].strip(),
                                           symbol=r["ISSUERTRADINGSYMBOL"].strip().upper())
    owners = defaultdict(list)
    for r in rows("REPORTINGOWNER.tsv"):
        owners[r["ACCESSION_NUMBER"]].append(dict(
            cik=int(r["RPTOWNERCIK"]) if r["RPTOWNERCIK"].strip().isdigit() else None, name=r["RPTOWNERNAME"].strip(),
            relationship=r["RPTOWNER_RELATIONSHIP"].strip(), title=r["RPTOWNER_TITLE"].strip()))
    lines = []
    for r in rows("NONDERIV_TRANS.tsv"):
        if r["TRANS_CODE"].strip() != CODE:
            continue                        # only code-P lines are ever read (all others are excluded by rule)
        lines.append(dict(accession=r["ACCESSION_NUMBER"], sk=int(r["NONDERIV_TRANS_SK"]),
                          title=r["SECURITY_TITLE"].strip(), trans_date=_ddmmmyyyy(r["TRANS_DATE"]),
                          ad=r["TRANS_ACQUIRED_DISP_CD"].strip(), shares=_num(r["TRANS_SHARES"]),
                          price=_num(r["TRANS_PRICEPERSHARE"]), ownership=r["DIRECT_INDIRECT_OWNERSHIP"].strip()))
    return dict(subs=subs, owners=dict(owners), lines=lines)


def merge_quarters(parts: list[dict]) -> dict:
    """Union of quarterly data sets (an accession appearing twice must be identical: else ValueError)."""
    subs, owners, lines, seen = {}, {}, [], set()
    for p in parts:
        for a, s in p["subs"].items():
            if a in subs and subs[a] != s:
                raise ValueError(f"accession {a} differs between quarterly data sets")
            subs[a] = s
        for a, o in p["owners"].items():
            if a in owners and owners[a] != o:
                raise ValueError(f"owners of {a} differ between quarterly data sets")
            owners[a] = o
        for ln in p["lines"]:
            k = (ln["accession"], ln["sk"])
            if k not in seen:
                seen.add(k)
                lines.append(ln)
    return dict(subs=subs, owners=owners, lines=lines)


# ----------------------------------------------------------------------------------------------- qualification
LINE_REASONS = ("not_form4", "joint_filing", "no_owner_cik", "not_director_officer", "not_acquisition",
                "indirect", "title_not_common", "missing_price", "missing_shares", "no_issuer_cik")


def classify_line(ln: dict, sub: dict | None, own: list | None) -> str:
    """'ok' or the FIRST failing rule (order = LINE_REASONS) for one code-P non-derivative line."""
    if sub is None or sub["form"] != FORM:
        return "not_form4"
    if not own or len(own) != 1:
        return "joint_filing"
    o = own[0]
    if o["cik"] is None:
        return "no_owner_cik"
    d, f, _ = roles(o["relationship"])
    if not (d or f):
        return "not_director_officer"
    if ln["ad"] != ACQUIRED:
        return "not_acquisition"
    if ln["ownership"] != DIRECT:
        return "indirect"
    if not common_title(ln["title"]):
        return "title_not_common"
    if ln["price"] is None or ln["price"] <= 0:
        return "missing_price"
    if ln["shares"] is None or ln["shares"] <= 0:
        return "missing_shares"
    if sub["issuer_cik"] is None:
        return "no_issuer_cik"
    return "ok"


@dataclass
class Filing:
    """One original Form 4 with >= 1 qualifying purchase line (values from qualifying lines only)."""
    accession: str
    issuer_cik: int
    owner_cik: int
    owner_name: str
    director: bool
    officer: bool
    ten_pct: bool
    title: str
    filing_date: date
    symbol: str
    lines: list = field(default_factory=list)           # (trans_date, shares, price, value)
    acceptance: datetime | None = None                   # US Eastern, from the EDGAR header

    @property
    def value(self) -> float:
        return sum(v for _, _, _, v in self.lines)

    @property
    def ceo_cfo(self) -> bool:
        return bool(CEO_CFO.search(self.title or ""))


def qualifying_filings(data: dict, counts: dict | None = None) -> dict[str, Filing]:
    """accession -> Filing for every original Form 4 holding >= 1 qualifying line. counts (optional) receives the
    line-level reason tallies."""
    out: dict[str, Filing] = {}
    tally = defaultdict(int)
    for ln in sorted(data["lines"], key=lambda x: (x["accession"], x["sk"])):
        a = ln["accession"]
        sub, own = data["subs"].get(a), data["owners"].get(a)
        why = classify_line(ln, sub, own)
        tally[why] += 1
        if why != "ok":
            continue
        f = out.get(a)
        if f is None:
            o = own[0]
            d, fo, tp = roles(o["relationship"])
            f = out[a] = Filing(accession=a, issuer_cik=sub["issuer_cik"], owner_cik=o["cik"], owner_name=o["name"],
                                director=d, officer=fo, ten_pct=tp, title=o["title"], filing_date=sub["filing_date"],
                                symbol=sub["symbol"])
        f.lines.append((ln["trans_date"], ln["shares"], ln["price"], ln["shares"] * ln["price"]))
    if counts is not None:
        counts.update(tally)
    return out


def header_candidates(filings: dict[str, Filing], span_days: int) -> set[str]:
    """Superset of the filings that can belong to a cluster or a single-insider control: per issuer, a filing whose
    filing date lies within span_days of a filing by ANOTHER owner, or whose owner's purchases filed within span_days
    total >= SINGLE_MIN_USD. (Acceptance date <= filing date <= acceptance date + span slack; verified on every fetched
    header, spec section 4.)"""
    by_issuer = defaultdict(list)
    for f in filings.values():
        by_issuer[f.issuer_cik].append(f)
    keep = set()
    for fs in by_issuer.values():
        fs.sort(key=lambda f: (f.filing_date, f.accession))
        days = [f.filing_date for f in fs]
        for i, f in enumerate(fs):
            lo = bisect.bisect_left(days, f.filing_date - timedelta(days=span_days))
            hi = bisect.bisect_right(days, f.filing_date + timedelta(days=span_days))
            near = fs[lo:hi]
            if any(g.owner_cik != f.owner_cik for g in near):
                keep.add(f.accession)
            elif sum(g.value for g in near if g.owner_cik == f.owner_cik) >= SINGLE_MIN_USD:
                keep.add(f.accession)
    return keep


def parse_header(raw: bytes) -> dict:
    """EDGAR <accession>.hdr.sgml -> dict(acceptance (naive US Eastern datetime or None), form, filing_date)."""
    m = HEADER_ACCEPT.search(raw or b"")
    acc = None
    if m:
        try:
            acc = datetime.strptime(m.group(1).decode(), "%Y%m%d%H%M%S")
        except ValueError:
            acc = None
    fm, dm = HEADER_FORM.search(raw or b""), HEADER_DATE.search(raw or b"")
    fd = None
    if dm:
        try:
            fd = datetime.strptime(dm.group(1).decode(), "%Y%m%d").date()
        except ValueError:
            fd = None
    return dict(acceptance=acc, form=fm.group(1).decode() if fm else None, filing_date=fd)


def header_url(issuer_cik: int, accession: str) -> str:
    return (f"https://www.sec.gov/Archives/edgar/data/{int(issuer_cik)}/{accession.replace('-', '')}/"
            f"{accession}.hdr.sgml")


def timing_status(f: Filing, hdr: dict | None, max_lag_days: int) -> str:
    """'ok' or the timing exclusion reason (spec section 4): the header must exist, carry a time of day, be a Form 4
    with the data set's filing date, and the acceptance date must be <= the filing date and >= filing date -
    max_lag_days (Section 16 forms accepted after 22:00 ET carry the next business day's filing date)."""
    if hdr is None:
        return "header_missing"
    a = hdr["acceptance"]
    if a is None:
        return "acceptance_missing"
    if a.time() == time(0, 0, 0):
        return "acceptance_no_time"
    if hdr["form"] != FORM:
        return "header_form_mismatch"
    if hdr["filing_date"] != f.filing_date:
        return "header_date_mismatch"
    if not (f.filing_date - timedelta(days=max_lag_days) <= a.date() <= f.filing_date):
        return "acceptance_outside_filing_date"
    if any(td is None or td > a.date() for td, *_ in f.lines):
        return "transaction_date_invalid"
    return "ok"


# ----------------------------------------------------------------------------------------------- calendar
class Sessions:
    """Trading sessions (sorted dates) with the H025 entry rule."""

    def __init__(self, sessions):
        self.s = sorted(set(sessions))
        self.idx = {d: i for i, d in enumerate(self.s)}

    def entry(self, acc: datetime) -> date | None:
        """First regular-session open strictly after the acceptance time: the acceptance date's own open if it is a
        session and the acceptance is before 09:30 ET, else the next session after the acceptance date."""
        d = acc.date()
        if d in self.idx and acc.time() < OPEN:
            return d
        i = bisect.bisect_right(self.s, d)
        return self.s[i] if i < len(self.s) else None


# ----------------------------------------------------------------------------------------------- clusters
@dataclass
class Event:
    event_id: str
    kind: str                                            # 'cluster' or 'single' (diagnostic control)
    issuer_cik: int
    trigger: datetime
    entry: date
    insiders: list                                        # owner CIKs (qualifying), sorted
    accessions: list                                      # accessions inside the window at the trigger (all owners)
    qualifying_accessions: list
    insider_values: dict                                  # owner CIK -> window aggregate (qualifying insiders)
    cluster_value: float
    symbol: str
    later: list = field(default_factory=list)             # descriptive: later qualifying filings within 10 days


def _window(fs, k):
    """Filings of one issuer inside the window ending at filing k (acceptance dates in [D-9, D], acceptance <= t)."""
    t = fs[k].acceptance
    lo = t.date() - timedelta(days=WINDOW_DAYS - 1)
    return [g for g in fs[:k + 1] if g.acceptance.date() >= lo]


def _state(win):
    agg = defaultdict(float)
    for g in win:
        agg[g.owner_cik] += g.value
    q = {o: v for o, v in agg.items() if v >= MIN_INSIDER_USD}
    return agg, q


def build_events(filings: list[Filing], cal: Sessions, start: date, last_exit: date, kind: str = "cluster") -> list:
    """Online events of ONE issuer (filings with valid acceptance times). Processing order = acceptance time, then
    accession. A cluster triggers at the first filing after which >= MIN_INSIDERS distinct owners each have
    >= MIN_INSIDER_USD inside the window and their sum >= MIN_CLUSTER_USD; a 'single' control triggers when exactly one
    owner holds >= MIN_INSIDER_USD in the window, with >= SINGLE_MIN_USD. Cooldown: a trigger whose entry session is
    < previous entry + COOLDOWN_SESSIONS (same kind, same issuer) is suppressed. Events are kept (in the ledger)
    whatever their dates; `start` / `last_exit` only bound the trading calendar used (entry must exist and its
    20-session exit must be <= last_exit, else the event is labelled by the caller)."""
    fs = sorted(filings, key=lambda f: (f.acceptance, f.accession))
    out, last_entry_i = [], None
    for k, f in enumerate(fs):
        win = _window(fs, k)
        agg, q = _state(win)
        if kind == "cluster":
            ok = len(q) >= MIN_INSIDERS and sum(q.values()) >= MIN_CLUSTER_USD
        else:
            ok = len(q) == 1 and next(iter(q.values())) >= SINGLE_MIN_USD
        if not ok:
            continue
        e = cal.entry(f.acceptance)
        if e is None:
            continue
        ei = cal.idx[e]
        if last_entry_i is not None and ei < last_entry_i + COOLDOWN_SESSIONS:
            continue
        last_entry_i = ei
        ins = sorted(q)
        eid = f"{kind[0].upper()}{f.issuer_cik:010d}-{f.acceptance:%Y%m%d%H%M%S}-{f.accession}"
        ev = Event(event_id=eid, kind=kind, issuer_cik=f.issuer_cik, trigger=f.acceptance, entry=e, insiders=ins,
                   accessions=[g.accession for g in win],
                   qualifying_accessions=[g.accession for g in win if g.owner_cik in q],
                   insider_values={o: round(q[o], 2) for o in ins}, cluster_value=round(sum(q.values()), 2),
                   symbol=f.symbol)
        ev.later = [g.accession for g in fs[k + 1:] if g.acceptance.date() <= f.acceptance.date() + timedelta(
            days=WINDOW_DAYS - 1)]
        out.append(ev)
    return out


def brute_force_triggers(filings: list[Filing], cal: Sessions, kind: str = "cluster") -> list[tuple]:
    """Independent reference implementation (determinism check): for EVERY distinct acceptance timestamp t of the
    issuer, recompute from scratch the set of filings public at t whose acceptance date is >= date(t) - 9 and test the
    criteria; then apply the cooldown in time order. Returns [(trigger, entry, insiders)]."""
    times = sorted({(f.acceptance, f.accession) for f in filings})
    cand = []
    for t, a in times:
        pub = [f for f in filings if (f.acceptance, f.accession) <= (t, a)
               and f.acceptance.date() >= t.date() - timedelta(days=WINDOW_DAYS - 1)]
        agg = {}
        for f in pub:
            agg[f.owner_cik] = agg.get(f.owner_cik, 0.0) + f.value
        q = {o: v for o, v in agg.items() if v >= MIN_INSIDER_USD}
        if kind == "cluster":
            ok = len(q) >= MIN_INSIDERS and sum(q.values()) >= MIN_CLUSTER_USD
        else:
            ok = len(q) == 1 and max(q.values()) >= SINGLE_MIN_USD
        if ok:
            cand.append((t, cal.entry(t), tuple(sorted(q))))
    out, last = [], None
    for t, e, ins in cand:
        if e is None:
            continue
        if last is not None and cal.idx[e] < last + COOLDOWN_SESSIONS:
            continue
        last = cal.idx[e]
        out.append((t, e, ins))
    return out


def load_zip(path) -> bytes:
    raw = open(path, "rb").read()
    return gzip.decompress(raw) if str(path).endswith(".gz") else raw
