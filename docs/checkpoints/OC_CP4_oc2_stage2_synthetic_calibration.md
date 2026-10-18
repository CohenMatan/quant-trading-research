# OC-CP4 — OC-2 Stage 2: Synthetic Statistical Inference Calibration

**Owner decision:** D248, 2026-10-18 (`docs/owner/2026-10-18_oc2_pit_integrity_synthetic_calibration.md`). Stage 1 = PASS (OC-CP3).

**Frozen protocol:** `research/longhorizon/oc2/stage2/OC2_S2_protocol.md`.
- Original SHA-256 447b4860…, committed in f4dca7e **before any synthetic result**.
- Addendum 1 (technical crash fix, commit 9da492d) gives the current SHA-256 bcb872ad….

**Code:**
- `src/qresearch/oc2synth.py` (generator and inference);
- `OC2_S2_run.py` (driver);
- `OC2_S2_classify.py` (protocol-correct classification, written after the results);
- tests: `tests/test_oc2synth.py`, `tests/test_oc2_stage2.py`.

**Results:**
- `OC2_S2_results.json` (driver summaries);
- `OC2_S2_classification.json` (classification and diagnostics);
- per-replication synthetic rows in `data/oc2_stage2_parts/` (not committed; reproducible from the seeds).

**Synthetic data only.** No real signal, return, price or QuantConnect run; no Holdout; no purchase.

## Outcome: **D — INSUFFICIENT EVIDENCE** (and, independently, the method as specified fails false-positive control)

Three findings, each reported as found:

1. **A pre-registered scenario failed.** The diagnostic N13 (3-month overlapping horizon) produced no statistic in any of its 1,000 replications. Protocol §6.1: "any failed or incomplete scenario … → D". The driver printed "C" because it implemented only the adequacy part of §6.1. The committed protocol governs.
2. **False-positive control fails in 9 of 14 gating scenarios** (§6.2), so the method would be **C — NOT VALIDATED** even with a working framework. The failures are **bias, not standard errors**:
   - the spread of t is about 1.03–1.07 everywhere, as a calibrated test needs (except N9);
   - but t is shifted upwards whenever several priced characteristics correlated with F5 are controlled only linearly in their ranks, or are measured with error.
3. **The synthetic power results are not credible.**
   - The generated worlds have a monthly IC volatility of about 0.03, essentially pure sampling noise. LH-CP4 assumed a realistic 0.06–0.12.
   - So "100% power at +2% a year" is an artefact of too little realistic dependence, not a property of our data.
   - The adequacy checks fixed in advance did not test this. That is a framework weakness.

**In plain words.** The data side of OC-2 is sound (Stage 1). The statistical test is not yet trustworthy:
- **Too many false alarms.** Under realistic "no-edge" worlds it gives false positives more often than allowed. These come from other priced company characteristics leaking into the signal, not from badly estimated uncertainty.
- **No credible power estimate.** Our synthetic markets were too quiet to say how often a real edge would be detected.

**No real-data test should be run** under this protocol.

## 1. Verified state and authorisation

- `main` 081ee55 at the start.
- Stage 1 committed in 9940057 before any synthetic result (OC-CP3, PASS).
- D248 authorises synthetic-only calibration, then STOP.
- Statuses unchanged:
  - H028 REJECTED (frozen defensive research reference);
  - H029 / H030 NOT EVALUABLE;
  - OF-A unqualified (D245 unchanged);
  - OC-2 approved direction, not performance-tested;
  - no qualified strategy.
- Holdout sealed.

## 2. What was frozen before results

- **Inference method:** the monthly cross-sectional OLS of the demeaned next-month return on:
  - the centred F5 rank;
  - eight centred control ranks (size, beta, LOWVOL, MOM, BM, GPA, AG, ACC);
  - 11 FF12 dummies.
- **Statistic:** t = mean slope / Newey–West(3) standard error, one-sided, Student t(117); nominal 1% (c = 2.359).
- **Companions:** G2 top-quintile adjusted excess, G3 halves and G4 year concentration (full rule). Diagnostic standard errors: iid, Newey–West 6, stationary block bootstrap.
- **DGP:** 118 reviews built from the Stage 1 structure:
  - 447 → 1,019 valid stocks a review by year;
  - quarterly refresh in three phases (62 / 10 / 28%);
  - 2.4% churn;
  - 2016 FF12 mix;
  - F5–control correlations from P14-CP1;
  - characteristic correlations, premia and return-side variances as labelled assumptions;
  - total cross-sectional sd 6.5%.
- **Scenarios:**
  - 14 gating nulls, 4,000 replications each (family S standard-error worlds N0i … N12, plus N5a identification);
  - 3 diagnostics (N5b, N2L, N13), 1,000 each;
  - 15 power worlds, 1,000 each.
- **Criteria:** size ≤ 2.0% at 1% and 3.5–6.5% at 5% (RM2 §14, unchanged; 4,000 replications so a calibrated test fails the band by chance with probability 0.02%). Power ≥ 80% at +3% a year. Adequacy checks. D / C / A / B precedence.

