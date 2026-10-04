# Owner message 2026-10-04: "Phase 4 — Design Cross-Sectional Technical Signal Validation Before Any Portfolio Backtest"

This is a recorded summary; the full message is in the session transcript.

## Decisions
- **P4-CP2 accepted** as the evidence basis for the next technical research step.
- **No return to a large technical-strategy optimizer.**
- The next step is **Cross-Sectional Technical Signal Validation**: first ask whether a very small number of pre-registered technical signals carry cross-sectional information about future returns, before any portfolio is built.
- **Design / methodology only.** No real signal-return result is to be computed yet.

## Content required
- **Signals:** exactly three.
  - S1 plain momentum (the reference, e.g. 12-1);
  - S2 smooth momentum;
  - S3 combined trend score.
- For S2 and S3: one academically defensible formula each, with its source, exact formula, lookback and rationale, frozen before results. Explain why alternatives were rejected. No competing definitions, no MA-set or weight optimisation.
- **No other indicators or overlays:** no RSI, MACD, ADX, Bollinger, volume, breakout, volatility filter, market regime, pullback, stops, trend exits or volatility scaling.
- **Universe:** US common stocks, market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M, using the existing point-in-time infrastructure.
- **Period:** 2010-01 / 2010-03 → 2017-12 (depending on warm-up). 2018–2021 is not accessed; the Holdout is locked under all circumstances.
- **Design choices to justify without using future signal returns:**
  - monthly vs weekly ranking (owner preference: monthly);
  - one primary future-return horizon, plus at most a few labelled diagnostics.
- **No portfolio:** no top-N selection, cash, sizing, commissions, exits or terminal wealth.
- **Primary tests:** quantile buckets, top-minus-bottom spread, rank IC (with the reason for the choice), and monotonicity.
- **Response, controls and inference:**
  - a market-relative or demeaned response variable;
  - sector treatment and size treatment (one primary interpretation each);
  - inference that respects cross-sectional, time-series and overlapping-return dependence;
  - an effective sample size and power (MDE at 50% and 80%) from synthetic or control data only.
- **History and incremental value:**
  - account for prior momentum work (H002, H008, Phase 3 momentum configurations and other related attempts);
  - plain momentum is a reference, not a new candidate;
  - an incremental-value test for S2 and S3 beyond plain momentum, chosen before results; keep it simple.
- **Stability:** year-by-year diagnostics and a few pre-declared subperiods.
- **Null and multiple testing:**
  - a cross-sectional null (e.g. a within-date permutation) that runs the full procedure;
  - one primary multiple-testing framework.
- **Pre-registration and promotion:**
  - a frozen, hashed pre-registration file before any results;
  - a multi-part promotion rule;
  - an economic-significance requirement;
  - turnover / implementability diagnostics.
- **Consequences** of "all fail" and "one passes", pre-registered.

## Deliverable
**P4-CP3 — Cross-Sectional Technical Signal Validation Architecture** (40 items + questions A–K).

## STOP conditions
- None of the following:
  - computing the real signals;
  - computing signal forward returns;
  - comparing quantiles;
  - computing IC;
  - running the null;
  - building a portfolio;
  - testing weekly exits;
  - volatility scaling;
  - market timing;
  - accessing 2018–2021 or the Holdout;
  - purchasing data.
- Allowed: verify the published definitions, use synthetic or control data for power, inspect infrastructure, design the methodology, estimate runtime, and write plumbing tests that expose no real signal performance.
- Commit P4-CP3, then STOP and wait for explicit approval before any real signal-validation run.
