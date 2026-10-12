# P14-CP2 — Fundamental PIT Data v3 Hardening

**Result: DATA V3 PASS.** All six H029 families are usable and point-in-time safe. Data v3 is frozen.

**Owner decision:** D229 (`docs/owner/2026-10-12_p14_h029_h030_plan.md`, Part A).

**Order of work:**
- **Spec:** pre-registered in `research/phase14/data_v3/DATA_V3_spec.md`, commit a43d706, before any build.
- **Build:** offline from public SEC data (commit c5b3b21).
- **Audit:** ONE run, E803-01.
- **Gate:** applied by `research/phase14/cp2/P14_CP2_analysis.py`, committed before the run.

**Strategy returns:** none was calculated. No H029 / H030 score, portfolio or null world exists yet.

**Holdout:** 2022-01-01 → 2026-08-31 is sealed. Nothing after 2021-12-31 was requested.

## 1. What Data v3 is

- **A new layer on top of the unchanged Data v2.1.**
  - The frozen X801 host is uploaded byte-identical, and every Data v2.1 rule is unchanged.
  - The v2.1 point-in-time store receives exactly the same versions as before, so H028's data, scores and results are untouched.
- **H029 reads a separate "v3 view".** It is the v2.1 history with one difference: a vendor report version is removed if it carries a restated SEC value that was not yet public when the version first appeared.
- **Where it differs from v2.1, the difference is recorded** (section 6). H028 is never modified.

## 2. Manifest

| Item | Value |
|---|---|
| Manifest | `research/phase14/data_v3/data_freeze_v3.json`, SHA-256 `601d0062…`, pinned in `qresearch.datafreeze_v3` (test `tests/test_data_freeze_v3.py`) |
| Builds on | Data v2.1 manifest `ef0a7a66…` (owner exception D213), unchanged |
| Guard-v3 table | `qr_data_v3_00..03` (4 project files, 242,098 characters); raw SHA-256 `d4e1065b…`; 45,450 restated values; 2,931 of 3,941 registrants; 141,451 periods scanned |
| SEC validation reference | `qr_v3val_00..05` (audit host only); raw SHA-256 `2dbec426…`; 275 registrants (25 per non-financial FF12 sector) |
| Deterministic build | A second full rebuild produced byte-identical tables |
| Run | E803-01 (X803 audit mode). QuantConnect backtest `6eb4f7a3…`. LEAN v2.5.0.0.**18179**: QuantConnect's default build, which moved from 18178 since P14-CP1; recorded, and universe digests unchanged. Commit c5b3b21. 862 s, 0 orders. Peak memory 5.74 GB (no price panel). 50 project files. |
| Universe | 131 / 131 review-eligibility digests equal E802-01 (and so E028-01) |
| H029 input-panel digests | 131 per-review digests in the manifest. The H029 host must reproduce them exactly. |

## 3. Field provenance and restatement handling

| Field | Use | Timing / availability | Restatement protection |
|---|---|---|---|
| Quarterly revenue | F1; True-TTM revenue (F2, F8) | Data v2.1 M2: max(first seen, original SEC filing + 1) | v2.1 guard (unchanged) + **guard v3** |
| Quarterly gross profit | TTM (F2) | same | **guard v3** (new) |
| Quarterly net income | TTM (F5) | same | **guard v3** (new) |
| Quarterly operating cash flow | TTM (F4) | same | **guard v3** (new) |
| Total assets | snapshots (F4, F5, F8) | same | v2.1 guard + **guard v3** |
| Fiscal-year totals | reconciliation only (1% True-TTM check) | same | the whole version is excluded if any guarded field is blocked |
| SEC cover-page shares | F7 | filing + 1, at most 135 days old | original filings only; a later filing cannot replace a count |

**How guard v3 is built:**
- **Timeline:** for every registrant and period it builds the SEC "as-known" value on every filing day, from facts filed on or before that day.
  - Cash-flow and fourth-quarter values come from year-to-date differences. A year-to-date value is never taken as a quarter.
- **What is stored:** later values that differ by more than 1.5% are stored as restatements, with their filing day.
- **Rule:** a vendor version is blocked if a value matches (within 0.5%) a restatement not yet public when the version was first seen, and matches no public one.

**Provenance of the 116,639 versions fed:**

