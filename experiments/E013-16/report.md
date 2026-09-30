# E013-16 — S013 v1.1 (research)

Technical repeat of E013-06 (identical configuration; not a new selection candidate, D069/D087). E013-06's QuantConnect backtest stuck 'In Queue' and was deleted with owner approval (research/cycles/incidents/E013-06_incident.md). C03 H013 S013 v1.1 seed 3 (one candidate per variation; seeds are replicates, D082) on IS, paired with null E962-24. Pre-declared in docs/checkpoints/CP3e_C03_final_plan.md §7; methodology research/cycles/C03_statistical_spec.md (D082).

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `789638226431e8308f11b54641ed80cedc58f057` · **QC backtest:** `6db8302df51c23f0ed4df34c4d465e02` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T17:25:59Z · **runtime:** 335s
- **Parameters:** `{'q': 0.1, 'stat': 'max', 'seed': 3, 'slots': 15, 'hold': 60}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 11.25% |
| Annualised volatility | 15.05% |
| Sharpe (rf = 0) | 0.78 |
| Sortino | 1.11 |
| Max drawdown | -22.12% |
| Longest drawdown (trading days) | 220 |
| Calmar | 0.51 |
| Worst year | -0.67% |
| Worst month | -9.45% |
| Closed trades | 481 |
| Win rate | 62.37% |
| Average winner | 10.80% |
| Average loser | -10.28% |
| Expectancy per trade | 2.87% |
| Profit factor | 1.71 |
| Average holding (calendar days) | 88.1 |
| Average exposure | 84.85% |
| Turnover (1-way, per year) | 3.60 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -2.09% | 0.95 | 0.90 |
| E901-07 | -2.68% | 0.91 | 0.93 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 10.21% |
| 2011 | 2.86% |
| 2012 | 4.95% |
| 2013 | 33.37% |
| 2014 | 18.11% |
| 2015 | -0.67% |
| 2016 | 9.69% |
| 2017 | 14.67% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 92402.31 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.029325; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 3 LEAN-generated fills |
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

- equity_sha256: `ce1f31c9f97ad57c014b8a197ba33df4d76137e072199f77ffd24655f9f641fe`
- fills_sha256: `fc2f9186366bf982b73c6ce1bda14f0ba064c0ac9793ec3de38d6fd6bacbd06e`
- trades_sha256: `7f18786acebf8e0727ae82b019d7f5dea96dbd51f6b51375a2df928c6e1da313`
