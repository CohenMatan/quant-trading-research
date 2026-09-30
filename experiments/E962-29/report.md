# E962-29 — X962 v1.0 (infrastructure)

C03 S2 null ($200K, 20 slots, hold 60, seed 2). Not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `dbe2802d86a2b5f29a36da3c676534d1286c170d` · **QC backtest:** `876935247c0a8267fa7bdc80a7a5bf03` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T19:03:02Z · **runtime:** 319s
- **Parameters:** `{'slots': 20, 'hold': 60, 'seed': 2}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 20, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 13.33% |
| Annualised volatility | 14.85% |
| Sharpe (rf = 0) | 0.92 |
| Sortino | 1.29 |
| Max drawdown | -23.12% |
| Longest drawdown (trading days) | 295 |
| Calmar | 0.58 |
| Worst year | -4.73% |
| Worst month | -9.21% |
| Closed trades | 642 |
| Win rate | 63.08% |
| Average winner | 11.18% |
| Average loser | -10.47% |
| Expectancy per trade | 3.19% |
| Profit factor | 1.76 |
| Average holding (calendar days) | 87.8 |
| Average exposure | 84.35% |
| Turnover (1-way, per year) | 3.59 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -0.01% | 0.94 | 0.91 |
| E901-07 | -0.60% | 0.90 | 0.94 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 23.85% |
| 2011 | -4.73% |
| 2012 | 18.32% |
| 2013 | 26.75% |
| 2014 | 9.87% |
| 2015 | 4.36% |
| 2016 | 21.92% |
| 2017 | 9.79% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 193524.56 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.087763; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 9 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3084730965147665e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1304 orders vs QuantConnect Total Orders 1304 |
| fills_match_harness_count | pass | downloaded fill events 1304 vs harness-recorded fills 1304 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1304 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `795b711fd849b820dcb6a469b8dea9ed465f8dcd04da2a9f3d4470f7ef3fc1b5`
- fills_sha256: `377a7635631954905523925a00efa93457fe28ab7e1a3111a585e860fa424240`
- trades_sha256: `3cf46dbb8a8ce86e3db8fe9ab9a6a0c758e3b097ee710e6d9622e7e1d3a55273`
