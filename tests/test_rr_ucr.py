"""Narrow SEC-based universe repair UCR-1 (owner D269, UR-2 option A): the point-in-time repair module qr_ucr on
SYNTHETIC filings (only filings filed before the decision day; latest prefix; staleness; contested / ambiguous /
multi-class identities; split since the cover count; float floor; cap and identity band; vendor-capped validation),
the frozen re-audit verdict, the PIT builder's per-filing rules, the X806 host on a fake QuantConnect environment, the
offline evaluation, the runner upload rule and the X806 config rule."""
import hashlib
import json
import sys
import types
from datetime import date, datetime, timedelta

import numpy as np
import pytest

import qr_sca as A
import qr_ucr as U
from conftest import ROOT, load_module

sys.path.insert(0, str(ROOT / "research/rr/universe_repair"))


def _doc():
    p = lambda filed, pref, ok=1, sh=1e8, ce=None: [filed, pref, ok, sh, ce or filed]
    r = {
        # 1: a current single-class registrant: prefix AAA, shares 1e8, float 3e9
        "1": dict(p=[p("2010-02-01", "AAA"), p("2010-05-03", "AAA")], f=[["2010-02-01", "2009-06-30", 3e9]]),
        # 2: renamed from OLD to NEW on its 2010-05-03 filing
        "2": dict(p=[p("2010-02-01", "OLD"), p("2010-05-03", "NEW")], f=[["2010-02-01", "2009-06-30", 3e9]]),
        # 3 and 4 claim the same prefix (contested)
        "3": dict(p=[p("2010-02-01", "DUP")], f=[["2010-02-01", "2009-06-30", 3e9]]),
        "4": dict(p=[p("2010-02-01", "DUP")], f=[["2010-02-01", "2009-06-30", 3e9]]),
        # 5: float only 4e8 (below the 0.5B floor)
        "5": dict(p=[p("2010-02-01", "LOW")], f=[["2010-02-01", "2009-06-30", 4e8]]),
        # 6: latest filing not common (became an LP)
        "6": dict(p=[p("2010-02-01", "LPX", 1), p("2010-05-03", "LPX", 0)], f=[["2010-02-01", "2009-06-30", 3e9]]),
        # 7: multi-class (no single cover count)
        "7": dict(p=[p("2010-02-01", "MCL", 1, None, None)], f=[["2010-02-01", "2009-06-30", 3e9]]),
        # 8: vendor-capped validation registrant (ticker VAL)
        "8": dict(p=[p("2010-02-01", "VAL")], f=[["2010-02-01", "2009-06-30", 3e9]]),
    }
    return {"meta": {"name": "test"}, "r": r}


def _rows(**over):
    base = dict(AAA=("kA", "AAA", "N", 40.0, 0.0, None, True), NEW=("kN", "NEW", "M", 40.0, 0.0, None, True),
                OLD=("kO", "OLD", "N", 40.0, 0.0, None, True), DUP=("kD", "DUP", "N", 40.0, 0.0, None, True),
                LOW=("kL", "LOW", "N", 40.0, 0.0, None, True), LPX=("kP", "LPX", "B_blank", 40.0, 0.0, None, True),
                MCL=("kM", "MCL", "N", 40.0, 0.0, None, True), VAL=("kV", "VAL", "E", 40.0, 4e9, None, True))
    base.update(over)
    return list(base.values())


def test_pit_filing_cutoff_and_staleness():
    ref = U.RepairRef(_doc())
    i = ref.ciks.index("2")
    assert ref.current(i, U.ordinal("2010-05-03")) == ("OLD", 1)   # the 2010-05-03 filing is not usable ON that day
    assert ref.current(i, U.ordinal("2010-05-04")) == ("NEW", 1)
    assert ref.current(i, U.ordinal("2010-12-31")) is None          # 242 days after the last filing: stale
    assert ref.current(i, U.ordinal("2010-01-15")) is None          # nothing filed yet: no future identity
    j = ref.ciks.index("1")
    assert ref.shares(j, U.ordinal("2010-02-01")) is None
    assert ref.shares(j, U.ordinal("2010-02-02"))[0] == 1e8
    assert ref.float_(j, U.ordinal("2010-12-01")) == 3e9            # December year-end: still the latest float
    assert ref.float_(j, U.ordinal("2011-04-11")) == 3e9            # 650 days after the 2009-06-30 as-of date
    assert ref.float_(j, U.ordinal("2011-04-12")) is None           # > 650 days old


