"""OC-2 Stage 2 (owner D248): the frozen synthetic protocol, code pins and the committed result's internal
consistency (outcome re-derived from the committed numbers with the protocol's rule)."""
import hashlib
import json
import sys

from conftest import ROOT

sys.path[:0] = [str(ROOT / "research/longhorizon/oc2/stage2"), str(ROOT / "src")]
import OC2_S2_run as R  # noqa: E402

PROTOCOL_SHA = "bcb872adc50d0479c69895253edb66252d4299061a4edff6dc54bfbffa6bc233"   # original 447b4860… + Addendum 1
OUT = ROOT / "research/longhorizon/oc2/stage2/OC2_S2_results.json"


def test_protocol_and_code_frozen():
    assert hashlib.sha256(R.PROTOCOL.read_bytes()).hexdigest() == PROTOCOL_SHA
    R.verify_frozen()


def test_scenario_set_matches_protocol():
    names = [w.name for w in R.GATING]
    assert names == ["N0i", "N0", "N1", "N2", "N3", "N4", "N6", "N7", "N8a", "N8b", "N9", "N11", "N12", "N5a"]
    assert [w.name for w in R.DIAG] == ["N5b", "N2L", "N13"]
    assert all(w.planted == 0 for w in R.GATING + R.DIAG)
    assert R.N_GATE == 4000 and R.N_DIAG == 1000 and R.N_POW == 1000
    assert R.SIZE_1 == 0.020 and R.SIZE_5 == (0.035, 0.065) and R.POWER_TARGET == 0.80


def test_committed_result_consistent():
    if not OUT.exists():
        return
    d = json.loads(OUT.read_text())
    assert d["protocol_sha256"] == PROTOCOL_SHA and d["decision"] == "D248"
    for n, s in d["size_gates"].items():
        assert s["ok"] == (s["rej_1"] <= R.SIZE_1 and R.SIZE_5[0] <= s["rej_5"] <= R.SIZE_5[1])
        assert d["scenarios"][n]["n"] == R.N_GATE
    failed = [n for n, s in d["size_gates"].items() if not s["ok"]]
    inadequate = [n for n, v in d["adequacy"].items() if v]
    p3 = d["scenarios"]["PM3"]["rej_0.01"]
    exp = ("D — INSUFFICIENT EVIDENCE" if inadequate else "C — METHOD NOT VALIDATED" if failed else
           "A — METHOD VALIDATED WITH USEFUL POWER" if p3 >= R.POWER_TARGET else
           "B — METHOD CALIBRATED BUT UNDERPOWERED")
    assert d["outcome"] == exp
