# E001-12 — S001 v1.1 (research)

C01 H001 S001 v1.1 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E001-02 under D051 with the D054 harness fix (replaces E001-07)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `61cd750cd15dcd73e211261d3810324a42b12b27` · **QC backtest:** `67eb5f536d39b84ee9682429c1bf3e14` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T07:54:01Z · **runtime:** 349s
- **Parameters:** `{'entry': 'rsi', 'rsi_max': 5, 'exit': 'sma5', 'max_hold': 10, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 1.66% |
| Annualised volatility | 13.28% |
| Sharpe (rf = 0) | 0.19 |
| Sortino | 0.26 |
| Max drawdown | -30.93% |
| Longest drawdown (trading days) | 1603 |
| Calmar | 0.05 |
| Worst year | -19.83% |
| Worst month | -10.48% |
| Closed trades | 1371 |
| Win rate | 53.03% |
| Average winner | 1.75% |
| Average loser | -2.63% |
| Expectancy per trade | -0.31% |
| Profit factor | 0.76 |
| Average holding (calendar days) | 6.3 |
| Average exposure | 65.41% |
| Turnover (1-way, per year) | 10.08 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -11.68% | 0.74 | 0.80 |
| E901-05 | -12.08% | 0.73 | 0.85 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 6.84% |
| 2011 | -19.83% |
| 2012 | 8.76% |
| 2013 | 16.84% |
| 2014 | 0.41% |
| 2015 | -12.60% |
| 2016 | 10.43% |
| 2017 | 8.13% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 77515.00 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.027912; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 2 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.757220605304979e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 2750 orders vs QuantConnect Total Orders 2750 |
| fills_match_harness_count | pass | downloaded fill events 2750 vs harness-recorded fills 2750 |
| commission_fixed_per_order | pass | 2750 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `c0765062b22b253ded73cf82be30b77a4376a995b6a59c22aad6155db0aa6d0b`
- fills_sha256: `937a4557472fcea7fe114a0b56b9d2bc039a9d0c3945705c40b486ee94328923`
- trades_sha256: `1426ccde6c89972babd785762506eb7dd7284ab0463410ea415647e0989d9589`
