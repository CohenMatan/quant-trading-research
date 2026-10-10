# P7-CP5f — Data Infrastructure v2 Build and Freeze

**Date:** 2026-10-10. **Decisions:** D190 (owner instruction, `docs/owner/2026-10-10_p7cp5f_data_v2_build_freeze.md`), D191 (this checkpoint). **Status:** STOPPED awaiting the owner.

## Short answer

Data Infrastructure v2 is built exactly as approved. It ran four times on QuantConnect's current default build (18178), and every run passed the compliance review and placed 0 orders.

| Check | Result |
|---|---|
| Point-in-time (PIT) audit, 11 counters, all runs | **all 0** |
| Two independent full runs (E998-01 / E998-02) | **every digest identical** |
| Run ending 2013-12-31 vs full run (E998-03) | **all 35 shared months identical** (ledger, universe, eligibility, scores) |
| Market-cap repair and P7-CP5e residuals | reproduced to the decimal (69% recovery, +0.79-point gap, 98.4% agreement) |
| Split audit | 223 of 224 splits continuous |
| Score v1 and frozen mechanics | unchanged; behave exactly as on data v1 |

Score v1 and the mechanics compared with data v1:

| | Data v1 (E993-02) | **Data v2 (E998-01)** |
|---|---|---|
| Universe stock-months 2011–2017 | 93,687 | 90,370 |
| Survivor share (members still present at end-2017) | 83.3% | 84.1% |
| Fully scored stocks a month | 196–612 | 304–728 |
| 80+ candidates a month (mean) | 7.0 | 7.07 |
| Orders a year / cost at $100K | 47 / 0.80% | 46.6 / 0.79% |
| Mean capital utilisation | 69% | 69% |

**The synthetic power study is unchanged.** On the Data v2 structure:
- 50% power: IC 0.034 (data v1: 0.033), an 80+ excess of about 6.9% a year;
- 80% power: IC 0.049 (data v1: 0.047), an 80+ excess of about 9.8% a year;
- synthetic false promotion: 0.1%.

**One owner-required check trips its pre-set limit: the identity sanity check (item 7).**

The check covers 161 securities:
- 105 whose earlier SEC identity was rejected (successor registrants: spin-offs, renamed successors);
- 56 with no SEC identity row at all.

Without an SEC identity, a report cannot be dated by M2, so it never feeds Score v1.

| Measure | Result | Limit (fixed before any output, commit 43e26ec) |
|---|---|---|
| Their share of eligible stock-months, each year | 3.4% (2011) rising to 6.9% (2017) | ≤ 3% every year: **fails** |
| Survivorship tilt they imply for the fully scored population | **0.47 points** | ≤ 1.0 point: passes |

I do not loosen a limit after seeing the result. By the owner's rule ("if this check reveals a material new survivorship problem, STOP before freezing"), freeze gate K fails. Every other gate passes.

Nothing was changed because of the result. The freeze manifest is written as an unpinned **candidate**. If the owner accepts this residual, Data v2 can be frozen exactly as built, with no code change, data change or rerun.

No real return, IC, H022 gate or portfolio result was computed. 2018–2021 and the Holdout are untouched. Nothing was purchased.

## What was built

| Component | File(s) | What it does |
|---|---|---|
| Consolidated reference table | `src/qresearch/lean/qr_data_v2*.py` (16 files), built by `research/phase7/data_v2/build_data_v2.py` | One table of public SEC data and our own tables, no QuantConnect data. Contents:<br>(1) the data-v1 SEC correction layer, unchanged in substance;<br>(2) every periodic filing of every identified registrant (M2 filing dates, D111 cover-share counts);<br>(3) the verified identity extension;<br>(4) the restatement-guard reference;<br>(5) identity-continuity reference values;<br>(6) diagnostics only.<br>Nothing filed or effective after 2017-12-31. |
| Packing | `src/qresearch/v2pack.py` | JSON → lzma (preset 9, extreme) → base85, in chunks of 63,000 characters; SHA-256 of the raw JSON checked on load; loader `v2-lzma-b85-1` |
| Pure v2 layer | `src/qresearch/lean/qr_v2.py` | M2 filing match, restatement guard, identity presence rule, the frozen mechanical simulator, and the synthetic power study port (bit-identical to `P7_power.py`, tested) |
| Export / verification host | `strategies/X998_data_v2_export/main.py` | Same Score v1 pipeline as X993 v1.1. The SEC layer is installed by the host from the v2 table: data-v1-pinned modules are untouched (`universe.sec_corrections` off). Exports aggregates and digests only. |
| Analysis | `research/phase7/data_v2/x998_analysis.py` → `x998_summary.json` | Gate thresholds committed before any E998 output (43e26ec) |
| Freeze record | `src/qresearch/datafreeze_v2.py` → `research/phase7/data_v2/data_freeze_v2.json` | Candidate manifest (unpinned; status "CANDIDATE - NOT FROZEN") |
| Tests | `tests/test_data_v2.py`, `tests/test_data_freeze_v2.py` | table, rules, M2, guard, identity, mechanics, truncation, host aggregate-only output, freeze record |

