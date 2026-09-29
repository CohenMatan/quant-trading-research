# E004-16 — S004 v1.3 (research)

C01 H004 S004 v1.3 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E004-04 under D051 with the D054 harness fix (replaces E004-12)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `7410367c71855d2f7c1cabe8057da3d01ef5b47a` · **QC backtest:** `87c26306caf18eda489a1832dfab1d95` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T09:28:14Z · **runtime:** 394s
- **Parameters:** `{'leader_frac': 0.2, 'drop': 0.05, 'hold_days': 10, 'slots': 15, 'regime_filter': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 2.96% |
| Annualised volatility | 18.69% |
| Sharpe (rf = 0) | 0.25 |
| Sortino | 0.35 |
| Max drawdown | -39.04% |
| Longest drawdown (trading days) | 965 |
| Calmar | 0.08 |
| Worst year | -24.91% |
| Worst month | -12.78% |
| Closed trades | 2296 |
| Win rate | 49.26% |
| Average winner | 6.38% |
| Average loser | -5.78% |
| Expectancy per trade | 0.21% |
| Profit factor | 1.04 |
| Average holding (calendar days) | 14.5 |
| Average exposure | 72.18% |
| Turnover (1-way, per year) | 18.51 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -10.38% | 0.80 | 0.62 |
| E901-05 | -10.78% | 0.81 | 0.66 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 5.97% |
| 2011 | -12.58% |
| 2012 | 14.64% |
| 2013 | 24.47% |
| 2014 | -24.91% |
| 2015 | -4.31% |
| 2016 | 9.58% |
| 2017 | 21.26% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 83842.06 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.029455; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3084730965147665e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 4612 orders vs QuantConnect Total Orders 4612 |
| fills_match_harness_count | pass | downloaded fill events 4606 vs harness-recorded fills 4606 |
| commission_fixed_per_order | pass | 4606 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `b4788304ce996b3e6cd5070c60a42164adb5448e268c17b32c6bb23817803785`
- fills_sha256: `790ca8080418acd70f8d863a3b41e8586a2bbd6a150320ba08f5e2bd058a32d1`
- trades_sha256: `d19d6bdaa28eafdfeefe2815fb39096861f5ae1a5fc12b04f21979837bce9a56`
