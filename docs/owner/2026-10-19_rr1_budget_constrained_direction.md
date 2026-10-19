# Owner decision D261 — RR1 budget-constrained research direction (2026-10-19)

**Context:**
- This follows RR1 (D259 / D260, `docs/checkpoints/RR1_research_reset_qc_migration_impact_roadmap.md`, PR #121).
- The message is recorded verbatim below, before any planning work.

---

Owner Decision — RR1 Budget-Constrained Research Direction

I have reviewed RR1 and want to clarify my current priorities.

I do not want to purchase additional datasets, subscriptions, infrastructure or services at this stage.

We should continue using QuantConnect and the tools and data already available to us, at least until we identify genuinely promising strategies that justify broader independent validation.

RR1 Decisions

1. Accept RR1 as the research-reset assessment, including its documented limitations and uncertainties.

2. Select Option 1 — QuantConnect-only, price-first research as the current programme direction.

3. Defer Option 3 (licensed data and a local engine). Keep D123's no-new-data-purchase restriction and D001's QuantConnect-first architecture in place for now. Revisit them only with separate owner approval after credible candidates emerge.

4. Approve the infrastructure simplification principles in RR1 §6. The validation architecture in §5 must be adapted to Option 1, explicitly distinguishing candidate discovery from independent confirmation.

5. Close the original SYS-1 as NOT RUN — PLATFORM BLOCKED — NO STRATEGY VERDICT. H028 remains REJECTED.

6. Defer additional QuantConnect Support questions unless a concrete compliance blocker requires clarification.

Research Objective

Our primary objective remains discovering long-only US equity strategies that outperform SPY in long-term terminal wealth after realistic trading costs.

Maintain our established portfolio constraints and transaction-cost assumptions unless I explicitly approve changes.

The immediate goal is to discover credible candidates worth further validation, not to claim that development-period performance establishes investable alpha.

Research Direction

Prioritize strategies using reliable existing price and volume data, while allowing existing fundamental or SEC data only when their point-in-time integrity and coverage can be demonstrated without major new infrastructure.

Avoid unnecessary redesigns of old strategies or attempts to reproduce the old QuantConnect data versions exactly.

Do not relax the $2B point-in-time market-cap requirement or substitute a survivorship-biased universe without explicit approval. If this requirement makes a proposed research track infeasible, report the blocker and an alternative design for owner review.

Consider the extensive prior research exposure to 2010–2021. No strategy should be described as independently validated based on that period alone.

The existing 2022–2026 Holdout remains sealed.

Next Task — Simplified Research Programme Proposal

Prepare a focused, practical plan for continuing research on the current QuantConnect platform.

Include:

- The simplest compliant infrastructure that supports repeated research without rebuilding the engine for each hypothesis.
- What historical data is reliably available today.
- Which categories of strategies can be investigated with those data.
- How to identify promising candidates efficiently with a limited hypothesis and run budget.
- Which existing research components can be reused safely.
- Clear candidate-selection criteria, realistic costs and stopping rules.
- How promising candidates could eventually proceed to genuinely independent validation.
- The minimum infrastructure work required before the next strategy experiment.
- Explicit limitations arising from the already-examined development history.

Prefer a small number of economically motivated hypotheses to broad parameter searches.

Do not purchase data, change frozen experiments, run new backtests, access the Holdout or begin implementation under this instruction.

Create a concise updated research roadmap based on RR1, commit the documentation and STOP for owner review.

The priority is to return to researching investment strategies efficiently, using our existing resources.
