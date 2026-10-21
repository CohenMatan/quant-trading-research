"""H032 / OS-1 revised canary C-OS1 (owner D278): the X807 host on a fake QuantConnect environment (30 synthetic
registrants, a split, financials, restored names, SPY clock), the frozen canary evaluation rule C1-C10 (OS1_eval), the
runner upload rule, the X807 config rule and the pins of the frozen specification, code and SEC objects."""
import copy
import hashlib
import json
import sys
import types
from datetime import date, datetime, timedelta

import numpy as np
import pytest

from conftest import ROOT, load_module

sys.path.insert(0, str(ROOT / "research/os"))


class _Sym:
    def __init__(self, sid, ticker):
        self.id = sid
        self.value = ticker


def _filings():
    """Quarterly periodic filings 2009-08 .. 2012-11; 10-Ks on 03-01 (period end Dec 31 of the prior year)."""
    out = []
    for y in range(2009, 2013):
        for m, d, form in ((3, 1, "10-K"), (5, 10, "10-Q"), (8, 10, "10-Q"), (11, 10, "10-Q")):
            f = date(y, m, d)
            if date(2009, 8, 1) <= f <= date(2012, 11, 30):
                out.append((f, form))
    return out


def _docs():
    ucr, ext = {}, {}
    for c in range(1, 31):
        tk = f"C{c:02d}"
        p, s, k = [], [], []
        for f, form in _filings():
            yrs = (f - date(2009, 8, 10)).days / 365.0
            sh = 1e8 * (1 - 0.004 * c) ** yrs
            if c == 5 and f > date(2011, 6, 1):
                sh *= 2.0                                    # 2:1 split on 2011-06-01
            p.append([f.isoformat(), tk, 1, sh, (f - timedelta(days=5)).isoformat()])
            s.append("6022" if c in (1, 2) else "3571")
            if form == "10-K":
                ocf = -1e7 if c % 7 == 0 else 5e8
                g = -0.02 if c % 5 == 0 else 0.05
                k.append([f.isoformat(), date(f.year - 1, 12, 31).isoformat(), ocf, 1e9 * (1 + g), 1e9])
        fl = [[f.isoformat(), date(f.year - 1, 6, 30).isoformat(), 3e9] for f, form in _filings() if form == "10-K"]
        ucr[str(c)] = dict(p=p, f=fl)
        ext[str(c)] = dict(s=s, k=k)
    return {"meta": {"name": "t"}, "r": ucr}, {"meta": {"name": "t"}, "r": ext}


