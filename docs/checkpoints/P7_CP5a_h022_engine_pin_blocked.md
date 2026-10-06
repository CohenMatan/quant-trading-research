# P7-CP5a — H022 real evaluation BLOCKED: QuantConnect no longer runs our pinned engine

**Date:** 2026-10-06. **Decisions:** D177 (owner authorisation), D178–D181. **Status:** STOPPED awaiting the owner.

**Short version.** Everything up to the real evaluation is done and verified:
- the wording fix was committed;
- the X994 canary passed 19 of 19 checks;
- all 5,000 null worlds completed;
- c_IC = 2.390976 was pinned and committed before any real run.

The one real evaluation has **not** happened. QuantConnect stopped letting our account select the engine build (LEAN 18131) that every Phase 7 run used. The real run executed on a different build (18166). The host then refused to compute anything, because its input panel no longer matched the panel the null was calibrated on.

**No real IC, gate, quintile, 80+ or diagnostic statistic exists anywhere** — not on QuantConnect, not on this machine. H022 is therefore neither QUALIFIED nor NOT QUALIFIED. The P7-CP5 result report cannot be written until the owner chooses a way forward (section 5).

## 1. What was done, in order

| Step | What | Result | Commit / time (UTC) |
|---|---|---|---|
| 1 | Wording-only fix in spec C3 ("…maximises the number of non-overlapping monthly response periods") | Spec SHA-256 `389f9364…` → **`2c99f962…1f58`**; nothing else changed | 7906b0b |
| 2 | Host S023 + canary X994 (byte copy), configs, runner wiring, synthetic host tests | Tests pass | 093fbda |
| 3a | Canary E994-01 | **Failed at start-up** on the canary's own fingerprint guard (a false alarm; nothing computed; D178) | 093fbda, 20:07 |
| 3b | Fix: fingerprint check moved to the runner (QuantConnect's stored file read back before compiling) | S023/X994 v1.1 | b9d7aa8, f59bfb5 |
| 3c | Canary **E994-02** | **19 / 19 checks pass** (section 2) | f59bfb5, 20:33 |
| 4 | Null E023-01 … E023-05 (seeds 1–5,000) | 5,000 / 5,000 worlds, 0 failed, 0 retried; identical panel in every batch and in the canary (section 3) | last batch 87bad41, 21:58:44 |
| 5 | **c_IC pinned** with the null result hash and panel digest | c_IC = **2.390976216956** | **dbfdcc0, 21:59:49** |
| 5b | Threshold commit recorded; real config written | — | ea614bf, 22:03:15 |
| 6a | Real run **E023-06** | Never started: QuantConnect refused the engine-pin call at upload ("Please migrate your organization to trading firm to select lean version feature"). No compile, no backtest (D180) | ea614bf, 22:03 |
| 6b | Real run **E023-07** (identical configuration, new ID because IDs are never reused) | QuantConnect ran it on **LEAN 18166**, not 18131. The host's guard found the prepared panel different from the null's and stopped: "nothing computed". The runner also refused the download (engine mismatch) (D181) | 516ff03, 22:08 |

Chronology: null completed (21:58:44) → c_IC pinned (21:59:49) → real attempts (22:03 onwards). That ordering is preserved for whatever happens next: **c_IC is immutable**.

## 2. Canary E994-02 (plumbing only; no IC of the real assignment, no gate, no null statistic)

| # | Check | Result |
|---|---|---|
| 1 | No real IC / gate / null statistic computed | PASS |
| 2 | Uploaded host + modules = pins (QuantConnect's stored copy verified before compile) | PASS |
| 3 | Spec fingerprint = the corrected spec | PASS |
| 4 | Calendar: 84 reviews, weekly checks match the session calendar | PASS |
| 5 | Decisions 2011-01-31 → 2017-11-30 (83); last response ends 2017-12-29 | PASS |
| 6 | No price after 2017-12-29 | PASS |
| 7 | Score fingerprint = the frozen E993-02 scores (every review identical) | PASS |
| 8 | Regimes = E993-02 | PASS |
| 9 | Population = E993-02's eligible, kept, fully scorable rows | PASS |
| 10 | Sliced technical inputs = full computation | PASS |
| 11 | Response timing: entry strictly after t, exit within the window | PASS (0 violations) |
| 12 | Every response (117,473 across 1/2/3-month horizons) independently recomputed | PASS (0 mismatches) |
| 13 | Corporate actions: 120 responses recomputed from fresh single-stock history (30 each: splits, dividends, delisted, plain) | PASS (worst relative difference 7e-16) |
| 14 | Response unchanged when prices after t′, prices at or before t (incl. t's close) or the truncation point change | PASS (80 / 80) |
| 15 | Six whole reviews re-scored from price histories cut at t, and with every later price distorted | PASS (6,708 rows identical; regimes identical) |
| 16 | Determinism (all responses recomputed) | PASS |
| 17 | Null machinery (on synthetic responses): deterministic, exact permutations, no self-match | PASS |
| 18 | Market cap and momentum present for every population row | PASS |
| 19 | Status counts cover every population row | PASS |

**Population and coverage (primary horizon):**
- 39,734 stock-months: 196–612 stocks per date, median 516, mean 479;
- 80+ stocks: mean 7.0 per date; 2 months with none;
- status counts: `ok` 39,584, `truncated` 127, `no_bar_after_t` 19, `unverified_split` 4 (excluded and counted).

Full record: `research/phase7/P7_CP5_canary.json`.

## 3. Null (E023-01 … 05) and the pinned threshold

- **Integrity:**
  - 5,000 requested, 5,000 completed, 0 failed, 0 retried, 0 recovered;
  - seeds exactly 1–5,000;
  - identical prepared panel (`a1e12dbf…`) in all batches and in the canary;
  - every batch on LEAN 18131, with uploaded modules = pins.
- **Null t_IC:** mean 0.195, sd 0.927, 95th percentile 1.713, 99th percentile 2.390, max 3.663.
- **c_IC = max(50th largest, 2.326) = 2.390976.** The floor does not bind.
- **Gate passes among null worlds with c_IC:**

  | Gate | Null worlds passing |
  |---|---|
  | G1 | 49 |
  | G2 | 1,284 |
  | G3 | 277 |
  | G4 | 312 |
  | All four | **7 (0.14%)** |

  This is the full-procedure false-promotion rate.
- **Pinned in `qresearch.p7pred` (commit dbfdcc0):**
  - C_IC;
  - NULL_RESULT_SHA256 `c96733d8…` (`research/phase7/P7_CP5_null.json`);
  - the worlds file;
  - PANEL_SHA256;
  - spec, code and host hashes;
  - the seed and gate definitions (in the null file).

  The threshold commit is recorded in the next commit (ea614bf).

QuantConnect backtest IDs are in `experiments/INDEX.csv` (the null summary's own `qc_backtest_id` field is empty because of an extraction-script slip; it is pinned by hash and is not edited).

## 4. The blocker

**What happened.**
- Until about 22:00 UTC on 2026-10-06, every run executed on LEAN build 18131: E993-01/02, the canary and all five null batches. The runner verifies this on every run.
- From about 22:00, QuantConnect refused the call that selects a build: "Please migrate your organization to trading firm to select lean version feature".
- The project still reports 18131 as its build, but QuantConnect executed the next backtest on 18166.
- Our organisation is on the "researcher" tier ($10 seat + $14 B2-8 node = $24/month).

**Why it matters.**
- c_IC was calibrated on the exact panel produced under 18131.
- Under 18166 the prepared panel is different (the host's guard detected it; which side differs — scores or responses — is not yet known).
- Evaluating the real score on a different panel than the null's would break the pre-registered calibration. That is why the host refused, as designed.
- The same constraint affects **every** future QuantConnect run: CLAUDE.md requires a pinned engine, and the frozen data infrastructure v1 was built and verified on 18131 (CLAUDE.md: 18131 is the branch carrying the new Morningstar dataset; QuantConnect moves master to that dataset on 2026-10-10 and retires the old dataset on 2026-10-31).

**What is not affected.**
- No real statistic was produced, so nothing has been seen that could bias any later choice.
- The spec, score, mechanics, gates, c_IC, the null and the canary result all stand.

## 5. Options for the owner

| Option | What | Cost | Integrity |
|---|---|---|---|
| **A. Restore engine selection** | Upgrade QuantConnect to the Trading Firm tier; re-run the real evaluation on 18131 (new ID E023-08, same configuration) | Published at about **$480 / month** (another source says $336 per user, 2-user minimum). Far above the $200 / month hard ceiling | Cleanest: identical panel, pinned c_IC used as is |
| **B. Diagnose first, then decide (recommended)** | One extra X994 canary on QuantConnect's default build (infrastructure only: no real IC, no gate; configured for whatever build QuantConnect runs, recorded as such). It reports which side of the panel differs and by how much. Best done **after 2026-10-10**, when QuantConnect's default moves to the new Morningstar dataset that 18131 carried. **B1:** if the default build reproduces the pinned panel exactly (same digest), run the real evaluation with the pinned c_IC. **B2:** if not, go to C | $0 (≈ 12 minutes of the existing node) | B1 is as clean as A (byte-identical inputs). The engine differs, but the guard proves the inputs do not |
| **C. Re-baseline on the new engine** | Declare data infrastructure v2 (the D114 rule: a data change is an owner decision), re-run canary + all 5,000 null worlds on the new build, re-pin a new c_IC, then the one real evaluation. Spec, score, gates and procedure unchanged | $0 (≈ 1.5 hours of node time) | Valid, because no real statistic has been seen. But it is a new data version: E993-02 / P7-CP3R figures were computed on v1 and would need a note |
| **D. Stop** | Close H022 as "not evaluable on the available infrastructure" | $0 | Honest, but wastes a finished, verified pipeline |

**Recommendation: B, run after 2026-10-10.**
- If B1 holds, the real evaluation goes ahead exactly as frozen.
- If not, C follows with the owner's approval of data infrastructure v2.

Option A is not recommended: it breaks the budget ceiling for a convenience the free options may provide.

**Also needed: a programme-wide rule** (independent of H022). The pinned-engine rule in CLAUDE.md cannot be followed on the researcher tier any more. Proposal: "every run records the build QuantConnect actually used. A frozen experiment family (null and real) must share one build, or byte-identical prepared inputs verified by digest."

## 6. Records

- **Experiments:** E994-01 (failed, start-up guard), E994-02 (completed), E023-01..05 (completed), E023-06 (failed, never started), E023-07 (failed on QuantConnect's side, engine 18166: nothing computed, nothing downloaded).
- **Totals for H022:** 1 hypothesis, strategy S023 (canary X994), 9 experiments.
- **Files:**
  - `research/phase7/P7_CP5_canary.json`, `P7_CP5_null.json`, `P7_CP5_null_worlds.json.gz`;
  - `P7_CP5_null.py`, `P7_CP5_canary.py`;
  - `P7_CP5_real.py` (prepared, not run);
  - `docs/owner/2026-10-06_p7cp5_execute_h022.md`.
- **Confirmations:**
  - no change to the score, mechanics, horizon, thresholds or gates;
  - 2018–2021 untouched; Holdout untouched;
  - no portfolio, no orders (all runs 0 orders);
  - nothing purchased.

## 7. Exact owner decision needed

Choose **A**, **B** (with B1 / C as follow-ups) or **D** in section 5, and say whether the proposed programme-wide engine rule is adopted.

Until then: STOP. No further QuantConnect run for H022. c_IC stays pinned at 2.390976216956.
