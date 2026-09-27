# E900-02 — B900 v1.0 (benchmark)

Benchmark: SPY buy-and-hold, dividends reinvested monthly. Re-run of E900-01: the QR equity chart was read before QC finished building it (runner fix).

- **Status:** completed
- **Split:** FULL (1999-01-04 → 2021-12-31)
- **Commit:** `ee2d4ac5ad8b2a0da1b53214abc8b251ed16771a` · **QC backtest:** `b6970d3e4387e85c41851897a4671b4d` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-27T21:26:24Z · **runtime:** 21s
- **Parameters:** `{'weight': 0.98}`
- **Costs:** `{'slippage_bps': 10, 'commission': 'IB fixed via LEAN InteractiveBrokersFeeModel: $0.005/share, $1 min, 1% max'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 1.0, 'cash_buffer': 0.02}`

## Metrics

| Metric | Value |
|---|---|
| Period | 1999-01-04 → 2021-12-31 (5788 trading days) |
| CAGR | 7.84% |
| Annualised volatility | 18.83% |
| Sharpe (rf = 0) | 0.50 |
| Sortino | 0.70 |
| Max drawdown | -54.38% |
| Longest drawdown (trading days) | 1656 |
| Calmar | 0.14 |
| Worst year | -36.18% |
| Worst month | -16.31% |
| Closed trades | 0 |
| Win rate | n/a |
| Average winner | n/a |
| Average loser | n/a |
| Expectancy per trade | n/a |
| Profit factor | n/a |
| Average holding (calendar days) | n/a |
| Average exposure | 97.86% |
| Turnover (1-way, per year) | 0.02 |

### Segment IS

| Metric | Value |
|---|---|
| Period | 1999-01-04 → 2014-12-31 (4025 trading days) |
| CAGR | 5.04% |
| Annualised volatility | 19.48% |
| Sharpe (rf = 0) | 0.35 |
| Sortino | 0.50 |
| Max drawdown | -54.38% |
| Longest drawdown (trading days) | 1656 |
| Calmar | 0.09 |
| Worst year | -36.18% |
| Worst month | -16.31% |
| Average exposure | 97.85% |
| Turnover (1-way, per year) | n/a |

### Segment VAL

| Metric | Value |
|---|---|
| Period | 2015-01-02 → 2021-12-31 (1763 trading days) |
| CAGR | 14.56% |
| Annualised volatility | 17.28% |
| Sharpe (rf = 0) | 0.87 |
| Sortino | 1.21 |
| Max drawdown | -33.05% |
| Longest drawdown (trading days) | 187 |
| Calmar | 0.44 |
| Worst year | -4.43% |
| Worst month | -12.26% |
| Average exposure | 97.90% |
| Turnover (1-way, per year) | n/a |

## Calendar-year returns

| Year | Return |
|---|---|
| 1999 | 20.17% |
| 2000 | -8.82% |
| 2001 | -11.77% |
| 2002 | -21.60% |
| 2003 | 27.45% |
| 2004 | 10.72% |
| 2005 | 4.64% |
| 2006 | 15.36% |
| 2007 | 5.25% |
| 2008 | -36.18% |
| 2009 | 25.66% |
| 2010 | 14.79% |
| 2011 | 1.86% |
| 2012 | 15.72% |
| 2013 | 31.42% |
| 2014 | 13.19% |
| 2015 | 1.30% |
| 2016 | 11.73% |
| 2017 | 21.20% |
| 2018 | -4.43% |
| 2019 | 30.52% |
| 2020 | 18.03% |
| 2021 | 28.07% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 5788 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 1999-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 65781.63 |
| equity_complete | pass | chart rows 5788 vs algorithm days 5788 |
| no_leverage | pass | min cash/equity 0.0170 |
| cash_never_negative | pass | min cash/equity 0.0170 |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.729208065967196e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `2bb70ad513323503714f250043daa45763b7682c3b8541ded85e6c87fe6e6011`
- fills_sha256: `746b0d9327956571dd3d36de782de7452534a5bcc9677b262a470806cda5d2ca`
- trades_sha256: `984c49829be77892db7b5a87a298f4e194f8acd6844b6d23738640385e240fb6`
