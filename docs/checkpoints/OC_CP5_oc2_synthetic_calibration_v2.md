# OC-CP5 — OC-2 Synthetic Calibration v2

**Owner decision:** D250 (`docs/owner/2026-10-18_oc2_v2_final_protocol_approval.md`), following D249 / OC-CP5a.

**Official classification: C — NOT VALIDATED.**

**In one paragraph:**
- The repaired test is well behaved where it can be: all 30 ordinary null worlds pass the strict size gates.
- But the complete research decision rule wrongly approves F5 in **4.40%** of replications (95% CI 3.59–5.39%; limit 2%) in one of the owner's mandatory severe-confounding worlds. In that world an unobserved factor, correlated 0.30 with F5, earns +5% a year, in the noisier (IC sd 0.12) market regime.
- Under D250 §3 that is a reliability failure for the intended claim, and no narrower outcome was pre-defined, so the method is **not validated**.
- Independently of that failure, the complete rule would have been underpowered at the +3% target: it passes a true +3% effect only **43.5%** of the time, while the t-test alone rejects 84.6%.

**Recommendation:** close OC-2 on the current data and methods, and keep SPY (OC-1) as the offensive baseline.

This is a synthetic, methodological result. It does **not** show that profitability improvement has no economic value.

---

## 1. Verified decision ID and repository state