## The 56 required items

### 1. Actual LEAN builds

| Run | Purpose | Commit | Build | QC backtest | Runtime | Result |
|---|---|---|---|---|---|---|
| E998-01 | export, 2011-01 → 2017-12 | 5c6854f | **18178** (default, recorded) | b94e25cc… | 688 s | completed, 0 orders |
| E998-02 | independent repeat of E998-01 | d699684 | **18178** | f6a5dcc3… | 669 s | completed, 0 orders |
| E998-03 | export truncated at 2013-12-31 | a1c81d8 | **18178** | 8146557b… | 364 s | completed, 0 orders |
| E998-04 | export + synthetic power study | 4f0a323 | **18178** | 9d1c1c36… | 2,715 s | completed, 0 orders |

No code changed between the four run commits: `git diff` of the host, the LEAN modules, the runner and the config rules is empty.

The runner's `code_sha256` differs per run by design, because it includes the generated `qr_params.py`, which carries the experiment id.

### 2. Code commit

- Build: 5c6854f.
- Gate thresholds: 43e26ec, committed before any output.
- Runs: as in item 1.
- Analysis fixes after the runs (items 32–33): in this checkpoint's commit.

### 3. Data v2 freeze manifest

`research/phase7/data_v2/data_freeze_v2.json`, written by `qresearch.datafreeze_v2`. It holds:
- SHA-256 of 45 files: runtime modules, the host, the offline builders, the evidence and both Score v1 specs;
- the frozen rules;
- the reference component hashes;
- the four runs' provenance;
- the gate results.

Status: **"CANDIDATE - NOT FROZEN (failed: K_identity_sanity_not_material, K_survivorship_bounds)"**. `MANIFEST_SHA256` stays unset until the owner decides.

### 4. Score v1 hash

Unchanged and pinned:
- spec SHA-256 `7d3ae5df…`;
- code hashes in `qresearch.p7score` / `p7pred`;
- `tests/test_p7_score_spec.py` and `tests/test_p7_pred_spec.py` pass.

The same code path (`qr_p7_score`, `qr_p7_export`, `qr_p7_mech`) runs in X998.

### 5. Final universe rule

A security is eligible at a monthly review if it passes the unchanged filters:
- US common stock, primary listing;
- the P7-CP1 price-series and corporate-event rules;
- the life rule `qr_p7.LIFE_GAP`;
- one class per company.

It also needs a market cap of at least $2B, taken from:
- QuantConnect's `market_cap` if it is > 0;
- otherwise a valid SEC market cap (item 6);
- otherwise the security is ineligible.

The data-v1 SEC correction layer (495 securities) is kept unchanged and not broadened.

### 6. Final market-cap fallback rule

SEC market cap = the single unambiguous cover-page share count × the raw close of the review session. Conditions:
- usable from the filing date + 1 day;
- cover date at most 135 days before the review;
- no interpolation;
- no weighted-average shares;
- multi-class companies stay unresolved.

### 7. SEC share age rule

The cover date may be at most **135 days** old. The audit counter `stale_share_count_used` is 0 in every run.

Among repaired stock-months, the cover date is a median 60 days old (p90: 93; maximum: 135).

### 8. Split rule

D111 logic: shares are adjusted by splits with an ex-date on or before the review day (the split history is filtered to that day). Splits after the review are never used.

### 9. Final M2 rule

A report is usable from the later of:
- the day it first appears in QuantConnect's stream;
- its SEC original periodic filing + 1 day (pre-XBRL filing dates from EDGAR submissions).

There is no FileDate and no +90-day rule.

| | Reports |
|---|---|
| Fed | 69,087 |
| Delayed by the SEC date | 154 |
| Unmatched to an SEC period (no fundamentals fed) | 62,358 |
| Revisions not re-fed | 4 |

### 10. Final identity-extension rule

- Identity-v2 dated rows are used as they are.
- Verified extension rows (SAFE / BOUNDED only, 1,807 rows) are used only while the security's feed presence is continuous since the row start (gap ≤ 60 days). 136 reports were left unmapped by a presence break.
- REJECT and ambiguous rows are never used.

### 11. Final restatement guard

Applies to quarterly revenue and total assets (P7-CP5d methodology). A report is blocked if all three hold:
- its value matches a later SEC re-report (> 0.5% from the first-filed value);
- it does not match the first-filed value;
- the later filing is not yet public + 1 day.

The reference covers 8,496 periods of 1,747 registrants with a later re-report. 90,076 periods were scanned.

