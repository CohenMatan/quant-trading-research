# E014-02 — S014 v1.1 (research)

P2 H014 candidate B (S014 v1.1) on DEV 2010-2021. Pre-declared in research/phase2/P2_spec.md (frozen, D094).

- **Status:** completed
- **Split:** DEV (2010-01-04 → 2021-12-31)
- **Commit:** `fe74f476cfd123a1c0968c76ef2877e75a7d3808` · **QC backtest:** `40dbcd48c50b8eca208df98e4b7e73d4` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T23:05:52Z · **runtime:** 1227s
- **Parameters:** `{'mode': 'h014', 'exit': 'B', 'limit': 126, 'rsi_pullback': 40, 'window': 5, 'rsi_recovery': 45, 'slots': 12}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 14.83% |
| Annualised volatility | 22.79% |
| Sharpe (rf = 0) | 0.72 |
| Sortino | 1.02 |
| Max drawdown | -39.17% |
| Longest drawdown (trading days) | 469 |
| Calmar | 0.38 |
| Worst year | -16.05% |
| Worst month | -27.52% |
| Closed trades | 547 |
| Win rate | 37.48% |
| Average winner | 27.97% |
| Average loser | -9.65% |
| Expectancy per trade | 4.45% |
| Profit factor | 1.51 |
| Average holding (calendar days) | 92.5 |
| Average exposure | 93.11% |
| Turnover (1-way, per year) | 3.38 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | 0.24% | 0.93 | 0.68 |
| E901-07 | 1.34% | 0.90 | 0.70 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 34.73% |
| 2011 | 9.21% |
| 2012 | 11.79% |
| 2013 | 37.57% |
| 2014 | 8.65% |
| 2015 | -9.77% |
| 2016 | 6.97% |
| 2017 | 43.41% |
| 2018 | -16.05% |
| 2019 | 30.40% |
| 2020 | 23.13% |
| 2021 | 14.37% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 94566.44 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.020174; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 9 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.050748481174355e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1106 orders vs QuantConnect Total Orders 1106 |
| fills_match_harness_count | pass | downloaded fill events 1106 vs harness-recorded fills 1106 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1106 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `982cf079ac658df70f29d613f2111dcda0dd33f0037e23897af1befec3feac4b`
- fills_sha256: `66dcc9562882d736fd610839dc9f318d1c77da39bfb2227a1017cc7994389b1e`
- trades_sha256: `335ca332fdca2fb1bc9dd2a58eb3d6cdfb414e586c3881ebc6b787057dcd03b0`
