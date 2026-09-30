# Phase 2: revised evaluation methodology (P2-CP0b)

| Field | Value |
|---|---|
| Date | 2026-09-30 |
| Status | **PROPOSAL. STOP, awaiting owner approval.** Nothing is implemented, no H014 backtest has run, and the 2022–2026 Holdout was not accessed in any form. |
| Replaces | §11 (statistics), §12 (periods), §13 (multiple testing), §15 (run count) and the Validation parts of `P2_CP0_research_proposal.md`. All other parts of that proposal (H014 rules, controls, portfolio, costs) stand unchanged. |
| Owner request | "Phase 2 — Revise Evaluation Philosophy Before H014 Execution" |
| Evidence | `research/phase2/P2_methodology_sim.py/.json`: a simulation of the whole pipeline (development screen, then Holdout, then forward test), with correlations calibrated on committed pre-Phase-2 in-sample results; 200,000 repetitions; seed 20261002. Also `P2_feasibility.py/.json`. |

## 0. Summary

- **Adopted:**
  - 2010–2021 is the development data;
  - DSR becomes a **reported warning, not a gate**;
  - one fully frozen candidate may go to the untouched 2022–2026 Holdout;
  - the Holdout is used **once**.
- **Advancement to the Holdout** requires a small set of pre-declared, economically meaningful gates. They combine benchmark superiority, controls, consistency, robustness and costs; most other items become diagnostics.
- **Two statistical problems with the requested philosophy as stated:**
  1. **A 4.7-year Holdout is a weak test on its own.** A strategy with **no** edge passes a "beat EW" check there about **30%** of the time.
  2. **Without DSR as a gate, false acceptance grows with every hypothesis screened on the same development data.** It reaches about 20% after 3 hypotheses, 27% after 5 and 35% after 10.
- **Proposed practical fix (it keeps your philosophy):**
  - a **hypothesis budget**: at most 3 hypotheses screened against this Holdout;
  - a development margin that **rises** with each hypothesis (+0.20, +0.30, +0.40 Sharpe over EW);
  - a **2-year forward test** after the Holdout, before any real-money decision.

  With these, false acceptance stays at or below about 12% (about 6% with the forward test). A genuine +0.3 Sharpe edge keeps about 53–57% acceptance, and a +0.5 edge about 84–86%.
- **A hindsight risk specific to this Holdout.** We know 2022 was a bear market, which a trend filter tends to benefit from. So the Holdout gate should also require the advantage to hold **outside 2022**.

## 1. What changes from the previous framework

| Element | C01–C03 framework | Phase 2 (proposed) |
|---|---|---|
| Development data | IS 2010–2017 | **2010–2021**, all of it development. Nothing in it is called "Validation". |
| Out-of-sample test | VAL 2018–2021, then Holdout at CP5 | **Holdout 2022-01-01 → 2026-08-31, used once, for one frozen candidate** |
| DSR | Hard gate (≥ 0.90) | **Diagnostic warning**, reported at 3 trial counts |
| PBO | Hard gate, then diagnostic | Diagnostic |
| IS screen (10+ items, all must pass) | Many correlated hard gates | **4 gate groups** (§5); everything else is a diagnostic |
| Trade-level items (≥ 100 trades, profit factor, expectancy interval, without the best 5%) | Hard gates | Diagnostics (concentration is covered by gate G3) |
| Positive years ≥ 5 of 8; largest year ≤ 40% | Hard gates | Replaced by a 2-year-block consistency gate (G3) |
| IS stress episodes vs EW | Hard gate | Diagnostic (drawdown is covered in G1) |
| 2× slippage | Hard gate | Kept (G4) |
| Robustness plateau | Hard gate | Kept, redefined against EW (G4) |
| Controls | Diagnostics | **Hard gate** (G2): the hypothesis must beat its own controls |
| After the Holdout | — | **Forward test** on data after 2026-08-31, before any real-money decision |

## 2. The exact role of DSR

