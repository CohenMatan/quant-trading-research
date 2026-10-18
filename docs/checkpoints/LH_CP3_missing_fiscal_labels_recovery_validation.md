# LH-CP3 — Missing Fiscal Labels Recovery & Validation

**Owner decision:** D244, 2026-10-18 (`docs/owner/2026-10-18_lh_cp3_missing_fiscal_labels_recovery.md`).

**Scope:** SEC accounting-period metadata only, dated ≤ 2021-12-31. Offline first, then 120 targeted EDGAR header requests. No prices, no returns, no OF-A signals, no QuantConnect run and no Holdout.

**Final classification (mechanical, protocol §10): B — PARTIAL RECOVERY.** Stage C stays **C — NOT FEASIBLE** and LH-CP2 stays **C — INSUFFICIENT EVIDENCE**. Neither is changed.

## In plain words

LH-CP2 found that about 13% of the Stage C input histories had quarters with no fiscal-quarter label (Q1 / Q2 / Q3 / FY). Most of those quarters were filed before the company began machine-readable (XBRL) reporting.

LH-CP3 tried to recover those labels without look-ahead, in three steps:
1. look them up again in the SEC data already on disk;
2. rebuild them with two independent methods:
   - the order of the company's 10-Q and 10-K filings;
   - the company's own later XBRL filings, which present the old quarter as a prior-year comparative;
3. check the rebuilt labels against EDGAR headers of genuine old filings.

**Local recovery.** Only 11.7% of the missing labels could be recovered locally. The rest are genuinely pre-XBRL.

**Validation.** The combined rule only accepts a label when both methods agree. It was tested on companies whose real labels were hidden from it. When it gave a label, it was right 99.95% of the time, and every disagreement traced back to a mislabelled "true" label, not to the rule. On real pre-XBRL filings, the headers agreed with 93 of 94 rebuilt labels.

**What could not be tested.** The rule could not be shown to catch genuine fiscal-calendar changes: only 10 held-back companies had one in the hidden part of a test history, and the pre-registered minimum is 20. That, plus a resolution share of 88.4% against the 90% needed for class A, makes the result **B**.

**Coverage.**
- With **strictly verified** histories only, the 70% floor fails in 2013–2014 but **holds in every year 2015–2021** for C1, C2 and C6.
- Adding the validated reconstruction rescues 2014 and, for C1, 2013. C2 and C6 stay just below the floor in 2013 (68.7% / 68.5%).

## 1. Verified initial repository state

