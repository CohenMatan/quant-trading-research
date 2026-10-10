# E995-03 — X995 v1.0 (infrastructure)

P7-CP5c NEW-DATASET (re-run of E995-01, which failed at upload: 50-file project limit; table trimmed to periods <= 2017-12) FUNDAMENTAL-TIMING PROBE (owner D184; infrastructure, QuantConnect default build, recorded): X971 v1.1 SEC verification on the X971 sample + pre-registered S2 (480 companies), schema scan of every fundamental object (timing-like members, every period window), per-security changes of every candidate timing field, aggregated market-cap check. Dates, identifiers and vendor/SEC value RATIOS only; no orders, no returns; 2009-06 .. 2017-12.

- **Status:** failed
- **Split:** AUDIT (2009-06-01 → 2017-12-31)
- **Commit:** `85e3abce6ffbac48620b61c4397065796268cbfc` · **QC backtest:** `` · **LEAN:**  · **run:** 2026-10-10T12:51:41Z · **runtime:** 0s
- **Parameters:** `{}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Error

```
QCError: files/create failed: ['This project has 50 files and researcher organizations are limited to 50 files per project. Delete or merge some files, or upgrade the organization to raise the limit.'] [stage: upload]
```
