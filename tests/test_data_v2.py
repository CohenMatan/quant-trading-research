"""Data Infrastructure v2 (P7-CP5f, owner D190): the consolidated reference table, the pure v2 layer (qr_v2) and the
X998 export host on a fake QuantConnect environment (SYNTHETIC prices / fundamentals / SEC reference).
- the packed table loads, its SHA-256 matches the build record, and it holds nothing dated after 2017-12-31;
- the consolidated data-v1 SEC layer is EQUIVALENT to the data-v1 table for every repaired security up to 2017-12-31
  (usable filings, cover counts, market caps with splits, Score v1 values fed to the PIT store, SIC / CIK rows);
- M2 filing match, restatement guard, identity extension with the presence rule, data-v1 membership decoding;
- the frozen mechanics simulation obeys every rule (caps, sector limit, thresholds) and reports no price / P&L;
- the in-cloud synthetic power study is the P7-CP4 study, bit for bit, on the same inputs;
- the X998 host: PIT audit all zero, guard blocks the planted case, truncation-invariant digests, aggregate-only
  output, config rules and the project file budget."""
import copy
import hashlib
import json
import sys
import types
from datetime import date, timedelta

import numpy as np
import pytest

from conftest import ROOT
from test_p7_export import _host
from test_p7_hosts import _market

sys.path[:0] = [str(ROOT / "src/qresearch/lean")]
import qr_v2 as V  # noqa: E402

X998 = "strategies/X998_data_v2_export/main.py"
EPOCH = date(2000, 1, 1)


def dn(d):
    return (d - EPOCH).days


def test_table_loads_hash_and_window():
    import qr_data_v2
    t = qr_data_v2.load_table()
    ref = json.loads((ROOT / "research/phase7/data_v2/data_v2_reference.json").read_text())
    from qresearch import v2pack
    assert hashlib.sha256(v2pack.raw_bytes(t)).hexdigest() == ref["table_sha256"] == qr_data_v2.SHA256
    assert t["version"] == "data_v2" and t["end"] == "2017-12-31" and qr_data_v2.LOADER_VERSION == v2pack.LOADER_VERSION
    end = dn(date(2017, 12, 31))
    for c in t["sec_v1"]["corrections"].values():
        assert all(r[1] <= end for r in c["rows"])
    assert all(r[0] <= end for rows in t["sec_v1"]["sic_history"].values() for r in rows)
    for cols in t["f"].values():
        pe = np.cumsum(cols[0])
        assert pe.max() <= end and (pe + np.asarray(cols[1])).max() <= end


def test_sec_v1_layer_is_equivalent_to_data_v1():
    import qr_data_v2
    import qr_sec_data
    from qr_fundamentals import PITStore
    from qr_sec_corrections import SECCorrections
    v1 = SECCorrections(qr_sec_data.load_table())
    v2 = SECCorrections(V.sec_v1_table(qr_data_v2.load_table()["sec_v1"]))
    keys = qr_data_v2.load_table()["sec_v1"]["keys"]
    assert set(v1.filings) == set(v2.filings)
    days = [date(2009, 6, 30), date(2011, 3, 31), date(2013, 12, 31), date(2015, 8, 3), date(2017, 12, 31)]
    for sid in v1.filings:
        for d in days:
            a = [(f.filed, f.period_end, f.cover_date, f.shares, {k: f.values[k] for k in keys if k in f.values})
                 for f in v1.usable(sid, d)]
            b = [(f.filed, f.period_end, f.cover_date, f.shares, dict(f.values)) for f in v2.usable(sid, d)]
            assert a == b, (sid, d)
        for s in (v1, v2):
            s.observe_split(sid, date(2014, 6, 2), 0.5)
        for d in days:
            assert v1.market_cap(sid, d, 25.0) == v2.market_cap(sid, d, 25.0), (sid, d)
    for sid in sorted(v1.filings)[:60]:
        s1, s2 = PITStore(200), PITStore(200)
        for d in days:
            v1.feed(sid, d, s1)
            v2.feed(sid, d, s2)
            for base in ("revenue", "gross_profit", "net_income", "operating_cash_flow"):
                assert s1.ttm(sid, base, d) == s2.ttm(sid, base, d)
            r1, r2 = s1.record(sid, d), s2.record(sid, d)
            assert (r1 is None) == (r2 is None)
            if r1:
                assert all(r1.values.get(k) == r2.values.get(k) for k in keys)
    t1 = qr_sec_data.load_table()["sic_history"]
    t2 = V.sec_v1_table(qr_data_v2.load_table()["sec_v1"])["sic_history"]
    for sid, rows in t1.items():
        assert [r for r in rows if r[0] <= "2017-12-31"] == t2.get(sid, [])


