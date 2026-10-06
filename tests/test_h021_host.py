"""X989 / S022 host (strategies/X989_h021_sector/main.py) run offline against a fake QuantConnect environment with
SYNTHETIC prices: canary checks all pass, null worlds are emitted, the real mode refuses without matching pins and
publishes the primary result before the NON-GATING diagnostics."""
import json
import sys
import types
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from conftest import ROOT, load_module
TICKERS = ("XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY", "SPY")


class Sym:
    def __init__(self, v):
        self.value = v
        self.id = v

    def __repr__(self):
        return self.value


def _market():
    d = np.arange(np.datetime64("1998-12-01"), np.datetime64("2017-12-30"))
    cal = d[np.is_busday(d)].astype(np.int64)
    D, N = cal.size, len(TICKERS)
    rng = np.random.default_rng(7)
    launch = int(np.searchsorted(cal, np.datetime64("1998-12-22").astype(np.int64)))
    alive = np.ones((D, N), bool)
    alive[:launch, :9] = False
    alive[2000, 3] = False                                  # one missing XLI session (as in E988-01)
    TR = 30 * np.exp(np.cumsum(rng.normal(0.0003, 0.012, (D, N)), axis=0))
    TRO = TR * np.exp(rng.normal(0, 0.003, (D, N)))
    divs = {j: [] for j in range(N)}
    for j in range(N):
        for b in range(launch + 40, D, 63):
            divs[j].append((b, 0.004))
    xlf = int(np.searchsorted(cal, np.datetime64("2016-09-19").astype(np.int64)))
    divs[2].append((xlf, 0.188))
    RAW, RAWO = TR.copy(), TRO.copy()
    for j in range(N):
        f = np.ones(D)
        for b, q in divs[j]:
            f[b:] *= (1 - q)                                # raw prices drop at each ex-row; TR does not
        RAW[:, j] *= f / f[-1]
        RAWO[:, j] *= f / f[-1]
    ev = {j: [(b, q * RAW[b - 1, j], RAW[b - 1, j]) for b, q in divs[j]] for j in range(N)}
    return dict(cal=cal, alive=alive, RAW=RAW, RAWO=RAWO, ADJ=TR * 0.37, divs=ev, xlf=xlf)


def _ts(days):
    return pd.to_datetime(days.astype("datetime64[D]")) + pd.Timedelta(days=1)


def _host(monkeypatch, M, mode, params=None, sid="X989"):
    ai = types.ModuleType("AlgorithmImports")
    ai.Resolution = types.SimpleNamespace(DAILY="daily")
    ai.DataNormalizationMode = types.SimpleNamespace(RAW="raw", SCALED_RAW="scaled", ADJUSTED="adjusted")
    ai.SecurityType = types.SimpleNamespace(EQUITY="equity")
    ai.Market = types.SimpleNamespace(USA="usa")
    syms = {t: Sym(t) for t in TICKERS}
    ai.Symbol = types.SimpleNamespace(create=lambda t, *a: syms[t])

    class Split:
        pass

    class Dividend:
        pass
    ai.Split, ai.Dividend = Split, Dividend
    monkeypatch.setitem(sys.modules, "AlgorithmImports", ai)
    hm = types.ModuleType("qr_harness")
    cal = M["cal"]

    def rng_rows(d0, d1):
        a = np.datetime64(d0.strftime("%Y-%m-%d")).astype(np.int64)
        b = np.datetime64(d1.strftime("%Y-%m-%d")).astype(np.int64)
        return (cal >= a) & (cal <= b)

    class QRAlgorithm:
        def __init__(self):
            self.qr_params = dict(mode=mode, **(params or {}))
            self.qr = {"end": "2017-12-31"}
            self.msgs = []
            self._qr_log_budget = 0

        def _qr_log(self, line):
            self.msgs.append(line)

        def history(self, what, *a, **kw):
            if what is Split:
                return pd.DataFrame()
            if what is Dividend:
                s, d0, d1 = a[0][0], a[1], a[2]
                j = TICKERS.index(s.value)
                sel = rng_rows(d0, d1)
                rows = [(cal[b], amt, ref) for b, amt, ref in M["divs"][j] if sel[b]]
                if not rows:
                    return pd.DataFrame()
                ix = pd.MultiIndex.from_arrays([[s] * len(rows), [pd.Timestamp(np.datetime64(int(r[0]), "D"))
                                                                  for r in rows]])
                return pd.DataFrame({"distribution": [r[1] for r in rows], "referenceprice": [r[2] for r in rows]},
                                    index=ix)
            s, d0, d1 = what[0], a[0], a[1]
            j = TICKERS.index(s.value)
            mode_ = kw["data_normalization_mode"]
            ok = M["alive"][:, j] & rng_rows(d0, d1 - pd.Timedelta(days=1))   # bars end at midnight after the session
            c = {"raw": M["RAW"], "scaled": M["RAW"], "adjusted": M["ADJ"]}[mode_][ok, j]
            o = {"raw": M["RAWO"], "scaled": M["RAWO"], "adjusted": M["ADJ"]}[mode_][ok, j]
            ix = pd.MultiIndex.from_arrays([[s] * int(ok.sum()), _ts(cal[ok])])
            return pd.DataFrame({"close": c, "open": o}, index=ix)

    hm.QRAlgorithm = QRAlgorithm
    monkeypatch.setitem(sys.modules, "qr_harness", hm)
    path = ROOT / ("strategies/X989_h021_sector/main.py" if sid == "X989" else "strategies/S022_h021_sector/main.py")
    mod = load_module(path, f"h021_{sid}_{mode}")
    a = mod.H021Sector()
    a.qr_initialize()
    return a


