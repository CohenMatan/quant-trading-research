# S002 — 12-1 momentum (H002)

**Rule:** Hold the 15 eligible stocks with the highest 12-1 (or 6-1) month return; rebalance monthly or every 2 months; optional SPY 200-day regime filter.

**Implementation:**

- Signals: `signals.py`, pure and truncation-tested.
- Execution: `main.py`, orders at the next session's open via the harness.
- Variations differ only in the config parameters listed in `research/hypotheses/H002.md`.

**Standard settings (approved):**

- $100K account;
- $7 per order commission; 10 bps slippage;
- slot weight: equal weight of 98% of equity per slot, but at least the $5,000 minimum, and at most 10%;
- at most 15 positions.

**Disclosure:** universe survivorship gap after 2010 (D043, `docs/data/survivorship_gap_2010.md`).
