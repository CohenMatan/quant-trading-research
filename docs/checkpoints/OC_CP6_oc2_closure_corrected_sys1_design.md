# OC-CP6 — OC-2 Closure and Corrected SYS-1 Design

**Owner decision:** D251 (`docs/owner/2026-10-19_oc2_closure_sys1_redesign.md`). Documentation, feasibility analysis and test design only.

Nothing was run:
- no backtest, QuantConnect experiment, stock-return analysis, simulation or Holdout access;
- no registered experiment;
- every figure below is copied from committed artifacts.

**In short:**
1. OC-2 is formally **CLOSED — STATISTICAL METHOD NOT VALIDATED UNDER CURRENT RESEARCH CONSTRAINTS**. SPY is now the preferred simple offensive baseline.
2. **The original 50 / 50 SYS-1 is infeasible under the frozen account rules at both $100,000 and $200,000:**
   - The 15-position limit counts every holding, ETFs included, so 15 stocks + SPY = 16.
   - The 10% single-position cap applies to every holding, so a 50% SPY position breaks it.
   - At $100,000 a 15-stock sleeve with half the money also breaks the $5,000 minimum ($3,333 per stock).
3. **A faithful SYS-1 needs two owner decisions:**
   - a rule for index / low-volatility ETF holdings (not counted among the 15 stock positions, not subject to the 10% cap);
   - $200,000 as SYS-1's capital. That gives the frozen H028 sleeve exactly its frozen $100,000 basis, with $6,667 per stock.
4. **Honest expectation.** On the already-examined 2015–2021 data the main wealth comparison is largely predictable from known components:
   - H028 + SPY should beat SPY;
   - LV15 + SPY should lag SPY.
   SYS-1 can therefore test implementability, exposure-adjusted value and costs, but it cannot produce evidence of a durable edge.

---

## 1. Verified repository state and owner decision