def _fake_host(monkeypatch, until=date(2012, 12, 31)):
    ai = types.ModuleType("AlgorithmImports")
    monkeypatch.setitem(sys.modules, "AlgorithmImports", ai)
    d = np.arange(np.datetime64("2009-05-01"), np.datetime64("2013-02-01"))
    cal = [date.fromisoformat(str(x)) for x in d[np.is_busday(d)]]
    ucr, ext = _docs()
    texts = {"rr/ucr.json": json.dumps(ucr), "rr/os1.json": json.dumps(ext)}
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
    hm.is_us_common = lambda f, day=None: True
    hm.non_common_reason = lambda f, day=None: None

    class QRAlgorithm:
        def __init__(self):
            self.qr = {"start": "2009-05-01", "end": "2021-12-31", "experiment_id": "E807-01",
                       "params": {"ucr_object_key": "rr/ucr.json", "ucr_reference_sha256": sha["rr/ucr.json"],
                                  "os1_object_key": "rr/os1.json", "os1_reference_sha256": sha["rr/os1.json"]}}
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
    mod = load_module(ROOT / "strategies/X807_os1_canary/main.py", "x807_test")
    a = mod.OS1Canary()
    a.qr_initialize()
    rng = np.random.default_rng(3)
    lvl = {c: 40.0 for c in range(1, 31)}
    spy = 100.0

    def fund(c, day):
        restored = c in (3, 4)                               # no fundamentals object -> SEC repair (1e8 x 40)
        sf = 0.5 if (c == 5 and day <= date(2011, 6, 1)) else 1.0
        f = types.SimpleNamespace(symbol=_Sym(f"SID{c}", f"C{c:02d}"), dollar_volume=2e7, price=40.0,
                                  split_factor=sf, adjusted_price=lvl[c], has_fundamental_data=not restored,
                                  market_cap=0.0 if restored else 4e9,
                                  security_reference=types.SimpleNamespace(exchange_id="NYS",
                                                                           security_type="ST00000001",
                                                                           is_depositary_receipt=False))
        return f

    class Bars(dict):
        count = 1

        def contains_key(self, k):
            return k in self

    for c in cal:
        if c > until:
            break
        rm = rng.normal(0, 0.01)
        spy *= np.exp(rm)
        for k in lvl:
            lvl[k] *= np.exp((0.5 + k / 30) * rm + rng.normal(0, 0.01))
        bars = Bars(SPY=types.SimpleNamespace(close=spy, is_fill_forward=False))
        data = types.SimpleNamespace(bars=bars, dividends=Bars())
        a.time = datetime(c.year, c.month, c.day, 16, 0)
        a.on_data(data)
        nd = c + timedelta(days=1)
        a.time = datetime(nd.year, nd.month, nd.day, 0, 0)
        a._qr_select([fund(k, c) for k in lvl])
    a.qr_on_end()
    return a


@pytest.fixture(scope="module")
def host_result():
    mp = pytest.MonkeyPatch()
    try:
        a = _fake_host(mp)
    finally:
        mp.undo()
    return a


def test_x807_host_on_fake_market(host_result):
    import OS1_eval as EV
    a = host_result
    assert all(ln.startswith("OS1|") for ln in a.msgs)
    assert not any("SID" in ln or "C07" in ln for ln in a.msgs)            # no identifiers leave
    res = EV.parse(a.msgs)
    meta = res["meta"]
    assert meta["checks"]["identity_duplicates"] == 0 and meta["checks"]["repaired_without_identity"] == 0
    assert meta["checks"]["repaired_rows"] > 0 and meta["determinism"] is True
    revs = [c for y in sorted(res["years"]) for c in res["years"][y]["reviews"]]
    assert revs[0]["t"] == "2010-01-29" and revs[-1]["t"] == "2012-12-31"
    r = revs[-1]
    assert r["elig"] == 30 and r["restored"] == 2 and r["fin"] == 2 and r["den"] == 28
    assert r["cov"] == 28 and r["passed"] == 28 - 4 - 6                  # OCF < 0 for c % 7 (4), growth < 0 for c % 5 (6)
    assert r["sizes"]["B1"] == 15 and r["sizes"]["B0"] == 15 and r["sizes"]["VB1"] == 15
    assert meta["start"] is not None and meta["start"] >= "2010-08-31"
    ev = EV.evaluate(res)
    g = ev["gates"]
    assert g["C1"]["passed"] and g["C2"]["passed"] and g["C5"]["passed"] and g["C9"]["passed"]
    assert g["C4"]["detail"]["sp_adjusted"] > 0 and g["C4"]["detail"]["sp_adjusted_in_bound"] == \
        g["C4"]["detail"]["sp_adjusted"]                                   # the 2:1 split is adjusted
    assert not g["C10"]["passed"] and g["C6"]["status"] == "UNEVALUABLE"   # a 3-year fake market: short, censored
    assert ev["outcome"] == "FAIL"
    assert ev["reported"]["years"]["2012"]["financial_removed_share"] == pytest.approx(2 / 30)


