# LH-CP2 — Fiscal Calendar Anomaly Resolution

**Owner decision D243, 2026-10-18.** The message is recorded verbatim in `docs/owner/2026-10-18_lh_cp2_fiscal_calendar_anomaly_resolution.md`.

**Nature:** an offline SEC metadata investigation only.
- No return, price, QuantConnect run, surprise value, ranking or backtest.
- No data dated after 2021-12-31.
- Holdout sealed.

**Stage C stays C — NOT FEASIBLE under its frozen protocol.** Nothing here changes it.

**Result in one line:**
- **Under the frozen LH-CP2 protocol: C — INSUFFICIENT EVIDENCE.**
- The specific 1.3% anomalies are **largely explained**: 91% are pure SEC fiscal-year-end metadata inconsistencies with fully consistent fiscal-quarter labels.
- But a period-based validity check cannot be completed for about 13% of input-complete histories. Their oldest quarters were filed **before the company used XBRL**, so no fiscal label exists for them in the permitted offline data.

**Labels:** [V] measured; [I] interpretation; [P] proposal.

---

## 1. Repository verification [V]

**State checked before any work:**
- `main` = `4bc96a7` (PR #107), working branch identical, tree clean; no change since PR #107.
- Last decision D242. The Stage C protocol hash is unchanged (`ff97789b…`; also pinned by a new test).
- No `HOLDOUT_UNLOCK.md`.
- QuantConnect checks passed (credentials present, values never printed). No QuantConnect call was made.

**Commits:**

| Commit | Content |
|---|---|
| `cb626e3` | Owner record, cut-off loaders + tests, frozen protocol (before any aggregate) |
| `bb300e6` | Script fix: a load-time crash on filing-index rows without a period; no aggregate had been produced |
| `c259cc4` | Investigation results |
| `16a1730` | Post-hoc diagnostic and rule proposal |

## 2. Owner authorisation and exact scope [V]

**D243 allows:**
- an offline SEC metadata investigation (≤ 2021-12-31) of the LH-CP1 fiscal-year-end anomalies;
- diagnostics and tests;
- aggregate classification and coverage effects;
- representative pre-2022 metadata cases;
- this checkpoint and a PR.

**Not allowed:**
- any 2022+ data or Holdout;
- QuantConnect, backtests, returns, OF-A signals or rankings, Stage B;
- H028 / Ridge changes;
- Data v2.1 / v3 changes;
- changing the Stage C classification or approving an exception;
- purchases;
- implementation.

**Frozen investigation protocol:** `research/longhorizon/cp2/LH_CP2_protocol.md`, SHA-256 **`f7cbac944e433fcda235b6c5e1c98cd2c62e486805c4b6cdaf98bc7e18819ed9`**. Pinned in `tests/test_lh_cp2.py`; committed before any aggregate.

## 3. Original LH-CP1 failure preserved [V]

- **LH-CP1 / Stage C remains C — NOT FEASIBLE.** The frozen criterion is: at most 1% of input-complete histories with a fiscal-year-end code change between q0 and its comparison quarters.
- **Measured failure:** 8.3–15.1% across C1–C6 (C1 14.4% = 11,930 / 82,802 stock-months).
- The Stage C protocol, hash, results, JSON and checkpoint are untouched. No exception is assumed.

## 4. Source and cut-off verification [V]

**Sources** (cache only; networking disabled; **0 network requests**):
- SEC company facts, submissions and the SEC XBRL filing index (local caches);
- the frozen Data v2.1 table (identity and filing tables);
- the E981-01 universe;
- the frozen Stage C functions (unchanged).

**Cut-off enforcement:**
- `research/longhorizon/cp2/lh_cp2_safe.py` drops every record dated after 2021-12-31 **inside the loader**, before any caller can see it:
  - companyfacts: filed, end and start dates;
  - submissions: filingDate and reportDate;
  - XBRL index: filed and period.
- Every output and example is checked by `assert_no_post_cutoff`.
- Tests cover synthetic post-cut-off rows and the cached files.
- **The 2026-row slip of LH-CP1 did not recur:** all inspection, including the structure check, went through these loaders.

## 5. Reproduction of the anomaly counts [V]

- The committed diagnostic (`LH_StageC_fye_diagnostic.py`) was re-run unchanged into a temporary file. Its output is **bit-identical** to the committed JSON.
- **13-quarter chains (unique filing-table chains, all 3,941 registrants, anchor 2011–2021):**

| Behaviour | Count | Share of 69,182 chains with codes | Reported |
|---|---|---|---|
| Any code change | 7,213 | 10.43% | 10.4% |
| Shift ≤ 7 days | 5,085 | 7.35% | 7.4% |
| Shift 8–31 days | 560 | 0.81% | 0.8% |
| Shift > 31 days | 1,568 | 2.27% | 2.3% |
| – quarter-aligned (≈ 3 months 354, ≈ 6 months 324) | 678 | 0.98% | 0.9% |
| – other ("unexplained") | 890 | **1.29%** | 1.3% |
| (codes missing: 24,074 chains, excluded from the denominator) | | | |

- The earlier write-up rounded 0.98% down to 0.9%; 1.0% is correct.

## 6. Denominator reconciliation [V]

The figures use **three different denominators**. They must not be mixed.

| Basis | What is counted | With codes | Changed | "Other" > 31 days |
|---|---|---|---|---|
| **Stage C gate (C1)** | Repeated stock-months of input-complete C1 histories in the eligible non-financial universe | 82,802 | 11,930 (**14.4%**) | 1,064 (1.28%) |
| **P2 unique** (this study) | The same C1 histories, each counted once | 28,898 | 4,165 (14.4%) | 358 (1.24%) |
| **P1 diagnostic** | Unique chains of *all* registrants, no eligibility and no value requirement | 69,182 | 7,213 (10.4%) | 890 (1.29%) |

**The 1.3% does not use the Stage C gate's denominator.**
- It counts unique chains of all registrants.
- The gate counted eligible stock-months, repeated about 3 times per history.
- The gate's universe has more 52/53-week filers (technology, retail), which is why its change rate is higher (14.4% vs 10.4%).
- On the gate's own basis, the "other" group is 1.28% of stock-months.

**P2 reproduction:** the rebuilt Stage C population reproduces `LH_StageC_audit.json` exactly, for C1 / C2 / C6 coverage in every year 2011–2021 (protocol stop rule, passed).

## 7. Anomaly classification methodology [V]

**Per-period metadata** (each history period, filed before the decision day):
- the original 10-Q / 10-K accession (XBRL index);
- its **fiscal-period label** `fp` (Q1 / Q2 / Q3 / FY, from the company-facts facts carrying that accession);
- a **mapping check** (the accession has a duration fact ending at that period ±7 days, and the index filing date matches the Data v2.1 original filing day ±3 days);
- any **transition form** (10-KT / 10-QT) whose report date lies inside the history;
- an **identity change** of the security's SEC registrant during the history.

**Label consistency:** the labels follow the cycle Q1 → Q2 → Q3 → FY, and each seasonal pair (q_k, q_{k+4}) has the same fiscal quarter.

**Categories (first match):**

| Category | Rule |
|---|---|
| F | Transition form |
| D | Mapping failure |
| E | Identity change |
| B | Labels broken |
| G | Labels unknown |
| A | Shift ≤ 7 days and labels consistent |
| C | Larger shift and labels consistent |

The rules are frozen in protocol §6. The same tests were also applied to histories **without** a code change.

## 8. Classification results [V]

**The "unexplained" group (shift > 31 days, not quarter-aligned):**

| Category | P1 unique (n = 890) | P2 unique (n = 358) | P2 stock-months (n = 1,064) |
|---|---|---|---|
| **C — metadata inconsistency** (labels fully consistent) | 813 (**91.3%**) | 316 (88.3%) | 934 (87.8%) |
| B — label break | 16 (1.8%) | 11 (3.1%) | 33 (3.1%) |
| E — identity change | not assessed (P1 has no securities) | 10 (2.8%) | 32 (3.0%) |
| D — mapping problem | 2 (0.2%) | 0 | 0 |
| F — transition form | 1 (0.1%) | 0 | 0 |
| **G — unresolved** (labels unknown) | 58 (6.5%) | 21 (5.9%) | 65 (6.1%) |

**All code-change groups, P2 unique histories:**

| Group | A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|---|
| ≤ 7 days | 3,229 | 30 | — | 5 | 34 | 4 | 40 |
| 8–31 days | — | 3 | 245 | — | — | 3 | 23 |
| Quarter-aligned | — | 10 | 117 | 1 | — | 49 | 14 |
| Other | — | 11 | 316 | — | 10 | — | 21 |

The quarter-aligned group has the most transition forms (49 of 191). These are genuine fiscal-year changes filed with a transition report.

**Histories *without* a code change** (P2, C1-complete; protocol §6 last line):
- 278 unique histories (764 stock-months, **0.81%**) are **label-broken although their codes are equal**;
- 520 unique (1,515 stock-months) are label-unknown.

The code test is therefore **both over-inclusive** (most flagged changes are harmless) **and under-inclusive** (it misses label breaks).

**Concentration (P2):**

| Category | Unique histories | Registrants | Stock-months | Top-5 registrants' share |
|---|---|---|---|---|
| A | 3,229 | 236 | 9,197 | 6% |
| C | 678 | 101 | 1,979 | 17% |
| B | 54 | 10 | 145 | 79% |
| E | 44 | 4 | 136 | 100% |
| F | 56 | 11 | 162 | 65% |
| D | 6 | 4 | 19 | 100% |
| G | 98 | 22 | 292 | 47% |

- Entrant shares are 0–7% per category, against 4.5% overall. Leaver shares are 0–27%, against 18.0% overall.
- **Category C has more leavers (25%).**

## 9. Representative metadata-only examples [V]

Each example is the first OTHER-group history of its category, by hash. These are public SEC filing metadata, all pre-2022.

| Category | Registrant | Codes q0 / q4 / q12 | What the metadata shows |
|---|---|---|---|
| **C** | Albany International (CIK 819793), q0 = 2016-03-31 | 1231 / 1231 / 0218 | Labels follow a calendar fiscal year exactly (FY at every December period; Q1–Q3 at March, June, September) while the index code reads 0218 for 2013–14 filings. **Pure code noise.** |
| **F** | Raptor Pharmaceutical (CIK 1070698), q0 = 2016-03-31 | 1231 / 1231 / 0831 | The company moved its fiscal year from August to December with a transition report. After the move, the labels are consistent on calendar quarters. **Genuine change, disclosed.** |
| **D** | ONEOK Partners (CIK 909281), q0 = 2014-03-31 | 0216 / 0216 / 1231 | The oldest period end is recorded as 2011-03-23, an implausible quarter end, with codes 0713 / 1231 in 2011. **A genuine mapping / metadata problem.** |
| **G** | Astec Industries (CIK 792987), q0 = 2016-06-30 | 1231 / 1231 / 0723 | The 2015-09-30 10-Q is missing from the XBRL index, so one label is unknown. Codes 0723 for 2013–14. **Unresolved offline, but see §14.** |
| **B** | Euronet Worldwide (CIK 1029199), q0 = 2020-09-30 | 1231 / 1231 / 0222 | Calendar periods are perfectly regular, but the 2020-09-30 10-Q is tagged "Q2" instead of "Q3". **An isolated tagging error, not a fiscal change.** A pure label test misreads it. |

## 10. Fiscal-quarter comparability findings [V / I]

Answers per category (owner §6, questions 1–8):

| | A (≤ 7 days, labels OK) | C (metadata) | B (label break) | F (transition) | D (mapping) | E (identity) | G (unknown) |
|---|---|---|---|---|---|---|---|
| 1 Quarter ends consistent | Yes (80–100-day chain) | Yes | Yes | Yes | **Not always** (stray period end) | Yes | Yes |
| 2 Durations compatible | Yes (direct three-month facts or the frozen year-to-date rule) | Yes | Yes | Mostly | Unknown | Yes | Yes |
| 3 Did the continuity rule detect it? | No (nothing to detect) | No | **No** | **No** (quarter-aligned changes keep 80–100-day gaps) | **No** | No | No |
| 4 q0 / q4 same fiscal quarter | **100%** | **100%** | 69% | 64% | 100% | 93% | 87% (where known) |
| 5 All 9 seasonal pairs valid | **100%** | **100%** | 0% (by definition) | 0% | 0% | 73% | 0% (unknown) |
| 6 Could the arithmetic be wrong? | No | No | Possibly (real changes); no (tagging errors) | Yes, across the transition (year-to-date bases shift) | Yes | Possibly (wrong registrant) | Cannot say |
| 7 PIT risk | None | None | None | None | None | None | None |
| 8 Safely excludable without changing data | Not needed | Not needed | Yes (flag) | Yes | Yes | Yes | Yes (flag) |

- A code change does not make a history incomparable: categories A and C are fully comparable by period end and by fiscal label.
- A continuous-looking history is not proof of comparability: 0.81% of equal-code histories break their labels, and quarter-aligned fiscal changes pass the 80–100-day rule.
- Fiscal labels themselves contain tagging errors (the B example).

## 11. PIT implications [V]

- Every input used here (labels, forms, mapping, identity) comes from filings accepted **before** the decision day, and from rows dated ≤ 2021-12-31.
- Label- and form-based rules are therefore usable point-in-time.
- **No PIT violation was found.** The Stage C value PIT assertion (0 violations) is unaffected.
- The fiscal-year-end code is itself PIT, but unreliable as a validity signal.

## 12. Candidate C1 / C2 / C6 coverage effects [V]

Coverage of the eligible non-financial universe, 2013–2021, after conservative exclusions applied to unique histories. **The provisional 70% floor is unchanged.**

| Exclusion | C1 min year | C2 min year | C6 min year | Floor 70% all years |
|---|---|---|---|---|
| None (Stage C) | 78.6% (2021) | 73.5% (2013) | 73.4% (2013) | ✔ / ✔ / ✔ |
| X1 label-broken or transition | 75.9% (2021) | 72.9% (2013) | 72.7% (2013) | ✔ / ✔ / ✔ |
| X2 mapping failures | 78.1% | 72.9% | 72.7% | ✔ / ✔ / ✔ |
| X1 + X2 | 75.7% | 72.4% | 72.2% | ✔ / ✔ / ✔ |
| X3 labels unknown (alone) | **41.0% (2013)** | **38.8%** | **38.7%** | ✘ / ✘ / ✘ |
| **X1 + X2 + X3** (rule V, conservative) | **40.7% (2013)** | **38.5%** | **38.4%** | ✘ / ✘ / ✘ |

**Rule V by year, C1:** 2013 40.7 · 2014 68.2 · 2015 75.1 · 2016 79.6 · 2017 80.5 · 2018 81.0 · 2019 82.6 · 2020 80.5 · 2021 75.2%.

**Rule V on C1-complete histories:**
- unique: valid 28,340, invalid 552, unknown 4,196;
- stock-months: valid 81,150, invalid 1,535, unknown 12,151 (**12.8%**).

**[I]** Excluding demonstrably invalid histories (X1 + X2) costs about 1–3 points and keeps every year above the floor. Excluding *unknown* histories costs most of 2013–2014.

## 13. Sector / size / age / entrant / leaver effects [V]

Share of C1-complete stock-months excluded by rule V (X1 + X2 + X3); 14.4% overall:

| Group | Excluded |
|---|---|
| **Utilities** | **36.6%** |
| Energy | 19.0% |
| Telecom | 15.1% |
| Other sectors | 11–14% |
| Smallest size tercile (SEC total assets) | 15.8% |
| Middle / largest tercile | 13.5% / 13.9% |
| Firm age < 5 years | 19.0% |
| Firm age 5–15 years | 16.9% |
| Firm age ≥ 15 years | 13.5% |
| **Entrants** (first 12 eligible months) | **20.4%** (vs 14.2%) |
| **Leavers** | **22.4%** (vs stayers 12.7%) |

**[I]**
- The exclusion would deepen the selection bias already found in LH-CP1: against leavers, new and young firms, utilities and energy.
- Excluding a small share of histories does not remove bias. Here it adds to it.

## 14. Residual unresolved cases [V]

**Post-hoc diagnostic** (`LH_CP2_unknown_label_diagnostic.py` / `.json`). It was written **after** the protocol result, uses metadata only, and is **not** used for the classification. It covers 93,256 unique 13-quarter chains of all registrants; 24,867 (26.7%) have at least one unknown label.

| Cause of the unknown label | Chains | Share of unknown |
|---|---|---|
| **The quarter's original filing predates the registrant's first XBRL filing (pre-XBRL only)** | 19,187 | **77.2%** |
| Pre-XBRL plus missing index rows | 2,244 | 9.0% |
| Registrant already on XBRL, but this filing is **missing from the XBRL index** | 3,183 | 12.8% |
| Index row exists, but no fact carries its accession (`fp` missing), alone or combined | 253 | 1.0% |

**By anchor year:**
- pre-XBRL causes dominate 2011–2014 (7,117 · 6,462 · 4,251 · 1,047 chains);
- missing index rows persist at about 100–650 a year through 2021.

**[I] What would resolve them** (nothing done; owner decision needed):
1. **Missing index rows (about 13%, resolvable offline):** map each period's accession from the cached **submissions** file (every 10-Q / 10-K with its accession), not only from the XBRL index. This changes method, not data, and would need a protocol amendment.
2. **Pre-XBRL quarters (about 86%):** no `fp` label exists. Options:
   - **(a)** accept them by assumption when the labelled part of the history is consistent and no transition form appears in submissions (rule P "assume", §15);
   - **(b)** obtain pre-XBRL filing-header metadata (period of report and fiscal-year end at filing, from EDGAR filing headers). This is public and free, but needs **network access to www.sec.gov** (not authorised in D243), and the header's fiscal-year-end field is itself a code;
   - **(c)** shorten the history requirement. Not proposed: that would be choosing for coverage.

## 15. Proposed corrected calendar-validity rule [P]

**Rule P:** `research/longhorizon/cp2/lh_cp2_rule_proposal.py`. **A proposal only.** Its coverage is **deliberately not computed**, so it cannot be tuned to the floor.

**Inputs** (PIT; filings before the decision day): the contiguous period ends (the frozen 80–100-day chain), fiscal labels per original filing, transition forms in the span, and the mapping check. **No fiscal-year-end codes.**

| Outcome | When |
|---|---|
| **Invalid** | A transition form inside the history (the history restarts after the change); a mapping failure; a **persistent re-basing** of labels (2+ consecutive labelled periods off the dominant cycle = a genuine fiscal-year / quarter change); or 2+ separate off-cycle labels |
| **Valid** | All labelled periods on one cycle, or **exactly one isolated off-cycle label** (treated as a tagging error and flagged, as in the Euronet case) |
| **Unknown** | Labels missing |

**Variants for unknown histories:**
- **P-strict:** exclude.
- **P-assume:** accept only if at least 4 labelled periods are on the cycle and no transition form exists in the span. This is a stated assumption: no undisclosed fiscal change inside an unlabelled stretch.

**52/53-week calendars:** handled by period ends (80–100-day gaps) and three-month durations. Codes are ignored.

**Genuine fiscal-year transitions:** comparisons across the change are not used. The history requirement restarts.

**Rationale, independent of coverage:**
- a genuine fiscal change leaves footprints (a transition report, a persistent shift of the FY position, or a broken chain);
- an isolated wrong label without them is a tagging error;
- a code that disagrees with consistent labels is metadata noise (91% of the "unexplained" cases).

**Numerical choices that are arbitrary and need owner approval:**
- "2 consecutive" periods for re-basing;
- "exactly one" isolated error;
- "at least 4 labelled periods" for P-assume;
- the ±7-day and ±3-day matching tolerances (inherited from Data v3).

**Unit-test expectations** (implemented in `tests/test_lh_cp2.py`):

| Case | Expected |
|---|---|
| Regular or 52/53-week labels | Valid |
| One mis-tagged quarter | Valid, flagged |
| Labels re-based for 4 periods | Invalid |
| Transition form or mapping failure | Invalid |
| Oldest 5 quarters pre-XBRL | Unknown (strict) / valid with flag (assume) |
| All labels unknown | Unknown under both variants |

## 16. Unit-test results [V]

`tests/test_lh_cp2.py` (18 tests, all passing):
- the cut-off loaders (synthetic and cached files, 0 network requests);
- the output scanner;
- the Stage C protocol hash unchanged;
- the LH-CP2 protocol hash;
- the code bands, matching the committed diagnostic;
- label consistency;
- the category first-match order;
- rule V outcomes;
- rule P expectations;
- the output's reproduction flags (P1 identical, P2 identical to Stage C) and its cut-off.

The full suite passes (§20).

## 17. Limitations [V / I]

- `fp` labels are the filer's own tags. They contain errors (the B example), so label tests are evidence, not proof.
- The XBRL index is incomplete for some filings (§14, row 3).
- The identity test (E) uses the Data v2.1 identity and E981-01 CIK lists. P1 has no securities, so E is assessed only in P2.
- The denominator is the Data v1 universe (as in LH-CP1).
- The B / F / D / E / G groups are small and concentrated in a few registrants (§8). Their percentages are fragile.
- Two diagnostics (the LH-CP1 fiscal-year-end diagnostic and the unknown-label diagnostic here) are post-hoc. Neither drives a classification.

## 18. Final classification

**Frozen protocol §10:** labels are unknown for **13.4%** of C1-complete stock-months (more than 10%).

### → C — INSUFFICIENT EVIDENCE

**What this means [I]:**
- **The question the owner asked about the 1.3% is largely answered.**
  - About 91% are SEC metadata inconsistencies with fully consistent fiscal-quarter labels, so their quarterly comparisons are valid.
  - About 2–3% are label breaks and 3% identity cases.
  - About 6% are unresolved.
- **What cannot be established with permitted offline data is the period-based validity of the whole 13-quarter histories** for about 13% of input-complete stock-months (mostly 2012–2014). Their oldest quarters were filed before XBRL, so no fiscal label exists offline.
- **Under the conservative unknown-excluded rule**, C1 / C2 / C6 fall to 38–41% in 2013 and 64–68% in 2014, below the provisional floor.
- **Excluding only demonstrably invalid histories** keeps every year above 72%.

**Not done:** Stage C is **not** reclassified; no exception is assumed; Stage B is not started.

## 19. Exact owner decision required next

Choose one:

1. **Close OF-A on existing data.** Accept Stage C = C and LH-CP2 = C; no further work.
2. **Authorise a narrow resolution step:** a protocol amendment, offline only. Resolve the about 13% of unknowns caused by missing index rows from cached submissions accessions, then re-measure.
   - The pre-XBRL unknowns would remain.
   - This alone cannot change the classification unless the owner also decides the pre-XBRL treatment.
3. **Decide the pre-XBRL treatment explicitly** (each a new owner decision; Stage C's failure stays recorded):
   - **(a) P-assume:** accept unlabelled pre-XBRL quarters under the stated assumption;
   - **(b) P-strict:** accept the coverage consequence (2013–2014 below the floor), effectively starting usable C1 / C2 / C6 history in 2015;
   - **(c)** approve network access to EDGAR filing headers for pre-XBRL quarters (free; needs an approval and a new session).
4. **Combine 2 + 3** and then, separately, consider a narrow **Stage C exception proposal**. It would replace the code criterion with rule P for future use only, keep the frozen failure on record, and be measured only after approval.

**Recommendation [I]:** option 2 together with 3(b) is the most conservative path that stays fully evidence-based. Option 1 is defensible given the cumulative blockers already listed in LH-CP1. **Nothing proceeds automatically.**

## 20. Confirmation: no returns, backtests, QuantConnect runs or Holdout data

- **No price, return, wealth, surprise value, ranking or model** was computed or read.
- **No backtest, no QuantConnect call:** 0 network requests of any kind.
- **No data or filing dated after 2021-12-31** was inspected or used; the cut-off is enforced in the loaders and tested.
- **H028, Data v2.1 and Data v3 are untouched.**
- **The Holdout is sealed; nothing was purchased.**

---

**Files** (all under `research/longhorizon/cp2/`, plus `tests/test_lh_cp2.py`):
- `LH_CP2_protocol.md` (frozen);
- `lh_cp2_safe.py`;
- `LH_CP2_investigation.py` / `.json`;
- `LH_CP2_unknown_label_diagnostic.py` / `.json` (post-hoc);
- `lh_cp2_rule_proposal.py` (proposal).
