"""SEC Classification Audit SCA-1 (owner D267, UR-1 option A): the pure module qr_sca on SYNTHETIC records (point-in-time
SEC reference, ticker / fingerprint matching, matched / confirmed / possible / unresolved classes, gaps, survivorship
bounds, frozen verdict rule, no identifiers in the output), the SEC builder's filters, the X805 host on a fake
QuantConnect environment, the offline evaluation, the runner upload rule and the X805 config rule."""
import json
import sys
import types
from datetime import date, datetime, timedelta

import numpy as np
import pytest

import qr_sca as A
from conftest import ROOT, load_module

sys.path.insert(0, str(ROOT / "research/rr/sec_classification"))


def _doc():
    r = {
        "1": dict(t=[["AAA", "2009-01-01", "2022-06-30"]], s=[["2009-11-01", 1e8]], f=[["2009-11-01", "2009-06-30", 3e9]],
                  l="2021-11-01"),
        "2": dict(t=[["BBB", "2009-01-01", "2012-03-31"]], s=[["2009-11-01", 1e8], ["2010-05-01", 1e8],
                                                              ["2010-11-01", 1e8], ["2011-05-01", 1e8]],
                  f=[["2009-11-01", "2009-06-30", 3e9], ["2010-11-01", "2010-06-30", 3e9]], l="2011-11-01"),
        "3": dict(t=[["CCC", "2009-01-01", "2022-06-30"]], s=[["2009-11-01", 1e8]] + [[f"{y}-0{m}-01", 1e8] for y in
                                                                                    range(2010, 2022) for m in (2, 8)],
                  f=[["2009-11-01", "2009-06-30", 1e9]], l="2021-11-01"),
        "4": dict(t=[["DDD", "2009-01-01", "2022-06-30"]], s=[[f"{y}-0{m}-01", 5e7] for y in range(2009, 2022)
                                                              for m in (2, 8)],
                  f=[["2009-08-01", "2009-06-30", 2.4e9]], l="2021-11-01"),
        "5": dict(t=[["EEE", "2009-01-01", "2022-06-30"]], s=[], f=[[f"{y}-08-01", f"{y}-06-30", 5e9]
                                                                     for y in range(2009, 2022)], l="2021-11-01"),
        "6": dict(t=[["FFF", "2009-01-01", "2022-06-30"]], s=[[f"{y}-0{m}-01", 1e8] for y in range(2009, 2022)
                                                              for m in (2, 8)], f=[], l="2021-11-01"),
        "7": dict(t=[["G.G", "2009-01-01", "2022-06-30"]], s=[[f"{y}-0{m}-01", 1e8] for y in range(2009, 2022)
                                                              for m in (2, 8)], f=[], l="2021-11-01"),
    }
    return {"meta": {"name": "test"}, "r": r}


def _points(y0=2010, y1=2013):
    out = []
    for y in range(y0, y1 + 1):
        for m in range(1, 13):
            d = date(y, m, 28)
            call = (date(y + (m == 12), m % 12 + 1, 1)).toordinal()
            out.append((y, m, call, d.toordinal()))
    return out


def _rows(day):
    """QuantConnect side at one audit day: AAA E; BBB M until 2011-12 (then gone); CCC N; ZZZ E with 5e7 x 50 vendor
    shares (fingerprint for DDD); FFF A_lt; GGG illiquid; QQQ an unmatched E name."""
    rows = [("kA", "AAA", A.CAT_E, 40.0, 4e9), ("kC", "CCC", A.CAT_N, 30.0, 0.0), ("kZ", "ZZZ", A.CAT_E, 50.0, 2.5e9),
            ("kF", "FFF", A.CAT_ALT, 25.0, 1.5e9), ("kG", "GG", A.CAT_I, 30.0, 0.0), ("kQ", "QQQ", A.CAT_E, 20.0, 3e9)]
    if day < date(2012, 1, 1).toordinal():
        rows.append(("kB", "BBB", A.CAT_M, 40.0, 0.0))
    return rows


def _run(y1=2013):
    a = A.Audit(A.SecRef(_doc()))
    for y, m, call, day in _points(2010, y1):
        for key, *_ in _rows(day):
            a.observe(key, call)
        a.audit_point(y, m, call, day, _rows(day))
    return a


