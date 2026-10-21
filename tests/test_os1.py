"""H032 / OS-1 revised (owner D278): the pure module qr_os1 on SYNTHETIC filings — point-in-time cut-offs (a filing
dated t is never used at t), the extension object (SIC parallel to the UCR-1 filings, original annual reports with the
same-filing comparative), net share issuance with split adjustment (2:1, 1:2 reverse), the sanity bound, unknown split
factors, identity rules, filters and coverage status, ranking / buffer, turnover-matched random and beta-matched
control books, betas, quintiles, momentum, the coverage start rule and digests."""
import math

import numpy as np
import pytest

import qr_os1 as O
import qr_ucr as U

D = O.ordinal


def _p(filed, pref, ok=1, sh=1e8, ce=None):
    return [filed, pref, ok, sh, ce or filed]


def _docs():
    r = {
        # 1: AAA, cover counts a year apart (1.00e8 -> 0.95e8: 5% repurchase), annual reports with comparatives
        "1": dict(p=[_p("2011-02-20", "AAA", sh=1.00e8, ce="2011-02-15"), _p("2011-05-05", "AAA", sh=0.99e8,
                                                                              ce="2011-05-01"),
                     _p("2012-02-20", "AAA", sh=0.95e8, ce="2012-02-15")],
                  f=[["2011-02-20", "2010-06-30", 3e9]]),
        # 2: BBB, a 2:1 split between the counts (raw count doubles)
        "2": dict(p=[_p("2011-02-20", "BBB", sh=1e8, ce="2011-02-15"), _p("2012-02-20", "BBB", sh=2.1e8,
                                                                            ce="2012-02-15")],
                  f=[["2011-02-20", "2010-06-30", 3e9]]),
        # 3: a bank (SIC 6022)
        "3": dict(p=[_p("2011-02-20", "BNK", sh=1e8, ce="2011-02-15"), _p("2012-02-20", "BNK", sh=1e8,
                                                                            ce="2012-02-15")],
                  f=[["2011-02-20", "2010-06-30", 3e9]]),
        # 4, 5: contested prefix DUP
        "4": dict(p=[_p("2012-02-20", "DUP")], f=[]),
        "5": dict(p=[_p("2012-02-20", "DUP")], f=[]),
        # 6: renamed on its 2012-02-20 filing (OLD -> NEW)
        "6": dict(p=[_p("2011-11-01", "OLD"), _p("2012-02-20", "NEW")], f=[]),
    }
    k = lambda filed, pe, ocf, rev, prior: [filed, pe, ocf, rev, prior]
    e = {
        "1": dict(s=["3571", "3571", "3571"], k=[k("2011-02-20", "2010-12-31", 5e8, 9e9, 8e9),
                                                 k("2012-02-20", "2011-12-31", 6e8, 1e10, 9e9)]),
        "2": dict(s=["2834", "2834"], k=[k("2012-02-20", "2011-12-31", -1e7, 5e9, None)]),
        "3": dict(s=["6022", "6022"], k=[k("2012-02-20", "2011-12-31", 1e9, 2e9, 1.5e9)]),
        "4": dict(s=["7372"], k=[]),
        "5": dict(s=["7372"], k=[]),
        "6": dict(s=["3711", "3711"], k=[k("2012-02-20", "2012-03-31", 1e8, 1e9, 9e8)]),   # period after filing
    }
    return {"meta": {}, "r": r}, {"meta": {}, "r": e}


def _setup():
    ucr, ext = _docs()
    ref = U.RepairRef(ucr)
    return ref, O.Ext(ext, ref)


def _splits(**over):
    s = O.Splits()
    for key in ("kA", "kB", "kN", "kBNK"):
        s.observe(key, D("2010-01-04"), 1.0)
    for key, rows in over.items():
        for o, f in rows:
            s.observe(key, D(o), f)
    return s


def test_extension_must_be_parallel():
    ucr, ext = _docs()
    ext["r"]["1"]["s"] = ext["r"]["1"]["s"][:2]
    with pytest.raises(ValueError):
        O.Ext(ext, U.RepairRef(ucr))


