# Data v3 — targeted fundamental PIT / restatement hardening for H029: pre-registered specification

**Owner decision:** D229 (`docs/owner/2026-10-12_p14_h029_h030_plan.md`, Part A, sections 4–16).
**Written and committed before:**
- the Data v3 reference table is built;
- any vendor-to-SEC comparison is made;
- any H029 or H030 value, score, portfolio, null world or return is computed.

**Scope:** data quality only. No return, IC, wealth, portfolio or feature-return quantity is computed, requested or inspected in Part A. The in-cloud audit host (X803) exports aggregates and digests only.

## 1. What Data v3 is (and is not)

- **A new, immutable layer for H029 only.** It is built **on top of** the frozen Data Infrastructure v2.1 and changes nothing in it:
  - the frozen Data v2.1 host X801 is uploaded byte-identical as `qr_x801`;
  - the packed v2.1 table `qr_data_v21*`, its manifest and every v2.1 rule (universe, M2 timing, v2.1 restatement guard, identity, freshness, True TTM, SEC market-cap repair) are used unchanged.
- **Components added by Data v3:**
  - (a) the **guard-v3 reference table** `src/qresearch/lean/qr_data_v3*.py`, built offline from public SEC company facts only (no QuantConnect data);
  - (b) the **v3 view** logic, `src/qresearch/lean/qr_v3.py` (pure, unit-tested offline);
  - (c) the six **H029 signal constructions** and their validity / denominator / corruption rules (section 5);
  - (d) the **SEC validation reference** `qr_v3val*.py`, used by the audit host X803 only (section 7).
- **H028 is untouched.**
  - The v2.1 point-in-time store keeps receiving exactly the versions it received before.
  - H028's features, scores and results are computed from that store only. H028 stays reproducible from its frozen artifacts.
  - H029 reads only the v3 view.
  - Where Data v3 gives a different accounting value from Data v2.1, the difference is recorded (section 11). H028 is never modified.
- **Window:** nothing filed, reported or effective after 2021-12-31 enters any table. Nothing after 2021-12-31 is requested in any run. The Holdout (2022-01-01 → 2026-08-31) is never touched.

## 2. Field provenance

| Field (vendor) | Use in H029 | Period | Timestamp / availability | Source version | Restatement relationship | Earliest permissible signal date |
|---|---|---|---|---|---|---|
| `revenue_q` | F1 (quarters q0, q1, q4, q5); True-TTM revenue for F2, F8 | fiscal quarter ending at the report's period end, matched to the SEC period (±6 days; frozen `qr_v2.Reference.match`) | M2: max(first seen in QuantConnect's historical stream, original SEC 10-Q/10-K filing + 1 day) | the vendor version (first seen, or a revision first seen on a weekly scan) | guard v2.1 (unchanged) **and** guard v3 (section 4) | the M2 usable day; computed on the universe-selection day (the calendar day after the review session); traded at the next session's open |
| `gross_profit_q` | True-TTM gross profit (F2) | same | same | same | guard v3 (new) | same |
| `net_income_q` | True-TTM net income (F5) | same | same | same | guard v3 (new) | same |
| `operating_cash_flow_q` | True-TTM operating cash flow (F4) | same | same | same | guard v3 (new) | same |
| `total_assets` | snapshots TA0, TA4 (F4, F5, F8) | balance-sheet date = period end | same | same | guard v2.1 and guard v3 | same |
| `*_ttm` (fiscal-year totals) | **reconciliation only**: the frozen 1% True-TTM fiscal-year check (D113). Never a signal input. | fiscal year | same | same | not guarded field-by-field (a fiscal-year total alone can only make a TTM window fail, never change a TTM value); a version blocked for any guarded field is excluded whole | same |
| SEC cover-page shares | F7 | cover date | the filing's own date + 1 day (D111); at most 135 days old | the original 10-Q / 10-K only (each count belongs to its own filing; never restated by a later filing) | not applicable: no later filing can replace it | filing date + 1 |

**Splits for F7:** QuantConnect's split events, applied only when the ex-date is on or before the decision day (frozen D111 `_adjust` rule, as in `qr_h029a.dilution`).

## 3. Guard-v3 reference table (offline builder `research/phase14/data_v3/build_data_v3.py`)

