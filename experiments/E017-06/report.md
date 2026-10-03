# E017-06 — S017 v1.0 (benchmark)

P2 H017 random-event control seed 4: identical code path, timing, sizing, holding, costs and daily k_t as E017-01; only the selection differs. Pre-declared in research/phase2/H017_spec.md (frozen 2026-10-03).

- **Status:** completed
- **Split:** DEV (2010-03-01 → 2021-12-31)
- **Commit:** `c26b2e854d001a870014674ca9bb58676b9d7d51` · **QC backtest:** `901f745bca4f71b53dba3abad4672deb` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-03T19:27:54Z · **runtime:** 848s
- **Parameters:** `{'slots': 10, 'hold_sessions': 60, 'quantile': 0.9, 'reaction_lag': 1, 'book': 'random', 'seed': 4}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2021-12-31 (2983 trading days) |
| CAGR | 10.26% |
| Annualised volatility | 20.22% |
| Sharpe (rf = 0) | 0.58 |
| Sortino | 0.81 |
| Max drawdown | -47.01% |
| Longest drawdown (trading days) | 721 |
| Calmar | 0.22 |
| Worst year | -19.15% |
| Worst month | -23.47% |
| Closed trades | 461 |
| Win rate | 62.69% |
| Average winner | 10.49% |
| Average loser | -10.45% |
| Expectancy per trade | 2.68% |
| Profit factor | 1.49 |
| Average holding (calendar days) | 87.0 |
| Average exposure | 88.98% |
| Turnover (1-way, per year) | 3.72 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -4.62% | 1.08 | 0.88 |
| E901-07 | -3.13% | 1.04 | 0.92 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 14.63% |
| 2011 | 6.08% |
| 2012 | 15.94% |
| 2013 | 23.38% |
| 2014 | 26.62% |
| 2015 | -9.30% |
| 2016 | 9.25% |
| 2017 | 11.31% |
| 2018 | -19.15% |
| 2019 | 24.56% |
| 2020 | 7.60% |
| 2021 | 20.67% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2983 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 90435.98 |
| equity_complete | pass | chart rows 2983 vs algorithm days 2983 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2983 vs QuantConnect tradeableDates 2983 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 166 warm-up sessions |
| no_leverage | pass | min cash/equity 0.030508; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 1 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.6943742754118166e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 932 orders vs QuantConnect Total Orders 932 |
| fills_match_harness_count | pass | downloaded fill events 932 vs harness-recorded fills 932 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 932 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `df10eff7b3d8cecdeb0ec97b8ad3a3a15c355e5e19812ebf6d28830c031603e5`
- fills_sha256: `d906959ef5abca82ba334411d8a8fdbc569a2180cea186166c9e1ff779dab55f`
- trades_sha256: `835d08bffc0c256bb5238f60c834b0ba3f1369ec2b4e6b9e02b6b5851df18ee7`