### 12. Research window

- Sessions: 2011-01-03 → 2017-12-29.
- Monthly reviews: 84, 2011-01-31 → 2017-12-29.
- H022 decisions: 83, 2011-01-31 → 2017-11-30.
- Weekly checks: 325.
- History-only warm-up from 2008-07-01.

Nothing after 2017-12-31 is read.

### 13. Project file count

**33 files**, 942,000 characters of reference data:
- 16 table files (1 loader + 15 chunks);
- 17 code files (host, harness, Score v1 modules, `qr_v2`, `qr_xs` family, params).

For comparison: X997 had 47 and data v1 hosts 40+.

The owner's 25–28 target is **not reached**. The table is already lzma-compressed and base85-encoded, and each file is capped at 64,000 characters. Fewer files would require dropping rule data, which I did not do:
- the 1.9 MB filing / share table that M2 and the market-cap repair need;
- the 1.4 MB data-v1 SEC layer;
- the 0.4 MB guard reference.

The H022 modules would add about 2–3 files, still within QuantConnect's 50-file limit.

### 14. Packed-reference structure

JSON → lzma (preset 9 | extreme) → base85 → chunks of 63,000 characters:
- `qr_data_v2_00.py` … `qr_data_v2_14.py` hold the chunks;
- `qr_data_v2.py` is the loader (version `v2-lzma-b85-1`).

The loader joins, decodes, decompresses and checks SHA-256 against the pinned table hash before returning. Every date is a day number since 2000-01-01; the build is deterministic.

### 15. Reference hashes

| Component | SHA-256 |
|---|---|
| Whole table | `107b6b5534a83368f3a9620a8d96dc6fec1a14793aa0639a3787240b85346884` |
| Data-v1 SEC layer (`sec_v1`) | `54014632d67c36f851e482442350132ed4d7620abe21040af182c36e2786fae1` |
| SEC filings + cover shares (M2 / market cap, `f`) | `d6df94fe06dc91d8a36f247fee5f2bc067623752678039ab4a2af8ee7ba2ff75` |
| Identity extension (`ext`) | `93c60b652f079a4d7b7cc353b73e408b0ffb6bb8292ec82011679887481a5383` |
| Restatement-guard reference (`guard`) | `95d15aed27afb3a91d0a04c188e561777ac7ba847db1b19a80e44882f188b4e8` |
| Identity-continuity values (`idv`) | `201e70a2cffe672cdd4aae52201d4c02741b0af87c7a846b04853c28dd723f9c` |
| Diagnostics only (`diag`) | `f791716470d4200f5d6f5309578adefe40518f7c98d08c519618f71ec09cc11c` |
| SEC snapshot: data-v1 SEC table source | `fbdaa68a…` |
| SEC snapshot: P7-CP5e reference | `1ece9c48…` |
| SEC snapshot: `identity_extension.json` | `9b37bc0b…` |
| SEC snapshot: target population | `f751460b…` |

Per-file hashes are in `research/phase7/data_v2/data_v2_reference.json`.

### 16. Eligible stock-months

**90,370** in 2011–2017 (data v1: 93,687).

| Year | Eligible a month | from QC cap | from SEC repair | v1 SEC layer | Non-financial | H2 % of non-financial | Fully scored | Candidates (no hard disqualifier) | 75+ | 80+ | 85+ | 90+ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2011 | 872 | 653 | 141 | 79 | 663 | 46.6% | 353 | 268 | 12.9 | 5.6 | 1.3 | 0.5 |
| 2012 | 889 | 687 | 136 | 66 | 683 | 43.1% | 384 | 303 | 13.4 | 5.0 | 0.6 | 0.3 |
| 2013 | 1,024 | 793 | 164 | 67 | 789 | 41.1% | 459 | 408 | 9.9 | 3.5 | 0.3 | 0.1 |
| 2014 | 1,149 | 896 | 186 | 67 | 881 | 29.3% | 617 | 510 | 16.3 | 6.2 | 1.4 | 0.3 |
| 2015 | 1,180 | 941 | 183 | 55 | 889 | 23.7% | 672 | 445 | 23.2 | 8.8 | 4.1 | 1.4 |
| 2016 | 1,153 | 958 | 161 | 34 | 859 | 21.6% | 670 | 466 | 18.8 | 7.6 | 1.2 | 0.4 |
| 2017 | 1,263 | 1,078 | 150 | 35 | 938 | 24.3% | 707 | 555 | 28.3 | 12.9 | 2.8 | 0.8 |

### 17. SEC-repaired stock-months

| | Stock-months |
|---|---|
| Candidates for repair (QC cap missing, everything else passes, SEC identity with a shares table) | 24,220 |
| Repaired (SEC cap ≥ $2B) | **13,455** |
| SEC cap below $2B | 9,773 |
| No fresh share count | 992 |

