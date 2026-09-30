# E011-03 — S011 v1.2 (research)

C02 H011 S011 v1.2 (pre-declared selection candidate, D069) on IS 2010-2017: 5 annual lags, only stocks above SMA200

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `a52a714933e1dca227af9468269e1010631ea890` · **QC backtest:** `912f48b13ee14c796de51765feb56350` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T01:39:01Z · **runtime:** 1040s
- **Parameters:** `{'lags': 5, 'trend_filter': True, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 2.90% |
| Annualised volatility | 19.48% |
| Sharpe (rf = 0) | 0.24 |
| Sortino | 0.34 |
| Max drawdown | -41.74% |
| Longest drawdown (trading days) | 619 |
| Calmar | 0.07 |
| Worst year | -24.02% |
| Worst month | -18.26% |
| Closed trades | 882 |
| Win rate | 52.61% |
| Average winner | 8.64% |
| Average loser | -8.56% |
| Expectancy per trade | 0.49% |
| Profit factor | 1.06 |
| Average holding (calendar days) | 30.7 |
| Average exposure | 80.23% |
| Turnover (1-way, per year) | 9.54 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -10.44% | 1.04 | 0.76 |
| E901-07 | -11.02% | 1.01 | 0.80 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 10.12% |
| 2011 | -8.12% |
| 2012 | -12.86% |
| 2013 | 56.61% |
| 2014 | 15.62% |
| 2015 | 1.25% |
| 2016 | -24.02% |
| 2017 | 2.34% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 81099.61 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.042018; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 7 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.160079701089563e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1784 orders vs QuantConnect Total Orders 1784 |
| fills_match_harness_count | pass | downloaded fill events 1774 vs harness-recorded fills 1774 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1774 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `d8e858bb8e554a2c81efd0b10db240fc358ce2ee1dbbea2fb41fb2a0e7d1c0d2`
- fills_sha256: `218ddc077c69ef5a6cf148cb08cdeb1fc3e42acc4798430b771469ad6824dbfe`
- trades_sha256: `e0ab6774c5e0980bce6e03e28553d480d0bcec2b251709f21f75d10bf418591e`
