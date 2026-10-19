# OC-2 synthetic calibration v2 — protocol (FROZEN — owner decision D250)

**Owner decisions:**
- D249 (`docs/owner/2026-10-18_oc2_synthetic_calibration_v2.md`): one controlled methodological repair attempt after v1 = D (OC-CP4).
- D250 (`docs/owner/2026-10-18_oc2_v2_final_protocol_approval.md`): Option 2 approved, with mandatory safeguards. They are written into §5, §6, §8 and §9 below.

**Status: FROZEN — owner decision D250.**
- `FROZEN.json` records this file's SHA-256, the code SHA-256 values, `ident_treatment = 2` and `owner_decision = D250`.
- `OC2_V2_run.py` refuses to start unless all of these match.
- The OC-CP5a draft (protocol SHA-256 4f7624dd…, `OC2_V2_draft_hashes.json`) is kept as the historical record. The changes made at the freeze are listed in §13.
- Nothing in this text may change after the confirmatory evaluation starts.

**Scope:**
- synthetic data only;
- no real F5 signal, return, price or Fama–MacBeth estimate;
- no QuantConnect run, no backtest, no Holdout, no purchase;
- no use of post-2021 data;
- v1 artifacts (`research/longhorizon/oc2/stage2/`) are preserved unchanged, and v1 stays **D — INSUFFICIENT EVIDENCE**.

**Evidence available before the freeze:** engineering and structure statistics only (DEV seeds):
- the failure-mode audit `OC2_V2_audit.json` (population algebra; no returns simulated);
- the engineering record `OC2_V2_engineering.json`.

No v2 scenario rejection rate, and no v2 power, was simulated before the freeze. The §9 projections are analytic.

## 1. Question

Does the proposed universe-wide Fama–MacBeth test of the frozen Data v3 F5 signal control false positives in realistic null worlds? Does the complete research decision rule avoid false approvals when controls are mismeasured or a correlated factor is unobserved? Can it detect a +3% a year gross top-quintile effect over 2012-02 → 2021-11 (118 monthly reviews, Stage 1 population)?

A synthetic pass is not evidence that OC-2 is profitable. It would only permit asking the owner for one real-data test.

## 2. Inference method (one primary method, no model search)

**Each review t = 1…118:**
- **Sample:** stocks with a valid signal and all eight controls (complete case; controls missing at random in 5% of stock-months; MNAR selection in N11).
- **Response:** next-month total return minus the sample's equal-weight mean. Not winsorised.
- **Signal:** centred cross-sectional rank.
- **Controls:** size, beta, LOWVOL, MOM, BM, GPA, AG, ACC.
  - Each is converted to a cross-sectional normal score Φ⁻¹(rank).
  - Each then enters as a **restricted cubic spline**: Harrell's natural cubic spline with 5 fixed knots at the normal quantiles 0.05 / 0.275 / 0.5 / 0.725 / 0.95, giving 4 columns per control.
  - Plus 11 FF12 sector dummies (financials excluded) and an intercept.
- **Estimation:** OLS. b_t = the signal coefficient (Frisch–Waugh partial slope via QR).
- **Companion G2:** the same regression with the signal rank replaced by a top-quintile dummy (signal rank ≥ 0.3). G2 = 12 × 0.8 × the mean dummy coefficient (top minus universe, per year).

**Primary statistic:** t = mean(b) / SE_NW7 (§3), one-sided, at the nominal 1% level (fixed-b critical value 2.5904). 5% is reported.

**Complete research decision rule** ("full rule", unchanged from v1; frozen in `oc2synth_v2.full_rule`) — a world-replication is *approved* only if all four hold:
- **G1:** t > 2.5904;
- **G2:** estimated top-quintile effect ≥ +3.0% a year;
- **G3:** positive mean slope in reviews 1–59 and in reviews 60–118;
- **G4:** no calendar year supplies more than 50% of the sum of monthly slopes.

**Non-gating diagnostics:**
- v1-style rank controls;
- NW lag 4;
- iid SE;
- the rule without G2;
- the full rule at G2 floors 2.0 / 2.5 / 3.5 / 4.0%. These are sensitivity results only, never optimised and never used for classification.
- The oracle control set (N2L-oracle) is impossible in real data and is never used for classification.

## 3. Standard error and critical values

