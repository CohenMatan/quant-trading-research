# E962-06 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series S: portfolio size: 15 slots at $100K, hold 20, seed 3. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `43d3a1582472aff2c0e563ae8019d21c4a99f53d` · **QC backtest:** `ede28bb0051b667a9770a78c1812fad8` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T09:01:34Z · **runtime:** 302s
- **Parameters:** `{'slots': 15, 'hold': 20, 'seed': 3}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 9.66% |
| Annualised volatility | 14.55% |
| Sharpe (rf = 0) | 0.71 |
| Sortino | 1.00 |
| Max drawdown | -17.05% |
| Longest drawdown (trading days) | 303 |
| Calmar | 0.57 |
| Worst year | 1.84% |
| Worst month | -9.54% |
| Closed trades | 1352 |
| Win rate | 56.14% |
| Average winner | 5.95% |
| Average loser | -5.83% |
| Expectancy per trade | 0.78% |
| Profit factor | 1.27 |
| Average holding (calendar days) | 30.3 |
| Average exposure | 82.27% |
| Turnover (1-way, per year) | 9.93 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -3.68% | 0.89 | 0.88 |
| E901-07 | -4.27% | 0.85 | 0.91 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 17.26% |
| 2011 | 1.94% |
| 2012 | 5.61% |
| 2013 | 27.79% |
| 2014 | 5.23% |
| 2015 | 4.28% |
| 2016 | 1.84% |
| 2017 | 15.80% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 96153.36 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.059331; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 3 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.174388296080242e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 2719 orders vs QuantConnect Total Orders 2719 |
| fills_match_harness_count | pass | downloaded fill events 2719 vs harness-recorded fills 2719 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 2719 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `ef99ed31b3c4da5509b2ec45154fc26fc2d507ca660607afb51d0221d6f03064`
- fills_sha256: `c12c3d7445d079c0d5c4ee8b3d2f03b75fb10841cf137b7a4c3b9917970caabb`
- trades_sha256: `e45f486cbf478d41b9fe33603b2c503b606ec401e0ed0469759c0f1d6789a218`
