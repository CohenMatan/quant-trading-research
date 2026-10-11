"""H026 host S028 (owner D206) on the fake QuantConnect environment EXTENDED to 2021 (SYNTHETIC prices, fundamentals
and SEC reference): canary (no real portfolio result), null worlds = qr_h026.run_world on the host's own months,
real mode output = the gates on the same months, refusals on unpinned / different digests, upload rules."""
import inspect
import json
import shutil
import sys
import types
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

import qr_h026 as H
import qr_p7_export as E
import test_p7_export as TE
import test_p7_hosts as TH
from conftest import ROOT
from test_data_v2 import dn, g4

S028 = "strategies/S028_h026_learned_score/main.py"
X801 = "strategies/X801_data_v21_export/main.py"
END = "2021-12-31"
_CACHE = {}


def _market21(n=34):
    src = inspect.getsource(TH._market).replace('np.datetime64("2017-12-30")', 'np.datetime64("2022-01-01")')
    ns = dict(vars(TH))
    exec(src, ns)
    M = ns["_market"](n)
    for j, b, f in ((20, 1310, 0.5), (21, 1460, 1 / 3), (22, 1625, 2.0), (23, 1790, 0.5), (24, 1955, 0.5),
                    (25, 2110, 0.5)):
        for k in ("RAW", "O", "H", "L"):
            M[k][b:, j] *= f
        M["splits"][j] = [(b, f)]
        M["SC"][:, j] = M["RAW"][:, j]
        M["SC"][:b, j] *= f
        m = np.where(np.arange(M["cal"].size) < b, f, 1.0)
        for e, amt, ref in M["divs"][j]:
            m[:e] *= 1 - amt / ref
        M["ADJ"][:, j] = M["RAW"][:, j] * m
    for j, b in ((26, 1322), (27, 1488), (28, 1650), (29, 1811), (30, 1977)):
        M["alive"][b:, j] = False
        M["divs"][j] = [e for e in M["divs"][j] if e[0] < b - 40]
    return M


def _table21():
    from test_p7_export import CIK, SIC
    pes = [date(y, mo, d) for y in range(2008, 2022) for mo, d in ((3, 31), (6, 30), (9, 30), (12, 31))]
    f = {}
    for j in range(34):
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
    sic = {f"S{j:02d}": [[dn(date(2008, 1, 2)), SIC.get(f"S{j:02d}", 3570), CIK.get(f"S{j:02d}", f"c{j}")]]
           for j in range(34) if f"S{j:02d}" != "S06"}
    sic["S11"] = [[dn(date(2010, 6, 1)), 3570, "c11"]]
    revs = ["2011-01-31", "2013-06-28"]
    import hashlib
    lost = {"2011-01-31": ["S99"], "2013-06-28": ["S99"]}
    return dict(version="data_v2.1", end=END, sec_v1=dict(keys=[], forms=[], corrections={}, sic_history=sic), f=f,
                ext={"S11": [dn(date(2008, 7, 1)), "c11"]}, guard={}, idv={},
                diag=dict(old=dict(reviews=revs, bits={"S00": "3", "S01": "3", "S99": "3"}), tgt=["S99"],
                          tgt_sha256=hashlib.sha256(json.dumps([["S99"], lost], sort_keys=True).encode()).hexdigest(),
                          id_reject=["S10"], id_none=["S06"]))


def _fund21():
    src = inspect.getsource(TH._fund).replace("while len(pes) < 45:", "while len(pes) < 64:")
    ns = dict(vars(TH))
    exec(src, ns)
    return ns["_fund"]


def _run(monkeypatch, tmp_path, mode, **params):
    key = (mode, json.dumps(params, sort_keys=True))
    if key not in _CACHE:
        mod = types.ModuleType("qr_data_v21")
        mod.load_table = _table21
        monkeypatch.setitem(sys.modules, "qr_data_v21", mod)
        d = tmp_path / "lean"
        d.mkdir(exist_ok=True)
        shutil.copy(ROOT / X801, d / "qr_x801.py")
        monkeypatch.syspath_prepend(str(d))
        monkeypatch.delitem(sys.modules, "qr_x801", raising=False)
        monkeypatch.setattr(TE, "_fund", _fund21())
        import qr_fundamentals as F
        monkeypatch.setattr(F, "available_from", F.available_from)
        monkeypatch.setattr(F, "is_estimated_file_date", F.is_estimated_file_date)

        def mutate(f, nd):
            f.security_reference = types.SimpleNamespace(security_type="ST00000001", is_depositary_receipt=False,
                                                         is_primary_share=True)
            f.company_reference.country_id = "USA"
        base = dict(spec_sha256="spec", h026_code_sha256="code", data_v21_manifest_sha256="manifest")
        a = TE._host(monkeypatch, _market21(), path=S028, cls="H026Learned", params=dict(base, mode=mode, **params),
                     end=END, mutate=mutate, sec_off=True)
        hist = a.history

        def history(what, *x, **kw):
            if what is a.spy:
                df = hist(what, *x, **kw)
                return df.assign(open=df["close"] * 0.998)
            return hist(what, *x, **kw)
        a.history = history
        a.qr_on_end()
        parts = sorted((m for m in a.msgs if m.startswith("QRW|")), key=lambda m: int(m.split("|")[1]))
        st = json.loads("".join(m.split("|", 2)[2] for m in parts))
        blobs = {}
        for tag in ("QRWN", "QRWR"):
            ps = sorted((m for m in a.msgs if m.startswith(tag + "|")), key=lambda m: int(m.split("|")[1]))
            if ps:
                blobs[tag] = json.loads(E.unpack("".join(m.split("|", 2)[2] for m in ps)))
        _CACHE[key] = (a, st, blobs)
    return _CACHE[key]


