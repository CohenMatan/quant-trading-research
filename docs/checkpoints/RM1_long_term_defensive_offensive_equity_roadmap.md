# Long-Term Defensive and Offensive Equity Research Roadmap — 30-Year Objective

**Owner decision D240, 2026-10-18. DESIGN ONLY.**

> **Update (D241, 2026-10-18):** extended by `docs/checkpoints/RM2_h028_defensive_reference_offensive_companion_design.md` (H028 as a descriptive defensive reference + an offensive companion; staged roadmap A–H). The owner did not choose one of the section-22 options below; RM2 section 25 states the next decision. Nothing below is withdrawn.
- Nothing here is approved for execution.
- No hypothesis, backtest, null, synthetic run, data purchase or Holdout access is implied.

**Labels:**
- **[V]** = verified record, with its source;
- **[I]** = my interpretation;
- **[P]** = a proposal needing owner approval.

## 1. Programme objective

- **Goal:** an autonomous, long-only system of US common stocks that compounds more terminal wealth than SPY buy-and-hold with distributions reinvested, over about 30 years.
- **Conditions:** after realistic costs, without leverage, with acceptable risk.
- **Baseline universe:** NYSE/Nasdaq common stocks, market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M.
- **Mechanics:**
  - point-in-time data only;
  - correct delistings and corporate actions;
  - next-open execution;
  - $7 per order plus 10 bps slippage per side;
  - $100,000 research capital;
  - identical dates and capital versus SPY.

**Primary statistic (prospective):** S = ln(W_strategy / W_SPY).

**Annual win rate** is a diagnostic, never a universal gate. Historical gates of H026–H028 are not relaxed.

## 2. Current verified status [V]

| Item | Status | Source |
|---|---|---|
| Research cycle | Completed, No Production Candidate Found | D240 |
| Phases 13 and 14 | CLOSED | `docs/checkpoints/RC1_research_cycle_closure_phases_13_14.md` |
| H028 | REJECTED; its null evidence unreliable | D238 |
| H028 repaired-null attempt | B — METHOD NOT VALIDATED | D239 |
| H029 / H030 | NOT EVALUABLE | — |
| Active experiment | None | — |
| Holdout 2022-01-01 → 2026-08-31 | Sealed, never accessed | — |
| Hypothesis statuses | H001–H030 | `research/hypotheses/STATUS.md` |

## 3. Findings from H001–H030

**Technical and price-based selection** [V]:
- 13 hypotheses failed: reversal, momentum, 52-week high, pullbacks, breakouts, squeeze, residual momentum, volume, gaps, seasonality, trend/pullback, a 1,533-configuration technical search, and three cross-sectional signals (H001–H004, H006–H011, H014, H018, H019).
- A deterministic chart score (H020) failed.
- Sector rotation (H021-A) failed.

**Low volatility:**
- H005 (S005) passed in-sample and **failed Validation 2018–2021** (D060).

**Fundamental selection** [V]:
- Failed: GP/A (H016); a hand-designed technical + fundamental + sector score (H022); its reweighting (H023); 11-feature redesign (H024).
- Event signals failed: earnings-event continuation from 8-K price reactions (H017) and insider cluster buying (H025).

**Learned scores** [V]:
- H026–H028 produced development wealth above SPY (1.19–1.25×) with lower beta and drawdown.
- All three failed their own gates: D1/D3, A4, B4.
- Their advantage came almost entirely from SPY-down months, above all 2018 and March 2020 (P11-CP2, P13-CP4).
- With 2018 and 2020 removed, only 9.3% of bootstrap paths beat SPY (P13-CP3).

**Business improvement:**
- H029 / H030 were never evaluated on returns: the nulls were inadequate.

## 4. What the negative results establish [I]

- **Within this framework none of the tested signals qualified.** The framework:
  - stocks ≥ $2B, 2010/2011–2021 data, monthly or slower decisions;
  - pre-registered gates with α ≈ 1%;
  - mostly Top-10 to Top-20 books.
- **Several real statistics were far below their thresholds**, so threshold choice is not what failed them:
  - H022 t_IC 0.48 vs 2.38;
  - H024 2.48 vs 4.37;
  - H019 F 1.31 vs 2.87;
  - H025 t −0.93.