Bands of the SEC market cap among those candidates:

| Band | Stock-months |
|---|---|
| < $1.5B | 6,593 |
| $1.5–1.8B | 2,022 |
| $1.8–2.0B | 1,158 |
| $2.0–2.2B | 922 |
| $2.2–2.5B | 1,290 |
| > $2.5B | 11,243 |

### 18. Recovered securities

Of the 560 target securities (frozen in P7-CP5e):
- **371** are recovered at least once;
- 232 of them later disappear.

Of the 18,915 lost stock-months, **13,038** are recovered (68.9%), including 66.8% of the stock-months of later-disappearing securities.

### 19. Unrecovered securities

189 securities are never recovered. By their last reason:

| Reason | In the universe at end-2017 | Later disappearing |
|---|---|---|
| Market cap below $2B | 56 | 18 |
| QC market cap missing, no SEC repair | 22 | 22 |
| No fundamentals | 1 | 67 |
| Reference or security type | 3 | — |

Lost stock-months by reason, and how many were recovered:

| Reason | Lost | Recovered |
|---|---|---|
| QC market cap missing | 15,235 | 13,038 |
| Below $2B | 1,300 | 0 |
| No fundamentals | 2,212 | 0 |
| Reference or security type | 168 | 0 |

Why the "market cap missing" stock-months were not repaired:

| Status | Stock-months |
|---|---|
| Repaired | 13,038 |
| No SEC identity | 757 |
| No shares table | 927 |
| No fresh share count | 456 |
| SEC cap below $2B | 57 |

### 20. Survivorship diagnostic

Share of stock-months whose security is still in the data-v1 universe at 2017-12-29:

| Year | Data v1 | Data v2 | Gap (points) |
|---|---|---|---|
| 2011 | 74.5% | 77.2% | +2.70 |
| 2012 | 78.3% | 80.1% | +1.76 |
| 2013 | 78.1% | 79.7% | +1.64 |
| 2014 | 79.1% | 80.4% | +1.32 |
| 2015 | 82.8% | 83.6% | +0.80 |
| 2016 | 90.1% | 89.8% | −0.27 |
| 2017 | 95.7% | 93.7% | −2.02 |
| **All** | **83.27%** | **84.06%** | **+0.79** |

Limits: within 2.0 points overall and 4.0 points in every year (P7-CP5e criterion MC7). **Passes.**

For comparison, the delivered new feed without repair had 90.0% (+6.7 points).

### 21. Identity REJECT / no-identity sanity check (owner item 7)

**Affected:** 161 securities (105 REJECT + 56 without an identity row), **4,656 eligible stock-months** (5.2% of 90,370).

The REJECT securities still use their own identity-v2 rows from their first XBRL filing on. Of their stock-months:
- 894 are fully scored anyway;
- about 3,700 carry H2 (no usable fundamentals).

| Year | Affected eligible stock-months | Share of eligible | Of which H2 | Of which fully scored | Retained fully scored stock-months |
|---|---|---|---|---|---|
| 2011 | 357 | 3.41% | 357 | 0 | 4,236 |
| 2012 | 399 | 3.74% | 368 | 31 | 4,577 |
| 2013 | 521 | 4.24% | 433 | 88 | 5,414 |
| 2014 | 703 | 5.10% | 553 | 150 | 7,256 |
| 2015 | 799 | 5.65% | 637 | 162 | 7,903 |
| 2016 | 827 | 5.98% | 590 | 224 | 7,817 |
| 2017 | 1,050 | 6.93% | 767 | 239 | 8,239 |

**Survival:** share of stock-months whose security is still in the Data v2 universe at the last review (2017-12-29):

| Group | Stock-months | Still present |
|---|---|---|
| Affected (REJECT + no identity) | 4,656 | **82.4%** |
| Retained fully scored | 45,442 | **87.5%** |
| **Difference** | | **5.05 points** |

The affected securities disappear somewhat more often, as successor registrants and companies without SEC periodic filings would.

**Implied survivorship tilt** on the fully scored population: 4,656 / (4,656 + 45,442) × 5.05 points = **0.47 points** towards survivors.

**Pre-set materiality criteria** (`x998_analysis.py`, committed before any output):
- tilt ≤ 1.0 point: **passes**;
- share of eligible stock-months ≤ 3% in every year: **fails** in every year, rising from 3.4% to 6.9%.

**Verdict under the owner's rule: material by the pre-set criteria → STOP before freezing.**

Two observations for the owner's decision. Neither changes the verdict.
1. "Affected" counts every stock-month of these securities, including 894 already fully scored. The stock-months actually lost to scoring are about 3,700 (4.1%, 3.4% in 2011 → 5.1% in 2017).
2. The bias they imply (0.47 points) is smaller than the P7-CP5e residual the owner already accepted (+0.79 points overall), and points in the same direction.

