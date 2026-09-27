# RESEARCH_PLAN.md

**Status: DRAFT, pending Checkpoint 1 approval.** Sections marked *(TBD at CP2)* will be completed before the first research campaign and require owner approval.

## 1. Objective

Identify at most one simple, explainable, robust long-only swing-trading strategy on US equities with point-in-time market cap ≥ $2B that passes every validation stage below. Otherwise, report **"No Production Candidate Found"**.

## 2. Universe (fixed across all strategies)

- US-listed common stocks with Morningstar fundamentals on QuantConnect. This excludes ETFs, ADRs and OTC stocks.
- Eligible on day T if the point-in-time `MarketCap` on day T is **≥ $2B nominal**. An inflation-adjusted threshold will be used only as a robustness check.
- Tradability filters: a minimum price and a minimum dollar volume. *(Exact values TBD at CP2. They are fixed once and never tuned per strategy.)*
- The universe is rebuilt daily from securities that existed on that day, including ones that later delisted.

## 3. Data split

| Segment | Dates | Use |
|---|---|---|
| IS (Research/Training) | 1999-01-04 → 2014-12-31 | Exploration; choosing among a few pre-declared variations |
| VAL (Validation) | 2015-01-01 → 2021-12-31 | One frozen-parameter pass per promoted candidate; walk-forward evaluation |
| **HOLDOUT** | **2022-01-01 → 2026-08-31** | Once, after CP5 approval, frozen strategies only |

Indicator warm-up uses data before each segment's start. Warm-up bars never generate trades.

The **holdout lock** works as follows:

- The runner rejects any end date after 2021-12-31 unless `HOLDOUT_UNLOCK.md` exists.
- That file is created only after owner approval at CP5, and records the frozen commits.

## 4. Execution model

- The signal uses day T's completed daily bar. The order is **market-on-open on T+1**.
- Long-only, cash account, no leverage.
- Position sizing is defined per strategy, within fixed portfolio constraints *(TBD at CP2)*.
- Costs:
  - Interactive Brokers–style per-share commissions.
  - Base slippage of X bps per side *(TBD at CP2)*.
  - Stress runs at 2×, 4× and 6× the base slippage.
- Corporate actions: fills use raw prices, dividends are credited as cash, signals use adjusted history. Delistings liquidate at the last price, which is noted as a limitation.
- Assumed account size: $100,000 *(pending owner confirmation)*.

## 5. Research loop

```
Hypothesis (H###) → Strategy (S###) → Exploration on IS (3–10 variations)
  → Analysis → Reject / Continue
  → Robustness on IS (parameter plateau, sub-periods, regimes, costs, trade distribution)
  → Validation (VAL, frozen) → Walk-forward (1999–2021, pre-declared selection rule)
  → Realistic LEAN checks → CP4 → Freeze → CP5 approval → HOLDOUT once
  → Production Candidate / Reject
```

## 6. Metrics (computed locally from the equity curve and trades)

- CAGR, annualized return, and annualized volatility.
- Max drawdown and its duration.
- Sharpe, Sortino and Calmar ratios.
- Profit factor, win rate, average winner, average loser and expectancy.
- Number of trades, average holding period, exposure and turnover.
- Worst year, worst month, and performance by year.
- Benchmark-relative figures: excess CAGR, beta and correlation.
- Multiple-testing indicators:
  - **Deflated Sharpe Ratio**, using the registry's trial count.
  - **Probability of Backtest Overfitting**, using CSCV across a hypothesis's variations.
  - IS→VAL degradation.

Benchmarks:

- SPY buy-and-hold, total return.
- Equal-weight buy-and-hold of the ≥$2B universe.

## 7. Robustness battery

- **Parameter stability:** ±20–50% perturbations around the chosen parameters. We need a plateau, not a single peak.
- **Time stability:** sub-period and per-year results.
- **Regimes:**
  - Bull and bear markets, defined by SPY relative to its 200-day moving average and by drawdown periods.
  - High and low volatility, defined by realized-volatility terciles.
  - Named episodes: 2000–02, 2008–09, 2011, 2015–16, 2018 Q4, 2020, and 2022 (holdout only).
- **Costs:** slippage stress at 2×, 4× and 6× the base; also a higher commission assumption.
- **Trade distribution:**
  - Share of profit from the top 1%, 5% and 10% of trades.
  - Performance with the best N trades removed.
  - A bootstrap confidence interval on expectancy.

## 8. Promotion gates

Exact numerical thresholds are **deliberately not yet defined**, per the owner's instruction. Before the first campaign, Claude will propose screening criteria at CP2, and the owner will approve them. Gates will then be fixed *before* the data they apply to is examined.

## 9. Research budget (first campaign)

- Tens of hypotheses, 3–10 variations each, and at most a few hundred experiments.
- Any substantial expansion must be justified to the owner first.

## 10. Hindsight control

Every hypothesis must cite a rationale that does not depend on knowledge of post-2014 market events. Validation-era and holdout-era events may not motivate new hypotheses.
