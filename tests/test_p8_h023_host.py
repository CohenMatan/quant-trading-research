"""H023 host S025 (owner D199) on the fake QuantConnect environment of the H022 / Data v2 tests (SYNTHETIC prices,
fundamentals and SEC reference):
- S025 subclasses the pinned S024 (uploaded byte-identical as qr_s024) and reuses its panel unchanged (same panel
  digest as S024 on the same market); the inherited H022 canary still passes;
- the layer subtotals sum to the Score v1 total for every population row; the control score is 360 x the total;
- the canary computes no statistic of real responses; null worlds equal qr_h023.null_record and their control column
  equals the frozen H022 null world of the same seed; null / real modes refuse a different panel or subtotal digest;
- the real mode output is exactly qr_h023.evaluate on the same panel (offline recomputation);
- config rules and runner wiring (qr_s024 / qr_h023 / qr_x998 uploaded byte-identical)."""
import copy
import hashlib
import json
import shutil
import sys

import numpy as np
import pytest

import qr_h023 as G
import qr_p7_export as E
import qr_p7_pred as R
from conftest import ROOT
from qresearch import p7pred_v2, p8h023
from test_p7_export import _host
from test_p7_h022_host import _mk
from test_p7_h022_v2 import BASE as H022_BASE
from test_p7_h022_v2 import _chunks, _env, _mutate
from test_p7_h022_v2 import _run as _run24

S025 = "strategies/S025_h023_score_v2/main.py"
S024 = "strategies/S024_h022_data_v2/main.py"
BASE = dict(spec_sha256="spec", pred_code_sha256=p7pred_v2.PRED_CODE_SHA256, grid_code_sha256="grid")
_CACHE = {}


def _env25(monkeypatch, tmp_path):
    _env(monkeypatch, tmp_path)
    shutil.copy(ROOT / S024, tmp_path / "lean" / "qr_s024.py")            # as the runner uploads it
    monkeypatch.delitem(sys.modules, "qr_s024", raising=False)


def _run(monkeypatch, tmp_path, mode, **params):
    key = (mode, json.dumps(params, sort_keys=True))
    if key not in _CACHE:
        _env25(monkeypatch, tmp_path)
        a = _host(monkeypatch, _mk(), path=S025, cls="H023ScoreV2", params=dict(BASE, mode=mode, **params),
                  mutate=_mutate, sec_off=True)
        a.qr_on_end()
        _CACHE[key] = (a, json.loads(_chunks(a.msgs, "QRP7V")))
    return _CACHE[key]


def _canary(monkeypatch, tmp_path):
    return _run(monkeypatch, tmp_path, "canary")


def test_s025_imports_the_pinned_s024_and_adds_only_g_names():
    src = (ROOT / S025).read_text()
    assert "import qr_s024 as S24" in src and "class H023ScoreV2(S24.H022DataV2)" in src
    assert "import qr_x998" in src and "import qr_h023 as G" in src
    import ast
    tree = ast.parse(src)
    cls = [n for n in tree.body if isinstance(n, ast.ClassDef)][0]
    names = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}
    assert names == {"qr_initialize", "_g_attach", "_g_emit", "_canary_v2", "_null", "_real"}
    s24 = ast.parse((ROOT / S024).read_text())
    x98 = ast.parse((ROOT / "strategies/X998_data_v2_export/main.py").read_text())
    inherited = set()
    for t in (s24, x98):
        for c in [n for n in t.body if isinstance(n, ast.ClassDef)]:
            inherited |= {n.name for n in c.body if isinstance(n, ast.FunctionDef)}
    assert {"qr_initialize", "_canary_v2", "_null", "_real"} <= inherited          # overridden mode steps
    assert not ({"_g_attach", "_g_emit"} & inherited)                             # new names never reuse old ones


def test_canary_passes_and_reuses_the_h022_panel(monkeypatch, tmp_path):
    a, st = _canary(monkeypatch, tmp_path)
    _, s24 = _run24(monkeypatch, tmp_path, "canary")
    assert st["panel_sha256"] == s24["panel_sha256"]                               # S024's panel, unchanged
    assert st["data_v2_digests"] == s24["data_v2_digests"]
    ck = st["canary"]
    assert ck["real_ic_computed"] is False and ck["gates_computed"] is False
    assert not any(m.startswith(("QRN|", "QRR|", "QRH|")) for m in a.msgs)
    # the inherited H022 canary checks still pass
    tm = ck["timing"]
    assert tm["value_mismatch"] == tm["status_mismatch"] == tm["entry_not_after_t"] == 0
    assert ck["fresh_recomputation"]["agree_1e9"] == ck["fresh_recomputation"]["checked"] > 0
    assert ck["gate_procedure"]["identity_dates"] == 0 and ck["newey_west"]["max_abs_diff"] < 1e-9
    assert st["pit_audit"] and all(v == 0 for v in st["pit_audit"].values())
    # H023 checks
    g = ck["h023"]
    assert g["grid"] == 92 and g["control"] == [40, 45, 15] and g["control_z_mismatch"] == 0
    assert g["vs_h022_procedure"]["compared"] == 15 and g["vs_h022_procedure"]["max_abs_diff"] < 1e-12
    nr = g["null_record"]
    assert nr["repeat_identical"] and nr["distinct"] == 10 and nr["control_equals_h022"] and nr["finite_max_t"] == 10
    obs = sum(1 for d in a.h_dates if d["year"] >= 2014 and np.isfinite(d["y"]).sum() >= R.MIN_STOCKS)
    assert g["machinery"]["folds"] == 4 and g["machinery"]["pseudo_oos_months"] == obs > 0
    cc = st["components_check"]
    assert cc["rows"] > 1000 and cc["sum_mismatch"] == cc["total_mismatch"] == cc["out_of_range"] == 0
    assert len(st["components_sha256"]) == 64
    assert set(st["g_runtime_modules"]) == {"qr_h023.py", "qr_s024.py", "qr_x998.py", "qr_p7_pred.py"}
    for d in a.h_dates:                                                            # subtotals = Score v1 points
        assert np.array_equal(d["C"].sum(axis=1), np.asarray(d["S"], dtype=np.int64))


