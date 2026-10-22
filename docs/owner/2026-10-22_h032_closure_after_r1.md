# Owner decision D285 — H032 closure after R1 (2026-10-22)

**Context:** follows OS-CP3 (`docs/checkpoints/OS_CP3_h032_r1_performance_E033.md`, D284, PR #131). The message is recorded verbatim below, before any work.

---

Owner Decision — H032 Closure After R1
I have reviewed OS-CP3 and the E033-01 results.
I accept R1 as technically valid and accept the frozen evaluation verdict.
H032 is REJECTED — NOT PROMISING.
The strategy failed all eight applicable R1 gates, including terminal wealth, upside participation, alpha, control comparisons and subperiod consistency.
The result is particularly important because H032 underperformed SPY while exhibiting higher beta and a worse maximum drawdown.
Decisions

1. Formally close H032 as REJECTED — NOT PROMISING.
2. Do not execute R2. Its cancellation is correct under D282 because R1 already failed the required gates.
3. Preserve all frozen specifications, run evidence, transaction records, results and research decisions unchanged.
4. Record the principal conclusions:
   * H032 CAGR 11.84% versus SPY 16.31%.
   * Upside capture 0.96 and downside capture 1.21.
   * Beta 1.17 with negative regression alpha.
   * The strategy failed the fixed controls and second development subperiod.
   * The OCF and revenue-growth filters did not improve the unfiltered share-reduction strategy in this sample.
   * The unfiltered B0 strategy also underperformed SPY.
5. Do not promote B0, the momentum diagnostic or any control portfolio as a new candidate based on these observed returns.
6. H031 remains parked. H028 remains REJECTED. RR6 remains INCONCLUSIVE. The Holdout remains sealed.

Next Step
Complete a concise closure record covering the observed failure mechanisms and the implications for our offensive stock-selection research.
Do not initiate new backtests, additional hypotheses, parameter changes, infrastructure development, purchases or data repairs.
Do not attempt to rescue H032 by removing filters, changing portfolio constraints or adjusting the ranking methodology.
I want the next research direction to be chosen through a separate, economically motivated decision—not through optimization of failed strategies on the heavily explored 2010–2021 development data.
Commit the closure and STOP for owner review.
