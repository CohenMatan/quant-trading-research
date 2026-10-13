# P13-CP5 — H028 Conditional-Null Structural Audit

**Owner decision D238** (message recorded verbatim in `docs/owner/2026-10-13_p13cp5_h028_null_structural_audit.md`).

This is an audit of an already-rejected historical result. It is not a new hypothesis and not an attempt to rescue H028.

**Inputs:**
- synthetic panels only;
- the frozen H026 / H027 / H028 code, run unchanged;
- committed artifacts, structural fields only.

**Not done:**
- no QuantConnect run;
- no real H028 return, wealth, CAGR, SPY comparison, alpha or IC computed;
- no new or repaired null;
- Holdout sealed.

**Result: H028 NULL STRUCTURAL AUDIT — FAIL. The historical conditional-null significance is structurally suspect.**
**H028 FORMAL STATUS REMAINS REJECTED.**

---

## Owner questions (Q1–Q10)

| # | Question | Answer |
|---|---|---|
| Q1 | Does H028 use a donor mechanism vulnerable to universe-churn re-mapping? | **YES.** Section 9 gives the proof. The null is the same persistent pointer tether (`qr_p7_pred.Tether`, one stratum) that failed in H029 Null #2. It applies to the ten non-LOWVOL features. |
| Q2 | How often does donor re-mapping occur? | **About 17.6% of recipient-months**, i.e. about **84 of about 475 stocks per review**, on the real H026 / H028 population (committed E029-01 canary). That is about 3.3 times H029's rate. The calibrated synthetic panels have 17.4%. |
| Q3 | Does realistic churn make null portfolios trade more than an equivalent no-signal real portfolio? | **Yes, when the ranking process is held fixed.**<ul><li>Null name turnover is **+0.02 to +0.08 a month** higher (S2).</li><li>The no-signal real portfolio trades less than **every** null world in 7 of 10 panels with the committed H028 coefficients, and in 7 of 10 with the panel's own fitted coefficients.</li></ul>In the full refit pipeline the effect shows clearly in **score-rank persistence**: the null is less persistent in all 10 realistic panels, and outside the 99.5% band in 5 of them. The turnover gap there (median +0.044 moderate, −0.027 strong) is masked by world-to-world coefficient noise that the real H028 null does not have (Q5). |
| Q4 | Does keeping LOWVOL attached materially protect against the artifact? | **Only partly.** Rank instability is about 20% smaller than when all eleven features move. The turnover gap is not consistently smaller. Even a stylised score with 40% of its weight on LOWVOL still shows the full turnover gap (+0.01 to +0.07). |
| Q5 | Does Ridge refitting amplify or reduce it? | **Neither, systematically.** In no-signal panels each world fits different noise coefficients. This widens the null turnover band and hides the gap rather than removing it.<br>The committed real-data null worlds (seeds 1–25) have very **stable** refit coefficients (year-to-year cosine 0.94–0.98). So the frozen-coefficient diagnostics are the closer analogue of the real null's ranking layer. |
| Q6 | How much extra trading cost does the artifact create? | In the synthetic S2 panels with the committed H028 coefficients: **0.5–2.5% of final wealth**, a log-wealth shift of about **0.005–0.025** against null worlds. At H028's own scale this is roughly $2K–6K over 2015–2021. |
| Q7 | Does the effect disappear in the no-churn control? | **Yes.**<ul><li>S1 has no re-formations.</li><li>Every S1 criterion statistic is inside the null band in all 6 panels.</li><li>With frozen coefficients the S1 turnover gap is −0.007 to +0.010 and the rank gap is 0.000 ± 0.004.</li></ul> |
| Q8 | Is there a clear churn dose-response? | **Yes.** With frozen coefficients, from no churn → realistic → double churn:<ul><li>turnover gap about 0 → +0.02 to +0.08 → +0.05 to +0.11;</li><li>rank-persistence gap 0 → −0.06 → −0.12;</li><li>"real below every null world" in 0/6 → 4/6 → 6/6 panels.</li></ul> |
| Q9 | Can the historical p ≈ 0.0004 still be treated as reliable development evidence? | **No.** Under the pre-registered rule the null is structurally suspect, so B1's p ≈ 0.0004 should no longer be treated as reliable evidence of stock-selection alpha. No corrected p-value is computed. The size of the cost channel is reported in section 33 as information only. |
| Q10 | Does anything here change H028's formal REJECTED status? | **NO.** |

