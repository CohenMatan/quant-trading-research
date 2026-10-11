"""H024 host S026 (owner D201) on the fake QuantConnect environment of the H022 / Data v2 tests (SYNTHETIC prices,
fundamentals and SEC reference):
- S026 subclasses the pinned S024 (uploaded byte-identical as qr_s024); its panel equals S024's on the same market;
- the canary computes no statistic of real responses; features are recomputed independently; the total-assets ledger
  feeds AG consistently; the model library is generated from the feature correlations (no response);
- null worlds equal qr_h024.null_record and need the pinned population / library digests; the real mode output is
  qr_h024.evaluate on the same panel; config rules and runner wiring."""
import copy
import hashlib
import json
import shutil
import sys

import numpy as np
import pytest

import qr_h023 as G
import qr_h024 as K
import qr_p7_export as E
from conftest import ROOT
from qresearch import p7pred_v2, p9h024
from test_p7_export import _host
from test_p7_h022_host import _mk
from test_p7_h022_v2 import _chunks, _env, _mutate
from test_p7_h022_v2 import _run as _run24

S026 = "strategies/S026_h024_features/main.py"
S024 = "strategies/S024_h022_data_v2/main.py"
BASE = dict(spec_sha256="spec", pred_code_sha256=p7pred_v2.PRED_CODE_SHA256, feature_code_sha256="feat")
_CACHE = {}


def _env26(monkeypatch, tmp_path):
    _env(monkeypatch, tmp_path)
    shutil.copy(ROOT / S024, tmp_path / "lean" / "qr_s024.py")
    monkeypatch.delitem(sys.modules, "qr_s024", raising=False)


def _run(monkeypatch, tmp_path, mode, **params):
    key = (mode, json.dumps(params, sort_keys=True))
    if key not in _CACHE:
        _env26(monkeypatch, tmp_path)
        a = _host(monkeypatch, _mk(), path=S026, cls="H024Features", params=dict(BASE, mode=mode, **params),
                  mutate=_mutate, sec_off=True)
        a.qr_on_end()
        _CACHE[key] = (a, json.loads(_chunks(a.msgs, "QRP7V")))
    return _CACHE[key]


def _pins(st):
    g = st["canary"]["h024"]
    return dict(features=g["retained"], links=g["links"], library_sha256=g["library_sha256"],
                population_sha256=g["population_sha256"], panel_sha256=st["panel_sha256"])


def test_canary_passes_and_reads_no_response(monkeypatch, tmp_path):
    a, st = _run(monkeypatch, tmp_path, "canary")
    _, s24 = _run24(monkeypatch, tmp_path, "canary")
    assert st["panel_sha256"] == s24["panel_sha256"] and st["data_v2_digests"] == s24["data_v2_digests"]
    ck = st["canary"]
    assert ck["real_ic_computed"] is False and ck["gates_computed"] is False
    assert not any(m.startswith(("QRN|", "QRR|", "QRK|")) for m in a.msgs)
    g = ck["h024"]
    assert g["library"] == list(K.LIBRARY)
    assert g["retained"] == [f for f in K.LIBRARY if g["coverage"][f] >= K.COVERAGE_MIN]
    rec = g["recomputation"]
    assert rec["checked"] > 50 and rec["mismatch"] == 0 and rec["ledger_mismatch"] == 0
    assert g["ledger"]["months"] >= 72
    assert g["vs_h022_procedure"]["compared"] > 0 and g["vs_h022_procedure"]["max_abs_diff"] < 1e-12
    assert g["control_equals_score_v1"]
    nr = g["null_record"]
    assert nr["repeat_identical"] and nr["distinct"] == 6
    lib = K.Library(K.model_library(tuple(g["retained"]), K.FAMILY, [tuple(x) for x in g["links"]]), tuple(g["retained"]))
    assert lib.sha == g["library_sha256"] and lib.M == g["models"] <= K.MODEL_BUDGET
    F = len(g["retained"])
    assert np.array(g["correlation"]["median_abs"]).shape == (F, F)
    cov = st["feature_coverage"]
    assert cov["rows"] == sum(len(d["ids"]) for d in a.h_dates)
    assert st["pit_audit"] and all(v == 0 for v in st["pit_audit"].values())


def test_feature_values_are_point_in_time_and_consistent(monkeypatch, tmp_path):
    a, st = _run(monkeypatch, tmp_path, "canary")
    d = a.h_dates[-1]
    assert d["X"].shape[0] == len(d["ids"])
    t = {str(x): x for x in a.mon}[d["day"]]
    for s_, row in zip(d["ids"][:20], d["X"][:20]):
        vals = a.mon[t][s_]["vals"]
        if vals[4] and vals[1] is not None and np.isfinite(row[K.LIBRARY.index("GPA")]):
            assert row[K.LIBRARY.index("GPA")] == vals[1] / vals[4]
    assert all(k < (2017, 1) for k in a.k_ta)                                      # ledger never reaches 2017


