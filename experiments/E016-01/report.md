# E016-01 — S016 v1.0 (research)

P2 H016 candidate: top 20 by GP/A (True TTM gross profit / same-quarter total assets), quarterly, $100K, one-time top-up rule (D116). Consumes Phase 2 slot 2. Pre-declared in research/phase2/H016_spec.md (frozen, D116).

- **Status:** completed
- **Split:** DEV (2010-03-01 → 2021-12-31)
- **Commit:** `834a55056804cb1857f848d80995ccd6a6190189` · **QC backtest:** `ce8d5082718c69d73463f093dfeb0fb1` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-02T15:18:27Z · **runtime:** 842s
- **Parameters:** `{'slots': 20, 'months': [3, 6, 9, 12], 'book': 'gpa'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 20, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2021-12-31 (2983 trading days) |
| CAGR | 12.77% |
| Annualised volatility | 20.39% |
| Sharpe (rf = 0) | 0.69 |
| Sortino | 0.97 |
| Max drawdown | -40.53% |
| Longest drawdown (trading days) | 543 |
| Calmar | 0.32 |
| Worst year | -2.64% |
| Worst month | -14.28% |
| Closed trades | 197 |
| Win rate | 52.79% |
| Average winner | 45.86% |
| Average loser | -20.12% |
| Expectancy per trade | 14.71% |
| Profit factor | 2.39 |
| Average holding (calendar days) | 350.1 |
| Average exposure | 95.28% |
| Turnover (1-way, per year) | 0.74 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -2.11% | 1.02 | 0.83 |
| E901-07 | -0.61% | 0.99 | 0.87 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 15.76% |
| 2011 | 15.85% |
| 2012 | 2.38% |
| 2013 | 45.01% |
| 2014 | 2.34% |
| 2015 | 2.18% |
| 2016 | -2.64% |
| 2017 | 20.99% |
| 2018 | 5.37% |
| 2019 | 18.75% |
| 2020 | 35.03% |
| 2021 | 0.10% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2983 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 94002.76 |
| equity_complete | pass | chart rows 2983 vs algorithm days 2983 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2983 vs QuantConnect tradeableDates 2983 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 418 warm-up sessions |
| no_leverage | pass | min cash/equity 0.019350; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 9 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.9241314226868925e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 596 orders vs QuantConnect Total Orders 596 |
| fills_match_harness_count | pass | downloaded fill events 596 vs harness-recorded fills 596 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 596 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `dbdec4984693d8fdc957843d44bdf085553373397f435d90fe369025accf1b1f`
- fills_sha256: `8dc3d265cbca20b8c1224432c4193741c0e1d2f3822d315a9982f6f301f9fd25`
- trades_sha256: `5658c32c30dd773b68772e74e8b0ef2a34004db01935015c6599d8a1e711c54e`