@pytest.fixture(scope="module")
def M():
    return _market()


def _msg(a, tag):
    return [m for m in a.msgs if m.startswith(tag)]


def test_canary_passes_on_synthetic_market(monkeypatch, M):
    a = _host(monkeypatch, M, "canary")
    a.qr_on_end()
    k = json.loads(_msg(a, "K|")[0][2:])
    assert k["all_ok"], {x: v for x, v in k.items() if x.endswith("_ok") or x == "all_ok"}
    assert k["decisions"] == 215 and k["decision_first_last"] == ["2000-01-31", "2017-11-30"]
    assert k["xlf_large_distributions"][0]["day"] == "2016-09-19"
    assert k["missing_sessions"]["XLI"] == 1
    assert not any(m.startswith(("R|", "N|")) for m in a.msgs)         # no real IC from the canary
    assert "ic_mean" not in _msg(a, "K|")[0].split('"placebo"')[0]


def test_null_and_real_modes(monkeypatch, M):
    c = _host(monkeypatch, M, "canary")
    c.qr_on_end()
    k = json.loads(_msg(c, "K|")[0][2:])
    n = _host(monkeypatch, M, "null", dict(seeds=[1, 3]), sid="S022")
    n.qr_on_end()
    lines = _msg(n, "N|")
    assert [int(x.split("|")[1]) for x in lines] == [1, 2, 3]
    summ = json.loads(_msg(n, "QRX989|summary|")[0].split("|", 2)[2])
    assert summ["panel"]["panel_sha256"] == k["panel_sha256"]
    pins = dict(threshold_c=2.5, threshold_commit="x", null_result_sha256="y", spec_sha256="z",
                panel_sha256=k["panel_sha256"], diag_sha256="wrong")
    bad = _host(monkeypatch, M, "real", pins, sid="S022")
    with pytest.raises(Exception, match="panel differs"):
        bad.qr_on_end()
    pins["diag_sha256"] = k["diag_sha256"]
    r = _host(monkeypatch, M, "real", pins, sid="S022")
    r.qr_on_end()
    tags = [m.split("|")[0] for m in r.msgs]
    assert tags[:3] == ["R", "RS", "RD"]
    res = json.loads(_msg(r, "R|")[0][2:])
    assert set(res["gates"]) == {"P1_statistical", "P2_economic", "P3_monotonic", "P4_stable", "qualified"}
    assert res["summary"]["dates"] == 215
    d = json.loads(_msg(r, "RD|")[0][3:])
    assert d["label"] == "NON-GATING DIAGNOSTIC" and d["D1_2010_2017"]["dates"] == 95
    assert d["D2_2005_2017"]["dates"] == 155 and d["D3_3m"]["dates"] == 213 and d["D4_6m"]["dates"] == 210


def test_real_mode_needs_pins(monkeypatch, M):
    with pytest.raises(Exception, match="provenance"):
        _host(monkeypatch, M, "real", dict(threshold_c=2.5))


def test_s022_is_a_byte_copy():
    assert (ROOT / "strategies/X989_h021_sector/main.py").read_bytes() == \
        (ROOT / "strategies/S022_h021_sector/main.py").read_bytes()