No identity rule was changed.

### 22. Remaining survivorship gap

The repaired universe is +0.79 points more survivor-rich than data v1 overall, between −2.0 and +2.7 points by year. This is the same as P7-CP5e.

The identity exclusion adds an estimated +0.47 points within the fully scored population (item 21).

### 23. Near-$2B diagnostics

- 922 repaired stock-months have an SEC cap between $2.0B and $2.2B.
- 379 stock-months between $1.8B and $2.2B rely on a share count more than 90 days old.

Where both caps exist, SEC vs QuantConnect agreement on the $2B decision is:
- **98.4%** away from the threshold (81,504 / 82,809);
- 95.7% within $1.8–2.2B (5,273 / 5,513).

The median absolute relative difference is 0.03% (p90: 1.96%).

### 24. H1–H7 counts

Hard-disqualifier bits, eligible stock-months, 2011–2017:

| Year | H1 financial | H1 no SIC | H2 | H3 | H4 | H5 | H6 | H7 | Duplicate class |
|---|---|---|---|---|---|---|---|---|---|
| 2011 | 1,912 | 595 | 5,649 | 166 | 81 | 0 | 2,356 | 141 | 12 |
| 2012 | 2,046 | 428 | 5,449 | 208 | 98 | 0 | 1,943 | 170 | 12 |
| 2013 | 2,423 | 405 | 6,213 | 301 | 123 | 0 | 1,054 | 165 | 14 |
| 2014 | 2,848 | 374 | 5,577 | 445 | 151 | 0 | 2,093 | 269 | 29 |
| 2015 | 3,117 | 365 | 5,064 | 375 | 125 | 0 | 4,335 | 353 | 48 |
| 2016 | 3,199 | 325 | 4,533 | 227 | 80 | 0 | 3,756 | 399 | 68 |
| 2017 | 3,499 | 397 | 5,279 | 361 | 62 | 0 | 2,520 | 461 | 81 |
| **Total** | **19,044** | **2,889** | **37,764** | **2,083** | **720** | **0** | **18,057** | **1,958** | **264** |

The weekly checks (325) apply H1/H2/H7 and, for stocks that ever reached 75+, H3–H6, exactly as X993 v1.1.

H2 among non-financials falls from 47% (2011) to 22–24% (2016–17). Early years have shorter SEC filing histories for the True TTM and the revenue baseline.

Field presence for non-financials, 2011 → 2017:

| Field | 2011 | 2017 |
|---|---|---|
| Revenue TTM | 66% | 89% |
| Gross profit TTM | 63% | 86% |
| Net income TTM | 67% | 88% |
| Operating cash flow TTM | 67% | 91% |
| Total assets | 97% | 98% |
| Equity | 97% | 98% |
| Valid revenue baseline | 74% | 85% |

Mappable to an SEC registrant: 97.3–97.7% every year.

### 25. Fully scored population by month / year

| Period | Min | Median | Mean | Max |
|---|---|---|---|---|
| 2011 | 304 | 357 | 353 | 376 |
| 2012 | 355 | 385 | 384 | 402 |
| 2013–2017 | 402 | 659 | 625 | 728 |
| All 84 months | 304 | 621 | 552 | 728 |

The per-month table is in `x998_summary.json` (`E998-01.population`; per review in the run output).

### 26. Candidate population

Fully scored with no hard disqualifier, i.e. the H022 population:

| | Min | Median | Mean | Max |
|---|---|---|---|---|
| A month | 163 | 436 | 422 | 595 |

It is lowest in the RISK_OFF months of 2011-08/09 and 2015-09/2016-02, when H6 (broken trend) hits more stocks.

### 27. ≥75 / ≥80 / ≥85 / ≥90 counts

Means a month:

| Threshold | Mean a month |
|---|---|
| 75+ | 17.5 |
| **80+** | **7.07** (only one month with zero) |
| 85+ | 1.65 |
| 90+ | 0.54 |

By year in item 16. Data v1 (P7-CP3R): 80+ 7.0 a month.

### 28. Score distribution

| Population | n | Mean | SD | p10 | Median | p90 | Max |
|---|---|---|---|---|---|---|---|
| Fully scored | 46,336 stock-months | 43.6 | 16.8 | 21 | 43 | 66 | 94 |
| Candidates | 35,458 | 47.7 | 15.5 | 26 | 48 | 68 | 94 |

The maximum score is 94, as on data v1. Five-point histograms are in `x998_summary.json`.

### 29. Layer distributions

Fully scored population:

