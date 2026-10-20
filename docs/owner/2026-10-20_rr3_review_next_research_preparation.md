# Owner decision D265 — RR3 review and next research preparation (2026-10-20)

**Context:**
- This follows RR3 (D264, `docs/checkpoints/RR3_universe_baseline_audit_E804_01.md`, PR #123).
- The message is recorded verbatim below, before any work.

---

Owner Decision — RR3 Review and Next Research Preparation
I have reviewed RR3 and the E804-01 results.
The findings are encouraging. The current QuantConnect dataset appears materially more usable than the earlier October snapshot.
However, I want to preserve research integrity while avoiding another lengthy infrastructure project.
1. Accept the Audit Findings
Accept RR3 W1 = PASS-A as the outcome of the pre-registered universe audit for the measured, structurally classified population over 2010–2021.
This does not establish that the entire eligible US common-stock universe is survivorship-bias-free.
Continue to disclose:

* The remaining missing-market-cap population.
* The unclassified no-fundamentals population.
* Missing structural-classification fields.
* Unassessable 2021 survivorship.
* Dataset and engine version instability.

Do not silently interpret PASS-A as proof that all potentially eligible securities were included.
2. Historical Confirmation
Accept RR3 W0 = FAIL.
The current QuantConnect data cannot support our required PIT market-cap universe over 1999–2009.
Do not amend D033 or D035.
Keep the 2022–2026 Holdout sealed.
Any future confirmation plan must explicitly account for the lack of an independent historical validation period.
3. Retire U-B
Accept the rejection of the QuantConnect share-count reconstruction approach.
Do not use U-B to repair historical market capitalization.
Preserve the failure evidence and its PIT limitations.
4. Remaining Universe Blind Spots
I do not yet approve treating the no-fundamentals or unclassified population as harmless.
Before proposing additional infrastructure, perform a bounded offline feasibility assessment using existing repository records and independently sourced public SEC information where already available.
Determine:

* Whether the potentially missing US common-stock population can be bounded more tightly.
* Whether the gap could materially affect our $2B universe and survivorship conclusions.
* What can be established without exporting QuantConnect Platform Data or performing new cloud runs.
* Whether a narrowly scoped, free SEC-based classification check would be feasible.
* The minimum effort required.

Do not implement U-C, upload data or start a large identity-reconstruction project under this instruction.
If the gap cannot be resolved cheaply, explain the implications and present a clearly identified owner decision rather than automatically accepting the bias.
5. Prepare the Next Research Stage
In parallel, proceed with the offline design work proposed in RR2 and RR3:
A. Prepare the candidate-discovery and confirmation criteria for freezing, retaining the distinction between development evidence and independent validation.
B. Assess K1 — Dividend-event drift.
Verify point-in-time signal availability, dividend announcement versus ex-date timing, dividend-adjusted returns, event frequency, and compatibility with the existing portfolio constraints.
C. Assess K2 — Market-trend exposure control.
Verify feasible portfolio construction under our current 15-position limit, $5,000 minimum position, 10% maximum initial allocation, long-only requirement and existing cost model.
Pay particular attention to whether K2 is genuinely feasible as a broad-market strategy without requiring exceptions to our portfolio rules.
Do not register either hypothesis yet.
6. Execution Boundaries
No strategy backtests, additional QuantConnect runs, purchases, new subscriptions, Holdout access or modifications to frozen experiments.
Keep the infrastructure minimal.
Prepare a concise next checkpoint covering:

1. RR3 decisions and limitations.
2. Remaining universe-risk assessment.
3. Frozen candidate-screen proposal.
4. K1 and K2 feasibility verdicts.
5. Minimum actions required to begin the first legitimate strategy experiment.

Commit documentation through the normal workflow and STOP for my approval.
The priority remains returning to efficient strategy discovery with our existing resources, without weakening research integrity or building unnecessary infrastructure.