---

## 1. H028 permanent status

**ORIGINAL RESEARCH STATUS: H028 REJECTED** (P13-CP1, D220; B4 failed).

This audit cannot change that status. H028 was not reopened, refitted, re-run or modified. No H028b or H031 was created.

## 2. Objective-alignment status

**30-YEAR OBJECTIVE ALIGNMENT: PARTIALLY OBJECTIVE-ALIGNED** (P13-CP4, D225). Unchanged.

## 3. Audit motivation

H029 work (P14-CP4, P14-CP6a) showed a failure mode of persistent-donor nulls. Eligibility churn forces donor re-assignments, so a "real" vector changes owner. This adds score discontinuities and turnover in null worlds even with no signal.

H028's strongest statistical evidence was its conditional null: S_WEALTH 0.224, with 1 of 5,000 null worlds at or above it, p ≈ 0.0004. That null uses the same tether family.

## 4. Historical null specification

Sources:
- `research/phase13/H028_spec.md` section 4;
- `qr_h028.run_fixed_conditional` → `qr_h027.conditional_permuted` (unchanged since H027) → `qr_p7_pred.Tether` (a single-stratum subclass of `qr_h020_stats.ChartTether`).

Each world:
1. applies the null to all 131 reviews (2011-01 → 2021-11);
2. refits the Ridge model with λ = 100 for each outer year 2015–2021 on the null features of every month whose 63-session label has exited;
3. scores, picks the Top-15 (FF12 cap 3), rebalances monthly at $7 per order plus 10 bps slippage per side, and compares with SPY.

The pre-registration is `research/phase13/cp5/P13_CP5_audit.py`. It was committed in 1d7ff5c before any statistic was computed. Amendment 1 (b61b83e) was committed before any result was read.

## 5. Exact randomized features

The ten columns `OTHER`: MOM, GPA, ACC, BM, AG, REV1M, CBOP, HI52, CFP, EQA.
- They move **together as one row**: the donor's centred percentiles at the same review.
- The code check is "other_not_donor_row 0" in the committed canary.

## 6. Exact preserved features

The recipient keeps its own:
- LOWVOL (canary check "lowvol_changed 0");
- 63-session label, returns, prices, open / alive flags and corporate actions;
- FF12 sector, which drives the sector cap;
- universe membership;
- SPY.

**Missingness:** none can move. The population rule requires all 11 features to be finite (coverage 99.8–99.98%).

## 7. Donor-persistence mechanics

- At the first review, each recipient gets a random donor (one stratum, no self-matching).
- A pair r → d is **kept while both r and d are in the population** (`keep = {i: j ... if i != j and i in lab and j in lab and lab[i] == lab[j]}`; one stratum, so `lab` is constant).
- The committed canary confirms this: 153,249 possible continuations, 0 broken.

## 8. Donor-remapping mechanics

**Free recipients** each review are:
- new members (entries and re-entries);
- recipients whose donor has left.

**Free sources** are:
- new members;
- stocks whose own recipient has left.

The free recipients receive a random permutation of the free sources. Fixed points are removed by a swap, or a splice into a kept pair (at most one per review).

Sector and stratum changes cannot cause re-formation (single stratum). The donor's sector is not preserved.

**On the real population** (`research/phase13/cp5/P13_CP5_artifacts.json`, from the committed E029-01 canary, seeds 1–3 × 131 reviews):

| Item | Value |
|---|---|
| Recipient-months | 186,864 (≈ 186,062 after the first review) |
| Possible continuations | 153,249 |
| Retained | 153,249 (0 broken, 0 self-matches) |
| Re-formed | ≈ 32,813 = **17.6%** of recipient-months after the first review |
| Re-formed per review | ≈ **84** of a mean population of 475 |
| Causes | recipient entry or re-entry ≈ 44 per review; donor exit ≈ 40 per review (estimated: the canary counts the two together; split via net growth of +3.8 per review); sector changes 0 (not applicable); splices 0 |
| Recipient exit | Removes the recipient. Its donor's vector becomes a free source and is **handed to a new owner**: the transfer channel. |

