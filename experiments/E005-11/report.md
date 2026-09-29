# E005-11 — S005 v1.1 (research)

C01 H005 S005 v1.1 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E005-02 under D051 with the D054 harness fix (replaces E005-08)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `a7c58943a0094ca8510d1f52219d48156a344bf2` · **QC backtest:** `f14c573316eb6ad5fa1691eb9c103a6d` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T09:41:12Z · **runtime:** 502s
- **Parameters:** `{'vol_days': 252, 'slots': 15, 'band': 0.25, 'require_positive_mom': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 10.40% |
| Annualised volatility | 8.29% |
| Sharpe (rf = 0) | 1.23 |
| Sortino | 1.82 |
| Max drawdown | -9.39% |
| Longest drawdown (trading days) | 153 |
| Calmar | 1.11 |
| Worst year | 2.43% |
| Worst month | -5.43% |
| Closed trades | 164 |
| Win rate | 62.80% |
| Average winner | 12.13% |
| Average loser | -6.19% |
| Expectancy per trade | 5.31% |
| Profit factor | 2.92 |
| Average holding (calendar days) | 221.2 |
| Average exposure | 82.81% |
| Turnover (1-way, per year) | 1.37 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -2.95% | 0.45 | 0.77 |
| E901-05 | -3.35% | 0.39 | 0.73 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 12.57% |
| 2011 | 12.61% |
| 2012 | 4.22% |
| 2013 | 18.04% |
| 2014 | 14.12% |
| 2015 | 2.43% |
| 2016 | 9.06% |
| 2017 | 10.79% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 98066.82 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.044871; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 5 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.6796259073508613e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 344 orders vs QuantConnect Total Orders 344 |
| fills_match_harness_count | pass | downloaded fill events 343 vs harness-recorded fills 343 |
| commission_fixed_per_order | pass | 343 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `89d8ad85c33a34d5a887e13470cda619a03a7912e352c759eb3e22a155909143`
- fills_sha256: `df993a301ddb75dc1b5b1a7cbe5333bae272dc1fd6aa599a6092dbe9762e2809`
- trades_sha256: `0c3335379b40254bf3e432053f0d46b4b4deedfb61317574f39f88ef29f8721b`
