# C03 statistical specification (D082), frozen 2026-09-30

| Field | Value |
|---|---|
| Status | **FROZEN.** Approved by the owner on 2026-09-30 (D082), with Clarifications A and B written here before any C03 strategy backtest. |
| Implementation | `src/qresearch/c03stats.py` (the only implementation), plus `registry.trial_accounting` and `registry.dsr_trial_count`. |
| Tests | `tests/test_c03_stats.py`. `test_spec_is_frozen` fails if this file changes by a single byte (its SHA-256 is pinned in `c03stats.SPEC_SHA256`). |
| Scope | C03 only (H012, H013). C01/C02 conclusions and the rules they were judged under (D069, D073) are unchanged. |
| Data used to write it | None from C03, Validation or the Holdout. The hurdle figures come from `research/cycles/C03_dsr_hurdles.py/.json`, which uses only the pre-C03 registry. |

## 1. What is decided

1. **PBO is a diagnostic only for C03.**
   - It is calculated and reported for every C03 result (cycle level over the 6 candidates, and per hypothesis), with the same CSCV (16 blocks, at-or-below-median rule) and with its known limitations stated.
   - It never passes, fails, ranks or selects a candidate.
2. **The Deflated Sharpe Ratio (DSR) is the principal multiple-testing adjustment.**
   - Every qualifying book must have **DSR ≥ 0.90 at the official N and DSR ≥ 0.90 at the conservative N.**
   - A "book" is a portfolio that could actually be deployed: an H012 variation's run, or **one H013 seed's run**. Seeds are never averaged into a combined portfolio for any acceptance decision.
3. **H013:** each variation is **one** candidate in the official N. **Each of its three seeds must pass independently** the IS screen, robustness, Validation and both DSR requirements. No seed is chosen, dropped or replaced.
4. Every other rule is unchanged:
   - the IS screen (D036, including Sharpe ≥ 0.4 at 2× slippage);
   - the robustness criteria;
   - the Validation gates;
   - costs, universe and capital ($100K primary; $200K S1/S2 as pre-declared sensitivity only);
   - random-portfolio comparisons and H012's Controls A and B are diagnostics;
   - the budget cap of 82 QuantConnect backtests and the stopping rule;
   - no Validation outcome is used for any decision before Validation, and the Holdout stays locked.
5. **No discretionary exceptions.** Every outcome follows mechanically from the rules below.

## 2. Clarification A: the trial counts

### 2.1 Unit of counting

- The registry `experiments/INDEX.csv` (append-only) is the only source. Only rows with `run_type = original` are runs. Annotation and recovery rows are not runs (D077).
- A **configuration** is the tuple: hypothesis, strategy, version, parameters, split, start date, end date, cost-stress multiple (D066/D069).
  - Any change to a strategy's logic requires a new version. So a changed strategy is always a new configuration, never a "repeat".
  - In C03 no strategy may change after its first result.
- A configuration counts **once**, the first time a backtest of it **started**, whatever the outcome.
  - A failed run that started counts. It was an attempt.
  - A run annotated `not_started` (no backtest ever ran, e.g. "no spare nodes") does not count.

### 2.2 Categories

Every started research run falls into exactly one category.

| Category | Rule (in code: `registry.trial_category` + replicate grouping) | Official N | Conservative N |
|---|---|---|---|
| **S: selection candidate** | An IS configuration at base costs, not a robustness run. For a config with `replicate_param` (H013: `seed`), only the **first started** value of that parameter in its group. | **yes** | **yes** |
| **P: replicate** | Every further distinct seed of an H013 selection configuration (seeds 2 and 3 of each variation, whichever two started later). | no | **yes** |
| **R: robustness** | Any configuration with `robustness_of`, or with a cost-stress multiple ≠ 1. This includes the 2× slippage screen item, the 4×/6× cost runs and the plateau perturbations. **Each H013 seed counts separately.** | no | **yes** |
| **V: Validation** | Any research configuration whose split is not IS. **Each H013 seed counts separately.** | no | **yes** |
| T: technical repeat | A further run of a configuration already counted: operational retries, re-runs after an infrastructure fix, recoveries. | no | no |
| not_started | Annotated `not_started`. | no | no |
| X: not a strategy trial | `kind` ≠ research, i.e. canaries and audits (infrastructure), H012 Controls A and B (benchmark), random nulls X962 (infrastructure), capital sensitivity S1/S2 (sizing), 1999–2009 finalist stress (stress), and the pipeline demo. | no | no |

**Formulas (deterministic):**

- **official N = |S|**, cumulative over all cycles;
- **conservative N = |S| + |P| + |R| + |V|**, cumulative over all cycles.

**Why the X runs are excluded.** None of them is a strategy candidate or a variation of one:

- controls and nulls are fixed comparison portfolios defined before any result;
- canaries only test code;
- sizing re-runs a fixed rule at another capital and can never select or rescue a candidate.