def test_null_worlds_need_the_pinned_digests(monkeypatch, tmp_path):
    _, stc = _run(monkeypatch, tmp_path, "canary")
    pins = _pins(stc)
    a, st = _run(monkeypatch, tmp_path, "null", seeds=[1, 3], **pins)
    blob = _chunks(a.msgs, "QRK")
    assert st["null"]["blob_sha256"] == hashlib.sha256(blob.encode()).hexdigest()
    pay = json.loads(E.unpack(blob))
    assert pay["fields"] == list(K.NULL_FIELDS) and [w[0] for w in pay["worlds"]] == [1, 2, 3]
    lib = K.Library(K.model_library(tuple(pins["features"]), K.FAMILY, [tuple(x) for x in pins["links"]]),
                    tuple(pins["features"]))
    prep = K.prepare(a.h_dates, lib)
    for w in pay["worlds"]:
        assert w == K.null_record(prep, lib, w[0])
    for bad in (dict(population_sha256="f" * 64), dict(library_sha256="f" * 64)):
        with pytest.raises(Exception, match="differs"):
            _run(monkeypatch, tmp_path, "null", seeds=[1, 2], **dict(pins, **bad))


def test_real_mode_is_qr_h024_evaluate(monkeypatch, tmp_path):
    _, stc = _run(monkeypatch, tmp_path, "canary")
    prov = dict(_pins(stc), c_model=3.1, c_feature=2.9, c_fold={"2014": 3.2, "2015": 3.2, "2016": 3.3, "2017": 3.1},
                null_result_sha256="0" * 64, threshold_commit="x" * 40)
    a, st = _run(monkeypatch, tmp_path, "real", **prov)
    blob = _chunks(a.msgs, "QRK")
    assert st["real"]["blob_sha256"] == hashlib.sha256(blob.encode()).hexdigest()
    out = json.loads(E.unpack(blob))
    lib = K.Library(K.model_library(tuple(prov["features"]), K.FAMILY, [tuple(x) for x in prov["links"]]),
                    tuple(prov["features"]))
    ev = K.evaluate(K.prepare(a.h_dates, lib), lib, 3.1, [3.2, 3.2, 3.3, 3.1])
    assert np.array_equal(np.array(out["IC"]), ev["world"]["IC"]) and out["pick"] == ev["pick"]
    assert out["models"] == [list(m) for m in lib.models] and set(out) >= {"h2", "h3", "walk_forward", "stability"}
    with pytest.raises(Exception, match="differ"):
        _run(monkeypatch, tmp_path, "real", **dict(prov, panel_sha256="f" * 64))


def test_initialisation_refuses_bad_params(monkeypatch, tmp_path):
    _env26(monkeypatch, tmp_path)
    for bad in (dict(BASE, mode="export"), dict(BASE, mode="canary", feature_code_sha256=""),
                dict(BASE, mode="null", seeds=[1, 10], panel_sha256="a" * 64),
                dict(BASE, mode="real", features=[], links=[], library_sha256="a", population_sha256="b")):
        with pytest.raises(Exception):
            _host(monkeypatch, _mk(), path=S026, cls="H024Features", params=bad, mutate=_mutate, sec_off=True)


def test_configs_and_runner_wiring():
    from qresearch import experiment, run
    c = json.loads((ROOT / "experiments/E026-01/config.json").read_text())
    experiment.validate(c)
    p = c["params"]
    assert (c["strategy_id"], c["kind"], p["mode"], c["hypothesis_id"], c["programme"]) == (
        "S026", "infrastructure", "canary", "H024", "P9")
    assert p["spec_sha256"] == p9h024.SPEC_SHA256 and p["feature_code_sha256"] == p9h024.CODE_SHA256[
        "src/qresearch/lean/qr_h024.py"] and c["end"] == "2017-12-31" and c["owner_approval_required"]
    files = run.assemble_files(c, None, False)
    assert files["qr_s024.py"] == (ROOT / S024).read_text()
    assert files["qr_h024.py"] == (ROOT / "src/qresearch/lean/qr_h024.py").read_text()
    assert files["qr_h023.py"] == (ROOT / "src/qresearch/lean/qr_h023.py").read_text()
    assert hashlib.sha256(files["qr_h023.py"].encode()).hexdigest() == p9h024.ENGINE_SHA256
    assert len(files) <= 50 and all(len(v) <= 64_000 for v in files.values())
    for k, v in (("end", "2018-12-31"), ("hypothesis_id", "H023"), ("programme", "P8")):
        bad = copy.deepcopy(c)
        bad[k] = v
        with pytest.raises(experiment.ConfigError):
            experiment.validate(bad)
    n = copy.deepcopy(c)
    n["params"] = dict(p, mode="null", seeds=[1, 1000], features=list(p9h024.FEATURES or K.LIBRARY),
                       links=[list(x) for x in (p9h024.LINKS or [])], library_sha256=p9h024.LIBRARY_SHA256 or "a",
                       population_sha256=p9h024.POPULATION_SHA256 or "b", panel_sha256=p9h024.PANEL_SHA256)
    if p9h024.FEATURES is None:
        with pytest.raises(experiment.ConfigError):
            experiment.validate(n)
    else:
        experiment.validate(n)
    r = copy.deepcopy(n)
    r["kind"] = "research"
    r["params"] = dict(n["params"], mode="real", c_model=2.5, c_feature=2.5, c_fold={}, null_result_sha256="0",
                       threshold_commit="x")
    with pytest.raises(experiment.ConfigError):
        experiment.validate(r)
