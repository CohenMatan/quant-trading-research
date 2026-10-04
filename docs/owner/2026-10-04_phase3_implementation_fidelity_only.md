# Owner message 2026-10-04: "Phase 3 — Approve Architecture Direction, Authorise Implementation/Fidelity Only, and Freeze the Search Before Any Strategy Sweep"

This is a recorded summary; the full message is in the session transcript.

## Approved

- The general P3-CP1 architecture direction.
- The constrained grammar: 1 primary + at most 1 confirmation from a different family + at most 1 volatility filter.
- About 1,533 Stage-1 configurations.
  - The spec must record every family, parameter, value, structure and exclusion.
  - **No additions after the search begins.**
- The partition, in principle.

## Required design work before any search

### Null calibration
- **Repetitions:** target 200–500, prefer 500.
- **Report:** the number of repetitions, the number passing the full pipeline, the false-pass rate, and a binomial CI. No bare point estimates.
- **The null must preserve market structure:** regimes, cross-sectional correlation, volatility clustering, autocorrelation, universe changes, delistings, corporate actions, common shocks, signal frequency and portfolio constraints.
- **It must break only the signal → future-return link.**
- **Document:**
  - what is randomised and what is preserved;
  - an evaluation of within-date, block, signal-label and circular-shift nulls.
- **Choose ONE primary null before results.** Secondary nulls are diagnostics only; no cherry-picking.

### Frozen architecture
- **Freeze:** 63 sessions, 10 positions, $100K, $7 + $7, 10 bps, no leverage. Do not optimise H.
- **126-day / 20-position architecture:** must not be a rescue path. Give a frozen trigger, or remove it.
- **Walk-forward:**
  - document how it interacts with the search;
  - 2014–2017 must not become an informal tuning set;
  - the walk-forward tests the procedure; never redesign after it.
- **Internal OOS:** 2018–2021 is used exactly once, for one frozen candidate. If it fails, it fails.

### Precise definitions to freeze
- **Plateau:** neighbour, minimum neighbours, boundary, minimum cluster size, connectivity, cluster score, centre.
- **Simplicity rule:** lexicographic preferred.
- **Stage-1 score:** hierarchical / gate-based, with no arbitrary weights.
- **Search null:** must run the ENTIRE optimizer and use the distribution of the full optimizer's best result.
- **Controls:** the primary control is the empirical full-search null. Secondary methods (SPA / DSR / PBO) only where useful; do not stack methods.
- **Promotion:** a finite budget with exact meanings; no discretionary finalist.

## Fast engine
- **Build it inside QuantConnect / LEAN.**
- **Fidelity:** it must reproduce previously completed controls within pre-declared tolerances, covering:
  - daily returns, final value, trade count;
  - entries and exits, cash, commissions, slippage;
  - delistings, splits and dividends, sizing.
- **Tolerances must be defined before testing.**
- **If it materially disagrees: STOP.** Do not calibrate away discrepancies with candidate strategies.

## Runtime / memory canary
- Infrastructure only, with dummy or null configurations.
- **Establish:**
  - the maximum configurations per run, memory, runtime, output size and QC limits;
  - whether 1,533 configurations fit;
  - deterministic batching if needed.

## Authorised to build
- Indicator computation, the grammar generator and configuration ids.
- The fast engine and the cost / accounting model.
- The plateau detector and the simplicity selector.
- The walk-forward and null frameworks.
- The fidelity harness, the runtime canary and tests.

## Not authorised
- No real 2010–2017 configurations through the optimizer.
- No technical strategy returns (MA / RSI / MACD performance, rankings, heatmaps).
- No Holdout, not even for fidelity or runtime tests.
- No paid data.

## Required outputs
1. **A frozen, hash-pinned spec** covering:
   - the data split, families, grids, grammar and exact count;
   - holding, positions and mechanics;
   - the score, plateau, cluster rule and simplicity rule;
   - the null method, number of nulls and threshold;
   - the walk-forward, promotion limits and internal-OOS rule;
   - the LEAN verification requirements, robustness requirements and Holdout criteria.
2. **Checkpoint P3-CP2 — Technical Search Engine Implementation, Null Calibration Design and Fidelity Readiness** (30 items), ending with the verdict "READY FOR PHASE 3 SEARCH" or "NOT READY".

## STOP
- After implementation, the null-framework infrastructure and fidelity validation: **STOP**.
- Do not start the real search or evaluate the 1,533 configurations on real returns.
- No 2018–2021 access, no Holdout, no purchase.
- **Wait for explicit approval before the first real Phase 3 search run.**
