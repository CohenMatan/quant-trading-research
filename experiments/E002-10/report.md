# E002-10 — S002 v1.1 (research)

C01 H002 S002 v1.1 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E002-02 under D051 with the D054 harness fix (replaces E002-06)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `b2c4a148ec556094b22e7baad2d300a1a9fdd82d` · **QC backtest:** `1bc25df60094997814192fb8aee028f3` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T08:28:29Z · **runtime:** 332s
- **Parameters:** `{'lookback': 126, 'skip': 21, 'every_months': 1, 'slots': 15, 'band': 0.25, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 6.66% |
| Annualised volatility | 18.82% |
| Sharpe (rf = 0) | 0.44 |
| Sortino | 0.60 |
| Max drawdown | -31.10% |
| Longest drawdown (trading days) | 998 |
| Calmar | 0.21 |
| Worst year | -15.05% |
| Worst month | -10.43% |
| Closed trades | 458 |
| Win rate | 54.15% |
| Average winner | 14.54% |
| Average loser | -12.60% |
| Expectancy per trade | 2.09% |
| Profit factor | 1.23 |
| Average holding (calendar days) | 63.4 |
| Average exposure | 63.06% |
| Turnover (1-way, per year) | 3.53 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -6.68% | 0.87 | 0.66 |
| E901-05 | -7.08% | 0.88 | 0.72 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 22.37% |
| 2011 | -5.20% |
| 2012 | 11.21% |
| 2013 | 36.55% |
| 2014 | -15.05% |
| 2015 | -6.08% |
| 2016 | 8.02% |
| 2017 | 10.24% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 96243.10 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.133213; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 30 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.955482056239172e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 974 orders vs QuantConnect Total Orders 974 |
| fills_match_harness_count | pass | downloaded fill events 973 vs harness-recorded fills 973 |
| commission_fixed_per_order | pass | 973 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `819bf7b4a91095a32bf72163c324d647a66a146ca57139f0a5185658897610b2`
- fills_sha256: `28c6c9e0ab1b3f815a0b3c544fcd617757c9e261023e5750604a66e937e26af9`
- trades_sha256: `a825d5212d28a1829bdca6e38df3b4233a192227028ecc40b9cc6d601732bf72`