1. **Registrants and periods.**
   - Registrants: every registrant of the Data v2.1 filing table `f` (3,941 registrants).
   - Periods: every period end p of that registrant in `f` (10-K / 10-Q period ends 2008-03-31 → 2021-12-31). These are the same SEC periods that the in-host match (`Reference.match`) returns.
2. **Facts.**
   - SEC XBRL company facts (the cached `data.sec.gov` snapshots), keeping only facts **filed on or before 2021-12-31**.
   - Concept groups (`qresearch.sec_pit.TAGS`): revenue, gross profit, net income, operating cash flow; total assets = `Assets`.
   - Within one filing, the tag order of `TAGS` decides.
3. **As-known value of period p on date d** (only facts filed on or before d):
   - **Quarterly flow:**
     - (i) the latest-filed three-month fact ending within ±7 days of p (ties: accession number, then tag order);
     - otherwise (ii) the year-to-date difference: take the longest year-to-date duration class c ∈ {12, 9, 6 months} with a fact ending within ±7 days of p (latest filed). Subtract the latest-filed fact of class c − 3 months with the same start (±7 days), ending 60–120 days before p.
     - This is how a fourth quarter (fiscal year minus nine months) and the cumulative cash-flow statements become quarterly values. A year-to-date value is **never** taken as a quarter.
     - No interpolation; if a piece is missing, the value is missing.
   - **Total assets:** the latest-filed instant fact within ±3 days of p.
4. **Timeline.**
   - Evaluate the as-known value on every distinct filing date of the facts involved.
   - Keep a value only if it differs by **more than 1.5%** from every value kept before it.
   - The 1.5% storage threshold was fixed **before any vendor comparison**, to fit the guard table into four QuantConnect project files (the 50-file limit; section 3.7). Restatements of 1.5% or less are immaterial for cross-sectional ranks.
   - The first kept value is the original (as first filed). Every later kept value is a **restated value**, with the day it was filed.
5. **Stored:** for every (registrant, period, field) with at least one restated value: field, (filing date − p) in days, and the restated value (four significant digits, the frozen `g4` code). The original value is not stored (section 4 shows why it is not needed).
6. **Fields guarded:** `revenue_q`, `gross_profit_q`, `net_income_q`, `operating_cash_flow_q`, `total_assets`.
7. **Packing:**
   - columnar, lzma + base85 (the `qresearch.v2pack` encoding);
   - parts `qr_data_v3_NN.py` of at most 63,900 characters each, with **at most four parts**;
   - no separate loader file: `qr_v3.load_guard()` reassembles the parts and verifies the SHA-256.
   - Table SHA-256 and sizes are recorded in `research/phase14/data_v3/data_v3_reference.json`.
   - If the built table needs more than four parts, STOP and report (the H029 host could not fit the project-file limit). No threshold is changed after the build.

## 4. Guard-v3 rule and the v3 view (in-host, `qr_v3.py`)

1. **Where it applies.**
   - It applies to every vendor version that the frozen Data v2.1 ledger feeds to the v2.1 store (new reports and weekly-scan revisions). Versions the v2.1 guard blocks are never fed, so they are never in v3 either.
   - It uses the same registrant (CIK) and the same matched SEC period as the v2.1 ledger: the frozen `Identity.m2` and `Reference.match`, evaluated with the same state on the same day.