- **Newey–West, Bartlett, lag 7**, fixed prospectively: the Andrews AR(1) plug-in L = 1.1447 (αT)^{1/3}, α = 4ρ² / (1 − ρ²)², at ρ = 0.5 and T = 118 (L = 6.8 → 7).
- **Critical values:** fixed-b one-sided quantiles of the NW(7) t under iid Gaussian slopes, T = 118 (2,000,000 draws, seed 118007):

| level | fixed-b CV |
|---|---|
| 5% | 1.7768983745981166 |
| 1% | 2.5903943399261284 |
| 0.5% | 2.904988356486873 |
| 0.1% | 3.5885898416418374 |

- Lags 4 and 0 are reported, never gating; the lag is not selected by any result.
- **Reported per world:**
  - SE calibration: mean NW SE / across-replication sd of mean(b);
  - bias: mean of mean(b); truth 0 under every null.

## 4. Synthetic DGP (`qresearch.oc2synth_v2`; population structure imported unchanged from the frozen v1 module)

**Frozen parameters:**
- cross-section 447 → 1,019 valid stocks a review (Stage 1);
- FF12 sector mix;
- quarterly refresh phases 0.62 / 0.10 / 0.28;
- exits 2.4% / entries 2.9%;
- characteristic correlation matrix;
- F5–characteristic correlations: MOM 0.175, ACC −0.177, GPA 0.105, AG 0.078, BM −0.07, LOWVOL −0.05, latent growth 0.30;
- characteristic AR 0.95;
- signal AR 0.70;
- total cross-sectional return sd 6.5% a month;
- t(5) noise;
- LOWVOL heteroskedasticity 0.30;
- sector shocks 2.5%, factor shocks 1.0%, market 4.5% (× 0.3 beta loading);
- missing controls 5% MAR.

**Signal payoff:** zero-mean AR(1), ρ_g = 0.10 (0.30 in N9). Stationary sd G_SD = 0.0025457771839916855 / 0.004513291014499582 / 0.006309844357589551 for IC sd regimes 0.06 / 0.09 (central) / 0.12. Verified partial IC sd 0.061 / 0.090 / 0.118.

**Variance budget:** the systematic share must be ≤ 60%, otherwise the world is refused.

**Every slot trades every month, with stock-id tracking.** An overlapping response stops accumulating on exit.

**Seeds:** sha256("OC2-V2|FINAL|<world>")[:8] + replication index, mod 2³². FINAL seeds are used only in the confirmatory run; DEV / TEST / SMOKE tags were used for engineering.

## 5. Scenario inventory (verified count: 60 worlds)

| owner §7 item | worlds | tier |
|---|---|---|
| 1 pure null | N0i, N0 | 1 |
| 2 market / size | N1m | 1 |
| 3 LOWVOL | N1 | 1 |
| 4 growth / profitability | N3, N2 | 1 |
| 5 nonlinear | N4, N4r, N4q | 1 |
| 6 noisy controls | N5a (reliability 0.80), N5b (0.60) | 2 |
| 7 latent factor | N2L1 (+1%), N2L (+3%), N2L5 (+5%); corr with F5 0.30 | 2 |
| 8 time-varying premia | N6, N9 | 1 |
| 9 sector / market shocks | N7 (sector 3.5%, factor 1.1%) | 1 |
| 10 heavy tails | N12 | 1 |
| 11 quarterly refresh | N13 (3-month overlapping response) | 1 |
| 12 entrants / leavers / MNAR | N8a, N8b, N11 | 1 |
| 13 small / varying N | N14 (× 0.5), N14s (× 0.25) | 1 |
| 14 irregular timing | N15 | 1 |

- **Base:** N4 (every control priced at 3% a year) for items 5–14, as in v1.
- **IC regimes:** every world runs at 0.09. N0, N4, N4q, N12, N14, N5a, N2L, N5b and N2L5 also run at 0.06 and 0.12.
- **Tier 1 (ordinary null worlds): 30** — 20 central (N0i, N0, N1m, N1, N3, N2, N4, N4r, N4q, N6, N9, N7, N12, N13, N8a, N8b, N11, N14, N14s, N15) plus 10 regime copies of N0, N4, N4q, N12 and N14.
- **Tier 2 (identification family): 13** — N5a, N5b, N2L1, N2L, N2L5, plus N5a, N5b, N2L and N2L5 at 0.06 and 0.12. **Severe:** N5b and N2L5 (6 worlds with regime copies).
- **Diagnostic:** N2L-oracle (non-gating).
- **Power cells: 16** (§6).