def test_eval_outcomes_on_synthetic_records(host_result):
    import OS1_eval as EV
    res = EV.parse(host_result.msgs)
    ev = EV.evaluate(res)
    # SHORT: every gate but C10 forced to pass
    r2 = copy.deepcopy(res)
    for y in r2["years"].values():
        for c in y["reviews"]:
            c["gcov2"] = dict(assessable=True, exit_den=5, exit_cov=5, stay_den=20, stay_cov=19,
                              exit_restored_den=1, exit_restored_cov=1)
            c["den_restored"], c["cov_restored"] = max(c["den_restored"], 3), max(c["cov_restored"], 3)
            if c.get("sizes"):
                c["sizes"]["MOM"] = 15
                c["pool_mom"] = 20
            c["sp_adjusted"], c["sp_adjusted_in_bound"] = 5, 5
    r2["meta"]["beta_attempted"], r2["meta"]["beta_matched"] = 100, 100
    e2 = EV.evaluate(r2)
    assert e2["failed"] == ["C10"] and e2["outcome"] == "SHORT"
    # a PIT violation fails C1
    r3 = copy.deepcopy(r2)
    r3["meta"]["checks"]["annual_filing_on_or_after_t"] = 1
    assert "C1" in EV.evaluate(r3)["failed"]
    # coverage below 65% after the start fails C5
    r4 = copy.deepcopy(r2)
    last = sorted(r4["years"])[-1]
    r4["years"][last]["reviews"][-1]["cov"] = int(0.6 * r4["years"][last]["reviews"][-1]["den"])
    assert "C5" in EV.evaluate(r4)["failed"]
    # a determinism mismatch fails C9
    r5 = copy.deepcopy(r2)
    r5["meta"]["digests_recomputed"] = dict(r5["meta"]["digests_recomputed"], B1="x")
    assert "C9" in EV.evaluate(r5)["failed"]
    assert ev["gates"]["C3"]["passed"]


def test_upload_rule():
    from qresearch import run
    files = run.assemble_files({"strategy_dir": "strategies/X807_os1_canary", "experiment_id": "E807-01",
                                "start": "2009-05-01", "end": "2021-12-31", "cash": 100000,
                                "universe": {}, "costs": {}, "portfolio": {}, "params": {}}, None, False)
    assert {"qr_os1.py", "qr_ucr.py", "qr_harness.py", "main.py"} <= set(files)
    assert not any(n.startswith(("qr_sec_data", "qr_data_v", "qr_p7_export", "qr_ub", "qr_sca")) for n in files)
    run.check_upload(files)


def test_pins_and_config():
    from qresearch import experiment, os1 as P, rr_ucr
    assert P.SPEC_SHA256 and P.file_sha256(P.SPEC) == P.SPEC_SHA256
    changed = [f for f, h in P.CODE_SHA256.items() if h is None or P.file_sha256(f) != h]
    assert not changed, f"pinned H032 files changed: {changed}"
    man = json.loads((ROOT / P.OS1_MANIFEST).read_text())
    assert man["sha256"] == P.OS1_REFERENCE_SHA256 and man["object_store_key"] == P.OS1_OBJECT_KEY
    assert man["meta"]["parent_sha256"] == rr_ucr.UCR_REFERENCE_SHA256 == P.UCR_REFERENCE_SHA256
    import OS1_configs as C
    cfg = json.loads((ROOT / "experiments" / P.RUN / "config.json").read_text())
    experiment.validate(cfg)
    assert cfg == C.build(P.RUN)
    from qresearch.holdout import HoldoutLockedError
    for bad in (dict(cfg, experiment_id="E807-03"), dict(cfg, end="2022-06-30"),
                dict(cfg, params=dict(cfg["params"], os1_reference_sha256="x")),
                dict(cfg, universe=dict(cfg["universe"], sec_corrections=True)), dict(cfg, hypothesis_id="H031"),
                {k: v for k, v in cfg.items() if k != "owner_approval_required"}):
        with pytest.raises((experiment.ConfigError, HoldoutLockedError)):
            experiment.validate(bad)
