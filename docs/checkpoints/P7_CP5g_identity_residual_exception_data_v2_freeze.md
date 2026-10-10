# P7-CP5g — Owner Acceptance of Identity Residual and Final Data v2 Freeze

**Date:** 2026-10-10. **Decisions:** D192 (owner decision, `docs/owner/2026-10-10_p7cp5g_identity_residual_exception_freeze.md`), D193 (this checkpoint). **Status:** STOPPED awaiting the owner.

## Short answer

Data Infrastructure v2 is **frozen exactly as built in P7-CP5f**, with an owner-approved exception to Gate K. Nothing was rebuilt, rerun or recomputed. Only three things were done:
1. the owner decision was recorded;
2. the exception was written into the freeze record beside the original, still-failed Gate K result;
3. the manifest was pinned.

> **Permanent research record.** Data v2 did not technically pass every original freeze criterion. Gate K failed because the identity-affected population exceeded the pre-registered 3%-per-year incidence threshold. The owner knowingly accepts this residual without changing the threshold because the measured survivorship effect is only +0.47 percentage points, below the 1.0-point materiality bound, every PIT/integrity gate passed, and no real H022 result has yet been observed.

Freezing Data v2 does not authorise any H022 work.

## The 39 required items

### 1. Owner decision ID

**D192** (owner, 2026-10-10): Option 1 of P7-CP5f item 56. **D193** records this checkpoint.

### 2. Exact identity residual accepted

| Item | Value |
|---|---|
| Affected securities | **161** |
| SEC identity REJECT (successor registrants: spin-offs, renamed successors) | **105** |
| Without a usable SEC identity row | **56** |
| Affected eligible stock-months, 2011–2017 | 4,656 of 90,370 (about 3,700 of them without usable fundamentals, H2) |
| Survival to end-2017: affected | 82.4% |
| Survival to end-2017: retained fully scored | 87.5% |

### 3. Original failed Gate K criterion

```
Gate K:
FAILED under the original pre-registered 3%-per-year identity-incidence criterion.
```

Resolution: **OWNER-APPROVED EXCEPTION** (D192).

The original gate results in `research/phase7/data_v2/x998_summary.json` are unchanged:
- `K_identity_sanity_not_material` = false;
- `K_survivorship_bounds` = false;
- `all` = false.

The frozen manifest copies them as they are. A test checks they are never relabelled.

### 4. Original 3% threshold

The affected share of eligible stock-months must be **≤ 3% in every year**. It was fixed in `x998_analysis.py`, commit 43e26ec, before any E998 output existed.

It is **unchanged** (`TH["identity_excluded_share_year"] = 0.03`, tested).

### 5. Actual annual affected-share range

| 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 |
|---|---|---|---|---|---|---|
| 3.41% | 3.74% | 4.24% | 5.10% | 5.65% | 5.98% | 6.93% |

The criterion fails in every year.

### 6. Measured survivorship tilt

**+0.47 percentage points** towards survivors in the fully scored population:

4,656 / (4,656 + 45,442) × (87.5% − 82.4%)

### 7. 1.0-point survivorship threshold result

**Passed.** 0.47 ≤ 1.0, a pre-registered limit fixed at the same time as the 3% criterion and also unchanged.

### 8. Why this is an owner exception, not a retroactive threshold change

- The 3% criterion and its FAILED result stay in the permanent record, unaltered.
- No threshold was edited, and no gate was re-evaluated or relabelled.
- The owner made a separate, explicit governance decision to accept a known, measured residual. The decision is recorded beside the failure, not in place of it.
- The decision was made **before** any H022 real return, real IC, null threshold or gate result existed on Data v2. It therefore cannot have been influenced by research results.
- Owner's reasoning:
  - the measured survivorship effect (+0.47 points) is below the 1.0-point limit;
  - it is smaller than the +0.79-point overall universe residual the owner had already accepted;
  - every PIT and integrity gate passed.

### 9–13. Confirmations: no changes, no reruns

| # | Confirmation | Evidence |
|---|---|---|
| 9 | **No code changed** that defines data, rules or scores | The only source edits are the freeze-record module `qresearch.datafreeze_v2` (exception record, status, pin) and its tests. Every frozen file's SHA-256 in the manifest is identical to the P7-CP5f candidate. |
| 10 | **No data changed** | Reference table, identity extension, REJECT / no-identity lists, filing / share table and guard reference are unchanged (table SHA-256 `107b6b55…`, as in P7-CP5f). |
| 11 | **No rule changed** | Universe, market-cap repair, M2, identity, guard, Score v1, H1–H7, mechanics and window are identical (the manifest `rules` block is unchanged). |
| 12 | **No threshold changed** | Gate thresholds in `x998_analysis.py` are unchanged (tested). |
| 13 | **No rerun occurred** | E998-01..04 not rerun; no QuantConnect run in this checkpoint; `x998_summary.json` unchanged. |

