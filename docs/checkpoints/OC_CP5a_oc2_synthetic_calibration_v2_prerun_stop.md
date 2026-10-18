# OC-CP5a — OC-2 Synthetic Calibration v2: pre-run STOP for an owner decision

**Owner decision:** D249 (`docs/owner/2026-10-18_oc2_synthetic_calibration_v2.md`): one final controlled methodological repair attempt of the OC-2 synthetic calibration.

**Outcome of this checkpoint: STOPPED BEFORE THE CONFIRMATORY EVALUATION.** The repaired method is built, engineering-validated and written into a complete draft protocol. One part of the written criterion cannot coherently address two of the owner's required null worlds:
- noisy controls (N5a / N5b);
- a priced latent factor (N2L).

The owner's instruction for this case (D249 §7 and §10) is to "STOP before confirmatory evaluation and request a specific owner decision". This checkpoint does that.

**What the owner gets from it:**
- No v2 classification exists yet.
- v1 (OC-CP4) stays **D — INSUFFICIENT EVIDENCE**, unchanged.
- No v2 scenario rejection rate and no v2 power was simulated.

**Decision requested (one line):** choose how the identification family is treated — Option 1 strict, Option 2 decision-rule gate with a scoped claim, or Option 3 stop OC-2 → SPY (section 25). My recommendation is Option 2 if OC-2 is to continue at all; Option 3 is defensible.

The owner's 27 deliverable items follow. Items 16–20 and 22 are scheduled for the confirmatory run and are marked NOT RUN.

---

## 1. Repository verification

