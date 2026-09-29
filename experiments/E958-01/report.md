# E958-01 — X958 v1.0 (infrastructure)

D063 end-to-end canary: selected at the close, removed from the universe overnight while the buy is pending; buy must fill, window must survive, window-based exit must execute. Infrastructure; not a trial.

- **Status:** completed_with_warnings
- **Split:** AUDIT (2012-01-03 → 2012-12-31)
- **Commit:** `f493c9877e905c1ed5629b3e081d3f8c4f876ecb` · **QC backtest:** `d2910ba2cc119630a253b3e1ea29aaad` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T15:11:00Z · **runtime:** 90s
- **Parameters:** `{}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': "D039: $7 per executed buy or sell order (owner's broker); slippage separate"}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2012-01-03 → 2012-12-31 (250 trading days) |
| CAGR | 0.83% |
| Annualised volatility | 0.97% |
| Sharpe (rf = 0) | 0.87 |
| Sortino | 1.62 |
| Max drawdown | -0.43% |
| Longest drawdown (trading days) | 108 |
| Calmar | 1.93 |
| Worst year | 0.83% |
| Worst month | -0.19% |
| Closed trades | 23 |
| Win rate | 60.87% |
| Average winner | 2.79% |
| Average loser | -2.48% |
| Expectancy per trade | 0.73% |
| Profit factor | 1.74 |
| Average holding (calendar days) | 4.4 |
| Average exposure | 1.39% |
| Turnover (1-way, per year) | 1.16 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2012 | 0.83% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 250 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2012-01-03..2012-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 996653.80 |
| equity_complete | pass | chart rows 250 vs algorithm days 250 |
| equity_matches_qc_tradeable_dates | pass | chart rows 250 vs QuantConnect tradeableDates 250 |
| no_leverage | pass | min cash/equity 0.945373; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.0828430248158542e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 47 orders vs QuantConnect Total Orders 47 |
| fills_match_harness_count | pass | downloaded fill events 46 vs harness-recorded fills 46 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | warn | 4 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 46 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `c9f5d756fb982ff1bc77040da9ad795209934ab168048bab48461a888fa3eb02`
- fills_sha256: `72d593159a324fb60be5a97b549ae30f4636999cc7d638caa4bf2d77d94d92e1`
- trades_sha256: `98a648a71e67615fc8ff2abc78b9b9cee92a4dae10a0a36d311113960385b6d8`
