# OC-2 Stage 2 — synthetic statistical inference calibration: frozen protocol

**Owner decision:** D248 (`docs/owner/2026-10-18_oc2_pit_integrity_synthetic_calibration.md` §8–§15).
**Precondition met:** Stage 1 = PASS — PIT-SAFE AND SUFFICIENT (OC-CP3, commit 9940057).
**Committed before any synthetic result.** The run script refuses to start unless the two code files carry the SHA-256 values below (`verify_frozen`). The protocol's own hash is recorded in the result and pinned in `tests/test_oc2_stage2.py`. Any substantive change after a result needs a new owner decision.

**Scope:**
- synthetic data only: characteristics, signal and returns are generated;
- no real signal, return, price or QuantConnect run;
- no Holdout, no purchase.

**Frozen code:**
- `oc2synth.py` SHA-256: `adde2d4cbafebd3390f8ece545f587f4a7637ce73097fe1ac4e1901169bcba77`
- `OC2_S2_run.py` SHA-256: `08018d283183673bfb5c5fbeeddac8a62f8495ef126b98af2d84cd53fc2fbfed`

## 1. Question

Does the proposed real-data test control false positives under realistic null worlds, and can it detect a +3% a year gross top-quintile effect over 2012-02 → 2021-11?

That real-data test is the OC-CP2 §10 universe-wide Fama–MacBeth test of the frozen F5 signal with controls. No synthetic result is evidence that OC-2 has an edge.

## 2. Inference method (the one being validated)

**Each review t (118 reviews):**
- the sample is the stocks with a valid signal;
- the response is the next-month return minus the sample's equal-weight mean;
- OLS of the response on:
  - the centred signal rank;
  - eight centred control ranks (size, beta, LOWVOL, MOM, BM, GPA, AG, ACC);
  - 11 FF12 sector dummies (financials excluded).
- The slope on the signal rank is b_t.

**Primary statistic:**
- t = mean(b) / SE, where SE is the Newey–West estimate with fixed lag 3 (Bartlett weights);
- **one-sided** test, critical values from Student t with 117 degrees of freedom;
- nominal 1% (c = 2.359) is the proposed real-test level; 5% is also reported.

**Real-test companion statistics (reported, not validated as tests):**
- G2: controls-adjusted top-quintile excess = 12 × 0.8 × mean of the monthly coefficient on a top-quintile dummy, in the same regression with the signal rank replaced by the dummy. This is top-minus-universe.
- G3: positive mean slope in both halves (reviews 1–59 and 60–118).
- G4: no calendar year supplies more than 50% of the sum of monthly slopes.
- **Full rule** = G1 (t > 2.359) ∧ G2 ≥ +3% ∧ G3 ∧ G4.

**Diagnostic standard errors** (never substituted for the primary one):
- iid Fama–MacBeth t;
- Newey–West lag 6;
- a one-sided stationary block bootstrap (mean block 6, 499 resamples).

**Not used:** identity-tether or pointer permutations (D235, D238), matched twins (D239), time-series factor regressions (D239).

**Controls' historical availability in the real test:**
- LOWVOL, MOM, GPA, BM, AG and ACC use the frozen H024 point-in-time definitions (D201);
- size is point-in-time market cap;
- sector is the SEC SIC at filing (FF12);
- beta is the one new control: 252-session OLS beta against SPY from past daily returns only (≥ 200 sessions).
- None uses information after the selection day.

## 3. Synthetic data-generating process (`oc2synth.Panel`)

