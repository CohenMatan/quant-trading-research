"""P7-CP1 reusable Phase-7 data canary suite (offline, SYNTHETIC; fails loudly if a future change introduces
leakage). Covers: fundamental future-filing invariance, dataset truncation, amendment timing, restatement /
accession protection, estimated filing dates, sector classification point-in-time, the SEC-repaired market cap,
breadth / universe survivorship (point-in-time denominators), cross-domain alignment and determinism. The real-data
counterparts are the QuantConnect audits X991 / X992 (research/phase7/)."""
import hashlib
import json
from datetime import date, timedelta

from conftest import ROOT, load_module

F = load_module(ROOT / "src/qresearch/lean/qr_fundamentals.py", "qr_fundamentals_p7")
I = load_module(ROOT / "src/qresearch/lean/qr_industry.py", "qr_industry_p7")
S = load_module(ROOT / "src/qresearch/lean/qr_sec_corrections.py", "qr_sec_corrections_p7")
import qr_p7 as P  # noqa: E402

FIELDS = ("revenue_ttm4q", "net_income_ttm4q", "operating_cash_flow_ttm4q", "total_assets", "stockholders_equity")


def _filings():
    """A calendar-year filer 2009-2012: (period end, file date, values). FY totals on the 10-K; '_ttm' on a 10-Q is
    the previous fiscal year (vendor semantics, D111)."""
    out = []
    fy_prev = None
    for y in (2009, 2010, 2011, 2012):
        qs = [10 + y - 2009 + i for i in range(4)]
        fy = sum(qs)
        for i, (m, d) in enumerate(((3, 31), (6, 30), (9, 30), (12, 31))):
            pe = date(y, m, d)
            fd = pe + timedelta(days=60 if m == 12 else 35)
            ttm = fy if m == 12 else fy_prev
            v = {"revenue_q": qs[i], "net_income_q": qs[i] / 10, "operating_cash_flow_q": qs[i] / 5,
                 "revenue_ttm": ttm, "net_income_ttm": ttm / 10 if ttm else None,
                 "operating_cash_flow_ttm": ttm / 5 if ttm else None,
                 "total_assets": 1000 + 10 * i + y, "stockholders_equity": 400 + i + y}
            out.append((pe, fd, v))
        fy_prev = fy
    return out


def _replay(filings, dates, upto=None, store_kw=None, early=0):
    """Feed the vendor's reports day by day (each report first seen `early` days before its file date, as a vendor
    may) and record the point-in-time snapshot on each decision date. upto = truncate the dataset at that date."""
    st = F.PITStore(**(store_kw or {}))
    snaps = {}
    d = date(2009, 1, 1)
    end = max(dates)
    while d <= end:
        if upto is not None and d > upto:
            break
        for pe, fd, v in filings:
            if fd - timedelta(days=early) <= d:
                acc = v.get("_acc_year")
                st.observe("K", pe, fd, {k: x for k, x in v.items() if not k.startswith("_")}, acc, d)
        if d in dates:
            r = st.record("K", d)
            snaps[d] = dict({f: st.get("K", f, d) for f in FIELDS},
                            record=None if r is None else (str(r.period_end), str(r.file_date), str(r.available)))
        d += timedelta(days=1)
    return snaps


DATES = [date(2010, m, 28) for m in range(1, 13)] + [date(2011, m, 28) for m in range(1, 13)] + \
    [date(2012, m, 28) for m in range(1, 13)]


def test_future_filing_invariance():
    base = _filings()
    a = _replay(base, set(DATES))
    t0 = date(2011, 6, 28)
    for mutate in ("delete", "change"):
        fut = []
        for pe, fd, v in base:
            if fd > t0:
                if mutate == "delete":
                    continue
                v = dict(v, revenue_q=v["revenue_q"] * 7, total_assets=1)
            fut.append((pe, fd, v))
        b = _replay(fut, set(DATES))
        for d in DATES:
            if d <= t0:
                assert a[d] == b[d], (mutate, d)
    # a vendor that delivers reports 20 days EARLY changes nothing (held until availability)
    c = _replay(base, set(DATES), early=20)
    assert c == a


def test_dataset_truncation():
    base = _filings()
    full = _replay(base, set(DATES))
    for t in (date(2010, 8, 28), date(2011, 3, 28), date(2012, 5, 28)):
        tr = _replay(base, {t}, upto=t)
        assert tr[t] == full[t]


def test_amendment_only_from_its_own_availability():
    base = _filings()
    pe_amend = date(2010, 12, 31)
    amend_fd = date(2011, 5, 10)
    amended = base + [(pe_amend, amend_fd, dict(dict((p, v) for p, _, v in base)[pe_amend], total_assets=5555))]
    a = _replay(base, set(DATES) | {amend_fd, amend_fd + timedelta(days=1)})
    b = _replay(amended, set(DATES) | {amend_fd, amend_fd + timedelta(days=1)})
    for d in sorted(a):
        if d <= amend_fd:
            assert a[d] == b[d], d
    # the amended period is not the current report once Q1 2011 is visible, so its snapshot never shows; but the
    # store's history uses the amended version only from amend_fd + 1 (TTM equality checked via the record dates)
    st = F.PITStore()
    for pe, fd, v in amended:
        st.observe("K", pe, fd, v, None, fd)
    assert st.record("K", amend_fd).period_end == date(2011, 3, 31)


