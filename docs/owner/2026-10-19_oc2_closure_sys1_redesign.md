# Owner decision D251 — Close OC-2 and Redesign SYS-1 (2026-10-19)

**Context:**
- This follows D250 / OC-CP5 (`docs/checkpoints/OC_CP5_oc2_synthetic_calibration_v2.md`, merged in PR #115, main 8ad20e0).
- The decision covers research documentation, feasibility analysis and test design only.
- The message is recorded verbatim below.

---

Owner Approval — Close OC-2 and Redesign SYS-1
H028 + SPY: Executable Portfolio Feasibility and Test Design
I approve two actions:

1. Formally close OC-2 under the current research constraints, preserving its methodological findings.
2. Prepare a corrected, executable design for SYS-1, comparing H028 + SPY against simpler defensive and market-exposure alternatives.

This approval is for research documentation, feasibility analysis and test design only.
Do not run any new backtest, QuantConnect experiment, stock-return analysis, performance simulation or Holdout evaluation.
1. Verify and Record the Owner Decision
Verify:

* Latest merged main branch and working-tree status.
* PR #115 and OC-CP5.
* D250 as the latest owner decision, unless a newer legitimate decision exists.
* Frozen H028 specifications and historical results.
* OC-CP1's original SYS-1 proposal.
* Existing capital, position-size and trading constraints.
* Holdout status.

Record this authorization as the next available owner decision, expected to be D251 if D250 is still the latest.
Do not change frozen experimental results.
2. Formally Close OC-2
Record OC-2 as:
CLOSED — STATISTICAL METHOD NOT VALIDATED UNDER CURRENT RESEARCH CONSTRAINTS.
Preserve:

* Stage 1 data integrity: PASS.
* Synthetic calibration v1: D — INSUFFICIENT EVIDENCE.
* Synthetic calibration v2: C — NOT VALIDATED.
* The successful calibration of all 30 ordinary null worlds.
* The severe hidden-factor false-approval failure: 4.40% versus the allowed 2%.
* The 43.5% full-rule power at the +3% annual reference effect.

Clarify explicitly:

* OC-2 was never evaluated on real stock returns.
* Its economic hypothesis was not disproven.
* Its statistical methodology did not meet our frozen research standards.
* No further OC-2 calibration is authorized.
* H029 and H030 retain their historical NOT EVALUABLE statuses.

Update the research roadmap, decision log and selection ledger accordingly.
Do not resume OC-2, OF-A or any other offensive stock-selection investigation automatically.
SPY becomes the preferred simple offensive baseline for the next system-design investigation.
3. Redesign SYS-1 Around Our Actual Objective
Our objective is:
Determine whether combining market exposure through SPY with a defensive stock-selection component provides a credible, economically meaningful benefit over SPY Buy & Hold, after realistic costs.
The experiment must answer two distinct questions:

1. Does defensive exposure improve risk-adjusted outcomes or downside behavior?
2. Does the defensive component contribute enough incremental economic value to justify its complexity and any reduction in terminal wealth?

We care primarily about long-term wealth accumulation relative to SPY.
Lower volatility by itself is not sufficient.
A smoother equity curve that consistently sacrifices substantial long-term wealth is not automatically acceptable.
H028 remains:
REJECTED — Frozen Defensive Research Reference.
A SYS-1 success cannot retroactively qualify H028 or establish independent stock-selection alpha.
4. Critical Issue: Portfolio Feasibility
Before proposing a SYS-1 implementation, verify all historical account-level constraints from the owner's frozen decisions.
Our baseline includes:

* $100,000 research capital.
* $200,000 diagnostic capital.
* Long-only.
* No leverage.
* Maximum 15 concurrent stock positions, subject to the exact frozen definition.
* Minimum $5,000 per new stock position.
* Maximum 10% position allocation under the applicable frozen sizing rule.
* $7 per executed order.
* 0.10% slippage per side.
* Next-open execution after a valid decision.

Check whether the 15-position limit includes or excludes ETF holdings according to the actual approved rules.
Do not assume.
The 50/50 Construction Problem
OC-CP1 proposed:

* 50% H028.
* 50% SPY.

At $100,000:

* The H028 stock sleeve receives $50,000.
* Fifteen positions at a minimum of $5,000 each require $75,000.
* Therefore a fully populated 15-stock sleeve appears infeasible under the minimum position size.

Also verify whether H028's 10% cap is measured relative to:

* The entire account; or
* The defensive sleeve.

The choice materially changes feasibility.
At $200,000:

* The defensive sleeve receives $100,000.
* Fifteen positions may satisfy the minimum position requirement.
* However, the global position-count rule and ETF treatment must still be verified.

Do not silently reduce H028's Top-K from 15 to 10.
Do not increase the number of allowed positions.
Do not waive the minimum trade size.
Do not change the frozen sizing logic.
Do not switch the baseline from $100,000 to $200,000 without explicit owner approval.
If the original 50/50 SYS-1 cannot satisfy the constraints, clearly classify it as infeasible and propose alternatives requiring separate owner decisions.
For each alternative, report:

* Capital required.
* Number of stock and ETF positions.
* Minimum stock trade size.
* Maximum position size.
* Cash requirements.
* Whether the original H028 strategy remains unchanged.
* Which owner rule would need modification, if any.

An approximate H028-like portfolio is not equivalent to the frozen H028 strategy.
5. Avoid Misleading Beta-Matched Comparisons
OC-CP1 proposed:
90% SPY + 10% cash as a beta-matched control.
However, the illustrative 50/50 H028 + SPY mixture has beta approximately:
0.5 × 0.76 + 0.5 × 1.0 = 0.88.
Therefore a 0.90-beta control is only an approximate exposure comparator, not an exact match.
Also, H028's 0.76 beta was measured on already examined development data.
Do not optimize comparator weights using that historical result.
Propose a prospective method for defining risk- or beta-matched benchmarks using only information that would have been available before the evaluation period.
If reliable ex-ante matching is not possible, use transparent predeclared approximate controls and disclose their mismatch.
Keep SPY Buy & Hold as the main wealth benchmark.
No outcome-based weight fitting.
No retrospective search for the best combination.
6. Compare Against Simple Alternatives
The corrected design should include the following candidate comparators where executable:

1. SPY Buy & Hold.
2. Frozen H028 alone — historical development reference.
3. H028 + SPY.
4. Transparent LV15 defensive sleeve + SPY.
5. Low-volatility ETF (USMV or SPLV) + SPY, if historical availability can be established.
6. SPY + cash as an approximate lower-beta control.

Only include portfolios that can be implemented with the approved account restrictions.
The same financing, cash, dividend, commission and slippage assumptions must apply consistently.
Verify whether the required ETF price data have already been confirmed in our research infrastructure.
Do not run QuantConnect merely to check availability at this stage.
List unresolved data dependencies for the future canary.
Do not introduce QQQ as a new selectable candidate in this test.
7. One Executable Account
Any future backtest must simulate a single real investment account.
Requirements:

* Aggregate position count enforced.
* Aggregate exposure enforced.
* No borrowing.
* Cash sufficiency enforced.
* Stock trades follow existing PIT timing.
* ETF trades use the same valid execution conventions.
* Realistic commission and slippage on executed trades.
* Explicit handling of overlapping stock exposure through the ETF.
* Consistent dividends, splits and corporate actions.
* No synthetic blending of separately generated equity curves as a substitute for execution.

If the exact frozen H028 + SPY combination cannot be implemented, do not disguise a modified strategy as H028.
8. Primary Test Objective and Interpretation
SYS-1 should be a development-period falsification and implementation test, not a proof of statistical significance or future profitability.
The development period remains the verified H028 evaluation window:
2015–2021.
This history has already been examined extensively.
Therefore:

* A positive result cannot prove a durable investment edge.
* A negative result can weaken the case for the specific tested architecture.
* A negative result for one weight does not invalidate every possible defensive allocation.
* A positive result does not automatically justify opening the Holdout.

Specify:

* One primary investable combination, if feasible.
* Fixed benchmark portfolios.
* Predeclared capital and position rules.
* Net terminal wealth comparisons.
* Risk and downside comparisons.
* Transaction costs.
* Rolling and subperiod diagnostics.
* Concentration of advantage in 2018 and 2020.
* Sensitivity to doubled slippage.
* Explicit failure and stopping conditions.

Review the previous P-1 through P-5 gates.
Identify which gates remain justified and which require redesign because of account feasibility, mismatched exposure or overly strong interpretation.
Do not optimize new gates against known historical results.
If the available development evidence cannot justify a reliable pass/fail gate, say so and propose a descriptive feasibility assessment instead.
9. Historical Evidence and H028 Limitations
Preserve the existing findings:

* H028 beta approximately 0.76.
* Nearly full average upside participation but weaker capture during strong rallies.
* Historical relative advantage concentrated in SPY-down periods.
* Important dependence on 2018 and 2020.
* Top-K fragility.
* High turnover.
* Failed B4 qualification.
* Unreliable original significance evidence.

Explain what SPY exposure could address and what it cannot.
SPY may improve upside exposure, but it cannot repair:

* Unvalidated H028 alpha.
* H028's selection fragility.
* Historical episode concentration.
* H028's turnover costs.

Evaluate whether a transparent defensive alternative could be preferable to H028 even if its historical raw returns are lower.
10. Prepare the Corrected SYS-1 Protocol
Create a proposed, reproducible SYS-1 specification containing:

1. Exact account-level allocation rules.
2. Capital baseline.
3. Position-limit interpretation.
4. Minimum position-size requirements.
5. Frozen H028 compatibility.
6. Transparent defensive alternatives.
7. SPY and exposure-matched controls.
8. Required historical data.
9. Rebalance timing.
10. Order execution.
11. Cost assumptions.
12. Canary reproduction checks.
13. Primary economic comparison.
14. Robustness requirements.
15. Development-period interpretation.
16. Explicit limitations.
17. Next owner authorization needed.

Provide a feasibility matrix showing what can and cannot be implemented at both $100,000 and $200,000.
If a feasible exact H028 + SPY test requires a change in account constraints, present the required owner decision clearly.
Do not approve the change yourself.
11. Required Deliverables
Create:
OC-CP6 — OC-2 Closure and Corrected SYS-1 Design
Include:

* Verified repository and owner decision.
* Formal OC-2 closure.
* Preserved historical classifications.
* Corrected SYS-1 feasibility analysis.
* $100K versus $200K comparison.
* Global position-limit treatment.
* Beta-matched benchmark correction.
* ETF data availability assessment.
* Executable portfolio construction proposal.
* Realistic transaction-cost treatment.
* Prospective economic evaluation gates.
* Interpretation limits of in-sample results.
* Required canary and future experiment budget.
* One recommended SYS-1 design.
* Exact unresolved owner decisions.
* Mandatory STOP confirmation.

Update the appropriate research documentation and ledger.
A documentation-only PR may be committed and merged under the normal workflow.
Do not register or execute new experimental runs.
12. Mandatory STOP
After completing OC-CP6:
STOP AND RETURN FOR OWNER REVIEW.
You are not authorized to:

* Run SYS-1.
* Run QuantConnect backtests.
* Generate new real-return performance curves.
* Modify H028.
* Optimize allocations.
* Change Top-K.
* Change capital or position restrictions.
* Reopen OC-2.
* Begin a new offensive stock-selection search.
* Purchase datasets.
* Open the Holdout.

The next owner decision will determine whether a feasible SYS-1 test should actually be run.
Our research priority is now to determine whether a simple, implementable defensive + SPY architecture has a credible economic advantage over SPY alone.
Do not mistake a lower-beta portfolio for stock-selection alpha.
Do not mistake historical development success for independently validated evidence.
Preserve scientific integrity, and design something we could actually invest in under our stated constraints.
