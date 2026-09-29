# E001-02 — S001 v1.1 (research)

C01 H001 S001 v1.1 (pre-declared variation) on IS 2010-2017

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `7613185988712526eba7d8c7f66018863d1cacbf` · **QC backtest:** `ac3a01a35ebca5fc19e26e47154f872d` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T11:45:48Z · **runtime:** 369s
- **Parameters:** `{'entry': 'rsi', 'rsi_max': 5, 'exit': 'sma5', 'max_hold': 10, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 1.01% |
| Annualised volatility | 15.91% |
| Sharpe (rf = 0) | 0.14 |
| Sortino | 0.20 |
| Max drawdown | -35.18% |
| Longest drawdown (trading days) | 1068 |
| Calmar | 0.03 |
| Worst year | -19.64% |
| Worst month | -9.68% |
| Closed trades | 2440 |
| Win rate | 53.16% |
| Average winner | 1.61% |
| Average loser | -2.29% |
| Expectancy per trade | -0.22% |
| Profit factor | 0.80 |
| Average holding (calendar days) | 5.6 |
| Average exposure | 82.20% |
| Turnover (1-way, per year) | 17.64 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-04 | -12.27% | 0.92 | 0.83 |
| E901-03 | -13.14% | 0.89 | 0.88 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 8.47% |
| 2011 | -17.84% |
| 2012 | 8.34% |
| 2013 | 14.11% |
| 2014 | 1.48% |
| 2015 | -19.64% |
| 2016 | 13.21% |
| 2017 | 6.55% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 75048.65 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.0126 |
| cash_never_negative | pass | min cash/equity 0.0126 |
| fills_after_signal_date | pass | 0 violations, 3 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.209735034398567e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 4895 orders vs QuantConnect Total Orders 4895 |
| fills_match_harness_count | pass | downloaded fill events 4894 vs harness-recorded fills 4894 |
| commission_fixed_per_order | pass | 4894 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `caf4ed4aed5620d5cbab155ae3ec096df7b35417fed1cdeccefb37a1fa2cd5b1`
- fills_sha256: `f2c03c0921f9744bba270ee31012739c70c4a68f55b1e827e01a556af5f7cb2d`
- trades_sha256: `a93634f679570b2b7d61c58a276860562b67feb90326babd90f3f3b44a6082e3`