**Synthetic panels:** the causes are separated exactly. In S2, per panel: about 5,850 new-recipient re-formations (9.5% of rows), about 4,900 donor-exit re-formations (7.9%), and 0 splices. In total 17.4%, or about 83 per review.

## 9. Comparison with the H029 mechanism

**YES — the same class of donor discontinuity exists.**

Proof from the frozen code:
1. **Pointer semantics.** H028's null gives each recipient its donor's *current* ten-feature row at every review, exactly as H029 Null #2 gave the six-signal row.
2. **Forced re-pairing.** A pair survives only while both stocks are in the population. Every exit of a donor forces its recipient onto a random new donor, so the ten-feature path jumps. Every exit of a recipient frees its donor's persistent path to a random new owner, which can bring a top-ranked vector into a different name. Neither event exists in the real data, where each stock keeps its own features.
3. **No mitigation in the construction.** There is no stratification. LOWVOL stays attached, but it is one feature of eleven, and its weight in the H028 score is 15% (L1 share of the committed coefficients).

**Differences in magnitude:**
- re-pairing rate about 17.6% a month versus about 5.3% for H029, i.e. 3.3 times more;
- partial anchoring by LOWVOL;
- a refitted Ridge layer.

The synthetic study measures these directly.

## 10. Synthetic design

Pre-registered in `P13_CP5_audit.py`.

**Panels** (no market data, no returns used for calibration):
- 131 monthly reviews (2011-01 → 2021-11).
- Population growing from 267 to 768 stocks, from committed coverage counts.
- Exit probability calibrated on ids only so that the frozen tether re-forms **17.4%** (target 17.6%), with p_exit 0.0875.
- Half of the entries are returning earlier members.
- 12 FF12 sectors with sector mean shifts.

**Features:**
- 11 latent features with a pre-registered correlation matrix (e.g. MOM–HI52 0.55, LOWVOL–HI52 −0.35, BM–CFP 0.45).
- Persistent paths in two regimes:
  - **moderate:** monthly ρ ≈ 0.78–0.95;
  - **strong:** ρ ≈ 0.88–0.99.
- REV1M has no persistence in either regime.
- The six fundamental features update only in each stock's staggered filing month.
- Features become centred percentiles through the frozen `qr_h026.feature_matrix`.

**Returns** have **no relation to any feature**: market factor × beta plus noise. The label is the next-three-month return's centred percentile, and label exit = review + 91 days.

**Pipeline:** every world runs the frozen `qr_h027.conditional_permuted` and the frozen `qr_h028.run_world_fixed` (λ = 100, Fitter label availability, Top-15, cap 3, costs). The "real" pipeline is the same code on the unpermuted features.

## 11–15. Scenarios

| Scenario | Churn | Ten OTHER features | Purpose |
|---|---|---|---|
| S1 no churn | none (475 fixed stocks) | as regime | baseline (pairs never re-form) |
| S2 realistic | calibrated (17.4% re-formed) | as regime | the audit scenario |
| S3 2× churn | doubled (32.5% re-formed) | as regime | dose-response |
| S4 LOWVOL-anchor | realistic | i.i.d. noise each month | LOWVOL persistent, ten features without paths |
| S5 persistent vectors | realistic | static | stress of donor continuity |

## 16–17. Panel and world counts

As pre-registered, unchanged:
- **S2:** 5 panel seeds × **200** null worlds per regime (2,000 worlds plus 10 real).
- **S1, S3, S4, S5:** 3 panel seeds × **100** worlds per regime (2,400 worlds).
- **Diagnostics:** 100 worlds per main panel.
- **Exploratory addendum:** 3 panels × 100 worlds.

Runtime: 38 minutes for the audit and about 12 minutes for the addendum. Nothing was reduced.

## 18–24. Results (full frozen pipeline, refit per world)

- **Gap** = null median − real.
- **Positions** = where the real value lies relative to the null [0.5%, 99.5%] band, per panel: i = inside, b = below, a = above.

