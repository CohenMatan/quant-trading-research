"""H022 on FROZEN Data Infrastructure v2 (owner D194, P7-CP6): the host S024 (X999 = byte copy) on a fake QuantConnect
environment with SYNTHETIC prices, fundamentals and SEC reference.
- X999 is a byte copy of S024; the population / response / null / real / canary steps are S023 v1.1's, verbatim;
- the score side is the frozen X998 host's (identical per-review Score v1 and eligibility digests on the same market);
- the canary passes and computes no IC of the real assignment, no gate and no null statistic of real responses;
- null worlds equal the frozen qr_p7_pred procedure (seeded tether, never the identity assignment) and are refused
  when the prepared panel differs from the pinned one; the real mode refuses a different panel;
- config rules: X999 canary only; null runs only in the pinned batches against the pinned panel; no real run until a
  Data-v2 c_IC is pinned; the old Data-v1 c_IC is never used."""
import ast
import copy
import hashlib
import json
import shutil
import sys
import types

import numpy as np
import pytest

import qr_fundamentals as F
import qr_p7_export as E
import qr_p7_pred as R
from conftest import ROOT
from qresearch import p7pred, p7pred_v2
from test_data_v2 import _fake_table
from test_p7_export import _host
from test_p7_h022_host import _mk

S024 = "strategies/S024_h022_data_v2/main.py"
X999 = "strategies/X999_h022_v2_canary/main.py"
S023 = "strategies/S023_h022_predictive/main.py"
X998 = "strategies/X998_data_v2_export/main.py"
BASE = dict(spec_sha256=p7pred_v2.SPEC_SHA256, pred_code_sha256=p7pred_v2.PRED_CODE_SHA256)
VERBATIM = ("_st200", "_responses", "_digest", "_world_digest", "NULL_FIELDS", "_null", "_real", "_fresh_response",
            "_canary", "st_regime")


def _chunks(msgs, tag):
    parts = sorted((m for m in msgs if m.startswith(tag + "|")), key=lambda m: int(m.split("|")[1]))
    return "".join(m.split("|", 2)[2] for m in parts)


def _table34():
    """The X998 test table extended to all 34 synthetic securities (SEC filings, cover counts, SIC / CIK rows)."""
    from datetime import date, timedelta

    from test_data_v2 import dn, g4
    from test_p7_export import CIK, SIC
    t = _fake_table()
    pes = [date(y, m, d) for y in range(2008, 2018) for m, d in ((3, 31), (6, 30), (9, 30), (12, 31))]
    for j in range(12, 34):
        sid, cik = f"S{j:02d}", CIK.get(f"S{j:02d}", f"c{j}")
        if cik not in t["f"]:
            cols, prev = [[], [], [], [], []], 0
            for pe in pes:
                d = dn(pe)
                for i, v in enumerate((d - prev, 40, 2 if pe.month == 12 else 1, 5,
                                       g4(6e7) if pe + timedelta(days=40) >= date(2010, 6, 1) else None)):
                    cols[i].append(v)
                prev = d
            t["f"][cik] = cols
        t["sec_v1"]["sic_history"][sid] = [[dn(date(2008, 1, 2)), SIC.get(sid, 3570), cik]]
    return t


def _mutate(f, nd):
    f.security_reference = types.SimpleNamespace(security_type="ST00000001", is_depositary_receipt=False,
                                                 is_primary_share=True)
    f.company_reference.country_id = "USA"


def _env(monkeypatch, tmp_path):
    mod = types.ModuleType("qr_data_v2")
    mod.load_table = _table34
    monkeypatch.setitem(sys.modules, "qr_data_v2", mod)
    monkeypatch.setattr(F, "available_from", F.available_from)            # X998 rebinds these at import (M2)
    monkeypatch.setattr(F, "is_estimated_file_date", F.is_estimated_file_date)
    d = tmp_path / "lean"
    d.mkdir(exist_ok=True)
    shutil.copy(ROOT / X998, d / "qr_x998.py")                           # as the runner uploads it
    monkeypatch.syspath_prepend(str(d))
    monkeypatch.delitem(sys.modules, "qr_x998", raising=False)


_CACHE = {}


