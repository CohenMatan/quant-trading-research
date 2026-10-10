"""P7-CP5d (D186): the X996 first-seen ledger host on a fake QuantConnect environment (SYNTHETIC prices, fundamentals
and SEC reference): M1 availability = first seen, M2 = max(first seen, SEC original filing + 1); timing buckets, early
cases explained by an 8-K earnings release, vintage categories (incl. a value first filed only in the future =
contamination), weekly revision detection, truncation invariance of the ledger / eligible / score digests, universe
migration reasons, aggregate-only output (no vendor value, no per-stock row); config rule and project file limit."""
import copy
import json
import types
from datetime import date, datetime, timedelta

import pytest

from conftest import ROOT
from test_p7_export import _host
from test_p7_hosts import _market

X996 = "strategies/X996_first_seen_ledger/main.py"
EPOCH = date(2000, 1, 1)


def g4(x):
    sgn = -1 if x < 0 else 1
    m, e = f"{abs(x):.3e}".split("e")
    return sgn * (int(m.replace(".", "")) * 100 + int(e))


def _pes():
    out = []
    for y in range(2008, 2020):
        out += [date(y, 3, 31), date(y, 6, 30), date(y, 9, 30), date(y, 12, 31)]
    return out


def _ref():
    """SEC reference for the fake filers: every quarter filed 40 days after its end (the fake vendor's own timing);
    c3 files 45 days after (the vendor shows it 4 days early) with an 8-K earnings release 20 days after the quarter;
    c9 has no SEC filings (unmapped); c4's 2012-06-30 revenue was first filed as 90 and restated in 2015 to the value
    the vendor shows in 2012 (a value from the future)."""
    filings, vint, events = {}, {}, {}
    pes = _pes()
    for j in range(12):
        if j == 9:
            continue
        cik = f"c{j}"
        lag = 45 if j == 3 else 40
        flat, prev, vv = [], 0, {}
        for i, pe in enumerate(pes):
            d = (pe - EPOCH).days
            flat += [d - prev, lag, 2 if pe.month == 12 else 1]
            prev = d
            row = [g4(100.0 + i), lag, None, None, g4(5000.0), lag]
            if j == 4 and pe == date(2012, 6, 30):
                row = [g4(90.0), lag, g4(100.0 + i), (date(2015, 1, 5) - pe).days - lag, g4(5000.0), lag]
            vv[str(d)] = row
        filings[cik], vint[cik] = flat, vv
    ev, prev = [], 0
    for pe in pes:
        d = (pe - EPOCH).days + 20
        ev.append(d - prev)
        prev = d
    events["c3"] = ev
    old = {"sids": ["S00", "S01", "S99"], "reviews": {"2011-01-31": [0, 1, 2], "2013-06-28": [0, 2]}}
    return dict(filings=filings, vint=vint, events=events, old=old, epoch=str(EPOCH), forms={}, vfields=[])


def _mutate(f, nd):
    """S11 revises its 2014-03-31 quarterly revenue in the stream from 2014-06-20 (a vendor revision)."""
    if f.symbol.id == "S11" and f.earning_reports.period_ending_date.three_months == datetime(2014, 3, 31) \
            and nd >= date(2014, 6, 20):
        r = f.financial_statements.income_statement.total_revenue
        f.financial_statements.income_statement.total_revenue = types.SimpleNamespace(
            three_months=r.three_months * 1.1, twelve_months=r.twelve_months)


_CACHE = {}


def _run(monkeypatch, mode, end="2017-12-31"):
    key = (mode, end)
    if key not in _CACHE:
        ref = types.ModuleType("p5d_ref")
        ref.load_table = _ref
        monkeypatch.setitem(__import__("sys").modules, "p5d_ref", ref)
        a = _host(monkeypatch, _market(), path=X996, cls="FirstSeenLedger", params=dict(mode=mode), end=end,
                  mutate=_mutate)
        a.qr_on_end()
        parts = sorted((m for m in a.msgs if m.startswith("QRP5D|")), key=lambda m: int(m.split("|")[1]))
        text = "".join(m.split("|", 2)[2] for m in parts)
        _CACHE[key] = (a, json.loads(text), text)
    return _CACHE[key]


