# E007-01 — S007 v1.0 (research)

C02 H007 S007 v1.0 (pre-declared selection candidate, D069) on IS 2010-2017: base: bandwidth contraction (lowest 10% of 250 sessions)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `1c721e9d49b357b72e752e55092cee13cf141a86` · **QC backtest:** `bac8abbe160daa2d8933a9561492e2b9` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T20:50:24Z · **runtime:** 939s
- **Parameters:** `{'setup': 'bandwidth', 'pct': 0.1, 'atr_ratio': 0.6, 'use_trend': True, 'time_stop': 40, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 5.99% |
| Annualised volatility | 11.64% |
| Sharpe (rf = 0) | 0.56 |
| Sortino | 0.77 |
| Max drawdown | -16.83% |
| Longest drawdown (trading days) | 620 |
| Calmar | 0.36 |
| Worst year | -4.24% |
| Worst month | -8.69% |
| Closed trades | 911 |
| Win rate | 42.26% |
| Average winner | 6.10% |
| Average loser | -3.78% |
| Expectancy per trade | 0.40% |
| Profit factor | 1.14 |
| Average holding (calendar days) | 25.6 |
| Average exposure | 76.84% |
| Turnover (1-way, per year) | 10.92 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -7.35% | 0.52 | 0.63 |
| E901-07 | -7.94% | 0.50 | 0.66 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 8.89% |
| 2011 | -0.40% |
| 2012 | 8.58% |
| 2013 | 21.07% |
| 2014 | 15.14% |
| 2015 | -4.24% |
| 2016 | -2.87% |
| 2017 | 4.23% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 91881.27 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.030032; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 17 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.480852778507996e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1833 orders vs QuantConnect Total Orders 1833 |
| fills_match_harness_count | pass | downloaded fill events 1832 vs harness-recorded fills 1832 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1832 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `a7802f392f0bf02f89072dfe0e43e484f89e8796650ab620407bd9aa530e0912`
- fills_sha256: `4b6dbf3696e999d681994ed654cc12febb2dcd8856b734045a616dbb274f37de`
- trades_sha256: `ade9f84c032065e91fab2b2a997430a7239295f8394f952f9a4f95afd7993522`