def test_secref_point_in_time():
    ref = A.SecRef(_doc())
    i = ref.ciks.index("2")
    assert ref.shares_at(i, A.ordinal("2010-05-01")) == 1e8          # filed 2009-11-01 (< day), 181 days old
    assert ref.shares_at(i, A.ordinal("2009-11-01")) is None         # filed ON the day: not yet usable
    j = ref.ciks.index("1")
    assert ref.shares_at(j, A.ordinal("2010-06-30")) is None         # 241 days: stale
    assert ref.float_at(j, A.ordinal("2010-09-01")) == 3e9
    assert ref.float_at(j, A.ordinal("2011-01-01")) is None          # as-of 2009-06-30 > 456 days earlier
    assert ref.tickers_at(A.ordinal("2013-01-31"))[ref.ciks.index("7")] == {"GG"}
    assert 1 not in ref.tickers_at(A.ordinal("2013-01-31"))          # BBB evidence ended 2012-03-31


def test_evidence_rule():
    assert A.evidence(4e9, 3e9) == "strong"
    assert A.evidence(4e9, 1e9) == "weak"                            # float below $2B: lower bound only
    assert A.evidence(4e9, 3e8) == "weak"
    assert A.evidence(None, 3e9) == "weak"
    assert A.evidence(40e9, 3e9) == "weak"                           # outside the identity band
    assert A.evidence(1.5e9, 3e9) is None


def test_classes_gaps_and_verdict():
    res = _run().summarize()
    y10 = res["years"]["2010"]
    c = y10["counts"]
    # AAA matched by ticker; ZZZ matched by fingerprint (DDD); QQQ E unmatched; BBB M + strong -> confirmed (Jan..Apr
    # and Jun..Oct: shares stale in May? no: refiled every 6 months); CCC N + weak -> possible; FFF A_lt -> disagree;
    # GGG illiquid -> legit; EEE no QuantConnect ticker, float 5e9 -> unresolved
    assert y10["E"] == 36 and y10["E_matched"] == 24
    # BBB: float as-of 2009-06-30 too old in Oct 2010 (the 2010 float is filed 2010-11-01) -> weak that month
    assert y10["confirmed"] == 11 and c["confirmed_M"] == 11 and c["possible_M"] == 1
    assert y10["possible"] == 13 and c["possible_N"] == 12
    assert y10["unresolved"] == 12
    assert c["disagree_vendor_below_2B_weak"] == 12 and c["legit_illiquid_weak"] == 12
    assert y10["instrument"]["e_matched_fp"] == 12 and y10["instrument"]["agree_share"] == 1.0
    assert y10["gap_C"] == pytest.approx(y10["confirmed"] / (36 + y10["confirmed"]), abs=1e-6)
    assert y10["verdict"]["verdict"] == "FAIL"                       # confirmed gap far above 3% in this toy world
    assert res["windows"]["W1"]["outcome"] == "FAIL"
    txt = json.dumps(res)
    assert not any(s in txt for s in ("kA", "kB", "AAA", "BBB", "ZZZ"))   # no identifier or ticker leaves


def test_survivorship_uses_exits():
    res = _run().summarize()
    sv = res["years"]["2010"]["survivorship"]
    assert sv["horizon"] == 24
    assert sv["b_C"]["d"] == pytest.approx(1.0)                      # BBB exits, E never does
    assert sv["b_C"]["point"] > 0


def test_verdict_rules_pass_and_inconclusive():
    sv = dict(horizon=24, threshold=0.005, b_C=dict(point=0.0, ci_b=[0, 0], n_unr=0),
              b_CP=dict(point=0.0, ci_b=[0.0, 0.001], n_unr=5), b_U_sec=dict(point=0.0, ci_b=[0.0, 0.002], n_unr=3))
    ins = dict(E_cover=0.9, agree_share=0.99)
    rec = dict(gap_C=0.001, gap_max=0.02, survivorship=sv, instrument=ins)
    assert A.year_verdict(rec)["verdict"] == "PASS"
    assert A.year_verdict(dict(rec, gap_max=0.04))["verdict"] == "INCONCLUSIVE"
    sv2 = dict(sv, b_U_sec=dict(point=0.0, ci_b=[0.0, 0.0045], n_unr=3))
    assert A.year_verdict(dict(rec, survivorship=sv2))["verdict"] == "INCONCLUSIVE"
    assert A.year_verdict(dict(rec, instrument=dict(ins, E_cover=0.7)))["verdict"] == "INCONCLUSIVE"
    assert A.year_verdict(dict(rec, gap_C=0.031))["verdict"] == "FAIL"
    assert A.year_verdict(dict(rec, survivorship=dict(horizon=None)))["verdict"] == "PASS"
    yrs = {"2015": dict(verdict=dict(verdict="INCONCLUSIVE")), "2016": dict(verdict=dict(verdict="PASS"))}
    assert A.window_verdict(yrs, (2010, 1), (2021, 11))["outcome"] == "INCONCLUSIVE"
    assert A.window_verdict(yrs, (2016, 1), (2021, 11))["outcome"] == "PASS"


