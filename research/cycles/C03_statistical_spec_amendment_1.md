# C03 statistical specification: Amendment 1 (D087), owner-approved 2026-09-30

| Field | Value |
|---|---|
| Amends | `research/cycles/C03_statistical_spec.md` (D082, frozen). That file is **unchanged** and its hash stays pinned. This amendment is added beside it and has its own pinned hash. |
| Approved by | Owner, "C03 — Final Decisions and Conditional Execution Approval", 2026-09-30 |
| Made | Before any C03 strategy backtest. No C03 result exists. |
| Reason | H012 is removed from C03 as **not evaluable with sufficient statistical power using the currently available data** (`docs/checkpoints/CP3h_H012_power_reassessment.md`, D086). None of its planned strategy experiments will occur. |

## What changes

1. **Official N at the C03 evaluation = 40**:
   - the 37 selection candidates from before C03;
   - the 3 pre-declared H013 variations (v1.0, v1.1, v1.2).

   It is still counted from the registry by the unchanged formula (official N = number of selection candidates). The C03 evaluation still stops with an error if the registry does not give exactly this value, which is now **40 instead of 43**.
2. **Sensitivity diagnostic at N = 43,** the originally planned count, reported for every book beside the official and conservative DSR.
   - It is **not** a gate and does not replace either requirement.
   - The same Sharpe dispersion and the same return series are used.
3. **Conservative N:** the approved formula is unchanged (selection + replicate + robustness + Validation, from the registry). Only the H012 experiments that will no longer occur drop out.
   - Before C03: 64.
   - After the 9 committed H013 selection runs: **64 + 3 + 6 = 73**.
   - Upper bound with every pre-declared H013 conditional run: 73 + 9 (2× slippage, 3 variations × 3 seeds) + 18 (the robustness battery of the chosen variation, per seed) + 3 (Validation, 3 seeds) = **103**.

## What does not change

- **DSR ≥ 0.90** at both the official and the conservative N, on every deployable book (each H013 seed separately).
- The return series, frequency, moments, trial-count formulas, Sharpe dispersion and evaluation timing (spec §2–§3).
- **PBO** stays diagnostic only. For H013 it runs over the 3 variations, using the seed-averaged series.
- **H013:** all three seeds must pass every stage; no averaging for acceptance; no seed selection.
- All screening, robustness and Validation thresholds.

## H012 status (recorded, not a test result)

- **H012 is not evaluable with sufficient statistical power using the currently available data.** It is **not** a failed trading hypothesis: its trading performance was never evaluated.
- Its specification, controls, configurations (E012-01..11, withdrawn and never run), the canaries, the simulation studies and the decision history are all preserved.
- It may be reconsidered in a future project as a portfolio risk-management overlay, if a suitable underlying strategy exists.