Total: 30 + 13 + 1 + 16 = **60**.

**Note on the count.** D250 refers to "54 planned synthetic worlds":
- 54 was the count of the first engineering record (commit 3c9381c), before the N2L regime copies entered the OC-CP5a draft. The draft presented in OC-CP5a contained 56.
- At this freeze, N5b and N2L5 were added at 0.06 and 0.12 so that the severe robustness gate covers every regime, including the high-IC regime of the 4.4% N2L5 projection D250 cites. That gives 60.
- No world was removed or reclassified.

## 6. Planted alternatives and power (1,000 replications each)

**Cells:**
- P2 / P3 / P4 / P5: a gross top-quintile effect of +2 / +3 / +4 / +5% a year on the N4 base, in each IC regime (12 cells);
- P3-c0, P3-c2: F5–control correlations × 0 / × 2;
- P3-fresh: payoff only on freshly refreshed signals (quarterly arrival);
- P3-n50: half-size cross-section.

**Power A (statistical-test power):** the share of replications in which t > 2.5904 (1% level). 5% is reported.

**Power B (complete decision-rule power):** the share of replications that pass the full rule (G1 ∧ G2 ∧ G3 ∧ G4).

Both are reported for every cell, with MDE50 / MDE80 by linear interpolation over +2…+5% per regime, T_eff = T(1 − ρ₁)/(1 + ρ₁), and the G2-floor sensitivity (report-only).

**Disclosed before the run (owner D250 §4):** at a true +3%, the G2 floor (estimate ≥ +3%) limits Power B to roughly 50% under an approximately unbiased, symmetric estimator. With the unchanged 0.80 target (§8.4), classification A is therefore structurally unlikely at the +3% reference. The +3% reference and the 0.80 target are not changed.

## 7. Replications, Monte Carlo precision, runtime

| world group | reps each | total |
|---|---|---|
| central null worlds (25) | 4,000 | 100,000 |
| regime copies (18) | 2,000 | 36,000 |
| oracle | 1,000 | 1,000 |
| power cells (16) | 1,000 | 16,000 |

Total **153,000** replications.

**Monte Carlo precision:**
- Wilson 95% intervals for every rate.
- MC sd at 5% / 1% / 2%: 0.34 / 0.16 / 0.22 points at 4,000 replications; 0.49 / 0.22 / 0.31 points at 2,000.
- At 1,000 replications, power has an MC sd of at most 1.6 points.

**Runtime and storage:**
- ≈ 0.42 s per replication on 4 cores ≈ 4.5 h.
- Rows go to `data/oc2_v2_parts/` (gitignored, re-creatable from FINAL seeds).
- The summary goes to `OC2_V2_results.json`.

## 8. Criteria and classification (frozen; precedence D > C > A / B)

**8.1 Required evidence (otherwise D — INSUFFICIENT EVIDENCE):**
- Every one of the 60 worlds completes, with computational failures ≤ 1% of its replications. Failures are counted as non-rejection / non-approval in the primary rates; rates over completed replications must also pass. Failures are never excluded.
- Generator adequacy in N0 and N4 at each regime:
  - partial IC sd within ±15% of target;
  - refresh shares within ±0.05 of Stage 1 (0.625 / 0.097 / 0.270);
  - mean valid cross-section within ±3% of the Stage 1 mean × 0.95.
- In N4: F5–control correlations within ±0.03 of target.

**8.2 Tier 1 — size (otherwise C — NOT VALIDATED):** in each of the 30 Tier 1 worlds, on both denominators:
- rejection at 1% ≤ 2.0%;
- rejection at 5% within [3.5%, 6.5%].

**8.3 Tier 2 — complete-rule false approval (otherwise C — NOT VALIDATED):**
- In each of the 13 Tier 2 worlds — N5a, N5b, N2L1, N2L, N2L5 and every regime copy — the full-rule approval rate is ≤ 2.0% on both denominators.
- The severe worlds (N5b, N2L5, all regimes) are gating under this rule, not diagnostics. A severe failure gives C for the intended broad claim, and no narrower outcome is defined (owner D250 §3).
- N2L1 is gated under the same rule. That is a stricter reading than D250's list (N5a, N2L, N5b, N2L5), applied for consistency.
- Ordinary t-test rejection rates in Tier 2 are reported separately and are not gating, because no observed-control estimator can be size-correct there.

