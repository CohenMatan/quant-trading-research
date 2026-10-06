"""P7-CP2 pre-registration (research/phase7/P7_score_spec.md) is hash-pinned with the score code, and the code
carries exactly the pinned constants, weights and disqualifiers."""
import qr_p7_score as S
from qresearch import config, p7score

ROOT = config.REPO_ROOT


def test_spec_and_code_hashes():
    assert p7score.sha256(p7score.SPEC) == p7score.SPEC_SHA256
    for rel, h in p7score.CODE_SHA256.items():
        assert p7score.sha256(rel) == h, rel


def test_constants_weights_and_disqualifiers_pinned():
    for k, v in p7score.CONSTANTS.items():
        assert getattr(S, k) == v, k
    assert S.POINTS == p7score.POINTS and S.HARD_DQ == p7score.HARD_DQ
    assert S.LARGE_DISTRIBUTION == 0.10 and S.TREND_WINDOW == 221 and S.TR_WINDOW == 253


def test_spec_states_the_frozen_rules():
    s = (ROOT / p7score.SPEC).read_text()
    for frag in ("**Technical Quality (40)**", "**Fundamental Quality (45)**", "**Sector Context (15)**",
                 "Quintile **within the FF12 sector**", "**split-adjusted close C**", "**total-return close P**",
                 "**ExitThreshold < EntryThreshold**", "**No fixed holding period or time stop.**",
                 "**no forced filling**", "**never** from returns", "Same-universe rule", "6000–6999",
                 "**monthly**", "**holdings only**", "**Exposure ceilings** per regime are **deferred**"):
        assert frag in s, frag
