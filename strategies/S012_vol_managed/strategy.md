# S012: volatility-managed exposure (H012)

**Hypothesis:** `research/hypotheses/H012.md`. Methodology: `research/cycles/C03_statistical_spec.md` (D082). Implementation choices: D083.

**Rules:**

- **Basket:** the 15 largest eligible stocks by point-in-time market cap, set at the first session of each quarter, equal weight.
- **Exposure:** on each rescale day (the last session of the month, or of the week for v1.2), the target is e = min(1, RV(252) / RV(short)) of SPY. SPY is an indicator only and is never traded.
- **Band:** the new exposure is applied only if it differs from the applied one by more than 0.10.
- **Trading:** all orders are next-open orders through the shared harness, with $7 per order, 10 bps slippage and the D051 cash rules.

**Modes:**

- `timing`: the hypothesis.
- `control_a`: e = 1 always.
- `control_b`: e = the mean of the variation's own previous 12 targets.

Controls are benchmarks, not trials.
