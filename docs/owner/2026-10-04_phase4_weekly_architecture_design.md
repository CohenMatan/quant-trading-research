# Owner message 2026-10-04: "Phase 4 — Design a Weekly Multi-Indicator Trend/Momentum Strategy Research Architecture"

This is a recorded summary; the full message is in the session transcript.

## Direction
- A new research-design phase: **Weekly multi-indicator trend / momentum stock selection**.
- Not a rescue of H018; no Phase 3 result may be used to tune parameters.
- **Design only:** no Weekly backtest, no parameter search, no candidate, no 2018–2021 candidate evaluation, no Holdout, no purchase.

## Objective (unchanged)
- Terminal wealth above SPY total-return buy-and-hold after realistic costs, long-only, no leverage.
- $100K primary; $200K sensitivity.
- The wealth table is reported first; risk metrics are safeguards.

## Required design content
- **Weekly bars and timing:** exact construction from completed weekly bars only; execution at the next session; leakage canaries.
- **Indicator families:** 7–8 reviewed, grouped by information; a constrained grammar (1 primary trend / setup + 0–1 confirmation + 0–1 volatility / volume filter; ≤ 3 families).
- **Entry, ranking, exit:** a pre-declared ranking; a trend-state exit with no arbitrary fixed horizon ("let winners run"); a staged exit study (Stage B only if Stage A shows robust evidence).
- **Mechanics before any return search:** variable holding mechanics; position count chosen mechanically (e.g. 10 / 15 / 20; the owner's intuition of 15 is not to be adopted just because it was mentioned); expected turnover and costs ($7 + $7, 10 bps); reject structurally expensive designs.
- **Search space and selection:** ≈ 200–500 coarse, literature-based configurations; plateau, not peak; a frozen simplicity rule; hierarchical gates instead of a weighted score.
- **Null:** a full-optimizer null of no-edge worlds preserving market structure; the threshold computed, committed and hashed **before** the real search; enough null worlds for useful precision (≥ 500).
- **Partition:** retain 2010–2017 / walk-forward 2014–2017 / one-shot 2018–2021 / locked Holdout, or justify a better architecture (consider an expanding walk-forward) from power, not performance.
- **Controls:** random controls (same schedule, holdings, costs and holding mechanics; never averaged) kept distinct from the search null.
- **Power, implementation and comparison:** a power analysis (false pass, edge for 50% / 80% power) using controls or null models, not candidate returns; a QuantConnect / LEAN implementation plan with runtime and cost; an external-evidence review (academic vs practitioner vs inference); stock selection as primary, with market / sector rotation as context only.

## Deliverable
**P4-CP1 — Weekly Multi-Indicator Trend/Momentum Research Architecture Proposal** (38 items + questions A–J). Then STOP for owner approval before any Weekly implementation or backtest.
