# E006-01 — S006 v1.0 (research)

C02 H006 S006 v1.0 (pre-declared selection candidate, D069) on IS 2010-2017: base: 55-day high, volume >= 1.5x

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `5e7c42c71319717ce81b3d7fe16e9ccd4868864c` · **QC backtest:** `3f81fd0f705b0c989ccefef435b4f07d` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T20:11:01Z · **runtime:** 685s
- **Parameters:** `{'n': 55, 'vol_mult': 1.5, 'use_volume': True, 'k': 3.0, 'time_stop': 60, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 12.19% |
| Annualised volatility | 14.22% |
| Sharpe (rf = 0) | 0.88 |
| Sortino | 1.26 |
| Max drawdown | -19.29% |
| Longest drawdown (trading days) | 401 |
| Calmar | 0.63 |
| Worst year | -3.11% |
| Worst month | -10.15% |
| Closed trades | 529 |
| Win rate | 46.12% |
| Average winner | 10.59% |
| Average loser | -6.07% |
| Expectancy per trade | 1.61% |
| Profit factor | 1.46 |
| Average holding (calendar days) | 51.9 |
| Average exposure | 91.06% |
| Turnover (1-way, per year) | 6.23 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -1.15% | 0.72 | 0.73 |
| E901-07 | -1.73% | 0.69 | 0.75 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 14.71% |
| 2011 | -3.11% |
| 2012 | 15.77% |
| 2013 | 36.56% |
| 2014 | 7.49% |
| 2015 | 4.18% |
| 2016 | 11.91% |
| 2017 | 13.80% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 95980.06 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.024836; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 14 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.069879566903419e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1068 orders vs QuantConnect Total Orders 1068 |
| fills_match_harness_count | pass | downloaded fill events 1066 vs harness-recorded fills 1066 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1066 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `4b19376c5f423c86d5e15bcaf0772ce1d9582134f0fd925a38d92daabf5f9858`
- fills_sha256: `8bf7ebd005ecd0aaddaf03937394d3fd6ab358fa7dfab0226cf5d2389e25b597`
- trades_sha256: `483a351cae36b803d3ce163e87f32af0d480825212f810b9073b842d96bfa914`