def test_null_worlds_are_the_grid_null_and_need_both_digests(monkeypatch, tmp_path):
    _, stc = _canary(monkeypatch, tmp_path)
    prm = dict(seeds=[1, 3], panel_sha256=stc["panel_sha256"], components_sha256=stc["components_sha256"])
    a, st = _run(monkeypatch, tmp_path, "null", **prm)
    blob = _chunks(a.msgs, "QRH")
    assert st["null"]["blob_sha256"] == hashlib.sha256(blob.encode()).hexdigest() and st["null"]["grid"] == 92
    pay = json.loads(E.unpack(blob))
    assert pay["fields"] == list(G.NULL_FIELDS) and [w[0] for w in pay["worlds"]] == [1, 2, 3]
    prep = G.prepare(a.h_dates)
    rp = R.prepare(a.h_dates)
    for w in pay["worlds"]:
        assert w == G.null_record(prep, w[0])
        row = dict(zip(pay["fields"], w))
        assert abs(row["t_control"] - R.run_world(rp, seed=w[0])["t_ic"]) < 1e-12   # = the H022 null world
    assert not any(m.startswith(("QRR|", "QRN|")) for m in a.msgs)
    with pytest.raises(Exception, match="layer subtotals differ"):
        _run(monkeypatch, tmp_path, "null", **dict(prm, components_sha256="f" * 64))
    with pytest.raises(Exception, match="differs from the pinned"):
        _run(monkeypatch, tmp_path, "null", **dict(prm, panel_sha256="f" * 64))


def _prov(stc, **kw):
    p = dict(c_search=2.9, c_fold={"2014": 2.8, "2015": 2.8, "2016": 2.9, "2017": 2.9}, null_result_sha256="0" * 64,
             threshold_commit="x" * 40, panel_sha256=stc["panel_sha256"], components_sha256=stc["components_sha256"])
    p.update(kw)
    return p


def test_real_mode_is_qr_h023_evaluate(monkeypatch, tmp_path):
    _, stc = _canary(monkeypatch, tmp_path)
    a, st = _run(monkeypatch, tmp_path, "real", **_prov(stc))
    blob = _chunks(a.msgs, "QRH")
    assert st["real"]["blob_sha256"] == hashlib.sha256(blob.encode()).hexdigest()
    out = json.loads(E.unpack(blob))
    assert st["provenance"]["c_search"] == 2.9 and st["mode"] == "real"
    ev = G.evaluate(G.prepare(a.h_dates), 2.9, [2.8, 2.8, 2.9, 2.9])
    assert np.array_equal(np.array(out["IC"]), ev["world"]["IC"])
    assert out["grid"] == [list(w) for w in G.GRID] and len(out["days"]) == len(G.prepare(a.h_dates))
    assert np.allclose(np.array(out["summary"]["t_ic"]), ev["summary"]["t_ic"], rtol=0, atol=0)
    sel = out["selection"]
    assert sel["candidate"] == ev["selection"]["candidate"] and sel["argmax"] == ev["selection"]["argmax"]
    assert out["walk_forward"]["pseudo_oos"]["months"] == ev["walk_forward"]["pseudo_oos"]["months"]
    assert set(out) >= {"h2", "h3", "structure", "cstar"}
    # the control column is H022's real statistic on the same panel
    ref = R.run_world(R.prepare(a.h_dates))
    assert abs(out["summary"]["t_ic"][G.CONTROL_INDEX] - ref["t_ic"]) < 1e-12
    for bad in (dict(panel_sha256="f" * 64), dict(components_sha256="f" * 64)):
        with pytest.raises(Exception, match="differ"):
            _run(monkeypatch, tmp_path, "real", **_prov(stc, **bad))


