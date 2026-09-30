# E013-04 — S013 v1.1 (research)

C03 H013 S013 v1.1 seed 1 (one candidate per variation; seeds are replicates, D082) on IS, paired with null E962-22. Pre-declared in docs/checkpoints/CP3e_C03_final_plan.md §7; methodology research/cycles/C03_statistical_spec.md (D082).

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `fffaf852ba065e410c7deada66e679b76d3ae5a6` · **QC backtest:** `9375bfdcd16d291487a593a8b92c91dd` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T15:57:49Z · **runtime:** 409s
- **Parameters:** `{'q': 0.1, 'stat': 'max', 'seed': 1, 'slots': 15, 'hold': 60}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 9.70% |
| Annualised volatility | 14.75% |
| Sharpe (rf = 0) | 0.70 |
| Sortino | 1.00 |
| Max drawdown | -24.68% |
| Longest drawdown (trading days) | 464 |
| Calmar | 0.39 |
| Worst year | -6.75% |
| Worst month | -11.54% |
| Closed trades | 481 |
| Win rate | 58.21% |
| Average winner | 10.62% |
| Average loser | -9.14% |
| Expectancy per trade | 2.37% |
| Profit factor | 1.56 |
| Average holding (calendar days) | 88.1 |
| Average exposure | 83.95% |
| Turnover (1-way, per year) | 3.55 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -3.64% | 0.93 | 0.91 |
| E901-07 | -4.22% | 0.89 | 0.93 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 18.39% |
| 2011 | -6.75% |
| 2012 | 9.06% |
| 2013 | 28.95% |
| 2014 | 11.52% |
| 2015 | -1.83% |
| 2016 | 9.17% |
| 2017 | 12.89% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97441.22 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.109289; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 5 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.757220605304979e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 978 orders vs QuantConnect Total Orders 978 |
| fills_match_harness_count | pass | downloaded fill events 976 vs harness-recorded fills 976 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 976 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `3fb1daf41d3b3e5bf7886e7cbaee898d61c4feff709c9a0a24cf4603cf040c4d`
- fills_sha256: `102e98cbf1df848095e879f015895b4b3502fd356842ad32ff969064932c6cc7`
- trades_sha256: `c2b549be23edec77d347dedca2543e3c1e3cccb08a7cd74aebeecc804ff5c446`
