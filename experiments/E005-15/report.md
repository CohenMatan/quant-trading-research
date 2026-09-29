# E005-15 — S005 v1.2 (research)

C01 robustness of E005-12: slippage 2x (20 bps/side) (pre-declared in research/cycles/C01_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `1fcee93c7216d4e563b05f04e48a2eb67c26148d` · **QC backtest:** `710c2827c68af63761d25daf3e47b55b` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T10:14:13Z · **runtime:** 430s
- **Parameters:** `{'vol_days': 63, 'slots': 15, 'band': 0.25, 'require_positive_mom': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate', 'slippage_stress_multiple': 2}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 7.88% |
| Annualised volatility | 5.82% |
| Sharpe (rf = 0) | 1.33 |
| Sortino | 2.00 |
| Max drawdown | -5.33% |
| Longest drawdown (trading days) | 178 |
| Calmar | 1.48 |
| Worst year | 1.60% |
| Worst month | -3.58% |
| Closed trades | 408 |
| Win rate | 60.78% |
| Average winner | 5.21% |
| Average loser | -3.50% |
| Expectancy per trade | 1.80% |
| Profit factor | 2.14 |
| Average holding (calendar days) | 74.9 |
| Average exposure | 67.68% |
| Turnover (1-way, per year) | 3.22 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -5.46% | 0.31 | 0.77 |
| E901-05 | -5.86% | 0.28 | 0.74 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 11.08% |
| 2011 | 11.79% |
| 2012 | 4.48% |
| 2013 | 15.74% |
| 2014 | 4.67% |
| 2015 | 9.39% |
| 2016 | 1.60% |
| 2017 | 4.92% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97976.69 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.075643; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 71 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.219693434445196e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 828 orders vs QuantConnect Total Orders 828 |
| fills_match_harness_count | pass | downloaded fill events 828 vs harness-recorded fills 828 |
| commission_fixed_per_order | pass | 828 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `0d95433d9c7af1c75c3f271f0802cd428ff3d0e3d864dfb52eddd0491dae606f`
- fills_sha256: `d838696a9e768114e946cfb49ecbcb3319321eec3196a54ac7a5d54e2bd64362`
- trades_sha256: `cf69b552d6806687351fa6cdec05f880cbad54ed1baee44c16ee4cc11905e0a7`