def _run(monkeypatch, tmp_path, mode, **params):
    key = (mode, json.dumps(params, sort_keys=True))
    if key not in _CACHE:
        _env(monkeypatch, tmp_path)
        a = _host(monkeypatch, _mk(), path=S024, cls="H022DataV2", params=dict(BASE, mode=mode, **params),
                  mutate=_mutate, sec_off=True)
        a.qr_on_end()
        _CACHE[key] = (a, json.loads(_chunks(a.msgs, "QRP7V")))
    return _CACHE[key]


def _methods(path, cls):
    src = (ROOT / path).read_text()
    tree = ast.parse(src)
    c = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls][0]
    out = {}
    for n in c.body:
        name = getattr(n, "name", None) or (n.targets[0].id if isinstance(n, ast.Assign) else None)
        if name:
            out[name] = ast.get_source_segment(src, n)
    return out


def test_x999_is_a_byte_copy_and_the_h022_steps_are_s023_verbatim():
    assert (ROOT / X999).read_bytes() == (ROOT / S024).read_bytes()
    a, b = _methods(S024, "H022DataV2"), _methods(S023, "H022Predictive")
    a["_digest"] = a.pop("_h_digest").replace("def _h_digest(", "def _digest(")   # renamed: X998 has its own _digest
    for name in VERBATIM:
        assert a[name] == b[name], name
    src = (ROOT / S024).read_text()
    assert "import qr_x998 as X98" in src and "class H022DataV2(X98.DataV2Export)" in src
    assert "run_world(prep, seed=None" not in src and "R.run_world(prep)" not in src.split("def _real")[0]


def test_canary_passes_and_computes_no_real_statistic(monkeypatch, tmp_path):
    a, st = _run(monkeypatch, tmp_path, "canary")
    ck = st["canary"]
    assert st["decisions"] == dict(n=83, first="2011-01-31", last="2017-11-30", last_response_end="2017-12-29")
    assert st["calendar_check"]["reviews_match"] and st["calendar_check"]["reviews"] == 84
    assert ck["real_ic_computed"] is False and ck["gates_computed"] is False
    assert not any(m.startswith(("QRN|", "QRR|")) for m in a.msgs)
    tm = ck["timing"]
    assert tm["rows"] > 1000
    for k in ("entry_not_after_t", "entry_on_or_before_t_day", "exit_outside", "value_mismatch", "status_mismatch",
              "response_end_after_last_session"):
        assert tm[k] == 0, k
    fr = ck["fresh_recomputation"]
    assert fr["checked"] > 20 and fr["agree_1e9"] == fr["checked"] == fr["status_agree"], fr
    inv = ck["response_invariance"]
    assert inv["future_changed"] == inv["past_changed"] == inv["truncation_changed"] == 0
    sc = ck["score_invariance"]
    assert sc["truncated_mismatch"] == sc["future_mismatch"] == sc["regime_mismatch"] == 0
    assert ck["responses_repeat_identical"]
    nm = ck["null_machinery"]
    assert nm["repeat_identical"] and nm["tether"]["not_permutation"] == nm["tether"]["self_matches"] == 0
    assert ck["newey_west"]["max_abs_diff"] < 1e-9
    gp = ck["gate_procedure"]
    assert gp["worlds"] == gp["complete"] == gp["gates_evaluated"] == gp["fields_finite"] > 0
    assert gp["identity_dates"] == 0
    assert st["coverage"]["mcap_missing"] == st["coverage"]["mom_missing"] == 0
    assert st["slice_spot_check"]["mismatch"] == 0
    assert st["pit_audit"] and all(v == 0 for v in st["pit_audit"].values()), st["pit_audit"]
    for k in ("panel_sha256", "score_side_sha256", "response_side_sha256", "availability_sha256", "calendar_sha256"):
        assert len(st[k]) == 64


def test_score_side_is_the_frozen_x998_export(monkeypatch, tmp_path):
    """Same fake market: S024's per-review Score v1 / eligibility digests equal the frozen X998 host's."""
    _, st = _run(monkeypatch, tmp_path, "canary")
    _env(monkeypatch, tmp_path)
    x = _host(monkeypatch, _mk(), path=X998, cls="DataV2Export", params=dict(mode="export"), mutate=_mutate, sec_off=True)
    x.qr_on_end()
    ref = json.loads(_chunks(x.msgs, "QRV2"))["digests"]
    assert st["data_v2_digests"]["review_scores"] == ref["review_scores"]
    assert st["data_v2_digests"]["review_eligibility"] == ref["review_eligibility"]
    assert len(ref["review_scores"]) == 84