The candidate manifest (SHA-256 `d09f20fc…`, commit 0837ce6) differs from the final one only in three places:
- the `status` field;
- the added `gate_k_exception` record;
- the added `candidate_manifest_sha256` reference.

### 14. Final freeze-manifest SHA-256

```
cf833f6fd4b8c4f124e9416b3d0722f61da93b97bdb22b1664aad13f969177fb
```

Pinned as `qresearch.datafreeze_v2.MANIFEST_SHA256`. `tests/test_data_freeze_v2.py` recomputes the manifest and every file hash.

Candidate it finalises: `d09f20fcca4290faf664bc07511cce048f4458884c84871c53703d3cf27faddb`.

### 15. Final Data v2 status

```
FROZEN — OWNER-APPROVED GATE K EXCEPTION
```

The manifest freezes 45 files:
- runtime modules, the X998 host and the packed reference table;
- offline builders and evidence;
- both Score v1 specs.

It also holds the frozen rules, reference hashes, the E998-01..04 provenance and the original gate results.

### 16. Score v1 hash

- Spec SHA-256: `7d3ae5df2fb5ecfaf8338e1a1d43f01c7a3060e73e33bf1007560981234eed9b` (`qresearch.p7score`).
- Code hashes: as pinned in `p7score` / `p7pred`.
- Predictive spec: `2c99f962…`.

All unchanged.

### 17. Data v2 reference hash

Whole table: `107b6b5534a83368f3a9620a8d96dc6fec1a14793aa0639a3787240b85346884`.

| Component | SHA-256 |
|---|---|
| sec_v1 | `54014632…` |
| Filings / cover shares | `d6df94fe…` |
| Identity extension | `93c60b65…` |
| Guard | `95d15aed…` |
| idv | `201e70a2…` |
| diag | `f7917164…` |

Loader `v2-lzma-b85-1`; 16 table files; 33 project files.

### 18. M2 rule

A fundamental report is usable from the later of:
- the day it first appears in QuantConnect's stream;
- its SEC original periodic filing + 1 day (pre-XBRL filing dates from EDGAR submissions).

No FileDate, no +90-day rule. A report without an SEC period match is never fed.

### 19. Universe rule

Eligible at a monthly review if it passes the unchanged filters:
- US common stock, primary listing;
- P7-CP1 price-series and corporate-event rules;
- life rule `qr_p7.LIFE_GAP`;
- one class per company.

And it needs a market cap ≥ $2B from:
- QuantConnect's `market_cap` if > 0;
- else a valid SEC market cap (item 20);
- else the security is ineligible.

The data-v1 SEC correction layer (495 securities) is kept as is and not broadened. Financials and REITs are excluded by SEC SIC at filing (H1).

### 20. Market-cap repair rule

SEC market cap = the single unambiguous cover-page share count × the review session's raw close. Conditions:
- usable from filing + 1 day;
- cover date at most 135 days old;
- no interpolation;
- no weighted-average shares;
- multi-class companies unresolved;
- D111 split logic (only splits with an ex-date on or before the review day).

### 21. Identity-extension rule

- Dated identity-v2 rows are used as they are.
- Verified extension rows (SAFE / BOUNDED only, 1,807 rows) are used only while the security's feed presence is continuous since the row start (gap ≤ 60 days).
- REJECT and ambiguous rows are never used.
- No current identity is backdated.

### 22. Restatement-guard rule

Quarterly revenue and total assets (P7-CP5d methodology). A report is blocked if all three hold:
- its value equals a later SEC re-report (> 0.5% from the first-filed value);
- it does not equal the first-filed value;
- that later filing is not yet public + 1 day.

Reference: 8,496 periods of 1,747 registrants.

### 23. Research window

- Sessions: 2011-01-03 → 2017-12-29.
- Monthly reviews: 84.
- H022 decisions: 83, 2011-01-31 → 2017-11-30.
- Weekly checks: 325.
- History-only warm-up from 2008-07-01.
- Nothing after 2017-12-31 is read.

### 24. PIT audit result (from P7-CP5f, not recomputed)

**0 violations** on all 11 counters, in all four runs.

