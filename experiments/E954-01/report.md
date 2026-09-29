# E954-01 — X954 v1.0 (infrastructure)

Post-2010 survivorship gap (D043): later-ended securities without fundamentals, by year; bias direction via forward returns in IS years only.

- **Status:** completed
- **Split:** AUDIT (2009-09-01 → 2021-12-31)
- **Commit:** `b5d59a622ca24f5feaf910a6511b6b17285ab453` · **QC backtest:** `2116749971e15fc0c4d16b77e52c27c9` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T11:10:48Z · **runtime:** 1714s
- **Parameters:** `{'eval_from': '2010-01-01', 'forward_returns_until': '2017-12-31'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': "D039: $7 per executed buy or sell order (owner's broker); slippage separate"}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 1.0, 'cash_buffer': 0.02}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2009-09-01 → 2021-12-31 (3106 trading days) |
| CAGR | 0.00% |
| Annualised volatility | 0.00% |
| Sharpe (rf = 0) | n/a |
| Sortino | n/a |
| Max drawdown | 0.00% |
| Longest drawdown (trading days) | 0 |
| Calmar | n/a |
| Worst year | 0.00% |
| Worst month | 0.00% |
| Closed trades | 0 |
| Win rate | n/a |
| Average winner | n/a |
| Average loser | n/a |
| Expectancy per trade | n/a |
| Profit factor | n/a |
| Average holding (calendar days) | n/a |
| Average exposure | 0.00% |
| Turnover (1-way, per year) | 0.00 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2009 | 0.00% |
| 2010 | 0.00% |
| 2011 | 0.00% |
| 2012 | 0.00% |
| 2013 | 0.00% |
| 2014 | 0.00% |
| 2015 | 0.00% |
| 2016 | 0.00% |
| 2017 | 0.00% |
| 2018 | 0.00% |
| 2019 | 0.00% |
| 2020 | 0.00% |
| 2021 | 0.00% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3106 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2009-09-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 100000.00 |
| equity_complete | pass | chart rows 3106 vs algorithm days 3106 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3106 vs QuantConnect tradeableDates 3106 |
| no_leverage | pass | min cash/equity 1.0000 |
| cash_never_negative | pass | min cash/equity 1.0000 |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=0.0 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 0 orders vs QuantConnect Total Orders 0 |
| fills_match_harness_count | pass | downloaded fill events 0 vs harness-recorded fills 0 |
| commission_fixed_per_order | pass | no fills downloaded; harness recorded 0 fills |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `f2ab5702f545ba765341e69caa3a7b6b63eb73d7202de1a784a0e019d829072a`
- fills_sha256: `78a0962b9b70b6901d01d783a235cdae962b1dffa5be70026c022bbbddabc973`
- trades_sha256: `7099cb2261e2e834b28abe20af9c8e05779781d921eadddafc5db983545e4c35`
