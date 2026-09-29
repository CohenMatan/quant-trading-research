# E002-08 — S002 v1.3 (research)

C01 H002 S002 v1.3 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E002-04 under D051 (no borrowing)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `d2ebb3c716db471be1496c8608944c7856f3c40f` · **QC backtest:** `5b7cbf35d95468227651008c89f2c032` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T15:53:43Z · **runtime:** 412s
- **Parameters:** `{'lookback': 252, 'skip': 21, 'every_months': 2, 'slots': 15, 'band': 0.25, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 5.69% |
| Annualised volatility | 19.64% |
| Sharpe (rf = 0) | 0.38 |
| Sortino | 0.52 |
| Max drawdown | -37.85% |
| Longest drawdown (trading days) | 968 |
| Calmar | 0.15 |
| Worst year | -9.49% |
| Worst month | -12.23% |
| Closed trades | 225 |
| Win rate | 49.33% |
| Average winner | 26.18% |
| Average loser | -17.64% |
| Expectancy per trade | 3.98% |
| Profit factor | 1.22 |
| Average holding (calendar days) | 124.2 |
| Average exposure | 62.67% |
| Turnover (1-way, per year) | 1.74 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-05 | -7.65% | 0.92 | 0.67 |
| E901-04 | -8.05% | 0.93 | 0.73 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 28.72% |
| 2011 | -9.17% |
| 2012 | 14.33% |
| 2013 | 15.66% |
| 2014 | -9.49% |
| 2015 | -1.32% |
| 2016 | -0.54% |
| 2017 | 13.27% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97261.82 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.098316; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 13 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.955482056239172e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 508 orders vs QuantConnect Total Orders 508 |
| fills_match_harness_count | pass | downloaded fill events 508 vs harness-recorded fills 508 |
| commission_fixed_per_order | pass | 508 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `12ad422ea0b2d3e491936e3359cb631bd8a72bc760523c67f329485855cb2440`
- fills_sha256: `0d4442a60f6de5eaaad1c974db89ade9f96dfd7352454309f067d8ebf0ffad1e`
- trades_sha256: `7a34d3948695127227877b77e26f246aca88089ec13caa66ce55d7357329bb05`