| Element | Value | Source |
|---|---|---|
| Reviews | T = 118, first in February, plus 24 warm-up months | OC-CP3 window |
| Cross-section | Valid-signal stocks per review, by year: 447, 543, 710, 751, 741, 766, 801, 839, 847, 1,019 (2012 → 2021), interpolated monthly | OC-CP3 post-hoc (vendor-side F5 valid) |
| Sectors | 11 FF12 sectors with 2016 Stage 1 weights | OC-CP3 |
| Churn | Exits 2.4% a review, replaced by entrants; growth fills to the cross-section size | OC-CP3 |
| Refresh | Each stock refreshes once a quarter in its phase: Feb/May/Aug/Nov-type 62%, Mar/Jun/Sep/Dec-type 10%, Jan/Apr/Jul/Oct-type 28%. Between refreshes the signal is stale. Entrants arrive fresh | OC-CP3 refresh shares 0.625 / 0.097 / 0.270 |
| Characteristics | Size, beta, LOWVOL, MOM, BM, GPA, AG, ACC and a latent growth G: standard normal, correlation matrix C (`oc2synth._C`), monthly AR(1) 0.95 | Assumption (signs and magnitudes typical of the literature) |
| Signal | s = β′Z + √(1 − β′Cβ)·u, refreshed quarterly; u is AR(1) 0.70 per quarter; β = C⁻¹ρ | — |
| Target correlations ρ(s, ·) | MOM 0.175, ACC −0.177, GPA 0.105, AG 0.078, BM −0.07, LOWVOL −0.05, size 0, beta 0, G 0.30 | P14-CP1 committed F5-A medians; size, beta and G are assumptions |
| Returns | r = Σ_k (θ_k + f_kt) Z_k + 0.3·Z_beta·m_t + sector shock + planted + idiosyncratic | — |
| Return components | f_kt: zero-mean factor shocks, sd 1.0% per sd. m_t: market, sd 4.5%. Sector shocks: sd 2.5%. Idiosyncratic: Student t(5), heteroskedastic (exp(−0.3·LOWVOL), normalised) | — |
| Total cross-sectional sd | Kept at 6.5% a month (the idiosyncratic sd absorbs the rest) | LH-CP4 assumption |
| Priced factor premium (when priced) | ±3% a year top-quintile excess per characteristic, with literature signs: LOWVOL +, MOM +, BM +, GPA +, size −, beta −, AG −, ACC −. As strong as the effect the test must detect, which is conservative given the programme's weak factor evidence | — |
| Planted effect | θ_sig·s with θ_sig = e / (12 × 1.40), so the signal's own top-quintile gross excess over the universe = e a year. The information persists while the signal is stale | Owner §13 |
| Seeds | Replication r of scenario X uses SHA-256("OC2-S2\|X")[:8] + r; bootstrap seeds use "X\|boot" | — |

**Why these worlds approximate the real data without returns:**
- size, timing, churn, sector mix, missingness and signal–control correlations come from Stage 1 and P14-CP1 non-return aggregates;
- return-side magnitudes are labelled assumptions (as in LH-CP4);
- the factor premia are deliberately as strong as the target effect.

## 4. Null scenarios (no planted signal)

**Family S (standard-error calibration; GATING; 4,000 replications each):**

| ID | World | Owner §11 mechanism |
|---|---|---|
| N0i | iid Gaussian returns, independent characteristics, signal refreshed monthly, fixed sample | Sanity |
| N0 | Full structure, no priced factors | 1, 8, 9, 10, 11, 12, 13 (structure in every world below) |
| N1 | LOWVOL priced | 2 |
| N2 | Asset growth (AG, the growth control) priced | 3 |
| N3 | GPA priced | 4 |
| N4 | All eight controls priced | 5 |
| N6 | N4 with time-varying premia θ_k(1 + 2ξ_kt), ξ AR(1) 0.3 | 7 |
| N7 | N4 with sector-shock sd 5% and factor-shock sd 2% | 8 |
| N8a / N8b | N4 with churn 0× / 2× | 9 |
| N9 | N4 with signal AR 0.90 and a zero-mean AR(0.5) premium on the signal itself (sd equal to the +3% effect) | 10 |
| N11 | N4 with missing-not-at-random signals: about 18% missing, more for high-volatility stocks and retail (Shops); the sample size is kept at the targets | 12 |
| N12 | N4 with Student t(3) tails and heteroskedasticity exp(−0.6·LOWVOL) | 13 |

**Family I (identification):**

| ID | World | Status |
|---|---|---|
| N5a | N4 with every control observed with reliability 0.8 (squared correlation with the true priced characteristic) | **GATING** (4,000) |
| N5b | Reliability 0.6 | Diagnostic (1,000) |
| N2L | N4 plus the latent growth G priced (+3%). G is never a control: ρ(s, G) = 0.30, AG proxies G at 0.4 | Diagnostic (1,000) |