| Field | No restatement | Restated value already public | Blocked (future value) | Timeline but no match |
|---|---|---|---|---|
| Revenue | 103,350 | 64 | **458** | 8,620 |
| Gross profit | 89,722 | 27 | **42** | 4,312 |
| Net income | 107,103 | 206 | **444** | 8,501 |
| Operating cash flow | 104,998 | 127 | **125** | 10,338 |
| Total assets | 114,948 | 52 | 0 | 1,377 |

- **Blocked versions:** 1,018 (0.9%), spread over 2009–2021.
- **Every blocked version was the only version of its period:** the vendor's first snapshot already held the later value. The v3 view therefore **removes** those periods (0 replaced, 0 newer replacements). No value is imputed.

## 4. SEC validation (stratified sample; rank materiality; all pre-registered)

**Sample:** 275 registrants, 25 per non-financial FF12 sector, chosen by a SHA-256 order among registrants with SEC total assets or public float ≥ $1B. Their U_H029 stock-months were compared at the 131 reviews.

**Anchor agreement:**
- 12,436 stock-months have the same latest quarter on both sides.
- 167 are vendor-older (the vendor was slower; still point-in-time safe).
- 266 have no vendor anchor.
- **0 vendor anchors were ahead of the SEC filing.**

**Rank impact** (share of both-valid, anchor-agreeing stock-months whose percentile moves by more than 0.20; gate ≤ 5%):

| Signal | n | 2011–14 | 2015–17 | 2018–21 | Pooled | Sectors ≥ 100 | Status |
|---|---|---|---|---|---|---|---|
| F1 | 10,487 | 4.1% | 3.7% | 3.0% | **3.5%** | 11 | PASS |
| F2 | 4,931 | 4.2% | 1.3% | 1.2% | **1.9%** | 9 | PASS |
| F4 | 9,715 | 0.4% | 1.9% | 1.8% | **1.5%** | 11 | PASS |
| F5 | 9,609 | 0.4% | 0.3% | 0.1% | **0.2%** | 11 | PASS |
| F8 | 9,000 | 2.2% | 1.7% | 1.5% | **1.7%** | 11 | PASS |
| Composite H029 score | 8,630 | 6.5% | 4.0% | 4.4% | **4.8%** | — | PASS (near the 5% limit) |

**Notes:**
- **Median rank moves** are 0.06–0.13 percentile points for each signal and 0.7–1.0 for the composite.
- **Sample sufficiency** holds: at least 1,100 per period per signal and at least 9 sectors with at least 100.
- **Raw-value agreement** at agreeing anchors (match = within 0.5%):

  | Field | Match rate |
  |---|---|
  | Total assets | 99.9% |
  | Quarterly revenue | 96% |
  | Operating cash flow TTM | 93% |
  | Net income TTM | 94% |
  | Revenue TTM | 94% |
  | Gross profit TTM | 96% (of pairs where both exist; the SEC side often has no `GrossProfit` tag) |

  Major differences (> 10%) are about 1–2% of each field.
- **2011–2014 composite (6.5%)** is above 5% on its own. The pre-registered gate is the pooled share, so this is disclosed, not a failure.

**Descriptive SEC-only study (what unguarded restatements would do):**
- Restated SEC values instead of as-known ones would move F1 / F8 percentiles by more than 0.20 for 4–6% of 2011–2017 sample stock-months, and F2 for up to 5%.
- This is the look-ahead risk that guard v3 closes.

## 5. F7 split comparability (pre-registered; PASS)

The SEC cover-count dilution was compared with QuantConnect's market-cap-implied share ratio over the same year, split-adjusted the same way.

| Group | n | Disagree by > 10% | |F7| > 0.4 |
|---|---|---|---|
| Split in the window | 2,029 | 6.4% | 7.0% |
| No split | 75,765 | 2.7% | 1.1% |

- **Gate:** at least 30 split-window stock-months, and D_split ≤ D_non-split + 0.05. Result: 6.4% ≤ 7.7% → **PASS**.
- **Corruption rule** (S0/S1 outside [0.1, 10]): it removed 459 stock-months.
- **Disclosed:** split windows still show more large F7 values than non-split windows (7.0% vs 1.1%). The rank transform limits their influence.

## 6. Coverage, PIT checks and differences from Data v2.1

