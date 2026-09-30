# Research Cycle 3 (C03): final proposed plan

| Field | Value |
|---|---|
| Date | 2026-09-30 |
| Status | **PROPOSAL. STOP: awaiting owner approval.** No C03 strategy backtest has run. No Validation, Walk-Forward or Holdout data is used. |
| Builds on | `CP3d_structural_review_and_C03_proposal.md` (review and diagnostics) plus the owner's clarifications of 2026-09-30 |
| Hypotheses | `research/hypotheses/H012.md` (volatility-managed exposure) and `H013.md` (lottery-stock avoidance). The turn-of-the-month idea (H014) is **deferred, not rejected**. |
| New analysis | `research/cycles/C03_pbo_analysis.py` → `C03_pbo_analysis.json`: PBO behaviour with 6 candidates (synthetic, plus the real C02 returns and synthetic C03 columns). No C03 data. |

## 1. What is fixed now, before any C03 result

- **Everything in this document, once approved:**
  - hypotheses, variations and parameters;
  - controls, seeds and pairing;
  - capital scenarios;
  - screen and robustness rules;
  - the DSR count and PBO rule;
  - the budget.
- **Unchanged:** the D036 screen (including Sharpe ≥ EW + 0.10 and the 2× slippage item), the robustness criteria, costs ($7 per order, 10 bps), the universe (≥ $2B US common), and IS 2010-01-04 → 2017-12-29.
- **C03 design constraints** from the diagnostics (D080), applied to both hypotheses:
  - low turnover: hold 60 sessions, or a slowly rebalanced basket;
  - 15 positions at $100K;
  - expected costs below about 1.5% a year.

## 2. Starting capital: $100K primary, $200K sensitivity (owner item 1)

- **$100K is the primary account.** All selection, screening, robustness and statistics use $100K results only.
- **$200K is a pre-declared sensitivity check.** Its results never select a variation, never change a parameter and never replace a $100K result.
- **Two separate comparisons at $200K, never mixed:**

| Comparison | What changes | What stays identical | Purpose |
|---|---|---|---|
| **S1: pure capital effect** | cash $100K → $200K | signals, parameters, positions (15), seeds, dates, costs | The effect of capital alone: commission share, idle cash, CAGR, Sharpe, drawdown |
| **S2: construction at $200K** (documented separately) | positions 15 → 20 at $200K | signals, parameters, seeds, dates, costs, capital | Whether the extra capital is better used for more positions. With about $9.8K per position, the $5K minimum does not bind. |

- **Why 20 for S2:** it is the most positions that keep each position at about $9.8K, the size at which our cost analysis was calibrated. The diagnostics showed more names buy little diversification at our costs (R5). One construction variant only; no search.
- **Runs:**
  - S1 and S2 for the base variation (v1.0) of each hypothesis and its controls: always.
  - S1 for any other variation that passes the $100K screen: conditional.
- **Reported metrics:**
  - commission as % of position and % of equity a year;
  - positions held;
  - exposure and idle cash;
  - CAGR, Sharpe, max drawdown;
  - correlation with EW and idiosyncratic volatility;
  - the matched no-skill null at the same capital.
- **Statistical treatment:** kind `sizing` (D044, `account_size_test_of`). They are **not selection trials** and not in N or PBO; they are counted in their own category. *Why:* they apply fixed, already-chosen rules to more money, so they create no new selection opportunity.

## 3. H012: volatility-managed exposure (owner item 2)

Full definition: `research/hypotheses/H012.md`.

- **Indicator:** SPY realised volatility RV(n) = standard deviation of SPY's last n daily returns × √252, from adjusted closes up to and including the decision close. **SPY is never traded.**
- **Traded basket:** the 15 largest eligible stocks by **point-in-time** market cap, reconstituted quarterly (first session of January, April, July and October).
  - **Why this basket:** the literature scales the *market* portfolio. Within our stock-only universe and the 15-position limit:
    - the largest names track the cap-weighted market most closely;
    - they have the lowest trading costs;
    - they change rarely, so turnover is low;
    - the choice is deterministic, with no seed luck.
  - **Point in time:** the ranking uses the same Morningstar MarketCap value the universe filter uses on day T. A new infrastructure test and canary verify that each reconstitution's ranking equals the market caps known at that close.
  - **Limitation:** mega-cap and sector concentration. The basket's correlation with SPY is reported.
