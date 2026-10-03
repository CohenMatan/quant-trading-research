# E017-02 — S017 v1.0 (benchmark)

P2 EW-H017: equal weight of the exact H017 universe (eligible and a verified domestic 8-K earnings filer), monthly, 25% band (B901 mechanics), $10M paper notional. W3. Pre-declared in research/phase2/H017_spec.md (frozen 2026-10-03).

- **Status:** completed_with_warnings
- **Split:** DEV (2010-03-01 → 2021-12-31)
- **Commit:** `2a89aba1647d283779fd2f7d8e0defa198567948` · **QC backtest:** `534cd35e313b4d55722d65a19fb8a99a` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-03T18:26:55Z · **runtime:** 901s
- **Parameters:** `{'slots': 10, 'hold_sessions': 60, 'quantile': 0.9, 'reaction_lag': 1, 'book': 'ew', 'band': 0.25}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 1.0, 'cash_buffer': 0.02, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2021-12-31 (2983 trading days) |
| CAGR | 13.03% |
| Annualised volatility | 17.89% |
| Sharpe (rf = 0) | 0.77 |
| Sortino | 1.07 |
| Max drawdown | -37.95% |
| Longest drawdown (trading days) | 288 |
| Calmar | 0.34 |
| Worst year | -8.81% |
| Worst month | -18.77% |
| Closed trades | 3880 |
| Win rate | 21.83% |
| Average winner | 44.01% |
| Average loser | -16.81% |
| Expectancy per trade | -3.53% |
| Profit factor | 0.63 |
| Average holding (calendar days) | 404.6 |
| Average exposure | 94.59% |
| Turnover (1-way, per year) | 0.36 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -1.85% | 1.03 | 0.96 |
| E901-07 | -0.35% | 1.00 | 1.00 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 17.81% |
| 2011 | -0.42% |
| 2012 | 16.12% |
| 2013 | 34.98% |
| 2014 | 10.54% |
| 2015 | -2.30% |
| 2016 | 13.88% |
| 2017 | 18.10% |
| 2018 | -8.81% |
| 2019 | 26.44% |
| 2020 | 17.93% |
| 2021 | 17.37% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2983 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 9334203.39 |
| equity_complete | pass | chart rows 2983 vs algorithm days 2983 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2983 vs QuantConnect tradeableDates 2983 |
| warmup_left_account_untouched | pass | first recorded equity 10000000.00 vs initial cash 10000000.00; 166 warm-up sessions |
| no_leverage | pass | min cash/equity 0.035780; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 475 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.4962832304260223e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 23223 orders vs QuantConnect Total Orders 23223 |
| fills_match_harness_count | pass | downloaded fill events 23210 vs harness-recorded fills 23210 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | warn | 11 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 11 mirrored |
| commission_fixed_per_order | pass | 23221 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `20955828af33bd7be1e5b31a861ecc5f5bc959f3cf75f915238eb12b03f53b1a`
- fills_sha256: `e5b10feb9aae8d143de2df3fa9f2feff7a325515f8f5e6d17bae4b36437b369c`
- trades_sha256: `83318d90477686646e9046ba6c4df8de92cdac6a4f350c620a08703e9dbe32fd`
