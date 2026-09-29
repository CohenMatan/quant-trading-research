# E950-07 — X950 v1.0 (infrastructure)

Execution-timing canary under the 2010 scheme and the fixed $7/order commission (D039): verifies T+1 open fills, slippage, and that every executed order is charged exactly $7. Re-run of E950-04 under the D051 no-borrowing execution model. | D057/D059 harness re-verification (replaces E950-06)

- **Status:** completed
- **Split:** FULL (2010-01-04 → 2021-12-31)
- **Commit:** `9716444b7a09bdc5b0df368971def31bf26d03d1` · **QC backtest:** `8817853e623717b8b2f270ee664b10d3` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T13:22:18Z · **runtime:** 40s
- **Parameters:** `{'weight': 0.24}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': "D039: $7 per executed buy or sell order (owner's broker); slippage separate"}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.25, 'cash_buffer': 0.02, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 2.31% |
| Annualised volatility | 8.26% |
| Sharpe (rf = 0) | 0.32 |
| Sortino | 0.45 |
| Max drawdown | -23.68% |
| Longest drawdown (trading days) | 1556 |
| Calmar | 0.10 |
| Worst year | -13.55% |
| Worst month | -6.70% |
| Closed trades | 1204 |
| Win rate | 51.33% |
| Average winner | 3.30% |
| Average loser | -3.33% |
| Expectancy per trade | 0.07% |
| Profit factor | 1.05 |
| Average holding (calendar days) | 14.5 |
| Average exposure | 45.55% |
| Turnover (1-way, per year) | 11.45 |

### Segment IS

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 2.43% |
| Annualised volatility | 7.09% |
| Sharpe (rf = 0) | 0.37 |
| Sortino | 0.53 |
| Max drawdown | -10.40% |
| Longest drawdown (trading days) | 675 |
| Calmar | 0.23 |
| Worst year | -3.97% |
| Worst month | -4.23% |
| Average exposure | 45.57% |
| Turnover (1-way, per year) | n/a |

### Segment VAL

| Metric | Value |
|---|---|
| Period | 2018-01-02 → 2021-12-31 (1008 trading days) |
| CAGR | 2.04% |
| Annualised volatility | 10.21% |
| Sharpe (rf = 0) | 0.25 |
| Sortino | 0.34 |
| Max drawdown | -20.47% |
| Longest drawdown (trading days) | 793 |
| Calmar | 0.10 |
| Worst year | -13.74% |
| Worst month | -6.70% |
| Average exposure | 45.50% |
| Turnover (1-way, per year) | n/a |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 5.01% |
| 2011 | 2.83% |
| 2012 | 6.07% |
| 2013 | 6.73% |
| 2014 | 2.85% |
| 2015 | -3.97% |
| 2016 | -1.53% |
| 2017 | 1.85% |
| 2018 | -13.55% |
| 2019 | 11.25% |
| 2020 | 1.21% |
| 2021 | 11.61% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 94761.17 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.147475; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.9465308380415215e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 2420 orders vs QuantConnect Total Orders 2420 |
| fills_match_harness_count | pass | downloaded fill events 2412 vs harness-recorded fills 2412 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 2412 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `e98cd376cf48b5d0865432db30a75d7ae67b9219b90af66225162c3c3cc544ad`
- fills_sha256: `075fe0d9ca352eabc1f86f6df3578e099a7272119f6013bca80984f897b4ccda`
- trades_sha256: `1ecc670350be1c1151aacbc909de0b25fab2d0c69196c22cabf7663d2ebf14e2`
