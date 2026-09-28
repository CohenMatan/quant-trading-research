# S001 — Trend-filtered short-term reversal (H001)

**Rule:** Buy stocks above their 200-day average after a sharp 2–3 day drop (RSI(2) or 3-day return), exit on a close above the 5-day average or after 10 days.

**Implementation:**

- Signals: `signals.py`, pure and truncation-tested.
- Execution: `main.py`, orders at the next session's open via the harness.
- Variations differ only in the config parameters listed in `research/hypotheses/H001.md`.

**Standard settings (approved):**

- $100K account;
- $7 per order commission; 10 bps slippage;
- slot weight: equal weight of 98% of equity per slot, but at least the $5,000 minimum, and at most 10%;
- at most 15 positions.

**Disclosure:** universe survivorship gap after 2010 (D043, `docs/data/survivorship_gap_2010.md`).