This follows the table approved at CP3e §5.3 and CP3f §4.

### 2.3 How each item the owner listed is counted

| Item | Treatment |
|---|---|
| Robustness runs | **R**, each distinct configuration once. H012: at most 10 (4×/6× costs + 8 perturbations), plus its 2× slippage item. H013: each perturbation × each seed (at most 18), plus 2× slippage per seed. |
| Historical Validation runs | **V.** C01's E005-28 is the only one. It counts 1. H005 is never re-validated. |
| H013 extra seed runs | **P** (seeds 2 and 3 of each variation: 6 in total) at the IS selection stage. At the robustness and Validation stages every seed is its own R or V configuration. |
| Technical retries and verification runs | Neither count. A retry adds no new configuration. Canaries, audits, controls, nulls and sizing are not candidates. |
| Future conditional experiments | Counted **automatically** once registered, in the category their configuration defines. N can only rise. |

### 2.4 When the counts are taken

- The C03 DSR evaluation is run **once**, after every C03 Validation run the owner has authorised has finished (completed, or annotated failed or not_started).
- It uses the registry at the evaluation commit, and the same N applies to every C03 book.
- The output records:
  - the registry's SHA-256, row count and git commit;
  - N, with each of its components;
  - the Sharpe dispersion used.
- If any C03 research run is registered **after** that evaluation, the evaluation is repeated with the new counts, and the repeated result replaces it.
  - Because DSR falls as N rises, this can only turn a pass into a fail, never the reverse.
- The official N must be exactly **43** at the C03 evaluation (37 before C03, plus H012 v1.0–v1.2 and H013 v1.0–v1.2). Any other value stops the evaluation with an error, to be investigated and reported, never silently accepted (`expect_official=43`).

### 2.5 The numbers

| Moment | Official N | Conservative N |
|---|---|---|
| Before C03 (registry at this commit) | 37 | 64 = 37 S + 0 P + 26 R + 1 V |
| After the 12 committed selection runs | 43 | 76 = 43 S + 6 P + 26 R + 1 V |
| Upper bound, if every conditional run happens | 43 | 120 = 76 + 12 (2× slippage) + 28 (robustness battery) + 4 (Validation: H012 once, H013 × 3 seeds) |

**Correction to CP3f.** CP3f §2 quoted "at most about 104". That figure omitted the conditional 2× slippage items and the Validation runs. **The correct upper bound is 120.**

### 2.6 Sharpe dispersion (the other DSR input)

- **V[SR]** = the sample variance (ddof = 1) of the daily Sharpe ratio (registry `sharpe` ÷ √252) over every selection candidate's latest valid IS run (latest started run not retired by an annotation), cumulative over all cycles.
- For an H013 candidate, the value is the **mean of its seeds' daily Sharpes**. This is only an estimate of how much skill-less variations spread; it is never an acceptance statistic.
- The same V[SR] is used for both counts. Before C03 it is **0.0010013** (37 values).

## 3. Clarification B: how the DSR is calculated

