# E963-03 — X963 v1.2 (infrastructure)

C03 H012 infrastructure canary v1.2 after the S012 fix found by E963-02 (basket formed at the first close with eligible names, D083 addendum): unchanged S012 code with NON-candidate parameters (RV(10), weekly, 2010-2011). Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2011-12-30)
- **Commit:** `d5d7ab58703939da4644b451ee72a0e4c13b59e7` · **QC backtest:** `cbe09dd823b2f05ffd7844ea895e79f8` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T12:47:06Z · **runtime:** 234s
- **Parameters:** `{'rv_short': 10, 'cadence': 'weekly', 'band': 0.1, 'slots': 15, 'mode': 'timing'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2011-12-30 (504 trading days) |
| CAGR | 6.47% |
| Annualised volatility | 14.12% |
| Sharpe (rf = 0) | 0.51 |
| Sortino | 0.71 |
| Max drawdown | -15.13% |
| Longest drawdown (trading days) | 183 |
| Calmar | 0.43 |
| Worst year | 4.93% |
| Worst month | -6.26% |
| Closed trades | 8 |
| Win rate | 12.50% |
| Average winner | 3.27% |
| Average loser | -6.89% |
| Expectancy per trade | -5.62% |
| Profit factor | 0.04 |
| Average holding (calendar days) | 220.4 |
| Average exposure | 81.24% |
| Turnover (1-way, per year) | 1.45 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -0.96% | 0.65 | 0.92 |
| E901-07 | -3.97% | 0.58 | 0.90 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 7.92% |
| 2011 | 4.93% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 504 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2011-12-30 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 93011.19 |
| equity_complete | pass | chart rows 504 vs algorithm days 504 |
| equity_matches_qc_tradeable_dates | pass | chart rows 504 vs QuantConnect tradeableDates 504 |
| no_leverage | pass | min cash/equity 0.023033; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3327444232982833e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 405 orders vs QuantConnect Total Orders 405 |
| fills_match_harness_count | pass | downloaded fill events 405 vs harness-recorded fills 405 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 405 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `5f6e53920a554172784fbc5924ec6fa3a726a52511c81d5e2758a2699aa0c974`
- fills_sha256: `ce3058d662ba8637819dfe1e1dfb905254fbefb2ab70584508c806573b2ee0bf`
- trades_sha256: `865dfed593269b45c9f452315bdd7b3e5d4b3ce6101d42b7f072d1f9b122f414`
