"""P14-CP4 (owner D235): the structural turnover post-mortem is structural only (no return column is read), its
committed result matches the committed P14-CP3b null, the relabelling identity holds on synthetic panels, and the
H029 / H030 status (no thresholds, no real run) is unchanged."""
import json
import sys

from conftest import ROOT

sys.path.insert(0, str(ROOT / "src"))
from qresearch import p14h029 as P  # noqa: E402

RES = ROOT / "research/phase14/cp4/P14_CP4_postmortem.json"
SRC = (ROOT / "research/phase14/cp4/P14_CP4_postmortem.py").read_text()


def test_structural_only_no_return_columns():
    assert 'STRUCT = ("turn29", "hhi29", "turn30", "hhi30")' in SRC
    for bad in ('"s_up29"', '"w29"', '"up29"', '"dn29"', '"beta29"', '"s_inc30"', '"w30"', "spy_oo", "r_oo", "daily"):
        assert bad not in SRC, bad
    d = json.loads(RES.read_text())
    assert d["structural_only"] and not d["returns_read"] and not d["holdout_accessed"]
    assert d["quantconnect_runs"] == 0 and d["thresholds"] is None and d["new_null"] is False


def test_reproduces_committed_null_and_identity():
    d = json.loads(RES.read_text())
    cp3b = json.loads((ROOT / P.SECTOR_NULL_RESULT).read_text())
    t = d["reproduction"]["turn29"]
    assert t["real"] == cp3b["real_selection_structure"]["turn29"] and t["sector_worlds_at_or_below_real"] == 0
    assert abs(t["sector_null"]["p0.5"] - cp3b["adequacy"]["turn29"]["lo"]) < 1e-12
    ident = d["synthetic"]["relabelling_identity"]
    assert ident["no_churn_unclustered"]["turn_identical_all_worlds"]
    assert ident["no_churn_sector_clustered_cap_binding"]["turn_identical_all_worlds"]
    assert all(v["hhi_identical_all_worlds"] for v in ident.values())
    assert not ident["churn_18_22_sector_clustered"]["turn_identical_all_worlds"]
    assert all(x["exact_identity_holds"] for x in d["synthetic"]["decomposition_seeds_1_3"])


def test_status_unchanged():
    assert P.C_UP_H029 is None and P.C_INCREMENTAL_H030 is None and P.THRESHOLD_COMMIT is None
    assert not (ROOT / "experiments" / P.REAL).exists()
