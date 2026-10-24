"""OD-1 (owner D308): the X808 host end to end on a fake QuantConnect environment (40 synthetic registrants with SEC
filings, two SEC-restored names, financials, a delisting, SPY clock), then the frozen offline evaluation rule."""
import hashlib
import json
import sys
import types
from datetime import date, datetime, timedelta

import numpy as np
import pytest

from conftest import ROOT, load_module

sys.path.insert(0, str(ROOT / "research/od"))
sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
N = 40


class _Sym:
    def __init__(self, sid, ticker):
        self.id = sid
        self.value = ticker


def _filings():
    out = []
    for y in range(2009, 2015):
        for m, d, form in ((3, 1, "10-K"), (5, 10, "10-Q"), (8, 10, "10-Q"), (11, 10, "10-Q")):
            f = date(y, m, d)
            if date(2009, 8, 1) <= f <= date(2014, 11, 30):
                out.append((f, form))
    return out


def _docs():
    ucr, ext, od = {}, {}, {}
    rng = np.random.default_rng(7)
    for c in range(1, N + 1):
        tk = f"C{c:02d}"
        p, s, k, q = [], [], [], []
        for f, form in _filings():
            yrs = (f - date(2009, 8, 10)).days / 365.0
            sh = 1e8 * (1 - 0.004 * c) ** yrs
            p.append([f.isoformat(), tk, 1, sh, (f - timedelta(days=5)).isoformat()])
            s.append("6022" if c in (1, 2) else ("2834" if c % 3 else "3571"))
            g = 0.05 + 0.01 * (c % 9) - 0.04
            if form == "10-K":
                k.append([f.isoformat(), date(f.year - 1, 12, 31).isoformat(), 5e8, 1e9 * (1 + g), 1e9])
                q.append([f.isoformat(), "K", date(f.year - 1, 12, 31).isoformat(), 1e9 * (1 + g), 1e9,
                          1e8 * (1 + g), 1e8, 4e8, 3.8e8, 1.5e8, 2e9, 1.9e9, 1e9, 9.5e8])
            else:
                q.append([f.isoformat(), "Q", (f - timedelta(days=40)).isoformat(), 2.5e8 * (1 + g + rng.normal(0, 0.02)),
                          2.5e8, 2.5e7, 2.4e7, 1e8, 9.8e7, None, 2e9, None, 1e9, None])
        fl = [[f.isoformat(), date(f.year - 1, 6, 30).isoformat(), 3e9] for f, form in _filings() if form == "10-K"]
        ucr[str(c)] = dict(p=p, f=fl)
        ext[str(c)] = dict(s=s, k=k)
        od[str(c)] = q
    return ({"meta": {"name": "t"}, "r": ucr}, {"meta": {"name": "t"}, "r": ext}, {"meta": {"name": "t"}, "r": od})


def _fake_host(monkeypatch, until=date(2014, 6, 30)):
    ai = types.ModuleType("AlgorithmImports")
    monkeypatch.setitem(sys.modules, "AlgorithmImports", ai)
    d = np.arange(np.datetime64("2010-01-04"), np.datetime64("2014-08-01"))
    cal = [date.fromisoformat(str(x)) for x in d[np.is_busday(d)]]
    ucr, ext, od = _docs()
    texts = {"rr/ucr.json": json.dumps(ucr), "rr/os1.json": json.dumps(ext), "rr/od1.json": json.dumps(od)}
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
            self.qr = {"start": "2010-01-04", "end": "2021-12-31", "experiment_id": "E808-01",
                       "params": {f"{n}_object_key": f"rr/{n}.json" for n in ("ucr", "os1", "od1")}}
            for n in ("ucr", "os1", "od1"):
                self.qr["params"][f"{n}_reference_sha256"] = sha[f"rr/{n}.json"]
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
    for m in ("qr_od1", "qr_os1", "qr_ucr"):
        sys.modules.pop(m, None)
    mod = load_module(ROOT / "strategies/X808_od1_outcomes/main.py", "x808_test")
    a = mod.OutcomeStudy()
    a.qr_initialize()
    a.px, a.dvx, a.mpx = a.px[:8].copy(), a.dvx[:8].copy(), a.mpx[:8].copy()       # force growth
    a.last_px, a.last_day = a.last_px[:8].copy(), a.last_day[:8].copy()
    rng = np.random.default_rng(3)
    lvl = {c: 40.0 for c in range(1, N + 1)}
    spy = 100.0
    gone = date(2013, 3, 15)                                  # C07 leaves the stream

    def fund(c, day):
        restored = c in (3, 4)
        f = types.SimpleNamespace(symbol=_Sym(f"SID{c}", f"C{c:02d}"), dollar_volume=2e7 * (1 + 0.1 * (c % 4)),
                                  price=40.0, split_factor=1.0, adjusted_price=lvl[c],
                                  has_fundamental_data=not restored, market_cap=0.0 if restored else 4e9,
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
        rm = rng.normal(0.0004, 0.01)
        spy *= np.exp(rm)
        for k in lvl:
            lvl[k] *= np.exp((0.5 + k / N) * rm + rng.normal(0.0002 * (k % 5), 0.012))
        bars = Bars(SPY=types.SimpleNamespace(close=spy, is_fill_forward=False))
        data = types.SimpleNamespace(bars=bars, dividends=Bars())
        a.time = datetime(c.year, c.month, c.day, 16, 0)
        a.on_data(data)
        nd = c + timedelta(days=1)
        a.time = datetime(nd.year, nd.month, nd.day, 0, 0)
        a._qr_select([fund(k, c) for k in lvl if not (k == 7 and c > gone)])
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


def test_x808_host_on_fake_market(host_result):
    a = host_result
    assert all(ln.startswith("OD1|") for ln in a.msgs)
    assert not any("SID" in ln or "C07" in ln for ln in a.msgs)            # no identifiers leave
    import OD1_eval as EV
    res = EV.parse(a.msgs)
    meta = res["meta"]
    assert meta["first"] == "2011-01-31" and meta["reviews"] == 42
    assert meta["checks"]["pit_violations_ext"] == 0 and meta["checks"]["pit_violations_fund"] == 0
    assert meta["checks"]["obs_without_price_row"] == 0 and meta["checks"]["identity_duplicates"] == 0
    r = res["reviews"][-1]
    assert r["elig"] == N - 1 and r["restored"] == 2 and r["fin"] == 2 and r["ident"] == N - 1
    assert r["tech_ok"] == N - 1 and r["fund_ok"] >= N - 4
    f = res["feature"]["MOM12_1"]
    assert f["tables"]["12"]["ALL"]["univ"]["n"] > 0
    assert res["feature"]["REVYOY"]["coverage"]["2012"] > 0.8
    assert res["outcomes"]["12"]["ALL"]["left"] > 0                      # the delisted name
    ev = EV.evaluate(res)
    assert "candidates" in ev and isinstance(ev["features"], dict)


def test_filed_before_2010_is_discarded(host_result):
    a = host_result
    for i in range(len(a.ref.ciks)):
        assert all(d >= date(2010, 1, 1).toordinal() for d in a.ref.p_day[i])
        assert all(d >= date(2010, 1, 1).toordinal() for d in a.fund.day[i])