- Main was clean at 1d2605d (PR #113 merged). D248 was the latest decision; this approval is recorded as D249.
- Read in full: OC-CP2, OC-CP3, OC-CP4, the v1 protocol (447b4860… + Addendum 1 = bcb872ad…), `oc2synth.py`, `OC2_S2_run.py`, `OC2_S2_classify.py`, the results and classification JSON, D238 / D239, the frozen F5 definition, and the Stage 1 artifacts.
- H028 remains REJECTED and frozen (STATUS: "Frozen Defensive Research Reference", descriptive only).
- H029 / H030 remain NOT EVALUABLE.
- The Holdout is sealed: no `HOLDOUT_UNLOCK.md`; nothing after 2021 was used.

## 2. Owner decision record

- The owner message is recorded verbatim in `docs/owner/2026-10-18_oc2_synthetic_calibration_v2.md`.
- DECISIONS D249.

## 3. Original OC-CP4 classification preserved

Every file under `research/longhorizon/oc2/stage2/` is untouched, and v1 is not relabelled:
- `OC2_S2_results.json` (driver outcome C);
- `OC2_S2_classification.json` (**D**, failed N13; size failures N4, N6, N7, N8a, N8b, N9, N11, N12, N5a);
- the v1 module `oc2synth.py` (SHA-256 fc701816…, unchanged since Addendum 1).

v2 imports v1's population constants read-only.

## 4. Complete v1 failure-mode analysis

`research/longhorizon/oc2/v2/OC2_V2_audit.{py,json}`: frozen-v1-code reproduction plus large-sample population algebra (n = 400,000 synthetic stocks; no returns simulated).

| cause | v1 symptom | type | v2 treatment |
|---|---|---|---|
| A1 N7 variance budget | systematic variance 0.00588 > total 0.00423, so the idiosyncratic sd hit the floor (0.1% a month) | functional defect | budget guard (≤ 60% systematic), v2 N7 re-parameterised (item 5) |
| A2 N13 NaN | 11 of 118 months have a NaN 3-month response (10 shrink months) | functional defect | every slot trades, id tracking (item 6) |
| A3 classifier | driver printed C; protocol §6.1 says D | functional defect | one tested `classify` function, precedence written first (item 24) |
| B nonlinear leakage (N4 family) | N4 t mean +0.18 | **method** (rank controls mis-specify linear-in-characteristic premia) | restricted cubic splines (item 7) |
| C1 measurement error (N5a / N5b) | N5a t mean +0.72 | **identification** (observed-controls bias) | not removable; owner decision (items 8, 21) |
| C2 latent factor (N2L) | 47.7% rejection at 1% | **identification** | not removable; owner decision (items 9, 21) |
| D quiet market | implied IC sd 0.03 vs 0.06–0.12 | **DGP omission** (no payoff on the signal) | AR(1) signal payoff, calibrated to three regimes (items 12–13) |

**Population bias of the F5 coefficient** (apparent gross top-quintile effect, % a year; truth 0):

| null mechanism | v1 rank controls | v2 spline controls |
|---|---|---|
| N4 all controls priced, normal-linear | +0.044 | 0.000 |
| N4r premia linear in uniform rank | 0.000 | +0.001 |
| N4q premia only in the extreme deciles | +0.101 | −0.001 |
| N5a controls' reliability 0.8 | +0.246 | +0.216 |
| N5b reliability 0.6 | +0.412 | +0.393 |
| N2L1 latent growth +1% | +0.278 | +0.231 |
| N2L latent growth +3% | +0.746 | +0.694 |
| N2L5 latent growth +5% | +1.214 | +1.156 |
| N2L +3% with the latent factor as an (oracle) control | +0.099 | 0.000 |

What the table shows:
- The functional-form part (B) is fully repaired by the spline.
- The measurement-error and latent-factor parts (C) survive any observed-control specification, and only the impossible oracle removes them.
- The quiet market (D) was not a standard-error scaling problem. Separating the components:
  - cross-sectional return dispersion was realistic (6.5% a month);
  - premium variability existed only in N6 / N9;
  - sector shocks are absorbed by the dummies;
  - control-factor shocks are absorbed by the control coefficients (they would add ≈ 0.045 to a univariate IC);
  - residual noise was realistic except in N7;
  - what was missing is the month-to-month payoff on the signal itself, which also sets the IC's serial correlation.

## 5. N7 correction

- `variance_budget` refuses any world whose systematic variance exceeds 60% of the 6.5% total. The v1 N7 parameters are refused: 0.00590 > 0.00254.
- v2 N7 = sector shocks 3.5%, factor shocks 1.1%: systematic share 56.7%, idiosyncratic sd 4.28% a month.
- That is the strongest sector / factor shock structure that still leaves a realistic idiosyncratic component. Every world passes the guard (tested).

## 6. N13 correction

- Returns are generated every month for every slot. A stock leaving the universe keeps trading, and each slot carries a stock id.
- An overlapping 3-month response accumulates only while the slot holds the same stock. On exit it stops, which is the delisting convention.
- Engineering check (DEV seeds):
  - 0 failures and finite statistics at the realistic size (≥ 410 stocks) with churn 0 and 1;
  - the same at 0.1× size (39–40 stocks) with churn 1 and 2;
  - in unit tests, at 0.1× / churn 2 and at full size / churn 0.

## 7. N4 nonlinear-factor treatment

**Primary controls:**
- each control → cross-sectional normal score Φ⁻¹(rank);
- → restricted cubic spline, with 5 knots fixed at the normal quantiles 0.05 / 0.275 / 0.5 / 0.725 / 0.95 (Harrell's default placement) — 4 columns per control, linear tails.

**Why this specification:**
- It is fixed in advance and covers linear, rank-linear and tail-concentrated premia with population bias below 0.002% a year (item 4).
- It was chosen from the population-bias algebra, not from any rejection rate.
- There is no model search; v1 rank controls are kept only as a non-gating diagnostic.

**Remaining risk:** a premium shape the spline cannot represent, e.g. sharp interactions between controls, is not covered. No interaction world exists in the owner list.

## 8. N5a noisy-controls treatment

- Measurement error in a control correlated with F5 biases the F5 coefficient in the direction of that control's premium. That is classical errors-in-variables.
- No observed-controls estimator removes it.
  - Instrumenting would need a second, independent measurement of each control, which the future real test does not have.
  - Any estimator that "corrects" for an assumed reliability would build an unverifiable number into the test.
- The audit gives +0.22% a year of apparent effect at reliability 0.8 and +0.39% at 0.6.
- Analytic projection of the primary test's 5% rejection: 7.5–11% (item 21). It fails the [3.5%, 6.5%] criterion in every IC regime.
- v1's own simulated N5a shift agrees once scaled to v2's realistic noise (+0.25 vs +0.29 t).

## 9. N2L latent-factor identification assessment

N2L prices an unobserved "growth" characteristic, correlated 0.30 with F5, that is never a control.

**False signal magnitude** (population): about **+0.23% a year of apparent F5 effect per +1% a year of latent premium**. It is linear in factor strength: +0.23 / +0.69 / +1.16% at +1 / +3 / +5%.

**Proxy effects:**
- F5 partly proxies the latent factor.
- Adding the latent factor as a control (oracle) removes the bias exactly (0.000).
- The observed controls (GPA, AG, MOM…) absorb only a little of it (+0.746 → +0.694 even with the better spline).

**Projected 5% rejection** of the primary test:

| N2L strength | IC sd 0.06 | 0.09 | 0.12 |
|---|---|---|---|
| +1% | 11.6% | 8.9% | 7.7% |
| +3% | 38.7% | 23.1% | 16.9% |
| +5% | 73.3% | 44.8% | 31.0% |

**Scope of any alpha claim:** the future real test can show only that F5 predicts returns **incrementally to the eight observed controls as measured**. It cannot exclude that the predictive content belongs to an unobserved or mismeasured characteristic correlated with F5.

The scenarios stay in the official evaluation under every option (item 25).

## 10. Primary v2 estimator specification

Protocol §2 (`research/longhorizon/oc2/v2/OC2_V2_protocol.md`):
- monthly cross-sectional OLS of the demeaned next-month return (not winsorised) on [centred F5 rank | 8 control splines | 11 FF12 dummies | intercept];
- complete case on missing controls;
- Fama–MacBeth mean of the F5 slope (Frisch–Waugh / QR);
- companions G2 (top-quintile dummy, top minus universe), G3 (halves) and G4 (year concentration); full rule as v1.

Correlations between F5 and the controls are built into the DGP (realised in N4: MOM 0.171, ACC −0.174, GPA 0.104, AG 0.077, BM −0.07, LOWVOL −0.048, against targets 0.175 / −0.177 / 0.105 / 0.078 / −0.07 / −0.05). Estimator stability under changing N is tested in N14 / N14s and P3-n50.

## 11. Covariance / standard-error methodology

**Lag:**
- Newey–West, Bartlett, **lag 7**, fixed prospectively: the Andrews AR(1) plug-in 1.1447(αT)^{1/3} with α = 4ρ² / (1 − ρ²)² at the most persistent assumed slope dependence ρ = 0.5, T = 118 → 6.8 → 7.
- Lags 4 and 0 (iid) are non-gating diagnostics.

**Critical values:** fixed-b one-sided values of the NW(7) t under iid Gaussian slopes, T = 118, 2,000,000 draws, re-computed identically:
- 5%: 1.7769;
- 1%: 2.5904 (normal 2.326);
- 0.5%: 2.9050;
- 0.1%: 3.5886.

The fixed-b limit does not depend on the dependence structure, so one set of critical values serves every world.

**What the run reports, per world, separately:**
- SE calibration: mean NW SE / across-replication sd of mean(b);
- bias: mean of mean(b), truth 0;
- identification: family membership.

## 12. Synthetic market parameter justification

| parameter | value | source |
|---|---|---|
| cross-section | 447 → 1,019 valid stocks a review, mean 746.5, × 0.95 after missing controls | Stage 1 (OC-CP3) |
| sectors | FF12 mix, financials excluded | v1 / Stage 1 |
| refresh phases | 0.62 / 0.10 / 0.28 | Stage 1 |
| exits / entries | 2.4% / 2.9% | Stage 1 |
| F5–characteristic correlations | MOM 0.175, ACC −0.177, GPA 0.105, AG 0.078, BM −0.07, LOWVOL −0.05, latent 0.30 | v1 (OC-CP2 frozen-factor values) |
| total return sd | 6.5% a month | LH-CP4 |
| noise | t(5) | v1 |
| LOWVOL heteroskedasticity | 0.30 | v1 |
| characteristic AR | 0.95 | v1 |
| F5 AR | 0.70 | v1 |
| IC sd regimes | 0.06 / 0.09 / 0.12 | owner D249 §6 / LH-CP4 |
| signal payoff AR | 0.10 (0.30 in N9) | assumption: monthly premia close to serially independent |

## 13. Realistic variability checks (engineering, DEV seeds, 48 replications per regime)

| IC regime | partial IC sd | raw rank IC sd | slope ρ₁ | refresh shares | sec / rep |
|---|---|---|---|---|---|
| 0.06 | 0.061 | 0.071 | 0.05 | 0.631 / 0.127 / 0.304 | 0.42 |
| 0.09 | 0.090 | 0.092 | 0.08 | 0.631 / 0.129 / 0.302 | 0.42 |
| 0.12 | 0.118 | 0.116 | 0.07 | 0.633 / 0.128 / 0.300 | 0.42 |

- Mean valid cross-section: 709 (minimum 409–412).
- The generator produces the required IC regimes; v1 produced 0.03.
- The refresh shares sit 0.03 above Stage 1 in phases B and C because entrants arrive fresh. That is within the protocol's ±0.05 adequacy band.
- Payoff calibration (G_SD) re-computes identically.
- All 56 planned worlds run once without failure (DEV seed).

## 14. Frozen protocol and hashes

**NOT FROZEN — draft.** `OC2_V2_draft_hashes.json` records the draft SHA-256 values:

| file | draft SHA-256 |
|---|---|
| protocol | 4f7624dd… |
| `oc2synth_v2.py` | 684847a9… |
| `oc2synth.py` (v1, unchanged) | fc701816… |
| `OC2_V2_scenarios.py` | 179d8ed9… |
| `OC2_V2_run.py` | f9a533d9… |
| `OC2_V2_engineering.py` | 00014a30… |
| `OC2_V2_audit.py` | 9058ac86… |

A test fails if any of these files changes.

**Freeze procedure (protocol §12):** status line + §9 choice + `FROZEN.json` with hashes + test pins, then exactly one run. The driver refuses to start without `FROZEN.json` (tested).

## 15. Reproducibility seeds

- Seeds = sha256("OC2-V2|<tag>|<world>") + replication.
- FINAL seeds are reserved for the one confirmatory evaluation and have never been used.
- Engineering used DEV, TEST and SMOKE tags only.
- Same seed → identical statistics (tested); per-replication rows will be stored by world.

## 16. Full null-scenario results — NOT RUN

Pre-run STOP (protocol §9). The planned set is in protocol §5:
- 25 central null worlds × 4,000 replications;
- 14 regime copies × 2,000;
- oracle × 1,000.

## 17. False-positive results at 1% and 5% — NOT RUN

The only figures available are the analytic projections for the identification family (item 21) and the population bias (item 4). No simulated v2 rejection rate exists.

## 18. Monte Carlo uncertainty (planned)

- Wilson 95% intervals for every rate.
- MC sd at a true 5% / 1%: 0.34 / 0.16 points at 4,000 replications; 0.49 / 0.22 points at 2,000.
- A correctly sized method would fail the 5% band by chance with negligible probability at 4,000 replications: 4.4 MC sd from the band edges.

## 19. Planted-signal power results — NOT RUN

- Planned: +2 / +3 / +4 / +5% a year × three IC regimes, plus correlation (× 0, × 2), quarterly arrival and half-size cells; 1,000 replications each.
- Primary metric: rejection at 1%. Full-rule pass rate reported.
- Disclosed in advance: the full rule's own +3% G2 floor caps full-rule power near 50% at a true +3%.

## 20. Minimum detectable effects — NOT RUN

Planned MDE50 / MDE80 by interpolation of the power curve per regime, and T_eff. The earlier analytic figures stay as they were:
- LH-CP4 / OC-CP2: power at +3% about 45–74%;
- +2% undetectable.

## 21. Identification limitations

**Analytic projection** (population bias × DEV slope scale, through the fixed-b reference distribution; not a simulated scenario). Primary-test rejection, 5% / 1%:

| world | IC sd 0.06 | 0.09 | 0.12 |
|---|---|---|---|
| N5a (reliability 0.8) | 11.0 / 2.7 | 8.5 / 2.0 | 7.5 / 1.7 |
| N5b (0.6) | 19.0 / 5.6 | 12.9 / 3.3 | 10.4 / 2.5 |
| N2L1 (+1%) | 11.6 / 2.9 | 8.9 / 2.1 | 7.7 / 1.7 |
| N2L (+3%) | 38.7 / 15.8 | 23.1 / 7.4 | 16.9 / 4.8 |
| N2L5 (+5%) | 73.3 / 45.0 | 44.8 / 19.7 | 31.0 / 11.4 |

**Upper bound on full-rule false promotion**, from P(G2 ≥ +3%) alone:

| world | IC sd 0.06 | 0.09 | 0.12 |
|---|---|---|---|
| N5a | 0.0% | 0.03% | 0.5% |
| N2L | 0.0% | 0.2% | 1.6% |
| N2L5 | 0.1% | 1.2% | 4.4% |

In plain words:
- The t-test cannot be correctly sized against "no F5 premium beyond the TRUE characteristics" when the data contain mismeasured or missing ones.
- The +3% economic floor of the decision rule keeps false promotion low, because these biases are well below +3% a year.
- The limitation is structural (data), not computational.

## 22. Failed and incomplete scenarios

- None in engineering: 56 / 56 worlds ran (DEV).
- The confirmatory run has not happened, so no confirmatory failures exist.

## 23. Comparison with v1, without rewriting v1

| | v1 (OC-CP4, final: D) | v2 (draft) |
|---|---|---|
| controls | linear ranks | splines of normal scores |
| SE | NW(3), Student t(117) | NW(7) from a stated lag rule, fixed-b critical values |
| signal payoff | none (IC sd 0.03) | AR(1) payoff, IC sd 0.06 / 0.09 / 0.12 verified |
| N7 | defective (noise-free world) | budget-guarded |
| N13 | crashed, then NaN | finite at 40–1,019 stocks |
| classifier | driver ≠ protocol | one tested function |
| scenarios | 14 gating + 3 diagnostic | 39 null worlds (owner §7 list + regime copies) + oracle + 16 power cells |

v1's classification stays D. Nothing in v2 changes v1's results or labels.

## 24. Official A / B / C / D classification

**None.** The confirmatory evaluation was not run, by design (owner D249 §10).

**Classification precedence**, fixed in the draft before any run (protocol §8):
1. **D** — missing or failed required evidence: > 1% failures or an incomplete world, or a generator-adequacy miss.
2. **C** — any calibration-family size failure, or an identification-family failure under the chosen option.
3. **A** — power at +3%, central regime, at 1% is ≥ 0.80.
4. **B** — otherwise.

`OC2_V2_run.decide` implements this and is unit-tested against the text, including both §9 options.

## 25. Exact recommendation for owner review

Please choose one option for the identification family (protocol §9):
- **Option 1 — strict (v1 parity).**
  - N5a, at all regimes, is gated by the t-test size criterion; N5b / N2L are reported.
  - Projected result: **C — NOT VALIDATED** with near certainty (N5a 5% rejection 7.5–11% in every regime), regardless of everything else.
  - It costs about 4 h of compute to confirm a foreseeable answer.
- **Option 2 — decision-rule identification gate (my recommendation, if OC-2 continues).**
  - The size criterion applies, unchanged, to the 30 calibration-family worlds: pure null, priced market / size / LOWVOL / profitability / growth, nonlinear premia, time-varying premia, shocks, heavy tails, overlap, churn / MNAR, small N, irregular timing.
  - N5a and N2L (+3%) are gated at every regime by **full-rule false promotion ≤ 2.0%**.
  - The t-test inflation, bias and factor-strength dependence (N2L1 / N2L5, N5b) are reported in full.
  - Any future real-data result must carry the scoped claim: "incremental to the observed controls as measured; it cannot exclude correlated unobserved or mismeasured premia (≈ +0.23% a year of apparent effect per +1% of latent premium)".
  - This is a weaker treatment of N5a than v1's. It is proposed before any v2 result and must be judged as such.
  - The official evaluation then turns on the calibration family and on power, which the run would measure for the first time.
- **Option 3 — stop.** No run; OC-2 closes on the current data and methods; SPY (OC-1) remains the offensive complement.
  - Defensible because even a clean A / B would only permit one real-data test, whose prior is low (no qualified candidate across H001–H030).
  - The real-data test would also be underpowered below about +3% a year.

After the decision I would freeze the protocol (status line, §9 choice, `FROZEN.json`, test pins), run the one confirmatory evaluation (≈ 4.2 h, FINAL seeds), write OC-CP5 and STOP.

## 26. Confirmation: no real returns, signals or backtests

- No real F5 value, return, price, Fama–MacBeth estimate, QuantConnect run, backtest or portfolio was read or computed.
- The only committed inputs read were synthetic v1 artifacts (`oc2_stage2_parts`, synthetic rows) and the v1 classification.
- The v2 module contains no file, network or real-data access (tested).
- H028 is unchanged; H029 / H030 were not reactivated; SYS-1 was not run; nothing was purchased.

## 27. Confirmation: no Holdout information

No post-2021 data or Holdout information was accessed. The Holdout remains sealed.

---

**STOPPED — awaiting the owner's §25 decision.** Nothing further is authorised:
- no confirmatory run;
- no real-data test;
- no OC-2 portfolio, SYS-1 or H028 combination;
- no v3;
- no new data or hypothesis;
- no Holdout access.
