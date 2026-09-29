# E004-01 — S004 v1.0 (research)

C01 H004 S004 v1.0 (pre-declared variation) on IS 2010-2017

- **Status:** integrity_failed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `039b6aa157fca50658ee195fa4d503ca84bedb8b` · **QC backtest:** `fa783cfe42dfce4c9997327dfb555af4` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T13:18:12Z · **runtime:** 334s
- **Parameters:** `{'leader_frac': 0.2, 'drop': 0.05, 'hold_days': 10, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 0.21% |
| Annualised volatility | 24.19% |
| Sharpe (rf = 0) | 0.13 |
| Sortino | 0.18 |
| Max drawdown | -52.19% |
| Longest drawdown (trading days) | 965 |
| Calmar | 0.00 |
| Worst year | -22.69% |
| Worst month | -15.88% |
| Closed trades | 2805 |
| Win rate | 49.73% |
| Average winner | 6.31% |
| Average loser | -6.16% |
| Expectancy per trade | 0.04% |
| Profit factor | 0.98 |
| Average holding (calendar days) | 14.5 |
| Average exposure | 90.69% |
| Turnover (1-way, per year) | 22.87 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-04 | -13.07% | 1.29 | 0.76 |
| E901-03 | -13.94% | 1.26 | 0.82 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 21.48% |
| 2011 | -21.75% |
| 2012 | 12.56% |
| 2013 | 28.25% |
| 2014 | -22.69% |
| 2015 | -14.84% |
| 2016 | -0.04% |
| 2017 | 12.65% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 70034.68 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | FAIL | min cash/equity -0.0110 |
| cash_never_negative | warn | min cash/equity -0.0110 |
| fills_after_signal_date | pass | 0 violations, 1 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 5631 orders vs QuantConnect Total Orders 5631 |
| fills_match_harness_count | pass | downloaded fill events 5624 vs harness-recorded fills 5624 |
| commission_fixed_per_order | pass | 5624 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `0f71b8164d8d6945ddab2fcca2dcf72c1f07196830f6c92d294bb9f729bb62fb`
- fills_sha256: `b8d569d77102a51b65d1c2f371a026651b797889f341df8e69ec0fe3c1d0edfb`
- trades_sha256: `868a56e1be892dd943f8065c69def4db48bb2ffa1c8cfc3432bf3d6cd465d2b3`
