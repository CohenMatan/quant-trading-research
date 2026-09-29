# E001-20 — S001 v1.4 (research)

H001 remedial re-test after infrastructure correction (D057/D059/D063): S001 v1.4 exactly as pre-registered; identical to E001-15 except ID and harness

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `61607b350e35c7651067f57d32409134fd9c2a5d` · **QC backtest:** `f9ad9e7ff419a5bb3e212fce97895e0b` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T16:10:14Z · **runtime:** 448s
- **Parameters:** `{'entry': 'ret3', 'ret3_max': -0.06, 'exit': 'sma5', 'max_hold': 10, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | -5.60% |
| Annualised volatility | 16.45% |
| Sharpe (rf = 0) | -0.27 |
| Sortino | -0.38 |
| Max drawdown | -50.55% |
| Longest drawdown (trading days) | 1658 |
| Calmar | -0.11 |
| Worst year | -19.02% |
| Worst month | -17.18% |
| Closed trades | 3521 |
| Win rate | 55.61% |
| Average winner | 3.08% |
| Average loser | -4.25% |
| Expectancy per trade | -0.17% |
| Profit factor | 0.90 |
| Average holding (calendar days) | 6.4 |
| Average exposure | 50.31% |
| Turnover (1-way, per year) | 29.05 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -18.95% | 0.73 | 0.64 |
| E901-07 | -19.53% | 0.72 | 0.68 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 12.48% |
| 2011 | -4.16% |
| 2012 | -8.73% |
| 2013 | 5.69% |
| 2014 | -19.02% |
| 2015 | -2.69% |
| 2016 | -16.40% |
| 2017 | -7.88% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 60203.20 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.031828; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 2 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.6303945933115617e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 7051 orders vs QuantConnect Total Orders 7051 |
| fills_match_harness_count | pass | downloaded fill events 7044 vs harness-recorded fills 7044 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 7044 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `818e4223bb764efff9c83bd72a2e5e112830ec604b3c1e9b7637e20baa17b788`
- fills_sha256: `2f4dc89745e167921f15e5db2934d54f816e122158906d168cfae184f4c217c3`
- trades_sha256: `223a3311963cafbfa8ced4c9dc9f299260fabc73bd5b544aa5a7a14c66ea5f14`
