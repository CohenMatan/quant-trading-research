# OC-2 Stage 1 — Data v3 / PIT / fiscal-period integrity audit: frozen protocol

**Owner decision:** D248 (`docs/owner/2026-10-18_oc2_pit_integrity_synthetic_calibration.md`, sections 2–7).
**Committed before:** the audit script produces any aggregate. Its SHA-256 is recorded in the output and checked by `tests/test_oc2_stage1.py`. Any change after the first aggregate needs a new owner decision.

**Nature:** NON-RETURN and NO-VALUE.
- No F5 value, net-income or total-assets amount, ratio, percentile, ranking, price or return is computed, read into a statistic or inspected.
- Only accounting **metadata** is used: period-end dates, filing dates, form types, XBRL fact start / end dates and filing dates (fact *existence and duration*), registrant identity rows, SIC codes and universe membership.
- Offline only:
  - cache-only SEC client with networking disabled;
  - every SEC row filed after 2021-12-31 is dropped at load;
  - no QuantConnect run, no new data, no Holdout.

## 1. The object audited: the frozen F5 definition

Sources:
- Data v3 spec §5 (`research/phase14/data_v3/DATA_V3_spec.md`);
- the frozen code `src/qresearch/lean/qr_v3.py::signals`, `qr_h029a.Window`, `qr_h029a.ttm_at` and `qr_fundamentals.PITStore.ttm_detail`;
- the SEC-side reference construction `qresearch.data_v3.sec_signals`.

**Part A (static audit):** before any data step, Claude writes down the definition read from that code. Items:
1. formula;
2. fields;
3. TTM construction;
4. comparison period;
5. missing / denominator rules;
6. availability;
7. guards;
8. differences from the OC-CP2 description.

**If the code, the spec and OC-CP2 disagree on any item, the audit STOPS** (owner §2) and the inconsistency is reported. Nothing is modified.

## 2. Population (fixed)

