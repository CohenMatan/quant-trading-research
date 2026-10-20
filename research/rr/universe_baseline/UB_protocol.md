# Universe Baseline Audit — frozen protocol (UB-1)

**Decision:** D263 (owner, 2026-10-20). **Run:** E804-01 on host X804 v1.0. **Retry:** E804-02, only after a documented infrastructure failure, with identical code and settings.

**Kind:** infrastructure, aggregate-only, 0 orders.

**This protocol is frozen before any run.**
- It is SHA-256-pinned in `qresearch.rr_ub`, together with the host and the offline evaluation rule (`UB_eval.py`).
- No definition, threshold or outcome rule changes after the run.
- A genuine defect is handled as follows: STOP, document, ask the owner.

## 1. Question

Can QuantConnect's current data support a **point-in-time US-common-stock universe with market cap ≥ $2B, price ≥ $5 and ADV20 ≥ $5M** without survivorship bias?
- Tested on 2010–2021 (window W1), with QuantConnect's own market cap (**U-A**) and, where that is missing, a market cap rebuilt from QuantConnect's own data (**U-B**).
- Tested also on 1999–2009 (window W0).

No return, price path, per-security value or identifier is exported. The Holdout (2022-01-01 → 2026-08-31) is not read: the run ends 2021-12-31.

## 2. Run

| Item | Value |
|---|---|
| Window | LEAN 1999-01-04 → 2021-12-31 (the AUDIT split; the run cannot start earlier). No warm-up |
| Audit points | every month-end session from 1999-02 to 2021-11 (the 2021-12 month-end is stamped 2022-01-01 and never reached). 1999-01 is skipped because ADV20 needs 20 sessions |
| Windows | W0 = 1999-02 … 2009-12; W1 = 2010-01 … 2021-11 |
| Build | QuantConnect's default build, recorded (`lean_version_policy: default_build_digest_verified`) |
| Universe objects | every `Fundamental` object QuantConnect passes to universe selection (all US equities with price data that day) |
| Orders / subscriptions | none (selection returns no symbols); SPY only, as the harness clock |
| Output | aggregate counts, rates, quantiles, bootstrap intervals and SHA-256 digests (§7) as plain JSON in the harness summary statistics; no compression or encoding |

## 3. Definitions (at each audit point t = month-end session; data as of that session's close)

| Term | Definition |
|---|---|
| ADV20 | mean of the last 20 finite daily `dollar_volume` values seen in selection (the harness rule, D023 / D029); undefined with fewer than 20 |
| L(t) | `price` (raw) ≥ $5 and ADV20 ≥ $5M |
| Structural common | `has_fundamental_data` and the harness `is_us_common(f, None)` (common stock, not a depositary receipt, primary share or US country, D057 / D061 exclusions) and the vendor `exchange_id` in {NYS, NYSE, NAS, ASE, AMEX}. **No dated overrides** (they are keyed by earlier QuantConnect identifiers, D257); the 12 affected securities are a disclosed limitation |
| A(t) | L ∩ structural common, vendor `market_cap` > 0 |
| E(t) | A with `market_cap` ≥ $2B (**the vendor-eligible set**) |
| M(t) | L ∩ structural common with vendor `market_cap` missing / 0 / unreadable |
| N(t) | L without a fundamentals object (`has_fundamental_data` false). **N_c** = those whose security is structural common at *some* audit point of the run; **N_x** = the others (mostly ETFs / ADRs / funds; reported only) |
| S | `company_profile.shares_outstanding` (restated by Morningstar for all later splits, D107) |
| SF | the security's `split_factor` on the day (LEAN factor file: product of later split adjustments) |
| **R (U-B cap)** | S × raw price × SF when S > 0 and SF > 0, else invalid. The later-split restatement of S and SF cancel if both run through the same date |
| VS | vendor-implied shares = `market_cap` / (raw price × SF), A names only |
| R2B(t) | M names with valid R ≥ $2B (**repaired**) |
| q10(t) | 10th percentile of ADV20 over E(t) |
| U_A(t) | (M ∪ N_c) with ADV20 ≥ q10(t): unrepaired potential eligibles **without** U-B |
| U_B(t) | (M with invalid R ∪ N_c) with ADV20 ≥ q10(t): unrepaired potential eligibles **with** U-B |

**Gap (stock-months, per calendar year y):**
- Gap_A(y) = Σ|U_A| / Σ(|E| + |U_A|)
- Gap_B(y) = Σ|U_B| / Σ(|E| + |R2B| + |U_B|)

These are conservative upper bounds: liquid names of unknown cap are counted as potential eligibles. Variants without the q10 liquidity match are reported, not gated.

**Exit (survivorship):**
- `last_seen(s)` = the last selection date on which security s appears in the run (any filter state).
- A stock-month (s, t) **exits within h months** if last_seen(s) < call(t) + h months, where call(t) is the selection date that reflects t.
- It is **assessable** only if call(t) + h months ≤ the last selection date of the run (follow-up censoring; nothing after 2021-12-31 is read).
- Primary h = 24 months (months to 2019-11). Where 24 months is unassessable, h = 12 months (months to 2020-11).
- 2021 is unassessable.

**Survivorship bias (per year, assessable months, stock-months):**
- b_A(y) = e(E ∪ U_A) − e(E)
- b_B(y) = e(E ∪ R2B ∪ U_B) − e(E ∪ R2B)

where e(·) is the exit rate. In words: how much the excluded names would raise the universe's later exit rate.

