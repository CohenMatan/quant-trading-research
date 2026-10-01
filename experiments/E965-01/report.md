# E965-01 — X965 v1.0 (infrastructure)

P2 H014 canary: unchanged S014 code, H014 entry with NON-candidate thresholds (RSI 30/50, window 4) and a 20-session horizon with roll, 2010-2012, $100K. Verification; not a trial.

- **Status:** failed
- **Split:** AUDIT (2010-01-04 → 2012-12-31)
- **Commit:** `cc995f89d2c3474bc2659384bbdab50e2ea5a95d` · **QC backtest:** `f98b22cefd40a8159a485bbf095d6c8b` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T20:51:55Z · **runtime:** 172s
- **Parameters:** `{'mode': 'h014', 'exit': 'A', 'limit': 20, 'rsi_pullback': 30, 'window': 4, 'rsi_recovery': 50, 'slots': 12}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Error

```
2010-01-04 16:00:00 Runtime Error: &#039;NoneType&#039; object is not subscriptable
  at qr_on_close
    mom = {str(s.id): float(m) for s, m in zip(cands, f[&quot;mom&quot;])}
                                                      ~^^^^^^^
 in main.py: line 46
  at on_data
    self.qr_on_close(data)
 in qr_harness.py: line 532

'NoneType' object is not subscriptable
  at qr_on_close
    mom = {str(s.id): float(m) for s, m in zip(cands, f["mom"])}
                                                      ~^^^^^^^
 in main.py: line 46
  at on_data
    self.qr_on_close(data)
 in qr_harness.py: line 532

```
