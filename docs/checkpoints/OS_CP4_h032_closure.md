# OS-CP4 — H032 closure: REJECTED — NOT PROMISING

- **Decision trail:**
  - D282: R1 approved.
  - D284: the R1 result (OS-CP3, `docs/checkpoints/OS_CP3_h032_r1_performance_E033.md`).
  - D285: the owner closes H032 (message verbatim in `docs/owner/2026-10-22_h032_closure_after_r1.md`).
- **Basis:** only the committed E033-01 evidence (`research/os/OS1_R_result_E033-01.json`, `research/os/E033-01_os1r_lines.txt`, `experiments/E033-01/`). **No new run, statistic search, backtest or data work.**
- **Status:**
  - **H032: REJECTED — NOT PROMISING** (exploratory evidence).
  - R2: not executed, correctly, under D282.
  - H031: parked.
  - H028: REJECTED.
  - RR6: INCONCLUSIVE.
  - Holdout: sealed.

## 1. Closure

**H032 is closed.**

**Preserved unchanged:**
- spec `research/os/H032_spec.md`;
- protocol `research/os/H032_R_protocol.md`;
- host S033 and the pinned modules;
- canary and R1 records, transactions, results and decisions.

**Not reopened:**
- H032 is never rerun or rescued: no filter removal, constraint change, ranking change, other N, start date or cost assumption.
- B0, the momentum diagnostic MOM and every control book are **not candidates**. Their observed returns came from the same exposed 2012–2021 sample and were never pre-registered as strategies.

## 2. Principal conclusions (owner D285 item 4)

| | H032 (LEAN) | SPY |
|---|---|---|
| CAGR, 2012-07-31 → 2021-12-31 | **11.84%** | 16.31% |
| Terminal wealth from $100,000 | $286,598 | $414,278 |
| Maximum drawdown | −44.0% | −33.7% |
| Upside / downside capture (monthly mean ratio) | **0.96 / 1.21** | 1 / 1 |
| Regression on SPY (monthly, NW lag 2) | **β 1.17**, α −0.49% a month (t −1.57) | — |

- **Controls:** H032 failed the fixed controls. It trailed the equal-weight pool (14.24%) and beat only 1 of 5 random books, 1 of 5 beta-matched books and 3 of 5 filtered-random books.
- **Subperiods:** it failed the second development subperiod, 2016–2021, by −40 log points against SPY. It was ahead only in 2012–2015.
- **Filters:** the OCF and revenue-growth filters did not improve the unfiltered share-reduction strategy in this sample: B1 11.84% vs B0 14.96%.
- **B0 also underperformed SPY:** 14.96% vs 16.31%.

## 3. Observed failure mechanisms (descriptive, not causal)

The figures below are already in OS-CP3. They decompose what happened. They do not prove why.

| Layer | Evidence | Reading |
|---|---|---|
| Pool vs benchmark | Equal-weight covered pool 14.24% vs SPY 16.31% (−2.1 points a year) | Before any selection, an equal-weight book drawn from this ≥ $2B non-financial pool started about 2 points a year behind the cap-weighted benchmark in 2012–2021 |
| Concentration drag | Random 15-stock books from the covered pool: median 12.72% (range 9.6–13.4%) vs equal-weight pool 14.24% | 15-name books with this turnover and these costs lost about 1.5 points more on average, and their spread is wide |
| Filters | Random books from the **filtered** pool (B2): median 11.32% vs covered-pool random median 12.72%. B0 (no filters) 14.96% vs B1 11.84% | In this sample the "cash-generating and growing" filters **lowered** returns rather than removing bad buybacks |
| Ranking | B1 11.84% vs filtered-random median 11.32% (beat 3 of 5) | Net share reduction added little, if anything, inside the filtered pool |
| Risk profile | β 1.17, downside capture 1.21, maximum drawdown −44.0% (March 2020); beta-matched books median 12.55% | The filtered buyback book was a **higher-risk** equity portfolio, not a quality / defensive one. It lost more in falls and did not make it up in rises |
| Sector clustering | Retail (FF12 Shops) held 37–43% of target slots in 2016–2017, the years the book fell behind; H032 has no sector cap | Holdings were concentrated in one industry when it lagged; with 15 names, industry bets dominate |
| Persistence | Behind SPY in every calendar year from 2014 except 2018; two-year blocks after 2013 all negative | A steady shortfall, not one episode |

**Ruled out as causes:**
- **Execution and accounting:** the shadow replay equals LEAN to the cent, with 0 timing or invalid-order issues.
- **Costs:** about 0.45% a year, around a tenth of the shortfall.
- **Data drift:** all 113 reviews are identical to the canary.
- **Universe repair:** restored securities contributed −$1,978 of +$186,598; the vendor-only book VB1 gave 12.01%.

## 4. Implications for offensive stock-selection research

1. **The benchmark sets a high bar in this window.**
   - In 2012–2021 the cap-weighted SPY beat an equal-weight pool of eligible large caps by about 2 points a year.
   - A concentrated equal-weight Top-N book also gave up about 1.5 points more to concentration, timing and costs.
   - A selection rule therefore needed roughly **3–4 points a year of genuine edge just to tie SPY.**
   - Power studies (LH-CP4, OC-CP2) show that edges of about 3% a year are barely detectable in this window. Even a real edge of that size could not be confirmed here.
2. **Plausible "quality" screens can raise risk.**
   - Positive cash flow plus growth plus buybacks selected higher-beta, sector-concentrated names.
   - A screen's risk profile (beta, down-capture, industry mix) has to be part of its design, not discovered after the run.
3. **The pattern repeats across the programme.**
   - Offensive stock selection on QuantConnect data has now failed or been unevaluable in every form tried:
     - profitability (H016);
     - earnings reaction (H017);
     - technical rules and momentum (H018, H019);
     - chart scores (H020);
     - multi-factor scores (H022–H024);
     - insider buying (H025);
     - learned scores (H026–H028);
     - business improvement (H029–H030, not evaluable);
     - ΔROA (OC-2, method not validated);
     - and now net share reduction (H032).
   - None beat SPY robustly on exposed 2010–2021 data. **SPY remains the offensive baseline** (OC-CP6).
4. **Do not mine the observed winners.**
   - MOM (19.55%) and B0 (14.96%) are observations on the same exposed sample. Momentum was already tested and failed as a signal (H019, top decile −2.18% a year).
   - Promoting either, or any variant of H032, would be selection on 2012–2021 outcomes, which the owner has ruled out.
5. **2010–2021 is spent as development data for selection.**
   - Every further look at it adds selection risk and no independent evidence.
   - Any next direction should be chosen on economic grounds before any data is examined. It needs a plausible edge clearly larger than the about 3–4 points a year benchmark-and-concentration hurdle, or a design that does not need to clear it (for example, one judged against an equal-weight reference by construction).
   - Its validation should not rely on this window alone. The Holdout is reserved for at most one candidate (D267).

## 5. Programme totals

- **Hypotheses:** 31 registered (H001–H030 and H032); H031 is a parked draft.
- **Strategies:** 88 strategy ids.
- **Experiments:** 588 logged in `experiments/INDEX.csv`, every failed, rejected and infrastructure run included.
- **Production candidates found:** none.

## 6. STOP

- H032 is closed as REJECTED — NOT PROMISING.
- Nothing else is started: no backtest, hypothesis, parameter change, infrastructure, purchase or data repair.
- The next research direction is a **separate owner decision**, on economic motivation.
