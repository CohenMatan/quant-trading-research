"""P14 H029-A (owner D227): the audit host X802, its pins, config rule and upload set. The host forms no return,
requests nothing after 2021-12-31, keeps every frozen Data v2.1 rule (subclass of the byte-identical X801 module) and
fits the QuantConnect 50-file project limit."""
import hashlib
import json
import sys

import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research/phase14/cp1"))
from qresearch import experiment, p14h029a as P, run  # noqa: E402
from qresearch.holdout import HoldoutLockedError  # noqa: E402
import P14_CP1_configs as C  # noqa: E402

HOST = (ROOT / P.HOST).read_text()


def test_spec_and_code_pins():
    assert hashlib.sha256((ROOT / P.SPEC).read_bytes()).hexdigest() == P.SPEC_SHA256
    for rel, h in P.CODE_SHA256.items():
        assert h is not None and hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == h, rel


def test_host_forms_no_return_and_keeps_frozen_rules():
    code = HOST.split("\nfrom AlgorithmImports")[1]
    for bad in ('"open"', "response(", ".tsr(", "w_spy", "holding(", "label", "spy_tr", "RO[", "set_holdings",
                "market_order", "2022", "liquidate"):
        assert bad not in code, bad
    assert "class H029AAudit(X81.DataV2Export)" in HOST and "import qr_x801 as X81" in HOST
    assert 'Z_LAST = "2021-12-31"' in HOST
    for m in ("qr_x801", "qr_h029a", "qr_h024", "qr_h023", "qr_p7_pred", "qr_xs", "qr_data_v21"):
        assert m in HOST.split("from AlgorithmImports")[0], m


def _cfg():
    c = C.config()
    return json.loads(json.dumps(c))


def test_config_rule_accepts_only_the_pinned_audit():
    experiment.validate(_cfg())
    for mutate in (lambda c: c.update(end="2022-06-30"), lambda c: c["params"].update(mode="real"),
                   lambda c: c["params"].update(spec_sha256="0" * 64), lambda c: c.update(kind="research", split="DEV"),
                   lambda c: c["universe"].update(sec_corrections=True), lambda c: c.pop("owner_approval_required")):
        c = _cfg()
        mutate(c)
        with pytest.raises((experiment.ConfigError, HoldoutLockedError)):    # 2022+ hits the Holdout lock
            experiment.validate(c)


def test_upload_set_fits_the_project_limit():
    files = run.assemble_files(_cfg(), None, False)
    for n in ("main.py", "qr_x801.py", "qr_h029a.py", "qr_h024.py", "qr_h023.py", "qr_p7_pred.py", "qr_data_v21.py"):
        assert n in files, n
    for n in ("qr_h026.py", "qr_s028.py", "qr_s029.py", "qr_h027.py", "qr_h028.py"):
        assert n not in files, n
    assert files["qr_x801.py"] == (ROOT / P.DATA_HOST).read_text()
    assert len(files) <= 50, len(files)
