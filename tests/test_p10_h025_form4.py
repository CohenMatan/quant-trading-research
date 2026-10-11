"""H025 Form 4 parser and online cluster ledger (research/phase10/H025_spec.md sections 3-6): synthetic filings only."""
from datetime import date, datetime, timedelta

import pytest

from qresearch import h025_form4 as F


def sessions(start=date(2011, 1, 3), n=400):
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return F.Sessions(out)


CAL = sessions()


def filing(acc, owner, value, when, issuer=100, director=True, officer=False, title="", tdate=None):
    f = F.Filing(accession=acc, issuer_cik=issuer, owner_cik=owner, owner_name=f"O{owner}", director=director,
                 officer=officer, ten_pct=False, title=title, filing_date=when.date(), symbol="XYZ")
    f.lines = [(tdate or when.date() - timedelta(days=2), 1000.0, value / 1000.0, float(value))]
    f.acceptance = when
    return f


def dt(day, hh=16, mm=30):
    return datetime(2011, 3, day, hh, mm)


# ------------------------------------------------------------------ line rules (section 3)
def sub(form="4", cik=100):
    return dict(form=form, filing_date=date(2011, 3, 1), issuer_cik=cik, issuer_name="X", symbol="X")


def own(rel="Director", n=1, cik=7):
    return [dict(cik=cik, name="A", relationship=rel, title="") for _ in range(n)]


def line(**kw):
    d = dict(accession="a", sk=1, title="Common Stock", trans_date=date(2011, 2, 27), ad="A", shares=100.0,
             price=10.0, ownership="D")
    d.update(kw)
    return d


@pytest.mark.parametrize("args,why", [
    ((line(), sub(), own()), "ok"),
    ((line(), sub("4/A"), own()), "not_form4"),
    ((line(), sub("5"), own()), "not_form4"),
    ((line(), sub(), own(n=2)), "joint_filing"),
    ((line(), sub(), own(cik=None)), "no_owner_cik"),
    ((line(), sub(), own("TenPercentOwner")), "not_director_officer"),
    ((line(), sub(), own("Other")), "not_director_officer"),
    ((line(), sub(), own("Director,TenPercentOwner")), "ok"),
    ((line(), sub(), own("OfficerOther")), "ok"),
    ((line(ad="D"), sub(), own()), "not_acquisition"),
    ((line(ownership="I"), sub(), own()), "indirect"),
    ((line(title="Series A Preferred Stock"), sub(), own()), "title_not_common"),
    ((line(title="Common Units representing LP interests"), sub(), own()), "title_not_common"),
    ((line(title="American Depositary Shares"), sub(), own()), "title_not_common"),
    ((line(title="Class A Common Stock, par value $0.01"), sub(), own()), "ok"),
    ((line(title="Ordinary Shares"), sub(), own()), "ok"),
    ((line(price=None), sub(), own()), "missing_price"),
    ((line(price=0.0), sub(), own()), "missing_price"),
    ((line(shares=0.0), sub(), own()), "missing_shares"),
    ((line(), sub(cik=None), own()), "no_issuer_cik"),
])
def test_line_rules(args, why):
    assert F.classify_line(*args) == why


def test_roles_parse_concatenated_relationships():
    assert F.roles("Director,Officer,TenPercentOwner") == (True, True, True)
    assert F.roles("DirectorOther") == (True, False, False)
    assert F.roles("TenPercentOwnerOther") == (False, False, True)


def test_qualifying_filings_value_and_dedup_of_lines():
    data = dict(subs={"a": sub(), "b": sub()}, owners={"a": own(cik=1), "b": own(cik=2)},
                lines=[line(accession="a", sk=1, shares=1000, price=20.0),
                       line(accession="a", sk=2, shares=500, price=10.0),
                       line(accession="a", sk=3, ownership="I", shares=9e9),
                       line(accession="b", sk=4, price=None)])
    counts = {}
    out = F.qualifying_filings(data, counts)
    assert set(out) == {"a"} and out["a"].value == 25000.0
    assert counts == {"ok": 2, "indirect": 1, "missing_price": 1}
    merged = F.merge_quarters([data, data])
    assert len(merged["lines"]) == 4
    bad = dict(data, subs={"a": sub("4/A")})
    with pytest.raises(ValueError):
        F.merge_quarters([data, bad])