| Item | Frozen choice |
|---|---|
| Return series | Daily simple returns of the book's **net** equity curve: after the $7 commissions and 10 bps slippage, and with cash at 0%. This is the daily "QR equity" series the harness records at each close, returns = equity(t) / equity(t−1) − 1. |
| Sampling frequency | Daily: one return per trading session. No annualisation inside the formula. |
| Sample | The IS run (2010-01-04 → 2017-12-29) followed by the VAL run (2018 → 2021-12-31) of the same frozen book. The two are separate backtests, each starting from $100K cash. They are concatenated, and **no return is computed across the gap**. There is no overlap: the VAL curve must start after the IS curve ends, or the evaluation stops. |
| Observations | n = (IS points − 1) + (VAL points − 1), about 3,020. Any non-finite return stops the evaluation. |
| Sharpe | SR = mean(r) / std(r, ddof = 1), per day. |
| Volatility | std(r, ddof = 1), inside SR only. |
| Skewness | pandas `Series.skew()` (adjusted Fisher–Pearson, bias-corrected). |
| Kurtosis | pandas `Series.kurt()` (excess, bias-corrected) + 3, so a normal distribution gives 3. |
| Trial count | SR* = √V[SR] · [(1 − γ) Φ⁻¹(1 − 1/N) + γ Φ⁻¹(1 − 1/(N·e))], with γ = 0.5772 (Euler's constant), which is the expected best daily Sharpe of N skill-less tries. It is computed twice: once with the official N, once with the conservative N. |
| DSR | DSR = Φ[ (SR − SR*) · √(n − 1) / √(1 − skew·SR + (kurt − 1)/4 · SR²) ]. If the denominator is not positive, or SR is undefined, DSR is NaN. |
| Threshold | **Pass only if DSR ≥ 0.90 at the official N AND DSR ≥ 0.90 at the conservative N.** Compared unrounded, with 0.90 itself passing. NaN fails. Each H013 seed must pass on its own series. |

**Hurdles implied (normal returns, current dispersion).** A book needs an observed annual Sharpe over IS + VAL of about:

- **1.48** at N = 43;
- **1.59** at N = 76;
- **1.67** at N = 120.

For comparison, the expected best skill-less Sharpe is 1.11, 1.22 and 1.30 respectively.

### 3.1 IS 2010–2017 and VAL 2018–2021

- **The DSR gate uses IS + VAL combined.** This is the rule approved in D036 and applied to C01, and it is not changed. The IS-only DSR and the VAL-only PSR/DSR are **reported as diagnostics and never gate**.
- **Why combined.**
  - The DSR is a statement about the book's whole track record after accounting for how many candidates were tried. Using all 12 years maximises the statistic's power (n ≈ 3,020).
  - A VAL-only DSR (n ≈ 1,008) would need an annual VAL Sharpe of about **1.76 to 1.94**. It would reject almost any real edge of the size this project can plausibly find, and adding it now would be a new threshold, which the owner excluded.
- **Can a strong IS hide a weak VAL? Partly, and this is bounded by the unchanged Validation gates.**
  - The combined series is about two-thirds IS, so a strong IS lifts the combined Sharpe.
  - But the VAL gates must pass **independently**:
    - VAL Sharpe ≥ 0.40;
    - VAL Sharpe ≥ 0.5 × IS Sharpe;
    - VAL Sharpe above the equal-weight benchmark's VAL Sharpe;
    - max drawdown ≥ −35%;
    - ≥ 50 trades;
    - the 2020 episode check.
  - With the "≥ 0.5 × IS" gate, the weakest VAL that can coexist with a passing combined DSR is a VAL Sharpe of about **0.89** (N = 43), **0.96** (N = 76) or **1.00** (N = 120), paired with an IS Sharpe of about 1.78 to 2.01. That assumes equal volatility in both periods (`C03_dsr_hurdles.json`).
  - **Remaining limitation:** in that edge case the combined DSR "borrows" strength from IS. The VAL decay protection then rests on the Validation gates, not on the DSR. This is stated in every C03 Validation report next to the VAL-only diagnostic.
- **Validation remains genuinely out of sample.**
  1. Before any VAL run, the chosen variation (H013: with its three seeds) is frozen by a promotion record: code and parameter hashes (D042). A VAL run is refused unless the files match exactly.
  2. One VAL run per book, and only after separate owner approval.
  3. VAL results can only accept or reject. They are never used to select a variation, tune anything, re-weight seeds or change this methodology.
  4. This specification is frozen before any C03 result, and its hash is pinned by a test.

## 4. H013: three seeds

- **Fixed before execution:**
  - seeds 1, 2 and 3;
  - pairing with the null runs E962-22, E962-23 and E962-24 (same seed, same session, same eligible set, same random order);
  - the rule that the portfolio walks the null's own random order and skips excluded names.
- **Every stage is per seed:**
  - IS screen;
  - 2× slippage item;
  - robustness (each perturbation run per seed);
  - Validation gates;
  - DSR at both counts.

  A variation goes forward only if all three seeds pass that stage. Failing one seed fails the variation.
- **No averaging for acceptance; no favourable seed.**
  - The choice between variations uses the mean of the three seeds' IS Sharpes (CP3f §2). That is a ranking among variations that have already passed with every seed; it is not an acceptance test.
  - The seed-averaged series is used only for the diagnostic PBO. It is labelled as such.
- **Correlated seeds: limitations.**
  - The three seeds share the universe, the market, the costs and most holdings over time. Their daily returns correlate about **0.86** (measured on the X962 nulls).
  - Three seeds at ρ = 0.86 carry the information of about **1.1** independent portfolios (n_eff = 3 / (1 + 2 × 0.86)).
  - **So "all three pass" is not three independent confirmations.** It mainly protects against a result that depends on one lucky random draw: the seed-specific part of the returns, about 14% of their variance.
  - Correlation makes the all-three rule less restrictive than it would be for independent seeds. It is still never less strict than judging one seed alone.
  - Counting seeds 2 and 3 as replicates in the conservative N treats them as extra tries, which overstates the number of independent attempts and errs strict.
  - The seeds do **not** diversify away market risk shared by all three. The market and period risks are addressed by Validation (and later the walk-forward and holdout stages), not by the seeds.

## 5. What each C03 report will show

For every book and stage:

- the per-seed tables;
- screen and robustness items;
- the controls and paired nulls;
- S1/S2 sensitivity (labelled diagnostic);
- the diagnostic PBO with its limitations;
- after Validation, the DSR block. It contains:
  - n, SR, skew and kurtosis;
  - SR* and the DSR at each N;
  - pass or fail at each N;
  - the IS-only and VAL-only diagnostics;
  - the registry SHA-256 and commit;
  - the N components;
  - V[SR].
