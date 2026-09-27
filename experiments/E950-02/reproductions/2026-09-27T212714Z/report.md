# E950-02 — X950 v1.0 (infrastructure)

Execution-timing canary: verifies T+1 open fills, raw prices, slippage, on 8 large caps. Re-run of E950-01: the QR equity chart was read before QC finished building it (runner fix).

- **Status:** completed
- **Split:** FULL (1999-01-04 → 2021-12-31)
- **Commit:** `f7c11152381102341108a3386570e328b2997002` · **QC backtest:** `07172999dfb5001bf15226d4de121bad` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-27T21:27:14Z · **runtime:** 24s
- **Parameters:** `{'weight': 0.24}`
- **Costs:** `{'slippage_bps': 10, 'commission': 'IB fixed via LEAN InteractiveBrokersFeeModel: $0.005/share, $1 min, 1% max'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.25, 'cash_buffer': 0.02}`

## Metrics

| Metric | Value |
|---|---|
| Period | 1999-01-04 → 2021-12-31 (5788 trading days) |
| CAGR | 7.27% |
| Annualised volatility | 20.80% |
| Sharpe (rf = 0) | 0.44 |
| Sortino | 0.64 |
| Max drawdown | -51.81% |
| Longest drawdown (trading days) | 1507 |
| Calmar | 0.14 |
| Worst year | -28.41% |
| Worst month | -14.06% |
| Closed trades | 2312 |
| Win rate | 51.60% |
| Average winner | 4.00% |
| Average loser | -3.72% |
| Expectancy per trade | 0.26% |
| Profit factor | 1.13 |
| Average holding (calendar days) | 14.5 |
| Average exposure | 96.11% |
| Turnover (1-way, per year) | 24.18 |

### Segment IS

| Metric | Value |
|---|---|
| Period | 1999-01-04 → 2014-12-31 (4025 trading days) |
| CAGR | 5.76% |
| Annualised volatility | 21.56% |
| Sharpe (rf = 0) | 0.37 |
| Sortino | 0.53 |
| Max drawdown | -51.81% |
| Longest drawdown (trading days) | 1507 |
| Calmar | 0.11 |
| Worst year | -28.41% |
| Worst month | -14.06% |
| Average exposure | 96.11% |
| Turnover (1-way, per year) | n/a |

### Segment VAL

| Metric | Value |
|---|---|
| Period | 2015-01-02 → 2021-12-31 (1763 trading days) |
| CAGR | 10.87% |
| Annualised volatility | 18.99% |
| Sharpe (rf = 0) | 0.64 |
| Sortino | 0.91 |
| Max drawdown | -29.66% |
| Longest drawdown (trading days) | 349 |
| Calmar | 0.37 |
| Worst year | -5.97% |
| Worst month | -13.16% |
| Average exposure | 96.10% |
| Turnover (1-way, per year) | n/a |

## Calendar-year returns

| Year | Return |
|---|---|
| 1999 | 42.72% |
| 2000 | 6.39% |
| 2001 | -5.66% |
| 2002 | -19.64% |
| 2003 | 20.11% |
| 2004 | 17.13% |
| 2005 | 4.32% |
| 2006 | 15.33% |
| 2007 | 14.33% |
| 2008 | -28.41% |
| 2009 | 16.85% |
| 2010 | 12.03% |
| 2011 | -7.51% |
| 2012 | 8.82% |
| 2013 | 21.26% |
| 2014 | -3.87% |
| 2015 | -4.70% |
| 2016 | 14.98% |
| 2017 | 0.74% |
| 2018 | -5.97% |
| 2019 | 31.05% |
| 2020 | 22.76% |
| 2021 | 22.77% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 5788 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 1999-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 95625.82 |
| equity_complete | pass | chart rows 5788 vs algorithm days 5788 |
| no_leverage | pass | min cash/equity 0.0128 |
| cash_never_negative | pass | min cash/equity 0.0128 |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.4962832304260223e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `d36dd5b51503f9d3f7aaece6b85591d1b34e092e36c891451b53518c8dd6fa04`
- fills_sha256: `5c747946558139cf4a160e63637d82b352ed78af6dda03e3e1ba3e5b31c95932`
- trades_sha256: `459e5e3dec510ab94a3db1a6e793d597a398694235cec1c2963d6ead67d11475`

## Reproduction

- Original backtest: `888d5ef73d5a30ae2aa040d3b0ecf3dd`
- Identical: **True** {'equity_sha256': True, 'fills_sha256': True, 'trades_sha256': True}