def test_restatement_and_accession_protection():
    base = _filings()
    t = date(2011, 3, 28)                      # after the FY2010 10-K's filing (2011-03-01)
    pe = date(2010, 12, 31)
    fd = dict((p, f) for p, f, _ in base)[pe]
    # (1) the restatement guard: a vendor report carrying later restated values is blocked; the previous report stays
    blocked = {"K": [[str(pe), str(fd)]]}
    s = _replay(base, {t}, store_kw=dict(blocked=blocked))
    assert s[t]["record"][0] == "2010-09-30"
    # (2) an accession number from a later year (value may come from a later filing) is quarantined
    q = [(p, f, dict(v, _acc_year=2013) if p == pe else v) for p, f, v in base]
    s2 = _replay(q, {t})
    assert s2[t]["record"][0] == "2010-09-30"
    # True TTM falls back to the four previous visible quarters (Q4 2009 + Q1-Q3 2010), never the quarantined Q4 2010
    full = _replay(base, {t})
    assert full[t]["record"][0] == "2010-12-31"
    assert s2[t]["revenue_ttm4q"] == 13 + 11 + 12 + 13 and full[t]["revenue_ttm4q"] == 11 + 12 + 13 + 14


def test_estimated_file_date_waits_90_days():
    pe = date(2010, 3, 31)
    st = F.PITStore()
    st.observe("K", pe, pe + timedelta(days=45), {"total_assets": 1.0}, None, pe + timedelta(days=46))
    assert st.record("K", pe + timedelta(days=89)) is None
    assert st.record("K", pe + timedelta(days=90)) is not None


def test_sector_classification_is_point_in_time():
    h = I.SICHistory({"X": [["2010-03-01", 4911, "1"], ["2013-06-01", 6798, "1"]]})
    assert h.sic_on("X", date(2010, 2, 28)) is None                 # nothing known before the first filing
    assert h.sic_on("X", date(2013, 5, 31)) == 4911                 # today's (REIT) code is not projected back
    assert h.sic_on("X", date(2013, 6, 1)) == 6798
    assert I.classify(h.sic_on("X", date(2012, 1, 1)), None) == ("operating", "SIC")


def test_repaired_market_cap_only_from_filed_counts():
    t = {"X": {"status": "repaired", "filings": [
        ["0001-11-000001", "10-Q", "2011-05-05", "2011-03-31", "2011-04-30", 100e6, {}]]}}
    sc = S.SECCorrections(t)
    assert sc.market_cap("X", date(2011, 5, 5), 30.0) is None           # filed that day: not yet usable
    assert sc.market_cap("X", date(2011, 5, 6), 30.0) == 3e9
    sc.observe_split("X", date(2011, 6, 1), 0.5)
    assert sc.market_cap("X", date(2011, 5, 31), 30.0) == 3e9           # split not applied before its ex-date
    assert sc.market_cap("X", date(2011, 6, 1), 15.0) == 3e9


def test_breadth_survivorship_entrants_and_exits():
    """Eligibility from life spans: an IPO enters only once listed and eligible, a delisted / acquired / bankrupt
    company is in every denominator before its exit and in none after; a survivors-only denominator differs."""
    life = {"OLD": (0, 99), "IPO": (40, 99), "ACQ": (0, 30), "BKR": (0, 60)}
    above = {"OLD": True, "IPO": True, "ACQ": False, "BKR": False}
    for day in (10, 35, 50, 70):
        elig = [s for s, (a, b) in life.items() if a <= day <= b]
        share, up, known, n, _ = P.breadth(above, elig)
        assert n == len(elig)
        surv = [s for s in elig if life[s][1] == 99]
        if len(surv) < len(elig):
            assert P.breadth(above, surv)[0] != share                  # survivors-only would be biased
    assert "IPO" not in [s for s, (a, b) in life.items() if a <= 35 <= b]
    assert "ACQ" not in [s for s, (a, b) in life.items() if a <= 35 <= b]


def test_cross_domain_alignment_and_determinism():
    base = _filings()
    t = date(2011, 8, 26)
    s1 = _replay(base, {t})
    s2 = _replay(base, {t})
    assert hashlib.sha256(json.dumps({str(k): v for k, v in s1.items()}, default=str).encode()).hexdigest() == \
        hashlib.sha256(json.dumps({str(k): v for k, v in s2.items()}, default=str).encode()).hexdigest()
    rec = s1[t]["record"]
    ok, late = P.alignment(str(t), price_last_bar="2011-08-26", fundamental_available=rec[2],
                           fundamental_filed=rec[1], sic_effective="2010-03-01", market_cap_day="2011-08-26",
                           breadth_day="2011-08-26")
    assert ok and not late
    assert P.alignment(str(t), fundamental_available="2011-08-27")[1] == ["fundamental_available"]
