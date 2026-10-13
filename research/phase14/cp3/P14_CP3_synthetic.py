"""P14-CP3 (owner D229, spec section 12): synthetic long-horizon robustness of H030 -- run ONLY if H030 passed C1-C7.
Committed before E031-05 ran. The frozen P13-CP3 machinery (research/phase13/cp3/P13_CP3_bootstrap.py: sampling,
seeds, per-world metrics, summaries) is applied unchanged to the paired monthly returns of H030, H028 and SPY from
E031-05 (calendar month-end marks). Development gates, not probabilities of future success.

    PYTHONPATH=src python research/phase14/cp3/P14_CP3_synthetic.py
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7")]
spec = importlib.util.spec_from_file_location("p13cp3", ROOT / "research/phase13/cp3/P13_CP3_bootstrap.py")
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
import qr_h029 as Q  # noqa: E402
from P14_CP3_result import load  # noqa: E402

N = 10_000
METHODS = ("year", "mb12", "mb24", "ex1820")


def main():
    res = json.loads((HERE / "P14_CP3_result.json").read_text())
    if not res["synthetic_robustness_eligible"]:
        raise SystemExit("H030 did not pass C1-C7: the synthetic robustness study is not run (spec 12)")
    _st, o = load()
    days = np.asarray(o["days"], float)
    r = {n: Q.monthly(o["daily"][n], days)[0] for n in ("h030", "h028", "spy")}
    out = {}
    for order, tag in ((("h030", "h028", "spy"), "h030"), (("h028", "h030", "spy"), "h028")):
        lr = np.log1p(np.stack([r[n] for n in order], axis=1))              # P13 layout: (strategy, second, SPY)
        out[tag] = {}
        for m in METHODS:
            _w, _i, summ = B.run_method(lr, m, N)
            out[tag][m] = summ
    y30, x30 = out["h030"]["year"]["summary"]["30y"], out["h030"]["ex1820"]["summary"]["30y"]
    req = dict(primary_p=y30["p_beat_spy"] >= 0.90, primary_median=y30["ratio_spy"]["p50"] > 1.0,
               stress_median=x30["ratio_spy"]["p50"] > 1.0, stress_p=x30["p_beat_spy"] > 0.50)
    out["requirements"] = dict(req, all=all(req.values()),
                               note="'lv15' keys of the P13 summaries hold the second series (H028 for tag h030)")
    (HERE / "P14_CP3_synthetic.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(out["requirements"])


if __name__ == "__main__":
    main()