**Universe:** U_H029 = the Data v2.1 eligible universe minus financials / REITs (SIC 6000–6999) and stocks without a SEC SIC. The median is 903 stocks per review.

| Signal | Median coverage, 131 reviews | 2011–14 | 2015–17 | 2018–21 |
|---|---|---|---|---|
| F1 | 86.2% | 73.5% | 88.1% | 86.5% |
| F2 | 74.1% | 55.0% | 75.0% | 76.2% |
| F4 | 81.1% | 63.4% | 83.3% | 82.1% |
| F5 | 78.6% | 62.8% | 81.7% | 80.6% |
| F7 | 86.1% | 85.7% | 88.1% | 84.2% |
| F8 | 77.2% | 60.6% | 78.4% | 78.8% |
| **≥ 5 of 6 (H029 score)** | **76.1%** (gate ≥ 70%) | 58.1% | 77.1% | 78.1% |

- **2015–2021 median for ≥ 5 of 6:** 77.6%. The early years are weaker; this is disclosed, and 2011–2014 is used for history only.
- **PIT checks: all 0.** They cover:
  - every frozen X801 counter;
  - v3-view records after the decision day;
  - vendor anchors ahead of SEC;
  - F7 filings not yet public;
  - newer replacements;
  - guard entries after 2021.
- **Differences from Data v2.1** (U_H029 stock-months, all 131 reviews):

  | Signal | Valid on v2.1 only (period removed) | Different value | Valid on v3 only |
  |---|---|---|---|
  | F1 | 2,325 | 182 | 7 |
  | F2 | 2,616 | 148 | 7 |
  | F4 | 2,982 | 172 | 19 |
  | F5 | 2,976 | 170 | 19 |
  | F8 | 2,730 | 160 | 7 |

  The "valid on v3 only" cases arise because a removed quarter can change which chain is current.

## 7. Signal formulas and missing-data rule (frozen in Data v3)

**Notation:** q0 is the current v3 report (at most 200 days old). Chains are consecutive quarters (gaps of 80–100 days). TTMs follow the frozen True-TTM rules (four quarters plus the 1% fiscal-year reconciliation).

| Id | Formula ("+" = improvement) | Missing when |
|---|---|---|
| F1 | (r0/r4 − 1) − (r1/r5 − 1), quarterly revenue | any of the four revenues missing or ≤ 0 |
| F2 | GP0/R0 − GP4/R4 (TTM) | any TTM missing; R ≤ 0 |
| F4 | OCF0/TA0 − OCF4/TA4 (TTM OCF) | missing; TA ≤ 0 |
| F5 | NI0/TA0 − NI4/TA4 (TTM net income) | missing; TA ≤ 0 |
| F7 | −(S0/S1 − 1), SEC cover counts, splits ≤ T | counts missing or ≤ 0; S0/S1 outside [0.1, 10] |
| F8 | R0/TA0 − R4/TA4 | missing; TA ≤ 0 |

- **Excluded:** F3 and F6 are not computed and not replaced.
- **No imputation, no zero-filling, no winsorisation.** H029 will rank each signal.
- **A score needs at least 5 of the 6 signals.**

## 8. Integrity summary

| Item | Value |
|---|---|
| New hypotheses / strategies / experiments | 0 / 0 (X803 is an infrastructure audit host) / 1 (E803-01) |
| Spec before build | a43d706 |
| Analysis before run | c5b3b21 |
| QuantConnect compliance | Accepted. Aggregates and digests only. |
| H028 | Unchanged. No refit; no H028 file touched. |
| Holdout | Sealed |

## 9. Next step (owner run order)

Data v3 PASSED, so the owner's order continues with step 7:
- write the H029 / H030 hypotheses and the frozen spec (gates N1–N5, C1–C7, null, assessment);
- tests, then the canary;
- 5,000 null worlds, plus a rerun of seeds 1–25;
- the adequacy check, then pin c_UP_H029 and c_INCREMENTAL_H030;
- ONE real development evaluation;
- P14-CP3, then STOP.

**Risk noted now:** QuantConnect's default build is now 18179. Before any null world is run, the H029 host's canary must reproduce the frozen H026 feature / response panel digests and the committed H028 result ($328,294.908). If it cannot, the run order stops and the owner is asked.