def test_repair_rules_and_reasons():
    rep = U.Repair(U.RepairRef(_doc()))
    t = U.ordinal("2010-06-30")
    out = rep.repair(2010, t, _rows())
    c = rep.year[2010]
    keys = {_rows()[j][0] for j in out}
    assert keys == {"kA", "kN"}                                     # AAA (N) and NEW (M, renamed) repaired
    assert out[0] == pytest.approx(4e9)
    assert c["repaired"] == 2 and c["repaired_N"] == 1 and c["repaired_M"] == 1
    assert c["contested_prefix"] == 2                               # DUP claimed by two registrants
    assert c["float_missing_or_below_0.5B"] == 1                    # LOW
    assert c["registrant_not_common_pit"] == 1                      # LPX's latest filing is not common
    assert c["no_fresh_shares"] == 1                                # MCL
    assert c["already_eligible"] == 1 and c["validation_n"] == 1 and c["validation_agree_2B"] == 1
    assert "kO" not in keys                                         # OLD is no longer the registrant's ticker


def test_repair_guards():
    rep = U.Repair(U.RepairRef(_doc()))
    t = U.ordinal("2010-06-30")
    rows = _rows(AAA=("kA", "AAA", "N", 40.0, 0.0, U.ordinal("2010-06-01"), True))   # split after cover date
    fixed = rep.repair(2010, t, rows)
    assert not any(rows[j][0] == "kA" for j in fixed)
    assert rep.year[2010]["split_since_cover"] == 1
    rep = U.Repair(U.RepairRef(_doc()))
    rows = _rows(AAA=("kA", "AAA", "N", 10.0, 0.0, None, True))                      # cap 1e9 < $2B
    rep.repair(2010, t, rows)
    assert rep.year[2010]["cap_below_2B"] == 1
    rep = U.Repair(U.RepairRef(_doc()))
    rows = _rows(AAA=("kA", "AAA", "N", 400.0, 0.0, None, True))                     # cap 4e10 / float 3e9 > 10
    rep.repair(2010, t, rows)
    assert rep.year[2010]["identity_band_fail"] == 1
    rep = U.Repair(U.RepairRef(_doc()))
    rows = _rows(AAA=("kA", "AAA", "B_explicit", 40.0, 0.0, None, True))
    rep.repair(2010, t, rows)
    assert rep.year[2010]["vendor_non_common"] == 1
    rep = U.Repair(U.RepairRef(_doc()))
    rows = _rows() + [("kA2", "AAA", "N", 40.0, 0.0, None, True)]                   # two QC securities with AAA
    rep.repair(2010, t, rows)
    assert rep.year[2010]["ambiguous_qc_ticker"] == 1
    rep = U.Repair(U.RepairRef(_doc()))
    rows = _rows(AAA=("kA", "AA.A", "N", 40.0, 0.0, None, True))                   # class share ticker
    rep.repair(2010, t, rows)
    assert rep.year[2010]["multi_class_ticker"] == 1
    rep = U.Repair(U.RepairRef(_doc()))
    rows = _rows(AAA=("kA", "AAA", "N", 40.0, 0.0, None, False))
    rep.repair(2010, t, rows)
    assert rep.year[2010]["split_factor_unknown"] == 1


def test_reaudit_verdict():
    sv = dict(horizon=24, threshold=0.005, b_C=dict(point=0.0, ci_b=[0, 0], n_unr=0),
              b_CP=dict(point=0.0, ci_b=[0.0, 0.001], n_unr=5), b_U_sec=dict(point=0.0, ci_b=[0.0, 0.002], n_unr=3))
    rep = dict(gap_C=0.001, gap_max=0.02, survivorship=sv, instrument=dict(E_cover=1.0, agree_share=1.0))
    orig = dict(instrument=dict(E_cover=0.9, agree_share=0.99))
    good = dict(validation_n=100, validation_agree_2B=97)
    assert U.reaudit_verdict(rep, orig, good, A.year_verdict)["verdict"] == "PASS"
    assert U.reaudit_verdict(rep, dict(instrument=dict(E_cover=0.7, agree_share=0.99)), good,
                             A.year_verdict)["verdict"] == "INCONCLUSIVE"        # the ORIGINAL instrument is used
    assert U.reaudit_verdict(rep, orig, dict(validation_n=100, validation_agree_2B=90),
                             A.year_verdict)["verdict"] == "INCONCLUSIVE"
    assert U.reaudit_verdict(rep, orig, dict(validation_n=10, validation_agree_2B=10),
                             A.year_verdict)["verdict"] == "INCONCLUSIVE"
    assert U.reaudit_verdict(dict(rep, gap_C=0.04), orig, good, A.year_verdict)["verdict"] == "FAIL"


