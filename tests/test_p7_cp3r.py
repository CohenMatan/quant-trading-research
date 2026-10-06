"""P7-CP3R (owner D173): the store-wide company revenue baseline is point-in-time safe, and the provisional mechanics
planner follows the owner's rules.
A future-filing invariance, B truncation, C eligibility independence (ledger level; host level in test_p7_export),
D same-company continuity (security life / SEC registrant), E determinism."""
from datetime import date, timedelta

from qr_fundamentals import PITStore

import qr_p7_export as E
import qr_p7_mech as M


def _month_end(y, m):
    return date(y + m // 12, m % 12 + 1, 1) - timedelta(days=1)


def _quarters(n=24, start=date(2008, 3, 31)):
    out, y, m = [], start.year, start.month
    while len(out) < n:
        nm = m + 3
        ny = y + (nm - 1) // 12
        nm = (nm - 1) % 12 + 1
        out.append(_month_end(y, m))
        y, m = ny, nm
    return out


def _stream(store, key, until, amend=None):
    """Feed a quarterly filer day by day up to `until` (inclusive): revenue_q = 100 + i, filed 35 days after the
    period end; interim records carry the latest fiscal-year total (vendor convention). `amend` = (period index,
    filed date, new quarterly value): a later restatement of an old quarter."""
    qs = _quarters()
    fy = {}
    for i, pe in enumerate(qs):
        fy.setdefault(pe.year, 0.0)
        fy[pe.year] += 100.0 + i
    seen_fy = None
    events = []
    for i, pe in enumerate(qs):
        if pe.month == 12:
            seen_fy = fy[pe.year]
        events.append((pe + timedelta(days=35), pe, {"revenue_q": 100.0 + i, "revenue_ttm": seen_fy}))
    if amend:
        i, fd, v = amend
        pe = qs[i]
        events.append((fd, pe, {"revenue_q": v, "revenue_ttm": seen_fy}))
    for fd, pe, vals in sorted(events, key=lambda e: e[0]):
        if fd <= until:
            store.observe(key, pe, fd, vals, None, fd)


def _ledger(until, amend=None, reviews=(date(2011, 1, 31), date(2012, 1, 31))):
    store = PITStore()
    _stream(store, "A", until, amend)
    led = E.RevenueLedger()
    for t in reviews:
        if t <= until:
            led.record((t.year, t.month), t, t + timedelta(days=1), store, ["A"])
    return led, store


def test_A_future_filing_cannot_change_a_recorded_baseline():
    # live run: the ledger is recorded at each review as the stream arrives; a restatement of an old quarter is filed
    # in 2011-06, after the 2011-01 review
    store = PITStore()
    led = E.RevenueLedger()
    amend = (9, date(2011, 6, 15), 999.0)
    for t in (date(2011, 1, 31), date(2012, 1, 31)):
        _stream(store, "A", t, amend)                                   # (observe is idempotent per report)
        led.record((t.year, t.month), t, t + timedelta(days=1), store, ["A"])
    v_live = led.v[(2011, 1)]["A"][0]
    clean, _ = _ledger(date(2011, 2, 1))                                # nothing after the review exists
    assert v_live == clean.v[(2011, 1)]["A"][0]
    # the 2012-01 review uses exactly the value recorded in 2011-01, not a recomputation after the restatement
    assert led.baseline((2012, 1), "A")[0] == v_live
    # a recomputation after the restatement would NOT reproduce it (why the ledger is recorded live)
    assert store.ttm("A", "revenue", date(2011, 2, 1)) != v_live


def test_B_truncated_store_reproduces_the_baseline():
    full, _ = _ledger(date(2012, 3, 1))
    trunc, _ = _ledger(date(2011, 2, 1))
    assert full.v[(2011, 1)]["A"] == trunc.v[(2011, 1)]["A"]
    _, pe, fd = full.v[(2011, 1)]["A"]
    sel = date(2011, 2, 1).toordinal()
    assert all(x < sel for x in fd) and all(x <= date(2011, 1, 31).toordinal() for x in pe)


def test_C_ledger_records_every_store_company_regardless_of_eligibility():
    store = PITStore()
    _stream(store, "A", date(2011, 2, 1))
    _stream(store, "B", date(2011, 2, 1))
    led = E.RevenueLedger()
    led.record((2011, 1), date(2011, 1, 31), date(2011, 2, 1), store, ["A", "B"])
    assert set(led.v[(2011, 1)]) == {"A", "B"}
    assert led.v[(2011, 1)]["A"][0] == led.v[(2011, 1)]["B"][0]


def test_D_same_company_continuity():
    assert E.baseline_check(100, 120, "1", "1") == (True, "")
    assert E.baseline_check(130, 120, "1", "1") == (False, "life")          # life began after the baseline review
    assert E.baseline_check(None, 120, "1", "1") == (False, "life")
    assert E.baseline_check(100, 120, "1", "2") == (False, "cik")           # registrant changed
    assert E.baseline_check(100, 120, None, "2") == (True, "")              # unknown at one date: no evidence


def test_E_determinism():
    a, _ = _ledger(date(2012, 3, 1))
    b, _ = _ledger(date(2012, 3, 1))
    assert a.v == b.v and a.day == b.day


def test_stale_or_missing_baseline_is_not_searched_elsewhere():
    led, _ = _ledger(date(2012, 3, 1), reviews=(date(2012, 1, 31),))
    assert led.baseline((2012, 1), "A")[0] is None                          # no 2011-01 record: no other date used


# ----------------------------------------------------------------------------------------------- planner
def _r(total, f=20, t=20, elig=True):
    return dict(total=total, fund=f, tech=t, eligible=elig, dq=[] if elig else ["H6_broken_long_term_trend"])


def test_tie_break_total_fund_tech_adv_id():
    recs = {"A": _r(82, 30, 37), "B": _r(82, 35, 32), "C": _r(82, 35, 32), "D": _r(85, 10, 40)}
    adv = {"A": 9e9, "B": 1e7, "C": 2e7, "D": 1}
    p = M.plan(set(), recs, adv, {}, {}, 80, 70, 5, 10, 10)
    assert p["buy"] == ["D", "C", "B", "A"]


def test_sector_cap_skips_and_takes_next():
    recs = {k: _r(90 - i) for i, k in enumerate("ABCDE")}
    sec = dict(A="Tech", B="Tech", C="Tech", D="Tech", E="Hlth")
    p = M.plan(set(), recs, {}, sec, {}, 80, 70, 5, 10, 10)
    assert p["buy"] == ["A", "B", "C", "E"] and p["skipped_sector"] == ["D"]


def test_no_ladder_and_cash_allowed():
    recs = {"A": _r(81), "B": _r(79), "C": _r(75)}
    p = M.plan(set(), recs, {}, {}, {}, 80, 70, 5, 10, 10)
    assert p["buy"] == ["A"]


def test_regime_limit_exits_lowest_ranked_at_review():
    hold = {"A", "B", "C"}
    recs = {"A": _r(88), "B": _r(75), "C": _r(75, f=30)}
    p = M.plan(hold, recs, {}, {}, {}, 80, 70, 5, 10, 2)
    assert p["sell"] == ["B"] and p["reasons"]["B"] == "regime position limit"


def test_company_already_held_is_skipped():
    hold = {"GOOG"}
    recs = {"GOOG": _r(82), "GOOGL": _r(90), "X": _r(85)}
    p = M.plan(hold, recs, {}, {}, {"GOOG": "c1", "GOOGL": "c1"}, 80, 70, 5, 10, 10)
    assert p["buy"] == ["X"] and p["skipped_company"] == ["GOOGL"] and p["sell"] == []


def test_replacement_buffer_and_frozen():
    hold = {"A", "B"}
    recs = {"A": _r(78), "B": _r(84), "C": _r(82), "D": _r(83)}
    p = M.plan(hold, recs, {}, {}, {}, 80, 70, 5, 2, 2)
    assert p["buy"] == ["D"] and p["sell"] == ["A"]                         # 83 >= 78 + 5; 82 then fails vs 82
    p2 = M.plan(hold, recs, {}, {}, {}, 80, 70, 5, 2, 2, frozen={"A"})
    assert p2["buy"] == [] and p2["sell"] == []


def test_committed_cp3r_outputs():
    """E993-02 isolates the revenue-baseline change: same universe and share classes as E993-01, the CP3 rule
    reproduces E993-01's H2 exactly, regime identical, every rescued baseline usable before its baseline day (in-host,
    all rows) and on the SEC sample; no return-like field."""
    import json

    from conftest import ROOT
    c = json.loads((ROOT / "research/phase7/P7_CP3R_compare.json").read_text())
    assert c["consistency"] == dict(same_eligible_universe_every_review=True, share_class_choice_differences=0,
                                    cp3_rule_h2_mismatches=0)
    assert c["regime"]["identical"] and c["rescued"]["host"]["pit_violations"] == 0
    assert c["rescued"]["total"]["rescued"] > 0 and c["rescued"]["host"]["lost"] == 0
    sec = json.loads((ROOT / "research/phase7/P7_CP3R_sec_check.json").read_text())
    assert sec["V2_violations"] == 0 and sec["not_found"] == 0 and sec["samples"] == 40
    m = json.loads((ROOT / "research/phase7/P7_CP3R_mechanics.json").read_text())
    txt = json.dumps(m).lower() + json.dumps(c).lower()
    for bad in ("return", "cagr", "sharpe", "alpha", "drawdown", "forward", "profit_factor", "win_rate"):
        assert bad not in txt, bad
    r = json.loads((ROOT / "experiments/E993-02/result.json").read_text())
    assert r["harness_summary"]["orders"] == 0
