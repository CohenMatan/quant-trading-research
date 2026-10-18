# OC-2 synthetic calibration v2 — protocol (DRAFT — NOT FROZEN)

**Owner decision:** D249 (`docs/owner/2026-10-18_oc2_synthetic_calibration_v2.md`): one controlled methodological repair attempt after v1 = D (OC-CP4).

**Status: DRAFT — NOT FROZEN.**
- Every section is complete except §9: how the identification family (measurement error, latent factor) enters the classification. That needs an explicit owner decision before the run (owner D249 §7 and §10).
- The confirmatory driver `OC2_V2_run.py` refuses to start until `FROZEN.json` exists. That file records:
  - this file's SHA-256;
  - the code SHA-256 values;
  - the owner's §9 choice.
- The draft's hashes are recorded in `OC2_V2_draft_hashes.json`.
- Freezing changes only the status line and §9's "chosen option" line, plus writes `FROZEN.json`. Any other change to this text after the owner decision needs a new owner decision.

**Scope:**
- synthetic data only;
- no real F5 signal, return, price or Fama–MacBeth estimate;
- no QuantConnect run, no backtest, no Holdout, no purchase;
- no use of post-2021 data;
- v1 artifacts (`research/longhorizon/oc2/stage2/`) are preserved unchanged, and v1 stays **D — INSUFFICIENT EVIDENCE**.

**Evidence available before this draft:** engineering and structure statistics only (DEV seeds):
- the failure-mode audit `OC2_V2_audit.json` (v1 code reproduction + large-sample population algebra; no returns simulated);
- the engineering record `OC2_V2_engineering.json`.

No v2 scenario rejection rate, and no v2 power, was simulated. The §9 size projections are analytic: population bias × DEV slope scale, pushed through the fixed-b reference distribution.

## 1. Question

Does the proposed universe-wide Fama–MacBeth test of the frozen Data v3 F5 signal control false positives in realistic null worlds? And does it detect a +3% a year gross top-quintile effect over 2012-02 → 2021-11 (118 monthly reviews, Stage 1 population)?

A synthetic pass is not evidence that OC-2 is profitable. It would only permit asking the owner for one real-data test.

## 2. Inference method (one primary method, no model search)

**Each review t = 1…118:**
- **Sample:** stocks with a valid signal and all eight controls (complete case; controls missing at random in 5% of stock-months; MNAR selection in N11).
- **Response:** next-month total return minus the sample's equal-weight mean. Not winsorised: heavy tails are tested in N12 and through t(5) noise everywhere.
- **Signal:** centred cross-sectional rank (bounded; no winsorisation needed).
- **Controls:** size, beta, LOWVOL, MOM, BM, GPA, AG, ACC.
  - Each is converted to a cross-sectional normal score Φ⁻¹(rank) (bounded, outlier-robust).
  - Each then enters as a **restricted cubic spline**: Harrell's natural cubic spline with 5 fixed knots at the normal quantiles 0.05 / 0.275 / 0.5 / 0.725 / 0.95. That is 4 columns per control, linear beyond the outer knots.
  - Plus 11 FF12 sector dummies (financials excluded; one sector absorbed by the intercept).
  - Why splines: the audit (§B) shows that v1's linear-in-rank controls leave a functional-form leakage when premia are linear in the underlying characteristic (+0.044% a year population bias) or concentrated in the tails (+0.101%). With the spline, the population bias is zero to the third decimal for normal-linear, rank-linear and tail premia.
  - The specification is fixed here and is not chosen by any rejection rate.
- **Estimation:** OLS of the response on [signal rank | control splines | sector dummies | intercept]. b_t = the signal coefficient (Frisch–Waugh partial slope via QR).
- **Companion G2:** the same regression with the signal rank replaced by a top-quintile dummy. G2 = 12 × 0.8 × the mean dummy coefficient (top minus universe, per year).

**Primary statistic:** t = mean(b) / SE_NW7 (§3), one-sided.
- The nominal 1% level is the proposed real-test level; 5% is reported.

**Full decision rule (as v1, for the real test):** G1 (t > c₁%) ∧ G2 ≥ +3% a year ∧ G3 (positive mean slope in reviews 1–59 and 60–118) ∧ G4 (no calendar year supplies > 50% of the slope sum).

**Non-gating diagnostics:**
- v1-style rank controls (`t_rank_ctrl`);
- NW lag 4;
- iid SE;
- an **oracle** control set that adds the latent characteristic (N2L-oracle). The oracle is impossible in real data and is never used for classification.

## 3. Standard error and critical values

**Newey–West lag 7 with Bartlett weights**, fixed prospectively, as follows:
- Rule: the Andrews (1991) AR(1) plug-in L = 1.1447 (αT)^{1/3}, with α = 4ρ² / (1 − ρ²)², T = 118.
- It is evaluated at the most persistent slope dependence assumed for the real F5 test, ρ = 0.5.
- That gives L = 6.8 → 7.