def test_null_worlds_equal_the_frozen_procedure_and_need_the_pinned_panel(monkeypatch, tmp_path):
    _, stc = _run(monkeypatch, tmp_path, "canary")
    a, st = _run(monkeypatch, tmp_path, "null", seeds=[1, 3], panel_sha256=stc["panel_sha256"])
    assert st["panel_sha256"] == stc["panel_sha256"]
    blob = _chunks(a.msgs, "QRN")
    assert st["null"]["blob_sha256"] == hashlib.sha256(blob.encode()).hexdigest()
    pay = json.loads(E.unpack(blob))
    assert [w[0] for w in pay["worlds"]] == [1, 2, 3]
    prep = R.prepare(a.h_dates)
    for w in pay["worlds"]:
        ref = R.run_world(prep, seed=w[0])
        row = dict(zip(pay["fields"], w))
        assert row["t_ic"] == ref["t_ic"] and row["half2"] == ref["halves"][1] and row["t_inc"] == ref["t_inc"]
        T = R.Tether(w[0])
        assert all(list(T.step(p["ids"])) != list(p["ids"]) for p in prep)          # never the real assignment
    with pytest.raises(Exception, match="differs from the pinned"):
        _run(monkeypatch, tmp_path, "null", seeds=[1, 2], panel_sha256="f" * 64)


def test_real_mode_refuses_a_different_panel(monkeypatch, tmp_path):
    prov = dict(c_ic=2.5, threshold_commit="x" * 40, null_result_sha256="0" * 64)
    with pytest.raises(Exception, match="differs"):
        _run(monkeypatch, tmp_path, "real", panel_sha256="f" * 64, **prov)


def test_initialisation_refuses_bad_params(monkeypatch, tmp_path):
    _env(monkeypatch, tmp_path)
    for bad in (dict(BASE, mode="export"), dict(BASE, mode="null", seeds=[0, 10], panel_sha256="a" * 64),
                dict(BASE, mode="null", seeds=[1, 10]), dict(BASE, mode="real", c_ic=2.5), dict(mode="canary")):
        with pytest.raises(Exception):
            _host(monkeypatch, _mk(), path=S024, cls="H022DataV2", params=bad, mutate=_mutate, sec_off=True)


def test_pins_configs_and_runner_wiring():
    from qresearch import experiment, run
    assert p7pred_v2.manifest_ok()
    assert p7pred_v2.SPEC_SHA256 == p7pred.SPEC_SHA256 and p7pred_v2.C_IC_V2 != p7pred.C_IC
    assert p7pred.C_IC_STATUS == "DATA_V1_ONLY / UNUSED_ON_V2"
    assert p7pred_v2.NULL_BATCHES == ((1, 1000), (1001, 2000), (2001, 3000), (3001, 4000), (4001, 5000))
    c = json.loads((ROOT / "experiments/E999-01/config.json").read_text())
    experiment.validate(c)
    files = run.assemble_files(c, None, False)
    assert files["qr_x998.py"] == (ROOT / X998).read_text()
    m = json.loads((ROOT / "research/phase7/data_v2/data_freeze_v2.json").read_text())
    for name, rel in (("qr_x998.py", X998), ("qr_v2.py", "src/qresearch/lean/qr_v2.py"),
                      ("qr_p7_score.py", "src/qresearch/lean/qr_p7_score.py")):
        assert hashlib.sha256(files[name].encode()).hexdigest() == m["files"][rel], name    # = frozen Data v2
    assert hashlib.sha256(files["qr_p7_pred.py"].encode()).hexdigest() == p7pred_v2.PRED_CODE_SHA256
    assert len(files) <= 40 and all(len(v) <= 64_000 for v in files.values()) and "qr_sec_data.py" not in files
    for k, v in (("end", "2018-06-30"), ("params", dict(BASE, mode="null", seeds=[1, 1000]))):
        bad = copy.deepcopy(c)
        bad[k] = v
        with pytest.raises(experiment.ConfigError):
            experiment.validate(bad)
    s = copy.deepcopy(c)
    s.update(strategy_id="S024", strategy_dir="strategies/S024_h022_data_v2", experiment_id="E024-01")
    s["params"] = dict(BASE, mode="null", seeds=[1, 1000], panel_sha256=p7pred_v2.PANEL_SHA256 or "a" * 64)
    if p7pred_v2.PANEL_SHA256 is None:
        with pytest.raises(experiment.ConfigError):                       # no null run before the canary pins the panel
            experiment.validate(s)
    else:
        experiment.validate(s)
    r = copy.deepcopy(s)
    r["kind"] = "research"
    r["params"] = dict(BASE, mode="real", c_ic=p7pred.C_IC, threshold_commit=p7pred.THRESHOLD_COMMIT,
                       null_result_sha256=p7pred.NULL_RESULT_SHA256, panel_sha256=p7pred_v2.PANEL_SHA256)
    with pytest.raises(experiment.ConfigError):                           # the Data-v1 c_IC is never accepted
        experiment.validate(r)
    u = copy.deepcopy(c)
    u["universe"]["sec_corrections"] = True
    with pytest.raises(experiment.ConfigError):
        experiment.validate(u)


