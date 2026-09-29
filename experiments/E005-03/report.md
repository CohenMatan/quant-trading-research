# E005-03 — S005 v1.2 (research)

C01 H005 S005 v1.2 (pre-declared variation) on IS 2010-2017

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `7f935852be241b2a919dc517a0f716315198c756` · **QC backtest:** `ce6e55305b99200c8ee2912787d2d886` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T13:54:57Z · **runtime:** 428s
- **Parameters:** `{'vol_days': 63, 'slots': 15, 'band': 0.25, 'require_positive_mom': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 10.99% |
| Annualised volatility | 8.16% |
| Sharpe (rf = 0) | 1.32 |
| Sortino | 1.94 |
| Max drawdown | -7.92% |
| Longest drawdown (trading days) | 143 |
| Calmar | 1.39 |
| Worst year | 5.80% |
| Worst month | -6.10% |
| Closed trades | 584 |
| Win rate | 61.30% |
| Average winner | 5.03% |
| Average loser | -3.85% |
| Expectancy per trade | 1.60% |
| Profit factor | 1.95 |
| Average holding (calendar days) | 68.9 |
| Average exposure | 92.96% |
| Turnover (1-way, per year) | 4.80 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-04 | -2.30% | 0.46 | 0.81 |
| E901-03 | -3.17% | 0.40 | 0.78 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 13.29% |
| 2011 | 13.37% |
| 2012 | 8.31% |
| 2013 | 19.35% |
| 2014 | 9.62% |
| 2015 | 9.92% |
| 2016 | 5.80% |
| 2017 | 8.59% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97780.80 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.0177 |
| cash_never_negative | pass | min cash/equity 0.0177 |
| fills_after_signal_date | pass | 0 violations, 76 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3862034721872065e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1182 orders vs QuantConnect Total Orders 1182 |
| fills_match_harness_count | pass | downloaded fill events 1182 vs harness-recorded fills 1182 |
| commission_fixed_per_order | pass | 1182 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `531a907855d2493c6546baef4481283c2e0aebb8cc249e355d7a5d360ac90be3`
- fills_sha256: `2253027cf2ec694275b6bdcaf43cfd1629ecc74389f2f364cc244dfc23b44372`
- trades_sha256: `e965bca90a7d01753fee6aee8db27d537cd68bcb4eef210330a287f002f3d7a4`