| Scenario, regime | Re-formed | Name turnover real / null (gap median, range) | New names / review gap | Trades gap | Commission gap | Slippage gap | Total-cost gap | Top-15 survival gap | Rank autocorr real / null (gap) | Positions: turnover, cost, survival, rank |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 moderate | 0% | 0.50 / 0.48 (−0.011; −0.07..+0.07) | −0.17 | −28 | −$196 | +$1,212 | +$1,188 | +0.011 | 0.82 / 0.84 (+0.030) | iii iii iii iii |
| S1 strong | 0% | 0.29 / 0.36 (+0.063; −0.01..+0.07) | +0.95 | +156 | +$1,092 | +$863 | +$2,080 | −0.063 | 0.95 / 0.92 (−0.015) | iii iii iii iii |
| **S2 moderate** | 17.4% | 0.54 / 0.58 (**+0.044**; −0.05..+0.13) | +0.66 | +108 | +$756 | +$1,529 | +$2,257 | −0.044 | 0.84 / 0.77 (**−0.061**) | ibiii ibiii iaiii **iaaai** |
| **S2 strong** | 17.4% | 0.50 / 0.47 (−0.027; −0.13..+0.05) | −0.41 | −67 | −$469 | −$256 | +$262 | +0.027 | 0.87 / 0.84 (**−0.033**) | iiiii iiiii iiiii iaaii |
| S3 moderate | 32.5% | 0.56 / 0.66 (**+0.089**; +0.06..+0.12) | +1.34 | +219 | +$1,533 | +$2,101 | +$3,853 | −0.089 | 0.85 / 0.69 (**−0.149**) | iib iib iia aaa |
| S3 strong | 32.5% | 0.47 / 0.58 (**+0.111**; −0.17..+0.14) | +1.67 | +274 | +$1,918 | +$974 | +$3,374 | −0.111 | 0.93 / 0.76 (**−0.171**) | bib bii aia aia |
| S4 moderate | 17.3% | 0.96 / 0.96 (−0.006) | −0.09 | −14 | −$98 | +$4,039 | +$3,777 | +0.006 | 0.06 / 0.10 (−0.009) | iii iii iii iii |
| S4 strong | 17.3% | 0.96 / 0.96 (−0.002) | −0.04 | −6 | −$42 | +$1,932 | +$1,993 | +0.002 | 0.07 / 0.06 (−0.007) | iii iii iii iii |
| S5 moderate | 17.5% | 0.36 / 0.37 (+0.023) | +0.35 | +57 | +$399 | +$1,356 | +$1,758 | −0.023 | 0.94 / 0.89 (**−0.052**) | iii iii iii **aaa** |
| S5 strong | 17.4% | 0.26 / 0.27 (+0.033) | +0.49 | +81 | +$567 | +$1,206 | +$1,801 | −0.033 | 0.98 / 0.91 (**−0.070**) | bii bii aii **aaa** |

**Readings:**
- Score-change magnitude rises with churn: S2 gap +0.03 / +0.00, S3 +0.08 / +0.10. So does the rank change of held names: S2 +0.06 / +0.05, S3 +0.16 / +0.16, S1 about 0.
- Dollar costs are confounded by each path's wealth level, since no-signal paths differ by chance. Commissions and trade counts are the clean measure.
- **S4 control:** with no persistence in the ten features, the mechanism has nothing to break and every statistic is inside. This confirms the audit code itself does not create gaps.

## 25. Coefficient stability (B)

**Synthetic:**
- Year-to-year cosine of the seven λ = 100 vectors: real 0.89–0.96 versus null 0.92–0.95, about the same.
- LOWVOL L1 share: about 0.05–0.11 in both.
- In no-signal panels every world's coefficients are noise, which explains the wide null turnover bands of the refit pipeline.

**Committed real data** (`P13_CP5_artifacts.json`, structural fields only):

| | Real H028 | Null worlds 1–25 (median, range) |
|---|---|---|
| Year-to-year cosine | 0.90 | 0.96 (0.94–0.98) |
| LOWVOL L1 share | 0.155 | 0.31 (0.23–0.41) |
| L2 norm | 0.0125 | 0.0076 |
| LOWVOL coefficient negative | 7 of 7 years | 7 of 7 years |

The real null's refit layer is stable and LOWVOL-led, not noise. So the frozen-coefficient diagnostics (section 26) describe the real null's ranking layer more closely than the noisy synthetic refits.