**8.4 Power (only if 8.1–8.3 pass):**
- **A — CALIBRATED AND SUFFICIENTLY POWERED** if, at +3% in the central regime (cell P3-0.09), both Power A ≥ 0.80 and Power B ≥ 0.80.
- Otherwise **B — CALIBRATED BUT UNDERPOWERED**.
- Low and high regimes are reported, not gating.

**8.5 Implementation:** `OC2_V2_run.decide` → `oc2synth_v2.classify`, unit-tested against this text.

## 9. Identification family — owner choice (D250)

**Chosen option: 2, with the D250 safeguards** (§8.3 severe gating, two power types).

**Meaning:**
- Tier 2 evaluates whether the research procedure wrongly *approves* F5 when F5 has no independent effect but controls are mismeasured or a correlated factor is unobserved.
- It does **not** establish that the F5 coefficient is unbiased, or that latent-factor confounding is absent.
- The method is not identifiable with real observable controls in these worlds. The only remedy in the synthetic is the oracle control.

**Scope of any later claim:** "predictive beyond the eight observed controls as measured". This is not proof of independent alpha.

**Pre-run analytic projections** (population bias × DEV slope scale, through the fixed-b reference; not v2 results):
- t-test 5% rejection: N5a 7.5–11%, N5b 10–19%, N2L 17–39%, N2L5 31–73%.
- Upper bounds on full-rule false approval, from P(G2 ≥ 3%) alone: N2L 1.6% and N2L5 4.4% at IC sd 0.12.

**Reported per Tier 2 world:**
- n;
- ordinary rejection at 1% / 5%;
- full-rule false approval with its Wilson interval;
- bias in slope units and as an apparent top-quintile effect;
- assumed confounding strength (reliability or latent premium);
- the rule-without-G2 approval rate (the role of the +3% threshold);
- identifiability (no).

## 10. Reporting (every world)

- n, failures (with reasons);
- rejection at 5% / 1% / 0.5% / 0.1% on both denominators, with Wilson intervals;
- mean and sd of t; bias; SE ratio;
- G2 mean;
- full-rule approval, the rule without G2, and G2-floor sensitivity;
- realised IC sd and partial IC sd; ρ₁; T_eff;
- cross-section size, refresh shares, F5–control correlations;
- the rank-control, NW4 and iid diagnostics.

## 11. Stopping rules

- Exactly one confirmatory evaluation (FINAL seeds), from the clean committed tree.
- A technical retry is allowed only after a documented infrastructure failure, with the identical frozen code and seeds. The per-world files make the retry resume rather than re-draw.
- No v3, and no change of estimator, controls, noise, lag, thresholds, scenarios or confounding treatment after any result.
- After OC-CP5, STOP for the owner, whatever the outcome.

## 12. Freeze record

- `FROZEN.json` holds the SHA-256 of this file and of `oc2synth_v2.py`, `oc2synth.py` (v1, unchanged), `OC2_V2_scenarios.py` and `OC2_V2_run.py`.
- `tests/test_oc2synth_v2.py::test_frozen_record` checks them.
- Fixed-b critical values and G_SD are pinned in `oc2synth_v2`.

## 13. Changes at the freeze relative to the OC-CP5a draft (all owner-directed by D250, made before any confirmatory result)

1. §9: Option 2 chosen.
2. §8.3: Tier 2 extended from N5a / N2L to every identification-family world, with N5b / N2L5 explicitly gating.
3. §5: N5b and N2L5 added at the 0.06 / 0.12 regimes (+4 worlds; 60 in total).
4. §6 / §8.4: Power B defined, and classification A requires both power types.
5. §2 / §10: reporting of the rule without G2 and the G2-floor sensitivity.
6. Code: `classify` signature (two power arguments); `decide` without the option-1 branch; the driver requires `owner_decision = D250`.

Unchanged from the draft:
- estimator, controls, lag and critical values;
- DGP, seeds and replication counts per world type;
- Tier 1 gates;
- full-rule definition;
- adequacy rules and stopping rules.
