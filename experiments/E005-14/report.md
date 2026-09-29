# E005-14 — S005 v1.1 (research)

C01 robustness of E005-11: slippage 2x (20 bps/side) (pre-declared in research/cycles/C01_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `9ebc89d99b5ec5f61e763573b674541f862e0c63` · **QC backtest:** `a488640fe1a118cbd549f70cd64844d2` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T10:07:16Z · **runtime:** 405s
- **Parameters:** `{'vol_days': 252, 'slots': 15, 'band': 0.25, 'require_positive_mom': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate', 'slippage_stress_multiple': 2}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 10.10% |
| Annualised volatility | 8.31% |
| Sharpe (rf = 0) | 1.20 |
| Sortino | 1.76 |
| Max drawdown | -9.47% |
| Longest drawdown (trading days) | 154 |
| Calmar | 1.07 |
| Worst year | 2.17% |
| Worst month | -5.45% |
| Closed trades | 164 |
| Win rate | 60.98% |
| Average winner | 12.26% |
| Average loser | -6.02% |
| Expectancy per trade | 5.13% |
| Profit factor | 2.77 |
| Average holding (calendar days) | 221.2 |
| Average exposure | 82.89% |
| Turnover (1-way, per year) | 1.37 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -3.24% | 0.45 | 0.77 |
| E901-05 | -3.64% | 0.40 | 0.73 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 12.30% |
| 2011 | 12.43% |
| 2012 | 3.97% |
| 2013 | 17.74% |
| 2014 | 13.77% |
| 2015 | 2.17% |
| 2016 | 8.65% |
| 2017 | 10.44% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97982.10 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.042143; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 5 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.2158937724814711e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 345 orders vs QuantConnect Total Orders 345 |
| fills_match_harness_count | pass | downloaded fill events 344 vs harness-recorded fills 344 |
| commission_fixed_per_order | pass | 344 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `1e63789600167603d73573681de9b17ad90b451672fec2e3c88e97b98950a541`
- fills_sha256: `8bbe2d449fa1a79c391ab69a73441747b4de48fa14b649d61a3f23407f733f8f`
- trades_sha256: `3dc9214b53abc610cd44d320db867fd9c18339bbdc3e36d23fa9aba9c9009cbc`