## 26. Fixed-coefficient diagnostic (A → C → D without B)

Same S2 panels, 100 worlds, coefficients held fixed (no refit):

| Coefficients | Regime | Turnover gap per panel | Real below every null world | Turnover positions | Rank positions (gap) |
|---|---|---|---|---|---|
| Panel's own real fit | moderate | +0.032, +0.035, +0.035, +0.034, +0.024 | 4 / 5 | bbbbi | aaaaa (−0.055..−0.075) |
| Panel's own real fit | strong | +0.007, +0.016, +0.029, +0.042, +0.041 | 3 / 5 | iibbb | aaaaa (−0.067..−0.082) |
| **Committed real H028 coefficients** | moderate | +0.029, +0.029, +0.024, +0.035, +0.050 | 3 / 5 | biibb | aaaaa (−0.053..−0.059) |
| **Committed real H028 coefficients** | strong | +0.082, +0.046, +0.039, +0.067, +0.024 | 4 / 5 | bbbbi | aaaaa (−0.063..−0.069) |
| Stylised defensive (LOWVOL −1, others +0.15) | moderate | +0.033, +0.013, +0.041, +0.038, +0.023 | 1 / 5 | bibbi | aaaaa (−0.011..−0.017) |
| Stylised defensive (LOWVOL −1, others +0.15) | strong | +0.025, +0.022, +0.057, +0.025, +0.066 | 2 / 5 | iibib | aaaaa (−0.014..−0.018) |