| Layer | Points | Mean | Median | SD | p90 |
|---|---|---|---|---|---|
| Technical | 0–40 | 17.9 | 20 | 11.9 | 33 |
| Fundamental | 0–45 | 18.0 | 17 | 10.1 | 32 |
| Sector | 0–15 | 7.7 | 8 | 4.4 | 15 |

Correlations:
- T–F: −0.01;
- T–S: +0.23;
- F–S: −0.01.

80+ still needs strength in all three layers.

### 30. Regime counts

84 reviews (SPY trend × point-in-time breadth, unchanged):

| Regime | Reviews | Share |
|---|---|---|
| STRONG | 63 | 75% |
| NORMAL | 9 | 11% |
| WEAK | 7 | 8% |
| RISK_OFF | 5 | 6% |

Data v1 (P7-CP3): STRONG 75%, RISK_OFF 6%.

### 31. Sector counts

80+ candidates by FF12 sector, stock-months:

| Sector | Stock-months |
|---|---|
| BusEq | 188 |
| Other | 102 |
| Hlth | 92 |
| Utils | 61 |
| Shops | 50 |
| Manuf | 33 |
| NoDur | 29 |
| Telcm | 18 |
| Enrgy | 10 |
| Durbl | 8 |
| Chems | 3 |

The mechanics' ≤ 3-per-FF12 cap skipped 119 otherwise-qualifying entries.

### 32. Determinism result

**PASS.** E998-01 vs E998-02 (independent runs, same code) are identical on every digest:
- reference inputs (the loader checks the table hash);
- universe by year;
- first-seen ledger by year and to 2013;
- monthly eligibility sets (84);
- monthly score tables (84);
- H1–H7 counts;
- score distributions;
- mechanics.

All aggregates are equal apart from timing fields. Panel build time differs (90.7 s vs 86.5 s); the analysis now treats it as a timing field, documented.

E998-04 (power mode) also reproduces E998-01's export digests exactly.

### 33. Truncation result

**PASS.** E998-03 ends on 2013-12-31. Against E998-01, all 35 shared monthly reviews (2011-01 → 2013-11) have identical score tables, eligibility sets and per-review aggregates. Also identical:
- the first-seen ledger for every year 2008–2013;
- the ledger to 2013-12-31;
- the universe digests for 2011 and 2012.

The whole-year 2013 universe digest differs, but only by construction. A run ending on 2013-12-31 never reaches its December review, which QuantConnect stamps 2014-01-01, so its 2013 digest covers 11 reviews instead of 12. I fixed my analysis to compare whole-year digests only for years with identical review sets; the partial year is covered review by review. This is a measurement correction, not a rule change, documented in `x998_analysis.py`.

### 34. PIT-audit result

**All 0, in all four runs:**

| Counter | Value |
|---|---|
| Report fed before its SEC filing + 1 | 0 |
| Report fed before first seen | 0 |
| Future identity row used | 0 |
| Fed after a restatement-guard trigger | 0 |
| SEC share count > 135 days old used | 0 |
| Share filing not yet public | 0 |
| Repaired with a vendor cap | 0 |
| Repaired below $2B | 0 |
| Record older than 200 days | 0 |
| Revenue baseline from later data | 0 |
| Baseline used despite a life / CIK reject | 0 |

Truncation (item 33) shows that later data does not change earlier state. A spot check recomputing technical inputs from full history found 0 mismatches in 168 samples.

### 35. Split-audit result

**PASS:**
- 223 of 224 evaluable splits (≥ 1.4×, 2011–2017) give a continuous SEC market cap;
- 1 is ambiguous;
- 34 have no SEC identity and 10 no SEC market cap (not evaluable).

### 36. SEC identity-continuity result

Reports matched through extension rows are compared with SEC first-filed values (periods ending by 2010):

| Field | Extension rows | Identity-v2 rows |
|---|---|---|
| Total assets | **97.2%** (1,661 / 1,709) | 95.6% |
| Revenue | 86.2% (2,459 / 2,852) | 91.7% |

Total assets is the stronger identity test: it is a balance-sheet level with no derivation, and it matches as well as P7-CP5e (97.9%).

The P7-CP5e revenue figure (92.8%) covered only 263 reports. This check covers every pre-2011 extension-mapped report (2,852). The two SEC reference tables agree 100% on all shared keys, so the lower revenue rate reflects quarterly-definition differences in 2008–2010 reports, not identity errors.

This check is diagnostic and feeds no rule.

### 37. Restatement-guard blocked count

| Measure | Count |
|---|---|
| Reports blocked | **114** |
| Reports matched to an SEC period (all fed or held) | ~69,200 |
| Blocked share | **0.16%** |

All 114 are released only once the later SEC filing is public (`fed_after_guard_trigger` = 0).

By year:

| Year | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 |
|---|---|---|---|---|---|---|---|---|---|
| Blocked | 2 | 4 | 8 | 25 | 25 | 13 | 14 | 21 | 2 |

