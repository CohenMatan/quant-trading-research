# E006-03 — S006 v1.2 (research)

C02 H006 S006 v1.2 (pre-declared selection candidate, D069) on IS 2010-2017: no volume condition

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `f4d90481e2a7dc71184daf4427b175d9274b2749` · **QC backtest:** `9324b258834d57c1989449f4b3884416` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T20:34:53Z · **runtime:** 915s
- **Parameters:** `{'n': 55, 'vol_mult': 1.5, 'use_volume': False, 'k': 3.0, 'time_stop': 60, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 12.35% |
| Annualised volatility | 13.97% |
| Sharpe (rf = 0) | 0.90 |
| Sortino | 1.27 |
| Max drawdown | -22.73% |
| Longest drawdown (trading days) | 399 |
| Calmar | 0.54 |
| Worst year | -12.89% |
| Worst month | -9.55% |
| Closed trades | 517 |
| Win rate | 47.00% |
| Average winner | 9.57% |
| Average loser | -5.56% |
| Expectancy per trade | 1.55% |
| Profit factor | 1.53 |
| Average holding (calendar days) | 53.2 |
| Average exposure | 91.40% |
| Turnover (1-way, per year) | 6.08 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -0.99% | 0.70 | 0.72 |
| E901-07 | -1.58% | 0.67 | 0.74 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 9.09% |
| 2011 | -12.89% |
| 2012 | 21.15% |
| 2013 | 41.68% |
| 2014 | 2.45% |
| 2015 | 6.97% |
| 2016 | 11.31% |
| 2017 | 27.33% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 91346.50 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.026949; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 14 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.0818751887864673e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1044 orders vs QuantConnect Total Orders 1044 |
| fills_match_harness_count | pass | downloaded fill events 1043 vs harness-recorded fills 1043 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1043 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `a0abf5b303fe1b383ef27af2ebcebff5cd0cbfcbefce351abe67b3513d93d000`
- fills_sha256: `949af2634cbc6e4da1ef94cb1763bc575412d2e6f18569e9d7bc0f96292c188e`
- trades_sha256: `5263ae305884632dcaf23fcabc1f938a710df2765963bba172f8a5e52ef6f466`