- Before this work, main was at 56f55ef (PR #114 merged; OC-CP5a). D249 was the latest decision, so this approval is **D250**.
- The tree was clean; credentials were present (values never printed); QuantConnect was reachable but not used.
- **Commits:**
  - 3adf5b4 — frozen protocol, `FROZEN.json`, code and tests, committed and pushed **before** the run;
  - 58e4a8a — report formatter only;
  - fb49fb8 — confirmatory result.
- **Preserved unchanged:**
  - the v1 protocol and code (`oc2synth.py` SHA-256 fc701816…);
  - v1's **D** classification;
  - the OC-CP5a findings;
  - the OC-CP5a draft hashes (`OC2_V2_draft_hashes.json`, historical);
  - the F5 hypothesis.

## 2. Final frozen protocol and hashes

`research/longhorizon/oc2/v2/OC2_V2_protocol.md` — "FROZEN — owner decision D250". `FROZEN.json` (committed in 3adf5b4):

| file | SHA-256 |
|---|---|
| protocol | `4d8ff415bde152feb3e94f8c8c010b3a88d01cae3bb5cc68ddd34d1ac17f7fb8` |
| `oc2synth_v2.py` | `cc8ba9d1157f35a7ef2a61d97b0301f07bf8e32f0715342aa2f5f65440d72f38` |
| `oc2synth.py` (v1, unchanged) | `fc7018164413692408c5cd1907c98eb65ca6b50f1c0ffb0572fee545f4e9c8e4` |
| `OC2_V2_scenarios.py` | `54c2d976eeb370eee59080abc1670312eb4f1262d1b3076c278a7543eacc8802` |
| `OC2_V2_run.py` | `676d85bee18d9959d6359e064d41ffe85879bf146b09e6d724e2a2a863d902b9` |

- The result file records the same hashes, and a test checks them (`test_committed_result_matches_frozen_rule`).

**Frozen method:**
- monthly Fama–MacBeth of the demeaned next-month return on the centred F5 rank;
- controls: 8 controls as 5-knot restricted cubic splines of their normal scores, plus FF12 dummies;
- Newey–West lag 7 (Andrews rule at ρ = 0.5), with fixed-b critical values (1% 2.5904, 5% 1.7769).

**Complete decision rule:** t > 2.5904 ∧ top-quintile effect ≥ +3% a year ∧ both halves positive ∧ no year > 50%.

**Changes at the freeze relative to OC-CP5a** (all directed by D250, made before any result; protocol §13):
- Option 2 chosen;
- Tier 2 gating extended to every confounded world, including N5b / N2L5;
- N5b / N2L5 added at the 0.06 / 0.12 regimes;
- Power B defined; classification A requires both power types;
- G2-floor sensitivity reported.

## 3. Tier 1 — ordinary null worlds (strict size): 30 of 30 PASS

| world | n | rej 1% [95% CI] | rej 5% [95% CI] | mean t | sd t | SE ratio | G2 mean |
|---|---|---|---|---|---|---|---|
| N0i | 4000 | 1.12% [0.84, 1.50] | 5.20% [4.55, 5.93] | −0.020 | 1.101 | 0.937 | 0.01% |
| N0 | 4000 | 0.78% [0.55, 1.10] | 5.27% [4.62, 6.01] | −0.006 | 1.098 | 0.940 | 0.00% |
| N0@0.06 | 2000 | 1.45% [1.01, 2.07] | 5.40% [4.49, 6.48] | 0.023 | 1.097 | 0.947 | 0.01% |
| N0@0.12 | 2000 | 0.65% [0.38, 1.11] | 4.85% [3.99, 5.88] | 0.002 | 1.076 | 0.959 | 0.00% |
| N1m (market / size) | 4000 | 1.27% [0.97, 1.67] | 5.60% [4.93, 6.36] | −0.001 | 1.119 | 0.931 | 0.00% |
| N1 (LOWVOL) | 4000 | 1.07% [0.80, 1.44] | 5.40% [4.74, 6.14] | 0.024 | 1.104 | 0.941 | 0.02% |
| N3 (GPA) | 4000 | 1.03% [0.76, 1.39] | 5.22% [4.58, 5.96] | −0.011 | 1.105 | 0.932 | −0.02% |
| N2 (AG) | 4000 | 1.12% [0.84, 1.50] | 5.50% [4.84, 6.25] | −0.004 | 1.098 | 0.949 | 0.00% |
| N4 (all priced) | 4000 | 1.20% [0.91, 1.59] | 5.40% [4.74, 6.14] | −0.022 | 1.109 | 0.933 | −0.02% |
| N4@0.06 | 2000 | 1.05% [0.69, 1.60] | 5.10% [4.22, 6.15] | 0.014 | 1.093 | 0.948 | 0.02% |
| N4@0.12 | 2000 | 1.30% [0.89, 1.90] | 6.05% [5.09, 7.18] | −0.001 | 1.110 | 0.933 | 0.00% |
| N4r (rank-linear) | 4000 | 1.12% [0.84, 1.50] | 4.62% [4.02, 5.32] | −0.038 | 1.113 | 0.938 | −0.03% |
| N4q (tail) | 4000 | 1.07% [0.80, 1.44] | 4.88% [4.25, 5.59] | −0.002 | 1.082 | 0.955 | 0.00% |
| N4q@0.06 | 2000 | 0.80% [0.49, 1.30] | 5.40% [4.49, 6.48] | 0.010 | 1.081 | 0.967 | 0.01% |
| N4q@0.12 | 2000 | 0.75% [0.46, 1.23] | 5.05% [4.17, 6.10] | −0.023 | 1.115 | 0.929 | −0.01% |
| N6 (TV premia) | 4000 | 0.68% [0.46, 0.98] | 5.12% [4.48, 5.85] | −0.009 | 1.090 | 0.945 | −0.01% |
| N9 (persistent payoff) | 4000 | 1.55% [1.21, 1.98] | 6.40% [5.68, 7.20] | 0.018 | 1.150 | 0.905 | 0.02% |
| N7 (shocks) | 4000 | 1.23% [0.93, 1.62] | 5.75% [5.07, 6.51] | 0.000 | 1.117 | 0.930 | 0.00% |
| N12 (heavy tails) | 4000 | 1.00% [0.74, 1.36] | 4.90% [4.27, 5.61] | −0.007 | 1.087 | 0.956 | −0.01% |
| N12@0.06 | 2000 | 1.45% [1.01, 2.07] | 5.15% [4.26, 6.21] | 0.012 | 1.118 | 0.934 | 0.01% |
| N12@0.12 | 2000 | 1.05% [0.69, 1.60] | 4.75% [3.90, 5.77] | 0.007 | 1.065 | 0.971 | 0.00% |
| N13 (3-month overlap) | 4000 | 1.55% [1.21, 1.98] | 5.60% [4.93, 6.36] | −0.028 | 1.183 | 0.887 | −0.01% |
| N8a (no churn) | 4000 | 1.10% [0.82, 1.47] | 5.50% [4.84, 6.25] | 0.024 | 1.105 | 0.938 | 0.02% |
| N8b (2× churn) | 4000 | 0.85% [0.61, 1.19] | 5.35% [4.69, 6.09] | 0.020 | 1.115 | 0.932 | 0.01% |
| N11 (MNAR) | 4000 | 1.30% [0.99, 1.70] | 5.35% [4.69, 6.09] | −0.025 | 1.105 | 0.939 | −0.02% |
| N14 (× 0.5 N) | 4000 | 1.03% [0.76, 1.39] | 5.50% [4.84, 6.25] | 0.011 | 1.095 | 0.943 | 0.01% |
| N14@0.06 | 2000 | 0.75% [0.46, 1.23] | 4.95% [4.08, 5.99] | −0.023 | 1.115 | 0.925 | −0.02% |
| N14@0.12 | 2000 | 1.30% [0.89, 1.90] | 5.45% [4.54, 6.53] | 0.026 | 1.082 | 0.966 | 0.00% |
| N14s (× 0.25 N) | 4000 | 1.12% [0.84, 1.50] | 5.17% [4.53, 5.91] | −0.003 | 1.101 | 0.934 | −0.01% |
| N15 (irregular timing) | 4000 | 0.83% [0.59, 1.16] | 5.22% [4.58, 5.96] | 0.010 | 1.094 | 0.943 | 0.01% |

- Range: 1% rejection 0.65–1.55% (limit 2%); 5% rejection 4.62–6.40% (band 3.5–6.5%).
- The closest cases are N9 (6.40% at 5%) and N4@0.12 (6.05%).
- **Bias:** mean slope within ±0.0001 everywhere (truth 0). The v1 mean shifts (+0.18 to +0.72 t) are gone.
- **SE behaviour:** the NW(7) SE averages 0.89–0.97 of the true sampling sd. The fixed-b critical values compensate, which is why size holds.
- **Diagnostics (non-gating)** at 5%:
  - iid SE rejects 6.0–17% (N13 17%);
  - NW4 rejects 4.4–6.2%;
  - the v1-style rank controls reject 5.0–6.6% (N4q 6.2%).
  - So both the SE lag rule and the spline controls matter.

## 4. Tier 2 — complete-rule false approval (limit 2% per world): 12 of 13 PASS, 1 FAIL

| world | assumed confounding | n | t-test rej 1% / 5% | **full-rule false approval** [95% CI] | without the +3% floor | slope bias | apparent effect | result |
|---|---|---|---|---|---|---|---|---|
| N5a | controls' reliability 0.80 | 4000 | 1.98 / 8.67% | **0.07%** [0.03, 0.22] | 1.98% | 0.00044 | +0.21%/yr | PASS |
| N5a@0.06 | 0.80 | 2000 | 2.50 / 10.40% | **0.00%** [0.00, 0.19] | 2.50% | 0.00042 | +0.21% | PASS |
| N5a@0.12 | 0.80 | 2000 | 1.50 / 7.10% | **0.55%** [0.31, 0.98] | 1.50% | 0.00040 | +0.20% | PASS |
| N5b (severe) | reliability 0.60 | 4000 | 2.93 / 10.97% | **0.30%** [0.17, 0.52] | 2.90% | 0.00075 | +0.37% | PASS |
| N5b@0.06 (severe) | 0.60 | 2000 | 4.00 / 15.95% | **0.00%** [0.00, 0.19] | 4.00% | 0.00075 | +0.37% | PASS |
| N5b@0.12 (severe) | 0.60 | 2000 | 2.30 / 8.15% | **0.80%** [0.49, 1.30] | 2.30% | 0.00076 | +0.37% | PASS |
| N2L1 | latent +1%/yr, corr 0.30 | 4000 | 1.88 / 8.77% | **0.05%** [0.01, 0.18] | 1.88% | 0.00047 | +0.22% | PASS |
| N2L | latent +3%/yr | 4000 | 5.42 / 19.60% | **0.38%** [0.23, 0.62] | 5.42% | 0.00136 | +0.64% | PASS |
| N2L@0.06 | latent +3% | 2000 | 12.80 / 34.35% | **0.00%** [0.00, 0.19] | 12.80% | 0.00140 | +0.67% | PASS |
| N2L@0.12 | latent +3% | 2000 | 4.55 / 14.95% | **2.00%** [1.47, 2.71] | 4.55% | 0.00140 | +0.67% | PASS (at the limit: 40 of 2,000) |
| N2L5 (severe) | latent +5%/yr | 4000 | 15.32 / 38.80% | **1.40%** [1.08, 1.81] | 15.32% | 0.00230 | +1.10% | PASS |
| N2L5@0.06 (severe) | latent +5% | 2000 | 35.25 / 64.60% | **0.05%** [0.01, 0.28] | 35.25% | 0.00227 | +1.09% | PASS |
| **N2L5@0.12 (severe)** | latent +5% | 2000 | 9.25 / 25.05% | **4.40%** [3.59, 5.39] | 9.25% | 0.00232 | +1.10% | **FAIL** |

**Oracle diagnostic** (N2L +3% with the hidden factor added as a control, impossible in real data):
- t-test rejection 1.00% / 5.70%;
- full rule 0.10%;
- apparent effect +0.03%.

The bias belongs entirely to the missing control.

## 5. The four named confounded worlds (D250 §3)

**Replications:** 4,000 central and 2,000 per regime copy, all completed (0 failures).

**Ordinary rejection:** inflated everywhere, as predicted. The t-test is not size-correct when controls are mismeasured or a correlated factor is hidden:
- N5a: 1.5–2.5% at 1%; 7–10% at 5%;
- N5b: 2.3–4.0% / 8–16%;
- N2L: 4.6–12.8% / 15–34%;
- N2L5: 9–35% / 25–65%.

**Complete-rule false approval:**
- N5a 0.0–0.6%; N5b 0.0–0.8%; N2L 0.0–2.0%;
- N2L5 0.05–1.4%, but **4.40% at IC sd 0.12**.

**Coefficient bias** (apparent top-quintile effect): N5a +0.21%; N5b +0.37%; N2L +0.64–0.67%; N2L5 +1.09–1.10% a year. That is about +0.22% a year of fake F5 effect per +1% of hidden premium, matching the OC-CP5a audit.

**Role of the +3% threshold:** it removes most false approvals. Without G2, approvals equal the t-test rejections (2–35%); with it they fall to 0–4.4%.
- It fails exactly where the estimate is noisiest. At IC sd 0.12 the estimated top-quintile effect scatters more widely around its +1.1% bias, so it crosses +3% more often.
- At the low-noise regime the t-test rejects most (35%) but the effect estimate is tight and almost never reaches +3%.
- G2-floor sensitivity (report-only, never used): N2L5@0.12 approval 8.8 / 7.1 / 4.4 / 1.9 / 0.65% at floors 2 / 2.5 / 3 / 3.5 / 4%.

**Identifiable with real-world observable controls? No.**
- In these worlds no estimator using only the observed controls can separate F5 from the mismeasured or hidden characteristic.
- Only the impossible oracle control removes the bias.

## 6. All 60 worlds accounted for

**60 of 60 completed:**
- 30 Tier 1, 13 Tier 2, 1 oracle diagnostic, 16 power cells;
- 153,000 replications; **0 computational failures**.

**Note on D250's "54":**
- 54 was the count in the first engineering record (commit 3c9381c). The OC-CP5a draft contained 56.
- At the freeze, N5b and N2L5 were added at IC sd 0.06 / 0.12 so the severe gate covers the high-noise regime where the 4.4% projection lay. That gives 60.
- No world was removed or reclassified.

**Generator adequacy:** all checks pass.
- Partial IC sd: N0 0.0608 / 0.0905 / 0.1200; N4 0.0605 / 0.0906 / 0.1196 (targets 0.06 / 0.09 / 0.12).
- Refresh shares 0.632 / 0.128 / 0.302.
- Mean valid cross-section 709.2.
- N4 F5–control correlations within 0.004 of target.

**N7 / N13:**
- N7 ran with a realistic idiosyncratic sd: 57% systematic share, guard passed.
- N13's overlapping response produced no NaN in any of 4,000 replications.

## 7. Monte Carlo uncertainty

Every rate carries a Wilson 95% interval (tables above).
- At 4,000 replications the MC sd of a 5% rate is 0.34 points, and of a 1% rate 0.16 points.
- At 2,000 replications: 0.49 and 0.22 points.

**The failing cell:**
- N2L5@0.12 = 88 of 2,000 approvals = 4.40%, interval 3.59–5.39%. The whole interval lies above 2%, so the failure is not Monte Carlo noise.
- It reproduces the pre-run analytic upper bound (4.4%) almost exactly.

**The boundary cell:** N2L@0.12 = 40 of 2,000 = 2.00% (interval 1.47–2.71%). It passes because the rule is "≤ 2%", but it is not evidence of a comfortable margin.

## 8. Statistical-test power (Power A: t-test at 1%)

| effect / IC sd | 0.06 | 0.09 (central) | 0.12 |
|---|---|---|---|
| +2% | 88.6% | 46.7% | 26.5% |
| +3% | 99.9% | **84.6%** | 59.1% |
| +4% | 100.0% | 98.0% | 84.9% |
| +5% | 100.0% | 100.0% | 95.8% |

+3% at central under alternative structures:
- correlations × 0: 87.2%;
- correlations × 2: 82.9%;
- quarterly-arrival payoff: 89.2%;
- half-size cross-section: 79.9%.

5%-level power at +3% central: 96.6%. T_eff 102–110 of 118.

## 9. Complete decision-rule power (Power B)

| effect / IC sd | 0.06 | 0.09 (central) | 0.12 |
|---|---|---|---|
| +2% | 4.7% | 10.5% | 14.7% |
| +3% | 42.0% | **43.5%** | 42.5% |
| +4% | 90.3% | 81.9% | 73.7% |
| +5% | 99.8% | 98.7% | 93.3% |

+3% at central under alternative structures:
- correlations × 0: 50.5%;
- correlations × 2: **20.7%**;
- quarterly arrival: 49.3%;
- half-size: 45.3%.

What this shows:
- At a true +3% the rule passes only 42–44% in every regime. The +3% estimate floor caps it, as disclosed before the run.
- In addition, the controls absorb part of a planted effect through F5's correlations with them. The mean estimate at a planted +3% is 2.85%, and only 2.37% when the correlations are doubled.
- G2-floor sensitivity at +3% central (report-only): 78.3 / 63.2 / 43.5 / 23.4 / 9.7% at floors 2 / 2.5 / 3 / 3.5 / 4%.

## 10. Minimum detectable effects (gross top-quintile excess, % a year)

| IC sd | test MDE50 | test MDE80 | full-rule MDE50 | full-rule MDE80 |
|---|---|---|---|---|
| 0.06 | ≤ 2.0 | ≤ 2.0 | 3.17 | 3.79 |
| 0.09 | 2.09 | 2.88 | 3.17 | 3.95 |
| 0.12 | 2.72 | 3.81 | 3.24 | 4.32 |

The complete research procedure reliably detects only effects of roughly **+4% a year or more**.

## 11. Comparison with v1 (v1 not rewritten; it remains D)

| | v1 (OC-CP4, D) | v2 (this run) |
|---|---|---|
| ordinary nulls | 9 of 14 gating worlds failed size (mean t shifts +0.15…+0.72) | 30 of 30 pass; no bias |
| nonlinear premia (N4) | 1.92% / 7.55% | 1.20% / 5.40% (tail form 1.07% / 4.88%) |
| N7 | defective noise-free world | realistic; passes |
| N13 | crashed / NaN | completes; passes |
| noise realism | IC sd 0.03 (quiet) | 0.06 / 0.09 / 0.12 verified |
| N5a | t-test 6.4% / 19.2%, gating → fail | t-test 2.0% / 8.7% (reported); full-rule approval 0.07% |
| latent factor | N2L 47.7% at 1% (diagnostic) | t-test 5–35%; full-rule 0–4.4%; **one severe failure** |
| power at +3% | ~100% (not credible) | test 84.6%; full rule 43.5% |

The repair fixed every functional and specification defect. What remains is the identification limit, which no observed-control method can remove.

## 12. Identification limitations

- The method can show only that F5 predicts returns **beyond the eight observed controls as measured**.
- If any unobserved or mismeasured characteristic correlated with F5 carries a premium, part or all of a measured F5 effect may belong to it: about +0.22% a year of apparent effect per +1% a year of hidden premium at correlation 0.30.
- The +3% floor suppresses such false approvals in most worlds, but not when the hidden premium is large (+5%) and month-to-month noise is high. That is the 4.40% failure.
- None of this can be checked in real data, because the hidden factor is by definition unobserved.
- A real-data "pass" would therefore never by itself be proof of independent alpha.

## 13. Final classification

**C — NOT VALIDATED.** Frozen precedence D > C > A / B:
- **D does not apply:** 0 failures, all 60 worlds complete, generator adequacy passes.
- **C applies:** Tier 2 failure N2L5@0.12, a severe-confounding world. Under D250 §3 a severe failure blocks an A or B classification and any recommendation to proceed to a real-return test. No narrower outcome was pre-defined.
- **Had no Tier 2 failure occurred**, the result would have been **B — CALIBRATED BUT UNDERPOWERED**: Power A 84.6% ≥ 0.80 but Power B 43.5% < 0.80.

The classification is computed by `OC2_V2_run.decide` and re-derived by a unit test from the committed numbers.

**Failure type:** statistical / structural (identification), not computational.

## 14. Recommendation for owner review

**Close OC-2 on the current data and methods; keep SPY (OC-1) as the offensive baseline.** Reasons:
1. The only frozen, owner-approved repair attempt failed a mandatory reliability requirement.
2. The failure is structural. It comes from hidden-factor confounding that more data of the same kind cannot identify. The +3% floor that protects against it also halves the power at the target effect. Raising the floor would cut power further; lowering it would raise false approvals (sensitivity above). There is no free trade-off left to choose, and choosing one now would be a post-result change.
3. Even ignoring the failure, the procedure reliably detects only effects of about +4% a year or more. That is larger than the plausible ΔROA premium in large US stocks after 2012.

What this does **not** show:
- that profitability improvement has no economic value;
- that the real F5 signal is unprofitable (it was never computed).

Per D250 §9, nothing further is started:
- no real-return OC-2 test or F5 ranking;
- no portfolio or H028 combination;
- no SYS-1;
- no further synthetic calibration;
- no data purchase;
- no Holdout.

## 15. Reproducibility record

- **Run:** `research/longhorizon/oc2/v2/OC2_V2_run.py`, from clean frozen commit 3adf5b4, started 2026-10-18 20:04 UTC, 15,043 s, 4 processes (single-threaded BLAS).
- **Seeds:** FINAL tag; sha256("OC2-V2|FINAL|<world>") + replication index.
- **Result:** `research/longhorizon/oc2/v2/OC2_V2_results.json` (commit fb49fb8; it records the protocol and code hashes).
- **Per-replication rows:** `data/oc2_v2_parts/` (60 files; gitignored; re-creatable bit-identically by rerunning the frozen driver at 3adf5b4).
- **Tables:** `OC2_V2_tables.py` (formatting only).
- **Engineering record:** `OC2_V2_engineering.json` (DEV seeds).
- **Failure-mode audit:** `OC2_V2_audit.json`.
- **Retries:** no technical retry was needed. The run executed exactly once.

## 16. No real returns or real F5 signals

Every characteristic, signal and return was generated synthetically. No real F5 value, stock ranking, price, return or Fama–MacBeth estimate was read or computed.

## 17. No QuantConnect runs or backtests

No QuantConnect project, backtest or data request. The session-start reachability check made no API call. No backtest of any kind.

## 18. H028 unchanged; Holdout sealed

- H028 files and status are unchanged: REJECTED, Frozen Defensive Research Reference.
- H029 / H030 are untouched.
- No post-2021 data was used, and the Holdout (2022-01-01 → 2026-08-31) remains sealed.
- Nothing was purchased.

---

**STOPPED — awaiting the owner's review.** Recommendation: close OC-2 → SPY.
