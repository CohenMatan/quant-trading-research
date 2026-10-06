"""H021-A frozen specification v1 (owner D160): the spec and the module are hash-pinned, the code carries exactly the
pinned constants, and the one real evaluation never precedes the pinned null threshold."""
import json

import qr_h021 as H
from qresearch import config, p6h021

ROOT = config.REPO_ROOT


def test_spec_and_code_hash_pinned():
    assert p6h021.spec_hash() == p6h021.SPEC_SHA256
    for rel, h in p6h021.CODE_SHA256.items():
        assert p6h021.sha256(rel) == h, rel


def test_code_constants_pinned():
    for k, v in p6h021.CONSTANTS.items():
        assert getattr(H, k) == v, k
    assert len(p6h021.NULL_SEEDS) == 5000 and p6h021.NULL_BATCHES[0] == (1, 1000) and p6h021.NULL_BATCHES[-1] == (4001, 5000)


def test_spec_states_the_frozen_design():
    s = (ROOT / p6h021.SPEC).read_text()
    for frag in ("**XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY**", "**no skip month**", "**215 monthly decisions**",
                 "**open of the first session after the decision**", "t_IC **>** c", "+0.030", "no block share > 0.50",
                 "**entire signal history**", "**R = 5,000 worlds**", "the 50th largest of the 5,000 null t_IC",
                 "NON-GATING DIAGNOSTIC", "H021-A QUALIFIED FOR PORTFOLIO-DESIGN RESEARCH", "H021-A DID NOT QUALIFY",
                 "2018-01-01 → 2021-12-31", "A small real edge may therefore remain undetectable."):
        assert frag in s, frag


def test_real_run_never_precedes_the_pinned_threshold():
    idx = (ROOT / "experiments" / "INDEX.csv").read_text().splitlines()
    real_rows = [ln for ln in idx if ln.startswith(p6h021.REAL_RUN + ",")]
    cfg = ROOT / "experiments" / p6h021.REAL_RUN / "config.json"
    if p6h021.C is None:
        assert p6h021.NULL_RESULT_SHA256 is None and p6h021.THRESHOLD_COMMIT is None
        assert not real_rows and not cfg.exists()
        return
    assert p6h021.sha256(p6h021.NULL_RESULT) == p6h021.NULL_RESULT_SHA256
    if cfg.exists():
        p = json.loads(cfg.read_text())["params"]
        assert p["threshold_c"] == p6h021.C and p["null_result_sha256"] == p6h021.NULL_RESULT_SHA256
        assert p["spec_sha256"] == p6h021.SPEC_SHA256 and p["panel_sha256"] == p6h021.PANEL_SHA256
        assert p["diag_sha256"] == p6h021.DIAG_SHA256 and p["threshold_commit"] == p6h021.THRESHOLD_COMMIT