def test_sic_point_in_time_and_financial():
    ref, ext = _setup()
    i = ref.ciks.index("3")
    assert ext.sic_at(ref, i, D("2011-02-20")) is None              # filed ON t: not usable at t
    assert ext.sic_at(ref, i, D("2011-02-21")) == "6022"
    assert O.financial("6022") and O.financial("6799") and O.financial("6000")
    assert not O.financial("5999") and not O.financial("6800") and not O.financial(None)
    assert O.ff12("3571") == "BusEq" and O.ff12("6022") == "Money" and O.ff12(None) == "Unclassified"
    assert ext.pit_violations == 0


def test_annual_inputs_cutoff_comparative_and_reasons():
    ref, ext = _setup()
    i = ref.ciks.index("1")
    assert ext.annual(i, D("2011-02-20"))[2:] == ("no_annual_report", "no_annual_report")
    ocf, g, ro, rr = ext.annual(i, D("2011-02-21"))
    assert ocf == 5e8 and g == pytest.approx(9 / 8 - 1) and ro is None and rr is None
    ocf, g, _, _ = ext.annual(i, D("2012-02-21"))                   # the newer 10-K replaces the older
    assert ocf == 6e8 and g == pytest.approx(1e10 / 9e9 - 1)
    assert ext.annual(i, D("2012-02-20"))[0] == 5e8                 # the 2012 10-K is not usable on its filing day
    # 456-day staleness from the period end: 2011-12-31 + 456 days = 2013-03-31
    assert ext.annual(i, D("2013-03-31"))[2] is None
    assert ext.annual(i, D("2013-04-01"))[2:] == ("stale", "stale")
    j = ref.ciks.index("2")
    ocf, g, ro, rr = ext.annual(j, D("2012-03-01"))
    assert ocf == -1e7 and g is None and ro is None and rr == "no_same_filing_comparative"   # no silent fallback
    m = ref.ciks.index("6")
    assert ext.annual(m, D("2012-06-01"))[2:] == ("period_not_before_filing", "period_not_before_filing")
    assert ext.pit_violations == 0


def test_annual_prior_not_positive_and_missing_values():
    ucr, e = _docs()
    e["r"]["1"]["k"][0] = ["2011-02-20", "2010-12-31", None, None, 1.0]
    e["r"]["1"]["k"][1] = ["2012-02-20", "2011-12-31", 1.0, 5.0, 0.0]
    ref = U.RepairRef(ucr)
    ext = O.Ext(e, ref)
    i = ref.ciks.index("1")
    assert ext.annual(i, D("2011-03-01"))[2:] == ("no_ocf", "no_current_revenue")
    assert ext.annual(i, D("2012-03-01"))[2:] == (None, "prior_not_positive")


def test_nsi_pairing_bound_and_cutoff():
    ref, _ = _setup()
    sp = _splits()
    i = ref.ciks.index("1")
    t = D("2012-02-21")
    os_, why, adj = O.nsi_score(ref, i, t, sp, "kA")
    days = D("2012-02-15") - D("2011-02-15")
    assert why is None and not adj
    assert os_ == pytest.approx(-math.log(0.95) * 365 / days)       # repurchase -> positive offensive score
    # on its filing day the new count is not usable: the latest is 291 days old
    assert O.nsi_score(ref, i, D("2012-02-20"), sp, "kA")[1] == "no_fresh_shares"
    assert O.nsi_score(ref, i, D("2011-06-01"), sp, "kA")[1] == "no_prior_count"     # nothing a year before
    # unknown split factor (security not yet observed)
    assert O.nsi_score(ref, i, t, O.Splits(), "kA")[1] == "split_unknown"


