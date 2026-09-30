"""C03 DSR hurdles under the frozen D082 specification (no C03 or Validation data used).

For each trial count N: the expected best skill-less annual Sharpe (SR*), and the observed annual
Sharpe a book needs over IS + VAL (2,012 + 1,008 daily returns, normal returns) for DSR >= 0.90.
Also the weakest VAL Sharpe that can coexist with a passing combined DSR once the unchanged VAL gate
"VAL Sharpe >= 0.5 x IS Sharpe" holds (equal volatility in both periods assumed), and what a
VAL-only DSR would demand (a diagnostic, not a gate).

    PYTHONPATH=src python research/cycles/C03_dsr_hurdles.py  -> research/cycles/C03_dsr_hurdles.json
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, "src")
from qresearch import stats  # noqa: E402

VAR_SR = 0.0010013434709235445      # D069 dispersion before C03 (registry at the D082 commit)
T_IS, T_VAL = 2012, 1008
Z90 = 1.2815515655446004


def needed(n, t):
    e = stats.expected_max_sharpe(n, VAR_SR)
    return e * math.sqrt(252), (e + Z90 / math.sqrt(t - 1)) * math.sqrt(252)


def main():
    out = {}
    for label, n in (("official N = 43", 43), ("conservative N after committed runs = 76", 76),
                     ("conservative N, every conditional run = 120", 120)):
        star, comb = needed(n, T_IS + T_VAL)
        _, val_only = needed(n, T_VAL)
        w = (T_IS + 0.5 * T_VAL) / (T_IS + T_VAL)     # combined Sharpe = w x IS when VAL = 0.5 x IS
        out[label] = dict(n=n, sr_star_annual=round(star, 3), combined_needed_annual=round(comb, 3),
                          weakest_is_with_val_at_half=round(comb / w, 3),
                          weakest_val_that_can_pass=round(0.5 * comb / w, 3),
                          val_only_dsr_would_need=round(val_only, 3))
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
