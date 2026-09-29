# E001-06 — S001 v1.0 (research)

C01 H001 S001 v1.0 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E001-01 under D051 (no borrowing)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `2447f3200979d65c8664b30c75809ef13d08e20a` · **QC backtest:** `c91125551ec333aad149eae699ded5c1` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T14:53:52Z · **runtime:** 381s
- **Parameters:** `{'entry': 'rsi', 'rsi_max': 10, 'exit': 'sma5', 'max_hold': 10, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 1.75% |
| Annualised volatility | 13.95% |
| Sharpe (rf = 0) | 0.19 |
| Sortino | 0.27 |
| Max drawdown | -31.09% |
| Longest drawdown (trading days) | 752 |
| Calmar | 0.06 |
| Worst year | -17.63% |
| Worst month | -11.31% |
| Closed trades | 1638 |
| Win rate | 55.80% |
| Average winner | 1.65% |
| Average loser | -2.58% |
| Expectancy per trade | -0.22% |
| Profit factor | 0.81 |
| Average holding (calendar days) | 5.9 |
| Average exposure | 67.31% |
| Turnover (1-way, per year) | 12.06 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-05 | -11.60% | 0.80 | 0.82 |
| E901-04 | -12.00% | 0.78 | 0.86 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 6.10% |
| 2011 | -17.63% |
| 2012 | 8.88% |
| 2013 | 14.92% |
| 2014 | 4.65% |
| 2015 | -12.82% |
| 2016 | 6.80% |
| 2017 | 7.77% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 79238.56 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.027907; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 1 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.092280125712233e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 3291 orders vs QuantConnect Total Orders 3291 |
| fills_match_harness_count | pass | downloaded fill events 3287 vs harness-recorded fills 3287 |
| commission_fixed_per_order | pass | 3287 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `116c539fc16ac7e87e6c05bcf897186ea68aaefdbd7674d09586bae5ea4ac6f5`
- fills_sha256: `dc93710eefa63bc73039f8e1816cd4e5f787d91022034816fe5cb7bded8a6c2b`
- trades_sha256: `5314525ab3dcba8930064713b0b5cef5a3210493fa59a70633976c53044217ab`
