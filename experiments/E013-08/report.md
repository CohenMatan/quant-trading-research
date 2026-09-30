# E013-08 — S013 v1.2 (research)

C03 H013 S013 v1.2 seed 2 (one candidate per variation; seeds are replicates, D082) on IS, paired with null E962-23. Pre-declared in docs/checkpoints/CP3e_C03_final_plan.md §7; methodology research/cycles/C03_statistical_spec.md (D082).

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `31b49468b4554599efc50ccb6a3eb9ded5701020` · **QC backtest:** `4329263863b7574f305ec145010843d6` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T17:39:25Z · **runtime:** 685s
- **Parameters:** `{'q': 0.2, 'stat': 'max5', 'seed': 2, 'slots': 15, 'hold': 60}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 9.67% |
| Annualised volatility | 13.66% |
| Sharpe (rf = 0) | 0.74 |
| Sortino | 1.04 |
| Max drawdown | -20.79% |
| Longest drawdown (trading days) | 271 |
| Calmar | 0.47 |
| Worst year | -3.18% |
| Worst month | -8.13% |
| Closed trades | 481 |
| Win rate | 61.75% |
| Average winner | 9.57% |
| Average loser | -9.62% |
| Expectancy per trade | 2.23% |
| Profit factor | 1.53 |
| Average holding (calendar days) | 88.0 |
| Average exposure | 83.70% |
| Turnover (1-way, per year) | 3.55 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -3.67% | 0.86 | 0.90 |
| E901-07 | -4.25% | 0.81 | 0.92 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 15.81% |
| 2011 | -3.18% |
| 2012 | 22.13% |
| 2013 | 18.90% |
| 2014 | 5.40% |
| 2015 | 2.46% |
| 2016 | 13.10% |
| 2017 | 5.08% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 95332.84 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.109172; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 5 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3084730965147665e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 977 orders vs QuantConnect Total Orders 977 |
| fills_match_harness_count | pass | downloaded fill events 977 vs harness-recorded fills 977 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 977 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `baa86a7a53c52bde944d8350a150b7b5b491e5651c55e1a955836a9184270b62`
- fills_sha256: `3e81f28c8c1c1914d794570ac4769da720d53005560c1b80365ee5c4e073ea98`
- trades_sha256: `56d1a0a255e98248157b3d635b3ccddb2c1f74d4e7966652c61fb9bfec40967d`