def test_builder_pit_rules():
    import build_ucr_sec as B
    assert B.common_ok("APPLE INC", 3571) == 1
    assert B.common_ok("XYZ PARTNERS L.P.", 1311) == 0
    assert B.common_ok("VORNADO REALTY TRUST", 6798) == 1
    assert B.common_ok("SOME TRUST", 6799) == 0
    fl = [dict(accn="a1", filed="2012-02-01", prefix="abc", name="ABC CORP", sic=3571),
          dict(accn="a2", filed="2012-05-01", prefix="abc", name="ABC CORP", sic=3571)]
    cf = {"dei": {"EntityCommonStockSharesOutstanding": {"units": {"shares": [
              dict(accn="a1", form="10-K", val=1e8, end="2012-01-20"),
              dict(accn="a2", form="10-Q", val=1e8, end="2012-04-20"), dict(accn="a2", form="10-Q", val=5e7,
                                                                            end="2012-04-20")]}},
                  "EntityPublicFloat": {"units": {"USD": [dict(accn="a1", form="10-K", val=3e9, end="2011-06-30"),
                                                          dict(accn="a2", form="10-Q", val=3e6, end="2011-06-30")]}}},
          "us-gaap": {}}
    filings, floats, dropped = B.registrant(fl, cf)
    assert filings[0][1:] == ["ABC", 1, 1e8, "2012-01-20"]
    assert filings[1][3] is None and filings[1][4] is None          # two cover values -> multi-class / unknown
    # the a2 float (3e6) is checked against the latest EARLIER single count (a1, 1e8): $0.03 a share -> dropped
    assert floats == [["2012-02-01", "2011-06-30", 3e9]] and dropped == 1


# ------------------------------------------------------------------------------------------- X806 host (fake QC)
class _Sym:
    def __init__(self, sid, ticker):
        self.id = sid
        self.value = ticker


def _fake_host(monkeypatch, until=date(2010, 7, 31)):
    ai = types.ModuleType("AlgorithmImports")
    monkeypatch.setitem(sys.modules, "AlgorithmImports", ai)
    d = np.arange(np.datetime64("2009-05-01"), np.datetime64("2011-01-01"))
    cal = [date.fromisoformat(str(x)) for x in d[np.is_busday(d)]]
    sca_doc = {"meta": {"name": "t"}, "r": {"1": dict(t=[["AAA", "2009-01-01", "2022-01-01"]], s=[["2010-02-01", 1e8],
                                                                                                  ["2010-05-03", 1e8]],
                                                      f=[["2010-02-01", "2009-06-30", 3e9]], l="2021-11-01")}}
    ucr_doc = _doc()
    texts = {"rr/sca.json": json.dumps(sca_doc), "rr/ucr.json": json.dumps(ucr_doc)}
    sha = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in texts.items()}

    class Hours:
        def get_next_market_open(self, t, extended):
            dd = t.date()
            nxt = next(c for c in cal if c > dd or (c == dd and t.hour < 9))
            return datetime(nxt.year, nxt.month, nxt.day, 9, 30)

    class Store:
        def contains_key(self, k):
            return k in texts

        def read(self, k):
            return texts[k]

    hm = types.ModuleType("qr_harness")
    hm.EXCHANGES = ("NYS", "NAS")
    hm.COMMON_STOCK = "ST00000001"
    hm.is_us_common = lambda f, day=None: getattr(f, "common", True)
    hm.non_common_reason = lambda f, day=None: None

    class QRAlgorithm:
        def __init__(self):
            self.qr = {"start": "2009-05-01", "end": "2021-12-31", "experiment_id": "E806-01",
                       "params": {"sca_object_key": "rr/sca.json", "sca_reference_sha256": sha["rr/sca.json"],
                                  "ucr_object_key": "rr/ucr.json", "ucr_reference_sha256": sha["rr/ucr.json"]}}
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
    mod = load_module(ROOT / "strategies/X806_universe_repair_reaudit/main.py", "x806_test")
    a = mod.UniverseRepairReaudit()
    a.qr_initialize()
    # AAA: no fundamentals object (N) -> repaired from SEC (1e8 x 40 = 4e9); VAL: vendor E; GG: illiquid
    spec = {0: ("AAA", None, 40.0, 2e7), 1: ("VAL", 4e9, 40.0, 2e7), 2: ("GG", 3e9, 30.0, 1e6)}

    def fund(n):
        tk, mc, px, dv = spec[n]
        f = types.SimpleNamespace(symbol=_Sym(f"SID{n}", tk), dollar_volume=dv, price=px, split_factor=1.0,
                                  has_fundamental_data=mc is not None, market_cap=mc or 0.0,
                                  security_reference=types.SimpleNamespace(exchange_id="NYS", security_type="ST00000001",
                                                                           is_depositary_receipt=False))
        f.common = True
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


