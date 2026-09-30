# E009-02 — S009 v1.1 (research)

C02 H009 S009 v1.1 (pre-declared selection candidate, D069) on IS 2010-2017: 1-day volume shock, hold 40

- **Status:** completed_with_warnings
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `ca8d3b657e11d2541cd6cbe9e69bfcdbb4bf4d76` · **QC backtest:** `14d0c59039fea24d7d2fc2ad42fb33f6` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T23:52:50Z · **runtime:** 606s
- **Parameters:** `{'vol_mult': 2.5, 'days': 1, 'hold': 40, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 14.37% |
| Annualised volatility | 14.36% |
| Sharpe (rf = 0) | 1.01 |
| Sortino | 1.46 |
| Max drawdown | -20.73% |
| Longest drawdown (trading days) | 252 |
| Calmar | 0.69 |
| Worst year | -1.38% |
| Worst month | -14.46% |
| Closed trades | 482 |
| Win rate | 59.54% |
| Average winner | 8.07% |
| Average loser | -6.92% |
| Expectancy per trade | 2.00% |
| Profit factor | 1.57 |
| Average holding (calendar days) | 57.6 |
| Average exposure | 90.58% |
| Turnover (1-way, per year) | 5.77 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | 1.03% | 0.76 | 0.76 |
| E901-07 | 0.44% | 0.74 | 0.80 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 28.41% |
| 2011 | 6.37% |
| 2012 | -1.38% |
| 2013 | 38.80% |
| 2014 | 11.68% |
| 2015 | 7.09% |
| 2016 | 10.24% |
| 2017 | 18.51% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 95984.59 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.031262; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 28 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.057976964382307e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 975 orders vs QuantConnect Total Orders 975 |
| fills_match_harness_count | pass | downloaded fill events 973 vs harness-recorded fills 973 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | warn | 1 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 1 mirrored |
| commission_fixed_per_order | pass | 974 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `7cf676a3aff7ea1d97468e15f209043cda67155ae0e1247582d40588535ca976`
- fills_sha256: `ca0e971614c40a25eb2955c5f506d5bdb6a3262c905f77b8005e7ce84da54c72`
- trades_sha256: `7f7fbd56eaf0eebd819f261e52d45ee4e0b9b05e1339d37f71cae72f5ddcb5dd`
