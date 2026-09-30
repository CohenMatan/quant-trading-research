# E962-15 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series A: account size: 15 slots at $1000K, hold 20, seed 3. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `1276220ca646cf50edbeb04ddda09590fede6a2c` · **QC backtest:** `24d7977515692b06444e033c74b24ad0` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T10:02:54Z · **runtime:** 365s
- **Parameters:** `{'slots': 15, 'hold': 20, 'seed': 3}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 11.33% |
| Annualised volatility | 14.57% |
| Sharpe (rf = 0) | 0.81 |
| Sortino | 1.15 |
| Max drawdown | -16.68% |
| Longest drawdown (trading days) | 279 |
| Calmar | 0.68 |
| Worst year | 3.05% |
| Worst month | -9.41% |
| Closed trades | 1352 |
| Win rate | 57.62% |
| Average winner | 5.95% |
| Average loser | -5.88% |
| Expectancy per trade | 0.94% |
| Profit factor | 1.33 |
| Average holding (calendar days) | 30.3 |
| Average exposure | 82.49% |
| Turnover (1-way, per year) | 9.97 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -2.01% | 0.89 | 0.88 |
| E901-07 | -2.59% | 0.86 | 0.91 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 19.61% |
| 2011 | 3.87% |
| 2012 | 7.55% |
| 2013 | 29.72% |
| 2014 | 6.68% |
| 2015 | 5.57% |
| 2016 | 3.05% |
| 2017 | 17.15% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 965284.81 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.056219; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 3 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.174388296080242e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 2719 orders vs QuantConnect Total Orders 2719 |
| fills_match_harness_count | pass | downloaded fill events 2719 vs harness-recorded fills 2719 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 2719 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `5d39b2dbc72e548b537e588a536d513493b9af1f19604f6149208c21fbc76ef9`
- fills_sha256: `03415d08d2dc8678d796f89877dd0ab0394d3eda97af5ec0c23106faa6157609`
- trades_sha256: `c1635426b097d2ad33142b00e71ca95393929c3886a3443c973824122e5bc834`
