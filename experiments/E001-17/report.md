# E001-17 — S001 v1.1 (research)

H001 remedial re-test after infrastructure correction (D057/D059/D063): S001 v1.1 exactly as pre-registered; identical to E001-12 except ID and harness

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `6ba55c19af5670bab586ffb3007ee6825a3097c8` · **QC backtest:** `415002fc6b81ac4a8a0ab0ab3dabc461` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T15:36:44Z · **runtime:** 859s
- **Parameters:** `{'entry': 'rsi', 'rsi_max': 5, 'exit': 'sma5', 'max_hold': 10, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | -3.80% |
| Annualised volatility | 7.63% |
| Sharpe (rf = 0) | -0.47 |
| Sortino | -0.65 |
| Max drawdown | -29.34% |
| Longest drawdown (trading days) | 1945 |
| Calmar | -0.13 |
| Worst year | -8.64% |
| Worst month | -7.32% |
| Closed trades | 2432 |
| Win rate | 52.47% |
| Average winner | 1.55% |
| Average loser | -2.23% |
| Expectancy per trade | -0.25% |
| Profit factor | 0.77 |
| Average holding (calendar days) | 4.7 |
| Average exposure | 25.06% |
| Turnover (1-way, per year) | 20.22 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -17.14% | 0.28 | 0.52 |
| E901-07 | -17.72% | 0.27 | 0.54 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | -8.64% |
| 2011 | -8.41% |
| 2012 | -5.15% |
| 2013 | 0.22% |
| 2014 | 3.66% |
| 2015 | -1.69% |
| 2016 | -3.85% |
| 2017 | -5.81% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 72149.76 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.044386; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 1 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 4877 orders vs QuantConnect Total Orders 4877 |
| fills_match_harness_count | pass | downloaded fill events 4865 vs harness-recorded fills 4865 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 4865 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `3b6234fd7996b18ef46844dbdeb81f27ab1097d72d336374eff9c53876e8715a`
- fills_sha256: `37bfce9ed56512a2bb5050d537e6f8741c2d7c9c334b95191489ea70b43408e6`
- trades_sha256: `ef1318ed050ef9d862c6f7d0437a4d29cd9e6c0ec847b9666dca944d6f04ed6d`
