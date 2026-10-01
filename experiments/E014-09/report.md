# E014-09 — S014 v1.1 (benchmark)

P2 control C2 pullback without recovery, exit B (same code, universe, slots, costs and exit as E014-02). Benchmark, never a candidate. Pre-declared in research/phase2/P2_spec.md (frozen, D094).

- **Status:** completed
- **Split:** DEV (2010-01-04 → 2021-12-31)
- **Commit:** `56eb2406c683f2ec5492b15773664b64edc8debe` · **QC backtest:** `de47de097f5a6f6e31b232145a768fb5` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-01T01:39:14Z · **runtime:** 1237s
- **Parameters:** `{'mode': 'c2', 'exit': 'B', 'limit': 126, 'rsi_pullback': 40, 'window': 5, 'rsi_recovery': 45, 'slots': 12}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 14.27% |
| Annualised volatility | 27.83% |
| Sharpe (rf = 0) | 0.62 |
| Sortino | 0.87 |
| Max drawdown | -39.58% |
| Longest drawdown (trading days) | 726 |
| Calmar | 0.36 |
| Worst year | -11.91% |
| Worst month | -19.45% |
| Closed trades | 659 |
| Win rate | 32.02% |
| Average winner | 34.43% |
| Average loser | -10.09% |
| Expectancy per trade | 4.16% |
| Profit factor | 1.39 |
| Average holding (calendar days) | 76.9 |
| Average exposure | 92.89% |
| Turnover (1-way, per year) | 3.95 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -0.32% | 1.16 | 0.69 |
| E901-07 | 0.78% | 1.14 | 0.73 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 27.28% |
| 2011 | 3.21% |
| 2012 | 12.28% |
| 2013 | 37.21% |
| 2014 | 17.95% |
| 2015 | -5.30% |
| 2016 | -5.81% |
| 2017 | 7.21% |
| 2018 | -6.30% |
| 2019 | 58.99% |
| 2020 | 65.14% |
| 2021 | -11.91% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 84964.74 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.021443; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 11 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.6137604829183815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1331 orders vs QuantConnect Total Orders 1331 |
| fills_match_harness_count | pass | downloaded fill events 1330 vs harness-recorded fills 1330 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1330 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `2d82b8e6f964930008a78017ce5c46e9593263ab83e89ede4019b35197079786`
- fills_sha256: `590f47508c126ddd9811ac01de5b8f6cdd4705bb93ae1c4072cff06fcc877e2f`
- trades_sha256: `ecfc83077c7ab6978ade711608d2fe0d2bb1949396b97a767ed1527a9f223596`
