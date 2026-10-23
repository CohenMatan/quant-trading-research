# Owner direction D294 — Resolve the historical chart analysis blocker first (2026-10-23)

**Context:** follows TT-CP1 (`docs/checkpoints/TT_CP1_technical_trading_phase1_audit_architecture.md`, D293, PR #136). The message is recorded verbatim below, before any work.

---

Owner Direction — Resolve Historical Chart Analysis Blocker First
I want to preserve the hybrid research approach: Claude should help analyze real historical stock charts, identify potentially meaningful price-action behavior, and translate that behavior into deterministic trading rules.
I do not want to replace this objective with synthetic-chart analysis only.
Before approving TP-1 development or the proposed Phase 1b QuantConnect universe audit, investigate whether we can legally and practically obtain historical stock charts for Claude's analysis from an independent data source.
Requirements
1. Identify up to three credible historical US equity OHLCV or chart-data sources, prioritizing free or already-available resources.
2. Verify their actual licensing terms for sharing chart images or price data with external AI systems.
3. Assess historical depth, adjusted prices, delisted-stock coverage and suitability for blind chart analysis.
4. Distinguish a licence to view charts personally from permission to transmit them to an external AI.
5. Explain whether the source could support a representative, outcome-blind research sample.
6. QuantConnect-derived data and images must remain inside QuantConnect unless an appropriate explicit licence permits otherwise.
7. Assess whether a separate chart-development source and QuantConnect backtesting source can be used without contaminating independent validation.
Do not download datasets, extract charts, purchase subscriptions, implement code, run backtests or access the Holdout.
Deliverable
Produce one concise feasibility checkpoint with:
* Sources and their verified licensing terms.
* Data availability and limitations.
* Estimated costs, if any.
* A recommended compliant workflow.
* A clear GO / NO-GO decision on real historical chart analysis.
If no suitable source exists, explicitly present the decision between quantitative-only research and pausing the hybrid programme.
Do not assume synthetic charts can replace empirical market analysis.
Commit the checkpoint and STOP for owner review.
