# E007-15 — S007 v1.1 (research)

C02 robustness of E007-02 (H007 v1.1): cost stress 4x (40 bps/side) (pre-declared in research/cycles/C02_robustness_plan.md) | TECHNICAL REPEAT of E007-05 (runner lost in a container restart; identical configuration; D069)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `1c00e551002cf1f09cafc5b369789b2cbc2f7821` · **QC backtest:** `0c985c7d7c882e1d961f914770266fc2` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T02:43:17Z · **runtime:** 1212s
- **Parameters:** `{'setup': 'atr', 'pct': 0.1, 'atr_ratio': 0.6, 'use_trend': True, 'time_stop': 40, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate', 'slippage_stress_multiple': 4}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 3.84% |
| Annualised volatility | 4.85% |
| Sharpe (rf = 0) | 0.80 |
| Sortino | 1.23 |
| Max drawdown | -6.49% |
| Longest drawdown (trading days) | 548 |
| Calmar | 0.59 |
| Worst year | -0.41% |
| Worst month | -2.17% |
| Closed trades | 223 |
| Win rate | 40.36% |
| Average winner | 7.09% |
| Average loser | -2.62% |
| Expectancy per trade | 1.30% |
| Profit factor | 1.80 |
| Average holding (calendar days) | 27.6 |
| Average exposure | 20.98% |
| Turnover (1-way, per year) | 2.72 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -9.50% | 0.09 | 0.28 |
| E901-07 | -10.09% | 0.10 | 0.30 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 7.37% |
| 2011 | -0.00% |
| 2012 | 7.58% |
| 2013 | 2.75% |
| 2014 | 6.84% |
| 2015 | -0.41% |
| 2016 | 0.62% |
| 2017 | 6.32% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 99796.79 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.030662; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 30 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.201840497050239e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 447 orders vs QuantConnect Total Orders 447 |
| fills_match_harness_count | pass | downloaded fill events 446 vs harness-recorded fills 446 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 446 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `54c0a823099b6b4c1a607dc1475f6a2304d565f8006e988df628be28f45f8aef`
- fills_sha256: `94b5297612c7e57a2321d6da20c54cf68d28e50ec96704be178919dbbe956b36`
- trades_sha256: `81cc17c0cdf48068d1735e63aba098b6a736f51c0466f0d85d6c4c82663a892e`
