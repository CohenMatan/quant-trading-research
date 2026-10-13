# H029 / H030 — Amendment 1: sector-stratified null (owner D233)

**Status:** an **owner-approved pre-performance methodological amendment following a pre-registered adequacy failure**. The new null was **not** pre-registered from the start.

**Background:** the original null of `research/phase14/H029_H030_spec.md` section 8 failed the pre-registered adequacy rule (section 9 B) in P14-CP3a:
- real H029 FF12 sector HHI 0.1630 against the null 99.5th percentile 0.1599;
- only 2 of 5,000 null worlds reached the real concentration.

That record stays permanently, and that null stays **INADEQUATE**.

**Timing:** this amendment was written, frozen and committed before any sector-stratified null world, canary or real H029 / H030 value existed.
- **No real H029 / H030 portfolio return, wealth, capture, threshold or gate result has ever been computed.**
- The only real quantities ever observed are the score-only selection-structure values that the adequacy rule requires (turnover and sector HHI of the Top-15 target lists; section 9 B).
- The motivation is the structural inadequacy of the null, not strategy performance.

**Text:** the original specification is unchanged byte for byte (its SHA-256 stays pinned). This amendment replaces only the parts named below, and wherever it conflicts with the original text it takes precedence.

## A1. The only methodological change

| | Donor of a recipient's six-signal vector at a review |
|---|---|
| Original null (P14-CP3a, inadequate) | any other H029-eligible stock (`qr_p7_pred.Tether`, one stratum) |
| **Amendment 1 null** | **another H029-eligible stock of the recipient's own FF12 sector at that review** |

**Nothing else changes:**
- H029: F1, F2, F4, F5, F7, F8; at least 5 of 6; equal weights; no ML, Ridge or λ.
- H030: exactly 0.50 / 0.50.
- H028: frozen.
- Data v3: frozen (manifest, PIT rules, guard, signal formulas, eligibility).
- Mechanics: Top-15, at most 3 per FF12, monthly review, next-open execution, $7 per order, 0.10% slippage, $100,000.
- Gates N1–N5 and C1–C7.
- The adequacy rule (section 9), the threshold convention (50th largest of 5,000 = the 99th percentile) and the empirical p.
- The real-run outputs, the descriptive metrics and the synthetic long-horizon rule (section 12: only if C1–C7 all pass).

## A2. New null (replaces section 8 step 1)

One world, seed s = 1 … 5,000:

1. **Tether:** a fresh `qr_h020_stats.ChartTether(s)` steps over the 84 evaluation months in date order.
   - It acts on the ids of E29(t), with **strata = each stock's FF12 sector at that review**.
   - FF12 is the same frozen classification the strategy uses for its at-most-3-per-sector cap (the per-review `sector` of the H029 months, built in S031 exactly as for H026 / H028).
   - No new, broader or narrower sector grouping is created. The H029 universe already excludes SIC 6000–6999 and stocks without SIC (Data v3); no other sector treatment is introduced.
2. **Donor rule:** every recipient's donor is another stock of the **same FF12 sector at that review**.
   - Partners persist while both stocks stay eligible and in the same sector. This is the persistent identity-tether principle; the ChartTether rule 1 keeps a pair only within one stratum.
   - A stock whose sector changes between reviews is re-matched inside its new sector.
3. **Complete vectors:** the recipient receives the donor's **complete six-signal vector**, including its missing pattern. Features are never shuffled individually.
4. **Recipient keeps everything else:** its identity, prices, returns, corporate actions, H028 score, sector and mechanics.
   - E29(t), its size and every recipient's eligibility are unchanged, because donors are themselves eligible.
   - Sector strata do not change who qualifies.
5. **No self-matches:** donor ≠ recipient for every recipient at every review.
   - If any FF12 sector of any review holds fewer than 2 eligible stocks, the tether would map a stock to itself. Then: **STOP — SECTOR-STRATIFIED NULL NOT CONSTRUCTIBLE**.
   - Implemented as `qr_h029.NullNotConstructible`.
   - There is **no cross-sector fallback**.
6. **Unchanged steps:** steps 2–4 of section 8 and its recorded fields stay as they are. In particular:
   - **H030_null** = 0.50 × centred(**real** H028) + 0.50 × centred(sector-stratified permuted H029) over J(t);
   - H028 is **never** randomized.

**Implementation:** `qr_h029.tether_vectors` / `qr_h029.donors` with `_sector_step`, through `qr_p7_pred`'s import of the frozen `qr_h020_stats`. The S031 host is v1.1; only its canary checks were added.

## A3. Scientific interpretation and limitation (disclosure)

**The questions the new null asks:**
- **H029:** within the same sector environment, does the real Business Improvement ranking select stocks with more useful future information than a reassignment of Business Improvement vectors among sector peers?
- **H030:** does adding the real H029 information to the frozen H028 improve the portfolio more than adding the same-sector-randomized H029 information?

**Limitation:**
- **The sector-stratified null intentionally does not test whether H029's sector allocation itself is predictive.** It keeps the sector composition of the eligible set fixed in every world, and so it controls that structural source of variation.
- A significant result (N1 or C1) is therefore evidence of **within-sector / conditional stock-selection information**, not of total alpha including sector timing.
- An N1 pass would read: "H029 contains significant predictive information beyond randomized same-sector Business Improvement assignments". It never reads "H029 proves sector allocation is alpha".

