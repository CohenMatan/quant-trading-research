# E005-28 — S005 v1.2 (research)

VALIDATION of frozen S005 v1.2 (H005), exactly as E005-12; accept/reject only (D042, D056)

- **Status:** completed
- **Split:** VAL (2018-01-01 → 2021-12-31)
- **Commit:** `e1dda07bc9d1f9119c2e64cb3ca78ced3ce28390` · **QC backtest:** `752e4e25e5e6665f3aaaf62c8afdc6c4` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T12:28:28Z · **runtime:** 281s
- **Parameters:** `{'vol_days': 63, 'slots': 15, 'band': 0.25, 'require_positive_mom': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2018-01-02 → 2021-12-31 (1008 trading days) |
| CAGR | 4.43% |
| Annualised volatility | 5.02% |
| Sharpe (rf = 0) | 0.89 |
| Sortino | 1.26 |
| Max drawdown | -6.47% |
| Longest drawdown (trading days) | 200 |
| Calmar | 0.68 |
| Worst year | -0.92% |
| Worst month | -3.64% |
| Closed trades | 174 |
| Win rate | 59.77% |
| Average winner | 4.61% |
| Average loser | -7.36% |
| Expectancy per trade | -0.21% |
| Profit factor | 0.91 |
| Average holding (calendar days) | 84.0 |
| Average exposure | 71.62% |
| Turnover (1-way, per year) | 2.61 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -12.54% | 0.16 | 0.65 |
| E901-05 | -7.83% | 0.15 | 0.63 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2018 | -0.92% |
| 2019 | 8.33% |
| 2020 | 2.46% |
| 2021 | 8.09% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 1008 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2018-01-02..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97737.11 |
| equity_complete | pass | chart rows 1008 vs algorithm days 1008 |
| equity_matches_qc_tradeable_dates | pass | chart rows 1008 vs QuantConnect tradeableDates 1008 |
| no_leverage | pass | min cash/equity 0.057476; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 47 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.5442039528933444e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 377 orders vs QuantConnect Total Orders 377 |
| fills_match_harness_count | pass | downloaded fill events 374 vs harness-recorded fills 374 |
| commission_fixed_per_order | pass | 374 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `6ae7555fcbe679119a26b5b75db4471737fe5c917182f35120c454eed26796df`
- fills_sha256: `a8e3555daf42eadb6d957ef09f148dc9379379a18cee4ee555c72fab4f1dd322`
- trades_sha256: `3dc7c6022ff6ba35c4b0a2e6e60acb42f62fa61c0dd006dde50d8ba3db50f0e4`
