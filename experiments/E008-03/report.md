# E008-03 — S008 v1.2 (research)

C02 H008 S008 v1.2 (pre-declared selection candidate, D069) on IS 2010-2017: unscaled residual return

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `f7b712b7f20d8a0f1c213a537c5fe8a58583391a` · **QC backtest:** `35e96c606ac76172745b5dee8457f3df` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T23:13:57Z · **runtime:** 932s
- **Parameters:** `{'window': 252, 'skip': 21, 'scaled': False, 'slots': 10, 'keep': 20}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 14.86% |
| Annualised volatility | 25.83% |
| Sharpe (rf = 0) | 0.67 |
| Sortino | 0.94 |
| Max drawdown | -33.65% |
| Longest drawdown (trading days) | 615 |
| Calmar | 0.44 |
| Worst year | -4.55% |
| Worst month | -11.94% |
| Closed trades | 287 |
| Win rate | 56.79% |
| Average winner | 20.37% |
| Average loser | -16.55% |
| Expectancy per trade | 4.42% |
| Profit factor | 1.47 |
| Average holding (calendar days) | 95.8 |
| Average exposure | 90.61% |
| Turnover (1-way, per year) | 3.29 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | 1.52% | 1.29 | 0.71 |
| E901-07 | 0.94% | 1.27 | 0.76 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 15.62% |
| 2011 | -4.15% |
| 2012 | 52.70% |
| 2013 | 39.08% |
| 2014 | 18.13% |
| 2015 | -4.55% |
| 2016 | 11.15% |
| 2017 | 2.50% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 89311.00 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.029971; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 19 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.0289434728280054e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 584 orders vs QuantConnect Total Orders 584 |
| fills_match_harness_count | pass | downloaded fill events 584 vs harness-recorded fills 584 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 584 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `aadfc183e725676eb42d92c2919b6af098a3eb91bf3421addecdf581038acc1e`
- fills_sha256: `8a6537594222ff1c2d93685a238dae067406d16dbb4c686c340e9634e1d5050d`
- trades_sha256: `07be018662a8d22e18f2dbd160f32e5fe0d44a5b771973bc95f4d79607e94c14`