def test_canary_on_synthetic_market(monkeypatch, tmp_path):
    a, st, blobs = _run(monkeypatch, tmp_path, "canary")
    ck = st["canary"]
    assert not blobs and ck["real_portfolio_computed"] is False
    assert st["coverage"]["decisions"] == 131 and st["coverage"]["first"] == "2011-01-31"
    assert st["coverage"]["last"] == "2021-11-30"
    assert ck["feature_recomputation"]["checked"] > 50 and ck["feature_recomputation"]["mismatch"] == 0
    assert ck["label_purge"]["violations"] == 0 and ck["label_purge"]["checked"] == 9
    assert ck["timing"]["exit_row_mismatch"] == 0 and ck["timing"]["entry_not_after_review"] == 0
    syn = ck["synthetic"]
    assert syn["planted"]["S_WEALTH"] > syn["zero"]["S_WEALTH"]
    assert syn["planted"]["repeat_identical"] and syn["zero"]["repeat_identical"]
    assert st["pit_audit"] and all(v == 0 for v in st["pit_audit"].values())
    rep = st["reproduction"]
    assert rep["decisions"] == 83 and len(rep["per_decision"]) == 83
    assert all(a >= b >= c >= 0 for _d, a, b, c in rep["per_decision"])
    assert sum(r[3] for r in rep["per_decision"]) == rep["h024_population_rows"]


def test_null_and_real_modes(monkeypatch, tmp_path):
    _, st0, _ = _run(monkeypatch, tmp_path, "canary")
    fp = st0["feature_panel_sha256"]
    a, st, blobs = _run(monkeypatch, tmp_path, "null", feature_panel_sha256=fp, seeds=[1, 3])
    W = blobs["QRWN"]["worlds"]
    assert [w[0] for w in W] == [1, 2, 3] and st["null"]["nonfinite"] == 0
    c = H.critical_value([w[1] for w in W])
    real = dict(feature_panel_sha256=fp, c_wealth=c, null_result_sha256="n", threshold_commit="t",
                response_panel_sha256=st["response_panel_sha256"])
    a3, st3, b3 = _run(monkeypatch, tmp_path, "real", **real)
    out = b3["QRWR"]
    assert set(out["gates"]) >= {"D1", "D2", "D3", "D4", "D5", "all", "S_WEALTH"}
    assert out["gates"]["S_WEALTH"] == pytest.approx(out["rec"]["S_WEALTH"])
    assert set(out["coefficients"]) == {str(y) for y in H.OUTER_YEARS}
    assert {"capital_200k", "top10", "top20", "sector_neutral", "regime"} <= set(out["diagnostics"])
    with pytest.raises(Exception, match="feature panel differs"):
        _run(monkeypatch, tmp_path, "null", feature_panel_sha256="0" * 64, seeds=[1, 2])
    with pytest.raises(Exception, match="response panel differs"):
        _run(monkeypatch, tmp_path, "real", **dict(real, response_panel_sha256="x" * 64))


def test_runner_uploads_x801_and_h026_modules():
    from qresearch import run
    cfg = json.loads((ROOT / "experiments/E801-01/config.json").read_text())
    cfg = dict(cfg, strategy_id="S028", strategy_dir="strategies/S028_h026_learned_score")
    files = run.assemble_files(cfg, None, False)
    need = {"qr_x801.py", "qr_h026.py", "qr_h024.py", "qr_h023.py", "qr_p7_pred.py", "qr_data_v21.py", "qr_v2.py"}
    assert need <= set(files) and not any(n.startswith("qr_data_v2_") or n == "qr_data_v2.py" for n in files)
    assert len(files) <= 50 and all(len(v) <= 64000 for v in files.values())


def test_result_assessment_on_synthetic_real_output(monkeypatch, tmp_path):
    """research/phase11/cp1/P11_CP1_result.assess on the fake-market real-mode output: reproduces the host's gates,
    reports every owner metric, and labels the outcome with one of the three D206 status strings."""
    from importlib import util
    _, st0, _ = _run(monkeypatch, tmp_path, "canary")
    fp = st0["feature_panel_sha256"]
    _, stn, bn = _run(monkeypatch, tmp_path, "null", feature_panel_sha256=fp, seeds=[1, 3])
    c = H.critical_value([w[1] for w in bn["QRWN"]["worlds"]])
    pins = dict(c_wealth=c, feature_panel_sha256=fp, null_result_sha256="n", threshold_commit="t",
                response_panel_sha256=stn["response_panel_sha256"])
    _, st, b = _run(monkeypatch, tmp_path, "real", **pins)
    spec = util.spec_from_file_location("p11res", ROOT / "research/phase11/cp1/P11_CP1_result.py")
    R = util.module_from_spec(spec)
    spec.loader.exec_module(R)
    prov = dict(git_commit="x", lean_version="v", qc_backtest_id="q", code_sha256="c")
    out = R.assess(st, b["QRWR"], prov, pins)
    assert out["host_gates_reproduced"] and out["pins_ok"]
    assert out["status"] in R.STATUS.values() and out["status"] != R.STATUS["blocked"]
    assert set(out["years"]) == {str(y) for y in H.OUTER_YEARS}
    assert set(out["coefficient_stability"]["by_feature"]) == set(H.FEATURES)
    for k in ("wealth", "cagr", "vol", "sharpe", "maxdd", "underwater_share", "underwater_longest"):
        assert k in out["portfolio"]["h026"]
    bad = R.assess(st, b["QRWR"], prov, dict(pins, c_wealth=c + 1.0))
    assert bad["status"] == R.STATUS["blocked"]                    # pins differ from the run -> pipeline invalid