Why ρ = 0.5:
- F5 refreshes quarterly and its ranks persist (signal AR 0.70–0.90);
- the payoff itself is assumed close to serially independent (ρ_g 0.10–0.30);
- a 3-month overlapping response has ρ₁ ≈ 0.67 but only MA(2) memory, which lag 7 covers.

**Critical values:** fixed-b one-sided quantiles of the NW(7) t, simulated once under iid Gaussian slopes with T = 118 (2,000,000 draws, seed 118007):

| level | fixed-b CV | normal |
|---|---|---|
| 5% | 1.7769 | 1.645 |
| 1% | 2.5904 | 2.326 |
| 0.5% | 2.9050 | |
| 0.1% | 3.5886 | |

The fixed-b limit is pivotal for any weakly dependent slope series, so the values do not depend on the scenario.

Alternative lags (4, iid) are reported, never gating.

For every world, the report separates three things:
- **SE calibration:** the ratio of the mean NW SE to the across-replication sd of mean(b);
- **bias:** the mean of mean(b), whose truth is 0 under every null;
- **identification:** the family membership in §9.

## 4. Synthetic DGP (`qresearch.oc2synth_v2`; population structure imported unchanged from the frozen v1 module)

**Unchanged from v1:**
- cross-section by year (447 → 1,019 valid stocks per review, Stage 1);
- FF12 sector mix;
- quarterly refresh phases 0.62 / 0.10 / 0.28;
- exits 2.4%, entries 2.9%;
- characteristic correlation matrix;
- F5–characteristic correlations (MOM 0.175, ACC −0.177, GPA 0.105, AG 0.078, BM −0.07, LOWVOL −0.05, latent growth 0.30);
- characteristic AR 0.95;
- signal AR 0.70;
- total cross-sectional return sd 6.5% a month;
- t(5) noise;
- LOWVOL heteroskedasticity 0.30.

**Repaired or added (each traced to the audit):**
1. **Signal payoff dependence (quiet-market repair, audit §D).** Returns include g_t × signal, where g_t is zero-mean AR(1) with ρ_g = 0.10 (0.30 in N9). Its stationary sd is fixed per IC regime so that the controls-adjusted monthly IC has sd **0.06 / 0.09 (central) / 0.12**: G_SD = 0.002546 / 0.004513 / 0.006310. These were calibrated once on the baseline structure with DEV seeds.
   - Verified on DEV seeds (48 replications each): partial IC sd 0.061 / 0.090 / 0.118; raw rank IC sd 0.071 / 0.092 / 0.116.
   - v1 had no such term (implied IC sd 0.03, sampling noise only).
   - The payoff is a property of the market, so smaller or missing cross-sections add sampling noise on top of it.
2. **Variance budget (N7 defect).** The systematic variance (sector + 8 factors + market + payoff) must be ≤ 60% of the 6.5% total, otherwise the world is refused. The v1 N7 parameters are refused (0.00590 > 0.00254). v2 N7 = sector 3.5%, factor 1.1% (57% systematic).
3. **Every slot trades every month, with stock-id tracking (N13 defect).** A stock leaving the universe keeps trading. An overlapping response accumulates only while the slot holds the same stock; on exit it stops accumulating, which is the delisting convention. No NaN can arise: tested at 40–1,019 stocks, churn 0–2.
4. **Missing controls** (5% MAR, complete case), **small cross-sections** (N14 / N14s) and **irregular filing timing** (N15: refresh month redrawn each quarter; 10% of stock-quarters skipped).

**Seeds:**
- sha256("OC2-V2|FINAL|<world>") + replication index. The confirmatory evaluation uses FINAL seeds only.
- Engineering used DEV and TEST tags only. Those seed streams are disjoint and never reused for classification.

## 5. Null scenarios (no planted signal) — owner D249 §7 list

| owner §7 item | v2 world | v1 id | change from the base |
|---|---|---|---|
| 1 pure null | N0i | N0i | iid characteristics and returns |
| 1 pure null | N0 | N0 | full structure, no premia |
| 2 market / size | N1m | new | size and beta priced (3% a year each) |
| 3 LOWVOL | N1 | N1 | LOWVOL priced |
| 4 growth / profitability | N3, N2 | N3, N2 | GPA priced; AG priced |
| 5 nonlinear | N4, N4r, N4q | N4, new, new | all 8 controls priced: normal-linear / linear in uniform rank / extreme deciles only |
| 6 noisy controls | N5a, N5b | N5a, N5b | controls observed with reliability 0.80 / 0.60 |
| 7 latent factor | N2L1, N2L, N2L5 | new, N2L, new | unobserved growth (corr with F5 0.30) priced at +1 / +3 / +5% a year |
| 8 time-varying premia | N6, N9 | N6, N9 | AR premia; signal AR 0.90 + payoff ρ_g 0.30 |
| 9 sector / market shocks | N7 | N7 | sector 3.5%, factor 1.1% (budget-safe) |
| 10 heavy tails | N12 | N12 | t(3), heteroskedasticity 0.60 |
| 11 quarterly refresh | N13 | N13 | 3-month overlapping response (refresh shares verified in every world) |
| 12 entrants / leavers / MNAR | N8a, N8b, N11 | N8a, N8b, N11 | churn 0 / 2×; MNAR missingness |
| 13 small / varying N | N14, N14s | new | cross-section × 0.5 / × 0.25 |
| 14 irregular timing | N15 | new | irregular refresh month, 10% skipped quarters |

