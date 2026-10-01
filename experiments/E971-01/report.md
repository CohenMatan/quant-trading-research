# E971-01 — X971 v1.0 (infrastructure)

SEC verification (D111): vendor fundamentals of a 406-company sample vs SEC as-first-filed XBRL values (ratios, matching filing), PIT-layer exposure dates, SEC cover-share market-cap method vs vendor PIT market cap, split cross-check, and public-float identity fingerprints for the D043 repair (pairs: SEC registrants without vendor data x securities without fundamentals; native-coverage check). Ratios/identifiers only; no orders, no returns. Verification; not a trial.

- **Status:** failed
- **Split:** AUDIT (2009-06-01 → 2021-12-31)
- **Commit:** `70464a8f3bbfc4f55f3cfc80048c6199659114e6` · **QC backtest:** `d2beddbc302bccff485e670bfa9b9033` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-01T21:45:21Z · **runtime:** 118s
- **Parameters:** `{}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Error

```
2012-01-04 00:00:00 Runtime Error: float division by zero
  at _qr_select
    ratio = flt / (shares * float(f.price))
            ~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~
 in main.py: line 209

float division by zero
  at _qr_select
    ratio = flt / (shares * float(f.price))
            ~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~
 in main.py: line 209

```
