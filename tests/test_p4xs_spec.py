"""H019 pre-registration v1 (P4-CP3R): the specification hash and the qr_xs constants it names are pinned; the
primary design is the corrected one (1-month horizon, exact ID, exact Han-Zhou-Zhu trend factor, alpha 1%)."""
import sys

from qresearch import config, p4xs

sys.path.insert(0, str(config.REPO_ROOT / "src/qresearch/lean"))
import qr_xs as X  # noqa: E402


def test_spec_hash_pinned():
    assert p4xs.spec_hash() == p4xs.SPEC_SHA256


def test_qr_xs_constants_pinned():
    for k, v in p4xs.CONSTANTS.items():
        assert getattr(X, k) == v, k


def test_spec_states_the_corrected_design():
    s = (config.REPO_ROOT / p4xs.SPEC).read_text()
    for frag in ("ID = sgn(PRET) × (%neg − %pos)", "key = −sgn(PRET) × ID", "{3, 5, 10, 20, 50, 100, 200, 400, 600, 800, 1000}",
                 "12 most recent completed regressions", "**2011-02 → 2017-11: 82 dates**", "**lag 2**",
                 "R = 5,000", "α = 1%", "can never promote, rescue or veto", "2018-01-01 → 2021-12-31",
                 "2022-01-01 → 2026-08-31", "large enough to satisfy the project's detection and economic-significance"):
        assert frag in s, frag
    assert len(p4xs.NULL_SEEDS) == 5000 and p4xs.NULL_BATCHES[-1] == (4001, 5000)