def test_builder_filters():
    import build_sca_sec as B
    assert B.norm("brk.b") == "BRKB" and B.norm("bf-a") == "BFA"
    assert B.excluded([dict(name="ABC ENERGY PARTNERS L.P.", sic=1311)]) == "non_common"
    assert B.excluded([dict(name="XYZ ACQUISITION CORP", sic=6770)]) == "non_common"
    assert B.excluded([dict(name="FOO ACQUISITION CORP", sic=7372)]) == "blank_check"
    assert B.excluded([dict(name="BIG TRUST", sic=6798)]) is None              # REIT trusts stay
    assert B.excluded([dict(name="SOME TRUST", sic=6799)]) == "investment_vehicle"
    assert B.excluded([dict(name="APPLE INC", sic=3571)]) is None


# ------------------------------------------------------------------------------------------- X805 host (fake QC)
class _Sym:
    def __init__(self, sid, ticker):
        self.id = sid
        self.value = ticker


def _fake_host(monkeypatch, until=date(2010, 6, 30)):
    ai = types.ModuleType("AlgorithmImports")
    monkeypatch.setitem(sys.modules, "AlgorithmImports", ai)
    d = np.arange(np.datetime64("2009-11-02"), np.datetime64("2011-01-01"))
    cal = [date.fromisoformat(str(x)) for x in d[np.is_busday(d)]]
    text = json.dumps(_doc(), sort_keys=True, separators=(",", ":"))
    import hashlib
    sha = hashlib.sha256(text.encode()).hexdigest()

    class Hours:
        def get_next_market_open(self, t, extended):
            dd = t.date()
            nxt = next(c for c in cal if c > dd or (c == dd and t.hour < 9))
            return datetime(nxt.year, nxt.month, nxt.day, 9, 30)

    class Store:
        def contains_key(self, k):
            return k == "rr/sca_sec_v1.json"

        def read(self, k):
            return text

    hm = types.ModuleType("qr_harness")
    hm.EXCHANGES = ("NYS", "NAS")
    hm.is_us_common = lambda f, day=None: getattr(f, "common", True)

    class QRAlgorithm:
        def __init__(self):
            self.qr = {"start": "2009-11-02", "end": "2021-12-31", "experiment_id": "E805-01",
                       "params": {"sec_object_key": "rr/sca_sec_v1.json", "sec_reference_sha256": sha}}
            self._qr_u = {"min_market_cap": 2e9, "min_price": 5.0, "min_avg_dollar_volume": 5e6, "adv_days": 20}
            self.spy = "SPY"
            self.securities = {"SPY": types.SimpleNamespace(exchange=types.SimpleNamespace(hours=Hours()))}
            self.object_store = Store()
            self.msgs = []
            self._qr_log_budget = 0

        def _qr_log(self, line):
            self.msgs.append(line)

        def on_data(self, data):
            pass
    hm.QRAlgorithm = QRAlgorithm
    monkeypatch.setitem(sys.modules, "qr_harness", hm)
    mod = load_module(ROOT / "strategies/X805_sec_classification/main.py", "x805_test")
    a = mod.SecClassificationAudit()
    a.qr_initialize()
    spec = {0: ("AAA", 4e9, True, "NYS", 40.0, 2e7), 1: ("BBB", 0.0, True, "NYS", 40.0, 2e7),
            2: ("CCC", None, True, "NYS", 30.0, 2e7), 3: ("FFF", 1.5e9, True, "NYS", 25.0, 2e7),
            4: ("GG", 3e9, True, "NYS", 30.0, 1e6), 5: ("XX", 3e9, False, "NYS", 30.0, 2e7),
            6: ("YY", 3e9, True, "OTC", 30.0, 2e7), 7: ("WW", 3e9, True, "", 30.0, 2e7)}

    def fund(n):
        tk, mc, common, ex, px, dv = spec[n]
        f = types.SimpleNamespace(symbol=_Sym(f"SID{n}", tk), dollar_volume=dv, price=px,
                                  has_fundamental_data=mc is not None, market_cap=mc or 0.0,
                                  security_reference=types.SimpleNamespace(exchange_id=ex))
        f.common = common
        return f
    data = types.SimpleNamespace(bars=types.SimpleNamespace(count=1))
    for c in cal:
        if c > until:
            break
        a.time = datetime(c.year, c.month, c.day, 16, 0)
        a.on_data(data)
        nd = c + timedelta(days=1)
        a.time = datetime(nd.year, nd.month, nd.day, 0, 0)
        a._qr_select([fund(n) for n in spec])
    a.qr_on_end()
    return a


