# E959-03 — X959 v1.1 (infrastructure)

C02 infrastructure canary v1.1 re-run after the D072 volume-convention fix (E959-02 diagnosis). IS dates only. Infrastructure; not a trial.

- **Status:** completed
- **Split:** AUDIT (2014-01-02 → 2014-12-31)
- **Commit:** `df196d86a286127cf819a11e89bc4f6624ebd47e` · **QC backtest:** `4b4d8af525c6485dde4dbbbf5351735b` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T18:13:47Z · **runtime:** 108s
- **Parameters:** `{}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': "D039: $7 per executed buy or sell order (owner's broker); slippage separate"}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2014-01-02 → 2014-12-31 (252 trading days) |
| CAGR | -4.23% |
| Annualised volatility | 8.42% |
| Sharpe (rf = 0) | -0.47 |
| Sortino | -0.60 |
| Max drawdown | -9.13% |
| Longest drawdown (trading days) | 231 |
| Calmar | -0.46 |
| Worst year | -4.20% |
| Worst month | -4.20% |
| Closed trades | 202 |
| Win rate | 50.99% |
| Average winner | 2.95% |
| Average loser | -3.47% |
| Expectancy per trade | -0.20% |
| Profit factor | 0.87 |
| Average holding (calendar days) | 5.8 |
| Average exposure | 32.08% |
| Turnover (1-way, per year) | 20.20 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2014 | -4.20% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 252 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2014-01-02..2014-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 91313.65 |
| equity_complete | pass | chart rows 252 vs algorithm days 252 |
| equity_matches_qc_tradeable_dates | pass | chart rows 252 vs QuantConnect tradeableDates 252 |
| no_leverage | pass | min cash/equity 0.489823; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 406 orders vs QuantConnect Total Orders 406 |
| fills_match_harness_count | pass | downloaded fill events 405 vs harness-recorded fills 405 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 405 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `aef6b8555a40ef94d620fa1166fcc68367ccc3d1a1f8ac34982f9e8681d7a1a2`
- fills_sha256: `a2d39678f7308a0f276763996ddba7a69c84ed8321df1589fdad491556ce57de`
- trades_sha256: `aa656b028b69bd3d3b7568cd8add59e8e25aef7761c55a76488dc98b18b75f7f`