- **Exposure rule:** e = min(1, RV(252)/RV(s)), set at month-end (v1.2: week-end); applied at the next open if it moves by more than 0.10; no leverage.
- **Variations:**
  - v1.0: s = 21, monthly;
  - v1.1: s = 63, monthly;
  - v1.2: s = 21, weekly.

**Separating timing from holding cash:**

- **Key fact:** Sharpe is computed with a 0% cash return, so holding a *constant* share in cash cannot change Sharpe. A Sharpe gain can come only from *when* exposure is high or low.
- **Control A (fully invested):** the same basket and reconstitution, e = 1 always. H012 − Control A (Sharpe) is the total timing value, before and after costs.
- **Control B (causal, exposure-matched):**
  - The same basket. At each rescale date, e_B = the mean of the variation's own targets over the **previous 12** rescale dates.
  - It holds about the same average exposure and pays similar rescaling costs, but does not respond to the *current* volatility regime.
  - It uses only information available at that date, so there is **no look-ahead**.
  - One per variation.
- **Descriptive ex-post control:** Control A scaled to the variation's realised mean exposure, a constant known only afterwards. It is used only to compare drawdown and CAGR at equal average exposure, and is labelled as ex post.
- **Reported for each variation and control:** Sharpe, CAGR, max drawdown, mean and range of exposure, idle cash, commission, slippage and turnover.
- **Interpretation rules (pre-declared):**
  - timing value requires a Sharpe gain > 0.05 over **both** controls;
  - **lower drawdown alone is never accepted as evidence of timing.** It counts only if drawdown is lower than Control B's with mean exposure within ±0.05.
- **Candidate status:** H012 variations are judged by the unchanged screen against EW. The controls are reported and are **not** selection candidates.
- **Limitation (stated in advance):** IS 2010–2017 has few high-volatility episodes, so the test has limited power.

## 4. H013: lottery-stock avoidance (owner item 3)

Full definition: `research/hypotheses/H013.md`.

- **Justification (independent of H005):**
  - Barberis & Huang (2008), Kumar (2009), Boyer, Mitton & Vorkink (2010), Bali, Cakici & Whitelaw (2011).
  - The MAX effect survives controls for idiosyncratic volatility.
  - H013 only **excludes** the top tail of recent one-day jumps; it never selects quiet stocks.
- **Controlled comparison with random portfolios.** H013 and its paired null share:
  - capital ($100K);
  - positions (15) and holding period (60 sessions);
  - execution (next open, D051), commission and slippage;
  - dates (IS);
  - seeds (1, 2, 3).
  - The null is X962, already run as E962-22..24 with these exact settings.
- **How the pairing works when H013 excludes stocks the null may buy:**
  1. Both draw the **same** random order of the **full** eligible set for each (seed, session): `pick_order(all eligible ids, seed, session)`.
  2. The null fills its free slots from the top of that order.
  3. H013 walks the **same** order and **skips** excluded names. Whenever the null's pick is allowed, H013 makes the same pick; when it is excluded, H013 takes the next allowed name in the same order.
  4. After the first difference, holdings and exit dates diverge, so later free slots differ too. That is unavoidable, and the **trade overlap** with the null is reported per seed.
- **Per-seed reporting:** every result (Sharpe, CAGR, drawdown, costs, trades, overlap, difference versus its own null seed) is shown for seeds 1, 2 and 3 separately, plus the mean.
- **Pre-declared rules kept:**
  - a variation passes only if **all three seeds** pass the screen;
  - no filters, thresholds or exclusion levels change after results;
  - stocks with fewer than 21 returns are never excluded.
- **Variations:**
  - v1.0: exclude the top 20% by MAX(21);
  - v1.1: exclude the top 10%;
  - v1.2: exclude the top 20% by MAX5.

## 5. PBO and Deflated Sharpe (owner item 4)

### 5.1 PBO with six C03 candidates: findings (synthetic, before any C03 result)

- C03 has 6 selection candidates in **2 groups of 3** highly correlated variations.
- Simulations (200 repetitions each; the frozen D073 rule: CSCV, 16 blocks, at-or-below-median counts as overfit, gate ≤ 0.30):

| True situation | 6-candidate PBO: mean | Share passing ≤ 0.30 | For comparison: C02's 18 candidates, null |
|---|---|---|---|
| No candidate better than any other (null) | 0.52 | **27%** (false pass) | 17% |
| One hypothesis better by 0.5 Sharpe | 0.27 | 65% | — |
| One hypothesis better by 1.0 Sharpe | 0.06 | 96% | — |
| **Both hypotheses genuinely good (1.0 and 1.0)** | 0.53 | **22%** | — |
| One variation better within a group | 0.23 | 69% | — |

