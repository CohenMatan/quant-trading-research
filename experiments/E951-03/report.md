# E951-03 — X951 v1.0 (infrastructure)

Data audit on the NEW Morningstar dataset (LEAN 18131) with the exchange filter fixed for the new codes (NYSE/AMEX). Supersedes E951-02's n_ge2b/n_elig counts.

- **Status:** completed
- **Split:** FULL (1999-01-04 → 2021-12-31)
- **Commit:** `4ac91f20a5ce38134d613233ed4b78a14b03f796` · **QC backtest:** `6eda8828d24a84091122fc5f20112f77` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-27T21:09:37Z · **runtime:** 213s
- **Parameters:** `{}`
- **Costs:** `{'slippage_bps': 10, 'commission': 'IB fixed via LEAN InteractiveBrokersFeeModel: $0.005/share, $1 min, 1% max'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02}`

## Metrics

| Metric | Value |
|---|---|
| Period | 1999-01-04 → 2021-12-31 (5788 trading days) |
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

### Segment IS

| Metric | Value |
|---|---|
| Period | 1999-01-04 → 2014-12-31 (4025 trading days) |
| CAGR | 0.00% |
| Annualised volatility | 0.00% |
| Sharpe (rf = 0) | n/a |
| Sortino | n/a |
| Max drawdown | 0.00% |
| Longest drawdown (trading days) | 0 |
| Calmar | n/a |
| Worst year | 0.00% |
| Worst month | 0.00% |
| Average exposure | 0.00% |
| Turnover (1-way, per year) | n/a |

### Segment VAL

| Metric | Value |
|---|---|
| Period | 2015-01-02 → 2021-12-31 (1763 trading days) |
| CAGR | 0.00% |
| Annualised volatility | 0.00% |
| Sharpe (rf = 0) | n/a |
| Sortino | n/a |
| Max drawdown | 0.00% |
| Longest drawdown (trading days) | 0 |
| Calmar | n/a |
| Worst year | 0.00% |
| Worst month | 0.00% |
| Average exposure | 0.00% |
| Turnover (1-way, per year) | n/a |

## Calendar-year returns

| Year | Return |
|---|---|
| 1999 | 0.00% |
| 2000 | 0.00% |
| 2001 | 0.00% |
| 2002 | 0.00% |
| 2003 | 0.00% |
| 2004 | 0.00% |
| 2005 | 0.00% |
| 2006 | 0.00% |
| 2007 | 0.00% |
| 2008 | 0.00% |
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
| equity_nonempty | pass | 5788 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 1999-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 100000.00 |
| equity_complete | pass | chart rows 5788 vs algorithm days 5788 |
| no_leverage | pass | min cash/equity 1.0000 |
| cash_never_negative | pass | min cash/equity 1.0000 |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=0.0 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `822751a12d7d87fcc884d573180a21448b19a2457757550d1112ba4ec66d48e9`
- fills_sha256: `78a0962b9b70b6901d01d783a235cdae962b1dffa5be70026c022bbbddabc973`
- trades_sha256: `7099cb2261e2e834b28abe20af9c8e05779781d921eadddafc5db983545e4c35`