- DSR is computed with the frozen method (D082 §3) on the development data (2010–2021), for the candidate that is to advance. It is reported at three trial counts:
  - **P2 official** = Phase 2 selection candidates (2 for H014; 0.62 is the Sharpe that would be needed);
  - **P2 conservative** = selection + robustness + technical-variant counts (about 13; about 1.2 needed);
  - **cumulative** = the 40 programme-1 candidates plus Phase 2's (42; about 1.45 needed).
- **It never blocks advancement by itself.** A DSR below 0.90 is printed in the report as a **statistical-confidence warning**, together with the plain-language meaning. For example: "after 42 tried ideas, a result this good would appear by chance with probability X".
- Programme-1 history is **not reset or hidden**. The cumulative count is always shown.
- **What replaces DSR's protective role:**
  - the small search space (2 candidates);
  - the rising margin and the hypothesis budget (§8);
  - the controls;
  - the frozen Holdout;
  - the forward test.

## 3. Periods

**Development: 2010-01-04 → 2021-12-31.** Not untouched: programme 1 learned from 2010–2017 in general terms, and S005's 2018–2021 report showed EW's 2018–2021 statistics. Everything we know is disclosed.

**Holdout: 2022-01-01 → 2026-08-31.** Locked. It is opened once, for one frozen candidate, under written owner approval (`HOLDOUT_UNLOCK.md`). After that it becomes development data for any later research.

**Forward period F1: from 2026-09-01.**

- These dates already partly exist, so they are **locked as well** from today, and never used in development.
- The forward test is run as a single backtest of the frozen strategy over F1 at a pre-set date (e.g. after 12 and 24 months).
- **No daemon or live system is needed.** That keeps within the project's scope rules.

## 4. Evaluation design on 2010–2021

- **Nothing is fitted.** H014's parameters are fixed conventions, so no rolling re-estimation is needed. "Walk-forward" here means a chronological evaluation of fixed rules.
- **Blocks:** 6 two-year blocks (2010–11, 2012–13, 2014–15, 2016–17, 2018–19, 2020–21). The Sharpe difference against EW and the controls is reported per block and per year.
- **Choosing between the two candidates (the only fitted choice):**
  - v1.0 (63-session exit) is the pre-declared **primary**;
  - v1.1 (trend-failure exit) replaces it **only if** it has a higher Sharpe difference against EW in **both** halves, 2010–2015 and 2016–2021.

  This uses half the data to choose and the other half to confirm, and makes cherry-picking the full-period winner impossible.
- **Paired stationary block bootstrap** (mean block 63 days; the method calibrated in C03), with confidence intervals for the Sharpe difference against EW, SPY, C1, C2 and the random controls. Reported, not gated.
- **Pre-declared perturbations** of the chosen candidate (6):
  - RSI pullback threshold 35 / 45;
  - pullback window 3 / 8 sessions;
  - exit horizon 42 / 84 (v1.0) or cap 84 / 168 (v1.1).
- **Cost stress:** 2× slippage (gated); 4× and 6× (reported).
- **Seeds:** the random-uptrend control uses 3 fixed seeds. Every seed is reported, and none is chosen.

## 5. Advancement criteria: opening the Holdout

These are computed on 2010–2021 at $100K for the chosen candidate. **All four gates must pass. Everything else is a diagnostic.**

