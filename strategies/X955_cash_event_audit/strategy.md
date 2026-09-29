# X955: cash-event audit (infrastructure)

**Purpose.** Classify and reconcile every non-trade cash credit of a completed run. The first use is the Validation run E005-28 (owner request, 2026-09-29).

**How it works.**

- It subscribes to every security the audited run held, using the exact security identifiers from the run's fills.
- It is given the run's holdings (quantity after each fill date).
- For each dividend, split, ticker change and delisting that LEAN delivers while the run held the security, it records the cash those holdings should receive.

**Rules.**

- It places no orders, runs no strategy and is not a research trial.
- It outputs derived portfolio amounts only (no per-share data series; licence rule).
