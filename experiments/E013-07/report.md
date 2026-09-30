# E013-07 — S013 v1.2 (research)

C03 H013 S013 v1.2 seed 1 (one candidate per variation; seeds are replicates, D082) on IS, paired with null E962-22. Pre-declared in docs/checkpoints/CP3e_C03_final_plan.md §7; methodology research/cycles/C03_statistical_spec.md (D082).

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `6573b801c90b376323e1b2285f2ed513b5ec5970` · **QC backtest:** `cab5c58107eed6e6bf23e6e64707fc9c` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T17:31:45Z · **runtime:** 449s
- **Parameters:** `{'q': 0.2, 'stat': 'max5', 'seed': 1, 'slots': 15, 'hold': 60}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 9.00% |
| Annualised volatility | 14.10% |
| Sharpe (rf = 0) | 0.68 |
| Sortino | 0.97 |
| Max drawdown | -25.70% |
| Longest drawdown (trading days) | 488 |
| Calmar | 0.35 |
| Worst year | -5.51% |
| Worst month | -11.52% |
| Closed trades | 481 |
| Win rate | 59.04% |
| Average winner | 9.92% |
| Average loser | -8.87% |
| Expectancy per trade | 2.23% |
| Profit factor | 1.57 |
| Average holding (calendar days) | 88.1 |
| Average exposure | 83.91% |
| Turnover (1-way, per year) | 3.55 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -4.34% | 0.89 | 0.91 |
| E901-07 | -4.93% | 0.85 | 0.93 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 18.42% |
| 2011 | -5.51% |
| 2012 | 8.60% |
| 2013 | 21.33% |
| 2014 | 10.74% |
| 2015 | -3.68% |
| 2016 | 14.37% |
| 2017 | 10.63% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97426.26 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.108010; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 5 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.757220605304979e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 978 orders vs QuantConnect Total Orders 978 |
| fills_match_harness_count | pass | downloaded fill events 976 vs harness-recorded fills 976 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 976 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `796232468f899149dd922151bf248c49b6ca0cd37e35f1a25f5c93499dcaa7db`
- fills_sha256: `fbacca78d696851423e21d469461675f87f56ab8dc5af85a34939d400dd9ec5c`
- trades_sha256: `8928a9554f6de41fe3f428636faea004ccc856a89d14afa0ace9f32cf3fa1bfb`
