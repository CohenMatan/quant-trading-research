# E963-01 — X963 v1.0 (infrastructure)

C03 H012 infrastructure canary: unchanged S012 code with NON-candidate parameters (RV(10), weekly, 2010-2011). Verification; not a trial.

- **Status:** failed
- **Split:** AUDIT (2010-01-04 → 2011-12-30)
- **Commit:** `57049085bb8509c6a4c6aeb6c4b1a58ae008b3d5` · **QC backtest:** `b690fe949694e600ce2ff76b7b31051f` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T12:30:58Z · **runtime:** 92s
- **Parameters:** `{'rv_short': 10, 'cadence': 'weekly', 'band': 0.1, 'slots': 15, 'mode': 'timing'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Error

```
2010-11-26 13:00:00 Runtime Error: Trying to perform a summation, subtraction, multiplication or division between &#039;float&#039; and &#039;NoneType&#039; objects throws a TypeError exception. To prevent the exception, ensure that both values share the same type.
  at _check_rv
    dev = abs(a / b - 1)
              ~~^~~
 in main.py: line 82
  at qr_on_close
    self._check_rv(today)
 in main.py: line 58
  at on_data
    self.qr_on_close(data)
 in qr_harness.py: line 532

Trying to perform a summation, subtraction, multiplication or division between 'float' and 'NoneType' objects throws a TypeError exception. To prevent the exception, ensure that both values share the same type.
  at _check_rv
    dev = abs(a / b - 1)
              ~~^~~
 in main.py: line 82
  at qr_on_close
    self._check_rv(today)
 in main.py: line 58
  at on_data
    self.qr_on_close(data)
 in qr_harness.py: line 532

```
