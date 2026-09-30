# E962-27 — X962 v1.0 (infrastructure)

C03 S1 null ($200K, 15 slots, hold 60, seed 3). Not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `ec12576e4901c969200f6bcadbebb72d4351c8fe` · **QC backtest:** `fad627cdfc5ff42f160dc3ce3f92a5b6` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T18:53:49Z · **runtime:** 235s
- **Parameters:** `{'slots': 15, 'hold': 60, 'seed': 3}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 13.74% |
| Annualised volatility | 15.30% |
| Sharpe (rf = 0) | 0.92 |
| Sortino | 1.31 |
| Max drawdown | -21.63% |
| Longest drawdown (trading days) | 259 |
| Calmar | 0.64 |
| Worst year | 0.18% |
| Worst month | -9.44% |
| Closed trades | 481 |
| Win rate | 62.16% |
| Average winner | 11.89% |
| Average loser | -10.21% |
| Expectancy per trade | 3.53% |
| Profit factor | 1.84 |
| Average holding (calendar days) | 88.2 |
| Average exposure | 83.84% |
| Turnover (1-way, per year) | 3.57 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | 0.40% | 0.95 | 0.89 |
| E901-07 | -0.19% | 0.91 | 0.92 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 13.64% |
| 2011 | 5.67% |
| 2012 | 10.13% |
| 2013 | 32.95% |
| 2014 | 19.31% |
| 2015 | 0.18% |
| 2016 | 18.46% |
| 2017 | 12.25% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 186543.08 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.047707; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 2 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3084730965147665e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 977 orders vs QuantConnect Total Orders 977 |
| fills_match_harness_count | pass | downloaded fill events 977 vs harness-recorded fills 977 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 977 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `69624021130fb7d2a69c3e7c9a0e17d9964811df31c851a0337575ec199f3fea`
- fills_sha256: `d710c1b31a5812191c3d622b7435ebcc470735638f6f7e064425efb9a15ff754`
- trades_sha256: `c124002c5f9851473044eddf9607ef8de906d4b3233f99106d5a89205cc732f1`
