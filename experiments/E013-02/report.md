# E013-02 — S013 v1.0 (research)

C03 H013 S013 v1.0 seed 2 (one candidate per variation; seeds are replicates, D082) on IS, paired with null E962-23. Pre-declared in docs/checkpoints/CP3e_C03_final_plan.md §7; methodology research/cycles/C03_statistical_spec.md (D082).

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `cd76d2c9aa4422c1834f261c0e05d71e9ad80cb9` · **QC backtest:** `318343734707f52d3d7679445786824c` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T15:38:56Z · **runtime:** 623s
- **Parameters:** `{'q': 0.2, 'stat': 'max', 'seed': 2, 'slots': 15, 'hold': 60}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 10.87% |
| Annualised volatility | 13.61% |
| Sharpe (rf = 0) | 0.83 |
| Sortino | 1.16 |
| Max drawdown | -19.47% |
| Longest drawdown (trading days) | 273 |
| Calmar | 0.56 |
| Worst year | -1.63% |
| Worst month | -9.22% |
| Closed trades | 482 |
| Win rate | 62.45% |
| Average winner | 9.87% |
| Average loser | -9.82% |
| Expectancy per trade | 2.47% |
| Profit factor | 1.58 |
| Average holding (calendar days) | 87.8 |
| Average exposure | 83.85% |
| Turnover (1-way, per year) | 3.56 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -2.47% | 0.85 | 0.90 |
| E901-07 | -3.05% | 0.81 | 0.92 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 19.17% |
| 2011 | -1.63% |
| 2012 | 17.53% |
| 2013 | 27.01% |
| 2014 | 8.72% |
| 2015 | 3.73% |
| 2016 | 9.51% |
| 2017 | 5.48% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97343.93 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.099582; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 6 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3084730965147665e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 979 orders vs QuantConnect Total Orders 979 |
| fills_match_harness_count | pass | downloaded fill events 979 vs harness-recorded fills 979 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 979 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `37f59f536a351880aa2706159c2fd2e9e98688287ce818d2714be2e9aad7f6e9`
- fills_sha256: `018a9f0287aef745a87da1fe59001e107d46d5c7340a7196462636d89401ce05`
- trades_sha256: `a74b054a6b028b6d9e5cb805b393e49fdb2e7fa15afe5019b9d9c02e23ad882b`
