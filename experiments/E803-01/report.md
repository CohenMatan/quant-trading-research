# E803-01 — X803 v1.0 (infrastructure)

P14-CP2 (owner D229): Data v3 audit (X803 audit mode) on frozen Data v2.1 + the guard-v3 table: guard-v3 provenance / blocks of every fed vendor version, the H029 v3 view, the six H029 signals live at each of the 131 reviews 2011-01 .. 2021-11 (U_H029 coverage, >= 5 of 6), stratified SEC validation (rank materiality), F7 split comparability, PIT checks, v2.1 differences, per-review panel digests. NO return, IC, wealth or feature-return statistic. Infrastructure. Default build.

- **Status:** completed
- **Split:** AUDIT (2011-01-03 → 2021-12-31)
- **Commit:** `c5b3b2194145f47b02324d8219b317ed7c92d845` · **QC backtest:** `6eb4f7a30b1d9393cf439dc50c262378` · **LEAN:** v2.5.0.0.18179 · **run:** 2026-10-12T21:13:54Z · **runtime:** 862s
- **Parameters:** `{'mode': 'audit', 'spec_sha256': 'b4b8aa9b1c212e98bdf1aea7ed3ed577be21d9d1c195fa06ff54764452ab73d0', 'v3_code_sha256': '40bcf98d3aa62f625faa5c1f97a18c08d5a0d0d40bd9afcf300f5bf67fdcaccd', 'guard_sha256': 'd4e1065baec3786d29d30397cf21fc7f8d298b52455e8b1f156b377bd680996a', 'val_sha256': '2dbec426034970661526b7ab6e9774df0231022caf79e3c36ef8eccba9aed97b', 'data_v21_manifest_sha256': 'ef0a7a66f5ff1e746447cccdab3d812059192d474c6778ad307b946f4974a7bf'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order (no order is ever placed by X803)'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': False}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2011-01-03 → 2021-12-31 (2769 trading days) |
| CAGR | 0.00% |
| Annualised volatility | 0.00% |
| Sharpe (rf = 0) | n/a |
| Sortino | n/a |
| Max drawdown | 0.00% |
| Longest drawdown (trading days) | 0 |
| Calmar | n/a |
| Worst year | 0.00% |
| Worst month | 0.00% |
| Closed trades | 0 |
| Win rate | n/a |
| Average winner | n/a |
| Average loser | n/a |
| Expectancy per trade | n/a |
| Profit factor | n/a |
| Average holding (calendar days) | n/a |
| Average exposure | 0.00% |
| Turnover (1-way, per year) | 0.00 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -14.61% | 0.00 | n/a |

## Calendar-year returns

| Year | Return |
|---|---|
| 2011 | 0.00% |
| 2012 | 0.00% |
| 2013 | 0.00% |
| 2014 | 0.00% |
| 2015 | 0.00% |
| 2016 | 0.00% |
| 2017 | 0.00% |
| 2018 | 0.00% |
| 2019 | 0.00% |
| 2020 | 0.00% |
| 2021 | 0.00% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2769 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2011-01-03..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 100000.00 |
| equity_complete | pass | chart rows 2769 vs algorithm days 2769 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2769 vs QuantConnect tradeableDates 2769 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 632 warm-up sessions |
| no_leverage | pass | min cash/equity 1.000000; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=0.0 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 0 orders vs QuantConnect Total Orders 0 |
| fills_match_harness_count | pass | downloaded fill events 0 vs harness-recorded fills 0 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | no fills downloaded; harness recorded 0 fills |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `181cd94e5e887eff9a05c10246c2e57ef3f74d4686d0536f79a8a777787cb70a`
- fills_sha256: `78a0962b9b70b6901d01d783a235cdae962b1dffa5be70026c022bbbddabc973`
- trades_sha256: `7099cb2261e2e834b28abe20af9c8e05779781d921eadddafc5db983545e4c35`