- **Semi-real check** (18 real C02 return series plus synthetic C03 columns): the six-only PBO behaves the same way. Null: 29% false pass; both hypotheses good: 19% pass.

**Findings:**

1. **Weaker protection.** Under the null, the 6-candidate gate falsely passes 27% of the time, against 17% with C02's 18.
2. **It becomes a two-way contest.** With two tight groups, PBO largely measures *which hypothesis wins in each half*, the same "sibling dominance" pathology D073 removed for 3-variation PBO. **Two genuinely good hypotheses usually fail it (only 22% pass).**
3. **Pooling with C02 is not a fix.**
   - Adding C02's 18 real candidates (same harness, dates and costs) makes the gate pass in **79%** of null cases in the semi-real test, because C02's own dispersion decides the in-sample winner.
   - Pooling would mostly measure C02, not C03, and would be far too lenient.
4. **The actual selection procedure is per hypothesis.** Each hypothesis's best passing variation goes forward on its own; the two hypotheses do not compete for one slot. No PBO construction over 6 correlated columns mirrors that well.

**Genuine statistical evidence versus small-sample limitation.** With 6 candidates in 2 groups, the CSCV statistic has too little resolution to separate a real edge from luck. Its pass/fail outcome is dominated by how the two hypotheses compare with each other. That is a limitation of the small candidate set, not evidence about either hypothesis.

### 5.2 Proposal (owner decision; no threshold is loosened)

- **Option P1 (recommended):**
  - Keep the frozen D073 rule unchanged: cycle-level PBO ≤ 0.30 over the C03 selection set (6 columns; H013 as seed-averaged series).
  - **Add one stricter requirement:** DSR ≥ 0.90 must hold at **both** the official N **and** the conservative count (selection + robustness + Validation + C03 seed replicates).
  - Pre-declared contingency: if a candidate passes every other gate and fails only the PBO, and the failure is because *both* hypotheses perform alike (the pathology above), the result is reported as such and **the owner decides**. It is not waived automatically.
- **Option P2:** keep D073 exactly as it is, with its known limitations disclosed.
- **Rejected:** pooling C02 and C03 (too lenient); dropping PBO (loosens the standard).

### 5.3 Trial counting (D069), before C03

| Category | Treatment | Why |
|---|---|---|
| **Selection candidates** (H012 v1.0–1.2; H013 v1.0–1.2) | **Counted in DSR N: 37 → 43** | The configurations compared to choose a winner |
| H013 seeds 2 and 3 of each variation | Replicates: counted once in N; counted in the conservative count | Each variation must pass on all seeds; no seed is chosen |
| Robustness runs (conditional) | Conservative count only | They can only reject an already-chosen variation |
| Capital sensitivity (S1/S2, kind `sizing`) | Neither; own category | Fixed rules applied to other capital; no selection |
| Controls (H012 A and B), random nulls (X962), canaries | Neither; benchmark and infrastructure categories | Not strategies competing for selection |
| Technical retries and recoveries | Neither (D066, D077) | Same configuration |

- **DSR bar:** at N = 43, with the current Sharpe dispersion, the expected best skill-less Sharpe is about **1.11** (1.08 at 37).
- **DSR procedure:** on IS + VAL, as approved; Validation only after approval.
  - H013 uses its seed-averaged series.
  - Sharpe dispersion is computed across the latest valid run of each selection candidate.
- **Infrastructure needed for this accounting:** a `replicate_group` config field so that H013's seeds 2 and 3 are classified as replicates rather than as new candidates. The registry key already ignores `sizing` and benchmark kinds. It gets tests, and is implemented only after approval.

## 6. Random-portfolio benchmark (owner item 5)

- **Reported next to every relevant C03 result:** the matched no-skill null, i.e. the same capital, positions, holding period, costs and dates.
  - H013: the paired seed-matched nulls.
  - H012: the null is less natural, because its basket is fixed rather than random. We report the $100K / 15-position / hold-60 null cell (E962-22..24) and both controls.
- **Status:** a **diagnostic**; not a gate; not a replacement for the equal-weight benchmark. Screen thresholds are unchanged.

## 7. Scope, experiment budget and runtime (owner item 6)

**Committed runs** (always):

