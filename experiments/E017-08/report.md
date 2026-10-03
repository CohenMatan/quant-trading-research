# E017-08 — S017 v1.0 (sizing)

P2 $200K sensitivity of E017-01. Never decides, never rescues. Pre-declared in research/phase2/H017_spec.md (frozen 2026-10-03).

- **Status:** completed
- **Split:** DEV (2010-03-01 → 2021-12-31)
- **Commit:** `25acee24dc4b4656596c81919d1ef87bc6b02e2f` · **QC backtest:** `6c85aace195b1c63c456fbf48ddb337d` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-03T19:56:00Z · **runtime:** 1099s
- **Parameters:** `{'slots': 10, 'hold_sessions': 60, 'quantile': 0.9, 'reaction_lag': 1, 'book': 'candidate'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2021-12-31 (2983 trading days) |
| CAGR | 17.63% |
| Annualised volatility | 20.67% |
| Sharpe (rf = 0) | 0.89 |
| Sortino | 1.26 |
| Max drawdown | -36.80% |
| Longest drawdown (trading days) | 387 |
| Calmar | 0.48 |
| Worst year | -0.11% |
| Worst month | -10.29% |
| Closed trades | 461 |
| Win rate | 62.04% |
| Average winner | 13.03% |
| Average loser | -9.46% |
| Expectancy per trade | 4.49% |
| Profit factor | 2.05 |
| Average holding (calendar days) | 86.9 |
| Average exposure | 89.09% |
| Turnover (1-way, per year) | 3.72 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | 2.75% | 1.06 | 0.85 |
| E901-07 | 4.25% | 1.03 | 0.89 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 19.16% |
| 2011 | -0.11% |
| 2012 | 24.91% |
| 2013 | 35.75% |
| 2014 | 30.37% |
| 2015 | 7.10% |
| 2016 | 6.04% |
| 2017 | 23.85% |
| 2018 | 4.76% |
| 2019 | 17.45% |
| 2020 | 26.42% |
| 2021 | 18.71% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2983 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 179966.52 |
| equity_complete | pass | chart rows 2983 vs algorithm days 2983 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2983 vs QuantConnect tradeableDates 2983 |
| warmup_left_account_untouched | pass | first recorded equity 200000.00 vs initial cash 200000.00; 166 warm-up sessions |
| no_leverage | pass | min cash/equity 0.030071; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 3 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.6303945933115617e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 932 orders vs QuantConnect Total Orders 932 |
| fills_match_harness_count | pass | downloaded fill events 932 vs harness-recorded fills 932 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 932 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `771ab84e3a7f873740289cf9938a98a9c1c6b22aeffa7cb0517b38842a00d222`
- fills_sha256: `6e2644f36fe4805bada3f28e00d728bf243a04a6e1612f12ea39ca66bf47c2af`
- trades_sha256: `34bbdd24f66d7e48e8d9cac2daab95ca80622c17cbed4f0cc94f1379099e04ef`