def test_x806_host_on_fake_market(monkeypatch):
    import UCR_eval as EV
    a = _fake_host(monkeypatch)
    res = EV.parse(a.msgs)
    y = res["years"]["2010"]
    assert y["original"]["E"] == 7 and y["repaired"]["E"] == 7 + y["repair"]["repaired"]
    # AAA becomes usable from 2010-02-02 (first filing filed 2010-02-01): Feb..Jul month-ends = 6 repairs
    assert y["repair"]["repaired"] == 6 and y["repair"]["repaired_N"] == 6
    assert y["original"]["confirmed"] >= 6 and y["repaired"]["confirmed"] == 0
    assert y["repaired_exits"]["repaired_stock_months"] == 6
    assert all(ln.startswith("UCR|") for ln in a.msgs)
    assert not any("SID" in ln or "AAA" in ln for ln in a.msgs)
    assert res["meta"]["ucr_reference_sha256"]


def test_upload_rule():
    from qresearch import run
    files = run.assemble_files({"strategy_dir": "strategies/X806_universe_repair_reaudit", "experiment_id": "E806-01",
                                "start": "2009-05-01", "end": "2021-12-31", "cash": 100000,
                                "universe": {}, "costs": {}, "portfolio": {}, "params": {}}, None, False)
    assert {"qr_sca.py", "qr_ucr.py", "qr_harness.py"} <= set(files)
    assert not any(n.startswith(("qr_sec_data", "qr_data_v", "qr_p7_export", "qr_ub")) for n in files)
    run.check_upload(files)


def test_pins_and_config():
    from qresearch import experiment, rr_ucr as P
    assert P.PROTOCOL_SHA256 and P.file_sha256(P.PROTOCOL) == P.PROTOCOL_SHA256
    changed = [f for f, h in P.CODE_SHA256.items() if h is None or P.file_sha256(f) != h]
    assert not changed, f"pinned UCR-1 files changed: {changed}"
    man = json.loads((ROOT / P.UCR_MANIFEST).read_text())
    assert man["sha256"] == P.UCR_REFERENCE_SHA256 and man["object_store_key"] == P.UCR_OBJECT_KEY
    from qresearch import rr_sca
    assert P.SCA_REFERENCE_SHA256 == rr_sca.SEC_REFERENCE_SHA256 and P.SCA_OBJECT_KEY == rr_sca.OBJECT_KEY
    import UCR_configs as C
    cfg = json.loads((ROOT / "experiments" / P.RUN / "config.json").read_text())
    experiment.validate(cfg)
    assert cfg == C.build(P.RUN)
    from qresearch.holdout import HoldoutLockedError
    for bad in (dict(cfg, experiment_id="E806-03"), dict(cfg, end="2022-06-30"),
                dict(cfg, params=dict(cfg["params"], ucr_reference_sha256="x")),
                dict(cfg, universe=dict(cfg["universe"], sec_corrections=True)),
                {k: v for k, v in cfg.items() if k != "owner_approval_required"}):
        with pytest.raises((experiment.ConfigError, HoldoutLockedError)):
            experiment.validate(bad)
