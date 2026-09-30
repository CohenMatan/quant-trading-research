# E013-03 — S013 v1.0 (research)

C03 H013 S013 v1.0 seed 3 (one candidate per variation; seeds are replicates, D082) on IS, paired with null E962-24. Pre-declared in docs/checkpoints/CP3e_C03_final_plan.md §7; methodology research/cycles/C03_statistical_spec.md (D082).

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `f853e48ceec09e2323e2c37d9dab6afaade608e9` · **QC backtest:** `eaa1741d929c61337686f17255e52e0e` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T19:13:38Z · **runtime:** 395s
- **Parameters:** `{'q': 0.2, 'stat': 'max', 'seed': 3, 'slots': 15, 'hold': 60}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 11.58% |
| Annualised volatility | 14.35% |
| Sharpe (rf = 0) | 0.84 |
| Sortino | 1.18 |
| Max drawdown | -22.40% |
| Longest drawdown (trading days) | 289 |
| Calmar | 0.52 |
| Worst year | -0.35% |
| Worst month | -9.11% |
| Closed trades | 481 |
| Win rate | 62.58% |
| Average winner | 10.40% |
| Average loser | -9.61% |
| Expectancy per trade | 2.91% |
| Profit factor | 1.78 |
| Average holding (calendar days) | 88.1 |
| Average exposure | 84.09% |
| Turnover (1-way, per year) | 3.57 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -1.77% | 0.91 | 0.90 |
| E901-07 | -2.35% | 0.87 | 0.93 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 8.55% |
| 2011 | 1.62% |
| 2012 | 9.09% |
| 2013 | 38.29% |
| 2014 | 14.23% |
| 2015 | -0.35% |
| 2016 | 8.79% |
| 2017 | 16.35% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 91516.81 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.048971; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 3 LEAN-generated fills |
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

- equity_sha256: `6b9b645df70ad7971d4aaeb10a89180d3ba33acb589d3b81874deb5280b6879a`
- fills_sha256: `ef021d48333e24e93f476fa173ed63a087304b3946a551a1d7e666429f452fd5`
- trades_sha256: `eff0f89076b66813eeeb100bc4cb67beb48ec5e826e0a2657f7b13f44e7f54b9`

## Reproduction

- Original backtest: `f20167ce25ee4d28cf44413e6f5ee8e4`
- Identical: **True** {'equity_sha256': True, 'fills_sha256': True, 'trades_sha256': True}