- **Reviews:** the 131 frozen review days 2011-01 … 2021-11 (`data_v3.review_days`), decision day D = the selection day.
- **Primary window:** 2012-02 … 2021-11 (118 reviews; OC-CP2's rule). 2011-01 … 2012-01 is reported as context only.
- **Universe:** the E981-01 point-in-time eligible universe (Data v1 denominator: ≥ $2B, price ≥ $5, ADV20 ≥ $5M). This is the only eligible-universe membership available offline, as in LH-CP1–CP4 (disclosed).
- **Identity and SIC:** the frozen Data v2.1 identity rows as known on D (`Ident.at`, as in the Stage C audit).
- **Exclusions:**
  - financials (SIC 6000–6999), as in U_H029;
  - stock-months without CIK or SIC, counted as `no_identity` / `no_sic`.
- **Audit population:** identified non-financial stock-months.

## 3. SEC-side F5 structure (exactly the Data v3 SEC reference rules)

For each audit stock-month and its CIK:
- **Visible originals:** `data_v3.originals` of the Data v2.1 filing table (original 10-Q / 10-K / 10-KT; amendments excluded), with filed + 1 ≤ D.
- **Anchor p0:** the latest visible period, at most 200 days before D.
- **Chain:** `data_v3.chain_back(vis, i0, 8)`, i.e. 8 consecutive periods with gaps of 80–100 days.

**Missing reasons, first match in this order:**
1. `no_filing_table`;
2. `no_fresh_anchor`;
3. `short_history` (fewer than 8 visible periods);
4. `gap_short` (some gap < 80 days within the 8);
5. `gap_long` (some gap > 100 days).

**Complete chain** = 8 periods p0 … p7. **p8** = the next older visible period, if consecutive (80–100 days before p7).

## 4. Comparability checks on complete chains (metadata only)

| Code | Check | Definition |
|---|---|---|
| L0 | Current TTM window length | p0 − p4 days; **regular** if \|L0 − 365.25\| ≤ 8 (calendar, 52-week and 53-week years) |
| L4 | Prior TTM window length | p4 − p8 when p8 is consecutive; regular as above; `unmeasured` otherwise |
| W53 | 52 / 53-week mismatch | both measured and \|L0 − L4\| ≥ 5 days (one 53-week year); a bounded scale effect, not a validity failure |
| AP | Annual-report positions | positions k ∈ 0 … 7 whose original form class is annual (10-K / 10-KT). **Regular** = exactly two, 4 positions apart. Otherwise `annual_break` (a quarter-aligned fiscal-year change, or a missing / misclassified form) |
| TF | Transition form in span | a 10-KT or 10-QT in the CIK's submissions, filed ≤ D − 1, with report date in [p7 − 100 d, p0] |
| FYE | Fiscal-year-end code change | the XBRL-index fye codes of periods in the span differ. **Non-gating:** LH-CP2 showed these codes are mostly metadata noise |
| DUR | Quarterly net-income duration | for each of p0 … p7, the Data v3 `q_known` method decided from fact dates only (facts filed ≤ D − 1; `sec_pit.TAGS['net_income']`; duration classes of `sec_pit.dur_class`): `direct` (a 3-month fact), `ytd` (a class-c fact minus a class c−1 fact with the same start ± 7 days ending 60–120 days earlier) or `none`. **Verified** = all 8 `direct` or `ytd`. A `ytd` of class 4 = a derived fourth quarter (counted) |
| TA | Total-assets instants | an `Assets` instant fact within ± 3 days of p0 and of p4, filed ≤ D − 1. Reported alongside DUR |
| ID | Identity within span | the CIK as known on the filing day of p7 (`Ident.at`) equals the CIK on D; otherwise `id_change` (or `id_unknown` when no row exists then) |
| PIT | Point-in-time | every chain period's original filed + 1 ≤ D (must be 0 violations by construction; checked). Late filing: a chain period filed after a later chain period (out of order), counted |
| AMD | Amendment-only period | a period near p7 … p0 (± 6 days) that exists only as an amendment in the filing table (it breaks the SEC chain). Counted on all stock-months with a fresh anchor |

**Classes of complete chains** (first match):
1. **NON-COMPARABLE RISK:** L0 irregular, or L4 measured and irregular, or ID = `id_change`.
2. **FY-CHANGE, WINDOW-VALID:** not class 1, and AP = `annual_break` or TF present. Both twelve-month windows are still consecutive-quarter windows of regular length. The frozen in-host fiscal-year reconciliation may make the signal missing (fail-safe).
3. **COMPARABLE-VERIFIED:** not 1–2; DUR verified and TA present at p0 and p4.
4. **COMPARABLE-UNVERIFIED:** not 1–2, but DUR or TA not verifiable from SEC facts (pre-XBRL or missing facts). The vendor quarterly values are then validated only by the frozen in-host fiscal-year reconciliation.

**Additional flags, not classes:** W53, FYE, ID = `id_unknown`, derived Q4, late filing.

## 5. Committed evidence re-read (no recomputation)

- **P14-CP2 / E803-01:**
  - every PIT check;
  - anchor agreement vendor vs SEC;
  - NI0 / TA0 raw-field agreement;
  - F5 availability and rank-move validation;
  - guard-v3 provenance for `net_income_q` and `total_assets`.
- **P14-CP1 / E802-01:** the F5-A monthly vendor-side coverage and breadth; the OC-CP2 window rule (`OC_CP2_power.py::window_from_coverage`).
- **Data v2.1 / E981-01:** monthly eligible counts (P14-CP1 `monthly_counts.all_eligible`) vs the offline E981-01 counts. Universe-definition differences are taken from P7-CP5e / P7-CP5f / D207.
- **Hashes recorded:**
  - the Data v3 manifest and the Data v2.1 manifest (`data_freeze_v3.json`, `data_freeze_v21.json`);
  - P14-CP1 / P14-CP2 audit JSONs;
  - the frozen code files of §1.

## 6. Population statistics for Stage 2 (non-return)

By review / year, on the audit population:
- complete-chain counts per month;
- the **anchor-refresh share** (the stock-month's p0 differs from its p0 at the previous review);
- the share of reviews falling in each calendar month of the filing cycle;
- the entry / exit share (the stock enters or leaves the complete-chain population between reviews);
- FF12 sector counts;
- missing-reason shares.

These feed the Stage 2 synthetic population (owner §8).

## 7. Gate (fixed before any aggregate)

Y = the years 2012 … 2021 (shares are computed on the primary-window reviews of each year).

| Gate | PASS condition | CONDITIONAL | FAIL |
|---|---|---|---|
| G-DEF | Part A finds no inconsistency | — | Any inconsistency → STOP (reported as FAIL — NOT SUPPORTED pending owner decision) |
| G-PIT | Offline PIT violations = 0 **and** every committed P14-CP2 PIT check = 0 | — | Any violation |
| G-RISK | NON-COMPARABLE RISK ≤ 2.0% of complete chains in every year of Y | > 2.0% and ≤ 5.0% in some year | > 5.0% in some year |
| G-COV | SEC-side complete-chain share of the audit population ≥ 60% in every year of Y | ≥ 50% but < 60% in some year | < 50% in some year |
| G-VER | (COMPARABLE-VERIFIED + verified FY-CHANGE) ≥ 70% of complete chains in every year of Y | < 70% in some year | — |
| G-AGR | Committed vendor-vs-SEC anchor agreement ≥ 90% **and** NI0 / TA0 match shares ≥ 90% of non-missing | < 90% | — |
| G-WIN | The OC-CP2 window rule on committed P14-CP1 F5-A coverage yields 2012-02 | Any other month (the window then follows the rule; reported) | — |

**Classification:**
- **PASS — PIT-SAFE AND SUFFICIENT** only if every gate passes.
- **FAIL — NOT SUPPORTED** if any FAIL condition holds.
- **CONDITIONAL** otherwise.

**Rules for the result:**
- **Thresholds are never changed after an aggregate exists.**
- A CONDITIONAL or FAIL is committed as found, and the audit STOPS for the owner (owner §7).
- A sub-window that would pass is reported only as information. It never re-classifies the gate.

## 8. Outputs

- `OC2_S1_audit.json` (aggregates only);
- `OC2_S1_static.md` (Part A);
- the checkpoint (`docs/checkpoints/OC_CP3_oc2_stage1_data_integrity.md`).

Nothing else is written.