### 25. Determinism result (from P7-CP5f)

**PASS.** E998-01 and E998-02 are identical on every digest:
- universe;
- ledger;
- eligibility;
- score tables;
- H counts;
- distributions;
- mechanics.

### 26. Truncation result (from P7-CP5f)

**PASS.** E998-03 (ends 2013-12-31) is identical to the full run on all 35 shared months and on the ledger to 2013.

### 27. Split result (from P7-CP5f)

**PASS:** 223 of 224 evaluable splits are continuous.

### 28. QuantConnect compliance result

**PASS** in all four runs (LEAN 18178, default build recorded). They were accepted at compile time and not stopped. Only aggregates and digests were exported.

The other P7-CP5f gates also passed:

| Gate | Result |
|---|---|
| Score v1 hash (A) | PASS |
| M2 timing (B) | PASS |
| Market-cap repair (C) | PASS |
| Identity extension implemented exactly (D) | PASS |
| Restatement guard (E) | PASS |
| 2011–2012 operational (J) | PASS |
| Aggregate export (M) | PASS |
| No real return (N), 2018–2021 (O), Holdout (P) | PASS |

### 29. Population summary (descriptive, non-predictive)

| Measure | Value |
|---|---|
| Universe stock-months 2011–2017 | 90,370 (data v1: 93,687) |
| Survivor share | 84.1% (data v1: 83.3%) |
| Fully scored stocks a month | 304–728 (2011: 304–376; 2012: 355–402) |
| H022 population (no hard disqualifier) | 163–595 a month |
| Mean 80+ candidates a month | 7.07 |
| Mean capital utilisation | 69% |
| Mechanical orders a year | 46.6 |
| Estimated cost at $100K | 0.79% a year |
| Estimated cost at $200K | 0.63% a year |

### 30. Synthetic power summary (from P7-CP5f, not rerun)

| Main scenario | Data v2 | Data v1 |
|---|---|---|
| IC needed for 50% power | **≈ 0.034** | 0.033 |
| IC needed for 80% power | **≈ 0.049** | 0.047 |
| Synthetic false promotion | **≈ 0.1%** | 0.3% |
| Synthetic c_IC | 2.53 | 2.50 |

The synthetic c_IC comes from synthetic returns and is **not** the empirical H022 null threshold. That threshold does not exist yet (item 34).

### 31. Old c_IC remains Data-v1-only

c_IC = 2.390976216956 stays labelled **DATA_V1_ONLY / UNUSED_ON_V2**:
- `qresearch.p7pred.C_IC_STATUS`, tested;
- the freeze rules (`old_c_ic`).

It must never be used on Data v2.

### 32–37. Confirmations

| # | Confirmation |
|---|---|
| 32 | **No real future return has ever been computed on Data v2**: no stock, portfolio or SPY return, CAGR, Sharpe or drawdown. |
| 33 | **No real H022 IC has been computed** on Data v2 (or on any data). |
| 34 | **No empirical Data v2 null threshold exists yet**: no identity-tethered null world has been run on Data v2. |
| 35 | **2018-01-01 → 2021-12-31 untouched.** |
| 36 | **Holdout 2022-01-01 → 2026-08-31 untouched** (`HOLDOUT_UNLOCK.md` absent). |
| 37 | **Nothing purchased.** The subscription stays at $24/month. |

### 38. Final status

```
FROZEN — Data Infrastructure v2
Owner-approved Gate K identity residual exception
```

### 39. Exact next owner decision required

Whether to authorise the next stage, **H022 on Data v2**. Planned workflow (not started, not authorised):
1. **Canary.** One plumbing run of the H022 predictive host ported to Data v2: X998's frozen pipeline plus `qr_p7_pred`, with the H022 spec and gates unchanged and a new Data v2 panel digest pinned.
2. **Null worlds.** 5,000 new identity-tethered null worlds in five runs of 1,000.
3. **New c_IC.** Calculate the new empirical c_IC: the 50th largest null t_IC, floor 2.326.
4. **Pin.** Pin the c_IC and the null-result hash in a commit before any real run.
5. **Owner review.**
6. **Real evaluation.** One real H022 evaluation.

Estimated QuantConnect time is about 1.5–3 hours on the existing node, with no purchase. The owner may authorise step 1 alone, steps 1–4, or decline.

**STOP.** Not run, and not authorised:
- H022 canary;
- null worlds;
- new c_IC;
- real returns;
- real IC;
- G1–G4;
- portfolio;
- 2018–2021;
- Holdout.
