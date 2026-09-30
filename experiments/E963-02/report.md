# E963-02 — X963 v1.1 (infrastructure)

C03 H012 infrastructure canary v1.1 (E963-01 stopped on a canary-code defect at the 2010-11-26 half-day): unchanged S012 code with NON-candidate parameters (RV(10), weekly, 2010-2011). Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2011-12-30)
- **Commit:** `a4a2d9384410b012fd84f51d173e3c9d5b8ead53` · **QC backtest:** `e5e79f99129ae83d2995c6e062af362b` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T12:34:24Z · **runtime:** 90s
- **Parameters:** `{'rv_short': 10, 'cadence': 'weekly', 'band': 0.1, 'slots': 15, 'mode': 'timing'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2011-12-30 (504 trading days) |
| CAGR | 3.27% |
| Annualised volatility | 13.67% |
| Sharpe (rf = 0) | 0.30 |
| Sortino | 0.42 |
| Max drawdown | -15.05% |
| Longest drawdown (trading days) | 182 |
| Calmar | 0.22 |
| Worst year | 1.60% |
| Worst month | -6.25% |
| Closed trades | 7 |
| Win rate | 14.29% |
| Average winner | 3.25% |
| Average loser | -10.11% |
| Expectancy per trade | -8.20% |
| Profit factor | 0.03 |
| Average holding (calendar days) | 207.7 |
| Average exposure | 73.03% |
| Turnover (1-way, per year) | 1.41 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -4.15% | 0.62 | 0.91 |
| E901-07 | -7.16% | 0.55 | 0.89 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 1.60% |
| 2011 | 4.93% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 504 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2011-12-30 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 87537.55 |
| equity_complete | pass | chart rows 504 vs algorithm days 504 |
| equity_matches_qc_tradeable_dates | pass | chart rows 504 vs QuantConnect tradeableDates 504 |
| no_leverage | pass | min cash/equity 0.023073; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3327444232982833e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 396 orders vs QuantConnect Total Orders 396 |
| fills_match_harness_count | pass | downloaded fill events 396 vs harness-recorded fills 396 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 396 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `2bd66c4eaebb35cd240c94956e632aa4af1ee82ffc72e1260150a9288efc3376`
- fills_sha256: `180da36161a6a07b516aefb92c18274026634de0f0a69149457cc343fe0dafa2`
- trades_sha256: `d9232de8dce64e26afaaae0ab420ec2a77a580a090de4672c130ffaa0bd61425`
