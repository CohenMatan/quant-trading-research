# E006-02 — S006 v1.1 (research)

C02 H006 S006 v1.1 (pre-declared selection candidate, D069) on IS 2010-2017: 52-week-high breakout (N = 252)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `4729987f232412d3cb9a8475d3390c42b42f2e4b` · **QC backtest:** `624bccead89f68f8f1e191be257fbb3d` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T20:23:00Z · **runtime:** 695s
- **Parameters:** `{'n': 252, 'vol_mult': 1.5, 'use_volume': True, 'k': 3.0, 'time_stop': 60, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 9.76% |
| Annualised volatility | 13.94% |
| Sharpe (rf = 0) | 0.74 |
| Sortino | 1.03 |
| Max drawdown | -24.31% |
| Longest drawdown (trading days) | 646 |
| Calmar | 0.40 |
| Worst year | -10.42% |
| Worst month | -11.34% |
| Closed trades | 519 |
| Win rate | 46.63% |
| Average winner | 9.39% |
| Average loser | -5.73% |
| Expectancy per trade | 1.32% |
| Profit factor | 1.39 |
| Average holding (calendar days) | 53.1 |
| Average exposure | 90.81% |
| Turnover (1-way, per year) | 6.18 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -3.58% | 0.71 | 0.73 |
| E901-07 | -4.17% | 0.68 | 0.75 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 14.72% |
| 2011 | -10.42% |
| 2012 | 17.04% |
| 2013 | 36.18% |
| 2014 | 14.95% |
| 2015 | -5.31% |
| 2016 | 4.11% |
| 2017 | 13.34% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 96546.88 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.031011; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 17 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.0818751887864673e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1049 orders vs QuantConnect Total Orders 1049 |
| fills_match_harness_count | pass | downloaded fill events 1047 vs harness-recorded fills 1047 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1047 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `00e24249603330324a3645375bf39f7897aa6fb551d61860905705412b9bb8b3`
- fills_sha256: `e91df7be5932916af46e475fda1b45ee3dd8ad3812e66545d2efa3104ad772b6`
- trades_sha256: `cba5fa7b500f45a693bece550c70af99d384cb61e95b0e0c55fde5a319033010`
