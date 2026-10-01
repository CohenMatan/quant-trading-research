# E014-24 — S014 v1.0 (sizing)

Technical repeat of E014-13 (identical configuration). E014-13's QuantConnect backtest never started: the backtest node reported 'No space left on device' (QC infrastructure; progress 0, 0 tradeable days). P2 $200K sensitivity (12 slots) of E014-01. Diagnostic, never used for selection. Pre-declared in research/phase2/P2_spec.md (frozen, D094).

- **Status:** completed
- **Split:** DEV (2010-01-04 → 2021-12-31)
- **Commit:** `7e4f93aed7c86bd4fbb5d4a2d96f8da3448d651a` · **QC backtest:** `5a8b89c7f4e57f85c231f020bc416493` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-01T03:29:40Z · **runtime:** 1364s
- **Parameters:** `{'mode': 'h014', 'exit': 'A', 'limit': 63, 'rsi_pullback': 40, 'window': 5, 'rsi_recovery': 45, 'slots': 12}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 12.33% |
| Annualised volatility | 21.30% |
| Sharpe (rf = 0) | 0.65 |
| Sortino | 0.91 |
| Max drawdown | -36.85% |
| Longest drawdown (trading days) | 372 |
| Calmar | 0.33 |
| Worst year | -14.62% |
| Worst month | -24.64% |
| Closed trades | 817 |
| Win rate | 43.57% |
| Average winner | 18.02% |
| Average loser | -9.41% |
| Expectancy per trade | 2.54% |
| Profit factor | 1.31 |
| Average holding (calendar days) | 61.6 |
| Average exposure | 92.22% |
| Turnover (1-way, per year) | 5.30 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -2.26% | 0.88 | 0.68 |
| E901-07 | -1.15% | 0.86 | 0.72 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 33.29% |
| 2011 | 6.71% |
| 2012 | 12.50% |
| 2013 | 34.07% |
| 2014 | 7.92% |
| 2015 | -0.35% |
| 2016 | 13.69% |
| 2017 | 20.54% |
| 2018 | -14.62% |
| 2019 | 27.36% |
| 2020 | 2.17% |
| 2021 | 14.71% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 189193.15 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.020716; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 12 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.2692361674484425e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1647 orders vs QuantConnect Total Orders 1647 |
| fills_match_harness_count | pass | downloaded fill events 1646 vs harness-recorded fills 1646 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1646 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `f10107617218acbc5d08d9c6e796a837a756dabaad4b77f92fb69f66dc1ac046`
- fills_sha256: `f7a5a52e8d7174eef1c487f79ee66f8bb5ecc8b9e540a38553ce34734f6c8e64`
- trades_sha256: `aadfe0409f9c58be24d264ad8c82e47305617bb1d7c3ebfffd0adaef63f64f1b`