- Main 8ad20e0 (PR #115 merged, OC-CP5 / D250); working tree clean.
- D250 was the latest decision; this approval is **D251**.
- QuantConnect credentials present (values never printed); reachable but not used.
- The Holdout is sealed: no `HOLDOUT_UNLOCK.md`, no post-2021 data used.
- **Verified sources:**
  - frozen H028 specification `research/phase13/H028_spec.md` and the committed E030-05 result `research/phase13/cp1/P13_CP1_result.json`;
  - OC-CP1's original SYS-1 (§16–§19);
  - D041, D044, D051;
  - `qresearch.config.RESEARCH_PORTFOLIOS`;
  - the harness order planner `qr_harness.plan_orders`;
  - the frozen H026 / H028 portfolio simulator `qr_h026.simulate`.
- Frozen results are unchanged.

## 2. Formal OC-2 closure

**OC-2 (profitability improvement, exact Data v3 F5): CLOSED — STATISTICAL METHOD NOT VALIDATED UNDER CURRENT RESEARCH CONSTRAINTS.**

- OC-2 was **never evaluated on real stock returns**. No real F5 ranking, return or Fama–MacBeth estimate exists.
- Its economic hypothesis was **not disproven**.
- Its statistical methodology **did not meet the frozen research standards**:
  - the complete decision rule could not keep false approvals ≤ 2% when a correlated hidden factor is priced;
  - it passes a true +3% effect only 43.5% of the time.
- **No further OC-2 calibration is authorised.**
- OC-2, OF-A and every other offensive stock-selection line stay closed unless the owner explicitly reopens them.
- H029 / H030 keep their historical **NOT EVALUABLE** status.
- **SPY (OC-1)** is the preferred simple offensive baseline for the next system-design investigation.

## 3. Preserved classifications

| item | classification | source |
|---|---|---|
| OC-2 Stage 1 data integrity | **PASS — PIT-SAFE AND SUFFICIENT** | OC-CP3 |
| OC-2 synthetic calibration v1 | **D — INSUFFICIENT EVIDENCE** | OC-CP4 |
| OC-2 synthetic calibration v2 | **C — NOT VALIDATED** | OC-CP5 |
| v2 Tier 1 (30 ordinary null worlds) | 30 / 30 pass the strict size gates | OC-CP5 §3 |
| v2 severe hidden factor (N2L5, IC sd 0.12) | complete-rule false approval **4.40%** vs 2% allowed | OC-CP5 §4 |
| v2 complete-rule power at +3% / yr | **43.5%** (t-test 84.6%) | OC-CP5 §9 |
| H028 | **REJECTED — Frozen Defensive Research Reference** | D220, D238–D241 |
| H029 / H030 | **NOT EVALUABLE** (historical BLOCKED) | D240 |

## 4. Frozen account constraints — what the rules actually say

| rule | frozen text / code | source | applies to ETFs? |
|---|---|---|---|
| Research capital | $100,000 primary; $200,000 diagnostic / account-size re-test only | D044; H026 spec §7 | — |
| Position limit | "maximum of 15 positions"; effective max = min(15, ⌊equity × (1 − 2%) / $5,000⌋) | D041, D044 | **Yes.** The harness counts every open position (`plan_orders`, `n_open_positions`); no rule distinguishes stocks from ETFs |
| Minimum new position | $5,000 absolute (H016 / H017 alone used $4,000 by explicit owner exception) | D041, D044; D116 | Yes (any new position) |
| Maximum weight | `max_position_weight` 10% of **account** value, applied to every position at entry; no trimming afterwards | `config.RESEARCH_PORTFOLIOS`; D171; H026 owner spec "maximum initial weight per position: 10%" | **Yes**, as written |
| No borrowing | D051: buys from settled cash only, 15% gap reserve, 2% cash buffer, whole shares | D051 (`execution_model: d051`) | Yes |
| Costs | $7 per executed order; 0.10% slippage per side | D041, H026 spec | Yes |
| Execution | next session open after the decision | D005 | Yes |

**H028's frozen mechanics differ from D051.** H028 was evaluated by its own shadow-book simulator (`qr_h026.simulate`, E030-05: 0 LEAN orders):
- notional, fractional buys at the open;
- each new position is bought at **its portfolio's equity / 15** (6.67% < 10%);
- when cash is short, new buys are scaled down equally, with no floor, so the $5,000 minimum is not enforced in code;
- no gap reserve and no cash buffer;
- no trimming;
- total-return valuation.

So "frozen H028" means these mechanics. Putting H028 under D051 would change it.

**The 10% cap's reference.** For frozen H028 the cap is relative to the whole account, because H028 was the whole account. In a combined account a sleeve stock is 3.3% of the account and 6.7% of the sleeve at entry, so the cap is not binding for stocks under either reading. **For ETFs it binds:** a 50% SPY holding is five times the cap.

## 5. Corrected SYS-1 feasibility analysis

A sleeve with share s of capital C buys each new stock at s·C / 15.

| configuration | capital | stocks + ETFs | stock ticket at start | largest holding | cash | frozen H028 unchanged? | rules violated → owner decision needed |
|---|---|---|---|---|---|---|---|
| **OC-CP1 50 / 50 H028 + SPY** | $100,000 | 15 + 1 = 16 | **$3,333** | SPY 50% | ≈ 0 (E1) | sleeve basis only | **INFEASIBLE:** position limit (16 > 15), 10% cap (SPY), $5,000 minimum |
| 50 / 50 H028 + SPY | $200,000 | 15 + 1 = 16 | $6,667 | SPY 50% | ≈ 0 | **yes** (sleeve basis = $100,000 = frozen H028 capital) | position limit + 10% cap (ETF) → **OD-1**; capital → **OD-2** |
| 50 / 50 + ETF rule (OD-1) | $100,000 | 15 + 1 | $3,333 | SPY 50% | ≈ 0 | — | **INFEASIBLE:** $5,000 minimum |
| 50 / 50, minimum waived | $100,000 | 15 + 1 | $3,333 | SPY 50% | ≈ 0 | yes | D041 / D044 minimum + OD-1; commission per order 0.21% vs 0.105% (about 2× ticket drag) — not recommended |
| 75 / 25 H028 + SPY + OD-1 | $100,000 | 15 + 1 | $5,000 | H028 stocks | ≈ 0 | sleeve basis only | at the minimum from day 1; any fall makes new buys < $5,000 → **INFEASIBLE in practice**; also a different system |
| H028-like Top-K ≤ 10, 50 / 50 + OD-1 | $100,000 | ≤ 10 + 1 | ≥ $5,000 | SPY 50% | ≈ 0 | **NO** (K is frozen at 15; Top-10 S 0.095 vs 0.224 shows K-fragility) | K change — **not recommended; not H028** |
| LV15 + SPY | same rows as H028 | 15 + 1 | same | same | same | LV15 frozen | same as the H028 rows |
| SPLV + SPY 50 / 50 | $100,000 or $200,000 | 0 + 2 | — | ETFs 50% | ≈ 0 | n/a | 10% cap (ETF) → OD-1; data → canary |
| SPY + cash (BM-X) | either | 0 + 1 | — | SPY ≤ 100% | rest | n/a | 10% cap (ETF) → OD-1 |
| SPY buy-and-hold | either | 0 + 1 | — | SPY 100% | 0 | n/a | historically run as a benchmark outside the strategy rules; same OD-1 logic |
| H028 alone | $100,000 | 15 + 0 | $6,667 | ≤ 10% at entry | ≈ 0 | yes (E030-05) | none (historical reference) |

### $100,000 versus $200,000

| | $100,000 | $200,000 |
|---|---|---|
| Exact H028 + SPY (50 / 50) | **infeasible** (minimum, count, cap) | **feasible only with OD-1 + OD-2** |
| LV15 + SPY | infeasible | feasible with OD-1 + OD-2 |
| SPLV / USMV + SPY | feasible with OD-1 | feasible with OD-1 |
| SPY + cash, SPY buy-and-hold | feasible with OD-1 | feasible with OD-1 |
| Drawdown headroom before the $5,000 minimum binds (stock sleeves) | none | account may fall 25% below $200,000 |

**Conclusion.** The original 50 / 50 SYS-1 is **INFEASIBLE** under the frozen rules as written, at both capital levels. The closest faithful design is $200,000 plus the ETF rule. Neither change may be made without the owner (§16).

## 6. Global position-limit treatment

- **Frozen reading:** the limit of 15 counts all positions (D041 / D044; the harness counts every holding). The owner's brief phrases it as "15 concurrent stock positions", but no frozen rule says "stock". I do not assume the narrower reading.
- **Proposed OD-1 clarification** (needs the owner): broad index or low-volatility ETF holdings (SPY, SPLV, USMV):
  - are **not counted** among the 15 positions, which become "15 stock positions";
  - are **exempt** from the 10% single-position cap, because the cap is a single-company concentration rule and an index fund is already diversified;
  - remain subject to every cash, no-borrowing, cost and execution rule.
- **Without OD-1, SYS-1 cannot hold a material SPY allocation at all.** The only feasible "system" would be H028 alone.

## 7. Beta-matched benchmark correction

- **What was wrong in OC-CP1:** 90% SPY + 10% cash assumes a sleeve beta of 0.8, so a system beta of 0.90. The illustrative 50 / 50 H028 + SPY beta is about 0.88, using H028's realised 0.76. LV15 + SPY would be about 0.76, using LV15's realised 0.53.
  - Both realised betas come from the examined 2015–2021 data and must not set any weight.
  - One fixed control also cannot match systems with different exposures.
- **Proposed prospective method — BM-X, one control per system:**
  - At each review t, hold SPY at w_t = the system's ex-ante beta from its **current planned holdings**, and cash for the rest.
  - The ex-ante beta is the weighted sum of Blume-adjusted (0.67 β + 0.33) trailing-252-session daily betas to SPY, computed from prices before t only. SPY counts as 1; SPLV uses its own trailing beta.
  - SPY is traded at the next open at the same costs.
  - No outcome enters, and H028's 0.76 is never used.
  - A truncation canary (C7) proves it.
- **Known limitation:** trailing betas of low-volatility stocks are noisy and tend to drift toward 1. The Blume adjustment is the standard pre-declared correction. The residual mismatch is reported as the difference between the realised betas of the system and its control.
- The fixed 90 / 10 is kept only as a **non-gating diagnostic**, with its mismatch disclosed. **SPY buy-and-hold remains the main wealth benchmark.**

## 8. ETF data availability (no QuantConnect run made to check)

| ETF | status in our infrastructure | gap for the canary |
|---|---|---|
| SPY | **Verified:** daily prices and dividends used by every H026–H028 run; SPY buy-and-hold $262,325.46 reproduced (E028-05 / E029-05 / E030-05) | none |
| Nine original Select Sector SPDRs | Verified 1998-12-22+ (E988-01); shows QuantConnect ETF daily data with distributions is usable | not used here |
| SPLV | **Identifier only:** `SPLV UWBCA8CFMB1H` in QuantConnect's security master (E970 identifier export, `research/phase2/sec/candidates.json`); inception 2011-05-05 | prices, splits, dividends 2014–2021 unverified → canary C4 |
| USMV | **Identifier only:** `USMV V0WRDXSSH205`; inception 2011-10-18 | same |
| T-bill ETF (BIL / SHV) | not checked | cash earns 0% in every arm (disclosed) |
| SPY constituent weights | not available | look-through overlap is a proxy (PIT market-cap share; diagnostic) |
| QQQ | excluded by the owner | — |

## 9. Executable portfolio construction proposal (single account)

Full specification: `research/longhorizon/sys1/SYS1_protocol_PROPOSED.md`.

- **One cash ledger, one equity line, real trades.** Every buy and sell is executed in the ledger with its own commission and slippage. No equity curves are blended.
- **Split rule:**
  - 50% sleeve / 50% SPY;
  - each new sleeve stock is bought at (50% × account equity at the open) / 15;
  - held stocks are untouched (frozen rule);
  - SPY absorbs the residual cash after the sleeve's trades at every review;
  - the sleeve weight floats between reviews.
- **Aggregate constraints, enforced and counted:**
  - ≤ 15 stocks;
  - new stock buys ≥ $5,000 (otherwise skipped: slot empty, cash to SPY);
  - cash ≥ 0;
  - no leverage;
  - ETF holdings under OD-1.
- **Stock trades** follow the frozen H028 / LV15 PIT timing. ETF trades use the same next-open convention.
- **Corporate actions:** total-return valuation for stocks and ETFs alike; delisted stocks at the last real close, turned into cash at the next review. These are the frozen conventions.
- **Overlap:** sleeve stocks are also inside SPY. There is no netting; a look-through proxy is reported.
- **Exact-H028 check:** the engine at s = 1 must reproduce E030-05 exactly (canary C1). Only then is the A1 sleeve "frozen H028".

## 10. Transaction-cost treatment

- $7 per executed order (stocks and ETFs) and 0.10% slippage per side on traded value. Every arm is repeated at 0.20%.
- **Illustration** from committed turnover (H028 about 7.4–7.8× a year; $5,789 commissions in 7 years at $100,000; not a new computation):
  - at a $6,667 ticket, a commission is 0.105% of the order;
  - at $3,333 it would be 0.21%, which is why the $100,000 50 / 50 design would roughly double the commission drag.
- SPY absorption adds at most two ETF orders a month.
- ETF expense ratios are inside ETF prices (SPY about 0.09%, SPLV 0.25%, USMV 0.15% a year).

## 11. Prospective evaluation gates — review of P-1 to P-5

| OC-CP1 gate | status | corrected form (protocol §11) |
|---|---|---|
| P-1 system wealth > SPY | **kept**, as the primary wealth question; but **predictable**: a never-rebalanced 50 / 50 split of the committed endpoints gives 0.5 × $328,295 + 0.5 × $262,325 = $295,310 vs SPY $262,325 (arithmetic on committed figures, not a simulation) | FS-3 |
| P-2 system > 90 / 10 | **redesigned:** the fixed control mismatches the exposure | FS-2 versus each system's own ex-ante BM-X |
| P-3 system > LV15 + SPY and > ETF + SPY | **kept** (complexity question); the LV15 part is largely known (sleeve endpoints $328,295 vs $220,156); SPLV is genuinely new | FS-6 |
| P-4 not episodic | **kept unchanged** (defined in OC-CP1, not re-tuned); known risk: H028's advantage came from SPY-down months, mostly 2018 and 2020 | FS-5 (versus BM-X) |
| P-5 0.20% slippage | **kept** | FS-4 |
| new | implementation | FS-1 (canary, zero rule violations) |

**Can the development evidence justify a reliable pass / fail gate?** Only partly.
- The A1 wealth result (FS-3) and the A1-versus-LV15 part of FS-6 are close to determined by already-known component results, so passing them carries little information.
- FS-1, FS-2, FS-4, FS-5 and the SPLV comparison are not determined in advance.
- I therefore propose **falsification screens, not qualification gates:**
  - **NOT EXECUTABLE** if FS-1 fails;
  - **NOT SUPPORTED** if any of FS-2 to FS-6 fails;
  - otherwise **NOT FALSIFIED — DEVELOPMENT-CONSISTENT**, which is explicitly not "qualified".
- Q1 (risk / downside) is answered descriptively.

## 12. Interpretation limits of in-sample results

- 2015–2021 has been examined repeatedly: H026–H028, P11-CP2, P13-CP2 to CP4, OC-CP1.
- A positive SYS-1 cannot:
  - prove a durable edge;
  - requalify H028;
  - establish stock-selection alpha;
  - open the Holdout by itself.
- A negative SYS-1 weakens the tested architecture at the tested 50 / 50 weight. It does not invalidate every defensive allocation.
- Lower beta is not alpha. FS-2 exists to separate the two.

## 13. What SPY can and cannot fix, and transparent alternatives

- **SPY can address** H028's upside shortfall in strong rallies (0.87 capture when SPY ≥ +5%; beta 0.76), by raising market exposure.
- **SPY cannot repair:**
  - H028's unvalidated alpha (B4 failed; p-value structurally suspect, D238; repair not validated, D239);
  - Top-K fragility;
  - dependence on the 2018 / 2020 episodes;
  - turnover costs (about 7.5× a year).
- **Could a transparent defensive sleeve be preferable to H028 even with lower raw returns?** As a risk-reduction tool, plausibly yes:
  - LV15 or SPLV involve no learned model and no unreliable significance claim;
  - SPLV needs no stock trading at all, so it is feasible at $100,000 and has no Top-K fragility;
  - LV15's 2015–2021 drawdown was −16.5% vs SPY −33.7%.
- **But under the owner's objective (wealth relative to SPY) it does not look attractive on the known data:**
  - LV15 alone compounded at 11.9% a year vs SPY 14.8%;
  - a never-rebalanced 50 / 50 LV15 + SPY split of the committed endpoints gives $241,241 vs SPY $262,325 (arithmetic, not a simulation).
- A transparent sleeve would answer Q1 (smoother path), not Q2 (more wealth). SPLV's 2015–2021 behaviour has not been examined.

## 14. Required canary and future experiment budget

- **IDs on approval:** host **S032** (wrapper of frozen S030 / S029; null-mode files removed to stay within 50 project files); canary **X032**.
- **Runs:**
  - **E032-01** canary (C1–C9, protocol §9);
  - **E032-02** one evaluation computing all arms and both slippage levels;
  - at most two technical retries for documented infrastructure failures, identical code.
- **Spend:** none beyond the existing $24 a month QuantConnect plan; no data purchase.
- **Technical risks:**
  - memory (S030 peaks at 7.7–7.8 GB against an 8 GB node);
  - the 50-file limit;
  - QuantConnect compliance (aggregates only, D185).
- **Offline evaluation script:** committed before any run.
- No experiment is registered now.

## 15. One recommended SYS-1 design

**SYS-1 (corrected) — $200,000, single account, falsification screens** (protocol `research/longhorizon/sys1/SYS1_protocol_PROPOSED.md`):
- **Primary system A1:** 50% frozen-H028 sleeve (sleeve basis $100,000 at the start = frozen H028's capital) + 50% SPY.
- **Comparators:** A0 SPY buy-and-hold; A2 LV15 + SPY; A3 SPLV + SPY (if verified).
- **Controls:** BM-X for each system.
- **Diagnostics:** D1 H028 alone (replay), D2 90 / 10, D3 USMV + SPY.
- **Execution:** E1 (frozen H028 shadow-book convention) for every arm; $5,000 minimum overlay; costs at 0.10% and 0.20%.
- **Screens and classification:** FS-1 to FS-6 → NOT EXECUTABLE / NOT SUPPORTED / NOT FALSIFIED.

**Recommendation on whether to run it at all.** It is worth one canary and one run **only if** the owner accepts OD-1 and OD-2. Its useful new information is:
- implementability under the account rules;
- value beyond exposure-matched SPY;
- cost robustness;
- the SPLV comparison.

If OD-1 or OD-2 is declined, no faithful H028 + SPY test exists, and the programme should default to **SPY**.

## 16. Exact unresolved owner decisions

| id | decision | options | recommendation |
|---|---|---|---|
| **OD-1** | ETF treatment | (a) index / low-vol ETFs not counted among the 15 positions and exempt from the 10% cap; all other rules apply · (b) counted but exempt from the cap (then 15 stocks + SPY = 16 → infeasible) · (c) no change (→ SYS-1 infeasible) | (a) |
| **OD-2** | SYS-1 capital | (a) $200,000 for SYS-1 only; $100,000 stays the programme baseline · (b) $100,000 (→ the H028 / LV15 arms are infeasible; only ETF arms remain) | (a) |
| **OD-3** | Execution convention | (E1) frozen H028 shadow book (notional fractional at the open, no gap reserve) for every arm · (E2) D051 whole shares, 2% buffer, 15% reserve for every arm (H028 then not frozen) | E1 |
| **OD-4** | Transparent ETF comparator | SPLV gating, USMV non-gating diagnostic; if SPLV fails canary C4 the arm is dropped and disclosed (no substitute search) | as stated |
| **OD-5** | Cross-sleeve rule | (a) sleeve basis = 50% of account equity at each review, no trimming, SPY absorbs the residual · (b) never rebalance between sleeves | (a) |
| **OD-6** | Evaluation type | (a) falsification screens FS-1 to FS-6 (NOT SUPPORTED / NOT FALSIFIED) · (b) descriptive feasibility report only, no screens | (a) |
| **OD-7** | Authorisation | canary E032-01 + one evaluation E032-02 (+ ≤ 2 technical retries); host S032 / X032; no spend | approve only together with OD-1 / OD-2 |

## 17. Mandatory STOP confirmation

**STOPPED — returning for owner review.** Not done and not authorised:
- running SYS-1, QuantConnect backtests or any performance curve;
- modifying H028, Top-K, capital or position rules;
- optimising allocations;
- reopening OC-2 or starting any offensive stock-selection search;
- purchasing data;
- opening the Holdout.
