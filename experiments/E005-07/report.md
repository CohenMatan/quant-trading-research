# E005-07 — S005 v1.0 (research)

C01 H005 S005 v1.0 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E005-01 under D051 (no borrowing); retry of E005-04 (operational failure, D053)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `a9295d04c94bb94fadb3764a059cd264a8651f16` · **QC backtest:** `ceafed5f36d88f1411003215213918f3` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T06:41:12Z · **runtime:** 367s
- **Parameters:** `{'vol_days': 63, 'slots': 15, 'band': 0.25, 'require_positive_mom': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 8.06% |
| Annualised volatility | 5.78% |
| Sharpe (rf = 0) | 1.37 |
| Sortino | 2.03 |
| Max drawdown | -5.30% |
| Longest drawdown (trading days) | 114 |
| Calmar | 1.52 |
| Worst year | 2.53% |
| Worst month | -3.52% |
| Closed trades | 396 |
| Win rate | 63.38% |
| Average winner | 5.13% |
| Average loser | -3.87% |
| Expectancy per trade | 1.83% |
| Profit factor | 2.14 |
| Average holding (calendar days) | 77.2 |
| Average exposure | 68.69% |
| Turnover (1-way, per year) | 3.12 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-05 | -5.28% | 0.31 | 0.77 |
| E901-04 | -5.68% | 0.28 | 0.75 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 10.21% |
| 2011 | 12.16% |
| 2012 | 5.67% |
| 2013 | 16.85% |
| 2014 | 7.27% |
| 2015 | 4.52% |
| 2016 | 2.53% |
| 2017 | 5.85% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 98149.72 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.065455; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 73 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3862034721872065e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 804 orders vs QuantConnect Total Orders 804 |
| fills_match_harness_count | pass | downloaded fill events 804 vs harness-recorded fills 804 |
| commission_fixed_per_order | pass | 804 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `9a2b45b932ed4e129a2645b6cc9cd215b59daef9dbc09c87a64d41ef352110d1`
- fills_sha256: `2a6acfef29db08a68637c1e60028d0847e0967971bc46a46b7ecc34448df2591`
- trades_sha256: `1de2dc7615fb8a240a8569bc11fbb00ea6bbcde4c0c105eae2a6af4b795dd7ea`