**Identification vs standard errors** (owner §11):
- In N5 / N2L, part of a priced characteristic is not controlled, and the signal is correlated with it. A rejection there is **omitted-variable leakage**, not a wrong standard error: no standard-error choice can remove it.
- N5a sets a realistic measurement-error level as an essential identification requirement.
- N5b and N2L measure how large the leakage would be under harsher assumptions. They define the interpretation limit of a real rejection (reported as the mean apparent top-quintile effect).

**N13 (diagnostic; 1,000):** N4 with a 3-month overlapping response (churn 0, Newey–West lag 5). Only for the decay diagnostics of the real test, never the primary test.

## 5. Planted alternatives (power; 1,000 replications each)

- **PM1–PM6** (main): N4 with e = +1%, +2%, +3%, +4%, +5% and +6% a year.
- **PP2–PP6** (pessimistic): N4 combined with N7 dependence and N12 tails; e = +2 … +6%.
- **Sensitivity at +3%:**
  - PC0: no signal–control correlation;
  - PC2: twice the correlation;
  - PF3 / PF5: information only in the first month after a refresh (×3 there, so the same average excess), at +3% and +5%.

## 6. Criteria and outcome (fixed now)

**6.1 Framework adequacy (D triggers)**, checked on N0, N4, N11 and PM3:
- the realised mean sample size is within 5% of the target;
- the realised fresh share for each phase type is within 0.07 of the Stage 1 share + 0.03 (entrants);
- the realised cross-sectional sd is 5.5–7.5%;
- each realised signal–control correlation is within 0.05 of its target.
- Any miss, any failed or incomplete scenario, or any internal inconsistency → **D — INSUFFICIENT EVIDENCE**.

**6.2 False-positive control** (every gating scenario: family S and N5a):
- rejection at nominal 1% **≤ 2.0%**;
- rejection at nominal 5% **within [3.5%, 6.5%]** (RM2 §14, unchanged).
- **Replication count:** 4,000 per gating scenario, not the 1,000 minimum, because of the 5% band. With 1,000 replications a perfectly calibrated test would fall outside it in at least one of 14 scenarios with probability 29%. With 4,000 that probability is 0.02%, and P(rate > 2% | true 1%) < 10⁻⁸.
- This tightens precision. It changes no threshold.
- **Calibration diagnostics** (reported, non-gating): the Kolmogorov–Smirnov distance of the one-sided p-values from uniform; the mean and sd of t; the diagnostic standard errors.

**6.3 Power:**
- the rejection rate of the primary test at nominal 1% in PM3 (+3% a year) is the power at the economically meaningful effect;
- **sufficient power = ≥ 80%** (RM2 §14);
- also reported:
  - power at nominal 5%, 0.5% and 0.1% (the programme's multiple-testing context);
  - the full-rule pass rates;
  - MDE at 50% / 80% by linear interpolation (main and pessimistic);
  - the realised slope autocorrelation and T_eff = T(1 − ρ)/(1 + ρ);
  - the sensitivities.

**6.4 Outcome:**
- **D** if 6.1 fails.
- Else **C — METHOD NOT VALIDATED** if any gating scenario fails 6.2.
- Else **A — METHOD VALIDATED WITH USEFUL POWER** if PM3 power ≥ 80%.
- Else **B — METHOD CALIBRATED BUT UNDERPOWERED**.
- One favourable scenario never validates the method. The threshold, effect target, method and scenarios are not changed after results.

## 7. Stopping rules

- A crash or incomplete run is recorded and re-run with the same seeds. Nothing else may change.
- No parameter, scenario or method is altered after any result.
- After the outcome: write the checkpoint and STOP for the owner, whatever the outcome.
- No real-return test follows automatically.

## 8. Outputs

- `OC2_S2_results.json` (summaries);
- per-replication synthetic rows in `data/oc2_stage2_parts/` (not committed; reproducible from the seeds);
- the checkpoint `docs/checkpoints/OC_CP4_oc2_stage2_synthetic_calibration.md`.
