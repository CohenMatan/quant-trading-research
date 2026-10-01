# E014-25 — S014 v1.1 (sizing)

Technical repeat of E014-14 (identical configuration); E014-14's QC backtest never started (node out of disk). P2 $200K sensitivity (12 slots) of E014-02. Diagnostic, never used for selection. Pre-declared in research/phase2/P2_spec.md (frozen, D094).

- **Status:** completed
- **Split:** DEV (2010-01-04 → 2021-12-31)
- **Commit:** `04ff66b303a973d3ad45a78c3ec5afea818e674a` · **QC backtest:** `cbacaa5c5d0aeeee5077cef1a16e8478` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-01T14:28:20Z · **runtime:** 1513s
- **Parameters:** `{'mode': 'h014', 'exit': 'B', 'limit': 126, 'rsi_pullback': 40, 'window': 5, 'rsi_recovery': 45, 'slots': 12}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 14.97% |
| Annualised volatility | 22.79% |
| Sharpe (rf = 0) | 0.73 |
| Sortino | 1.02 |
| Max drawdown | -38.98% |
| Longest drawdown (trading days) | 469 |
| Calmar | 0.38 |
| Worst year | -15.94% |
| Worst month | -27.47% |
| Closed trades | 547 |
| Win rate | 37.48% |
| Average winner | 28.02% |
| Average loser | -9.61% |
| Expectancy per trade | 4.49% |
| Profit factor | 1.51 |
| Average holding (calendar days) | 92.5 |
| Average exposure | 93.14% |
| Turnover (1-way, per year) | 3.39 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | 0.38% | 0.94 | 0.68 |
| E901-07 | 1.49% | 0.90 | 0.70 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 35.10% |
| 2011 | 9.47% |
| 2012 | 12.00% |
| 2013 | 37.66% |
| 2014 | 8.76% |
| 2015 | -9.68% |
| 2016 | 6.96% |
| 2017 | 43.54% |
| 2018 | -15.94% |
| 2019 | 30.57% |
| 2020 | 23.27% |
| 2021 | 14.48% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 189193.15 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.019999; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 9 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.050748481174355e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1106 orders vs QuantConnect Total Orders 1106 |
| fills_match_harness_count | pass | downloaded fill events 1106 vs harness-recorded fills 1106 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1106 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `9b7c1eec6325de8acf3eec3e6590fe5bbecbebcf2d8a2533aa97be5e198282b3`
- fills_sha256: `ec936624da16212d4b846d0249cce617543fa3161ca4bceecb493a18f33695fb`
- trades_sha256: `c8abed9451b5b7757c2f00b46bf7643841a4e3a99f5dee93880501dfd11be22b`
