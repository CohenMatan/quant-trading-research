# E013-09 — S013 v1.2 (research)

C03 H013 S013 v1.2 seed 3 (one candidate per variation; seeds are replicates, D082) on IS, paired with null E962-24. Pre-declared in docs/checkpoints/CP3e_C03_final_plan.md §7; methodology research/cycles/C03_statistical_spec.md (D082).

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `c331b4cbb3bb06c32eb21c50638df31bdcc070ff` · **QC backtest:** `5a2ca508055dc528b44ab42043139a73` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T17:51:02Z · **runtime:** 397s
- **Parameters:** `{'q': 0.2, 'stat': 'max5', 'seed': 3, 'slots': 15, 'hold': 60}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 13.24% |
| Annualised volatility | 14.25% |
| Sharpe (rf = 0) | 0.94 |
| Sortino | 1.34 |
| Max drawdown | -22.28% |
| Longest drawdown (trading days) | 191 |
| Calmar | 0.59 |
| Worst year | 2.87% |
| Worst month | -9.66% |
| Closed trades | 481 |
| Win rate | 63.83% |
| Average winner | 10.44% |
| Average loser | -9.33% |
| Expectancy per trade | 3.29% |
| Profit factor | 1.96 |
| Average holding (calendar days) | 88.1 |
| Average exposure | 84.86% |
| Turnover (1-way, per year) | 3.62 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -0.10% | 0.90 | 0.91 |
| E901-07 | -0.69% | 0.86 | 0.94 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 11.03% |
| 2011 | 2.87% |
| 2012 | 7.97% |
| 2013 | 35.07% |
| 2014 | 17.12% |
| 2015 | 5.57% |
| 2016 | 9.00% |
| 2017 | 20.19% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 93428.73 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.038702; 0 closes with negative cash |
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

- equity_sha256: `b1e3c5175bd6d945150bb89af6fde3ecad1b7c922d1d814b607f719f85cd1a86`
- fills_sha256: `89acee4854a82a8683e010969092b848e2a711687398baae91d0f7d0da5e664f`
- trades_sha256: `64fcf35866f0814cf9a13a89746a02ff1797d99a9ca983cf4eaef2c536bcce72`