## 3. Runs (every attempt recorded)

| Attempt | What happened | Results used? |
|---|---|---|
| 1 | Started after the freeze; numerical-library threads oversubscribed 4 cores (load 12). Stopped by Claude after about 11 minutes, before **any** scenario finished. No result produced or seen | — |
| 2 | Restarted with single-threaded BLAS (environment only; code unchanged). All 14 gating scenarios plus N5b and N2L completed. **Crashed** in the diagnostic N13 (IndexError: the 3-month response looked one review past the end) | Yes, cached rows reused |
| — | **Addendum 1** (commit 9da492d): one-line clamp of the cross-section size for t ≥ 118. It cannot affect any horizon-1 world. Recorded in the protocol with the new hash; no scenario, parameter, threshold or rule changed | — |
| 3 | Resumed: completed results reused from cache; N13 and the 15 power worlds run. N13 then produced NaN statistics in all 1,000 replications: a second N13 defect, because shrinking cross-sections drop stocks inside the 3-month window. **Not fixed**: it would be a further change after results | Yes |

Compute: about 1.5 hours on 4 local cores. Cost $0.

## 4. False-positive results (gating; nominal 1% / 5%; 4,000 replications)

| Scenario | Rejection 1% | Rejection 5% | Mean t | sd t | Apparent top-quintile effect | Passes? |
|---|---|---|---|---|---|---|
| N0i iid | 1.30% | 5.37% | −0.00 | 1.03 | 0.00% / yr | Yes |
| N0 structure, no priced factors | 0.97% | 5.55% | +0.01 | 1.04 | 0.01% | Yes |
| N1 LOWVOL priced | 0.95% | 5.15% | −0.02 | 1.03 | −0.01% | Yes |
| N2 AG (growth control) priced | 1.38% | 5.87% | −0.02 | 1.06 | 0.00% | Yes |
| N3 GPA priced | 1.40% | 4.98% | +0.04 | 1.04 | 0.01% | Yes |
| **N4 all eight priced** | 1.92% | **7.55%** | **+0.18** | 1.05 | +0.05% | **No** |
| N6 time-varying premia | 1.85% | **7.22%** | +0.15 | 1.05 | +0.05% | **No** |
| N7 strong dependence* | **4.10%** | **13.5%** | +0.53 | 1.04 | +0.05% | **No** |
| N8a churn 0× | 1.58% | **6.88%** | +0.17 | 1.04 | +0.06% | **No** |
| N8b churn 2× | 1.80% | **7.55%** | +0.16 | 1.04 | +0.05% | **No** |
| N9 persistent signal + own zero-mean premium | **2.95%** | **9.60%** | +0.13 | **1.17** | +0.06% | **No** |
| N11 missing not at random | 1.70% | **7.37%** | +0.17 | 1.04 | +0.05% | **No** |
| N12 t(3) tails | 1.50% | **7.55%** | +0.16 | 1.04 | +0.04% | **No** |
| **N5a controls with reliability 0.8 (identification)** | **6.40%** | **19.2%** | **+0.72** | 1.07 | +0.24% | **No** |

\* N7 has a **parameterisation defect**: its systematic variance exceeds the fixed 6.5% total, so the idiosyncratic noise collapsed to the floor (implied IC sd 0.008). Its failure is exaggerated. It is reported, not corrected.

**Diagnostics (1,000 replications each):**

| Scenario | Rejection 1% | Mean t | Apparent effect |
|---|---|---|---|
| N5b reliability 0.6 | 9.6% | +1.03 | +0.39% / yr |
| N2L latent growth priced, uncontrolled | 47.7% | +2.35 | +0.70% / yr |
| N13 | failed (NaN) | — | — |

**Alternative standard errors (5% level).** In N0 they reject at 5.2% (iid), 6.1% (Newey–West 6) and 6.7% (bootstrap, slightly liberal). In N4 they all reject 6.8–8.4%. **No standard-error choice repairs the failures**: they are a mean shift.

## 5. What fails, and why (owner §11: identification vs standard errors)

- **(a) Control functional form (N4 and its variants).** The synthetic premia are linear in each characteristic's normal score. The test controls with linear ranks, which cannot fully absorb the tails. F5's correlations with MOM (+0.175, priced +) and ACC (−0.177, priced −) both push the residual the same way. The result is a small upward bias in F5's slope:
  - t shifted by about +0.17;
  - about +0.05% a year economically;
  - enough to breach the 5% band (about 7.5% vs ≤ 6.5%) and to sit at the 1% limit (1.6–1.9%).
  - This is an **identification (specification) problem, not a standard-error problem**. A correctly specified (more flexible) control set would remove it in these worlds. In real data the true functional form is unknown.
- **(b) Measurement error (N5a, N5b, N2L).** If the true priced characteristic is observed only noisily, or not at all (latent growth), part of its premium is attributed to F5:
  - +0.24% a year at reliability 0.8;
  - +0.39% at 0.6;
  - +0.70% a year for an uncontrolled growth factor correlated 0.3 with F5.
  - No standard-error choice can fix this. It sets an **interpretation limit**: a real rejection is only meaningful if the measured effect is clearly larger than plausible leakage.