def test_nsi_split_adjustment_forward_and_reverse():
    ref, _ = _setup()
    i = ref.ciks.index("2")
    t = D("2012-02-21")
    # forward 2:1 split on 2011-08-01: factor 0.5 before, 1.0 after (relative to the end of the factor file)
    sp = O.Splits()
    sp.observe("kB", D("2010-01-04"), 0.5)
    sp.observe("kB", D("2011-08-02"), 1.0)
    os_, why, adj = O.nsi_score(ref, i, t, sp, "kB")
    assert why is None and adj
    assert os_ == pytest.approx(-math.log(2.1 / 2.0) * 365 / (D("2012-02-15") - D("2011-02-15")))
    # without a split record the raw doubling falls to the bound
    sp2 = _splits()
    assert O.nsi_score(ref, i, t, sp2, "kB")[1] == "bound"
    # a split recorded the wrong way (1:2 reverse) makes it worse: bound_split
    sp3 = O.Splits()
    sp3.observe("kB", D("2010-01-04"), 2.0)
    sp3.observe("kB", D("2011-08-02"), 1.0)
    assert O.nsi_score(ref, i, t, sp3, "kB")[1:] == ("bound_split", True)


def test_reverse_split_adjusted():
    ucr, e = _docs()
    ucr["r"]["2"]["p"][1][3] = 0.52e8                               # 1:2 reverse split: count halves
    ref = U.RepairRef(ucr)
    sp = O.Splits()
    sp.observe("kB", D("2010-01-04"), 2.0)
    sp.observe("kB", D("2011-08-02"), 1.0)
    os_, why, adj = O.nsi_score(ref, ref.ciks.index("2"), D("2012-02-21"), sp, "kB")
    assert why is None and adj and os_ == pytest.approx(-math.log(1.04) * 365 / 365)


def test_split_factor_timing():
    sp = O.Splits()
    sp.observe("k", D("2011-08-02"), 1.0)                           # stamp = the day after the session it reflects
    assert sp.F("k", D("2011-07-31")) is None
    assert sp.F("k", D("2011-08-01")) == 1.0                        # session 2011-08-01 known from stamp 08-02
    sp.observe("k", D("2011-08-03"), 1.0)                           # unchanged values are not re-recorded
    sp.observe("k", D("2011-09-02"), 2.0)
    assert sp.o["k"] == [D("2011-08-02"), D("2011-09-02")]
    assert sp.F("k", D("2011-08-31")) == 1.0 and sp.F("k", D("2011-09-01")) == 2.0
    sp.observe("k", D("2011-09-03"), float("nan"))
    assert sp.F("k", D("2011-09-05")) == 2.0


def test_identity_rules():
    ref, _ = _setup()
    t = D("2012-03-01")
    rows = [("kA", "AAA"), ("kB", "BBB"), ("kD", "DUP"), ("kN", "NEW"), ("kO", "OLD"), ("kX", "BNK.A")]
    out, why = O.identity(ref, t, rows)
    assert {rows[j][0]: ref.ciks[i] for j, i in out.items()} == {"kA": "1", "kB": "2", "kN": "6"}
    assert why == {"contested_prefix": 1}                           # BNK.A normalises to BNKA: no claim
    out2, why2 = O.identity(ref, t, rows + [("kB2", "BBB")])
    assert "kB" not in {rows[j][0] for j in out2} and why2["ambiguous_qc_ticker"] == 1
    out3, why3 = O.identity(ref, t, [("kC", "AAA-")])
    assert out3 == {} and why3 == {"multi_class_ticker": 1}
    assert len(set(out.values())) == len(out)                       # no registrant matched twice


def test_classify_status():
    ref, ext = _setup()
    sp = _splits()
    t = D("2012-03-01")
    a = O.classify(ref, ext, sp, t, "kA", ref.ciks.index("1"))
    assert a[1] is False and a[9] and a[10]                          # covered and passing
    b = O.classify(ref, ext, sp, t, "kB", ref.ciks.index("2"))
    assert b[1] is False and not b[9] and b[3] == "bound" and b[8] == "no_same_filing_comparative"
    f = O.classify(ref, ext, sp, t, "kBNK", ref.ciks.index("3"))
    assert f[1] is True and not f[9] and f[2] is not None           # financial: scored (B0) but outside H032
    n = O.classify(ref, ext, sp, t, "kZ", None)
    assert n[1] is None and n[3] == "no_identity" and not n[9]
    assert ext.pit_violations == 0