| Class | Runs | Notes |
|---|---|---|
| Technical verification (canaries) | 2 | X963: SPY RV indicator vs fresh history, point-in-time largest-15 ranking, exposure band, next-open. X964: MAX/MAX5 exclusion and the paired order equal to the null's. |
| **Selection** ($100K) | **12** | H012 × 3; H013 × 3 variations × 3 seeds (**6 candidates**) |
| Controls ($100K) | 4 | H012 Control A (1) + Control B per variation (3) |
| Capital sensitivity S1 ($200K, v1.0) | 8 | H012 v1.0 + Control A; H013 v1.0 × 3 seeds + null × 3 seeds |
| Capital sensitivity S2 ($200K, 20 positions, v1.0) | 8 | Same 8, with 20 positions |
| Random-portfolio nulls at $100K | 0 | E962-22..24 reused (identical settings) |
| **Committed total** | **34** | |

**Conditional runs** (only if a variation passes the preceding step):

| Class | At most | Notes |
|---|---|---|
| 2× slippage screen item | 12 | H012 ≤ 3; H013 ≤ 3 variations × 3 seeds |
| Robustness battery (≤ 2 hypotheses, pre-declared) | 28 | H012: 4×/6× costs + 8 perturbations (RV short 15/30, RV long 189/315, band 0.05/0.20, reconstitution monthly/semiannual) = 10. H013: (4×/6× costs, exclusion 15%/25%, hold 45/75) × 3 seeds = 18. |
| S1 for other passing variations | 8 | H012 ≤ 2; H013 ≤ 6 |
| **Conditional total** | **≤ 48** | |

- **Maximum: 82 QuantConnect backtests. This exceeds the 53 approved earlier.** Proposed revised cap: **82**, of which 34 are committed.
  - If no variation passes the screen, which is the most likely case, only the 34 committed runs happen.
  - Technical retries and recoveries are reported separately and are outside the cap.
  - **Reduced option (≤ 53):** drop S2 (−8) and run H013's robustness on seeds 1–2 only (−6); the maximum becomes 68. To reach 53, S1/S2 would also have to be limited to H013 only. That weakens the capital study, so it is not recommended.
- **Runtime** (measured on X962: 5–8 minutes per run):
  - committed ≈ 34 × 7 min ≈ **4 hours** of node time;
  - maximum ≈ 82 × 7 min ≈ **9.5 hours**.
  - Wall-clock time is longer with QuantConnect delays; the resumable queue and D077 recovery contain restart losses.
- **Cost:** fits the existing $24/month subscription (one node; runs are sequential). **No additional spending.**
- **Infrastructure (verification, not trials; with tests and canaries):**
  - SPY realised-volatility indicator;
  - point-in-time largest-15 basket with quarterly reconstitution;
  - exposure scaling with a band;
  - Control B's causal lagged exposure;
  - MAX/MAX5 exclusion reusing X962's `pick_order`;
  - `replicate_group` in trial accounting;
  - a C03 evaluation script (per-seed tables, controls, S1/S2, D073/P1 statistics), written and committed **before** the first C03 run.

## 8. Integrity and stopping rules (owner item 7)

- No Validation outcome is used to design or tune anything. No Holdout access.
- All definitions, parameters, configurations, seeds, controls and acceptance criteria are fixed and committed **before** the first C03 strategy result.
- **Rejection rules:** as in H012.md and H013.md; failed hypotheses are closed; no rescue in C03.
- **Stopping rule (owner-approved):** if C03 produces no qualifying candidate, no new cycle starts. A comprehensive review of the whole research programme follows (findings, limitations, costs, alternatives) for a separate owner decision.

## 9. Decisions requested

1. **Approve H012 and H013** as defined: variations, controls (A and causal B), pairing and per-seed rules, and the $200K S1/S2 design.
2. **PBO for C03:** Option P1 (recommended: D073 unchanged plus the stricter dual-count DSR and a pre-declared owner contingency) or Option P2 (D073 unchanged only).
3. **Budget:** approve the revised cap of **82** QuantConnect backtests (34 committed, ≤ 48 conditional), or choose the reduced option.
4. **Accounting infrastructure:** approve the `replicate_group` classification for H013's seeds (N 37 → 43).
5. **Order of work after approval:**
   1. build the infrastructure and tests;
   2. run the 2 canaries;
   3. commit the C03 evaluation script;
   4. then the 34 committed runs, the screen, and conditional runs as pre-declared;
   5. the C03 results checkpoint; STOP before any Validation.

   An owner checkpoint between the canaries and the first strategy run is optional: say if you want one.
