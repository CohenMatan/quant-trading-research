# E005-20 — S005 v1.2 (research)

C01 robustness of E005-12: plateau vol_days 76 (base 63) (pre-declared in research/cycles/C01_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `81eb215aa63edd689956543b7578e96374b39b4f` · **QC backtest:** `13fe4be5dd3bf744a92d82a082f36715` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T10:46:53Z · **runtime:** 456s
- **Parameters:** `{'vol_days': 76, 'slots': 15, 'band': 0.25, 'require_positive_mom': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 8.07% |
| Annualised volatility | 6.15% |
| Sharpe (rf = 0) | 1.29 |
| Sortino | 1.92 |
| Max drawdown | -6.60% |
| Longest drawdown (trading days) | 134 |
| Calmar | 1.22 |
| Worst year | 3.72% |
| Worst month | -3.73% |
| Closed trades | 372 |
| Win rate | 65.86% |
| Average winner | 5.13% |
| Average loser | -4.16% |
| Expectancy per trade | 1.96% |
| Profit factor | 2.32 |
| Average holding (calendar days) | 83.8 |
| Average exposure | 69.93% |
| Turnover (1-way, per year) | 2.93 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -5.27% | 0.33 | 0.76 |
| E901-05 | -5.67% | 0.29 | 0.73 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 7.10% |
| 2011 | 10.48% |
| 2012 | 3.72% |
| 2013 | 17.54% |
| 2014 | 4.75% |
| 2015 | 9.82% |
| 2016 | 5.78% |
| 2017 | 5.89% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97532.58 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.065045; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 58 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.913330198470113e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 757 orders vs QuantConnect Total Orders 757 |
| fills_match_harness_count | pass | downloaded fill events 757 vs harness-recorded fills 757 |
| commission_fixed_per_order | pass | 757 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `6f3ffdb106ca8bce4b07b429d895cff621f8f8c64a7df3cd2158abd3e8796c2c`
- fills_sha256: `c7b7fda6ec2c82796e5127c35bfacbc7d8a6b8331fbdae628652a95f42992129`
- trades_sha256: `63efdfafd8f27a82d0331c81df54bc2b2666078de23ec8fd77ad2a5e7c401362`