- **"Best-of-search" results beat SPY even in no-edge worlds** (median +6.8%/yr; D139). Historical outperformance alone is not evidence.

## 5. What they do NOT establish [I]

- **No small edge has been ruled out.** Power was limited: the 50%-detectable edge was typically 4–15%/yr (P2-CP10, P4-CP3R, P7-CP4), against plausible edges of 0–3%/yr. A real but modest edge would usually go undetected.
- **Not that factor premia are absent.** Low volatility, profitability and value were tested only in specific constructions over one decade.
- **Not that technical analysis "never works"** (D139 wording).
- **Not that H029's business-improvement idea is wrong.** It was never tested.

## 6. The role and limits of H028 [I]

**Use:** a *descriptive* defensive-style observation.

**Not evidence of:**
- stock-specific alpha. Committed factor regressions give LOWVOL-factor alpha t 1.26 (`P13_CP1_result.json`). In null comparisons its distinguishing feature was **upside** participation (up-capture 0.97 vs null median 0.71), plausibly a growth/profitability tilt (D238, D239);
- persistence: the advantage is concentrated in already-observed episodes.

**Rules:** never a production component; never a source of weights or regime rules.

## 7. Transparent defensive benchmarks (candidates, to be frozen before any use) [P]

| ID | Benchmark | Properties | Data |
|---|---|---|---|
| DB1 | SPY buy-and-hold | Primary benchmark | QuantConnect, 1998+ |
| DB2 | LV15 (frozen H027 definition: 15 lowest-volatility stocks, sector cap 3, same costs) | Strong downside protection, but beta 0.53, up-capture 0.62 and CAGR 11.9% vs SPY 14.8% over 2015–2021 (seen data): **large opportunity cost** | Data v2.1 (2011–2021) |
| DB3 | Investable low-volatility ETF buy-and-hold (USMV or SPLV) | Simplest real-world defensive equity holding | Prices only; inception about 2011 (dates to verify) |
| DB4 | Fixed 50/50 SPY + DB3, annual rebalance | Weights chosen **ex ante, not optimised**; the natural "simple combined" benchmark | As DB3 |
| DB5 | Beta-target mix of SPY + DB3, with the target beta fixed in advance (e.g. 0.8 as a round number, never H028's realised 0.76) | Separates beta from selection | As DB3 |
| DB6 | Quality ETF (e.g. QUAL), or quality + low-vol | Profitability/quality exposure benchmark | About 2013 (to verify) |

**Rules:**
- A defensive candidate must beat **both** SPY on S **and** the most similar of DB2–DB6 on S at comparable beta.
- It must state its expected opportunity cost in sustained bull markets in advance.
- Lower drawdown is a safeguard, not an objective.

## 8. Distinct offensive research families (at most four) [P]

| | OF-A Fundamental surprise and acceleration | OF-B Capital allocation: net issuance / buybacks | OF-C Profitability-trend / business improvement (new design, not H029) | OF-D Analyst estimate revisions |
|---|---|---|---|---|
| Economic hypothesis | Prices under-react to changes in reported fundamentals: same-quarter YoY earnings or revenue surprise and its acceleration | Firms issue when overvalued and repurchase when undervalued | Firms whose margins, returns and asset efficiency improve persistently are under-priced | Slow diffusion of analysts' information |
| Evidence (committed refs) | Foster-type SUE, Ball & Brown 1968, Bernard & Thomas 1989/90; weaker in large caps after the 2000s (Chordia et al. 2009; Martineau 2021): P2-CP3 table D | Ikenberry et al. 1995; Loughran & Ritter 1995; Daniel & Titman 2006; Pontiff & Woodgate 2008; Fama & French 2008 (P2-CP3 B, P2-CP10 §6) | Piotroski 2000; Novy-Marx 2013; QMJ (P2-CP3 A); H029 concept (P14-CP1) | Womack 1996; Chan, Jegadeesh & Lakonishok 1996 (P2-CP3 E) |
| Relation to earlier work | H017 used the **price reaction**, not the accounting surprise; H022 used revenue-growth *levels*; H029 F1/F5 related but never evaluated | AG / ACC inside H024 (model-level fail); H029 F7 (never evaluated) | H029 (blocked); GP/A *levels* (H016) failed. Trend ≠ level | None |
| Raw data | SEC XBRL quarterly revenue / NI (Data v3 guard); 8-K timing (Event Data v1) | SEC cover-page share counts (Data v3 F7; split test passed) | Data v3 revenue / GP / OCF / NI / total assets | Point-in-time consensus estimates |
| PIT availability, no purchase | **Yes**, 2011–2021 (XBRL era); about 76–82% of the eligible universe (P14-CP1) | **Yes**, 2011–2021 | **Yes**, 2011–2021 | **No:** EODHD / Estimize paid, PIT unverified (P2-CP11) |
| Historical depth | About 11 years (pre-2009 XBRL absent) | About 11 years | About 11 years | 1998+ only with purchase |
| Turnover / costs | Quarterly events; moderate | Annual; low | Quarterly; low–moderate | Monthly; moderate |
| Main exposures | Growth, momentum, quality | Size, value, quality | Quality, growth | Momentum, growth |
| Main risks | Weak in large caps; restatements (guard v3); filing timing | Mostly a short-leg effect; long-only edge small (0–2%) | Overlap with profitability / growth factors; the H029 null problems | Data cost; PIT reliability; survivorship of coverage |
| Evaluation method (§15) | Universe-wide cross-sectional test with stock-level controls; no identity pairing; synthetically calibrated | Same | Same | Same (after a data audit) |
| Evidence type | Development (2011–2021 seen); independent only on the Holdout or purchased pre-2010 data | Same | Same | Possibly independent pre-2010, but needs a purchase (blocked by D124) |

**No family is presented as new if it is a repackaging.** Plain momentum, the 52-week high, low volatility and profitability *levels* are exhausted for this universe and period.

None of the four is known to raise *up-market capture* specifically. "Offensive" here means selection with a tolerance for higher beta, not leverage.

## 9. Point-in-time historical-data availability [V / I]

| Dimension | 1998–2009 | 2010–2021 | Holdout 2022-01-01 → 2026-08-31 | Forward (after a freeze) |
|---|---|---|---|---|
| 1. Data exists | Prices / corporate actions / SPY yes, from 1998 (AlgoSeek); Morningstar market cap absent before Oct 2009; no fundamentals for firms that died before 2009; SEC XBRL absent (text filings only); 8-K timestamps from about 2003–04 (P2-CP11) | Yes | In QuantConnect; **not inspected**. Data v2.1 / v3 end 2021-12-31, so an extension would be needed (built without looking at returns) | Accrues in real time |
| 2. Historically accurate | Prices yes; corporate actions audited only for 2010+ | Audited (Data v1–v3; PIT audits 0) | Unknown until audited (blind) | Yes |
| 3. Point-in-time usable | Prices yes; universe and fundamentals **no** without new data | Yes | After a blind extension, yes | Yes |
| 4. Free of material survivorship bias | **No:** a ≥ $2B universe cannot be rebuilt without Sharadar-type data | Small residual (0.5–1.2%/yr, D113) plus the Gate K identity residual (D192) | To be verified | Yes |
| 5. Already influenced decisions | Not used for stock selection: only infrastructure / benchmark runs E900, E950–E953 and Phase-6 sector ETFs 2000–2017 (`INDEX.csv`). **Macro history is public knowledge** (2000–02, 2008), so design hindsight is a risk | **Heavily** (H001–H030) | Never accessed | No |
| 6. Can give independent confirmation | Potentially, for hypotheses designed without reference to it, **only after purchase and audit** | **No:** development only | **Yes**, single-use, about 4.7 years (low power) | **Yes**, slow |

## 10. Pre-2010 feasibility [V / I]

- **Without a purchase:** a stock-level ≥ $2B point-in-time backtest before 2010 is **not feasible**. Market cap and dead-firm fundamentals are missing.
- **With Sharadar-type data** (about $69/month; total about $93 against the $200 ceiling; P2-CP12):
  - point-in-time market cap and share counts from 1998;
  - about 9,000 delisted firms;
  - as-reported fundamentals.
  - **Licence terms for use inside QuantConnect are unverified**, and a full audit would be needed.
- **D124 constraint:** D124 forbids purchases "until a strategy shows a promising result on existing data". Any pre-2010 path needs that rule revisited first.
- **Ceiling on history:** a true 30-year backtest is **impossible**. At most about 24 years (1998–2021), plus the Holdout. Shorter results must never be extrapolated into a "30-year test".

## 11. Unseen versus already-examined periods [V]

| Period | Status for stock selection |
|---|---|
| 2010–2021 | Examined (development only) |
| 2018–2021 | Development since H026 (D206); used once as H005 Validation |
| 2022-01-01 → 2026-08-31 | Unseen; single-use Holdout |
| 2026-09-01 → freeze | Locked unseen (D094) |
| 1998–2009 | Unseen for stock selection, but unusable without new data |

## 12. Long-horizon evaluation framework [P]

**Primary:** S = ln(W/W_SPY). Same dates and capital; costs included; no leverage.

**Statistical evidence:** g ≥ 2.15 × max(iid, block-bootstrap) SE of the annualised log excess (the Amendment 3 W2 form), with the threshold pre-registered.

**Power reality [I]**, arithmetic at H028's tracking error of about 10%/yr:

| Years of data | SE of annualised excess | 2.15 × SE |
|---|---|---|
| 11 | 3.0%/yr | 6.5%/yr |
| 24 | 2.0%/yr | 4.4%/yr |
| 30 | 1.8%/yr | 3.9%/yr |

**No available history can statistically confirm a modest edge.** Evidence must combine:
- prior economic and literature support;
- signal-level breadth (all stocks, not a Top-15);
- consistency across independent periods;
- forward accumulation.

**Diagnostics (all reported, thresholds fixed per pre-registration):**
- CAGR and excess CAGR;
- max drawdown, time underwater, recovery duration;
- relative drawdown versus SPY: depth and duration;
- rolling 3-, 5- and 10-year relative returns (15–20-year windows where history allows);
- up- and down-capture; volatility; beta;
- sector / style concentration;
- turnover and costs, including a 2× cost stress;
- regime split.

**Fragility versus tolerable underperformance:** a strategy is **fragile** if any of these holds:
- S ≤ 0 after removing its top k contributing months (k pre-set, e.g. 6), or its single best calendar year;
- one episode supplies more than a pre-set share of S (the H017 / H028 pattern: 74% in 2014–15; 49% in March 2020);
- fewer than a pre-set share of rolling 5-year windows are ahead;
- the relative drawdown or its duration exceeds a pre-set investor tolerance (e.g. 15 years behind would be untenable even with positive S).

Intermittent lagging that leaves positive S in leave-episode-out tests and is spread across regimes is tolerable.

## 13. Risk and drawdown requirements to consider [P]

- MaxDD ≤ 1.25 × SPY's and volatility ≤ 1.25 × SPY's (the H026-style safeguard).
- Beta reported but not constrained.
- A pre-registered relative-drawdown tolerance.
- A sector cap of 3 per FF12 for Top-15-type books.
- No leverage; cash allowed.

## 14. Benchmarks per portfolio type [P]

| Portfolio | Must beat on S | Also compare against |
|---|---|---|
| Defensive | SPY and the closest of DB2–DB6 at comparable beta | — |
| Offensive | SPY and an equal-weight eligible-universe benchmark | A style ETF matching its main exposure |
| Combined | SPY **and DB4** (fixed SPY + defensive-ETF mix) | — |

**Combined portfolio requirements:**
- It must also show it adds value over the simpler DB4 alternative.
- Weights are fixed ex ante, or set by an independently justified rule. **No 50/50 assumption; no weights estimated from H028's path; no 2018 / 2020 regime switch.**
- It is evaluated as **one** investable system: netted overlapping holdings, total sector and position limits, combined turnover and costs, portfolio beta, joint drawdowns, bull- and bear-market relative behaviour.
- **Independent evidence for each component is a precondition.** Complexity must earn its place against DB4.

## 15. Statistical evaluation validity requirements [P], from D238 / P13-CP6

1. **The null must test the stated hypothesis.** Do not reuse a familiar null.
2. **No persistent identity-pairing nulls in a churning universe.** Pair re-formation adds rank changes, turnover and cost (D235, D238).
3. **Conditional questions need conditional inference.** Marginal permutation is invalid when the tested features correlate with controlled exposures (D238).
4. **Concentrated Top-N portfolios cannot be exposure-matched** (D239). The statistical test should be **signal-level across the eligible universe**:
   - e.g. cross-sectional regressions of forward returns on the signal with stock-level controls (sector, size, LOWVOL, BM, PROF, MOM, past beta);
   - Fama–MacBeth with Newey–West or block-bootstrap standard errors.
   - Portfolio backtests then become economic evidence, not the significance test.
5. **Time-series factor regressions on factor portfolios are not sufficient controls** (R3: 14% false rejections at nominal 1%; D239).
6. **Repeated use of 2011–2021** makes every new result development evidence, labelled post-hoc where it is.

## 16. Synthetic-validation requirements [P]

Before any real-data inference, the method passes a frozen synthetic suite. The offline generator `qresearch.r1synth` already models churn, priced and time-varying factors, persistence, delistings and sector moves.

**The suite:**
- no-edge and priced-factor-only scenarios;
- planted-signal power at three strengths;
- churn at 0×, 1× and 2×;
- composition drift and thin coverage;
- cost levels.

**Criteria fixed in advance:**
- rejection ≤ 0.02 at α = 0.01;
- 0.035–0.065 at α = 0.05;
- a p-value distortion bound;
- power ≥ 0.80 at a pre-declared economically meaningful effect.

**Fail rule:** if the suite fails, the hypothesis is not run.

## 17. Computational and QuantConnect limits [V]

- B2-8 node with an 8 GB memory limit; learned-score hosts peak at 7.6–8.2 GB.
- 50 files per project; 64,000 characters per file.
- Compliance review rejects code that exports data for probing or validation.
- Engine pinning is blocked below the Trading Firm tier; the default build changes.
- Daily log quota; ObjectStore export blocked.
- **Offline synthetic work in this container is unconstrained** (one 475-stock panel plus 1,000 twin worlds takes about 1.1 s and 46 MB).

## 18. Data costs [V]

| Item | Monthly cost | Notes |
|---|---|---|
| Current QuantConnect (Researcher seat + B2-8 node) | $24 | — |
| Sharadar | about +$69 | — |
| EODHD (estimates, PIT unverified) | about +$31 more | Total about $124 |
| I/B/E/S | Institutional only | — |
| Ceiling | $200 | Target $100 |
| Trading Firm tier (engine pinning) | about $480 | Over the ceiling |

## 19. Multiple-testing governance [P]

- **Ledger:** one ledger of every hypothesis, variant and selection decision. About 25 hypotheses with real results so far; `INDEX.csv` has 413 experiment IDs.
- **Budget:** a new programme gets a fixed hypothesis budget (e.g. at most 3) with family-wise control (Holm) across them.
- **Holdout:** reserved for at most one frozen candidate.
- **Post-hoc ideas** are labelled as such and need independent data.
- **Proposed checkpoint sequence**, each step needing owner approval, with no auto-advance:
  1. economic hypothesis and independent justification;
  2. point-in-time data feasibility and integrity audit;
  3. synthetic validity study of the evaluation method;
  4. frozen portfolio and model specification;
  5. frozen costs and risk requirements;
  6. frozen success criteria;
  7. development experiment;
  8. development decision and audit;
  9. independent confirmation (Holdout or other unseen data), separately approved;
  10. prospective paper trading (periodic manual runs; no daemon or scheduler, per scope) before any production use.

## 20. Recommended next research direction [P]

**Preferred: OF-A — fundamental surprise and acceleration, signal-first.**
- Accounting earnings and revenue surprise plus acceleration, from SEC data already in Data v3 and Event Data v1.
- Tested first as a **universe-wide cross-sectional signal**, with inference validated synthetically before any real data.
- **Its first checkpoint is a synthetic-only validity study of the inference method itself**: cross-sectional Fama–MacBeth with stock-level controls and HAC / block-bootstrap errors, on the existing `r1synth` generator.
  - It must show calibration in exactly the case that broke R3: priced growth and profitability.
  - It must show power against a planted signal.
  - **If it fails, the programme stops before touching any data.**

**Credible alternative: data-horizon feasibility.**
- A desk-only review (no purchase) of whether a 1998–2009 ≥ $2B point-in-time panel (e.g. Sharadar) can be licensed, imported and audited within QuantConnect's limits and the budget.
- It would double the independent history and add two bear markets, which matters most for any defensive or 30-year claim.
- **It requires revisiting D124** before any purchase.

**Stopping** remains a defensible outcome.

**Prerequisites:**
- **For OF-A:** a non-return coverage and timing audit on Data v3 (already largely covered by P14-CP1 / CP2); a later blind Data v3 extension beyond 2021 if a candidate ever reaches the Holdout.
- **For the alternative:** owner revision of D124, plus licence verification.

## 21. Main reasons for the recommendation [I]

- **It tests information this programme has never evaluated against returns.** The accounting surprise was not tested (H017 used prices); H029 was never evaluated. It is grounded in pre-2010 published evidence, **not** in H026–H028's 2018 / 2020 path or their defensive tilt.
- **It attacks the method failure first.** The repeated failures were in inference (D235, D238, D239). A cheap synthetic study decides whether a valid test exists before any data is touched.
- **Signal-level testing uses the whole cross-section.** That gives more power than a Top-15 book, and it avoids the matching infeasibility that sank R1.
- **It needs no purchase**, so it respects D124.
- **Honest expectation:** large-cap evidence for this family is weaker after the 2000s, and plausible edges are below the detection power. The most likely result is "not qualified", but it would be a clean answer.

## 22. Required next owner decision

Choose one:
1. **Approve the smallest next checkpoint:** OF-A inference validity study, synthetic only (offline, no real data, no QuantConnect), with acceptance criteria frozen before running. Its output is a design pass or fail.
2. **Approve the alternative instead:** a desk-only pre-2010 data feasibility review (no purchase), and decide whether D124 may be revisited later.
3. **Stop the research programme.**

**Nothing begins without that decision.** The Holdout stays sealed.

---

**Update (D246, 2026-10-18): research priority changed to an offensive complement for H028.** Candidate selection and test design: `docs/checkpoints/OC_CP1_h028_offensive_complement_candidate_selection_test_design.md`.
- **Preferred complement:** SPY (market-exposure completion).
- **Stock-selection offensive search on existing data:** recommended to STOP. Momentum and quality-growth families are exhausted; fundamental improvement (OC-B) is a conditional backup only.
- **Proposed single test:** SYS-1, an account-level 2015–2021 system test against beta-matched and transparent controls. It is not run and is awaiting owner approval.
- **Not superseded:** the OF-A path (Stages A–H) stays as recorded. Its next step remains subject to D245 / LH-CP4.

**Update (D247, 2026-10-18): candidate discovery before SYS-1.** `docs/checkpoints/OC_CP2_independent_offensive_stock_selection_candidate_review.md`.
- **Correction to OC-CP1:** business improvement was set aside on an imported 2015–2021 window; Data v3 signals need no fiscal labels, so the PIT-safe window is 2012-02 → 2021-11.
- **Proposed:** OC-2 (ΔROA, Data v3 F5) as the single earnings-improvement signal test, replacing OF-A's surprise definitions if approved; Stage B-OC2 synthetic calibration first.
- **Unchanged:** SYS-1 (not run), the D245 exception for OF-A, every formal status, the Holdout seal.

**Update (D248, 2026-10-18): OC-2 integrity and calibration.** `docs/checkpoints/OC_CP3_oc2_stage1_data_integrity.md` (Stage 1 PASS) and `docs/checkpoints/OC_CP4_oc2_stage2_synthetic_calibration.md` (Stage 2 D — INSUFFICIENT EVIDENCE; the method as specified is not validated).
- **Lesson for any signal-level test:** with several priced characteristics correlated with the signal, rank-linear controls and noisy controls bias the Fama–MacBeth slope upwards. A valid design needs flexible controls and an explicit leakage tolerance.
- **Lesson for synthetic calibration:** synthetic power is only credible if the generated payoff dependence reaches realistic IC volatility.
