"""P14 H029 / H030 (owner D229): the standalone host S031, its pins, config rule and upload set. The frozen S028 /
S029 month-building methods are copied VERBATIM (source text identical), the host imports no S028 / S029 / S030 /
H027 / H028 module (no subclass chain), places no order, requests nothing after 2021-12-31 and fits 50 files."""
import ast
import hashlib
import json
import sys

import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research/phase14/cp3"))
from qresearch import experiment, p14h029 as P, run  # noqa: E402
from qresearch.holdout import HoldoutLockedError  # noqa: E402
import P14_CP3_configs as C  # noqa: E402

HOST = (ROOT / P.HOST).read_text()


def _methods(path, cls):
    src = (ROOT / path).read_text()
    lines = src.split("\n")
    for node in ast.parse(src).body:
        if isinstance(node, ast.ClassDef) and node.name == cls:
            return {f.name: "\n".join(lines[f.lineno - 1:f.end_lineno]) for f in node.body
                    if isinstance(f, ast.FunctionDef)}
    raise KeyError(cls)


def test_pins():
    assert hashlib.sha256((ROOT / P.SPEC).read_bytes()).hexdigest() == P.SPEC_SHA256
    for rel, h in P.CODE_SHA256.items():
        assert h is not None and hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == h, rel


def test_frozen_s028_s029_methods_are_verbatim():
    mine = _methods(P.HOST, "H029H030")
    s28 = _methods("strategies/S028_h026_learned_score/main.py", "H026Learned")
    s29 = _methods("strategies/S029_h027_exposure_controlled/main.py", "H027Conditional")
    for n in ("_repair", "_w_features", "_w_months", "_w_feature_digest", "_w_response_digest", "_w_emit"):
        assert mine[n] == s28[n], n
    for n in ("_build", "_w_scores", "_g_free_panel", "_g_release_run_state", "_g_stage"):
        assert mine[n] == s29[n], n
    # the S028 month-end additions, verbatim
    s28_me = s28["_month_end"].split("super()._month_end(t, today, elig, adv, fl)\n", 1)[1]
    assert s28_me.strip() in mine["_month_end"]


def test_standalone_no_orders_no_2022():
    head, code = HOST.split("\nfrom AlgorithmImports")
    assert "class H029H030(X81.DataV2Export)" in HOST and "import qr_x801 as X81" in HOST
    for bad in ("qr_s028", "qr_s029", "qr_s030", "qr_h027", "qr_h028", "qr_h029a", "qr_h020", "qr_v3val"):
        assert bad not in HOST, bad
    for bad in ("set_holdings", "market_order", "liquidate", "2022", "limit_order"):
        assert bad not in code, bad
    for m in ("qr_x801", "qr_v3", "qr_data_v3", "qr_h029", "qr_h026", "qr_p7_pred", "qr_data_v21"):
        assert m in head, m
    assert 'Y_LAST = "2021-12-31"' in HOST


def _cfg(mode="canary", seeds=None):
    exp = {"canary": P.CANARY, "null": P.NULL_RUNS[0]}[mode]
    return json.loads(json.dumps(C.config(exp, mode, seeds)))


def test_config_rule():
    experiment.validate(_cfg())
    experiment.validate(_cfg("null", P.NULL_SEEDS[P.NULL_RUNS[0]]))
    for mutate in (lambda c: c.update(end="2022-06-30"), lambda c: c["params"].update(spec_sha256="0" * 64),
                   lambda c: c["params"].update(h028_real_wealth=1.0), lambda c: c["params"].update(seeds=[1, 9]),
                   lambda c: c["params"].update(h029_panel_digests_sha256="0" * 64),
                   lambda c: c.update(kind="research"), lambda c: c.pop("owner_approval_required"),
                   lambda c: c["universe"].update(sec_corrections=True)):
        c = _cfg("null", P.NULL_SEEDS[P.NULL_RUNS[0]])
        mutate(c)
        with pytest.raises((experiment.ConfigError, HoldoutLockedError)):
            experiment.validate(c)
    if P.C_UP_H029 is None:                         # the real run is impossible before the thresholds are pinned
        c = _cfg()
        c["params"].update(mode="real")
        c.update(kind="research", split="DEV")
        with pytest.raises(experiment.ConfigError):
            experiment.validate(c)


def test_upload_set_fits_the_project_limit():
    files = run.assemble_files(_cfg(), None, False)
    for n in ("main.py", "qr_x801.py", "qr_v3.py", "qr_h029a.py", "qr_h029.py", "qr_h026.py", "qr_h024.py", "qr_h023.py",
              "qr_p7_pred.py", "qr_h020_stats.py", "qr_data_v21.py", "qr_data_v3_00.py", "qr_data_v3_03.py"):
        assert n in files, n
    for n in ("qr_h027.py", "qr_h028.py", "qr_s028.py", "qr_s029.py", "qr_v3val_00.py", "qr_chart.py"):
        assert n not in files, n
    assert files["qr_x801.py"] == (ROOT / P.DATA_HOST).read_text()
    assert len(files) <= 50, len(files)
    assert max(len(t) for t in files.values()) <= 64_000


def test_amendment1_sector_null_pins_and_records():
    """Amendment 1 (owner D233): own pin; the original spec stays byte-identical; the original null runs and result
    stay the record and are never reused; the new run ids are distinct; the inadequate null's thresholds are never
    the pinned ones; the frozen H028 result is pinned."""
    assert hashlib.sha256((ROOT / P.AMENDMENT1).read_bytes()).hexdigest() == P.AMENDMENT1_SHA256
    assert hashlib.sha256((ROOT / P.ORIGINAL_NULL_RESULT).read_bytes()).hexdigest() == P.ORIGINAL_NULL_RESULT_SHA256
    assert hashlib.sha256((ROOT / P.H028_RESULT).read_bytes()).hexdigest() == P.H028_RESULT_SHA256
    old = json.loads((ROOT / P.ORIGINAL_NULL_RESULT).read_text())
    assert (old["c_up_h029"], old["c_incremental_h030"]) == P.INVALID_THRESHOLDS
    assert old["verdict"] == "STOP — H029/H030 NULL INADEQUATE"
    new = {P.CANARY, P.RERUN, P.REAL, *P.NULL_RUNS}
    orig = {P.ORIGINAL_RUNS["canary"], P.ORIGINAL_RUNS["rerun"], P.ORIGINAL_RUNS["real_never_run"],
            *P.ORIGINAL_RUNS["null"]}
    assert len(new) == 5 and not new & orig
    assert set(P.NULL_SEEDS) == {*P.NULL_RUNS, P.RERUN}
    assert not (ROOT / "experiments" / P.ORIGINAL_RUNS["real_never_run"]).exists()
    if P.C_UP_H029 is not None:
        assert (P.C_UP_H029, P.C_INCREMENTAL_H030) != P.INVALID_THRESHOLDS
        assert P.C_UP_H029 not in P.INVALID_THRESHOLDS and P.C_INCREMENTAL_H030 not in P.INVALID_THRESHOLDS
    host = (ROOT / P.HOST).read_text()
    assert "S031 v1.1" in host and "donor_other_sector" in host and "Q.NullNotConstructible" in host


def test_amendment1_config_carries_the_amendment_pin():
    c = _cfg()
    assert c["params"]["amendment1_sha256"] == P.AMENDMENT1_SHA256 and c["strategy_version"] == "v1.1"
    c["params"]["amendment1_sha256"] = "0" * 64
    with pytest.raises(experiment.ConfigError):
        experiment.validate(c)
