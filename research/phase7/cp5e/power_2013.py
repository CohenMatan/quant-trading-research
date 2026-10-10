"""P7-CP5e (D188) item 27 / 36: synthetic power of the frozen H022 procedure if the research window started in 2013.
Identical to research/phase7/P7_power.py (same synthetic return model, seeds, gates and null calibration; REAL
data-v1 score tables, SYNTHETIC returns only, no real return), except that the decision dates are restricted to
2013-01-31 .. 2017-11-30 (59 of the 83). A 2013 start would be forced by data availability / PIT integrity, never
chosen from returns. Output: research/phase7/cp5e/power_2013.json."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research/phase7"))
import P7_power as P  # noqa: E402

FIRST = 24                                   # decisions 0..23 = 2011-01 .. 2012-12


def main(workers=4):
    full = P.score_tables
    P.score_tables = lambda: full()[FIRST:]
    tables = P.score_tables()
    res = dict(first_decision_index=FIRST, n_dates=len(tables), seed_base=P.SEED_BASE, scenarios={})
    for name, sd in P.SCENARIOS.items():
        o = P.scenario(tables, sd, workers)
        res["scenarios"][name] = o
        print(name, json.dumps({k: o[k] for k in ("n_dates", "c_ic_synthetic", "null_ic_month_sd",
                                                   "holdout_false_promotion_full", "full_procedure")}, default=float))
    txt = json.dumps(res, indent=1, sort_keys=True, default=float)
    for bad in ("cagr", "sharpe", "drawdown"):
        assert bad not in txt.lower()
    (Path(__file__).parent / "power_2013.json").write_text(txt + "\n")


if __name__ == "__main__":
    main()