def test_old_membership_decodes_to_e993_02():
    import qr_data_v2
    sys.path.insert(0, str(ROOT / "strategies/X996_first_seen_ledger"))
    from p5d_ref import load_table
    o = load_table()["old"]
    old = V.old_membership(qr_data_v2.load_table()["diag"]["old"])
    assert old == {t: {o["sids"][i] for i in ix} for t, ix in o["reviews"].items()}


def _small_table():
    pe0 = dn(date(2012, 3, 31))
    return dict(f={"7": [[pe0, 91], [40, 40], [1, 3], [5, None], [g4(1e8), None]]},
                ext={"S1": [dn(date(2008, 7, 1)), 7]},
                guard={"7": {str(pe0): [g4(90.0), g4(100.0), (date(2015, 1, 5) - date(2012, 3, 31)).days,
                                        None, None, None]}},
                idv={"7": {str(pe0): [g4(90.0), g4(5000.0)]}})


def g4(x):
    m, e = f"{abs(x):.3e}".split("e")
    return int(m.replace(".", "")) * 100 + int(e)


def test_reference_match_guard_identity_value():
    r = V.Reference(_small_table())
    m = r.match("7", date(2012, 4, 2))
    assert m[0] == dn(date(2012, 3, 31)) and m[1] == dn(date(2012, 5, 10)) and m[2] == "Q" and not m[3]
    assert r.match("7", date(2012, 4, 10)) is None                     # outside the 6-day tolerance
    assert r.match("7", date(2012, 6, 30))[3]                          # amendment-only period
    assert len(r.shrows["7"]) == 1 and r.shrows["7"][0][4] == "2012-05-05"
    blocked, cats = r.guard("7", m[0], {"revenue_q": 100.0}, date(2012, 5, 11))
    assert blocked and cats == {"revenue_q": "later_not_yet_public"}
    assert r.guard("7", m[0], {"revenue_q": 100.0}, date(2015, 1, 6)) == (False, {"revenue_q": "later_public"})
    assert r.guard("7", m[0], {"revenue_q": 90.0}, date(2012, 5, 11)) == (False, {})
    assert r.identity_value("7", m[0], {"revenue_q": 90.2, "total_assets": 6000.0}) == \
        {"revenue_q": "match", "total_assets": "differ"}


def test_identity_extension_presence_rule():
    ident = V.Identity({"S1": [(date(2010, 6, 1), "7")]}, {"S1": (date(2008, 7, 1), "7")})
    first = date(2008, 7, 1)
    assert ident.m2("S1", date(2011, 1, 3), first, first) == ("7", "v2")
    assert ident.m2("S1", date(2009, 5, 1), first, first) == ("7", "ext")
    assert ident.m2("S1", date(2009, 5, 1), date(2009, 1, 2), first) == (None, "presence_break")
    assert ident.m2("S1", date(2008, 6, 1), first, first) == (None, None)
    assert ident.m2("S2", date(2009, 5, 1), first, first) == (None, None)


