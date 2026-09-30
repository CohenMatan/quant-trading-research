# C03 statistical evaluation methodology: proposal for final approval

| Field | Value |
|---|---|
| Date | 2026-09-30 |
| Status | **STOP. Awaiting owner approval.** No C03 strategy backtest has run. No Validation, Walk-Forward or Holdout data is used. |
| Evidence | `research/cycles/C03_method_sim.py` → `C03_method_sim.json`: a simulation of the **whole** C03 decision pipeline, 9 scenarios × 1,000 repetitions, fully synthetic and calibrated to in-sample (IS) statistics only. Also `C03_pbo_analysis.py/.json` (previous checkpoint). |
| Unchanged | D036 screen and robustness criteria; Validation gates; costs; universe; DSR threshold 0.90; the D069 trial-count definition; all C01/C02 conclusions (D073 stays the rule under which C02 was judged). |

## 1. Recommendation in one paragraph

- **For C03, PBO becomes a fully reported diagnostic, not a hard gate.**
- **The Deflated Sharpe Ratio (DSR) becomes the principal multiple-testing test.** It must reach at least 0.90 at **both** the official and the conservative trial count, on **every deployable portfolio**; for H013 that means each seed separately.
- Every other screen, robustness and Validation requirement stays unchanged.
- Everything is mechanical: **no discretionary exceptions**.

The simulation shows why:

- With two correlated hypotheses, PBO protects against overfitting **only by accident** (when the two hypotheses happen to look alike). It gives **no** protection when one hypothesis has a spurious edge.
- It rejects most genuinely good pairs.
- The dual-count DSR lowers false acceptance in the cases PBO misses, at the price of lower power for a single moderate edge.

## 2. The proposed procedure (to be frozen before the first C03 result)

1. **IS screen (unchanged D036, $100K runs), including Sharpe ≥ 0.4 at 2× slippage.**
   - **H012:** each variation is judged on its own run.
   - **H013:** a variation passes only if **each of seeds 1, 2 and 3** passes every item.
2. **Choice of variation, per hypothesis, mechanical.** The passing variation with the highest IS Sharpe goes forward (H013: the highest mean of its three seed Sharpes). Ties go to the lower version number.
   - H012 and H013 **never compete**: each hypothesis is judged separately, and both may go forward.
   - Their joint multiplicity is covered by counting all 6 candidates in N (step 5).
3. **Robustness (unchanged criteria, pre-declared perturbations; H013 applies them per seed):**
   - plateau: ≥ 80% of perturbations keep Sharpe ≥ 70% of the base (H012: at least 7 of 8; H013: 4 of 4 per seed);
   - Sharpe > 0 at 4× costs;
   - every third of IS positive.
4. **Validation** (only after separate owner approval; unchanged gates):
   - VAL Sharpe ≥ 0.40 and ≥ 50% of IS Sharpe;
   - above the equal-weight benchmark;
   - max drawdown ≥ −35%;
   - ≥ 50 trades;
   - the 2020 episode check.
   - H013: **all three seeds** must pass.
5. **Deflated Sharpe on IS + VAL, ≥ 0.90 at both counts,** for each deployable portfolio: the H012 variation, or each H013 seed.
   - **Official N** = cumulative distinct selection candidates (D069) = 37 + 6 = **43**. Each H013 variation counts once.
   - **Conservative N** = selection + robustness + Validation configurations + the H013 replicate seed runs (seeds 2 and 3 of each variation), counted from the registry at evaluation time.
     - Before C03 it is 64. After the committed runs it is 64 + 6 + 6 = 76. With robustness it rises to at most about 104.
   - **Sharpe dispersion** (the other DSR input) is unchanged (D069): the spread of daily Sharpe across the latest valid run of each selection candidate. An H013 candidate's value is the mean of its seed Sharpes.