## A4. Run ids (replaces section 1's run list for the null and the real run)

| Run | Purpose |
|---|---|
| E031-01 .. E031-04 | Original null: canary, null and rerun. Kept as the permanent record (P14-CP3a). **Never reused.** Its thresholds 0.2696 / 0.0059 are **permanently invalid**. |
| **E031-06** | New canary (section A5) |
| **E031-07 / E031-08** | Sector-stratified null, seeds 1–2,500 / 2,501–5,000 |
| **E031-09** | Rerun of seeds 1–25: every stored field must be identical to E031-07's rows 1–25, else STOP |
| **E031-10** | The ONE real 2015–2021 development evaluation. **Only** after adequacy passes and the new c_UP_H029 / c_INCREMENTAL_H030 are pinned, committed and merged. |

E031-05 (the original real run id) was never run and is never used.

## A5. New canary (replaces section 13 item 7 and the synthetic B definition; everything else in section 13 stays)

**Item 7 — the null (seeds 1 and 2):**
- **Constructible:** every FF12 sector of every review holds ≥ 2 H029-eligible stocks. The minimum sector size is reported. If it fails: STOP — SECTOR-STRATIFIED NULL NOT CONSTRUCTIBLE.
- Donor sector == recipient sector for every mapping (count 0 otherwise).
- Recipient sectors unchanged by the null (count 0).
- Recipient eligible sets unchanged (count 0).
- Every recipient holds its donor's complete six-signal vector (count 0).
- No self-matches (count 0).
- Persistent donor mapping: of the recipients whose previous donor is still eligible and in the same sector, ≥ 95% keep it.
- Recipient return / holding arrays (H029 months and joint months) unchanged after a null world: digests identical.
- The H028 scores used by H030_null equal the real ones exactly.
- Costs and mechanics unchanged: the constants (K 15, cap 3, $100,000, $7, 0.10%, stress 0.20%, λ 100) are reported and checked.

**Items 1–6 unchanged:**
- Data v3 digests;
- H028 / LV15 reproduction;
- H029 score recomputation;
- H030 exactly 50/50;
- entries after the review.

**Item 8 — Synthetic A (pure noise within sectors):**
- Unchanged: i.i.d. N(0, 1), 5 replications (seeds 7101–7105), 50 **sector-stratified** null worlds each.
- **Pass:** at most 1 of 5 with p ≤ 0.02, for S_UP(H029) and for S_INC(H030).

**Item 9 — Synthetic B (planted within-sector upside predictor):**
- z = (r_oo − the mean r_oo of the stock's FF12 sector in that month) × 1[SPY month up] + N(0, 0.05²). This is a deliberate look-ahead, canary only.
- Seed 7201; 50 sector-stratified null worlds.
- **Pass:** S_UP(H029) above every null world (p = 1/51).
- The sector demeaning makes the planted information purely within-sector, so the canary shows the sector-stratified null can detect within-sector selection skill.

**Any failure → STOP.** No null world is run.

## A6. Adequacy (section 9, unchanged), outcome strings and comparison

**Rule:** exactly section 9, applied to the 5,000 sector-stratified worlds:
- **B:** the real H029 / H030 name turnover and FF12 sector HHI lie inside the [0.5%, 99.5%] range of the null;
- **C:** null volatility, beta, up capture and down capture are finite with sd > 0, and the medians of beta / up / down capture lie in [0.5, 1.5].

**Any failure → H029/H030 BLOCKED — SECTOR-STRATIFIED NULL ALSO INADEQUATE → STOP.**
- No third null is designed. Industry, sector + size, market-cap deciles, propensity and residualized nulls are all excluded without a separate owner review.

**Descriptive comparison** (not a choice between nulls; the original is already rejected on adequacy):
- the original single-stratum null (committed `research/phase14/cp3/P14_CP3_null_rows.json`) side by side with the sector-stratified null;
- covering the H029 / H030 sector HHI, turnover, beta, up capture, down capture and volatility.

**Thresholds:** only if every adequacy test passes, c_UP_H029 and c_INCREMENTAL_H030 are computed from the sector-stratified null.
- They are pinned in `qresearch.p14h029`, then committed and merged before E031-10.
- The old 0.2696 / 0.0059 are never used; a test asserts that the pinned values come from the new null result.

## A7. Statuses (unchanged wording)

**H029:**
- "H029 UPSIDE SIGNAL REJECTED", or
- "H029 UPSIDE SIGNAL CANDIDATE".

**H030:**
- "H030 REJECTED — PRE-REGISTERED 50/50 COMBINATION DOES NOT SUFFICIENTLY IMPROVE H028", or
- "H030 DEVELOPMENT CANDIDATE — PRE-REGISTERED H028 + H029 COMBINATION".

**Other rules:**
- The synthetic long-horizon stage runs only if C1–C7 all pass.
- The Holdout (2022-01-01 → 2026-08-31) stays sealed in every case: no prices, no fundamentals, no SPY returns, no diagnostic peek.