Trigger categories:

| Category | Count |
|---|---|
| Revenue: later value not yet public | 103 |
| Revenue: later value public | 26 |
| Total assets: later value not yet public | 21 |
| Total assets: later value public | 5 |

### 38. Revenue-baseline integrity result

68,769 store-wide baselines were checked against the security life and the SEC registrant:
- 7 rejected by the life rule;
- 12 rejected by the CIK rule;
- 0 baselines built from data later than the baseline day;
- 0 rejected baselines used.

### 39. QuantConnect compliance result

**All four runs passed** the compliance review (accepted at compile time, not stopped mid-run). The runs exported:
- counts, distributions and SHA-256 digests;
- synthetic power results;
- no vendor values and no returns.

### 40. Aggregate-export feasibility

**Feasible.** The aggregate summary travels in chunks through the established result channel. Run resources:

| Run | Wall time | Memory |
|---|---|---|
| E998-01 | 675 s | 5.95 GB |
| E998-03 | 353 s | — |
| E998-04 | 2,703 s (power study 2,035 s) | — |

### 41. Data v1 vs Data v2 structural comparison

| | Data v1 (LEAN 18131, E993-02) | Data v2 (LEAN 18178, E998) |
|---|---|---|
| Fundamental timing | vendor FileDate (+90 days when estimated) | M2: max(first seen, SEC filing + 1) |
| Market cap | vendor | vendor if > 0, else SEC cover shares × raw price |
| Universe stock-months | 93,687 | 90,370 (−3.5%) |
| Survivor share | 83.3% | 84.1% (+0.8 points) |
| Fully scored a month | 196–612 | 304–728 |
| H022 population (candidates) | about 196–612 | 163–595 |
| 80+ a month | 7.0 | 7.07 |
| Regime STRONG / RISK_OFF | 75% / 6% | 75% / 6% |
| Mechanical orders a year | 47 | 46.6 |
| Cost at $100K / $200K | 0.80% / 0.64% | 0.79% / 0.63% |
| Mean utilisation | 69% | 69% |
| Restatement handling | data-v1 restatement blocks | P7-CP5d guard (114 blocked) |

### 42. Synthetic power-study methodology

Identical to P7-CP4 (`P7_power.py`, D175), ported to `qr_v2.power_scenario` (bit-identical, tested). It runs in-cloud on the **Data v2** score tables:
- the first 83 reviews;
- the H022 population;
- real scores, sectors, risk bands, momentum bands, fundamental subtotals and ADV;
- no prices.

Returns are **synthetic**: market + sector + three style factors + fat-tailed idiosyncratic noise + a planted edge κ.

Procedure:
- 200 datasets per κ;
- c_IC from 2,000 null worlds;
- false promotion from 1,000 holdout null worlds;
- three scenarios (main, optimistic, pessimistic);
- the full frozen G1–G4 gate procedure.

No real return was used.

### 43. Data v2 50% power threshold

Full G1–G4 procedure:

| Scenario | IC needed (v2) | IC needed (v1) | 80+ excess (v2) | 80+ excess (v1) |
|---|---|---|---|---|
| Main | **0.034** | 0.033 | 6.9% / yr | 6.3% |
| Optimistic | 0.028 | 0.027 | 5.5% | 4.9% |
| Pessimistic | 0.041 | 0.040 | 8.5% | 8.7% |

Significance gate alone, main scenario: IC 0.026.

### 44. Data v2 80% power threshold

| Scenario | IC needed (v2) | IC needed (v1) | 80+ excess (v2) | 80+ excess (v1) |
|---|---|---|---|---|
| Main | **0.049** | 0.047 | 9.8% / yr | 10.2% |
| Optimistic | 0.042 | 0.040 | 8.4% | 8.3% |
| Pessimistic | 0.059 | 0.056 | 12.1% | 12.1% |

**Power has not materially changed.**

### 45. Synthetic false-promotion result

| Scenario | Full procedure | G1 alone | Synthetic c_IC | Null t_IC SD / p99 |
|---|---|---|---|---|
| Main | **0.1%** | 0.4% | **2.53** | 1.01 / 2.52 |
| Optimistic | 0.0% | 0.2% | 2.67 | 1.04 / 2.66 |
| Pessimistic | 0.1% | 0.3% | 2.54 | 0.99 / 2.52 |

Data v1 (main): false promotion 0.3%, synthetic c_IC 2.50.

The real c_IC for Data v2 is **not** computed. It needs the 5,000 identity-tethered null worlds, which are not authorised.

### 46. Estimated engineering / run plan for H022 next stage

Not authorised; for planning only.