def test_x805_host_on_fake_market(monkeypatch):
    import SCA_eval as EV
    a = _fake_host(monkeypatch)
    res = EV.parse(a.msgs)
    meta = res["meta"]
    assert meta["first_point"] == "2010-01" and meta["last_point"] == "2010-06" and meta["audit_points"] == 6
    y = res["years"]["2010"]
    c = y["counts"]
    assert c["qc_E"] == 6 and c["qc_M"] == 6 and c["qc_N"] == 6 and c["qc_A_lt"] == 6 and c["qc_I"] == 6
    assert c["qc_B"] == 12 and c["qc_X"] == 6                     # not common / blank exchange -> B; OTC -> X
    # BBB confirmed (M, strong); CCC possible (N, weak); EEE and DDD (no ticker, no fingerprint, float >= $2B) unresolved
    assert y["E_matched"] == 6 and y["confirmed"] == 6 and y["possible"] == 6 and y["unresolved"] == 12
    assert all(ln.startswith("SCA|") for ln in a.msgs)
    assert not any("SID" in ln or "AAA" in ln for ln in a.msgs)
    assert meta["sec_reference_sha256"]


def test_x805_refuses_wrong_digest(monkeypatch):
    ai = types.ModuleType("AlgorithmImports")
    monkeypatch.setitem(sys.modules, "AlgorithmImports", ai)
    hm = types.ModuleType("qr_harness")
    hm.EXCHANGES = ("NYS",)
    hm.is_us_common = lambda f, day=None: True

    class QRAlgorithm:
        def __init__(self):
            self.qr = {"start": "2009-11-02", "end": "2021-12-31",
                       "params": {"sec_object_key": "k", "sec_reference_sha256": "0" * 64}}
            self._qr_u = {"min_market_cap": 2e9, "min_price": 5.0, "min_avg_dollar_volume": 5e6, "adv_days": 20}
            self.object_store = types.SimpleNamespace(contains_key=lambda k: True, read=lambda k: "{}")
    hm.QRAlgorithm = QRAlgorithm
    monkeypatch.setitem(sys.modules, "qr_harness", hm)
    mod = load_module(ROOT / "strategies/X805_sec_classification/main.py", "x805_test2")
    with pytest.raises(Exception, match="digest"):
        mod.SecClassificationAudit().qr_initialize()


def test_upload_rule():
    from qresearch import run
    files = run.assemble_files({"strategy_dir": "strategies/X805_sec_classification", "experiment_id": "E805-01",
                                "start": "2009-11-02", "end": "2021-12-31", "cash": 100000,
                                "universe": {}, "costs": {}, "portfolio": {}, "params": {}}, None, False)
    assert "qr_sca.py" in files and "qr_harness.py" in files
    assert not any(n.startswith(("qr_sec_data", "qr_data_v", "qr_p7_export", "qr_ub")) for n in files)
    run.check_upload(files)


def test_pins_and_config():
    from qresearch import experiment, rr_sca as P
    assert P.PROTOCOL_SHA256 and P.file_sha256(P.PROTOCOL) == P.PROTOCOL_SHA256
    changed = [f for f, h in P.CODE_SHA256.items() if h is None or P.file_sha256(f) != h]
    assert not changed, f"pinned SCA-1 files changed: {changed}"
    man = json.loads((ROOT / P.SEC_MANIFEST).read_text())
    assert man["sha256"] == P.SEC_REFERENCE_SHA256 and man["object_store_key"] == P.OBJECT_KEY
    import SCA_configs as C
    cfg = json.loads((ROOT / "experiments" / P.RUN / "config.json").read_text())
    experiment.validate(cfg)
    assert cfg == C.build(P.RUN)
    assert cfg["kind"] == "infrastructure" and cfg["end"] == "2021-12-31" and not cfg["universe"].get("sec_corrections")
    from qresearch.holdout import HoldoutLockedError
    for bad in (dict(cfg, experiment_id="E805-03"), dict(cfg, end="2022-06-30"),
                dict(cfg, params=dict(cfg["params"], sec_reference_sha256="x")),
                dict(cfg, universe=dict(cfg["universe"], sec_corrections=True)),
                {k: v for k, v in cfg.items() if k != "owner_approval_required"}):
        with pytest.raises((experiment.ConfigError, HoldoutLockedError)):
            experiment.validate(bad)
