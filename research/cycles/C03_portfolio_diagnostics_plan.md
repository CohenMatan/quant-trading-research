# C03 portfolio-structure diagnostics: pre-registration

| Field | Value |
|---|---|
| Written | 2026-09-30, **before any diagnostic run** (owner instruction 2026-09-30, item 2) |
| Purpose | Measure how portfolio size, account size and holding period affect a portfolio **with no stock-picking skill**, under exactly the rules C01 and C02 faced. **Diagnosis of portfolio construction, not a strategy search.** |
| Status of runs | Verification diagnostics: kind `infrastructure`. **Not trials** (D069); no selection, no signal, no gate changes. |
| Period and data | IS 2010-01-04 → 2017-12-29, the approved ≥ $2B US-common universe. No Validation, Walk-Forward or Holdout data. |

## 1. The no-skill portfolio (X962)

- **Rules** (`strategies/X962_random_pick/`):
  - Every close, sell any holding held `hold` sessions.
  - Fill the empty slots with eligible stocks in a random order fixed by (seed, session).
  - Selection uses **no price or volume data**.
- **Unchanged harness rules**, identical to C02:
  - next-open execution; $7 per order; 10 bps slippage per side;
  - no borrowing (D051), 2% cash buffer, 15% gap reserve;
  - $5,000 minimum position; stale-holding and delisting rules (D054, D062).
- **Benchmarks** for the same dates:
  - equal-weight ≥ $2B universe, E901-07 (Sharpe 0.92);
  - SPY buy-and-hold, E900-07 (Sharpe 0.95).
- **Tests** (`tests/test_portfolio_diagnostics.py`):
  - seeded determinism, and the result does not depend on input order;
  - no price input; next-open orders only;
  - the configuration grid changes one factor at a time.

## 2. Configurations (24 runs, fixed now)

Seeds 1, 2 and 3 for every cell, so seed-to-seed spread is measured rather than assumed.

| Series | Factor varied | Cells | Runs |
|---|---|---|---|
| **S: portfolio size** | slots 10 / 15 / 19 at $100K, hold 20 | 3 | E962-01..09 |
| **A: account size** | $250K / $1M at 15 slots, hold 20 ($100K cell shared with S) | 2 | E962-10..15 |
| **B: breadth a larger account allows** | 30 slots at $250K, hold 20 (compare with A's $250K / 15 slots) | 1 | E962-16..18 |
| **H: holding period** | hold 5 / 60 at 15 slots, $100K (hold-20 cell shared with S) | 2 | E962-19..24 |

- **Why these values:**
  - 10 slots is the C02 standard; 15 is C01's maximum; 19 is the largest count the $5,000 minimum allows at $100K.
  - $250K and $1M separate the fixed $7 commission and the minimum-position limit from everything else.
  - Hold 20 is close to C02's typical holding period; 5 and 60 bracket C01/C02.
- The **base cell** (15 slots, $100K, hold 20) appears once, and each series changes one factor from it or from its partner cell.
- **Budget:** 24 runs plus at most 4 technical retries or recoveries (D077) = **28 QuantConnect backtests at most**. At about 20 minutes each that is about 8–9 hours of node time, within the existing subscription, with no new spending.

## 3. Metrics (computed by `research/cycles/C03_diagnostics_eval.py`, committed now)

For each run, and per cell as the mean and the range over the 3 seeds:

- **Performance:** CAGR, Sharpe, max drawdown, volatility.
- **Costs:** commission and slippage as % of equity per year; turnover.
- **Exposure:** average fraction invested; idle cash; average number of positions.
- **Diversification:** correlation and beta to equal-weight; idiosyncratic volatility, vol × √(1 − ρ²).
- **Relative performance:**
  - Sharpe minus equal-weight Sharpe;
  - alpha against equal-weight (with t-statistic);
  - Sharpe of equal-weight held at the same exposure;
  - SPY Sharpe.

## 4. Pre-registered readings (descriptive; none changes a gate)

- **R1 Diversification.** Δ mean Sharpe between 19 and 10 slots at $100K. It is called material only if Δ > 0.10 **and** Δ exceeds half of the larger within-cell seed range.
- **R2 Account size.** Commission and total cost at $100K, $250K and $1M, and Δ Sharpe from $1M to $100K, at 15 slots.
- **R3 Structural handicap** in the C02 setting (10 slots, $100K, hold 20): equal-weight Sharpe minus no-skill Sharpe. This is the part of the "Sharpe ≥ EW + 0.10" bar that a skill-less portfolio of our structure fails to reach.
- **R4 Holding-period cost curve.** Cost % per year and Sharpe at hold 5 / 20 / 60.
- **R5 Breadth with a larger account.** Δ Sharpe from 30 slots to 15 slots at $250K; idiosyncratic volatility of each.

## 5. What may and may not follow from the results

- **May follow (only as proposals, each needing owner approval before any C03 strategy result exists):**
  - the number of slots C03 strategies use;
  - whether a larger research account should be considered;
  - holding-period guidance for cost control;
  - reporting a matched no-skill reference next to every C03 result.
- **May not follow:**
  - any change to the screen thresholds, the DSR/PBO rules (D069, D073), the cost model or the universe;
  - any tuning of a signal. The diagnostics contain no signal.
- **Multiple testing.** These runs select nothing among signals, so they do not enter the DSR trial count. A portfolio-structure choice for C03 (e.g. slots) made from them is fixed **before** C03 results and applies equally to all C03 strategies. It is recorded as a decision and disclosed in every C03 report. If a structure choice were made after seeing C03 strategy results, each structure tried would have to be counted as a separate trial. That is not permitted here.
- **All results are kept**, including unfavourable ones, and reported in full.
