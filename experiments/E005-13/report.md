# E005-13 — S005 v1.0 (research)

C01 robustness of E005-10: slippage 2x (20 bps/side) (pre-declared in research/cycles/C01_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `a317f54e8aac2e899d2deee21e74cdae2488347f` · **QC backtest:** `708acfd9ac77af00359831d247c6de9b` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T09:59:56Z · **runtime:** 428s
- **Parameters:** `{'vol_days': 63, 'slots': 15, 'band': 0.25, 'require_positive_mom': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate', 'slippage_stress_multiple': 2}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 7.45% |
| Annualised volatility | 5.79% |
| Sharpe (rf = 0) | 1.27 |
| Sortino | 1.87 |
| Max drawdown | -5.35% |
| Longest drawdown (trading days) | 126 |
| Calmar | 1.39 |
| Worst year | 1.93% |
| Worst month | -3.58% |
| Closed trades | 396 |
| Win rate | 61.62% |
| Average winner | 5.08% |
| Average loser | -3.87% |
| Expectancy per trade | 1.64% |
| Profit factor | 1.98 |
| Average holding (calendar days) | 77.2 |
| Average exposure | 68.70% |
| Turnover (1-way, per year) | 3.12 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -5.90% | 0.31 | 0.77 |
| E901-05 | -6.30% | 0.28 | 0.74 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 9.66% |
| 2011 | 11.54% |
| 2012 | 5.01% |
| 2013 | 16.14% |
| 2014 | 6.57% |
| 2015 | 3.90% |
| 2016 | 1.93% |
| 2017 | 5.37% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97927.72 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.065703; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 73 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.219693434445196e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 804 orders vs QuantConnect Total Orders 804 |
| fills_match_harness_count | pass | downloaded fill events 804 vs harness-recorded fills 804 |
| commission_fixed_per_order | pass | 804 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `cba598ca1ef438fe513984cb3c1cac80762778e9ed11fe6f0bd6632365bf73ed`
- fills_sha256: `5ef1a99235e4f1d0229d885dc3e569bb3a5085e51461aa3bf82fe8b47f6f484c`
- trades_sha256: `e3ebeb1e62c171de5835ad6219cd184c02a2905b8bd11b09b160aab6aabc275c`
