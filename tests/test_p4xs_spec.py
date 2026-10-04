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
                 "all 12 required", "**2011-01 → 2017-11: 83 month-ends.**", "**lag 2**", "min_samples=1",
                 "Every null world re-runs the complete procedure", "the 50th largest F over R = 5,000",
                 "R = 5,000", "α = 1%", "never promotes, rescues or vetoes", "2018-01-01 → 2021-12-31",
                 "2022-01-01 → 2026-08-31", "large enough to satisfy the project's detection and economic-significance"):
        assert frag in s, frag
    assert len(p4xs.NULL_SEEDS) == 5000 and p4xs.NULL_BATCHES[-1] == (4001, 5000)


def test_h019_null_threshold_pinned():
    """D145: c, the null result and the per-world table are pinned before the one real evaluation E020-06."""
    import hashlib
    import json
    from qresearch import p4xs
    if p4xs.THRESHOLD_C is None:
        return
    root = config.REPO_ROOT
    path = root / p4xs.NULL_RESULT
    assert hashlib.sha256(path.read_bytes()).hexdigest() == p4xs.NULL_RESULT_SHA256
    n = json.loads(path.read_text())
    assert n["c"] == p4xs.THRESHOLD_C and n["worlds"] == 5000 and n["failed_worlds"] == 0 and n["rank_k"] == 50
    assert n["spec_sha256"] == p4xs.SPEC_SHA256 and n["seeds"] == [1, 5000]
    csv = root / "research/phase4/H019_null_worlds.csv"
    assert hashlib.sha256(csv.read_bytes()).hexdigest() == n["null_worlds_csv_sha256"] == p4xs.NULL_WORLDS_CSV_SHA256
    F = sorted((float(ln.split(",")[2]) for ln in csv.read_text().splitlines()[1:]), reverse=True)
    assert len(F) == 5000 and F[49] == p4xs.THRESHOLD_C
