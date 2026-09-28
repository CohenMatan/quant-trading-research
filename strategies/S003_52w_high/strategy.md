# S003 — 52-week-high proximity (H003)

**Rule:** Hold the 15 eligible stocks closest to their 52-week high; rebalance monthly or every 10 trading days; optional positive 12-1 momentum filter.

**Implementation:**

- Signals: `signals.py`, pure and truncation-tested.
- Execution: `main.py`, orders at the next session's open via the harness.
- Variations differ only in the config parameters listed in `research/hypotheses/H003.md`.

**Standard settings (approved):**

- $100K account;
- $7 per order commission; 10 bps slippage;
- slot weight: equal weight of 98% of equity per slot, but at least the $5,000 minimum, and at most 10%;
- at most 15 positions.

**Disclosure:** universe survivorship gap after 2010 (D043, `docs/data/survivorship_gap_2010.md`).
