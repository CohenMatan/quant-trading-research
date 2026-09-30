# E008-01 — S008 v1.0 (research)

C02 H008 S008 v1.0 (pre-declared selection candidate, D069) on IS 2010-2017: base: 12-1 month residual return, volatility-scaled

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `20a28f57ffab551b71ee45470ca31727458a936e` · **QC backtest:** `84654b17f30c7dd2f745d5e8ca1f5d91` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T22:41:57Z · **runtime:** 1017s
- **Parameters:** `{'window': 252, 'skip': 21, 'scaled': True, 'slots': 10, 'keep': 20}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 9.17% |
| Annualised volatility | 18.41% |
| Sharpe (rf = 0) | 0.57 |
| Sortino | 0.79 |
| Max drawdown | -26.15% |
| Longest drawdown (trading days) | 547 |
| Calmar | 0.35 |
| Worst year | -3.61% |
| Worst month | -9.91% |
| Closed trades | 429 |
| Win rate | 55.48% |
| Average winner | 9.87% |
| Average loser | -8.66% |
| Expectancy per trade | 1.62% |
| Profit factor | 1.36 |
| Average holding (calendar days) | 64.3 |
| Average exposure | 88.52% |
| Turnover (1-way, per year) | 4.89 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -4.17% | 1.04 | 0.81 |
| E901-07 | -4.76% | 1.00 | 0.84 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 9.73% |
| 2011 | 6.70% |
| 2012 | 8.14% |
| 2013 | 31.43% |
| 2014 | -2.46% |
| 2015 | -3.61% |
| 2016 | 5.75% |
| 2017 | 21.79% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 91013.17 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.047225; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 4 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.6137604829183815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 868 orders vs QuantConnect Total Orders 868 |
| fills_match_harness_count | pass | downloaded fill events 868 vs harness-recorded fills 868 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 868 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `973a73efbc16cf1e33aa8f1a7b3f673922208afea2727b92982f857df8aa969b`
- fills_sha256: `ca65df1e4b4fcd22fcf8cc8252b54b3209639beb43171e8b7d1427acaa1d1d94`
- trades_sha256: `b2bdc1cc22ccacb0420b098ee5b07b18d42063c3a97008294297b6c8ffd76769`
