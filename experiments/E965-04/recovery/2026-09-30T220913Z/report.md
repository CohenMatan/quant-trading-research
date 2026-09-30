# E965-04 — X965 v1.1 (infrastructure)

P2 H014 canary: unchanged S014 code, H014 entry with NON-candidate thresholds (RSI 30/50, window 4) and a 20-session horizon with roll, 2010-2012, $100K. Re-run of E965-01 with canary v1.1 (E965-01 stopped on a canary-audit defect on the first close). Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2012-12-31)
- **Commit:** `cd180e1e427b8bc08cc44ac1b0ad280ebf424086` · **QC backtest:** `addc0263c82157b2154d09812e3cc4ee` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T20:57:14Z · **runtime:** 0s
- **Parameters:** `{'mode': 'h014', 'exit': 'A', 'limit': 20, 'rsi_pullback': 30, 'window': 4, 'rsi_recovery': 50, 'slots': 12}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2012-12-31 (754 trading days) |
| CAGR | -2.27% |
| Annualised volatility | 7.42% |
| Sharpe (rf = 0) | -0.27 |
| Sortino | -0.35 |
| Max drawdown | -14.16% |
| Longest drawdown (trading days) | 664 |
| Calmar | -0.16 |
| Worst year | -3.16% |
| Worst month | -5.80% |
| Closed trades | 124 |
| Win rate | 38.71% |
| Average winner | 5.55% |
| Average loser | -4.82% |
| Expectancy per trade | -0.81% |
| Profit factor | 0.73 |
| Average holding (calendar days) | 23.4 |
| Average exposure | 21.00% |
| Turnover (1-way, per year) | 3.28 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -12.38% | 0.22 | 0.52 |
| E901-07 | -14.78% | 0.21 | 0.54 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | -0.79% |
| 2011 | -3.16% |
| 2012 | -2.83% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 754 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2012-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 89379.71 |
| equity_complete | pass | chart rows 754 vs algorithm days 754 |
| equity_matches_qc_tradeable_dates | pass | chart rows 754 vs QuantConnect tradeableDates 754 |
| no_leverage | pass | min cash/equity 0.034810; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.748094862010233e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 248 orders vs QuantConnect Total Orders 248 |
| fills_match_harness_count | pass | downloaded fill events 248 vs harness-recorded fills 248 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 248 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `451df29964325e8c005d65cdd0f7d510f2b1a92a1789a2c610a5f2819f9b6710`
- fills_sha256: `2843821e0ecbc3ad97d69cd7e119e7022c638b67cd733d55f83fc429665a26ca`
- trades_sha256: `a8567325d614e14b9d8ed7eded1bb5a575f9a971f83d2e05d2d01c76a13da32f`