# ------------------------------------------------------------------ timing (section 4)
def test_header_parse_and_timing_status():
    raw = b"<SEC-HEADER>\n<ACCEPTANCE-DATETIME>20110331142952\n<TYPE>4\n<FILING-DATE>20110331\n"
    h = F.parse_header(raw)
    assert h == dict(acceptance=datetime(2011, 3, 31, 14, 29, 52), form="4", filing_date=date(2011, 3, 31))
    f = filing("x", 1, 50000, datetime(2011, 3, 31, 14, 29, 52))
    assert F.timing_status(f, h, 7) == "ok"
    assert F.timing_status(f, None, 7) == "header_missing"
    assert F.timing_status(f, dict(h, acceptance=None), 7) == "acceptance_missing"
    assert F.timing_status(f, dict(h, acceptance=datetime(2011, 3, 31)), 7) == "acceptance_no_time"
    assert F.timing_status(f, dict(h, form="4/A"), 7) == "header_form_mismatch"
    assert F.timing_status(f, dict(h, filing_date=date(2011, 4, 1)), 7) == "header_date_mismatch"
    late = dict(h, acceptance=datetime(2011, 3, 20, 10))
    assert F.timing_status(f, late, 7) == "acceptance_outside_filing_date"
    after = dict(h, acceptance=datetime(2011, 4, 1, 10))
    assert F.timing_status(f, after, 7) == "acceptance_outside_filing_date"
    f.lines = [(date(2011, 4, 2), 1, 1, 1)]
    assert F.timing_status(f, h, 7) == "transaction_date_invalid"


def test_entry_is_strictly_after_acceptance():
    mon = date(2011, 3, 7)
    assert CAL.entry(datetime(2011, 3, 7, 9, 29, 59)) == mon             # before the open: that open
    assert CAL.entry(datetime(2011, 3, 7, 9, 30, 0)) == date(2011, 3, 8)  # at / after the open: next session
    assert CAL.entry(datetime(2011, 3, 7, 12, 0)) == date(2011, 3, 8)     # intraday never traded
    assert CAL.entry(datetime(2011, 3, 7, 21, 0)) == date(2011, 3, 8)
    assert CAL.entry(datetime(2011, 3, 5, 8, 0)) == mon                    # Saturday
    assert CAL.entry(datetime(2011, 3, 4, 23, 0)) == mon                   # Friday night


# ------------------------------------------------------------------ clusters (section 5)
def ev(fs, kind="cluster"):
    return F.build_events(fs, CAL, date(2011, 1, 1), date(2012, 12, 31), kind)


def test_trigger_is_the_completing_filing_never_backdated():
    a = filing("a", 1, 60000, dt(7, 11))          # Monday
    b = filing("b", 2, 60000, dt(10, 17))         # Thursday completes
    out = ev([b, a])
    assert len(out) == 1
    e = out[0]
    assert e.trigger == dt(10, 17) and e.entry == date(2011, 3, 11)
    assert e.insiders == [1, 2] and e.cluster_value == 120000.0


def test_thresholds_per_insider_and_aggregate():
    assert ev([filing("a", 1, 24999, dt(7)), filing("b", 2, 90000, dt(8))]) == []        # one insider < $25K
    assert ev([filing("a", 1, 25000, dt(7)), filing("b", 2, 74999, dt(8))]) == []        # aggregate < $100K
    assert len(ev([filing("a", 1, 25000, dt(7)), filing("b", 2, 75000, dt(8))])) == 1
    # several filings of one owner add up and count once
    fs = [filing("a", 1, 15000, dt(7)), filing("a2", 1, 15000, dt(8)), filing("b", 2, 80000, dt(9))]
    out = ev(fs)
    assert len(out) == 1 and out[0].insider_values == {1: 30000.0, 2: 80000.0}
    assert ev([filing("a", 1, 60000, dt(7)), filing("a2", 1, 60000, dt(8))]) == []        # one person, no cluster