| Check | Result |
|---|---|
| `main` | Merge of [PR #108](https://github.com/CohenMatan/quant-trading-research/pull/108) (eb76015) |
| Working tree | Clean |
| Latest owner decision | D243 |
| Checkpoints read | LH-CP1 and LH-CP2 |
| Stage C protocol | SHA-256 ff97789b… (verified and still pinned in `tests/test_lh_stage_c.py`) |
| LH-CP2 protocol | SHA-256 f7cbac94… (verified and still pinned in `tests/test_lh_cp2.py`) |
| H028 | REJECTED |
| H029 / H030 | NOT EVALUABLE |
| `HOLDOUT_UNLOCK.md` | Does not exist |

## 2. Owner decision and authorised scope

The message is recorded verbatim (D244).

- **Allowed:**
  - local SEC metadata;
  - recovery from cached submissions;
  - ≤ 150 EDGAR header requests to `www.sec.gov` at ≤ 2 per second, using the existing authorised contact;
  - audit scripts, tests and aggregates.
- **Prohibited:**
  - any filing or data after 2021-12-31, and the Holdout;
  - prices, returns, signals or rankings; QuantConnect; backtests; Stage B;
  - changes to H028, Ridge, Data v2.1 or Data v3, or to the LH-CP1 / LH-CP2 results;
  - P-assume as a default; H031; purchases.

## 3. Historical classifications preserved

- **LH-CP1 Stage C:** C — NOT FEASIBLE. Protocol, hash and artifacts untouched.
- **LH-CP2:** C — INSUFFICIENT EVIDENCE. Protocol, hash and artifacts untouched.
- **Inputs reused unchanged:** LH-CP2's figures, i.e. the 12,669 label-unknown C1-complete stock-months (13.36% of 94,836).
- **P2 rebuild:** reproduced the Stage C coverage exactly (stop rule passed in Part A).

## 4. Local data sources and hashes

| Source | Identifier |
|---|---|
| SEC cache `data/sec_cache` (companyfacts + submissions; outside Git) | 13,075 `data.sec.gov` files |
| `data/sec_derived/xbrl_filings.json.gz` | 0f9dff22… |
| Data v2.1 freeze manifest | ef0a7a66… (unchanged) |
| Stage C population | E981-01 (Data v1) eligible universe |
| LH-CP3 protocol | 38d790e5… |
| Addendum 1 | 4fbd4da7… |
| Frozen rules `lh_cp3_rules.py` | 9a72c5c8… |
| Manifest | ce09012e… |
| Development JSON | 5fa7375a… |
| Held-back JSON | 9292308d… |
| Final JSON | 9153240b… |

**Denominator.** The denominator is the **E981-01 (Data v1) non-financial eligible universe**. The Data v2.1 per-stock-month universe was never exported. This disclosed limitation is the same as in LH-CP1 and LH-CP2.

## 5. Network source restrictions

- **Host:** only `https://www.sec.gov/Archives/edgar/data/<cik>/<accession>/<accession>.hdr.sgml`, which are header-only files.
- **Not used:** bulk downloads, crawling, other providers and search engines.
- **Throttle:** minimum interval 0.6 s.
- **Budget:** 150 requests, counting retries.
- **Blocking:** a 403 stops the run.
- **User-Agent:** carries the owner-authorised contact, read at run time from the existing configuration. It is never written to the repository or the log; an automated check confirms the address appears nowhere in the repository.

## 6. Cut-off enforcement tests

`tests/test_lh_cp3.py`, all passing. The tests cover:
- **The URL builder.** It refuses a URL for any accession that is not in the committed manifest, is filed after 2021-12-31, is an amendment, or has a mismatched CIK. Every manifest row passes it.
- **The header parser.** It checks the filing date and the accession before reading any other field. It withholds the company block (fiscal-year end) when the header was changed after the cut-off. It never reads the body after `</SEC-HEADER>`. Both header layouts are tested: the text layout and the `.hdr.sgml` SGML layout.
- **Local metadata.** The registrant metadata loader shows no date after the cut-off and makes 0 network calls.
- **Outputs.** All LH-CP3 outputs pass `assert_no_post_cutoff`. The only exception is the request log, which records 2026 retrieval times — run metadata, not filing data.

The latest filing date in the manifest is 2014-08-12. All 120 headers were filed ≤ 2021-12-31, and none was changed after the cut-off.

## 7. Frozen reconstruction protocol and hash

The protocol `research/longhorizon/cp3/LH_CP3_protocol.md` (SHA-256 38d790e5…) was committed in e68414f, before any aggregate.

**Label tiers**

| Tier | Meaning |
|---|---|
| L0 | Direct label, as in LH-CP2 |
| L1 | Direct label found through local submissions (Part A) |
| L2 | Corroborated reconstruction |
| L3 | Single-source reconstruction |

**Methods**

| Method | How it works |
|---|---|
| M-SEQ | Annual brackets: two consecutive 10-Ks 357–378 days apart, exactly three 10-Qs between them, 80–100-day gaps, no transition form |
| M-CMP | A later original filing about one year later carries a prior-year comparative fact ending at the period, with a duration consistent with that filing's own label |
| R* | Accepts a label only when M-SEQ and M-CMP agree. Any disagreement is a conflict, which means no label |

**Validation design**
- Hidden labels behind pseudo-XBRL starts. Earlier filings lose their facts and labels, exactly as a genuine pre-XBRL filing would.
- Registrant split by hash: held-back registrants are evaluated once.
- Thresholds V1–V5 were frozen before any validation output.

**Rules freeze.** `lh_cp3_rules.py` was frozen **unchanged** after development (9a72c5c8…, commit 0f80d6a). The held-back run asserted that hash.

**Addendum 1.** Addendum 1 (4fbd4da7…) was written after the development run and before the held-back run. It adds a **non-gating** "truth-audited" view. The reason: all 35 unique development disagreements were mislabelled *truth* filings (11 contradict their own form, 22 are isolated off-cycle tags, 2 sit in garbled sequences). The official classification uses the stricter unaudited figures.

## 8. Local submissions recovery results (Part A, before any network request)

`LH_CP3_part_a.json` was committed in dc4766e, before the manifest and before any request. 0 network requests.

### Unique registrant-periods with an unknown L0 label in Stage C P2 chains: 3,796

| Class | Periods | Share |
|---|---|---|
| Verified (L1) | 444 | **11.7%** |
| Unknown-nonXBRL (genuinely no XBRL) | 3,288 | 86.6% |
| Invalid (mapping fails) | 22 | |
| Unknown-noFacts | 25 | |
| Unknown-noAccession | 17 | |

Split by the LH-CP2 reason for the missing label:

| LH-CP2 reason | Periods | Verified | Not XBRL at all |
|---|---|---|---|
| "No index row" | 321 | 151 | 147 |
| "Pre-XBRL" | 3,462 | 291 | 3,141 |

### Stage C P2, C1-complete stock-months (94,836)

| Measure | LH-CP2 | After L1 |
|---|---|---|
| Label-unknown share | 13.36% (12,669) | 11.43% (10,839) |
| Unique chains with unknown labels (of 33,088) | 4,380 | 3,762 |

### All-registrant unique 13-period chains (93,256; LH-CP2 diagnostic population)

| | Unknown share |
|---|---|
| LH-CP2 | 26.67% |
| After L1 | 25.58% |

## 9. Pre-registered EDGAR sample manifest

`LH_CP3_manifest.json` (SHA-256 ce09012e…) was committed in f6264f6, **before** the first request.

- **Population.** Non-XBRL original filings whose label is still unknown and which belong to label-unknown C1 / C2-complete histories of 2013–2014 stock-months: **1,743 accessions from 596 registrants**.
  - Frozen R* outcome: L2 1,641, L3 91, conflict 2, none 9.
- **Strata.** Form × filing-year base (6 × 10, L2 only), single-source 10, conflict / none 10, 52/53-week 10, transition registrants 10, entrants 10, leavers 10.
- **Size.** 120 accessions (82 10-Q, 38 10-K) from 110 registrants, at most 2 per registrant.
- **Ordering and replacement.** Ordered by `sha256('LH-CP3-sample|' + accession)`. No replacement.
- **Shortfalls.** Every stratum was filled; the smallest pool was conflict / none, with 11 eligible.

## 10. Exact SEC request count

**120 HTTP requests**, all HTTP 200: no retry, no fallback, no 404, no block. The run took 13:49–13:50 UTC on 2026-10-18 (`LH_CP3_request_log.json`).

**Parser defect.** The first parse discarded all 120 responses because the parser expected the text header layout, while `.hdr.sgml` uses SGML tags. The defect was found by inspecting **tag names only** and fixed. The headers were then re-parsed from the local cache with **0 additional requests**; the `--reparse` mode never overwrites the request log. Total requests stay at 120 of the 150 budget.

## 11. Filing-header information actually available

Every header carries:
- accession number;
- submission type;
- period of report;
- filing date and filing-date-change date;
- acceptance time;
- filer CIK;
- form type.

118 of 120 also carry a fiscal-year-end code, and 57 list former-name dates. **There is no fiscal-quarter field.**

| Check | Result |
|---|---|
| Period of report = local submissions report date | 120 / 120 |
| Form = local form | 120 / 120 |
| Changed after the cut-off | 0 of 120 |

**What a header proves:** the period end, the form and the registrant's fiscal-year-end code at filing time.

**What it does not prove:** the quarter label. A quarter from the fiscal-year-end code is an inference (H-FYE). H-FYE gave a quarter for 110 headers; 7 gave none and 3 were "inconsistent" (a 10-K period not at the code).

I did not compare header codes with the current-status code. That code comes from today's SEC record, which is post-cut-off metadata, so I deliberately did not read it.

## 12. Pre-XBRL recoverability

- **Of the 3,288 non-XBRL periods,** recovery depends on how far a quarter lies before the company's first XBRL filing:
  - **M-SEQ** can label almost any period inside two annual 10-K brackets.
  - **M-CMP** works only within about one year of the first XBRL filing, where later filings present the old quarter as a comparative.
- **2013–2014 pre-XBRL filings in the manifest population:** R* gives a corroborated L2 label for **94%** (1,641 of 1,743).
- **Validation recall:** R* abstains more for deeply hidden periods (recall 58% overall; M-SEQ alone 99.7%).

## 13. Held-back reconstruction validation

Run once, with the frozen rules, on held-back registrants:
- 1,911 registrants;
- 14,260 evaluable pseudo-histories;
- **97,082 hidden-label trials**.

R* outcomes: L2 56,658; L3 40,222; conflict 48; none 154.

## 14. Accuracy, error rates and confidence intervals (held-back; registrants are the independent units)

| Method | Accepted | Correct | Incorrect | Abstained | Precision | Recall | Label-error upper 95% (cluster bootstrap) | Registrants with ≥ 1 error |
|---|---|---|---|---|---|---|---|---|
| **R* (L2)** | 56,658 | 56,631 | 27 | 40,424 | 99.95% | 58.3% | **0.069%** | 18 / 1,379 (CP upper **1.93%**) |
| M-SEQ alone | 96,849 | 96,803 | 46 | 233 | 99.95% | 99.7% | 0.067% | 24 / 1,380 (2.44%) |
| M-CMP alone | 56,785 | 56,703 | 82 | 40,297 | 99.86% | 58.4% | 0.195% | 30 / 1,379 (2.94%) |
| R* L2 or L3 | 96,880 | 96,827 | 53 | 202 | 99.95% | 99.7% | 0.076% | 26 / 1,380 (2.61%) |

### Truth-audited view (Addendum 1, non-gating)

46 trials have a suspect truth label. With those set aside:
- **R* has 0 errors** (registrant upper bound 0.22%);
- M-SEQ has 0 errors;
- M-CMP has 55.

All 27 R* "errors" fall on mislabelled truth filings. These were never claimed as zero true error; the bound is reported.

### R* error rates by stratum (incorrect / accepted)

| Stratum | Errors |
|---|---|
| Filing type | 10-K 0 / 14,205; 10-Q 27 / 42,453 |
| Period year | 0 in 2011–2013; 2014 5; 2016 2; 2017 2; 2018 6; **2020 12 / 1,615 (0.74%; truth mis-tags in 2020 10-Qs)** |
| 52/53-week registrants | 4 / 11,399 (0.04%), against 0.05% otherwise |
| Fiscal-transition registrants | 6 / 2,405 (**0.25%**), against 0.04% otherwise; higher, as the owner anticipated |
| Hidden depth 1–4 / 5–8 / 9–12 | 0.03% / 0.04% / 0.07% |
| Entrants / leavers / stayers / not in the universe | 0.05% / 0% / 0.05% / 0.05% |

### Criteria (frozen thresholds)

| ID | Value | Threshold | Status |
|---|---|---|---|
| V1 label error, upper 95% | 0.069% (1,379 registrants) | ≤ 0.5% | **PASS** |
| V2 registrants with an error, CP upper | 1.93% | ≤ 2.0% | **PASS (narrow)** |
| V3 fiscal changes in the hidden part rated valid | 0 of **10** registrants (CP upper 25.9%) | ≤ 10%, n ≥ 20 | **INSUFFICIENT** |
| V4 first-four-XBRL-filings mis-tag rate | 0.058% vs later 0.115% (upper 0.117%) | ≤ max(2×, +0.5 pp); ≤ 2% | **PASS** |
| V5 header check on genuine pre-XBRL filings | 1 / 94 disagree (1.06%; CP upper 4.95%) | ≤ benchmark 0.38% + 5 pp | **PASS** |

**V3 in development.** The development set had 15 qualifying registrants; 1 was rated valid (descriptive only).

**V5 detail:**
- every stratum was retrieved;
- the single disagreement is a 2010 10-Q;
- the 52/53-week, transition, entrant and leaver strata show no disagreement;
- H-FYE agrees with M-SEQ on 99 of 100 usable headers and with M-CMP on 96 of 97.

## 15. Fiscal-year-transition handling

- **How transitions are excluded:**
  - M-SEQ rejects any bracket containing a 10-KT / 10-QT, any non-annual 10-K spacing and any irregular quarter count;
  - transition forms make a history invalid (rule V);
  - a conflict between the methods yields no label.
- **What the evidence shows:**
  - error rates are higher in transition registrants (0.25%);
  - **whether a genuine undisclosed fiscal change hidden in pre-XBRL quarters would be caught could not be validated**: only 10 held-back registrants had one (V3 insufficient), the pre-registered minimum is 20, and the CP upper bound with 0 of 10 is 25.9%.
- **Header evidence:** the 10 transition-registrant headers show no disagreement.

This is the main unresolved restriction.

## 16. 52/53-week handling

- **Rules:** period ends and day-count windows (357–378-day years, 80–100-day quarters, ±15-day H-FYE tolerance) handle drifting year ends. Fiscal-year-end codes are not used for validity.
- **Error rates:** 0.04% for 52/53-week registrants, versus 0.05% otherwise.
- **Header check:** 10 / 10 agree.

## 17. Proposed rule P evaluation (proposal only; unchanged)

**Rule P on held-back pseudo-histories (L2 labels).**

| True status | P-strict | P-assume | Histories |
|---|---|---|---|
| Valid | Valid | Valid | 2,336 |
| Valid | Unknown | Valid | 11,718 |
| Invalid | Invalid | Invalid | 53 |
| Invalid | Valid | Valid | 19 |
| Invalid | Unknown | Valid | 134 |

**P-assume accepts 134 truly invalid histories.** It must not become a default.

**Boundary weakness confirmed (all registrants; ex-post, labels ≤ CUT).** Rule P tolerates one isolated off-cycle label. In 13-period windows where that label sits at the edge of the window:

| Edge | Windows | Genuine re-basings | Reverting mis-tags | Other | Undetermined |
|---|---|---|---|---|---|
| Newest | 102 | **3** | 51 | 12 | 36 |
| Oldest | 46 | **8** | 21 | 3 | 14 |

At the boundary, at least **11 of 148 windows (7.4%)** are **genuine fiscal re-basings** that rule P would accept as valid. Interior isolated labels (439 windows) revert by construction.

**Suggested revision (not applied; owner's decision).** Treat an off-cycle label at either end of the window as *unknown*. The accounting justification: a single label at the edge cannot distinguish a tagging error from the first or last quarter of a new fiscal calendar.

## 18. Verified, conditional, invalid and unknown classifications (C1-complete stock-months, 94,836)

| Class | All | Among the 12,669 LH-CP2 label-unknown |
|---|---|---|
| Verified valid (L0 + L1, no identity flag) | 82,011 | 1,731 |
| Verified invalid | 1,658 | 641 |
| Conditionally valid B (validated R* L2; assumption: the measured R* error rate, and no undisclosed fiscal change) | 8,801 | 8,801 |
| Conditionally valid C (L3 single source or identity flag) | 2,212 | 1,342 |
| Invalid (reconstructed) | 30 | 30 |
| Unknown / conflict | 119 / 5 | 119 / 5 |

**Resolution share** of the LH-CP2 unknowns: **88.4%** (11,203 / 12,669), against the 90% required for class A.

Every retained observation can be traced to its class, and conditional ones are never merged into "verified". The per-stock-month class is reproducible from `LH_CP3_final.py`.

## 19. C1 / C2 / C6 coverage by year (E981-01 denominator; numerators in `LH_CP3_final.json`)

| Scenario | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | Min year |
|---|---|---|---|---|---|---|---|---|---|---|
| **A** strict verified — C1 | 41.3 | 69.9 | 77.3 | 81.2 | 81.4 | 81.8 | 83.0 | 80.2 | 74.8 | 2013 |
| A — C2 | 39.0 | 65.8 | 72.8 | 76.5 | 76.4 | 76.7 | 78.5 | 77.6 | 73.3 | 2013 |
| A — C6 | 38.9 | 65.7 | 72.7 | 76.5 | 76.4 | 76.7 | 78.5 | 77.6 | 73.3 | 2013 |
| **B** + validated R* — C1 | 73.4 | 78.3 | 78.8 | 81.7 | 81.8 | 82.4 | 83.3 | 80.5 | 75.2 | 2013 |
| B — C2 | 68.7 | 73.4 | 74.0 | 76.9 | 76.7 | 77.2 | 78.7 | 77.9 | 73.7 | 2013 |
| B — C6 | 68.5 | 73.3 | 73.9 | 76.8 | 76.7 | 77.2 | 78.7 | 77.9 | 73.7 | 2013 |
| **C** + conditional (sensitivity only) — C1 | 77.0 | 80.1 | 80.1 | 83.2 | 82.9 | 83.3 | 84.0 | 81.1 | 75.7 | 2021 |
| C — C2 | 71.8 | 74.9 | 75.2 | 78.0 | 77.5 | 77.9 | 79.3 | 78.4 | 74.1 | 2013 |
| C — C6 | 71.7 | 74.7 | 75.1 | 78.0 | 77.5 | 77.9 | 79.3 | 78.4 | 74.1 | 2013 |
| **D** LH-CP1 original — C1 | 78.7 | 81.4 | 81.3 | 84.1 | 83.9 | 84.1 | 85.0 | 83.1 | 78.6 | — |

- **2013 counts.** The denominator is 10,430. Scenario A covers 4,312 C1 stock-months; Scenario B covers 7,651.
- **Scenario D** is unchanged from LH-CP1 (C2 / C6 in `LH_StageC_audit.json`).
- **Scenario B uses R*** because R* met every evaluated criterion: class B, no failure.

## 20. Provisional 70% floor comparison

| Scenario | Result |
|---|---|
| A (verified only) | Fails 2013 for all three, and 2014 for all three (C1 69.9%). **Passes every year 2015–2021 for C1, C2 and C6** |
| B | C1 passes every year 2013–2021. C2 and C6 fail only 2013 (68.7% / 68.5%) |
| C (sensitivity) | All pass (minimum 71.7%) |
| D | All pass (the LH-CP1 reference) |

## 21. Missingness and selection-bias effects

**Recovered versus unrecovered,** among the 12,669 LH-CP2 label-unknown stock-months:

| Group | Recovered share | Overall: 88.4% |
|---|---|---|
| Anchor year | 2011 77%, 2012 85%, 2013 92%, 2014 93% | Later years 89–96% |
| Sector (lowest) | Energy 75%, consumer non-durables 81%, business equipment 85% | |
| Sector (highest) | Utilities 93%, manufacturing 92%, chemicals 92% | |
| Registrant age | < 5 years 77%; 5–15 years 88%; ≥ 15 years 89% | |
| Entrants / leavers / stayers | 86% / 88% / 89% | |
| Size terciles | 89% / 87% / 90% | Flat |
| History depth | Fewer than 20 prior periods 88%; 20–39 prior periods 92% | |

**Composition under the scenarios** (share of 2013–2021 C1-complete stock-months included):

| Group | Scenario A | Scenario B |
|---|---|---|
| All | 91.3% | 96.6% |
| Entrants | **81.3%** | 96.0% |
| Leavers | 84.9% | 96.2% |
| Young firms | 84.7% | 92.8% |
| Energy | 84.4% | 91.9% |
| 2013 | **52.5%** | 93.2% |

**Reading.**
- Scenario A (verified only) is strongly skewed: against 2013–2014, entrants, leavers, young firms and energy.
- Scenario B removes most of the skew. It narrows the entrant gap (96.0% vs 96.7%) and the leaver gap (96.2% vs 96.7%), but leaves energy and young firms behind.
- The recovered histories therefore *reduce* the bias that verified-only creates rather than adding new bias. They remain somewhat less complete for young firms and energy.

## 22. Residual uncertainty

1. **Undetected fiscal changes.** Genuine undisclosed fiscal changes inside reconstructed pre-XBRL stretches are not validated (V3 insufficient). The R* error rate is higher for transition registrants (0.25%).
2. **Narrow V2 pass.** V2 passes narrowly (1.93% vs 2.0%). It would pass comfortably if mislabelled truth filings are set aside, but that view is non-gating.
3. **Ground-truth noise.** The ground truth (company XBRL `fp` tags) itself contains tagging errors, about 0.05% of trials. Every accuracy figure is bounded by that noise.
4. **Header check limits.** The header check covers 94 usable filings (CP upper bound 4.95%). Headers prove the period, form and fiscal-year-end code, never the quarter label.
5. **Residual unresolved histories.** 11.6% of the LH-CP2 unknowns stay unresolved or depend on single-source / identity assumptions (Scenario C).
6. **Rule P.** Rule P's boundary tolerance would accept some genuine re-basings, so it remains a proposal.
7. **Denominator.** The denominator is the Data v1 universe (E981-01); the Data v2.1 per-stock-month universe was never exported.

## 23. Final classification

**B — PARTIAL RECOVERY** (protocol §10, mechanical).
- V1, V2, V4 and V5 pass; V3 is insufficient, so A is impossible.
- The resolution share is 88.4%, below the 90% that A would require.

**What is reliably recovered:**
- verified local recoveries (L1);
- corroborated reconstructions within about a year of each company's first XBRL filing, plus FY periods, under the stated assumption.

**Restrictions:**
- no evidence about undisclosed fiscal changes;
- single-source labels are not validated for use;
- C2 and C6 miss the floor in 2013 even with reconstruction.

This does **not** make OF-A feasible. It does **not** reclassify Stage C, which stays C, or LH-CP2, which stays C.

## 24. Exact next owner decision

**Recommendation: option 3 — restrict the usable research period rather than accepting uncertain historical records.**

- **Proposed period:** decision years **2015–2021**, using **strictly verified histories only (Scenario A)**.
- **Why:**
  - in that window C1, C2 and C6 all meet the 70% floor in every year (minimum 72.7%);
  - the floor is met without reconstructed or assumed labels, and without relying on the untestable fiscal-change behaviour;
  - entrant and leaver coverage is also less distorted after 2014.
- **Cost:** two fewer years of decisions, so lower statistical power.

**Not recommended now:**
- **Option 1** (a Stage C exception using validated reconstruction for 2013–2014), because V3 could not be validated.
- **Option 2** — there is no sound way to strengthen V3. Too few genuine fiscal changes exist for a larger test, and more headers cannot prove quarter labels.
- **Option 4** — the evidence does not require stopping.

**Even option 3 needs an explicit owner decision on Stage C.** Its frozen result stays C (driven by the mis-specified fiscal-year-end code criterion, D242). Any future use of the 2015–2021 verified population would be an owner exception to that criterion, with rule V applied (not rule P, given §17).

**Decision requested:**
- (a) accept LH-CP3 = B;
- (b) choose option 1, 2, 3 or 4;
- (c) if option 3: approve, or not, a narrowly defined Stage C exception limited to 2015–2021 verified histories under rule V.

Nothing proceeds without that decision. In particular: no Stage B, no signal selection and no change to trading frequency.

## 25. Confirmation: no stock-return analysis

No price, return, wealth, surprise value, ranking, predictive statistic, portfolio or backtest was computed, read or used. There was no QuantConnect run. Every artifact is accounting-period metadata.

## 26. Confirmation: no post-2021 filing or Holdout information

- **Network:** every record and header used was filed ≤ 2021-12-31. All 120 EDGAR headers were filed ≤ 2014-08-12, and none was changed after the cut-off.
- **Local data:** local loaders drop all later records before inspection, and this is tested.
- **Current-status metadata:** not read, and deliberately not compared.
- **Holdout:** the 2022-01-01 → 2026-08-31 Holdout was not accessed; `HOLDOUT_UNLOCK.md` does not exist.

---

**Counts.** Hypotheses tested: 0. Strategies: 0. Experiments (strategy backtests): 0. This was a metadata audit. Network requests: 120 of 150.

**STOPPED — awaiting owner review.**
