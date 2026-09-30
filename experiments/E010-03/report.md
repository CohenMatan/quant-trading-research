# E010-03 — S010 v1.2 (research)

C02 H010 S010 v1.2 (pre-declared selection candidate, D069) on IS 2010-2017: no hold condition (close >= open not required)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `9bf2e4f4617df5a73bdc58a022c972720011ec53` · **QC backtest:** `d436f0b69b242bec4d99242631b17720` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T00:48:59Z · **runtime:** 996s
- **Parameters:** `{'min_gap': 0.02, 'gap_atr': 1.5, 'require_hold': False, 'vol_mult': 2.0, 'hold': 40, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 6.14% |
| Annualised volatility | 13.34% |
| Sharpe (rf = 0) | 0.51 |
| Sortino | 0.70 |
| Max drawdown | -21.49% |
| Longest drawdown (trading days) | 433 |
| Calmar | 0.29 |
| Worst year | -9.78% |
| Worst month | -9.34% |
| Closed trades | 871 |
| Win rate | 34.56% |
| Average winner | 8.99% |
| Average loser | -3.92% |
| Expectancy per trade | 0.55% |
| Profit factor | 1.19 |
| Average holding (calendar days) | 29.9 |
| Average exposure | 86.13% |
| Turnover (1-way, per year) | 10.20 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -7.20% | 0.71 | 0.77 |
| E901-07 | -7.78% | 0.68 | 0.79 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | -0.01% |
| 2011 | -8.89% |
| 2012 | 17.57% |
| 2013 | 13.85% |
| 2014 | 12.45% |
| 2015 | -9.78% |
| 2016 | 12.96% |
| 2017 | 15.18% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 88395.34 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.029894; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 4 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1751 orders vs QuantConnect Total Orders 1751 |
| fills_match_harness_count | pass | downloaded fill events 1751 vs harness-recorded fills 1751 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1751 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `3c963dd00ff64be96e6ecec59b2a7cf55a6b8302245ce6c7d2bacaaa911b28b3`
- fills_sha256: `9ee4ae0c036ffbe9a3d875696fe8b5c74c797bb5181e8531c69766b497ef40ca`
- trades_sha256: `503247b00e8ad99d6e1ada38e577caae896944243857c1475d103725cc4faba1`