def test_window_is_ten_calendar_days_by_acceptance():
    assert len(ev([filing("a", 1, 60000, dt(1)), filing("b", 2, 60000, dt(10, 23))])) == 1   # dates 1..10
    assert ev([filing("a", 1, 60000, dt(1)), filing("b", 2, 60000, dt(11, 8))]) == []        # 11 days


def test_cooldown_20_sessions_then_retrigger():
    fs = [filing("a", 1, 60000, dt(1, 8)), filing("b", 2, 60000, datetime(2011, 3, 1, 9, 0))]   # 09:00 -> Mar 1
    fs += [filing("c", 3, 60000, dt(14)), filing("d", 4, 60000, dt(15))]      # inside cooldown: suppressed
    later = datetime(2011, 3, 29, 8)                                           # session 20 after Mar 1 entry
    fs += [filing("e", 5, 60000, later - timedelta(days=1)), filing("f", 6, 60000, later)]
    out = ev(fs)
    assert [e.entry for e in out] == [date(2011, 3, 1), date(2011, 3, 29)]
    assert CAL.idx[out[1].entry] - CAL.idx[out[0].entry] == F.COOLDOWN_SESSIONS


def test_later_purchases_descriptive_only():
    fs = [filing("a", 1, 60000, dt(7)), filing("b", 2, 60000, dt(8)), filing("c", 3, 900000, dt(9))]
    e = ev(fs)[0]
    assert e.insiders == [1, 2] and e.cluster_value == 120000.0 and e.later == ["c"]


def test_no_future_leakage_prefix_invariance():
    """Events triggered before time T are identical whatever filings arrive after T."""
    base = [filing("a", 1, 60000, dt(1)), filing("b", 2, 60000, dt(2)),
            filing("c", 3, 30000, datetime(2011, 4, 20, 12)), filing("d", 4, 80000, datetime(2011, 4, 22, 12))]
    extra = base + [filing("z", 9, 5e6, datetime(2011, 4, 26, 12)), filing("y", 8, 5e6, datetime(2011, 4, 27, 8))]
    cut = datetime(2011, 4, 25)
    a = [(e.trigger, e.entry, e.insiders, e.cluster_value) for e in ev(base) if e.trigger <= cut]
    b = [(e.trigger, e.entry, e.insiders, e.cluster_value) for e in ev(extra) if e.trigger <= cut]
    assert a == b and len(a) == 2


def test_brute_force_reference_matches_on_random_histories():
    import random
    rnd = random.Random(7)
    for trial in range(60):
        fs = []
        for i in range(rnd.randint(2, 25)):
            when = datetime(2011, 1, 3, 7) + timedelta(days=rnd.randint(0, 300), hours=rnd.randint(0, 15),
                                                       minutes=rnd.randint(0, 59))
            fs.append(filing(f"{trial}-{i:03d}", rnd.randint(1, 5), rnd.choice([10000, 25000, 40000, 120000]), when))
        for kind in ("cluster", "single"):
            got = [(e.trigger, e.entry, tuple(e.insiders)) for e in ev(fs, kind)]
            assert got == F.brute_force_triggers(fs, CAL, kind)


def test_single_insider_control():
    assert len(ev([filing("a", 1, 100000, dt(7))], "single")) == 1
    assert ev([filing("a", 1, 99999, dt(7))], "single") == []
    assert ev([filing("a", 1, 100000, dt(7)), filing("b", 2, 30000, dt(6))], "single") == []   # two insiders


def test_header_candidates_superset():
    fs = {f.accession: f for f in [filing("a", 1, 30000, dt(1)), filing("b", 2, 30000, dt(17)),
                                   filing("c", 3, 30000, dt(30)), filing("d", 4, 150000, datetime(2011, 5, 2, 10))]}
    keep = F.header_candidates(fs, 17)
    assert keep == {"a", "b", "c", "d"}
    fs2 = {k: fs[k] for k in ("a", "c")}
    assert F.header_candidates(fs2, 17) == set()
