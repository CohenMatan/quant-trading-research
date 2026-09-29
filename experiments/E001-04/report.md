# E001-04 — S001 v1.3 (research)

C01 H001 S001 v1.3 (pre-declared variation) on IS 2010-2017

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `91071b71585d5c24b20f446c0f21b978cc8fa7d9` · **QC backtest:** `8fb8be1fff9e08bec4841526cbb4082b` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T11:58:47Z · **runtime:** 362s
- **Parameters:** `{'entry': 'rsi', 'rsi_max': 10, 'exit': 'sma5', 'max_hold': 10, 'slots': 15, 'regime_filter': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | -3.13% |
| Annualised volatility | 12.07% |
| Sharpe (rf = 0) | -0.20 |
| Sortino | -0.27 |
| Max drawdown | -40.55% |
| Longest drawdown (trading days) | 1943 |
| Calmar | -0.08 |
| Worst year | -25.12% |
| Worst month | -9.70% |
| Closed trades | 2016 |
| Win rate | 53.77% |
| Average winner | 1.42% |
| Average loser | -2.35% |
| Expectancy per trade | -0.32% |
| Profit factor | 0.70 |
| Average holding (calendar days) | 5.5 |
| Average exposure | 64.16% |
| Turnover (1-way, per year) | 18.45 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-04 | -16.41% | 0.64 | 0.76 |
| E901-03 | -17.28% | 0.62 | 0.81 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | -9.97% |
| 2011 | -25.12% |
| 2012 | 3.29% |
| 2013 | 11.17% |
| 2014 | -0.67% |
| 2015 | -7.71% |
| 2016 | 3.49% |
| 2017 | 5.66% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 63122.51 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.0122 |
| cash_never_negative | pass | min cash/equity 0.0122 |
| fills_after_signal_date | pass | 0 violations, 1 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.4962832304260223e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 4040 orders vs QuantConnect Total Orders 4040 |
| fills_match_harness_count | pass | downloaded fill events 4040 vs harness-recorded fills 4040 |
| commission_fixed_per_order | pass | 4040 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `e4e97b4c39c9cfce2b18c998c92bdd7284cfa2e2c35f09aedcd68d61c6ecb40d`
- fills_sha256: `5391ff27db6bfdf2f5b621b76fcb5df88955cb9e6d362f06fd0e96e81fe4a276`
- trades_sha256: `8b9c8e602c2aa8e42563caa95748fc0594e1aff2ef26e414e9490c1381302691`