def test_mechanics_simulation_obeys_the_frozen_rules():
    import qr_p7_export as E
    import qr_p7_mech as M
    import qr_p7_score as S
    rng = np.random.default_rng(3)
    sids = [f"X{i:03d}" for i in range(60)]
    reviews, weekly = [], []
    for i in range(36):
        t = date(2011 + i // 12, i % 12 + 1, 28)
        rows = {}
        for s in sids:
            tot = int(rng.integers(40, 101))
            pts = (min(15, tot // 7), 10, 5, 10, 5, 5, 5, 8)
            rows[s] = (E.BIT["H6"] if rng.random() < 0.05 else 0, tot, pts)
        reviews.append(dict(t=t, year=t.year, rows=rows, adv={s: 1e7 for s in sids},
                            ff={s: int(s[1:]) % 4 for s in sids}, company={s: s for s in sids},
                            regime=("STRONG", "NORMAL", "WEAK", "RISK_OFF")[i % 4]))
        weekly.append(dict(t=t + timedelta(days=7), review_index=i, bits={s: E.BIT["H5"] if rng.random() < 0.02 else 0
                                                                          for s in sids}, members=sids))
    out = V.simulate(reviews, weekly, E.BIT, E.eligible_flag, M.plan, S.weekly_check, M.REGIME_POSITIONS)
    assert out["rule_checks"] == dict(cap_violations=0, sector_violations=0, max_holdings_le_K=True)
    assert out["buys"] > 0 and out["weekly_dq_exits"] > 0 and set(out["sells"]) <= {
        "exit_threshold", "replacement", "regime_cap", "universe_exit", "dq_review", "dq_weekly"}
    assert out["costs"]["100000"]["commission_usd_yr"] == round(out["orders"] * 7.0 / 3.0, 2)
    txt = json.dumps(out).lower()
    for bad in ("return", "pnl", "profit", "cagr", "sharpe"):
        assert bad not in txt


def test_power_port_matches_p7_cp4_study(monkeypatch):
    sys.path.insert(0, str(ROOT / "research/phase7"))
    import P7_power as PW
    import qr_p7_pred as R
    rng = np.random.default_rng(11)
    tables = []
    for i in range(84):
        n = 40
        tables.append(dict(ids=np.array([f"Z{j:02d}" for j in range(n)]), S=rng.integers(20, 95, n),
                           sector=rng.integers(0, 12, n), risk=rng.choice([0, 3, 7, 10], n),
                           mom_pts=rng.choice([0., 5., 10., 15.], n), fund=rng.integers(0, 45, n).astype(float),
                           size=np.log(rng.integers(5000, 90000, n).astype(float)), year=2011 + i // 12,
                           regime="STRONG", tk=f"{2011 + i // 12}-{i % 12 + 1:02d}-28"))
    for mod in (PW, V):
        monkeypatch.setattr(mod, "N_DATASETS", 2)
        monkeypatch.setattr(mod, "NULL_DATASETS", 1)
        monkeypatch.setattr(mod, "HOLDOUT_DATASETS", 1)
    monkeypatch.setattr(PW, "score_tables", lambda: tables)
    a = PW.scenario(tables, 0.0055, workers=1)
    b = V.power_scenario(R, tables, 0.0055)
    a.pop("runtime_s")
    assert json.dumps(a, sort_keys=True, default=float) == json.dumps(b, sort_keys=True, default=float)


# ----------------------------------------------------------------------------------------------- the X998 host
def _fake_table():
    from test_p7_export import CIK, SIC
    pes = []
    for y in range(2008, 2018):
        pes += [date(y, 3, 31), date(y, 6, 30), date(y, 9, 30), date(y, 12, 31)]
    f, guard, idv = {}, {}, {}
    for j in range(12):
        cik = CIK.get(f"S{j:02d}", f"c{j}")
        if cik in f:
            continue
        cols, prev = [[], [], [], [], []], 0
        for pe in pes:
            d = dn(pe)
            for i, v in enumerate((d - prev, 40, 2 if pe.month == 12 else 1, 5,
                                   g4(6e7) if pe + timedelta(days=40) >= date(2010, 6, 1) else None)):
                cols[i].append(v)
            prev = d
        f[cik] = cols
    k = pes.index(date(2012, 6, 30))                    # S04's 2012-06-30 revenue: first filed 90, restated in 2015
    guard["c4"] = {str(dn(date(2012, 6, 30))): [g4(90.0), g4(100.0 + k), (date(2015, 1, 5) - date(2012, 6, 30)).days,
                                                None, None, None]}
    idv["c11"] = {str(dn(pe)): [g4(100.0 + i), g4(5000.0)] for i, pe in enumerate(pes) if pe <= date(2010, 12, 31)}
    sic = {f"S{j:02d}": [[dn(date(2008, 1, 2)), SIC.get(f"S{j:02d}", 3570), CIK.get(f"S{j:02d}", f"c{j}")]]
           for j in range(12) if f"S{j:02d}" != "S06"}
    sic["S11"] = [[dn(date(2010, 6, 1)), 3570, "c11"]]
    revs = ["2011-01-31", "2013-06-28"]
    old = dict(reviews=revs, bits={"S00": "3", "S01": "3", "S99": "3"})
    lost = {"2011-01-31": ["S99"], "2013-06-28": ["S99"]}
    return dict(version="data_v2", end="2017-12-31",
                sec_v1=dict(keys=[], forms=[], corrections={}, sic_history=sic), f=f,
                ext={"S11": [dn(date(2008, 7, 1)), "c11"]}, guard=guard, idv=idv,
                diag=dict(old=old, tgt=["S99"], tgt_sha256=hashlib.sha256(json.dumps([["S99"], lost], sort_keys=True)
                                                                          .encode()).hexdigest(),
                          id_reject=["S10"], id_none=["S06"]))


_CACHE = {}


def _run(monkeypatch, end="2017-12-31"):
    if end not in _CACHE:
        mod = types.ModuleType("qr_data_v2")
        mod.load_table = _fake_table
        monkeypatch.setitem(sys.modules, "qr_data_v2", mod)

        def mutate(f, nd):
            f.security_reference = types.SimpleNamespace(security_type="ST00000001", is_depositary_receipt=False,
                                                         is_primary_share=True)
            f.company_reference.country_id = "USA"
        a = _host(monkeypatch, _market(), path=X998, cls="DataV2Export", params=dict(mode="export"), end=end,
                  mutate=mutate, sec_off=True)
        a.qr_on_end()
        parts = sorted((m for m in a.msgs if m.startswith("QRV2|")), key=lambda m: int(m.split("|")[1]))
        _CACHE[end] = (a, json.loads("".join(m.split("|", 2)[2] for m in parts)))
    return _CACHE[end]


def test_x998_export_audit_guard_mechanics(monkeypatch):
    a, st = _run(monkeypatch)
    assert all(v == 0 for v in st["pit_audit"].values()), st["pit_audit"]
    assert st["checks"]["guard_blocked"] >= 1 and st["restatement_guard"].get("new|revenue_q|later_not_yet_public")
    assert st["target_check"]["sha256_match"]
    assert len(st["per_review"]) == 84 and st["slice_spot_check"]["mismatch"] == 0
    mech = st["mechanics"]
    assert mech["rule_checks"]["cap_violations"] == 0 and mech["rule_checks"]["sector_violations"] == 0
    assert any(k.startswith("mapped|ext|") for k in st["identity_mapping"])
    assert st["identity_sanity"]["affected_securities"] == 2
    plain = json.dumps({k: v for k, v in st.items() if k != "digests"})
    for bad in ('"S0', '"S1', '"c4', "5000.0", "pnl", "cagr", "sharpe"):
        assert bad not in plain, bad


def test_x998_truncation_invariance(monkeypatch):
    _, full = _run(monkeypatch)
    _, tr = _run(monkeypatch, end="2013-12-31")
    assert tr["digests"]["ledger_to_2013"] == full["digests"]["ledger_to_2013"]
    for k in ("review_scores", "review_eligibility"):
        shared = set(tr["digests"][k])
        assert shared and all(tr["digests"][k][t] == full["digests"][k][t] for t in shared)
    for y in ("2011", "2012"):
        assert tr["digests"]["universe_by_year"][y] == full["digests"]["universe_by_year"][y]


def test_x998_config_rule_and_file_budget():
    from qresearch import experiment, run
    for e in ("E998-01", "E998-02", "E998-03", "E998-04"):
        c = json.loads((ROOT / f"experiments/{e}/config.json").read_text())
        experiment.validate(c)
        files = run.assemble_files(c, None, False)
        assert len(files) <= 34 and all(len(v) <= 64_000 for v in files.values())
        assert "qr_sec_data.py" not in files and "qr_data_v2.py" in files and "qr_p7_mech.py" in files
    for k, v in (("end", "2018-06-30"), ("start", "2010-01-04"), ("params", {"mode": "real"})):
        bad = copy.deepcopy(c)
        bad[k] = v
        with pytest.raises(experiment.ConfigError):
            experiment.validate(bad)
    bad = copy.deepcopy(c)
    bad["universe"]["sec_corrections"] = True
    with pytest.raises(experiment.ConfigError):
        experiment.validate(bad)
    bad = json.loads((ROOT / "experiments/E998-03/config.json").read_text())
    bad["params"] = {"mode": "power"}
    with pytest.raises(experiment.ConfigError):
        experiment.validate(bad)
