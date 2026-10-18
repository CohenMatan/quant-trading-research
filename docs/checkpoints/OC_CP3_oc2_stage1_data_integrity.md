# OC-CP3 — OC-2 Stage 1: Data v3 / PIT / Fiscal-Period Integrity Audit

**Owner decision:** D248, 2026-10-18 (`docs/owner/2026-10-18_oc2_pit_integrity_synthetic_calibration.md`).

**Frozen protocol:** `research/longhorizon/oc2/stage1/OC2_S1_protocol.md`, SHA-256 91da6f27…, committed in 819a7a1 **before any aggregate existed**.

**Other artifacts:**
- `OC2_S1_static.md` (Part A, the definition audit);
- `OC2_S1_audit.py` → `OC2_S1_audit.json` (the gate; script committed in 3e15eb4 before its first run);
- `OC2_S1_posthoc.py` → `OC2_S1_posthoc.json` (post-hoc, **non-gating**);
- `tests/test_oc2_stage1.py`.

**What was not done:**
- no F5 value, accounting amount, ratio, ranking, price or return was computed;
- no QuantConnect run, no purchase, no Holdout;
- fact values were never read: only dates, forms, durations and identity metadata.

**Result:** **PASS — PIT-SAFE AND SUFFICIENT.**
- All seven pre-registered gates pass.
- The 2012-02 → 2021-11 window (118 reviews) is supported.
- Under D248 this authorises Stage 2 (synthetic calibration only).

## In plain words

**The question.** Can the change in return on assets be measured correctly from our data, without fiscal-quarter labels, and without peeking at information that was not yet public? It can.

**Why fiscal labels do not matter here.** F5 compares two adjacent twelve-month windows. Each window is the sum of four consecutive quarters, so seasonal patterns cancel. A company that relabels its quarters keeps two valid twelve-month windows. OF-A's surprises needed labels because they compare the *same* quarter across years.

**What could still go wrong, and what we found.** On about 112,000 primary-window stock-months (102,000 with a complete eight-quarter SEC chain):
- **Window lengths.** Every measured twelve-month window is 364–371 days. None is irregular.
- **Fiscal-year changes and transition reports.** These touch 0.2–0.5% of usable stock-months, and both windows remain valid twelve-month windows there.
- **Quarter lengths.** Genuine three-month quarters are confirmed from SEC filings for 97% (2012) to 99.7% of usable stock-months.
- **Timing.** No point-in-time violation was found.
- **Agreement.** The vendor data agree with SEC filings on the reporting period in 96% of a committed sample, and on twelve-month net income in 94%.

**The limitations, disclosed.**
- **52 / 53-week years.** One window contains 53 weeks and the other 52 in 4–10% of stock-months a year. This inflates that window by about 1.9%: a small, bounded scale error.
- **Vendor-side gaps.** The vendor-side signal is missing for about 18% of stock-months that SEC data could support. These are failed checks, so the gaps are fail-safe, not errors. The usable cross-section is about 450 stocks a month in 2012, 540 in 2013 and 710–1,020 from 2014.
- **Skew of the missing stocks.** In 2011–2014 the missing stocks lean slightly towards retailers.

## 1. Verified state and authorisation

