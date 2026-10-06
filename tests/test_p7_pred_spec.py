"""P7-CP4 (D175): the frozen predictive-test specification, the score / mechanics / null / power code and the tests it
names are hash-pinned, and the code carries exactly the pinned constants; c_IC is not pinned yet (no real run)."""
import qr_p7_mech as M
import qr_p7_pred as R
from qresearch import p7pred, p7score


def test_spec_and_code_hashes():
    assert p7pred.sha256(p7pred.SPEC) == p7pred.SPEC_SHA256
    for rel, h in p7pred.CODE_SHA256.items():
        assert p7pred.sha256(rel) == h, rel
    for rel, h in p7score.CODE_SHA256.items():              # Score v1 unchanged
        assert p7pred.CODE_SHA256[rel] == h


def test_constants_pinned():
    for k, v in p7pred.CONSTANTS.items():
        assert getattr(R, k) == v, k
    assert R.SEEDS == p7pred.NULL_SEEDS
    assert M.SECTOR_MAX == 3 and M.REGIME_POSITIONS == p7pred.MECHANICS["REGIME_POSITIONS"]
    assert (M.INITIAL_POSITION_CAP, M.GROWN_WINNER_CAP) == (0.10, 0.20)


def test_no_real_threshold_pinned_yet():
    assert p7pred.C_IC is None and p7pred.NULL_RESULT_SHA256 is None and p7pred.THRESHOLD_COMMIT is None


def test_spec_states_the_frozen_rules():
    from qresearch import config
    s = (config.REPO_ROOT / p7pred.SPEC).read_text()
    for frag in ("**83 dates:**", "**next session's open**", "**last real close**", "Newey-West standard error with **lag 2**", "+3.0% a year**",
                 "**≥ 0.90**", "**both halves**", "identity-tethered within-date permutation", "R = **5,000**",
                 "**one-sided 1%**", "**80 / 70 / 5**", "**STRONG 10, NORMAL 8, WEAK 5, RISK_OFF 2**",
                 "**3** holdings per PIT FF12", "**20%** of equity", "CIK Option A"):
        assert frag in s, frag