6. **PBO: reported, diagnostic only.**
   - The cycle-level CSCV over the 6 candidates (H013 as seed-averaged series) and the per-hypothesis values, with the same 16 blocks and median rule.
   - Shown next to every C03 result, with the known limitations stated. **It can neither pass nor fail a candidate.**
7. **The random-portfolio comparison (matched null) and H012's Controls A and B are reported.** They are diagnostics, not gates.

**What the DSR requires in practice.**

- With the current Sharpe dispersion, a portfolio needs an **observed annual Sharpe over IS + VAL (12 years) of about 1.48** to pass at N = 43.
- At the conservative count it needs about **1.59** (N = 76) to **1.65** (N = 104).
- For comparison, the equal-weight benchmark's IS Sharpe is 0.92.

## 3. Evidence (simulation of the full pipeline)

**Setup:**

- Synthetic daily returns: IS 2,012 days plus a Validation-length period of 1,008 days.
- Equal-weight benchmark: Sharpe 0.92, volatility 15.5%.
- Correlations:
  - candidates correlate 0.90 with the benchmark;
  - H012 variations 0.95 with each other;
  - H013 seeds of one variation 0.86 (as measured on the X962 random portfolios);
  - H013 variations within a seed 0.95.
- The screen is modelled on its Sharpe and drawdown items only. Trade-level items are omitted, which **overstates** pass rates, so these false-acceptance figures err on the high side.

**Frameworks compared:**

- **F0** = the current rule (DSR at the official count + PBO gate);
- **F1** = proposed (PBO diagnostic, DSR at both counts);
- **F2** = PBO diagnostic, DSR at the official count only;
- **F3** = no multiple-testing adjustment.

Figures are the probability that **at least one** hypothesis is accepted:

| True situation (annual Sharpe) | F0 | **F1** | F2 | F3 |
|---|---|---|---|---|
| **Ineffective strategies (false acceptance)** | | | | |
| No skill, our structure (0.75) | 0.0% | **0.0%** | 0.1% | 0.8% |
| No alpha vs benchmark (0.92) | 0.4% | **0.2%** | 0.7% | 8.7% |
| Barely meets the bar (1.02) | 0.5% | 1.1% | 2.2% | 24.1% |
| Edge in IS only (1.3 → 0.92 in VAL), **both** hypotheses | 2.6% | 4.9% | 8.7% | 35.9% |
| Edge in IS only, **one** hypothesis (the other has no skill) | **7.5%** | **3.5%** | 7.5% | 29.9% |
| **Genuinely better strategies (power)** | | | | |
| One hypothesis at 1.3 | 24.2% | 12.9% | 24.5% | 68.5% |
| Both at 1.3 | 7.9% | 12.8% | 26.5% | 78.2% |
| Both at 1.6 | 20.0% | 53.3% | 68.3% | 91.5% |
| One at 2.0 | 93.1% | 88.4% | 93.1% | 95.5% |

**What the evidence shows:**

1. **PBO does not detect overfitting here.**
   - When only one hypothesis has a spurious in-sample edge, PBO passes it 98% of the time. F0 then accepts it exactly as often as having no PBO at all (7.5% vs 7.5%).
   - PBO's apparent protection in the "both hypotheses" row comes from the same artefact identified earlier: two similar hypotheses fail PBO regardless of skill.
2. **PBO as a gate removes most of the power when both ideas are good.** Both at 1.6: 20% with the gate, 53% without.
3. **The conservative-count DSR adds real protection.**
   - Versus F2 it lowers false acceptance in every "ineffective" row, e.g. the one-hypothesis spurious edge from 7.5% to 3.5%.
   - It costs power for a single moderate edge (24% → 13%).
   - That is a deliberate tightening, not a loosening.
4. **Neither F1 nor F0 dominates on every row.**
   - F1 is better where F0's protection is illusory (the one-hypothesis spurious edge) and where two good ideas compete.
   - F0 looks better only in the rows where its protection comes from the artefact, or where one moderate idea stands alone.
   - F1's worst false-acceptance case is 4.9%, against F0's 7.5%.
