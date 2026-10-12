# H027 — Exposure-Controlled Learned Stock Score: frozen pre-registration (v1)

Owner decision **D213** (`docs/owner/2026-10-12_p12cp1_h027_exposure_controlled_score.md`, verbatim). This file is hash-pinned in `qresearch.p12h027` with the code that implements it, before any H027 null world or result exists. Nothing in it changes after a result is seen; any change is H028 or later.

## 1. Status and periods

- **Closed and unchanged:**
  - H022 — REJECTED.
  - H023 — NO ROBUST SCORE V2 CANDIDATE.
  - H024 — NO ROBUST H024 FEATURE MODEL.
  - H025 — REJECTED.
  - **H026 — REJECTED — LEARNED SCORE PORTFOLIO DOES NOT ROBUSTLY BEAT SPY.**
  - H026's original unconditional null (E028-02/03, 5,000 worlds, c_WEALTH 0.2245) is kept unchanged beside the new H027 null.
- **Data v2.1:** frozen under D207, manifest SHA-256 `ef0a7a66…`.
  - The owner-approved exception (D213) is recorded in `research/phase11/data_v21/owner_exception_D213.json`.
  - NEW_YEARS_MAPPING stays recorded as failed as written.
- **Development data:** 2011–2021, **fully seen** (H026 and its post-mortem). H027 can give **development evidence only**; it cannot confirm.
- **Holdout:** 2022-01-01 → 2026-08-31 stays sealed. Nothing from it is read.

## 2. The question

Does the learned 11-feature score contain stock-selection information beyond the LOWVOL exposure, while still producing more terminal wealth than SPY?

**H0 (the conditional null):** LOWVOL may have a genuine return and risk relationship, but the other ten features (MOM, GPA, ACC, BM, AG, REV1M, CBOP, HI52, CFP, EQA) carry no stock-specific predictive information beyond LOWVOL.

## 3. The real H027 portfolio = the frozen H026 procedure

The real H027 portfolio is `qr_h026.run_world(months, None)`, unchanged.

**Unchanged from H026 (spec `research/phase11/H026_spec.md`):**
- the 11 features and their PIT formulas (`qr_h024`);
- the transforms;
- the 63-session SPY-relative target and the label-availability rule;
- monthly equal weighting;
- weighted Ridge with λ ∈ {0.01, 0.1, 1, 10, 100};
- the outer walk-forward 2015–2021 (cutoff at each December review);
- inner λ selection on 2013..Y−1 by Σ ln(W/SPY);
- Top-15, at most 3 per FF12 sector, 10% initial cap;
- monthly rebalance at the next open;
- $7 per order and 0.10% slippage per side;
- long only, no leverage, $100,000 start.

**Integrity expectation:** terminal wealth $311,396.77 and S_WEALTH 0.171482 (E028-05). If the real run does not reproduce them (beyond 1e-9 relative), STOP and explain.

## 4. LOWVOL-conditional null (`qr_h027.conditional_permuted`)

- **Per seed (1–5,000):** the frozen persistent identity tether `qr_p7_pred.Tether(seed)` (one stratum, no self-matching, the partner kept while both are in the population) gives every recipient a donor on each review date.
- **What the recipient gets:** the donor's complete OTHER vector (the ten non-LOWVOL feature columns, together, from the donor's own row on that date).
- **What the recipient keeps:**
  - its own LOWVOL value;
  - its returns, prices, corporate actions and identity;
  - its sector and universe membership.
- **Never permuted:** prices, returns, SPY and the calendar.
- **Every world reruns the complete procedure** (`qr_h027.run_world_xs`, line-for-line `qr_h026.run_world`):
  - inner λ selection and annual Ridge fits;
  - scores, Top-15 and the sector cap;
  - trading, commissions and slippage;
  - terminal wealth vs SPY.
- **Recorded per world:**
  - S_WEALTH and terminal wealth;
  - excess CAGR, MaxDD and volatility;
  - monthly beta to SPY, and up and down capture;
  - years beating SPY;
  - the 7 yearly returns and the 7 λ;
  - a coefficient digest (full coefficients for seeds 1–25).
- **Seeds and runs:**
  - 1–2,500 in E029-02 and 2,501–5,000 in E029-03;
  - seeds 1–25 rerun independently in E029-04.
  - The rerun must reproduce λ, coefficients, yearly returns, terminal wealth and S_WEALTH **exactly** (bitwise-equal JSON values). Otherwise STOP.