- **Base:** N4 (every control priced at 3% a year) for items 5–14, as in v1.
- **IC regimes:** every world runs at the central regime (0.09). N0, N4, N4q, N12, N14, N5a and N2L also run at 0.06 and 0.12.
- **Identification family** (§9): N5a, N5b, N2L1, N2L, N2L5 and their regime copies.
- **Calibration family:** every other null world (30 worlds including regime copies).

## 6. Planted alternatives (power; 1,000 replications each)

- P2 / P3 / P4 / P5: a gross top-quintile effect of +2 / +3 / +4 / +5% a year on the N4 base, in each IC regime (0.06 / 0.09 / 0.12) — 12 cells.
- P3-c0, P3-c2: +3% with F5–control correlations × 0 / × 2 (correlation regimes).
- P3-fresh: +3% paid only on freshly refreshed signals (quarterly arrival).
- P3-n50: +3% with a half-size cross-section (sample-size dependence).

**Power** = rejection at the 1% fixed-b level (primary); 5% is diagnostic. Full-rule pass rates are reported too.

Note: at exactly +3% the full rule's own G2 floor (≥ +3%) caps full-rule power near 50%. As in v1, the classification uses t-test power.

**Reported:** power by regime, correlation regime, arrival, and N; MDE50 / MDE80 by linear interpolation over the effects (or "> 5%"); T_eff = T(1 − ρ₁)/(1 + ρ₁).

## 7. Replications and Monte Carlo precision

| world group | reps each | total |
|---|---|---|
| central nulls (25) | 4,000 | 100,000 |
| regime copies (14) | 2,000 | 28,000 |
| oracle diagnostic | 1,000 | 1,000 |
| power cells (16) | 1,000 | 16,000 |

Precision at true rejection rates of 5% and 1% (Wilson 95% intervals reported for every rate):

| reps | MC sd at 5% | MC sd at 1% |
|---|---|---|
| 4,000 | 0.34 points | 0.16 points |
| 2,000 | 0.49 points | 0.22 points |

- Planned runtime ≈ 145,000 × 0.42 s / 4 cores ≈ 4.2 h.
- Per-replication rows go to `data/oc2_v2_parts/` (gitignored; re-creatable from FINAL seeds).
- The summary goes to `OC2_V2_results.json`.

## 8. Criteria and classification (fixed now; precedence D > C > A / B)

**8.1 Required evidence (otherwise D — INSUFFICIENT EVIDENCE):**
- Every planned world completes, with computational failures ≤ 1% of its replications. Failures are recorded and counted as non-rejections in the primary rate; the rate over completed replications must also pass. They are never excluded.
- Generator adequacy in N0 and N4 at each regime:
  - partial IC sd within ±15% of the regime target;
  - refresh shares within ±0.05 of Stage 1 (0.625 / 0.097 / 0.270);
  - mean valid cross-section within ±3% of the Stage 1 mean × 0.95.
- In N4: F5–control correlations within ±0.03 of the targets.

**8.2 Size (calibration family; otherwise C — NOT VALIDATED):** in every calibration-family world, at every regime run, on both denominators:
- rejection at 1% ≤ 2.0%;
- rejection at 5% within [3.5%, 6.5%].

**8.3 Identification family:** governed by §9 (OWNER DECISION REQUIRED).

**8.4 Power (only if 8.1–8.3 pass):**
- **A — CALIBRATED AND SUFFICIENTLY POWERED** if power at +3%, central regime (P3-0.09), at 1% is ≥ 0.80;
- otherwise **B — CALIBRATED BUT UNDERPOWERED**.
- Low and high regimes are reported, not gating.

The classification is computed by one function (`OC2_V2_run.decide` → `oc2synth_v2.classify`), unit-tested against this text.

## 9. Identification family — OWNER DECISION REQUIRED before freezing

**Why the written v1-style criterion cannot coherently address these worlds (owner D249 §10):**
- In N5a / N5b the controls are measured with error. In N2L the return-relevant characteristic is unobserved and correlated with F5 at 0.30.
- No estimator that uses only the observed controls can remove the resulting bias. The bias is a property of the data, not of the test.
- The audit (population algebra, n = 400,000, spline controls) gives an apparent F5 effect of:

| world | apparent F5 effect (% a year) |
|---|---|
| N5a | +0.22 |
| N5b | +0.39 |
| N2L1 | +0.23 |
| N2L | +0.69 |
| N2L5 | +1.16 |
| oracle (adds the latent factor as a control) | 0.000 |

- Projected (analytic, not simulated) rejection rates of the primary 5% / 1% test against the strict gate [3.5%, 6.5%] / ≤ 2%:

| world | IC sd 0.06 | 0.09 | 0.12 |
|---|---|---|---|
| N5a | 11.0 / 2.7 | 8.5 / 2.0 | 7.5 / 1.7 |
| N5b | 19.0 / 5.6 | 12.9 / 3.3 | 10.4 / 2.5 |
| N2L1 | 11.6 / 2.9 | 8.9 / 2.1 | 7.7 / 1.7 |
| N2L | 38.7 / 15.8 | 23.1 / 7.4 | 16.9 / 4.8 |
| N2L5 | 73.3 / 45.0 | 44.8 / 19.7 | 31.0 / 11.4 |

- v1's own simulated N5a t-shift (+0.72 at IC sd 0.03), scaled to the v2 slope noise, gives +0.25 at the central regime. The analytic projection gives +0.29: they agree.
- Upper bounds on full-rule false promotion, from P(G2 ≥ +3%) alone:

| world | IC sd 0.06 | 0.09 | 0.12 |
|---|---|---|---|
| N5a | 0.0% | 0.03% | 0.5% |
| N2L | 0.0% | 0.2% | 1.6% |
| N2L5 | 0.1% | 1.2% | 4.4% |

**Options:**
- **Option 1 — strict (v1 parity).**
  - N5a, at every regime, is gated by the §8.2 size criterion; N5b and the N2L family are reported, non-gating (as v1).
  - Projected outcome: **C** (N5a 5% rejection 7.5–11% in every regime), whatever the calibration family shows.
- **Option 2 — identification gate on the decision rule (proposed before any v2 result).**
  - The §8.2 size criterion applies to the calibration family.
  - The identification family is gated by bounded false promotion of the full decision rule: in N5a and N2L (+3%, the v1 strength), at every regime, the full-rule pass rate is ≤ 2.0%.
  - The t-test rejection rates, the bias, and the dependence on latent-factor strength (N2L1 / N2L / N2L5) and reliability (N5a / N5b) are reported, non-gating.
  - **The scope of any later alpha claim is then limited, explicitly:** "incremental to the eight observed controls as measured; it cannot exclude premia on unobserved or mismeasured characteristics correlated with F5". Each +1% a year of latent premium at correlation 0.30 produces about +0.23% a year of apparent F5 effect.
  - Projected: the gate is probably met (upper bound N2L 1.6% at the high regime), so the outcome would be decided by the calibration family and power.
  - This weakens v1's treatment of N5a (gated by t-test size in v1) and must be judged as such.
- **Option 3 — stop.** No confirmatory run; OC-2 closes and SPY (OC-1) remains the offensive complement.

**Chosen option:** — (pending the owner).

The latent-factor worlds stay in the official evaluation under every option. None is removed.

## 10. Reporting (every world)

- n, failures (with reasons), and rejection at 5% / 1% / 0.5% / 0.1% on both denominators, with Wilson intervals;
- mean and sd of t;
- bias (mean of mean(b)); SE ratio;
- G2 mean (apparent top-quintile effect);
- full-rule pass rate;
- realised IC sd and partial IC sd; ρ₁; T_eff;
- cross-section size; refresh shares; F5–control correlations;
- the rank-control, NW4 and iid diagnostics;
- for the identification family: the false-signal magnitude against factor strength and reliability, and the oracle comparison.

## 11. Stopping rules

- One confirmatory evaluation (FINAL seeds), after the freeze.
- A technical rerun is allowed only for an infrastructure failure (process killed, disk full), using the same frozen code and seeds. It is never allowed for a statistical result.
- No v3, no change of controls, lag, gates or scenarios after any result.
- After OC-CP5 the programme STOPS for the owner, whatever the outcome.

## 12. Freeze procedure (after the owner's §9 decision)

1. Replace the status line with "FROZEN — owner decision D2xx" and fill §9's "Chosen option". No other text changes.
2. Write `FROZEN.json` with this file's SHA-256, the SHA-256 of `oc2synth_v2.py`, `oc2synth.py`, `OC2_V2_scenarios.py` and `OC2_V2_run.py`, and `ident_treatment` (1 or 2). Commit it, and pin the hashes in `tests/test_oc2synth_v2.py`.
3. Run `OC2_V2_run.py` once from the clean committed tree.