- **(c) Persistent slopes (N9).** With a persistent signal and a time-varying premium on it, the slopes are autocorrelated (ρ₁ ≈ 0.19). Newey–West lag 3 under-covers (sd t 1.17); lag 6 does better (8.9% at 5%, mostly the inherited N4 bias).
- **(d) Framework defects:**
  - N7's variance budget is inconsistent;
  - N13 fails when the cross-section shrinks;
  - all worlds have too little time-varying dependence in the signal payoff (implied IC sd about 0.03 vs a realistic 0.06–0.12).

## 6. Power (reported; **not credible**)

| Effect (top-quintile gross excess a year) | +1% | +2% | +3% | +4% … +6% |
|---|---|---|---|---|
| Main (N4 + planted), nominal 1% | 82.7% | 100% | 100% | 100% |
| Pessimistic | — | 100% | 100% | 100% |

- Correlation sensitivity (×0, ×2) and fresh-only information: all 100%.
- Full rule (G1–G4) at +3%: 41%; at +1%: 0%. G2's +3% floor binds, as expected.
- **Why these numbers cannot be used:**
  - every power world has an implied IC volatility of about 0.03 (the pessimistic family 0.008, from the N7 defect). That is about one third of the 0.09 main case of LH-CP4;
  - realistic dependence, such as industry-level and style-level shocks to the payoff of improving-profitability firms, was not generated;
  - **the realistic power remains the LH-CP4 / OC-CP2 analytical figure**: about 45–74% at +3% a year at nominal 1%, with +2% undetectable.

## 7. Calibration diagnostics

- KS distance of the one-sided p-values from uniform: 0.008 (N0i) and 0.016 (N0); larger where the bias exists.
- The mean slope autocorrelation is about 0 (T_eff ≈ 118–120) in all worlds except N9.
- Realised structure matched its targets in N0, N4, N11 and PM3:
  - sample size 746.5 vs target;
  - phase fresh shares 0.63 / 0.13 / 0.30;
  - cross-sectional sd 6.3–6.5%;
  - F5–control correlations within 0.05.

## 8. Economic relevance (owner §15)

This stage evaluated only whether the method could reliably detect (1) statistically significant information and (2) an economically meaningful gross cross-sectional effect. It says nothing about:
- a realisable portfolio;
- costs;
- SPY outperformance;
- complementarity with H028;
- long-term wealth.

The future portfolio constraints are unchanged:
- ≥ $2B, price ≥ $5, ADV20 ≥ $5M, long-only;
- $100K baseline / $200K diagnostic;
- $7 per order, 0.10% slippage per side;
- at most 15 positions.

## 9. Answer to the owner's question (§19)

- **Can our existing point-in-time data support the exact OC-2 signal?** Yes (Stage 1 PASS).
- **Can we validate a statistical method reliable and powerful enough to test it?** **Not with this protocol.**
  - The method as specified has too many false positives under realistic correlated-factor worlds, from control misspecification and measurement-error leakage.
  - The synthetic framework could not produce a credible power estimate.
- **The limitation is recorded and the work STOPS.** No real-data proposal is made under this protocol.

## 10. Next owner decision (choose one)

1. **Stop OC-2.** Return to SPY as the offensive complement (OC-1; SYS-1 or OC-CP1 option 2).
   - Justification: the cleanest outcome.
   - What is known: the data are sound, but a valid test would need a further revision whose best plausible result is "calibrated but underpowered" (LH-CP4).
2. **Approve one revised synthetic protocol (Stage B-OC2 v2)** — RM2 §14 allows at most one pre-specified revision. It would change these things, all frozen before any result:
   - **(a) Flexible controls:** each control entered as decile dummies or as rank + rank², to remove the functional-form bias of §5(a).
   - **(b) Standard error:** Newey–West lag 6 as the primary, given N9.
   - **(c) Realistic payoff dependence:** a persistent, sector- and style-level time-varying payoff on signal-correlated characteristics, set so the implied IC sd spans the LH-CP4 range 0.06 / 0.09 / 0.12. These are assumptions, never estimated from real returns. Power is gated in the 0.09 case.
   - **(d) Defect fixes:** a consistent variance budget for N7; N13 re-specified on a fixed panel.
   - **(e) An explicit, owner-set tolerance for identification leakage**, e.g. a real effect must exceed the N5a / N2L leakage bound. Measurement error cannot be removed by any method.
   - Expected outcome: at best **B — calibrated but underpowered** at +3% a year.
3. **Accept the analytical (LH-CP4-type) limits** and decide directly whether a real test with roughly 45–74% power at +3% a year is worth one look. Not recommended: the false-positive problem above would then be unresolved.

**Recommendation: option 1, unless the owner wants the one permitted revision (option 2) with the understanding that its best realistic result is "calibrated but underpowered".**

STOPPED. No real-return test, portfolio, SYS-1, H028 change, purchase or Holdout access.