5. **No framework makes C03 easy to pass.** A genuine but moderate edge (Sharpe 1.3) is usually rejected under both F0 and F1. That strictness is the approved standard; it is not changed.

## 4. H013's three seeds and trial accounting

- **Fixed now:**
  - seeds 1, 2 and 3;
  - the paired sampling procedure (the null's own random order, skipping excluded names);
  - the all-three-seeds rule at every stage (screen, robustness, Validation, DSR).
- No seed can be chosen or dropped: every seed is evaluated and reported individually.
- **DSR:**
  - each H013 variation is **one** candidate in the official N, because no choice between seeds is ever made;
  - its seeds 2 and 3 are **replicates**, counted in the conservative N;
  - the DSR must pass on **each seed's own series**. The seed average is a roughly 45-stock portfolio nobody would trade, so using it would overstate the deployable result.
- **PBO (diagnostic only):** H013 enters as the seed-averaged series; this is stated in every report.
- **Why H012 and H013 differ:** H012's variations are deterministic, so one run is one deployable portfolio. H013's deployable portfolio depends on the seed, so "robust" must mean robust across seeds. Requiring all three seeds at every stage is stricter than judging one averaged series.
- **Categories (unchanged principle, D069):**

  | Category | In official N? | In conservative N? |
  |---|---|---|
  | Selection candidates | yes | yes |
  | H013 replicate seeds | no | yes |
  | Robustness runs | no | yes |
  | Validation runs | no | yes |
  | Capital sensitivity (`sizing`) | no | no (own category) |
  | Controls and random nulls | no | no (benchmarks and diagnostics) |
  | Canaries, technical retries and recoveries | no | no (verification and technical) |

## 5. Limitations and remaining statistical risks

- **Worst case:** about 5% of the time, an edge that exists in IS but fades to benchmark level in Validation could still be accepted. These are the "IS-only edge" rows: 3.5–4.9% under F1.
- **Model simplifications:**
  - returns are normal (real returns have fatter tails);
  - the screen and Validation gates are only partly modelled;
  - the correlations are assumed;
  - the Sharpe dispersion is frozen from C01/C02 and may not match C03's candidates.
  - The first two points mostly make the real process **stricter** than simulated. The dispersion assumption can go either way.
- **Low power by design:** a real edge of Sharpe 1.3 is accepted only about 13–18% of the time. C03 may end with "No Production Candidate Found" even if one idea has a genuine but modest edge. That is the cost of 43 cumulative trials.
- **DSR acts only at Validation.** Before Validation, protection rests on the screen and robustness (the F3 columns show they alone let through many in-sample-only edges). Validation itself therefore remains essential, and requires separate approval.
- **Short samples:** IS 2010–2017 is a single, mostly calm bull regime, and Validation covers only 4 years. H012 in particular has few volatility episodes to learn from.
- **Correlated variations:** DSR treats them as independent tries, which errs strict.

## 6. Decision requested

**Approve, and freeze before the first C03 result** (proposed D082):

1. PBO is a diagnostic only for C03 (cycle-level and per-hypothesis; reported, never a gate).
2. DSR ≥ 0.90 at **both** the official N (43) and the conservative N (counted at evaluation time), on each deployable portfolio (H013: each seed).
3. H013: all three fixed seeds must pass every stage. Each variation counts once in the official N; its replicate seeds are in the conservative N.
4. The mechanical choice of variation per hypothesis, with H012 and H013 judged independently.
5. No discretionary exceptions, and no threshold changes.

**The alternative** is to keep F0 (the PBO gate plus official-count DSR). It is not recommended, because its extra protection is shown to be an artefact and it rejects most pairs of genuinely good hypotheses.

After approval: build the infrastructure, run the tests and canaries, and write and commit the C03 evaluation script implementing exactly this procedure. Then **stop** for authorisation of the strategy backtests.
