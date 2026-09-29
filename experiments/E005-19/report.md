# E005-19 — S005 v1.2 (research)

C01 robustness of E005-12: plateau vol_days 50 (base 63) (pre-declared in research/cycles/C01_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `11be118f3389843f2b5e97061e741118a9b55540` · **QC backtest:** `83a310b00281b6f0c2c848eb5432fabe` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T10:39:41Z · **runtime:** 411s
- **Parameters:** `{'vol_days': 50, 'slots': 15, 'band': 0.25, 'require_positive_mom': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 8.19% |
| Annualised volatility | 5.46% |
| Sharpe (rf = 0) | 1.47 |
| Sortino | 2.24 |
| Max drawdown | -5.13% |
| Longest drawdown (trading days) | 119 |
| Calmar | 1.60 |
| Worst year | 2.08% |
| Worst month | -3.29% |
| Closed trades | 455 |
| Win rate | 63.74% |
| Average winner | 4.61% |
| Average loser | -3.36% |
| Expectancy per trade | 1.72% |
| Profit factor | 2.30 |
| Average holding (calendar days) | 65.3 |
| Average exposure | 65.35% |
| Turnover (1-way, per year) | 3.56 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -5.15% | 0.28 | 0.74 |
| E901-05 | -5.55% | 0.25 | 0.72 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 9.18% |
| 2011 | 9.52% |
| 2012 | 8.03% |
| 2013 | 14.34% |
| 2014 | 7.32% |
| 2015 | 10.89% |
| 2016 | 2.08% |
| 2017 | 4.49% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 98045.03 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.062373; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 94 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.017355591316655e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 920 orders vs QuantConnect Total Orders 920 |
| fills_match_harness_count | pass | downloaded fill events 920 vs harness-recorded fills 920 |
| commission_fixed_per_order | pass | 920 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `2a36cc4634947d20464c3e4c399391141f45edd6229ebf82b6a1c7cb3cac03db`
- fills_sha256: `235161e12a9b6671cc64231fc4580f2cae83ae9082a75a1162c740a3233d251f`
- trades_sha256: `e453814735ef7a21623c1c241182be1238c6dde0d31b03e9ee4a693f776277f4`