1. **Host.** Port the S023 predictive host to Data v2: X998's pipeline plus `qr_p7_pred`. Pin a new panel digest from the Data v2 tables; the H022 spec and gates stay unchanged. About 36 project files.
2. **Canary.** One plumbing run, about 15 minutes.
3. **Null.** 5 × 1,000 identity-tethered null worlds. About 5 runs of 15–45 minutes, so 1.5–3 hours of node time.
4. **Pin.** Pin the new c_IC and null hash in a commit before any real run.
5. **Owner review.**
6. **Real run.** One real evaluation (E-number to be assigned).

Every run records its build. A changed panel digest stops the work (the `default_build_digest_verified` policy). No new purchase is needed: the $24/month subscription is enough.

### 47–54. Confirmations

| # | Confirmation |
|---|---|
| 47 | **No real future return computed**: no stock, portfolio or SPY return, CAGR, Sharpe or drawdown. X998 has no forward-return code path (tested). |
| 48 | **No real IC computed**: only synthetic ICs in the power study. |
| 49 | **No H022 gate computed** on real data. |
| 50 | **No portfolio performance computed**: the mechanics are a P&L-free order simulation (counts, utilisation and cost estimates only). |
| 51 | **No orders**: 0 orders in all four runs. |
| 52 | **2018–2021 untouched**: every run ends at or before 2017-12-31; the reference table holds nothing filed after 2017. |
| 53 | **Holdout untouched**: `HOLDOUT_UNLOCK.md` absent; `holdout_unlocked` false in every run. |
| 54 | **Nothing purchased.** |

### 55. Final status

```
NOT FROZEN — Data Infrastructure v2 failed one or more freeze gates
```

| Gate | Result |
|---|---|
| A. Score v1 hash unchanged | pass |
| B. M2 timing implemented exactly | pass |
| C. Market-cap repair implemented exactly | pass |
| D. SEC identity extension implemented exactly | pass |
| E. Restatement guard implemented | pass |
| F. PIT violations = 0 | pass |
| G. Split audit | pass |
| H. Determinism | pass |
| I. Truncation invariance | pass |
| J. 2011–2012 operational | pass (fully scored 304–402 a month) |
| **K. Survivorship within the approved bounds** | **fail**: MC7 gap and residuals pass; the identity sanity check (item 21) exceeds its pre-set 3%-a-year limit |
| L. QuantConnect compliance | pass |
| M. Aggregate outputs exportable | pass |
| N. No real return inspected | pass |
| O. 2018–2021 untouched | pass |
| P. Holdout untouched | pass |

### 56. Exact next owner decision

Decide on the identity residual of item 21. Options:

1. **Accept it as a documented residual and freeze Data v2 as built.**
   - The residual: 161 securities, about 4–7% of eligible stock-months a year without usable fundamentals, implying a +0.47-point survivorship tilt.
   - Steps: pin the candidate manifest (`MANIFEST_SHA256`), mark it FROZEN and commit. No code or data change and no rerun; the existing E998 evidence stands.
   - H022 null calibration would then still need its own explicit authorisation.
   - **Recommended:** the tilt is half the residual already accepted, every other gate passes, and power is unchanged.
2. **Do not freeze; commission a feasibility study** of SEC identity for the successor registrants and the 56 securities without an identity row (offline public SEC data first). It would cost another build-and-verify cycle with an uncertain yield.
3. **Close H022** as not evaluable on available data.

Until the owner decides, nothing further runs.

## Fixes made during this checkpoint (bugs only; no rule changed)

1. **Population comparison (analysis).** The P7-CP5e reference populations are X997's fully scored counts; my script first compared them with X998's eligible counts. Now like for like (−0.7% to −1.1%); threshold unchanged.
2. **Gate labelling (analysis).** The owner's gate D is "SEC identity extension implemented exactly". The item-7 sanity check, a survivorship STOP condition, is now evaluated under gate K with the same pre-set criteria. The outcome is the same either way.
3. **Timing fields and truncation partial year (analysis).** As in items 32–33.
4. **Before the runs:** `qr_p7_mech.py` added to the runner's upload list; the reference table compacted from 34 to 33 project files (lossless).

## Records

- **Experiments:** E998-01, E998-02, E998-03, E998-04, all infrastructure, in `experiments/INDEX.csv`.
- **Programme totals:**
  - hypotheses: 22 (H001–H022);
  - no new hypothesis or strategy;
  - experiments: four infrastructure runs added; all earlier records preserved.
- **Old c_IC:** 2.390976216956 is labelled **DATA_V1_ONLY / UNUSED_ON_V2** (`qresearch.p7pred.C_IC_STATUS`, tested). It is never used on Data v2.

**STOP.** Awaiting the owner's decision (item 56). Not run, and not authorised:
- the H022 canary;
- null worlds;
- a new c_IC;
- any real IC or return;
- G1–G4;
- a portfolio;
- 2018–2021;
- the Holdout.