| Gate | Requirement | Why |
|---|---|---|
| **G1: practical superiority over passive investing** | (a) Sharpe(H) − Sharpe(EW) ≥ **m** (m = +0.20 for H014, the first Phase 2 hypothesis; see §8).<br>(b) Sharpe(H) − Sharpe(SPY) ≥ +0.10.<br>(c) CAGR(H) ≥ CAGR(EW) − 2.0 points a year.<br>(d) max drawdown(H) no deeper than EW's. | Return and risk judged together (§6). It allows slightly lower return with clearly better risk, but not a much lower return, and not a higher return bought with a deeper drawdown. |
| **G2: the hypothesis itself** | Sharpe(H) > Sharpe(C1 trend-only), > Sharpe(C2 no-recovery), and > the median Sharpe of the 3 random-uptrend seeds (point estimates) | If H014 does not beat these, its advantage comes from the trend filter or chance, not the pullback/recovery entry (§7). |
| **G3: consistency, not one lucky period** | Sharpe(H) − Sharpe(EW) > 0 in **at least 4 of the 6** two-year blocks, **and** no single block contributes more than 50% of the cumulative excess return over EW | Replaces the old year-count and year-share items with a measure that suits multi-month holding. |
| **G4: robustness and cost realism** | (a) At least 5 of 6 perturbations keep Sharpe(H) − Sharpe(EW) ≥ +0.10.<br>(b) At 2× slippage, Sharpe(H) − Sharpe(EW) ≥ +0.10.<br>(c) Realised cost drag ≤ 1.5% a year at base costs. | Parameter and cost fragility are the classic technical-analysis failure. |

**Diagnostics (reported, never blocking):**

- DSR at three trial counts (§2), PSR, PBO;
- bootstrap intervals for every comparison;
- trade count, profit factor, expectancy and its concentration (share of profit from the top 5% of trades);
- turnover, market exposure, holding-period distribution;
- per-year and per-block tables;
- stress episodes (2011, 2015–16, 2018 Q4, 2020);
- 4× and 6× costs;
- $200K sensitivity;
- volume at entry.

**Correlation between the gates, and why this keeps a real strategy's chances workable.**

- G1 and G3 are related, but G3 adds timing information. G2 asks a different question. G4 tests fragility.
- The simulation (§8) models G1 alone. The other gates only lower false acceptance further, so the simulated rates are upper bounds.
- A genuinely strong strategy (true +0.5 Sharpe over EW) passes G1 about 90% of the time. The remaining gates target specific failure modes, not noise, so they should rarely reject such a strategy.

## 6. Interpreting the EW and SPY comparisons

**The primary measure is risk-adjusted: the Sharpe difference.** Return and drawdown are guard-rails:

| Situation | Decision under G1 |
|---|---|
| Higher Sharpe (≥ margin), CAGR at most 2 points below EW, drawdown no deeper | **Qualifies.** Better risk-adjusted, with a practical return. |
| Higher Sharpe, but CAGR more than 2 points below EW | **Fails.** Most of the "improvement" is lower exposure, which the owner could get by simply holding less stock. |
| Higher CAGR, but deeper drawdown than EW | **Fails.** Extra return bought with extra risk. |
| Higher Sharpe only against EW, not by +0.10 against SPY | **Fails.** No practical reason to prefer it over the simplest passive choice. |

- **Why Sharpe first.** With cash earning 0%, holding a constant fraction of a strategy cannot raise its Sharpe. So a Sharpe margin is the fairest single measure of skill beyond simply holding less stock.
- **Why also CAGR and drawdown.** You invest money, not Sharpe. The strategy must earn a practical return and must not add risk.
- **SPY and EW** correlate about 0.97, so requiring both costs little extra power. It ensures the strategy beats the simplest real alternative too.

## 7. How the H014 controls decide

| Outcome on 2010–2021 | Meaning | Decision |
|---|---|---|
| H014 beats C1, C2 and random uptrend (G2 passes) | The entry timing adds value | Eligible (if G1, G3 and G4 also pass) |
| H014 ≈ C1 or below it, and C1 beats EW | "Holding uptrend stocks" explains the result; the pullback adds nothing | **H014 fails.** C1 was not a pre-declared candidate, so it **cannot** be promoted after the fact. That would be selection on results. It may become a new, separately registered hypothesis, counted in the hypothesis budget. |
| H014 beats C1 but not C2 | Waiting for recovery adds nothing over buying the dip | **H014 fails** (the recovery claim is refuted) |
| H014 beats random only for some seeds | The selection edge is not robust | **Fails** if it is below the median seed |

