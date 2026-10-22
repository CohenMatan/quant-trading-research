# Owner decision D290 — LW-CP1 / spin-off research, Stage 0 only (2026-10-22)

**Context:** follows LW-CP1 (`docs/checkpoints/LW_CP1_long_term_wealth_research_reset.md`, D289, PR #134). The message is recorded verbatim below, before any work.

---

Owner Decision — LW-CP1 / Spin-off Research
I have reviewed LW-CP1 and approve D2 — Stage 0 only: a bounded literature and data-feasibility desk review.
I do not authorize Stage 1, event extraction, QuantConnect runs, backtests, purchases or changes to our portfolio constraints.
Our primary objective remains higher long-term terminal wealth than SPY after costs, not lower drawdowns for their own sake.
1. Review the Evidence Critically
Examine the published evidence for post-spin-off abnormal returns, especially:

* McConnell, Ozbilgin & Wahal (2001), Spin-offs, Ex Ante.
* McConnell & Ovtchinnikov (2004), Predictability of Long-Term Spin-Off Returns.
* Klein & Rosenfeld (2010), The Long-Run Performance of Sponsored and Conventional Spin-Offs.
* Credible subsequent studies covering spin-offs after 2000.
* Evidence from real spin-off investment products and indices, accounting for fees, composition and benchmark differences.

Distinguish announcement returns, parent-company returns and investable returns from purchasing the newly separated company after regular-way trading begins.
Separate conventional pro-rata spin-offs from sponsored spin-offs, split-offs, carve-outs and IPOs.
Identify the evidence that supports the forced-selling mechanism, as well as evidence against it.
Do not assume the effect persists simply because early studies found it.
2. Verify Historical Data Feasibility Without Building Anything
Investigate whether a comprehensive 1998–2009 event list is realistically obtainable.
Important cautions:

* SEC EDGAR archives exist before 2009, but this does not establish that our current local SEC cache contains the required filings.
* Form 10 is not a complete universe of spin-off events.
* A filed registration does not prove the spin-off was completed.
* The distribution date, when-issued trading and first regular-way trading date must be distinguished.
* Historical company identities, ticker changes, acquisitions and delistings must be handled without survivorship or look-ahead bias.

Explain what existing files are available, what additional retrieval or parsing would be needed and what cannot currently be verified.
No event census or new data ingestion is authorized.
3. Assess Whether the Economics Are Meaningful for Our Actual Portfolio
Do not focus only on average abnormal return per spin-off.
Discuss:

* Expected annual opportunity frequency.
* Overlapping 12–24-month holding periods.
* The number of simultaneously investable positions.
* Portfolio-capacity constraints at $100,000.
* The $5,000 minimum position rule.
* Idle satellite capital.
* Trading costs, liquidity and taxes where applicable.
* The potential contribution to whole-account terminal wealth versus SPY.

Do not assume individual event returns are independent. Events may cluster in the same market regimes or industries.
Identify what evidence would be needed for a credible portfolio-level power analysis.
4. Research Integrity
The 1998–2009 window is unused by our internal stock-selection experiments, but parts of it have been studied in published spin-off research.
Do not equate an internally unused sample with a completely independent confirmation of a known published anomaly.
Keep the 2022–2026 Holdout sealed.
No returns are to be computed from our own research datasets at this stage.
5. Decision Gate
At the end of Stage 0, recommend exactly one:
GO to a separately approved event-census design, only if:

* credible evidence supports a plausible positive post-cost effect after 2000;
* an economically clear forced-selling mechanism remains;
* a sufficiently complete, reproducible historical event list appears feasible;
* a realistic path to meaningful portfolio-level terminal-wealth improvement exists.

NO-GO and PAUSE, if those conditions cannot be supported.
Do not invent an expected return or treat preliminary historical observations as validation.
6. Deliverable
Produce one concise Stage 0 checkpoint documenting:

1. Supporting and conflicting published evidence.
2. The exact investable spin-off mechanism.
3. Historical event-data availability and limitations.
4. Feasibility of the proposed independent test window.
5. Economic relevance for a $100,000 long-only, unleveraged portfolio.
6. Clear GO / NO-GO recommendation and evidence gaps.

Use only existing resources. No new experiments, purchases, data extraction or infrastructure.
Record the decision, commit the checkpoint and STOP for owner approval.
H032 and H028 remain REJECTED; H031 remains parked; RR6 remains INCONCLUSIVE; the Holdout stays sealed.