**Uncertainty:**
- Securities are the clusters: a within-year cluster bootstrap over securities, B = 1,000, seed 20261020.
- The upper bound is the 97.5th percentile.
- Also reported:
  - the exit-rate difference d = e(U) − e(included), with its interval;
  - security-level exit rates (each security's first assessable month in the category and year) with Wilson 95% intervals.

## 4. U-B validity tests (per window)

| Test | Population | Statistic | Pass |
|---|---|---|---|
| V1a vendor agreement | A stock-months with valid R | share with \|R / market_cap − 1\| ≤ 2% | ≥ 95% in every year |
| V1b threshold agreement | same | share with (R ≥ $2B) = (market_cap ≥ $2B) | ≥ 99% in every year |
| V2a split behaviour of S | consecutive audit months of one security with SF ratio q = SF(t2)/SF(t1) ≥ 1.4 or ≤ 1/1.4 and S > 0 both months (A and M names) | "restated": \|S2/S1 − 1\| ≤ 3%; "raw-like": \|S2/(S1·q) − 1\| ≤ 3%; else "other" | restated ≥ 90% and raw-like ≤ 5% (≥ 30 events) |
| V2b split continuity of R | the V2a events of A names with market_cap both months | \|(R2/R1)/(mc2/mc1) − 1\| ≤ 5% | ≥ 95% |
| V3 share-change timing | A names, consecutive months without a split (\|q − 1\| < 1%), \|S2/S1 − 1\| ≥ 5%, VS valid in months t−1 … t+1 | same-month: VS moves ≥ 2.5% in the same direction in the same month; lead: not same-month and VS moves so at t+1 (S known before the vendor's PIT cap: **look-ahead signal**); lag: not same-month and VS moved so at t−1; none: else | lead ≤ 10% and same-month ≥ 70% (≥ 100 events) |
| V4 staleness / backfill | stock-months with valid R | share whose S is unchanged for ≥ 18 audit months; **flat-life** securities: S identical over ≥ 24 audit months of L-common life | R2B stale share ≤ max(2 × E's, E's + 10 points); M flat-life share ≤ 2 × A's + 5 points |
| V5 availability | M stock-months | share with S > 0 on the decision date (read from the stream at that date) | reported (coverage of U-B) |

**U-B VALID (window)** = V1a, V1b, V2a, V2b, V3 and V4 all pass with the minimum samples met.
- A test with fewer events than its minimum is **INSUFFICIENT**, and U-B is then not VALID for that window.

**Interpretation limit (fixed now):**
- V1–V4 test agreement with the vendor's own market cap, split consistency and internal timing.
- They do **not** establish independent PIT validity of S. No external source is used in-run, because the SEC fallback is not authorised.
- A PASS through U-B is reported as "formula-consistent and internally PIT-consistent; independent PIT validity not established".

## 5. Per-year gates

| Gate | Rule |
|---|---|
| G-COV | Gap ≤ 3.0% in every year of the window (view A: Gap_A; view B: Gap_B) |
| G-SURV | upper 95% bound of b ≤ 0.50 percentage points (h = 24) or ≤ 0.25 points (h = 12), in every assessable year. Unassessable years (2021) carry no survivorship evidence: they do not block the outcome but are listed with it, and the report must say that survivorship was not assessable there |
| G-PRE (W0 only) | Uses the view's included set I (view A: E; view B: E ∪ R2B). (i) Plausibility: the yearly mean monthly count of \|I\| ≥ 50% of its 2010–2012 mean, in every W0 year. (ii) Dead companies present: of the securities in I at any 1999 audit point, ≥ 10% have last_seen before 2010-01-01 |

## 6. Outcome per window (evaluated in this order)

1. **PASS-A** (QuantConnect market cap alone suffices): G-COV and G-SURV pass in view A in every year (and G-PRE for W0).
2. **PASS-B** (needs U-B): U-B VALID, and G-COV and G-SURV pass in view B in every year (and G-PRE for W0).
3. **FAIL**:
   - in the best available view (B if U-B VALID, else A), some year has Gap > 3.0% or a point estimate of b above its threshold; or
   - G-PRE fails (W0).
4. **AMBIGUOUS**: anything else. Examples:
   - point estimates within the thresholds but an upper bound above;
   - U-B INSUFFICIENT;
   - U-B not VALID while view B would pass.

**Owner-facing rules:**
- Every outcome STOPS for owner review.
- AMBIGUOUS and FAIL never lead to U-C, a relaxed universe or another run.
- No outcome amends D033 / D035. A W0 PASS only allows a separate amendment proposal.
- A low missing rate or a non-significant difference is never reported as "unbiased" (D263). Only G-SURV's upper bound, together with G-COV, supports a pass.

## 7. Exported aggregates

- **Per year:**
  - stock-month and distinct-security counts of L, A, E, M, R2B, M-invalid, N_c, N_x, U_A, U_B (with and without the q10 match);
  - monthly min / mean / max of |E| and |E ∪ R2B|;
  - Gap_A, Gap_B;
  - exit rates (h = 24 / 12) by group (E, R2B, U_A, U_B, A below $2B, N_c, N_x) at stock-month and security level, with intervals;
  - b_A, b_B and d with bootstrap intervals.
- **V tests:**
  - V1 quantiles (1, 5, 50, 95, 99%) of R / market_cap per year;
  - V2 / V3 event counts by class;
  - V4 shares;
  - V5 coverage;
  - share-class market cap presence among M names (diagnostic only; not a repair rule).
- **Checks:** counts of structural read errors, market-cap and shares read errors.
- **Digests:** SHA-256 digest of the per-month category counts (for future reruns), audit-point count, runtime.
- **Excluded:** no identifier, ticker, per-security value, price, return or benchmark series.

## 8. What this run does not do

- No strategy, order or return.
- No SEC data (U-C is not implemented).
- No Holdout data.
- No change to any frozen experiment.
- No relaxation of the universe rule.

**Compliance refusal:** if QuantConnect's compliance review refuses the code, the run STOPS and is reported as a platform blocker, not retried.
