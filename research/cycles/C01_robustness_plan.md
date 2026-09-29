# C01 robustness battery: pre-declared before any robustness run

**Written:** 2026-09-29. This comes after the IS screen results of the final comparable runs, and before any run below.

**Criteria** are the approved ones (CP2 report §6, D036). None is changed here.

## Which variations

- **IS screen at base cost** (final comparable runs, benchmark E901-05 over the same dates):
  - **Passed:** E005-10 (S005 v1.0), E005-11 (v1.1), E005-12 (v1.2).
  - **Failed:** all 16 variations of H001–H004.
- **Selection rule (C01 plan, step 3).** The best passing variation by net IS Sharpe carries the robustness battery. That is **E005-12** (Sharpe 1.44).
  - If E005-12 fails the 2× slippage screen item, the battery moves to the next best variation that passes, under new, separately declared IDs.

## 1. Completing the IS screen: Sharpe ≥ 0.4 at 2× slippage

| Run | Of | Change |
|---|---|---|
| E005-13 | E005-10 | slippage 20 bps per side |
| E005-14 | E005-11 | slippage 20 bps per side |
| E005-15 | E005-12 | slippage 20 bps per side |

## 2. Robustness gate for E005-12

| Test | Runs | Pass criterion (approved) |
|---|---|---|
| Cost stress | E005-16 (4×, 40 bps), E005-17 (6×, 60 bps) | Sharpe > 0 at 4×. 6× is reported only. |
| Parameter plateau, ±20–50% | vol_days 32 / 50 / 76 / 95: E005-18..21<br>slots 8 / 12: E005-22, E005-23<br>band 0.125 / 0.2 / 0.3 / 0.375: E005-24..27 | ≥ 80% of the 10 perturbations keep Sharpe ≥ 70% of the base Sharpe (1.438 → **≥ 1.007**) |
| Sub-periods | from E005-12 itself | Positive Sharpe in each third of IS |
| Stress episodes | from E005-12 itself (part of the screen) | As in the screen |

**Notes on the perturbations.**

- `slots` cannot go above 15, because 15 is the approved maximum number of positions (D041).
- At 8 slots the 10% cap per position binds, so about 80% at most is invested. That is how the approved rules behave.
- `require_positive_mom` is a switch, not a number, so it has no ±% perturbation. Its two settings are already compared by v1.0 versus v1.2.

## Reported but not a CP3 gate

- PBO and DSR belong to the **Validation** gate (CP2 §6, D036).
  - DSR is computed on IS + VAL combined.
  - PBO is computed on the IS returns of the hypothesis's variations.
- Both are reported at CP3 as known facts.

## Accounting

- All 15 runs are kind `research`, in cycle `C01-R` with `robustness_of`. They count as trials in the registry and are excluded from the variation comparison table.
- No Validation, Walk-Forward or Holdout run is part of this battery.