2. **Matching.** For each guarded field with vendor value v, and each stored restated value L_j (filed on day d_j; public from d_j + 1):
   - **future match:** some j has d_j + 1 > today (the version's first-seen day) and |v / L_j − 1| ≤ 0.5%;
   - **known match:** some i has d_i + 1 ≤ today and |v / L_i − 1| ≤ 0.5% (the frozen Data v2.1 tolerance).
   - **The version is BLOCKED (v3)** if any guarded field has a future match and no known match. It then carries a value that was filed only later: a later restatement silently replacing what was actually known.
   - **Why the original value is not stored:** a vendor value within 0.5% of both the original and a restated value would need the two to be within about 1.0% of each other. Stored restated values differ from the original by more than 1.5%, so this cannot happen.
   - **Not guarded:** restatements of 1.5% or less (immaterial), and fiscal-year totals (reconciliation only, section 2).
3. **The v3 view of a security on day T** (what H029 reads):
   - **History:** for each period, the latest-filed fed version that is visible on T (available ≤ T) and **not** v3-blocked. A period whose every visible version is blocked is **absent**: its windows break and the dependent signals are missing. Nothing is imputed.
   - **Current report:** the visible full record with the latest period end in that history. It must be at most 200 days old (frozen freshness rule).
   - **Implementation:**
     - only periods that have guard-v3 timelines can ever differ from v2.1, so only their fed versions are retained (bounded memory);
     - every other period is read from the v2.1 store unchanged;
     - the v2.1 store itself is never changed.
4. **Provenance categories recorded for every fed version and guarded field** (aggregate counts by field and year):
   - `no_restatement` (no timeline);
   - `restated_known` (matches a restated value already public);
   - `blocked_future` (future match, no known match);
   - `unmatched` (a timeline exists, but v matches no restated value: the original or a vendor definition).

## 5. H029 signal constructions on the v3 view (the P14-CP1 canonical forms; owner D229 variants)

**Notation:**
- q0 is the current v3 report, at most 200 days old.
- qk is the report k fiscal quarters earlier on one consecutive chain of visible full reports (gaps of 80–100 days).
- X_k is the True TTM of base X for the window ending at qk. It uses the frozen `PITStore.ttm_detail` rules: four consecutive visible quarters with quarterly values, and the fiscal-year reconciliation within 1%. These are the exact constructions of `qr_h029a.Window` / `ttm_at`, applied to the v3 view.
- TA_k is the total-assets snapshot of qk.
- "+" = improvement.

| Id | Family | Formula (oriented) | Span | Missing when |
|---|---|---|---|---|
| F1 | Revenue growth acceleration: same-quarter year-on-year (owner: quarterly YoY acceleration; P14-CP1 F1-Q) | (r0/r4 − 1) − (r1/r5 − 1), r = quarterly revenue | 6 consecutive quarters | any of r0, r1, r4, r5 missing or ≤ 0 |
| F2 | Gross margin improvement, same period one year earlier (TTM; no quarter-on-quarter seasonality) | GP0/R0 − GP4/R4 | 8 | any TTM missing; R0 ≤ 0 or R4 ≤ 0 |
| F4 | Operating cash flow / assets improvement (TTM: the reconciliation proves the four quarterly cash flows sum to the fiscal-year total, so a year-to-date value is never used as a quarter) | OCF0/TA0 − OCF4/TA4 | 8 | any TTM or snapshot missing; TA0 ≤ 0 or TA4 ≤ 0 |
| F5 | ROA improvement (TTM net income) | NI0/TA0 − NI4/TA4 | 8 | same |
| F7 | Share dilution, inverted (less dilution / buybacks = +) | −(S0/S1 − 1). S0 = the latest usable SEC cover count (filed + 1 ≤ T, cover date ≤ 135 days old). S1 = the count whose cover date is closest to S0's minus 365 days (±45). Both are restated to T's share basis with splits dated ≤ T (frozen D111 rule). | two counts about a year apart | S0 or S1 missing or ≤ 0; **corrupted**: S0/S1 < 0.1 or > 10 (a tenfold change in one year is not share issuance; unit or split error) |
| F8 | Asset turnover improvement | R0/TA0 − R4/TA4 | 8 | any TTM or snapshot missing; TA0 ≤ 0 or TA4 ≤ 0 |

**Further rules:**
- **Denominators:** invalid (≤ 0 or missing) → the value is **missing**. Never zero, never imputed.
- **Outliers:** nothing is winsorised or clipped. H029 uses cross-sectional ranks. The only removals are the mathematically invalid denominators above and the F7 corruption rule.
- **Excluded:** F3 (operating margin) and F6 (debt / assets) are not computed for H029. They are not replaced.

## 6. Universe and coverage

- **U_H029(t):**
  - start from the Data v2.1 eligible universe at review t (X801 `mon[t]`, SEC-repaired members included);
  - exclude companies whose SEC SIC at the review is 6000–6999 (financials and REITs, the Score v1 H1 rule used for H028's population);
  - exclude companies **without** a SEC SIC at the review (Score v1 H1; the FF12 sector cap needs a sector).
  - Unlike P14-CP1's U_NF, no-SIC stocks are excluded; this is disclosed.
- **Coverage(t):** the share of U_H029(t) with at least 5 of the 6 signals valid.
- **Coverage gate:**
  - the **median over the 131 reviews 2011-01 → 2021-11** must be ≥ 70%;
  - the 2015–2021 median is reported alongside.
- **Per-family coverage:** the share of U_H029(t) with a valid value; median over the 131 reviews.

## 7. SEC validation (X803; aggregates only)

1. **Sample** (deterministic; fixed before any comparison):
   - **Candidates:** registrants of the Data v2.1 filing table with at least one SEC SIC row in the Data v2.1 identity table.
   - **Sector:** the FF12 sector of the registrant's latest SIC row dated ≤ 2021-12-31 (`qr_xs_diag.ff12`). Financials (SIC 6000–6999) are excluded.
   - **Size proxy** (for being in the ≥ $2B universe; SEC data only): maximum SEC `Assets` or `EntityPublicFloat` from 2010–2021 ≥ $1B.
   - **Selection:** per non-financial FF12 sector, the first 25 registrants by SHA-256(`"P14CP2-SEC-sample|" + CIK`). That gives at most 11 × 25 = 275 registrants.
   - **Realised sample:** their U_H029 stock-months at the 131 reviews (identity: frozen `Identity.m2`).
2. **SEC reference** (offline, public SEC data only), per sample registrant, as a step function of the decision day D:
   - **SEC anchor q0:** the latest Data v2.1 filing-table period whose original 10-Q / 10-K was filed with filed + 1 ≤ D and D − p ≤ 200 days. The chain is consecutive SEC periods (gaps of 80–100 days).
   - **Values as known on D:** section 3.3 quarterly values; TTM = the sum of four as-known quarters (no fiscal-year reconciliation needed); total assets.
   - **Computed:** F1, F2, F4, F5, F8 with the section 5 formulas and validity rules, plus the anchor raw values (quarterly revenue, the TTMs of revenue / gross profit / net income / operating cash flow, total assets).
   - F7 needs no SEC-side reference: the vendor side already uses the SEC cover counts.
3. **Comparison at every review, for each sample stock-month** (counts only):
   - per signal: both valid / vendor only / SEC only / neither;
   - among both valid: anchor agreement (|period-end difference| ≤ 6 days) or not;
   - raw-field agreement at agreeing anchors: match (≤ 0.5%), minor (≤ 2%), moderate (≤ 10%), major (> 10%), or sign differs;
   - **rank impact:** Δ = |P(vendor value) − P(SEC value)|. Both percentiles are taken in the **same** vendor cross-section of that signal in U_H029(t), where P is the empirical CDF. Δ is reported by period (2011–14, 2015–17, 2018–21) and FF12 sector;
   - **composite:** the owner's H029 score (D229 section 18). Each signal is mapped to its centred percentile in U_H029(t) among valid values (`qr_h026.centred_percentile`: 2·(average rank − 1)/(n − 1) − 1, in [−1, +1]). The score is the mean over the stock's valid signals, and needs at least 5 of 6.
     - It is computed twice: with the stock's vendor values, and with its SEC values substituted for F1, F2, F4, F5 and F8. The SEC value's percentile is taken in the vendor cross-section; F7 and every other stock are unchanged.
     - Δ_comp = |percentile of the vendor score − percentile of the SEC-substituted score|, both in the vendor score cross-section.
4. **Materiality gate (pre-registered):**
   - for each of F1, F2, F4, F5 and F8, among both-valid, anchor-agreeing sample stock-months: **P(Δ > 0.20) ≤ 5%**;
   - for the composite, among stock-months with a score on both sides: **P(Δ_comp > 0.20) ≤ 5%**;
   - mismatches are not resolved by hand; every mismatch counts at its measured rank impact;
   - **sample sufficiency:** at least 300 both-valid, anchor-agreeing stock-months per signal in each of the three periods, and at least 8 FF12 sectors with at least 100 such stock-months. Otherwise the validation is **INCONCLUSIVE**, which counts as failure.
5. **Anchor timing (PIT check):** a vendor anchor whose SEC original filing + 1 is after the decision day must never occur (M2). The count must be 0.
6. **Restatement materiality** (descriptive, offline, SEC only): for the same sample and decision days, signals from the SEC values as known on D vs the **latest** SEC values (filed ≤ 2021-12-31). This shows how large the look-ahead would be if restatements were not guarded. It is not a gate.

## 8. F7 split comparability test (X803; aggregates only)

- **Population:** U_H029 stock-months with a valid F7 for which X801 recorded a QuantConnect-native market cap and price (X801 `val`, same CIK) at review t and at the review 12 months earlier (t12).
- **Implied QuantConnect share ratio:**
  - N = market cap / raw price at each of t and t12;
  - R_qc = N_t / (N_t12 × Π m), with m = 1 / split factor for every split with ex-date in (t12's selection day, t's selection day].
- **Disagreement:** |ln(S0_adj / S1_adj) − ln(R_qc)| > ln(1.10).
- **Split window:** any split with ex-date in (min(S1 cover date, t12 selection day), t's selection day]. Other stock-months are non-split.
- **Gate:**
  - at least 30 split-window stock-months, and **D_split ≤ D_non-split + 0.05** (D = share disagreeing);
  - otherwise **F7 is not split-comparable → DATA V3 FAIL for F7** (owner section 6).
- **Reported:** the share with |F7| > 0.4 in each group; the share at the corruption bounds.

## 9. PIT checks (each must be 0)

- The frozen X801 audit counters:
  - fed before SEC filing;
  - fed before first seen;
  - future identity row;
  - fed after guard trigger;
  - stale / not-yet-public share counts;
  - records older than 200 days.
- v3-view records with availability after the decision day.
- F7 filings used before filed + 1.
- Splits used with ex-date after the decision day.
- Guard-v3 reference entries filed after 2021-12-31.
- Vendor anchors ahead of their SEC original filing (section 7.5).
- Any history row after 2021-12-31.

## 10. Data v3 gate

- **A family is usable** if:
  - (i) its median monthly coverage in U_H029 is ≥ 50% (the P14-CP1 UNUSABLE boundary);
  - (ii) it passes its section 7.4 materiality gate (F1, F2, F4, F5, F8), or section 8 (F7);
  - (iii) every section 9 check is 0.
- **Outcomes:**
  - **DATA V3 PASS:** all six families usable, the composite materiality gate passes, sample sufficiency holds, and coverage (section 6) ≥ 70%.
  - **STOP FOR OWNER REVIEW:** exactly five families usable, everything else passing. No five-feature alternative is built (owner section 12).
  - **DATA V3 FAIL:** otherwise. This covers:
    - four or fewer usable families;
    - a failed composite materiality gate;
    - INCONCLUSIVE validation;
    - coverage below 70%;
    - any PIT check ≠ 0.
  - If FAIL: STOP; H029 / H030 are not run.
- **QuantConnect compliance:** if QuantConnect rejects X803 at build, or stops it, the in-cloud validation cannot be done. Data v3 cannot PASS → STOP and report to the owner. No workaround is attempted (D185).

## 11. Data v2.1 differences recorded (no H028 change)

- Versions blocked by guard v3, by field and year.
- Provenance categories (section 4.4).
- Per signal: U_H029 stock-months whose value differs between the v2.1 store and the v3 view, and those valid in one but not the other.
- Change in ≥ 5/6 coverage.

## 12. Runs, digests and freeze

- **One audit run:** E803-01 (X803 mode `audit`; QuantConnect default build, recorded).
  - Window 2011-01-03 → 2021-12-31, warm-up from 2008-07-01, 0 orders.
  - Universe digests must equal E028-01 / E802-01 (131/131).
- **Digests:** per review, the SHA-256 of the H029 input panel (ids and the six signal values, 12 significant digits). The H029 host must reproduce it exactly (cross-host determinism).
- **Freeze:** `research/phase14/data_v3/data_freeze_v3.json` holds:
  - the table hash, code hashes (`qr_v3.py`, builder, X803) and spec hash;
  - the audit-result hash and the panel digests;
  - the gate outcome.
  - It is pinned in `qresearch.datafreeze_v3` with a test.
- **After the freeze:** Data v3 is never changed because of H029 / H030 results. A genuine bug means STOP, document, ask the owner, and issue v4.
- **Checkpoint:** P14-CP2 "Fundamental PIT Data v3 Hardening" before any strategy return is calculated.
