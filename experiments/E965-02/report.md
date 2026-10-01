# E965-02 — X965 v1.1 (infrastructure)

P2 canary: random-uptrend mode, seed 7 (not a control seed), exit B with a 30-session cap, $60K so that the $5,000 minimum position binds (slot weight raised, 11-position size cap). Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2011-12-30)
- **Commit:** `3e360d3325f922f19a5e70456eaefab72d01b2b1` · **QC backtest:** `772ca9c9ee1cfe7b8888b395498a6a3e` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T22:22:44Z · **runtime:** 224s
- **Parameters:** `{'mode': 'rand', 'exit': 'B', 'limit': 30, 'rsi_pullback': 40, 'window': 5, 'rsi_recovery': 45, 'slots': 12, 'seed': 7}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2011-12-30 (504 trading days) |
| CAGR | 6.25% |
| Annualised volatility | 17.24% |
| Sharpe (rf = 0) | 0.44 |
| Sortino | 0.61 |
| Max drawdown | -22.45% |
| Longest drawdown (trading days) | 123 |
| Calmar | 0.28 |
| Worst year | -10.40% |
| Worst month | -10.28% |
| Closed trades | 186 |
| Win rate | 51.08% |
| Average winner | 7.79% |
| Average loser | -6.97% |
| Expectancy per trade | 0.57% |
| Profit factor | 1.10 |
| Average holding (calendar days) | 34.2 |
| Average exposure | 73.53% |
| Turnover (1-way, per year) | 7.58 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -1.17% | 0.70 | 0.82 |
| E901-07 | -4.18% | 0.66 | 0.84 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 25.89% |
| 2011 | -10.40% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 504 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2011-12-30 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 57564.55 |
| equity_complete | pass | chart rows 504 vs algorithm days 504 |
| equity_matches_qc_tradeable_dates | pass | chart rows 504 vs QuantConnect tradeableDates 504 |
| no_leverage | pass | min cash/equity 0.037304; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 1 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.8467331175345625e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 392 orders vs QuantConnect Total Orders 392 |
| fills_match_harness_count | pass | downloaded fill events 384 vs harness-recorded fills 384 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 384 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `c76238b86a60f078ced02881852d97742177dc1166e8618ee2debf6df2dc5eb5`
- fills_sha256: `0aa20521dda745573b8267d493e9ede26ea90b28a20dcebe1ca45ea14be803d0`
- trades_sha256: `970a6b6fc41256e8a654e90349ff066550eb73ee343c95da526a1e3a941fd879`