| Item | State |
|---|---|
| `main` | 081ee55 (merge of [PR #112](https://github.com/CohenMatan/quant-trading-research/pull/112)) |
| Latest owner decision | D247, so this approval is **D248** |
| Holdout | Sealed: `HOLDOUT_UNLOCK.md` absent; nothing after 2021-12-31 was read |
| Statuses | H028 REJECTED (frozen defensive research reference); H029 / H030 NOT EVALUABLE; OF-A unqualified, D245 unchanged; **OC-2 approved direction, not performance-tested**; no qualified strategy |
| Authorised | Stage 1 audit; Stage 2 synthetic calibration only on a Stage 1 PASS |

## 2. The exact frozen F5 definition (Part A, G-DEF PASS)

From the frozen code (`qr_v3.signals`, `qr_h029a.Window` / `ttm_at`, `qr_fundamentals.PITStore.ttm_detail`) and Data v3 spec §5.

**Formula:** **F5 = NI_TTM(q0) / TA(q0) − NI_TTM(q4) / TA(q4).**

**Construction:**
- **Anchor.** q0 is the current v3-view report, at most 200 days old.
- **Span.** q0 … q7 must be 8 consecutive full records with period-end gaps of 80–100 days. q4 is 4 records before q0.
- **TTM.** Each NI_TTM is the four consecutive quarterly vendor values ending at its record, on the net-income history. A fiscal-year-end record inside the window must have its fiscal year's four quarters sum to the vendor fiscal-year total within 1%, otherwise the TTM is missing.
- **Assets.** TA is the balance-sheet snapshot at q0 and at q4.

**Missing rules:**
- no fresh report;
- short or broken span;
- missing TTM, including a failed reconciliation;
- missing TA;
- TA ≤ 0.
- Losses are allowed. Nothing is imputed or winsorised.

**Availability and guards:**
- each vendor version is usable from max(first seen in QuantConnect, SEC original filing + 1 day), matched to the SEC period within ± 6 days;
- guard v3 blocks versions that carry later restatements of net income or total assets;
- a blocked period falls back to the latest earlier clean version, or is removed.

**Differences from OC-CP2:**
- OC-CP2 did not restate the 1% fiscal-year reconciliation. That is an omission in the description, not a different definition.
- The coverage figures OC-CP2 quoted were F5-A on the Data v2.1 store, before guard v3.
- No inconsistency was found, so the definition is unchanged.

**Source hashes** (SHA-256, first 16 characters; full values in `OC2_S1_audit.json`):

| File | Hash |
|---|---|
| Data v3 spec | b4b8aa9b1c212e98 |
| Data v3 manifest | 601d00623e97696b |
| Data v2.1 manifest | ef0a7a66f5ff1e74 |
| `qr_v3.py` | 40bcf98d3aa62f62 |
| `qr_h029a.py` | 3cff1e0361fdae6b |
| `qr_fundamentals.py` | 0774343f24820ce4 |
| `data_v3.py` | 6495dc021d692ef0 |

## 3. Does F5 need comparable fiscal quarters, and does Data v3 ensure it?

**What F5 needs:**
- (a) genuine roughly three-month quarterly flows;
- (b) four contiguous quarters per window;
- (c) windows of about twelve months;
- (d) adjacent windows;
- (e) one economic entity;
- (f) values public on the decision day.

**What F5 does not need:** matching fiscal-quarter *labels*. Each window sums four quarters, so seasonality cancels. This is the demonstrated distinction from OF-A's seasonal surprises.

| Risk (owner §4) | What the frozen rules do | What the audit measured (SEC side, complete chains) |
|---|---|---|
| Genuine fiscal-year change | A non-quarter-aligned change breaks the 80–100-day gaps, so the signal is missing. A quarter-aligned change keeps two valid twelve-month windows; the fiscal-year reconciliation may then make the TTM missing (fail-safe) | Annual-report position breaks 0.04–0.31%; class FY-CHANGE, WINDOW-VALID 0.20–0.51% a year. Window lengths stay regular in all of them |
| 52 / 53-week years | Admitted (14-week quarters fit the 80–100-day gaps) | All windows 364–371 days: 79% calendar (365 / 366), 17% 364, 3.8% 371, 0.3% other regular, **0% irregular**. A 53-vs-52 mismatch between the two windows affects 4.4–10.4% of stock-months a year: a scale error of about 1.9% of one window's net income. **Bounded, not a validity failure; disclosed** |
| Irregular quarter durations | Gaps bound the window; durations are not checked directly | SEC net-income facts: about 95% direct three-month, 4.5–5.5% derived Q4 (fiscal year minus nine months; 7.4% in 2021), about 0.02% unresolvable. Durations are enforced by the frozen classes (80–100 / 170–190 / 260–285 / 350–380 days) |
| Missing reporting quarters | A gap > 100 days breaks the span | `gap_long` 0.8–2.2% of stock-months: missing, never bridged |
| Transition reports (10-KT / 10-QT) | As fiscal-year changes | Present in the span for 0.20–0.51% a year; all in the WINDOW-VALID class |
| Inconsistent fiscal-year-end metadata | Never used | XBRL fye-code changes in 7.6–16.6% of spans (non-gating). LH-CP2 showed these are mostly metadata noise, and F5 does not use them |
| Misidentified periods | Vendor period matched to the SEC period within ± 6 days | Committed: anchor agreement vendor vs SEC 95.9%. Mismatches are vendor-missing (2.1%) or vendor-older (1.3%) anchors: stale or missing, not mislabelled |
| Fourth quarter from annual and year-to-date figures | The 1% fiscal-year reconciliation validates the derived Q4 of the reconciled year | About 5% of quarters are derived Q4s, and 18.7–22.6% of spans contain one. They rise to 40% of 2021 spans: after the SEC dropped the quarterly-data requirement (Item 302, effective 2021), more 10-Ks report only annual figures |
| Balance-sheet snapshot vs quarterly flow | TA at q0 / q4 period ends; the flows end on the same dates | Assets instants at both dates are part of the verified share (≥ 96.9% a year). End-of-period assets is the frozen definitional choice. An acquisition late in a year raises TA before its earnings accrue (economic, not an error) |
| SEC registrant identity changes | Each vendor version is matched to one registrant's filing periods (identity M2). Predecessor periods do not match and are not fed (`fed_no_match` 122 of 116,639 versions) | SEC chains cannot mix registrants by construction. The Data v2.1 identity table holds one CIK per security for all but 4 of 3,958 securities, so "identity change inside the span" measures 0 **structurally**; this is not independent evidence. Identity unknown at the p7 filing date: 0.12–1.26% (non-gating) |
| Restatements / vendor corrections | Guard v3: versions carrying a not-yet-public restatement are blocked (net income 444, total assets 0). Known restatements are used as known (PIT-correct) | Committed P14-CP2 provenance (net income): no restatement 107,103; restated-known 206; blocked-future 444; unmatched 8,501 |

**Classification of complete chains, 2012–2021:**

| Class | Share |
|---|---|
| NON-COMPARABLE RISK | **0.00–0.03%** a year (gate ≤ 2%) |
| FY-CHANGE, WINDOW-VALID | 0.20–0.51% |
| COMPARABLE-VERIFIED | 96.7% (2012) → 98.7–99.5% |
| COMPARABLE-UNVERIFIED | 3.0% (2012) → 0.3–0.9%: quarters before XBRL, validated only by the in-host reconciliation |

## 4. Point-in-time constraints

- **Offline.** 0 chain periods used before their original filing + 1 day. No chain uses a period filed out of order (≤ 0.09%, in 2016–2017 only). Nothing filed after 2021-12-31 was loaded.
- **Committed P14-CP2 / E803-01 checks, all 0:**
  - `fed_before_sec_filing`, `fed_before_first_seen`, `vendor_anchor_ahead_of_sec`;
  - `view_future_records`, `record_older_than_200d`;
  - `guard_entries_after_2021`, `fed_after_guard_trigger`, `future_identity_row`.
- **First permitted trading session.** The selection day is the calendar day after the review session, and trading is at the next session's open (frozen).
- **Dependency that cannot be verified offline:** the vendor first-seen day (QuantConnect). It rests on the committed in-cloud checks above. No new QuantConnect run was needed or made.

## 5. Coverage 2012–2021 (no values; counts and shares only)

**Population (E981-01 universe, 131 reviews):**
- 159,717 eligible stock-months;
- financials 33,544;
- no identity 4,172; no SIC 1,008;
- **audit population 120,993**.

**Coverage and missing reasons by year:**

| Year | Audit stock-months | SEC-side complete chain | Main missing reasons | Vendor-side valid F5 per review (committed P14-CP1 F5-A × U_NF) |
|---|---|---|---|---|
| 2011 (context) | 8,299 | 91.7% | gap_short 4.8% | — |
| 2012 (Feb–Dec) | 7,899 | 91.5% | short history 3.5%, gap_short 2.7% | 447 (429–461) |
| 2013 | 9,946 | 91.1% | short history 4.4% | 543 (468–588) |
| 2014 | 11,037 | 90.5% | short history 5.2% | 710 |
| 2015 | 11,082 | 91.0% | short history 5.2% | 751 |
| 2016 | 10,600 | 92.1% | short history 3.9% | 741 |
| 2017 | 11,474 | 92.1% | short history 4.1% | 766 |
| 2018 | 11,956 | 91.8% | short history 4.6% | 801 |
| 2019 | 11,925 | 92.2% | short history 4.7% | 839 |
| 2020 | 12,114 | 91.1% | short history 6.7% | 847 |
| 2021 | 13,957 | 88.8% | short history 9.5% (new listings) | 1,019 |

**Earliest usable decision month: 2012-02.** The OC-CP2 rule reproduces it: P14-CP1 F5-A coverage stays ≥ 60% from 2012-02. Valid monthly decision dates: **118**.

**Exclusion reasons, in order:**
- financial;
- no identity / SIC;
- no filing table / no fresh anchor;
- short history;
- gap < 80 or > 100 days;
- and, vendor side only: missing TTM (including a failed reconciliation), missing TA, or TA ≤ 0.

**Vendor vs SEC availability** (committed validation sample):
- the vendor F5 is missing for **17.8%** of SEC-valid stock-months;
- the SEC side is missing for 2.7% of vendor-valid ones;
- when both exist, rank moves > 0.20 occur in 0.44% / 0.25% / 0.07% (2011–14 / 2015–17 / 2018–21).

**Selection effect of vendor-side missingness** (committed P14-CP1 F5-A):
- in 2011–2014, missing stocks are slightly larger (log market cap +0.09) and lean to retail (Shops 16.5% vs 11.2% of valid);
- from 2015 the valid stocks are slightly larger (+0.17 to +0.30 log market cap);
- this is disclosed as a coverage tilt, not a PIT problem.

**Impact of conservatively excluding problem observations:**
- dropping NON-COMPARABLE RISK and FY-CHANGE chains removes ≤ 0.5% a year;
- additionally dropping unverified chains removes about 3% in 2012 and ≤ 1.0% later;
- additionally dropping 53/52 mismatches removes 4–10%.
- None of these is required by the gate. The 53/52 exclusion is offered to the owner as an option for the real test design (§7).

## 6. Data v1 vs Data v2.1 universe

- **The offline audit uses E981-01** (the Data v1 eligibility masks, ≥ $2B / $5 / $5M), the only membership available offline. The real OC-2 population is **Data v2.1 / U_H029**:
  - QuantConnect's current market caps, repaired by the D111 SEC cover-share method where missing (P7-CP5e);
  - extended SEC identity;
  - Data v2.1 rules to 2021-12-31 (D207; NEW_YEARS_MAPPING owner exception D213).
- **Mean eligible stocks per review, E981-01 vs Data v2.1:**

  | Year | E981-01 | Data v2.1 | E981-01 above v2.1 |
  |---|---|---|---|
  | 2011 | 922 | 872 | +5.7% |
  | 2012 | 932 | 889 | +4.8% |
  | 2013 | 1,072 | 1,024 | +4.6% |
  | 2014 | 1,198 | 1,149 | +4.2% |
  | 2015 | 1,224 | 1,180 | +3.7% |
  | 2016–2021 | — | — | within 2.3% |

  The early-year difference is mostly the companies whose market cap the new feed lacks; the D189 repair recovers 69% of them.
- **The audit's comparability findings are about accounting periods, so they carry over.** Its coverage counts are a close proxy, not the exact real population. The vendor-side counts in §5 are on Data v2.1.

## 7. Remaining uncertainty (disclosed, non-gating)

1. **Vendor-side missing reasons are not available offline.** The 18% vendor-missing share cannot be split into reconciliation failures vs vendor quarterly gaps without an in-cloud aggregate export, which is not authorised and not needed for the gate. Missing is fail-safe.
2. **53/52-week windows** (4–10% of stock-months a year) carry a scale error of about 1.9% of one window's net income. The real-test design should either accept this (and disclose it) or pre-register a 364/371-day normalisation; that would be a definitional change and needs an owner decision.
3. **2012–2013 vendor-side cross-sections are smaller** (about 450 and 540 a month). Stage 2 uses these counts.
4. **Identity is protected by construction** (one registrant per chain), not by an independent identity-change test.

## 8. Stage 1 gate (protocol §7)

| Gate | Result | Value |
|---|---|---|
| G-DEF | PASS | Code = spec = OC-CP2 |
| G-PIT | PASS | 0 offline violations; every committed check 0 |
| G-RISK | PASS | Maximum 0.03% (threshold 2%) |
| G-COV | PASS | Minimum 88.8% (threshold 60%) |
| G-VER | PASS | Minimum 96.9% (threshold 70%) |
| G-AGR | PASS | Anchor 95.9%, NI0 94.0%, TA0 99.9% (threshold 90%) |
| G-WIN | PASS | 2012-02 |

**Classification: PASS — PIT-SAFE AND SUFFICIENT.**
- Stage 2 (synthetic calibration only) proceeds under D248.
- Its protocol is frozen and hashed before any synthetic result. The population parameters it uses are in `OC2_S1_audit.json` → `stage2_population` and in `OC2_S1_posthoc.json`.

**Stage 2 population parameters (non-return):**
- 118 reviews;
- SEC-side complete chains 865 a review (641–1,172);
- vendor-side valid F5 447 → 1,019 a review;
- anchor refresh 33% a month on average, clustered at 75% / 62% / 58% / 55% in the February / May / August / November reviews and 7–16% in the other months;
- entries 2.9% and exits 2.4% a month;
- FF12 sector structure by year.