- **c_WEALTH_CONDITIONAL** = the 50th largest of the 5,000 null S_WEALTH values (`qr_h026.critical_value`, the prior-phase convention). It is pinned and merged before the real run.
- **Empirical p** = (1 + #{null S ≥ real S}) / 5,001.

## 5. Risk-adequacy audit (before any significance claim)

**Rule (pre-registered).** The conditional null is ADEQUATE only if, for **each** of four measures, at least 1% of the 5,000 null worlds (≥ 50) are at least as defensive as the real portfolio:

| Measure | "At least as defensive" means | Real value |
|---|---|---|
| Annualised volatility | ≤ | 0.163921 |
| MaxDD | ≥ (shallower) | −0.261152 |
| Monthly beta to SPY | ≤ | 0.795037 |
| Monthly down-capture | ≤ | 0.775512 |

- The real values are the H026 values (E028-05; P11-CP2 definitions). They are identical to the real H027 values by construction, and that identity is checked in the real run.
- **Otherwise:** STOP with "H027 BLOCKED — EXPOSURE-CONTROLLED NULL INADEQUATE". No other null is tried; a different null would be H028.
- Up-capture distributions are reported too.

## 6. LV15_CONTROL (`qr_h027.lv15_scores`)

- **Population:** at each decision review, the same H026 model population.
- **Ranking:** by LOWVOL alone, lowest 60-day volatility first (score = −centred percentile of the raw 60-day volatility); ties go to security id.
- **Mechanics:** exactly as H026 — Top-15, at most 3 per FF12 sector, 10% initial cap, monthly rebalance at the next open, the same costs and cash handling.
- No Ridge and no other feature. It is a control, not a candidate.

## 7. Gates (all required)

| Gate | Requirement |
|---|---|
| A1 | S_WEALTH_real > c_WEALTH_CONDITIONAL and empirical p ≤ 0.01 |
| A2 | terminal wealth H027 > LV15 and CAGR H027 > LV15 |
| A3 | wealth H027 ≥ 1.15 × SPY and CAGR H027 − CAGR SPY ≥ +2.0 points (**a carried-forward economic requirement, not new independent evidence**) |
| A4 | H027 ahead of LV15 (yearly log-relative > 0) in ≥ 5 of 7 years; Σ 2015–2017 > 0 and Σ 2018–2021 > 0 |
| A5 | \|MaxDD H027\| ≤ 1.25 × \|MaxDD SPY\| and volatility H027 ≤ 1.25 × SPY |
| A6 | 0.20% slippage per side, same selections, no retraining: H027 wealth > SPY and > LV15 (each also at 0.20%) |

**Statuses:**
- All pass → "H027 DEVELOPMENT CANDIDATE — INCREMENTAL EDGE BEYOND LOWVOL DETECTED — FINAL HOLDOUT SEALED". The final score is then fitted exactly as in H026 spec §12 (inner years 2013–2021; fit at the 2021-12-31 cutoff; labels exiting before it).
- Any gate fails → "H027 REJECTED — NO ROBUST STOCK-SELECTION EDGE BEYOND LOWVOL EXPOSURE".

## 8. Non-gating diagnostics (never rescue)

1. **LOWVOL-factor regression:**
   - Per decision month: factor = equal-weight r_oc of the lowest-LOWVOL quintile (x ≤ the 20th percentile) minus the equal-weight r_oc of all open-valid population stocks (entry open → period-end close).
   - Dependent variable: H027 period return minus SPY period return (daily close marks at period ends).
   - Model: OLS, y = α + γ·factor. Report α monthly and annualised (×12), Newey-West t(α) with lag 2, γ and R².
2. **Sector-neutral:** as H026 (holdings vs their FF12 sector's equal-weight return).
3. **March 2020 attribution:** H027, LV15 and SPY returns, and the log-relatives.
4. **$200K, Top-10, Top-20, market regime:** as H026.

## 9. Memory reduction (infrastructure; numerics unchanged)

- **Host S029** subclasses the pinned S028, which is uploaded byte-identically as `qr_s028`.
- **Before the matrix build:**
  - it releases the run-time fundamentals store, revenue ledger, first-seen ledger, weekly checks and digest buffers, which are not used after the run;
  - it calls `gc.collect()` and `malloc_trim`.
- **During the build:**
  - it computes the 200-day state (the only use of the high and low matrices) right after X801's build;
  - it then frees high and low before S028's open-price and multiplier matrices are allocated.
- **In null and real modes:** after the months are built, it frees every price matrix and construction intermediate.
- **Stage memory** is reported (VmRSS and VmHWM).
- **Equivalence gate (canary E029-01, before any null world):**
  - the feature-panel digest equals H026's pinned `10a54163…`;
  - the response-panel digest equals `e1503f9c…`;
  - the eligible / H022-population per-decision counts equal the P11-CP1 canary;
  - H026's **unconditional** null worlds 1–25, rerun in S029 through the frozen `qr_h026.run_world`, equal the committed E028-04 rows exactly. That checks Ridge coefficients, λ decisions, portfolio and costs on real data without computing any H027 real statistic.
  - Any difference → STOP.

## 10. Canary E029-01 (no real H027, LV15 or factor result)

- **Checks:**
  - LOWVOL never permuted;
  - the ten other features move as one donor vector;
  - persistent donors and no self-matching (the frozen tether keeps a pair while both stay, except its documented fixed-point splice, at most one changed pair per month and seed);
  - recipients' returns, sectors and flags unchanged;
  - the equivalence gate (§9);
  - LV15 picks equal an independent lowest-volatility walk;
  - costs on a synthetic month by hand;
  - S_WEALTH arithmetic;
  - the c_WEALTH_CONDITIONAL order statistic;
  - stage memory.
- **Synthetic worlds** (returns from features + noise on the real month structure; SPY real):
  - **World A**, LOWVOL only: five replicates, each with 19 conditional-null worlds. Pass if the median percentile of the real model among its nulls is **below 0.90**.
  - **World B**, LOWVOL plus GPA (equal strength): three replicates, each with 19 nulls. Pass if **every** replicate's percentile is **≥ 0.90**.

## 11. Run order

1. Canary E029-01, then pin the code and digests.
2. Null E029-02 (seeds 1–2,500) and E029-03 (seeds 2,501–5,000), then the rerun E029-04 (seeds 1–25).
3. Adequacy audit. STOP if inadequate.
4. Pin c_WEALTH_CONDITIONAL and merge.
5. The ONE real run E029-05: check H026 reproduction, then A1–A6 and the diagnostics.
6. Final score only if every gate passes.
7. P12-CP1, then STOP.

The Holdout is never run.

## 12. Not allowed

- Any change to features, formulas, lookbacks, target, λ grid, K, sector cap, mechanics or costs.
- A regime, crash or trend filter, or intentional cash.
- New data or factors.
- A different null after a result.
- Removing or winsorising any period.
- Opening the Holdout.
