# Owner message — 2026-10-18 (D247)

**Scope recorded by Claude:** candidate discovery and research design only, before SYS-1.
- **Allowed:** inspecting committed results and code, data inventory and coverage from committed non-return aggregates, literature, analytical power equations, one concrete test proposal, roadmap / ledger updates, and a documentation-only PR.
- **Not allowed:** backtests, new returns or performance curves, new signals on real stocks, synthetic experiments, optimisation, reopening frozen hypotheses, changing H028, running SYS-1, the Holdout, purchases, or advancing automatically.
- **Statuses unchanged:** H028 REJECTED; H029 / H030 NOT EVALUABLE; OF-A unqualified and underpowered for modest effects under the D245 population; no production candidate; Holdout sealed.
- **No new active hypothesis.**
- **Mandatory STOP** after the checkpoint (OC-CP2).

The message follows verbatim.

---

Owner Direction — Prioritize Independent Offensive Stock Selection
H028 Complement Research — Candidate Discovery Before SYS-1
I want to clarify the research priority following OC-CP1 (D246).
I am open to using SPY as the offensive complement to H028, but I want us to first make a serious, disciplined attempt to identify an independent stock-selection strategy that could complement H028.
Do not proceed with SYS-1 yet.
Do not treat SPY as the final recommended solution until the remaining stock-selection opportunities have been carefully examined.
Our goal is to identify a credible strategy that:

1. Selects individual US stocks.
2. Has a return mechanism economically distinct from H028.
3. Could improve participation in sustained bull markets.
4. Can be tested with historical data we already possess.
5. Could add value to a future combined portfolio beyond simply increasing SPY exposure.
6. Can be implemented after realistic transaction costs.
7. Does not rely on fitting specific years where H028 underperformed.

This is a candidate-discovery and research-design approval only. It does not authorize a new backtest, simulation, signal computation, or Holdout access.
1. Review the Existing Research Honestly
Inspect the current repository and verify the latest owner decision.
Review the complete H001–H030 hypothesis history, OC-CP1, H028's post-mortems, and the long-horizon checkpoints.
Preserve formal statuses:

* H028: REJECTED.
* H029/H030: NOT EVALUABLE.
* OF-A: unqualified and underpowered for modest effects under the D245 population.
* No active production candidate.
* Holdout sealed.

OC-CP1 concluded that momentum, growth, quality and other stock-selection families were effectively exhausted.
I want that conclusion critically examined, not automatically repeated.
For each family distinguish:

* What was actually tested.
* What failed economically.
* What failed because of methodology or data.
* What was never evaluated.
* What would merely duplicate a rejected hypothesis.
* What genuinely distinct mechanism, if any, remains untested.

Do not restart a rejected hypothesis under a different name.
But also do not equate "previous implementations failed" with "every possible mechanism in this research family is impossible."
2. Use Existing Data as a Hard Constraint
Prioritize the data already available through our current infrastructure:

* Historical US equity prices and volume.
* PIT universe and liquidity filters.
* Market capitalization.
* Existing sector classifications.
* Price momentum and volatility inputs.
* Data v2.1 fundamentals.
* Data v3 fundamentals, subject to documented PIT and coverage restrictions.
* Previously validated SEC event and filing data.
* Existing corporate-action and total-return infrastructure.

For each potential candidate, verify:

* Earliest usable research date.
* Available historical coverage.
* PIT correctness.
* Necessary financial fields.
* Whether additional data preparation is required.
* Whether existing statistical limitations would prevent a meaningful test.

Prefer research that can use the existing 2011–2021 history where justified.
Do not purchase data or propose a new paid dataset as the primary solution.
Do not access the Holdout.
3. Search for Economically Distinct Mechanisms
Explore a small number of well-motivated stock-selection families, including where appropriate:
A. Business improvement and fundamental momentum
Revisit what H029 F1–F8 was actually designed to measure.
H029 was never return-evaluated.
Determine whether a narrowly defined, independently justified business-improvement mechanism remains worth investigating despite the limited quarterly history.
B. Sustained leadership and price-based mechanisms
Examine the prior momentum and trend experiments.
Determine whether any substantively different mechanism remains that is not simply another lookback period, filter or score variation.
C. Growth with independent confirmation
Investigate whether existing data support a growth mechanism genuinely different from the previously rejected quality-growth scores.
Do not simply combine old factors under a new label.
D. Other existing-data mechanisms
Consider other economically defensible stock-selection mechanisms identifiable from available price, volume, sector, corporate-action or validated fundamental data.
Do not restrict the search to these headings if repository evidence supports another mechanism.
Do not invent a new hypothesis merely to satisfy this instruction.
Identify at most three serious candidate families for detailed comparison, then recommend one.
Literature may support the economic rationale, but the ability to test the idea must come from our existing data.
4. What It Means to Complement H028
H028's observed development profile includes:

* Beta approximately 0.76.
* Upside capture approximately 0.97.
* Upside capture approximately 0.87 in SPY months of +5% or more.
* Downside capture approximately 0.69.
* Concentrated historical relative performance in 2018 and 2020.
* Significant turnover and Top-K sensitivity.
* Unvalidated stock-selection alpha.

A complementary strategy should be evaluated for an economically independent source of upside participation.
However:

* Do not optimize directly against H028's historical losing months.
* Do not target particular years.
* Do not use historical correlation with H028 as the primary candidate-selection criterion.
* Do not assume higher beta equals alpha.
* Do not assume a combination will repair H028's failed validation.

Select candidates based on their independent rationale and data feasibility first.
Only later evaluate portfolio-level complementarity.
5. SPY Is the Baseline, Not the Default Answer
Keep SPY as the simple offensive alternative.
Any future individual-stock strategy should justify its complexity relative to allocating the offensive capital to SPY.
Compare candidates conceptually on:

* Expected source of return.
* Market and style exposure.
* Potential upside participation.
* Concentration risk.
* Turnover and costs.
* PIT data quality.
* Statistical detectability.
* Implementation effort.
* Incremental value beyond simply increasing market beta.

Do not conclude that a candidate is useful merely because it is different from H028.
A candidate can be complementary without outperforming SPY in every period, but its incremental net economic contribution must be evaluated against simple feasible alternatives.
6. Statistical Power and Research Governance
Do not repeat the OF-A research path without confronting the lessons of LH-CP4.
For every serious candidate, estimate analytically whether the existing history is sufficient to detect an economically meaningful effect.
Distinguish:

* Stock-selection evidence.
* Portfolio-level evidence.
* Incremental value of combining strategies.
* A meaningful economic return advantage from statistically significant evidence.

Do not arbitrarily demand a 5% annual edge simply because the historical sample cannot reliably detect a smaller one.
If modest effects are underpowered, report that limitation honestly.
Avoid the invalid conditional-null methods documented in D238 and D239.
Any new inference method requiring synthetic calibration must have its validation protocol frozen before use.
Do not claim that a development-period result becomes independent merely because we create a new hypothesis name.
7. Propose One Specific Candidate and Test
The final outcome of this checkpoint must be concrete.
For the best remaining stock-selection candidate, specify:

1. Economic mechanism.
2. Exact distinction from earlier hypotheses.
3. Why it could complement H028.
4. Existing data source.
5. PIT-safe research period.
6. Proposed signal definition.
7. Expected update and holding frequency.
8. Investability constraints.
9. Primary independent signal test.
10. SPY and style-matched benchmarks.
11. Required statistical calibration.
12. Economically meaningful effect size.
13. Analytical power limitations.
14. Trading costs.
15. Stop/failure criteria.
16. Multiple-testing treatment.
17. What result would justify a subsequent combined-portfolio test.
18. What result would stop this research line.

Keep the first experiment minimal.
Prefer one clearly motivated signal over another large parameter search.
Do not execute that experiment yet.
8. Combined-Portfolio Requirements
If a standalone candidate eventually qualifies, separately investigate combining it with the frozen H028 reference.
The combined portfolio must be simulated as a single investable account with real costs and aggregate position limits.
Compare against:

* SPY.
* H028 alone.
* The offensive candidate alone.
* H028 + SPY.
* A transparent defensive sleeve + SPY.
* A transparent defensive sleeve + the offensive candidate.

Do not select weights using historical hindsight.
Check the feasibility of minimum position sizes and concentration limits at $100,000 and $200,000 before proposing an allocation.
H028 must not be modified or used as a production component without further independent evidence.
9. Required Deliverable
Create a concise but evidence-backed checkpoint:
OC-CP2 — Independent Offensive Stock-Selection Candidate Review
Include:

* Verified repository state and authorization.
* Critical assessment of the "all families exhausted" conclusion.
* Previously tested versus genuinely untested mechanisms.
* Existing-data coverage matrix.
* No more than three serious candidate families.
* One preferred stock-selection candidate, if justified.
* Why it might complement H028.
* Why SPY remains an important baseline.
* Statistical feasibility and limitations.
* Exact first test specification.
* One backup or a justified STOP recommendation.
* The next explicit owner approval required.

Update the roadmap and selection ledger only as needed.
Record this owner direction under the next available decision ID.
A documentation-only PR may be committed and merged under repository conventions.
10. Mandatory STOP
Do not:

* Run backtests.
* Compute new returns or historical performance curves.
* Compute new signals on real stocks.
* Run synthetic experiments.
* Optimize weights or parameters.
* Reopen frozen hypotheses.
* Change H028.
* Run SYS-1.
* Use the Holdout.
* Purchase data.
* Advance automatically to the next research stage.

STOP after the checkpoint and return for owner review.
If no genuinely distinct and credible stock-selection candidate can be found using our existing data, explicitly say so.
Only then should we return to SPY as the preferred offensive complement or reconsider the research constraints.
Our priority is to give independent offensive stock selection a fair but disciplined examination before settling on a simple SPY-based architecture.
