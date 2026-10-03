# E017-01 — S017 v1.0 (research)

P2 H017 candidate: top-decile 2-session SPY-adjusted 8-K earnings reaction, entry E+2, 60-session hold, 10 slots, $100K. CONSUMES PHASE 2 SLOT 3. Pre-declared in research/phase2/H017_spec.md (frozen 2026-10-03).

- **Status:** completed
- **Split:** DEV (2010-03-01 → 2021-12-31)
- **Commit:** `3474730026a0c77f556d59bc575933b218376bfa` · **QC backtest:** `322b89c18ff3d74de278aca451140c16` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-03T18:12:59Z · **runtime:** 783s
- **Parameters:** `{'slots': 10, 'hold_sessions': 60, 'quantile': 0.9, 'reaction_lag': 1, 'book': 'candidate'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2021-12-31 (2983 trading days) |
| CAGR | 17.46% |
| Annualised volatility | 20.66% |
| Sharpe (rf = 0) | 0.88 |
| Sortino | 1.25 |
| Max drawdown | -36.79% |
| Longest drawdown (trading days) | 388 |
| Calmar | 0.47 |
| Worst year | -0.38% |
| Worst month | -10.28% |
| Closed trades | 461 |
| Win rate | 62.04% |
| Average winner | 13.00% |
| Average loser | -9.49% |
| Expectancy per trade | 4.46% |
| Profit factor | 2.04 |
| Average holding (calendar days) | 86.9 |
| Average exposure | 89.03% |
| Turnover (1-way, per year) | 3.72 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | 2.58% | 1.06 | 0.85 |
| E901-07 | 4.08% | 1.03 | 0.89 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 18.91% |
| 2011 | -0.38% |
| 2012 | 24.60% |
| 2013 | 35.50% |
| 2014 | 30.20% |
| 2015 | 6.97% |
| 2016 | 5.93% |
| 2017 | 23.63% |
| 2018 | 4.65% |
| 2019 | 17.38% |
| 2020 | 26.32% |
| 2021 | 18.65% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2983 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 89886.90 |
| equity_complete | pass | chart rows 2983 vs algorithm days 2983 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2983 vs QuantConnect tradeableDates 2983 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 166 warm-up sessions |
| no_leverage | pass | min cash/equity 0.030013; 0 closes with negative cash |
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

- equity_sha256: `0825695b18388fca06c550c7f5c456645f9878e12f06441b040d288b7ffeb7c7`
- fills_sha256: `7ce6202869f4e95816e692096eb076989be016f12a748685461a51ba87555531`
- trades_sha256: `923ab7c8ed2f562385578d457d830cbab70e9e903c504b27fa92589a4b5aef47`