def test_m1_first_seen_ledger_timing_vintage_and_scores(monkeypatch):
    a, st, text = _run(monkeypatch, "M1")
    assert st["calendar_check"]["match"] and st["calendar_check"]["reviews"] == 84
    assert st["slice_spot_check"]["mismatch"] == 0
    c = st["checks"]
    assert c["reports_new"] > 400 and c["censored"] >= 11 and c["unmapped_cik"] == 0 and c["fed"] >= c["reports_new"]
    assert c["revisions"] >= 1 and c["pe_after_seen"] == 0
    # the fake vendor shows each report on the first selection day after its file date: SEC delta 1-3 days, except
    # c3 (SEC filing 5 days later): early, explained by its 8-K earnings release
    tm = st["timing"]
    assert sum(v for k, v in tm.items() if k.startswith(("Q|2009-2012|", "K|2009-2012|")) and
               k.split("|")[2] in ("1", "2-5")) > 50
    early = {k: v for k, v in tm.items() if k.startswith("early|")}
    assert early and all("|earnings_8k|" in k for k in early)
    assert not any(k.endswith("|le0") and v and not k.startswith("early") and "c3" in k for k, v in tm.items())
    vt = st["vintage"]
    assert vt.get("new|revenue_q|first", 0) > 300 and vt.get("new|total_assets|first", 0) > 300
    assert vt.get("new|revenue_q|later_FUTURE") == 1 and vt.get("new|revenue_q|restated_pending|later_FUTURE") == 1
    assert vt.get("revision|revenue_q|neither", 0) >= 1
    assert st["vendor_file_date"].get("seen_minus_fd|1", 0) > 0
    # scores: synthetic filers are fully scorable once four quarters and a baseline exist
    assert sum(r[4] for r in st["per_review"]) > 300
    yr = st["per_year"]["2015"]
    assert yr["h2_nonfin"] < yr["nonfin"]
    um = st["universe_migration"]
    assert um.get("2011|old_only|not_in_feed") == 1 and um.get("2013|old_only|not_in_feed") == 1
    assert um.get("2011|both") == 2
    # aggregates only: no vendor value, no per-security row
    plain = json.dumps({k: v for k, v in st.items() if k != "digests"})      # digests are hex: checked as such
    for v in ("5000.0", "2000.0", '"S0', '"S1', "c3", "c4"):
        assert v not in plain, v
    assert all(len(h) == 64 for h in st["digests"]["review_scores"].values())
    assert st["synthetic_export_check"]["n"] == 83


def test_m2_waits_for_the_sec_filing_and_drops_unmapped_reports(monkeypatch):
    _, st1, _ = _run(monkeypatch, "M1")
    _, st2, _ = _run(monkeypatch, "M2")
    c = st2["checks"]
    assert c["m2_delayed"] > 0 and c["m2_not_fed"] > 0          # c3 early reports wait; c9 has no SEC filing
    assert st1["checks"]["m2_not_fed"] == 0
    # the ledger (what the stream showed and when) does not depend on the mode: determinism of the observation
    assert st1["digests"]["ledger_by_year"] == st2["digests"]["ledger_by_year"]
    assert st1["digests"]["eligible_by_year"] == st2["digests"]["eligible_by_year"]
    s1 = {r[0]: r for r in st1["per_review"]}
    s2 = {r[0]: r for r in st2["per_review"]}
    assert sum(r[4] for r in s2.values()) < sum(r[4] for r in s1.values())     # S09 never scorable under M2


def test_truncation_invariance(monkeypatch):
    _, full, _ = _run(monkeypatch, "M1")
    _, tr, _ = _run(monkeypatch, "M1", end="2013-12-31")
    assert tr["calendar_check"]["match"] and tr["calendar_check"]["reviews"] == 35     # 2011-01 .. 2013-11
    assert tr["digests"]["ledger_to_2013"] == full["digests"]["ledger_to_2013"]
    assert tr["digests"]["eligible_to_2013"] == full["digests"]["eligible_to_2013"]
    for t, h in tr["digests"]["review_scores"].items():
        assert full["digests"]["review_scores"][t] == h, t


def test_config_rule_and_file_limit():
    from qresearch import experiment, run
    for e in ("E996-01", "E996-02", "E996-03"):
        c = json.loads((ROOT / f"experiments/{e}/config.json").read_text())
        experiment.validate(c)
        files = run.assemble_files(c, None, False)
        assert len(files) <= 50 and all(len(v) <= 64_000 for v in files.values())
    for k, v in (("end", "2018-06-30"), ("end", "2015-12-31"), ("start", "2010-01-04"), ("params", {"mode": "M3"})):
        bad = copy.deepcopy(c)
        bad[k] = v
        with pytest.raises(experiment.ConfigError):
            experiment.validate(bad)
    bad = copy.deepcopy(c)
    bad.pop("lean_version_policy")
    with pytest.raises(experiment.ConfigError):
        experiment.validate(bad)
