# E002-07 — S002 v1.2 (research)

C01 H002 S002 v1.2 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E002-03 under D051 (no borrowing)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `a19f4a4b5d184c34c3286fb4be8feebfa25cf80e` · **QC backtest:** `b752e59918f9f7530489274b28c1ce5f` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T15:46:32Z · **runtime:** 413s
- **Parameters:** `{'lookback': 252, 'skip': 21, 'every_months': 1, 'slots': 15, 'band': 0.25, 'regime_filter': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 9.20% |
| Annualised volatility | 19.14% |
| Sharpe (rf = 0) | 0.56 |
| Sortino | 0.76 |
| Max drawdown | -30.80% |
| Longest drawdown (trading days) | 361 |
| Calmar | 0.30 |
| Worst year | -7.30% |
| Worst month | -13.97% |
| Closed trades | 342 |
| Win rate | 54.97% |
| Average winner | 19.03% |
| Average loser | -14.27% |
| Expectancy per trade | 4.04% |
| Profit factor | 1.47 |
| Average holding (calendar days) | 82.0 |
| Average exposure | 62.25% |
| Turnover (1-way, per year) | 2.65 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-05 | -4.14% | 0.77 | 0.58 |
| E901-04 | -4.54% | 0.78 | 0.63 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 5.27% |
| 2011 | 1.56% |
| 2012 | 26.15% |
| 2013 | 18.37% |
| 2014 | -7.30% |
| 2015 | 13.10% |
| 2016 | 11.12% |
| 2017 | 8.58% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 93298.71 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.115386; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 15 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.0818751887864673e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 758 orders vs QuantConnect Total Orders 758 |
| fills_match_harness_count | pass | downloaded fill events 758 vs harness-recorded fills 758 |
| commission_fixed_per_order | pass | 758 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `1e1b4c17eca485db6674c6f2309d73b4abb7e390b6f5af36d099591f25f4bc42`
- fills_sha256: `129436113b78e83ddfae2b4f1d1432f00c1b076d3ecdbf55d07cbfa9b784c6c9`
- trades_sha256: `270464a8c1762c973b83a51c50d8705f20c126be9b7927493157d262aad9f66e`