def test_plan_buffer_ties():
    sc = {f"k{i:02d}": (100 - i, 1.0) for i in range(40)}
    top = O.plan(sc, [])
    assert top == sorted(f"k{i:02d}" for i in range(15))
    held = ["k29", "k30", "k05"]                                     # ranks 30, 31, 6
    new = O.plan(sc, held)
    assert "k29" in new and "k30" not in new and len(new) == 15
    assert O.plan({"a": (1.0, 5.0), "b": (1.0, 9.0), "c": (1.0, 9.0)}, [], n=2) == ["b", "c"]   # ADV, then key
    assert O.plan({"x": (1.0, 1.0)}, ["gone"]) == ["x"]              # holdings no longer scored leave


def test_random_step_turnover_matched_and_deterministic():
    pool = [f"p{i:03d}" for i in range(100)]
    a = O.random_step(pool, [], 15, 7, 0)
    assert len(a) == 15 and a == O.random_step(pool, [], 15, 7, 0)
    assert a != O.random_step(pool, [], 15, 8, 0)
    b = O.random_step(pool, a, 3, 7, 1)
    assert len(b) == 15 and len(set(a) - set(b)) == 3                # replaces as many names as the scored book
    c = O.random_step([x for x in pool if x != a[0]], a, 3, 7, 1)
    assert a[0] not in c and len(set(a) - set(c)) == 3              # a forced exit counts toward the replacements
    assert len(O.random_step(pool[:5], [], 15, 1, 0)) == 5


def test_beta_step():
    quint = {f"c{i:02d}": 1 + i % 5 for i in range(50)}
    quint.update({"b1": 1, "b2": 3, "b3": None})
    quint = {k: v for k, v in quint.items() if v is not None}
    pairs, att, mat = O.beta_step({}, ["b1", "b2", "b3"], quint, 11, 0)
    assert att == 3 and mat == 2 and set(pairs) == {"b1", "b2"}
    assert quint[pairs["b1"]] == 1 and quint[pairs["b2"]] == 3
    assert O.beta_step({}, ["b1", "b2", "b3"], quint, 11, 0)[0] == pairs
    p2, att2, mat2 = O.beta_step(pairs, ["b1"], quint, 11, 1)
    assert p2 == {"b1": pairs["b1"]} and att2 == 0 and mat2 == 0     # partner left -> control left; others kept


def test_betas_and_quintiles():
    rng = np.random.default_rng(0)
    rm = rng.normal(0, 0.01, 252)
    m = 100 * np.exp(np.concatenate([[0], np.cumsum(rm)]))
    s1 = 50 * np.exp(np.concatenate([[0], np.cumsum(1.5 * rm)]))
    s2 = s1.copy()
    s2[:100] = np.nan                                               # only 152 returns: no beta
    b = O.betas(np.vstack([s1, s2]), m)
    assert b[0] == pytest.approx(1.5) and np.isnan(b[1])
    q = O.quintiles({f"k{i}": float(i) for i in range(10)})
    assert q["k0"] == 1 and q["k9"] == 5 and sorted(q.values()).count(3) == 2


def test_momentum_start_digest():
    assert O.momentum(100.0, 120.0) == pytest.approx(0.2)
    assert O.momentum(None, 1.0) is None and O.momentum(0.0, 1.0) is None and O.momentum(float("nan"), 1.0) is None
    assert O.coverage_start([0.5, None, 0.69, 0.71, 0.6]) == 3 and O.coverage_start([0.1]) is None
    d1 = O.digest([(0, ["a", "b"]), (1, ["c"])])
    assert d1 == O.digest([(0, ["a", "b"]), (1, ["c"])]) and d1 != O.digest([(0, ["a", "b"]), (1, ["d"])])
    assert O.add_months(D("2012-01-31"), 1) == D("2012-02-29") and O.add_months(D("2019-12-31"), 24) == D("2021-12-31")