def test_null_configs_cover_exactly_seeds_1_to_5000_against_the_pinned_panel():
    from qresearch import experiment
    assert p7pred_v2.PANEL_SHA256 and len(p7pred_v2.PANEL_SHA256) == 64
    seeds = []
    for exp, (a, b) in zip(p7pred_v2.NULL_RUNS, p7pred_v2.NULL_BATCHES):
        c = json.loads((ROOT / f"experiments/{exp}/config.json").read_text())
        experiment.validate(c)
        p = c["params"]
        assert (c["strategy_id"], c["kind"], p["mode"], tuple(p["seeds"])) == ("S024", "infrastructure", "null", (a, b))
        assert p["panel_sha256"] == p7pred_v2.PANEL_SHA256 and c["owner_approval_required"]
        seeds += list(range(a, b + 1))
    assert seeds == list(p7pred_v2.NULL_SEEDS)
    c = json.loads((ROOT / f"experiments/{p7pred_v2.RERUN}/config.json").read_text())
    experiment.validate(c)
    assert tuple(c["params"]["seeds"]) == p7pred_v2.RERUN_SEEDS
    assert not (ROOT / "experiments/E024-07").exists()                    # no real-evaluation config exists


def test_data_v2_c_ic_is_pinned_from_the_5000_null_worlds():
    """The pinned Data-v2 c_IC is recomputed from the committed per-world null statistics with the frozen rule; the
    null result file is the pinned one; the Data-v1 value is a different, unused record."""
    import gzip
    path = ROOT / p7pred_v2.NULL_RESULT
    assert hashlib.sha256(path.read_bytes()).hexdigest() == p7pred_v2.NULL_RESULT_SHA256
    res = json.loads(path.read_text())
    ws = json.loads(gzip.open(ROOT / p7pred_v2.NULL_WORLDS).read())
    assert hashlib.sha256((ROOT / p7pred_v2.NULL_WORLDS).read_bytes()).hexdigest() == res["worlds_file_sha256"]
    assert [w["seed"] for w in ws] == list(p7pred_v2.NULL_SEEDS)
    assert R.critical_value(ws) == p7pred_v2.C_IC_V2 == res["c_ic"]
    assert sorted((w["t_ic"] for w in ws), reverse=True)[49] == p7pred_v2.C_IC_V2 > R.CRIT_FLOOR
    assert p7pred_v2.C_IC_V2 != p7pred.C_IC and p7pred.C_IC_STATUS == "DATA_V1_ONLY / UNUSED_ON_V2"
    integ = res["integrity"]
    assert integ["completed"] == 5000 and integ["seeds_exact"] and integ["panel_equals_pinned"]
    assert integ["rerun_identical"] and integ["zero_orders"] and integ["pit_audit_zero"]
    assert res["false_promotion"] == R.false_promotion(ws, p7pred_v2.C_IC_V2)
