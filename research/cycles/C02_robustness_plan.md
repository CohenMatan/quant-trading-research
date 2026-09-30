# C02 robustness procedure: pre-declared before any robustness run

**Written:** 2026-09-30, after the C02 IS screen (`C02_is_results.csv`, `C02_is_gates.json`) and before any run below.

It follows the approved C02 plan (§5, §8), the approved gates (D036) and the perturbations already written in `research/hypotheses/H007.md`. **Nothing here is new or tuned.**

## Which variation

- **IS screen at base cost:** 1 of 18 selection candidates passes all screen items: **E007-02 (H007 v1.1**, contraction measured as ATR10/ATR100 ≤ 0.6). Sharpe 1.117; the equal-weight benchmark E901-07 has 0.920 over the same dates.
- The 17 others fail. Every one fails "Sharpe ≥ EW + 0.10", and most fail further items.
- Only one hypothesis qualifies, so the cap of "at most 2 hypotheses" does not bind.

## Step 1: complete the IS screen, Sharpe ≥ 0.4 at 2× slippage

| Run | Change |
|---|---|
| E007-04 | slippage 20 bps per side (2×) |

**If E007-04 fails, stop.** H007 then fails the screen, no robustness battery runs, and C02 has no qualifying variation.

## Step 2: robustness gate (only if step 1 passes)

| Test | Runs | Pass criterion (approved, unchanged) |
|---|---|---|
| Cost stress | E007-05 (4×, 40 bps), E007-06 (6×, 60 bps) | Sharpe > 0 at 4×; 6× reported only |
| Parameter plateau (H007.md, v1.1) | ATR ratio 0.6 → 0.3 / 0.48 / 0.72 / 0.9: E007-07..10<br>time stop 40 → 20 / 32 / 48 / 60: E007-11..14 | ≥ 80% of the 8 perturbations (at least 7) keep Sharpe ≥ 70% of the base Sharpe (1.117 → **≥ 0.782**) |
| Sub-periods | from E007-02 itself | Positive Sharpe in each third of IS: 1.19 / 1.06 / 1.17 (known already, **passes**) |

## Accounting and limits

- **Runs:** 11 at most, so C02's total is 29 of the 56-backtest cap.
- **Recording:** all runs are kind `research`, cycle `C02-R`, `robustness_of: E007-02`.
  - Under D069 they are **robustness** runs. They are not selection candidates, so they are not in the DSR's N (which stays 37), and not in the cycle-level PBO.
  - They are counted in the conservative trial count.
- **Scope:** no Validation, Walk-Forward or Holdout run. Nothing is changed after seeing these results.
- **Disclosed now, before step 1, and not a gate:** E007-02 was on average only about 21% invested, and its CAGR is 5.4%. Its high Sharpe comes with low exposure. This must be read with the exposure-aware comparison (C02 plan §7). The C02 checkpoint will report it prominently.
