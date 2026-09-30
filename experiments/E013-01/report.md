# E013-01 — S013 v1.0 (research)

C03 H013 S013 v1.0 seed 1 (one candidate per variation; seeds are replicates, D082) on IS, paired with null E962-22. Pre-declared in docs/checkpoints/CP3e_C03_final_plan.md §7; methodology research/cycles/C03_statistical_spec.md (D082).

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `62b3b3fbfc9d71f07bf9e478b3a378049636d0c8` · **QC backtest:** `36964e685a06d4d72345a830690cfc39` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T15:32:22Z · **runtime:** 376s
- **Parameters:** `{'q': 0.2, 'stat': 'max', 'seed': 1, 'slots': 15, 'hold': 60}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 9.79% |
| Annualised volatility | 14.08% |
| Sharpe (rf = 0) | 0.73 |
| Sortino | 1.04 |
| Max drawdown | -23.17% |
| Longest drawdown (trading days) | 467 |
| Calmar | 0.42 |
| Worst year | -4.58% |
| Worst month | -9.08% |
| Closed trades | 482 |
| Win rate | 58.09% |
| Average winner | 10.48% |
| Average loser | -8.77% |
| Expectancy per trade | 2.41% |
| Profit factor | 1.56 |
| Average holding (calendar days) | 87.9 |
| Average exposure | 84.00% |
| Turnover (1-way, per year) | 3.56 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -3.55% | 0.89 | 0.90 |
| E901-07 | -4.14% | 0.84 | 0.93 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 20.63% |
| 2011 | -4.47% |
| 2012 | 11.08% |
| 2013 | 27.99% |
| 2014 | 9.11% |
| 2015 | -4.58% |
| 2016 | 10.01% |
| 2017 | 12.31% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97169.62 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.089655; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 7 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.757220605304979e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 980 orders vs QuantConnect Total Orders 980 |
| fills_match_harness_count | pass | downloaded fill events 978 vs harness-recorded fills 978 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 978 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `6a180d6a73890cdf7ad5ea4bc8dd10d1cff1bc9dfb1ba14a4fa2a4186201cfa3`
- fills_sha256: `975e0dada4910074dd26ec7afbef028f656b0d7f3d7cb11e9ae650594ca4afbb`
- trades_sha256: `ed9bf8ab19a50313e2d720a17b03bc3ab0ffe92ea13f2e4d251b8532d84cafef`
