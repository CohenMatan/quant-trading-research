# E982-01 — X982 v1.0 (infrastructure)

H017 non-candidate technical canary: byte copy of S017, random-event book seed 0 (not a control seed), full window with the 2009-07-01 history-only warm-up. Checks the event table hash, PIT reactions and breakpoints, E+2 entries, 60-session exits, 10 slots, k_t, held-stock events, sizing, cash, costs. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-03-01 → 2021-12-31)
- **Commit:** `3035a8848801d527567e11ed3228ac61a35f7208` · **QC backtest:** `12c528de68efbaa866f4d2bdc59b03cc` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-03T17:05:28Z · **runtime:** 872s
- **Parameters:** `{'slots': 10, 'hold_sessions': 60, 'quantile': 0.9, 'reaction_lag': 1, 'book': 'random', 'seed': 0, 'canary': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2021-12-31 (2983 trading days) |
| CAGR | 11.27% |
| Annualised volatility | 20.23% |
| Sharpe (rf = 0) | 0.63 |
| Sortino | 0.88 |
| Max drawdown | -41.91% |
| Longest drawdown (trading days) | 455 |
| Calmar | 0.27 |
| Worst year | -11.25% |
| Worst month | -19.38% |
| Closed trades | 462 |
| Win rate | 59.52% |
| Average winner | 11.14% |
| Average loser | -9.05% |
| Expectancy per trade | 2.97% |
| Profit factor | 1.72 |
| Average holding (calendar days) | 86.8 |
| Average exposure | 89.27% |
| Turnover (1-way, per year) | 3.74 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -3.61% | 1.06 | 0.87 |
| E901-07 | -2.11% | 1.03 | 0.91 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 18.86% |
| 2011 | -2.01% |
| 2012 | 7.11% |
| 2013 | 31.79% |
| 2014 | 9.21% |
| 2015 | -1.80% |
| 2016 | 21.35% |
| 2017 | 12.82% |
| 2018 | -11.25% |
| 2019 | 24.37% |
| 2020 | 11.42% |
| 2021 | 19.23% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2983 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 92959.54 |
| equity_complete | pass | chart rows 2983 vs algorithm days 2983 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2983 vs QuantConnect tradeableDates 2983 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 166 warm-up sessions |
| no_leverage | pass | min cash/equity 0.029826; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 4 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.050748481174355e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 934 orders vs QuantConnect Total Orders 934 |
| fills_match_harness_count | pass | downloaded fill events 934 vs harness-recorded fills 934 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 934 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `efc9a23df88e99e778ce7d80b19f241291af5503ee38c7663ebf03f64b8b39e2`
- fills_sha256: `58c95c76b17d41a83104452ec00c87e61a4ec8ce2b93f3b739cbcc0dac17df26`
- trades_sha256: `a558755bff4dadd8ad52a969b065b63719ad3f87c2122ff7d7b840601efd58ab`