## 8. Overfitting control: what replaces the DSR gate

1. **Small search space.** H014 has 2 candidates. The perturbations are robustness checks, never selection. There are no grids.
2. **Parameters frozen before any result:** conventions only (literature review §2), hash-pinned in a specification before the first run.
3. **Hypothesis budget for this Holdout: at most 3 hypotheses** (H014 plus at most two later, separately registered ones) may be screened on 2010–2021 before the 2022–2026 Holdout is used.
   - **The G1 margin rises with each:** +0.20, +0.30, +0.40.

   Simulated false acceptance when no hypothesis has any edge (development G1 only, then Holdout gate +0.10):

   | Scheme | 1 hypothesis | 2 | 3 | 5 | 10 |
   |---|---|---|---|---|---|
   | Fixed +0.20 margin, no budget | 8.3% | — | 19.8% | 26.9% | 34.6% |
   | **Rising margin, budget of 3** | **8.2%** | **11.3%** | **12.1%** | not allowed | not allowed |
   | … plus the 2-year forward test | 4.2% | 5.6% | 6.1% | — | — |

   Probability of accepting a genuine edge (tested first), with the budget:

   | True Sharpe gain | Acceptance |
   |---|---|
   | +0.3 | 53–57% |
   | +0.5 | 84–86% |

4. **Seeds, subperiods and parameters are never chosen after results.** All are reported.
5. **The Holdout is used once.**
   - If the candidate fails, it is recorded, and the Holdout counts as consumed.
   - No revised version is ever tested on it.
   - Everything listed in the owner's request is frozen and hash-pinned before unlocking: entry, exit, ranking, construction, sizing, costs, parameters, benchmarks and criteria.

## 9. Holdout acceptance criteria (pre-declared now; frozen before unlocking)

Computed on 2022-01-01 → 2026-08-31 for the frozen candidate. The following runs are needed: H, EW and SPY benchmark extensions, C1, and one random seed.

- **HO1:** Sharpe(H) − Sharpe(EW) ≥ +0.10, and Sharpe(H) − Sharpe(SPY) ≥ 0.
- **HO2:** CAGR(H) ≥ CAGR(EW) − 3 points a year, and max drawdown no deeper than EW's + 5 points.
- **HO3 (the hindsight guard, §10):** Sharpe(H) − Sharpe(EW) ≥ 0 **both** in 2022 **and** in 2023-01-01 → 2026-08-31.
- **Reported, not gated:** comparisons with C1 and random, DSR, costs, turnover and every diagnostic.

**Outcomes:**

- **Pass:** "provisionally accepted", then the forward test on F1. Only a pass there leads to a separate owner decision about any real-money use, which is outside the research scope.
- **Fail:** recorded, and the Holdout is consumed.

## 10. Concerns I believe materially affect false-positive risk

1. **A single 4.7-year Holdout cannot confirm a modest edge.**
   - Its noise in a Sharpe difference against EW is about ±0.32. A strategy with no edge passes "beat EW" there about 30% of the time.
   - The Holdout reliably catches large overfitting (a big development edge that disappears), not small illusions.
   - **So the Holdout must not carry the whole burden. The development margin and the forward test are essential.**
2. **Treating DSR as diagnostic without a hypothesis budget would let false acceptance grow with each idea screened:** about 27% after 5 and 35% after 10 (table above). The budget plus rising margin is the practical replacement for DSR's protection. **I recommend adopting it.**
3. **The Holdout is not "blind" to us.**
   - It is common knowledge that 2022 was a broad bear market and that 2023–2024 were strong, concentrated rallies.
   - A trend filter is precisely the kind of rule that tends to shine in a 2022-type bear market. Even an innocently chosen trend strategy could pass the Holdout mainly by stepping aside in 2022.
   - **HO3** requires the advantage to hold after 2022 too. That is my proposed guard, and it is pre-declared now, before any result.
