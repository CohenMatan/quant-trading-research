# S004 — Momentum-leader pullbacks (H004)

**Rule:** Among the top 20% by 6-month return (t-131 to t-5), buy the deepest 5-day pullbacks of at least 5% (or 8%); hold 10 or 20 trading days; optional regime filter.

**Implementation:**

- Signals: `signals.py`, pure and truncation-tested.
- Execution: `main.py`, orders at the next session's open via the harness.
- Variations differ only in the config parameters listed in `research/hypotheses/H004.md`.

**Standard settings (approved):**

- $100K account;
- $7 per order commission; 10 bps slippage;
- slot weight: equal weight of 98% of equity per slot, but at least the $5,000 minimum, and at most 10%;
- at most 15 positions.

**Disclosure:** universe survivorship gap after 2010 (D043, `docs/data/survivorship_gap_2010.md`).
