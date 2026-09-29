# C01: H001 remedial re-test after infrastructure correction (written before any run)

**Owner approval, 2026-09-29.**

- H001 was never validly tested: D063 left positions permanently stuck.
- It is re-run exactly as pre-registered, after D057 is finished and D063 is verified end to end.
- **This completes an invalid C01 test. It is not C02 and not a new strategy search.**

**Preconditions (both must pass, otherwise stop and report).**

1. **D057 final probe E956-03.** No excluded security type remains. The dated overrides take effect exactly on their dates.
2. **D063 canary E958-01.** Every picked stock is removed from the universe while its buy is pending, and its window is kept. Every buy fills with its window present. Every exit reads the window and fires after 3 closes. The safety net restores the deliberately deleted windows. No position is left stuck.

**Runs.**

- Fresh IDs E001-16..20, one per pre-registered variation (v1.0..v1.4).
- Each config is **identical** to E001-11..15 (the final C01 H001 configs), except for the ID, the description label "H001 remedial re-test after infrastructure correction", `remedial_of`, and the final harness (D057 + D059 + D063).
- Unchanged: signals, parameters, exits, sizing, costs, universe rules (other than the corrected infrastructure), execution timing and no-borrowing.
- All five are run and all five are reported.
- IS only: 2010-01-04 → 2017-12-29.

**Benchmark.** E901-07, the equal-weight ≥ $2B universe on the same final harness, over the same dates. SPY E900-07 is for reference only.

**Gates.** The original C01 IS screen (D036, `gates.is_screen`) is applied unchanged.

**If at least one variation passes.**

1. 2× slippage run for each passing variation (screen item: Sharpe ≥ 0.4).
2. Then, only for the best passing variation by net IS Sharpe, the C01 robustness battery as pre-declared in C01_plan.md:
   - slippage 4× (required Sharpe > 0) and 6× (reported);
   - thirds of IS all positive;
   - IS episodes (part of the screen);
   - parameter plateau ±20–50%: at least 80% of perturbations keep ≥ 70% of the base Sharpe.
   - The plateau values, fixed now and never extended:

     | Variation | Perturbations |
     |---|---|
     | v1.0 / v1.2 / v1.3 | rsi_max 10 → 5, 8, 12, 15 and max_hold 10 → 5, 8, 12, 15 |
     | v1.1 | rsi_max 5 → 3, 4, 6, 8 and max_hold 10 → 5, 8, 12, 15 |
     | v1.4 | ret3_max −0.06 → −0.03, −0.048, −0.072, −0.09 and max_hold 10 → 5, 8, 12, 15 |

   - PBO across the five variations is reported.
3. **No promotion to Validation.** A pass is reported only; the owner decides.

**No other runs.** No new parameters or variations, no Validation/Walk-Forward/Holdout, and no 2018+ dates.

**Trial accounting** (D066).

- The remedial runs repeat pre-registered variations on corrected infrastructure. They are counted as **technical re-runs**, not new strategy trials.
- Verification runs and canaries are never trials.
- Any robustness perturbation that is run **is** a genuine trial.
