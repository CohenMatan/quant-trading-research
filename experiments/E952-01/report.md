# E952-01 — X952 v1.0 (infrastructure)

Corporate actions and delistings: AAPL splits, KO/XOM dividends, ENE/WCOM/BSC/LEH delistings.

- **Status:** completed
- **Split:** IS (2001-01-02 → 2014-12-31)
- **Commit:** `54cfe3103a50c7c521f1e3f6cf6f6b6bff129a98` · **QC backtest:** `2db73e5ea070a2ebb76da3984e407b33` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-27T21:13:38Z · **runtime:** 20s
- **Parameters:** `{}`
- **Costs:** `{'slippage_bps': 10, 'commission': 'IB fixed via LEAN InteractiveBrokersFeeModel: $0.005/share, $1 min, 1% max'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2001-01-02 → 2014-12-31 (3521 trading days) |
| CAGR | 8.11% |
| Annualised volatility | 11.61% |
| Sharpe (rf = 0) | 0.73 |
| Sortino | 1.06 |
| Max drawdown | -30.90% |
| Longest drawdown (trading days) | 927 |
| Calmar | 0.26 |
| Worst year | -28.90% |
| Worst month | -13.39% |
| Closed trades | 4 |
| Win rate | 0.00% |
| Average winner | n/a |
| Average loser | -96.47% |
| Expectancy per trade | -96.47% |
| Profit factor | 0.00 |
| Average holding (calendar days) | 171.5 |
| Average exposure | 34.55% |
| Turnover (1-way, per year) | 0.01 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2001 | -3.93% |
| 2002 | -3.94% |
| 2003 | 0.00% |
| 2004 | 5.15% |
| 2005 | 11.19% |
| 2006 | 5.48% |
| 2007 | 28.36% |
| 2008 | -28.90% |
| 2009 | 31.80% |
| 2010 | 22.35% |
| 2011 | 13.84% |
| 2012 | 18.67% |
| 2013 | 5.65% |
| 2014 | 24.51% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3521 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2001-01-02..2014-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 92033.89 |
| equity_complete | pass | chart rows 3521 vs algorithm days 3521 |
| no_leverage | pass | min cash/equity 0.2594 |
| cash_never_negative | pass | min cash/equity 0.2594 |
| fills_after_signal_date | pass | 0 violations, 4 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.096995281705297e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `ca7982c984f5a77ac4ade13ec974f8ad2e004d04651143eb34798ecb564a3df2`
- fills_sha256: `ca9961fdc00dcad2ca3920ac9399f5e7a3f2ecfd150e1218e99afd320eab87d3`
- trades_sha256: `8a081b3bf9f6f8733bd2c6efc92ddf40428ef68dacfa13b638e6b4a1fb9d2e09`
