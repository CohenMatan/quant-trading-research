# E002-02 — S002 v1.1 (research)

C01 H002 S002 v1.1 (pre-declared variation) on IS 2010-2017

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `eabfec185ae0246b59f36dafa7a78d48988b7a24` · **QC backtest:** `c9808d15052feecb94a35ae45141f12d` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T12:16:59Z · **runtime:** 333s
- **Parameters:** `{'lookback': 126, 'skip': 21, 'every_months': 1, 'slots': 15, 'band': 0.25, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 13.18% |
| Annualised volatility | 25.53% |
| Sharpe (rf = 0) | 0.61 |
| Sortino | 0.86 |
| Max drawdown | -30.59% |
| Longest drawdown (trading days) | 540 |
| Calmar | 0.43 |
| Worst year | -11.16% |
| Worst month | -13.39% |
| Closed trades | 726 |
| Win rate | 56.34% |
| Average winner | 13.21% |
| Average loser | -11.60% |
| Expectancy per trade | 2.37% |
| Profit factor | 1.32 |
| Average holding (calendar days) | 57.4 |
| Average exposure | 95.02% |
| Turnover (1-way, per year) | 5.91 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-04 | -0.11% | 1.26 | 0.71 |
| E901-03 | -0.97% | 1.25 | 0.77 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 37.97% |
| 2011 | -11.16% |
| 2012 | 21.24% |
| 2013 | 50.14% |
| 2014 | -7.21% |
| 2015 | -0.64% |
| 2016 | 12.35% |
| 2017 | 16.25% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 94113.48 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.0079 |
| cash_never_negative | pass | min cash/equity 0.0079 |
| fills_after_signal_date | pass | 0 violations, 35 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.104451794696012e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1519 orders vs QuantConnect Total Orders 1519 |
| fills_match_harness_count | pass | downloaded fill events 1518 vs harness-recorded fills 1518 |
| commission_fixed_per_order | pass | 1518 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `a98d78a6b3989cdd9ff7446cce042244aaf36f2a1106faac04907a6af596a696`
- fills_sha256: `a2a14713963b609bacb36463176edcf00c899e7d2c082b707f1bb03e52e78917`
- trades_sha256: `dd26cda0d7c67aab5fd988c83c603169d7e58040a0a5bb8245715ae30dd31715`
