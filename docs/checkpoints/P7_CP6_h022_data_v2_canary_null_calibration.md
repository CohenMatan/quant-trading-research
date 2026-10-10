# P7-CP6 — H022 Data v2 Canary and Null Calibration

**Date:** 2026-10-10. **Decisions:** D194 (owner approval, `docs/owner/2026-10-10_p7cp6_h022_v2_null_calibration.md`), D195 (c_IC pinned), D196 (this checkpoint). **Status:** STOPPED awaiting the owner.

## Short answer

The H022 null calibration on frozen Data v2 is complete and valid:
- **Canary.** It passed every check (E999-02, 25 of 25).
- **Null worlds.** All 5,000 ran: seeds 1–5,000 exactly, on the identical pinned panel, on one QuantConnect build, with 0 orders.
- **Rerun.** An independent rerun of a pre-specified seed sample reproduced every world exactly.

> **New Data v2 threshold: c_IC = 2.3798883324991866**
>
> It is the 50th largest of the 5,000 null t_IC values. This is the same rule as Data v1, and the 2.326 floor does not bind. It was pinned and merged in Git (merge 6d6573f, PR [CohenMatan/quant-trading-research#75](https://github.com/CohenMatan/quant-trading-research/pull/75)) **before any real H022 evaluation**. No real evaluation has been run.

Under the null, the full four-gate procedure promotes **5 of 5,000 worlds (0.10%)**.

The null distribution is close to the Data v1 one:

| | Data v1 | Data v2 |
|---|---|---|
| c_IC | 2.391 | 2.380 |
| Mean null t_IC | 0.195 | 0.181 |
| SD | 0.927 | 0.937 |
| False promotion | 0.14% | 0.10% |

The real Score v1 → future-return relationship is still sealed. No real IC, t_IC, quintile, 80+ return or gate has been computed on any data.

**CALIBRATED — Data v2 c_IC pinned, real H022 still sealed**

## How it was built

**Host: S024 v1.0** (X999 = byte copy, used as the canary).
- It subclasses the **frozen Data v2 host X998**. X998 is uploaded byte-identically as the module `qr_x998.py`, and its hash equals the frozen-manifest entry.
- So the whole Data v2 pipeline is the frozen code:
  - universe and SEC market-cap repair;
  - M2 timing and identity;
  - restatement guard and revenue baseline;
  - Score v1.
- The subclass only adds what H022 needs:
  - each reviewed stock's market cap, for the size diagnostic;
  - the panel's raw open and split × dividend multiplier.
- Its population, response, null, real-mode and canary steps are copied **verbatim** from the Data-v1 H022 host S023 v1.1; a test compares the sources.
  - One rename: S023's panel-digest helper became `_h_digest`, because X998 already has its own `_digest` (its ledger digest).
  - The H022 statistics module `qr_p7_pred` is the unchanged, pinned file.

## The 53 required items

### 1. Owner approval ID

**D194** (2026-10-10): steps 1–3 only.

### 2. Frozen Data v2 manifest hash

`cf833f6fd4b8c4f124e9416b3d0722f61da93b97bdb22b1664aad13f969177fb`.
- Verified at every run's build commit.
- Every uploaded Data v2 / Score v1 file equals its manifest hash (canary check 2; null `uploaded_all`).

### 3. Score v1 hash

- Spec SHA-256: `7d3ae5df…`.
- Code: `qr_p7_score.py` `84b67317…`, `qr_p7_export.py` `40e1410e…`, `qr_p7.py` `86abb2b2…`, all unchanged and checked on the uploaded files.

### 4. H022 spec hash

`2c99f9623065a0d9576f35ea208733c47ce5ec3bbfe2f587ab2a9451b0061f58` (unchanged).

### 5. Null-method hash

| File | SHA-256 |
|---|---|
| `qr_p7_pred.py` (Tether, run_world, critical_value, promotion) | `bc6fd8e8…` |
| `qr_h020_stats.py` (identity tether) | `426d3721…` |
| `qr_xs.py` (ranks, Newey-West, order statistic) | `bd69bc6a…` |

All unchanged from Data v1; the runner verified QuantConnect's stored copy of `qr_p7_pred.py` before compiling.

### 6. Actual LEAN build(s)

**v2.5.0.0.18178** (QuantConnect default) in all eight runs, recorded under `default_build_digest_verified`.

### 7. Canary experiment ID

| Run | Result |
|---|---|
| **E999-02** | Passed |
| E999-01 | Superseded: identical digests, but that host version did not yet export the PIT audit counters, so check 25 could not be evaluated. Fixed by exporting them; nothing else changed. |

### 8. Canary status

**Completed** (QuantConnect backtest `cf7c33d5…`, build commit 14ef5b9, 0 orders).

### 9. Canary panel digest

`09b1de410810c2dc4c972975541e78c0eaeee19d6934836a4fe9d88ed37eeaf0`. Identical in E999-01 and E999-02; pinned as `qresearch.p7pred_v2.PANEL_SHA256` before any null world.

It covers, per decision:
- the population ids and the regime;
- the score-side inputs (score, sector, momentum, size);
- the responses at all three horizons.

Separately exported digests:

| Digest | SHA-256 |
|---|---|
| Score side | `score_side_sha256` |
| Response side | `response_side_sha256` |
| Response availability | `availability_sha256` |
| Calendar | `calendar_sha256` |
| Securities | `sids_sha256` |

These are hashes only; no values.

### 10. Number of decision dates

**83**, 2011-01-31 → 2017-11-30. 84 reviews; the last response ends 2017-12-29. 325 weekly checks; the calendar matches.

### 11. Population checks

- Score v1 tables and eligibility sets are **identical to the frozen E998-01 export for all 84 reviews**.
- The H022 population per decision equals E998-01's no-disqualifier candidates.
- Regimes are identical.
- Population: 163–585 stocks per decision (mean 420); 80+ stocks 7.1 per month (one month without).
- Market cap and momentum are present for every population row.

### 12. Response-timing check

Over 102,913 responses checked across all horizons:
- entry always after t;
- never on or before t's day;
- exit always inside the window;
- every response independently recomputed: 0 value or status mismatches;
- no price after 2017-12-29.

Primary-horizon status:

| Status | Count |
|---|---|
| ok | 34,755 |
| truncated | 90 |
| no bar after t | 14 |
| unverified split (excluded) | 4 |

### 13. Corporate-action integrity result

- 120 responses (split, dividend, truncated and plain classes) recomputed from fresh single-security histories: **120 of 120 agree to 1e-9**, with the same status.
- Response future / past / truncation invariance: 80 of 80 unchanged.
- Whole reviews re-scored on truncated and future-perturbed prices: 0 mismatches.

### 14. Null-plumbing check

All on synthetic responses only:
- the tether gives exact permutations with no self-match and is deterministic;
- Newey-West equals an independent computation (maximum difference 4.4e-16);
- the complete G1–G4 null procedure ran for 10 worlds, all complete, with **no date in any world reproducing the identity (real) assignment**.

### 15. QuantConnect compliance result

**Pass.** All eight runs were accepted at compile time and completed. Only aggregates, digests and per-world null statistics were exported.

### 16. Canary PASS/FAIL

**PASS, 25 of 25** (`research/phase7/cp6/P7_CP6_canary_E999-02.json`). PIT audit: all 11 counters 0.

### 17. Null batch experiment IDs

E024-01, E024-02, E024-03, E024-04, E024-05, plus the determinism rerun E024-06.

### 18. Seeds in each batch

| Run | Seeds |
|---|---|
| E024-01 | 1–1,000 |
| E024-02 | 1,001–2,000 |
| E024-03 | 2,001–3,000 |
| E024-04 | 3,001–4,000 |
| E024-05 | 4,001–5,000 |
| E024-06 | 1–25 (pre-specified rerun) |

### 19–22. Requested, completed, failed, retried

| Measure | Value |
|---|---|
| Requested | 5,000 |
| Completed | **5,000** |
| Failed | 0 |
| Retried | 0 |

No duplicates; every t_IC is finite.

### 23. Determinism / rerun result

**Pass.** E024-06, an independent QuantConnect run, reproduced seeds 1–25 **identically** in every statistic.

### 24. Panel-digest consistency across batches

**Pass:**
- all six null runs prepared the identical panel, equal to the pinned canary digest;
- each null run would have refused to compute anything otherwise;
- one build; the same host and module hashes; 0 orders; PIT audit 0 in every batch.

### 25–31. Null t_IC distribution

5,000 worlds:

| Statistic | Data v2 | Data v1 (diagnostic only) |
|---|---|---|
| Mean | **0.181** | 0.195 |
| SD | **0.937** | 0.927 |
| Median | **0.174** | 0.200 |
| p90 | **1.388** | 1.391 |
| p95 | **1.724** | 1.713 |
| p99 | **2.377** | 2.390 |
| Maximum | **4.354** | 3.663 |

The slightly positive mean is a property of the null on this panel, as on Data v1. The procedure handles it, because the threshold comes from this same distribution.

### 32. Empirical 1% threshold

**2.3798883324991866**: the 50th largest of 5,000 (the 51st is 2.3773).

### 33. Final Data-v2 c_IC

**2.3798883324991866**

### 34. Lower-bound check

2.380 > 2.326, so the floor does not bind.

### 35–39. Null gate pass counts

With the new c_IC:

| Gate | Passes (of 5,000) | Share | Data v1 |
|---|---|---|---|
| G1 significant (t_IC > c_IC and mean IC > 0) | **49** | 0.98% | 49 |
| G2 economic (80+ ≥ +3%/yr) | **1,231** | 24.6% | 1,284 |
| G3 monotonic (≥ 0.90 and Q5 > Q1) | **255** | 5.1% | 277 |
| G4 stable (halves, block ≤ 50%) | **279** | 5.6% | 312 |
| All four | **5** | 0.10% | 7 |

G2 passes often under the null, as on Data v1: the 80+ group is small (about 7 stocks), so its average is noisy. This is a known property of the frozen design, which is why all four gates are required.

### 40. Full-procedure false-promotion rate

**0.10%** (5 of 5,000).

### 41. Null-results hash

| File | SHA-256 |
|---|---|
| `research/phase7/cp6/P7_CP6_null.json` | `371c7e22ecea0e887fe6211c01d49f77594e951775749af1d28f7a50014edee8` |
| `P7_CP6_null_worlds.json.gz` (all 5,000 per-world rows) | `6d38c66d…` |

### 42. Threshold pin commit

- Commit **cc2b0d8** pinned c_IC, the null-result hash, the per-world file, the seeds (`NULL_SEEDS`), the panel digest, the code / spec hashes and the build.
- It was merged into main via [CohenMatan/quant-trading-research#75](https://github.com/CohenMatan/quant-trading-research/pull/75) (merge 6d6573f).
- The working tree was verified clean before this checkpoint.

`tests/test_p7_h022_v2.py` recomputes c_IC from the committed worlds with the frozen rule and checks the hashes.

### 43–51. Confirmations

| # | Confirmation |
|---|---|
| 43 | **Old c_IC 2.390976216956 remains DATA_V1_ONLY / UNUSED_ON_V2.** A config with it is refused (tested). |
| 44 | **No unpermuted real H022 result was computed.** No identity mapping was run, and no null world reproduces it. |
| 45 | **No real IC computed.** |
| 46 | **No real G1–G4 result computed.** |
| 47 | **No portfolio run.** |
| 48 | **0 orders** in all eight runs. |
| 49 | **2018–2021 untouched.** Every run ends 2017-12-31; the last price row is 2017-12-29. |
| 50 | **Holdout untouched** (`HOLDOUT_UNLOCK.md` absent). |
| 51 | **Nothing purchased.** |

### 52. Final status

```
CALIBRATED — Data v2 c_IC pinned, real H022 still sealed
```

### 53. Exact next owner decision

Whether to authorise **exactly one real H022 evaluation** on frozen Data v2:
- with the pinned c_IC = 2.3798883324991866;
- with the pinned panel digest `09b1de41…`, enforced by the host;
- with gates G1–G4 unchanged;
- as one research run of S024 in real mode (E024-07). Its config would be accepted only with the pinned provenance plus `--owner-approved <decision>`.

The alternative is to stop here and keep H022 sealed.

## Records

- **Experiments:** 8 infrastructure runs logged in `experiments/INDEX.csv`: E999-01, E999-02, E024-01..06.
- **Programme totals:** 22 hypotheses (H001–H022). No new hypothesis or strategy idea; S024 is the H022 host on Data v2.
- **Files:**
  - pins: `qresearch.p7pred_v2`;
  - analysis: `research/phase7/cp6/P7_CP6_canary.py`, `P7_CP6_null.py`;
  - outputs: `P7_CP6_canary_E999-0{1,2}.json`, `P7_CP6_null.json`, `P7_CP6_null_worlds.json.gz`.

**STOP.** Not run, and not authorised:
- the real H022 mapping;
- real IC;
- real 80+ returns;
- real quintiles;
- G1–G4 on the real score;
- Fama-MacBeth;
- 2- or 3-month diagnostics;
- a portfolio;
- 2018–2021;
- the Holdout.