Once the coefficient noise is removed, the artifact is unmistakable:
- null turnover is higher in **every** panel;
- the real value lies below every null world in 7 of 10 panels with the committed H028 coefficients (and 7 of 10 with each panel's own fit);
- Top-15 survival is lower by the same amounts.

## 27. LOWVOL anchoring diagnostic

The comparison case moves **all eleven** features from the donor (the frozen H026 `permuted`). It is a diagnostic only and never proposed as a null.

| Comparison | Rank gap | Turnover gap |
|---|---|---|
| Full refit pipeline: conditional null | −0.010..−0.128 (moderate); −0.014..−0.085 (strong) | turnover bands too wide in both cases to separate |
| Full refit pipeline: all eleven moved | −0.017..−0.134 (moderate); −0.020..−0.088 (strong) | turnover bands too wide in both cases to separate |
| Committed coefficients fixed (addendum): conditional null | −0.056..−0.059 (moderate); −0.063..−0.068 (strong) | +0.024..+0.029 (moderate); +0.039..+0.082 (strong) |
| Committed coefficients fixed (addendum): all eleven moved | −0.073..−0.074 (moderate); −0.079..−0.081 (strong) | +0.029..+0.039 (moderate); +0.035..+0.055 (strong) |

**Conclusion:** keeping LOWVOL attached removes about **20%** of the rank instability and does not reliably reduce the turnover gap. Even with 40% LOWVOL weight (the stylised vector), the turnover gap persists. The ten moving features change the top of the ranking whenever their path jumps.

## 28. Zero-cost diagnostic

Every S2 world was replayed with commission 0 and slippage 0 through the frozen `qr_h028.replay`. The order-count gap is **identical** to the trade-count gap in every panel. The structural difference lies in the rankings and holdings themselves; costs neither create nor remove it.

## 29. Churn dose-response

Committed H028 coefficients fixed, 3 panels × 100 worlds per cell (`P13_CP5_addendum.json`, exploratory, post-result):

| | No churn (S1) | Realistic (S2) | Double (S3) |
|---|---|---|---|
| Turnover gap, moderate | +0.003, +0.003, +0.010 | +0.029, +0.029, +0.024 | +0.050, +0.086, +0.055 |
| Turnover gap, strong | +0.008, −0.007, 0.000 | +0.082, +0.046, +0.039 | +0.080, +0.060, +0.108 |
| Real below every null world | 0 / 6 | 4 / 6 | 6 / 6 |
| Rank-autocorrelation gap | ≈ 0.000 | ≈ −0.06 | ≈ −0.12 |
| Held-name rank change gap | ≈ 0.00 | +0.05..+0.07 | +0.11..+0.13 |

The full refit pipeline shows the same ordering on rank persistence (S1 mixed around 0, S2 −0.03 / −0.06, S3 −0.15 / −0.17). No model was fitted to these numbers.

## 30. Mechanism decomposition (one mechanism at a time)

| Mechanism | Finding |
|---|---|
| **Eligibility churn → donor re-mapping (A: feature paths)** | **The cause.** With no churn the gap is zero. It grows with churn: about +0.03 to +0.06 turnover at realistic churn, about +0.08 at double. |
| Coefficient refitting (B) | Not a systematic amplifier. In no-signal panels it adds coefficient noise that widens the null band and masks the turnover gap. The real null's coefficients are stable (section 25), so this masking is not expected there. |
| Ranking effects (C) | Present everywhere churn is present: lower rank autocorrelation (−0.06 per month at realistic churn) and larger rank changes of held names (+0.05). |
| Sector-cap interaction | **Not material.** With the cap loosened to 15 (non-binding), the gaps are unchanged: moderate +0.020..+0.039, strong +0.047..+0.077. |
| Eligibility turnover itself | Already present in the real selection (exits are sold in both). The *extra* null turnover comes only from re-pairing and transfer. S4, where re-pairing changes nothing, shows no gap. |
| LOWVOL anchoring | About 20% less rank instability. No reliable reduction in turnover (section 27). |
| Costs (E) | A consequence, not a cause (section 28). |

**Cost amplification** (section 33 relates it to H028's numbers): with the committed coefficients, the extra null cost is 0.49–2.48% of final wealth in S2 panels (log-wealth shift 0.005–0.025).
- Cross-check at H028's own scale: 827 trades, value turnover 0.632 a month, about 4.9 new names a month. A +0.02 to +0.08 turnover gap means about 60–200 extra trades over 2015–2021, roughly $2K–6K of commission plus slippage, or 0.6–3% of final wealth.

## 31. Real committed structural fields available

| Field | Status |
|---|---|
| Real H028 trades | 827 (H027: 809) |
| Real H028 value turnover | 0.632 a month (H027: 0.619) |
| Real H028 commissions | $5,789 (= 827 × $7) |
| Real H028 coefficients | per year, committed (section 25) |
| Real H028 risk (vol, MaxDD, beta, down-capture) | committed (adequacy step 2) |
| Null worlds: turnover, trades, commissions, slippage, holdings | **NOT AVAILABLE FROM COMMITTED ARTIFACTS**. The 25 row fields are S_WEALTH, wealth, excess CAGR, MaxDD, vol, beta, up / down capture, years beating, 7 yearly returns, 7 λ and a coefficient digest. |
| Null worlds: coefficients | full vectors for seeds 1–25 (section 25) |
| Null worlds: risk distributions | committed summaries (P13_CP1_null.json) |

No null return column was read. The 5,000 worlds were not re-run.

## 32. Real-vs-null turnover

**NOT AVAILABLE FROM COMMITTED ARTIFACTS.** Real H028 turnover is known (0.632 value turnover, 827 trades), but no null world recorded turnover, trades or costs. So the real percentile cannot be given. Per owner section 27, the 5,000 worlds were not re-run to obtain it.

## 33. Historical p-value interpretation

**Classification: B — STRUCTURALLY SUSPECT.**

**Rule applied** (pre-registered; Amendment 1 committed before any result was read):

| Criterion | Result | Verdict |
|---|---|---|
| Score-rank persistence, moderate regime | Real lies above the null 99.5% band (the null is less persistent) in **3 of 5** S2 panel seeds: a same-direction failure in ≥ 3 of 5 | **directional failure** |
| Score-rank persistence, strong regime | 2 of 5 | — |
| Turnover, cost, survival | each inside in ≥ 4 of 5 seeds, in both regimes | pass |
| Strong-fail rule (real below every world in ≥ 9 of 10 panels) | turnover 1 of 10, cost 0 of 10 | not triggered |

**Amendment 1:** the first commit required a directional failure in *both* regimes. Under that wording the result would have been **C (INCONCLUSIVE)**. Before any result was read, I amended it to apply owner section 19 literally in each regime, because the first version weakened the owner's rule. Both criteria are stored in `P13_CP5_audit.json`.

**Labelling bug (in my audit script, not the frozen H028 null):** after the run, I found the `WORSE` direction map was inverted, so the rank failure was labelled "null_better" instead of "null_worse". Classification counts a same-side failure in either direction, so it is unaffected. The label was corrected and the JSON regenerated from the stored results.

**Consequence (owner section 31):** H028 remains REJECTED. Its historical B1 / p ≈ 0.0004 null-based significance should no longer be treated as reliable evidence of stock-selection alpha. No corrected p-value is computed, no replacement null is designed, and H028 is not re-run.

**Information only (not a correction):**
- The identified channel is mechanical: it lowers null worlds' structural persistence and raises their trading.
- Its direct cost effect estimated here (log-wealth 0.005–0.025) is small next to the committed gap between the real statistic (0.224) and the pinned threshold (0.0561).
- But the audit cannot bound every consequence of the distortion: it measured structure, not the null's full return distribution. The pre-registered rule therefore governs.

## 34. Economic vs statistical evidence

- **Economic backtest evidence, unchanged and still historical fact:** H028's development path (wealth, CAGR, MaxDD, volatility, SPY comparison), the 2015–2017 weakness, the B4 failure and the dependence on 2018 / 2020 (P13-CP1 to P13-CP4). The audit does not touch them.
- **Statistical null evidence, what changes:** how much confidence the conditional null gives that the path reflects stock-selection skill rather than a property of the test. The null was shown to be structurally biased against its own worlds under churn, so its p-value is no longer treated as reliable.

## 35. Bug status

**No implementation bug in the frozen H028 null.**
- `conditional_permuted` and `Tether` behave exactly as specified and documented: persistent pairs, re-formation only when a member is absent, no self-matching. The committed canary showed 0 broken possible continuations and 0 self-matches.
- The artifact is a **design property** of the pointer-tether family under churn, the same as H029 Null #2.
- The only defect found was the direction-label inversion in this audit's own script (section 33). It is corrected and does not affect the classification.

## 36. Holdout untouched

Holdout untouched: no data of any kind from 2022-01-01 → 2026-08-31 was accessed. There was no QuantConnect run and no market data.

## 37. No new H028 optimization

- No refit, no λ change, no feature change.
- No new, repaired or replacement null.
- No H028b or H031.
- H029 / H030 were not reopened.

## 38. Q1–Q10

See the top of this document.

## 39. Final audit classification

**H028 NULL STRUCTURAL AUDIT — FAIL**
**HISTORICAL CONDITIONAL-NULL SIGNIFICANCE IS STRUCTURALLY SUSPECT**

**H028 FORMAL STATUS REMAINS REJECTED.**

## 40. Exact next owner decision

1. **Accept P13-CP5 as recorded:** H028 remains REJECTED, and its conditional-null p-value is no longer reliable evidence. Then **close Phase 13 / the learned-score line (recommended)**. Nothing further is proposed for H028.
2. **Separate, still outstanding:** the P14-CP6a decision on H029 / H030 (close as NOT EVALUABLE recommended). This audit does not bear on it.
3. **Information for the programme (not a request):** every persistent pointer-tether null under a churning universe is exposed to this mechanism:
   - the portfolio-level nulls of H026 / H027 / H028;
   - H029 Null #2;
   - with a smaller expected effect, the IC-level nulls of H022–H024, which have no trading-cost channel.

   Any future pre-registration that uses an identity tether on a churning universe should include a no-signal synthetic structural check like this one *before* its null is run. This is a methodological note only; nothing is reopened.

**STOP.** Awaiting the owner.

## Files

- `docs/owner/2026-10-13_p13cp5_h028_null_structural_audit.md`: owner message (verbatim).
- `research/phase13/cp5/P13_CP5_audit.py` / `.json`: pre-registered synthetic audit (5 × 200 + 4 × 3 × 100 worlds per regime, diagnostics, criterion).
- `research/phase13/cp5/P13_CP5_artifacts.py` / `.json`: committed structural fields.
- `research/phase13/cp5/P13_CP5_addendum.py` / `.json`: exploratory post-result decomposition (non-gating).
- `tests/test_p13_cp5.py`.