4. **2018–2021 is partly known** (EW's 2018–2021 statistics were in the S005 report). It is correctly treated as development, not as a test.
5. **Point-estimate control gates (G2) are weak evidence on their own.** Each has about a 50% chance of passing by luck when there is no real difference. They filter out "right answer for the wrong reason". They do not prove the timing effect. Bootstrap intervals are reported.
6. **The calibration is borrowed.** The correlation of 0.76 comes from programme-1 books; H014 might track EW more closely (less noise) or less closely.

## 11. Long-term data strategy

- **How many hypotheses fit on 2010–2021?**
  - **At most 3 per Holdout use**, with rising margins.
  - Programme 1 already used 12 ideas on 2010–2017. Each further idea on the same data buys less new information and needs a higher bar.
- **When to open 2022–2026?** Only when one candidate has passed G1–G4 and is frozen. It is **not** opened for H014 automatically if H014 fails development.
- **After it is consumed:**
  - 2010–2026 becomes development data;
  - the next genuine test is **forward data** (F1, from 2026-09-01), which grows by about a year each year;
  - there is no second retrospective Holdout.
- **Forward testing:** a frozen strategy re-run over accumulated forward data at pre-set dates (12 and 24 months). It is cheap and reproducible, and needs no live infrastructure.
- **Other independent evidence** (each needs your approval):
  - pre-2010 US data only as a stress test, because the point-in-time universe is imperfect (D035);
  - international equities (a new universe, new data and a scope change; licensing and cost must be checked first);
  - sector or ETF tests (a different universe; a scope change).
- **I do not recommend using any of these as a routine substitute for forward data.**

## 12. Structural check of H014's rules under the revised method

No structural flaw was found in the rules themselves. Two practical risks are disclosed:

1. **Idle cash in bear phases.** The trend filter empties the candidate pool, so there are few signals. That hurts gate G1(c) in a mostly bull 2010–2021 period.
2. **Early Close < MA200 exits shorten holds.** Cost gate G4(c) checks for this.

The exit rule Close < MA50 remains excluded, because it would conflict with the pullback entry (proposal §6).

## 13. Run count and cost (replaces proposal §15)

| Class | Runs | Notes |
|---|---|---|
| Canaries | 2 | Operational |
| Candidates, 2010–2021 | 2 | |
| Controls | 10 | C1, C2 and random × 3, for each exit |
| $200K sensitivity | 2 | |
| **Committed total** | **14 research + 2 canaries** | |
| Conditional: perturbations | 6 | |
| Conditional: cost stress | 3 | 2×, 4×, 6× |
| Conditional: Holdout | ≤ 5 | H, C1, 1 random seed, EW and SPY extensions; only if G1–G4 pass and you approve |
| Later: forward test | 2–3 | |
| **Maximum** | **≤ 28 research runs** | Plus canaries |

- 12-year runs take about 10–14 minutes each: about 3 hours committed, about 6 hours in all.
- Cost: the existing $24 a month for 1–2 months.

## 14. Decisions requested

1. Adopt the principle: 2010–2021 is development, the Holdout is used once for one frozen candidate, and DSR is a reported warning.
2. **Gates G1–G4** (§5), with the margin m = +0.20 for H014.
3. **Hypothesis budget: at most 3 per Holdout use, with rising margins** (recommended to replace DSR's protection; §8, concern 2).
4. **Holdout criteria HO1–HO3**, including the post-2022 guard HO3 (§9, concern 3).
5. **Forward period F1 locked from 2026-09-01**, with a 12–24-month forward test before any real-money decision.
6. The candidate choice rule (v1.0 primary; v1.1 only if better in both halves).
7. A CLAUDE.md update for Phase 2: the holding horizon, the development and Holdout definitions, and DSR as a diagnostic.

After approval I will:

1. write the frozen, hash-pinned Phase 2 specification;
2. implement S014 and its controls, with tests and canaries;
3. run the committed 2010–2021 runs;
4. stop at the development checkpoint. **The Holdout stays locked until you approve it separately.**