def test_initialisation_refuses_bad_params(monkeypatch, tmp_path):
    _env25(monkeypatch, tmp_path)
    good = dict(c_search=2.9, c_fold={"2014": 1, "2015": 1, "2016": 1, "2017": 1}, null_result_sha256="0" * 64,
                threshold_commit="x" * 40, panel_sha256="a" * 64, components_sha256="b" * 64)
    for bad in (dict(BASE, mode="export"), dict(H022_BASE, mode="canary"),
                dict(BASE, mode="null", seeds=[1, 10], panel_sha256="a" * 64),
                dict(BASE, mode="null", seeds=[0, 10], panel_sha256="a" * 64, components_sha256="b" * 64),
                dict(BASE, mode="real", **dict(good, c_search=None)),
                dict(BASE, mode="real", **dict(good, c_fold={"2014": 1})),
                dict(BASE, mode="real", **{k: v for k, v in good.items() if k != "threshold_commit"})):
        with pytest.raises(Exception):
            _host(monkeypatch, _mk(), path=S025, cls="H023ScoreV2", params=bad, mutate=_mutate, sec_off=True)


def test_configs_and_runner_wiring():
    from qresearch import experiment, run
    c = json.loads((ROOT / "experiments/E025-01/config.json").read_text())
    experiment.validate(c)
    p = c["params"]
    assert (c["strategy_id"], c["kind"], p["mode"], c["hypothesis_id"], c["programme"]) == (
        "S025", "infrastructure", "canary", "H023", "P8")
    assert p["spec_sha256"] == p8h023.SPEC_SHA256 and p["grid_code_sha256"] == p8h023.CODE_SHA256[
        "src/qresearch/lean/qr_h023.py"] and c["owner_approval_required"] and c["end"] == "2017-12-31"
    files = run.assemble_files(c, None, False)
    assert files["qr_s024.py"] == (ROOT / S024).read_text()
    assert files["qr_x998.py"] == (ROOT / "strategies/X998_data_v2_export/main.py").read_text()
    assert files["qr_h023.py"] == (ROOT / "src/qresearch/lean/qr_h023.py").read_text()
    assert hashlib.sha256(files["qr_s024.py"].encode()).hexdigest() == p8h023.sha(p8h023.PARENT_HOST)
    assert len(files) <= 50 and all(len(v) <= 64_000 for v in files.values())
    for k, v in (("end", "2018-12-31"), ("hypothesis_id", "H022"), ("programme", "P7")):
        bad = copy.deepcopy(c)
        bad[k] = v
        with pytest.raises(experiment.ConfigError):
            experiment.validate(bad)
    for prm in (dict(p, spec_sha256="x"), dict(p, grid_code_sha256="x"), dict(p, mode="export")):
        bad = copy.deepcopy(c)
        bad["params"] = prm
        with pytest.raises(experiment.ConfigError):
            experiment.validate(bad)
    n = copy.deepcopy(c)
    n["params"] = dict(p, mode="null", seeds=[1, 1000], panel_sha256=p8h023.PANEL_SHA256,
                       components_sha256=p8h023.COMPONENTS_SHA256 or "a" * 64)
    if p8h023.COMPONENTS_SHA256 is None:
        with pytest.raises(experiment.ConfigError):                       # no null run before the canary pins it
            experiment.validate(n)
    else:
        experiment.validate(n)
        with pytest.raises(experiment.ConfigError):
            experiment.validate(dict(n, params=dict(n["params"], seeds=[1, 999])))
    r = copy.deepcopy(c)
    r["kind"] = "research"
    r["params"] = dict(p, mode="real", c_search=2.5, c_fold={}, null_result_sha256="0" * 64, threshold_commit="x",
                       panel_sha256=p8h023.PANEL_SHA256, components_sha256=p8h023.COMPONENTS_SHA256)
    with pytest.raises(experiment.ConfigError):                           # never an unpinned c_SEARCH
        experiment.validate(r)


def test_null_configs_cover_exactly_seeds_1_to_5000_against_the_pinned_digests():
    from qresearch import experiment
    assert p8h023.COMPONENTS_SHA256 and len(p8h023.COMPONENTS_SHA256) == 64
    seeds = []
    for exp, (a, b) in zip(p8h023.NULL_RUNS, p8h023.NULL_BATCHES):
        c = json.loads((ROOT / f"experiments/{exp}/config.json").read_text())
        experiment.validate(c)
        p = c["params"]
        assert (c["strategy_id"], c["kind"], p["mode"], tuple(p["seeds"])) == ("S025", "infrastructure", "null", (a, b))
        assert p["panel_sha256"] == p8h023.PANEL_SHA256 and p["components_sha256"] == p8h023.COMPONENTS_SHA256
        assert c["owner_approval_required"] and c["end"] == "2017-12-31"
        seeds += list(range(a, b + 1))
    assert seeds == list(p8h023.NULL_SEEDS)
    c = json.loads((ROOT / f"experiments/{p8h023.RERUN}/config.json").read_text())
    experiment.validate(c)
    assert tuple(c["params"]["seeds"]) == p8h023.RERUN_SEEDS
