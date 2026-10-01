# Phase 2: H015 pre-registration proposal (P2-CP2): diversified low-turnover trend portfolio

- **Date:** 2026-10-01.
- **Status: PROPOSAL ONLY.** Nothing implemented, no H015 or control backtest run, the Holdout untouched. **STOP:** awaiting owner approval.
- **Budget:** H015 would be Phase 2 hypothesis **2 of 3**. H014 is closed as Rejected (D101).
- **Supporting files:**
  - `research/hypotheses/H015.md`;
  - `research/phase2/H015_literature_review.md`;
  - `research/phase2/P2_h015_feasibility.py/.json`. This reads only already-observed 2010–2021 outputs; no new backtest.

## The most important point first

**The closest version of H015 has, in effect, already been observed on the development data, and it fell short.**

- H014's random-uptrend controls held 12 random uptrend stocks and sold on Close < MA200.
- Their Sharpe exceeded equal-weight by **−0.12, +0.20 and −0.07** (MA200 exit with roll) and **+0.01, +0.04 and +0.12** (126-session cap).
- The median is about +0.03, far below the **+0.25** margin.

H015 differs in ways that come from the literature, not from those results:
- a monthly review;
- a single trend condition;
- 15 slots;
- no time stop.

Those differences are second-order, though. My honest expectation is that H015 will be **profitable and roughly EW-like, and will not be development-qualified.**

**What H015 can still deliver**, which no H014 run measured:
- a clean answer to **"does the trend filter itself add value?"** It compares the same portfolio with and without the filter, and the whole trend-filtered universe against the whole universe;
- a fully pre-registered, low-cost design.

**Whether that is worth Phase 2 slot 2 is your decision (§17).**

## 1. Precise hypothesis

Among US common stocks with point-in-time market cap ≥ $2B, take an equal-slot portfolio of 15 stocks with these rules:
- stocks are drawn only from those whose price is above their 200-day average at a monthly review;
- each is held until a monthly review finds it at or below that average.

Over 2010–2021, net of $7 per order and 10 bps slippage, this portfolio has:
- (a) a Sharpe ratio at least 0.25 above the equal-weight eligible universe and 0.10 above SPY, under the full approved G1;
- (b) a higher Sharpe ratio than the same portfolio built without the trend filter.

**The economic mechanism:**
- intermediate-horizon momentum in its simplest binary form: stocks above their long average keep up with or beat the market for months;
- a trend-failure exit that avoids part of the losses of stocks in sustained decline.

## 2. External research (details in `research/phase2/H015_literature_review.md`)

**For it (pre-2010):**
- 200-day MA rules on the Dow (Brock, Lakonishok & LeBaron 1992).
- 200-day MA timing reduces drawdowns at similar returns (Siegel 1994+).
- A monthly 10-month SMA rule keeps equity-like returns with much smaller drawdowns, mainly by avoiding long bear markets (Faber 2007).
- Intermediate-horizon momentum and trend consistency in stocks (Jegadeesh & Titman 1993; Grinblatt & Moskowitz 2004).
- 1/N weighting is hard to beat (DeMiguel, Garlappi & Uppal 2009).

**Against, or limiting:**
- Technical-rule profits disappear after data-snooping correction post-1986 (Sullivan, Timmermann & White 1999).
- Weakening in later samples (Park & Irwin 2007).
- MA timing works mainly in high-volatility (small) stocks, not large low-volatility ones (Han, Yang & Zhou 2013).
- Post-2010 critiques: gains are concentrated in long bear markets and much smaller out of sample (Zakamulin; Bajgrowicz & Scaillet 2012; Hurst, Ooi & Pedersen 2017). These are caution only.

**A structural point (§2 of the review).**
- The best evidence is **index-level timing** (moving to cash).
- A 15-slot stock-level rule in a universe where roughly 700 or more of ≈ 1,100 eligible stocks are above their 200-day average almost never holds cash.
- So H015 is mainly a **cross-sectional selection plus trend-failure exit**, for which the external evidence is thinner and points to a **small** effect.

## 3. Exact trend rule

- A stock qualifies at a review if its adjusted **Close > SMA200**: the simple mean of its last 200 adjusted closes, including the review close.
- **One condition only.**
  - The 200-day window has the longest documented history (Brock et al.; Siegel; Faber's 10-month equivalent).
  - The MA50 > MA200 "golden cross" state is a convention with no separate evidence, and it adds a parameter.
- **No other MA lengths are tested as candidates.** 150 and 250 appear only as pre-declared robustness perturbations (§12).

## 4. Exact stock-selection rule

At each review, free slots are filled from qualifying, not-held stocks in a **seeded random order**. This is X962's `pick_order(ids, seed, review)`, already in the codebase and tested.
- Seeds 1–5 are **replicates of the one candidate**, not candidates (the D082 precedent).
- Every seed is reported. No seed is ever chosen.

**Why random:**
- The hypothesis is about the **trend population**, not a ranking. A random draw is the only factor-neutral way to sample 15 names from about 700.

| Alternative | Why not |
|---|---|
| 12-1 momentum ranking | Not the hypothesis. Already used in H014; your caution applies. |
| Largest market cap | Tilts away from the EW benchmark toward large caps. We **already know** from our own benchmarks (SPY Sharpe 0.91 vs EW 0.80 over 2010–2021) that this tilt helped in this period, so it would load on an observed outcome. |
| Hold every qualifying stock | About 700 names at $100K is impossible with the $5,000 minimum. It is used instead as the population control K2 (§9). |
| Distance above the average | A trend-strength ranking is a form of momentum ranking, with the same objections. |

**Real-world implementation.**
- Each month, draw the fill order from a pre-committed pseudo-random sequence: a published seed plus the date, as in the code.
- That is fully investable at $100K. Any investor can reproduce it, and it carries no factor tilt.
- An investor with more capital simply holds more names, moving toward the population result.
- The **seed-averaged result** estimates what such an investor should expect. Any single seed is one realisation of it, with about ±0.12 Sharpe of luck (§11).

## 5. Exact exit rule

- At a review, a held stock with **Close ≤ SMA200** is sold at the next open. That is the only strategy exit.
- There is no time stop, stop-loss or profit target. The hypothesis is trend persistence, and a cap would add an arbitrary parameter. Kaminski & Lo (2014) caution against arbitrary stops.
- Delisting and stale-data handling are unchanged (harness, D059). They are data handling, not strategy.

## 6. Portfolio construction

| Item | Rule | Reason |
|---|---|---|
| Positions | 15 equal slots, weight (1 − 2% buffer)/15 ≈ 6.5% at entry | The top of your 12–15 range: least idiosyncratic noise. ≈ $6.5K per position, above the $5,000 minimum. |
| Rebalancing | None: positions drift with price until sold | Lowest turnover. A buy-and-hold-while-trending test. |
| Weight cap | 10% at entry (harness); no forced trims | Trimming would add turnover and a parameter. Weight concentration is reported. |
| Cash | D051: settled cash only, 2% buffer, 15% gap reserve | Unchanged |
| Costs | $7 per order; 10 bps slippage per side | Unchanged |
| Execution | Review at the first close of each month (EW benchmark calendar); orders at the next open | Unchanged, T+1 open |
| Accounts | $100K primary; $200K sensitivity only (15 slots) | As instructed |

## 7. Expected holding period

- **Months.** The daily-checked MA200 books of H014 held about 100 sessions on average.
- A monthly check removes most short whipsaws: a stock is sold only if it is below its average on a review day.
- I expect **about 120–200 sessions (6–10 months)**, with a long right tail of names that stay in trend for years.

## 8. Expected turnover and costs

| Mean hold (sessions) | Round trips a year (15 slots) | Modelled costs a year |
|---|---|---|
| 100 | 35 | 0.96% |
| 150 | 23 | 0.64% |
| 200 | 18 | 0.48% |

- The model (`P2_feasibility.annual_costs`) is **conservative**. It predicted 0.85% for the H014 random books, which actually cost 0.57%.
- **Expected realised costs: about 0.4–0.7% a year,** well below the 1.5% ceiling and less than half of H014 A's 1.46%. The design does not depend on barely meeting the limit.

## 9. Controls

| Code | Book | Question it answers | Kind |
|---|---|---|---|
| EW | E901-07, existing | Does H015 beat the passive universe? | benchmark |
| SPY | E900-07, existing | Does it beat the simplest alternative? | benchmark |
| **K1: random eligible, no trend filter** | Same 15 slots, seeds 1–5 paired with H015's, monthly review, same costs. Fills from **all** eligible stocks. A position exits at the first review on which it has been held ≥ 126 sessions (6 months, the standard momentum horizon; pre-declared). | **Does the trend filter add value at the same position count?** (G2) | benchmark |
| **K2: trend population** | Equal weight in **every** eligible stock with Close > SMA200, rebalanced at each monthly review. Same construction and $10M notional as the EW benchmark B901. | **Does the trend filter add value for the whole population,** free of 15-stock sampling noise? Compare with EW. | benchmark (diagnostic) |

- **No random-uptrend control:** H015 is itself random selection among uptrend stocks, so that control would duplicate the candidate.
- **K1's exit differs from H015's.** Without a trend filter there is no trend exit to apply: a name bought below its average would be sold at once.
  - The fixed 6-month hold is pre-declared, not matched to results.
  - Turnover and exposure differences between H015 and K1 are reported, as in H014.
- Controls are never candidates and are never promoted.

## 10. Proposed candidate count

- **One candidate: H015 v1.0.** Seeds are replicates.
- This adds 1 Phase 2 selection trial (Phase 2 total 3; cumulative since C01: 43).
- **Considered, not proposed:**
  - **A second variant with an index-level regime switch** (hold stocks only while SPY > its 200-day average). This is the best-evidenced form of trend following (Faber, Siegel).
    - It is a second, different mechanism, so it would be a separate hypothesis.
    - In 2010–2021 its main effect would be the 2020 crash and recovery, which happened after 2017, so it carries hindsight risk.
  - **MA50 > MA200 as an extra condition:** no evidence; an extra parameter.
  - **Other MA lengths:** excluded as candidates. Robustness only.

## 11. Statistical feasibility (`research/phase2/P2_h015_feasibility.json`)

**Noise in the Sharpe difference vs EW over 12 years**
- From the observed 12-stock books: tracking correlation with EW ≈ 0.78.
- Population-level noise ≈ 0.14.
- Seed (selection) noise ≈ 0.12 per 15-stock book.

**Probability of passing the +0.25 G1.1 margin, by true edge** (decision rule options; simulated, seed 20261001):

| True Sharpe edge vs EW | Seed-averaged (5 seeds) | Every one of 5 seeds | At least 4 of 5 | One 15-stock book |
|---|---|---|---|---|
| 0 (no edge) | 4.6% | 0.7% | 2.2% | 8.5% |
| +0.10 | 16% | 3.5% | 8.8% | 21% |
| +0.25 | 50% | 20% | 35% | 50% |
| +0.40 | 84% | 54% | 73% | 80% |
| +0.50 | 95% | 76% | 89% | 92% |

**Reading:**
- Requiring every seed to pass, as in C03, would leave little power.
- **I recommend deciding on the seed-averaged returns**: low false-pass rate, the same power as one book, and no seed choice possible. All seeds are shown individually.

**Independent decisions**
- 144 monthly reviews.
- About 200–420 position entries over 12 years per seed.
- Only a handful of market-wide trend regimes (2011, 2015–16, 2018 Q4, 2020).
- The time-series evidence is thin even though trades are many.

**Exposure**
- With roughly 700 qualifying names, the 15 slots stay filled about 98% of the time. Expect ≈ 92–94% invested, as in H014's books.
- **H015 will not move to cash in sell-offs** the way index-level rules do. This is a structural reason to expect a small edge.

**Are G1–G4 still suitable?**
- G1, G3 and G4 apply unchanged, computed on the seed-averaged book.
- G4a uses 6 perturbations, each also seed-averaged.
- **G2 needs a structural adaptation**, which I flag now rather than after results. H014's controls (C1 trend-only, C2 no-recovery, R random uptrend) do not exist for H015. Proposed G2: H015's seed-averaged Sharpe > K1's seed-averaged Sharpe, with K1 paired by seed.
- K2 vs EW is reported as the population answer but is not gated: it is not investable at $100K.

**Seed sensitivity**
- Large at 15 stocks: in H014's controls, Sharpe varied by up to 0.33 between seeds.
- 5 seeds reduce this noise in the decision by √5.
- 3 seeds would save runs but leave more noise (§17).

## 12. Development evaluation plan (frozen before any run, as for H014)

1. **Freeze a spec** (`research/phase2/P2_H015_spec.md`, hash-pinned): rules, IDs, decision rule, gates, perturbations, trigger.
2. **Build and test S015**, K1 and K2: look-ahead, SMA history, monthly calendar, selection, exits, fees, $5K minimum.
3. **Canaries**: non-candidate settings (e.g. SMA 100, 2010–2012), plus a reproduction.
4. **Committed runs** (2010–2021, `DEV`):
   - H015 seeds 1–5;
   - K1 seeds 1–5;
   - K2;
   - $200K H015 seeds 1–5.
5. **Gates on the seed-averaged H015 book.**
   - G1 (+0.25 vs EW, +0.10 vs SPY, CAGR ≥ EW − 2 pts, Calmar ≥ EW, drawdown ≤ EW + 5 pts).
   - G2 (beats K1).
   - G3 (≥ 4 of 6 two-year blocks; no block > 50% of excess).
   - G4:
     - (a) ≥ 5 of 6 perturbations keep ≥ EW + 0.10;
     - (b) 2× slippage keeps ≥ EW + 0.10;
     - (c) costs ≤ 1.5% a year.
6. **Conditional robustness**, only if G1–G3 pass, each run on seeds 1–5:
   - 2×, 4× and 6× slippage;
   - SMA 150; SMA 250;
   - weekly review; daily review;
   - 12 slots; 18 slots.
7. **Diagnostics:** DSR at Phase 2 candidates (3), Phase 2 broad, and cumulative (43); PBO; bootstrap intervals; per-seed results; K2 vs EW; turnover, exposure, cash, slot use and weight concentration.
8. **STOP** at the development checkpoint. No Holdout without your approval.

## 13. Key differences from H014

| | H014 | H015 |
|---|---|---|
| Entry signal | Trend + RSI pullback + recovery bar | Trend only (Close > SMA200) |
| Indicators | MA50, MA200, RSI14, prior-day high, 12-1 momentum | SMA200 only |
| Selection | 12-1 momentum ranking | Seeded random (factor-neutral) |
| Review | Daily | Monthly |
| Exit | MA200 break or 63/126-session limit | MA200 break at a monthly review; no time limit |
| Slots | 12 | 15 |
| Expected costs | 1.46% (A) | ≈ 0.4–0.7% |
| Key control | Trend-only, no-recovery, random uptrend | Random **without** trend filter; trend population |

## 14. Why H015 is not merely "the part of H014 that happened to perform best"

**What would make it so** (none of these is done):
- copying a best-performing H014 book (random-uptrend exit A seed 2, Sharpe 1.00, or exit B, 0.84);
- keeping H014's two-condition trend rule and the exit that did better (B's cap);
- picking a seed or slot count after seeing results.

**What is actually proposed:**
- Every rule is the standard pre-2010 form from the literature: one 200-day condition, a monthly check, equal weights, and a trend-failure exit with no cap.
- Several choices differ from the better-performing H014 books: one condition not two, monthly not daily, no cap, 15 slots.
- **The best observed analogue fails the margin.** There is no "winning part" being carried over. On the evidence we have seen, H015 is **more likely to fail than pass**.
- **The new question is the trend filter itself**: K1 (no filter) and K2 vs EW, which no H014 run measured.

**What I cannot claim:**
- The idea was prompted by H014's controls. 2010–2021 is therefore **not an independent test** of "random uptrend selection".
- That is why the Holdout, and later a true forward test, remain the only independent evidence, and why I recommend reading a development pass, if it happens, with this caveat.

## 15. Key risks and weaknesses

1. **Pre-observation.** The development result is partly predictable (above). This reduces the evidential value of a pass.
2. **Low expected edge.** The literature says MA effects are weak in large, low-volatility stocks and mainly come from index-level cash in long bear markets, which this design does not do.
3. **Power.** A true +0.25 edge passes only about half the time.
4. **Seed noise.** Any single $100K realisation can differ from the seed average by about ±0.12 Sharpe.
5. **No rebalancing.** Long-held winners can grow to large weights. This is reported, and there is no trim rule.
6. **K1's exit differs** (6-month hold versus trend exit). G2 compares filter-plus-exit against no-filter-plus-time-exit, not the filter alone.
7. **2010–2021 has no long bear market**, the regime where trend rules historically earned their keep. This is a fact about the sample, not a reason to change it.
8. **Operational:** QuantConnect node disk failures occurred twice in H014 (D099). Each would cost a technical repeat.

## 16. Estimated QuantConnect runs, runtime and cost

| Class | Runs |
|---|---|
| Canaries | 2 + 1 reproduction |
| Committed: H015 × 5 seeds, K1 × 5, K2 × 1, $200K × 5 | 16 |
| Conditional (only if G1–G3 pass): 9 settings × 5 seeds | 45 |
| **Maximum** | **64** |

- **Runtime:** about 15–25 minutes per 12-year run (K2 longer). That is about 5–7 hours committed and about 15–18 hours more if the conditional runs trigger.
- **Cost:** the existing $24/month subscription only. **No new spending.**
- **With 3 seeds instead of 5:** 10 committed and 27 conditional runs.

## 17. Decisions requiring your approval

1. **Whether to spend Phase 2 slot 2 on H015 at all**, given the opening section and §14: the closest design is already observed below the margin, and the expected outcome is "not development-qualified". The alternatives are to keep the slot for a hypothesis whose development result is not already partly known, or to close Phase 2.
   - **My recommendation:** approve H015 only if the main value you want is the clean answer to "does the trend filter add value" (H015 vs K1; K2 vs EW).
   - If the goal is a Holdout-ready candidate, the evidence suggests H015 is unlikely to provide one.
2. **The H015 rules as written in §3–§6:** Close > SMA200; monthly review; seeded random fill; MA200 exit; 15 slots; no rebalancing; no time stop.
3. **The decision rule across seeds.**
   - Recommended: gates on the **5-seed averaged** book, with every seed reported.
   - Alternatives: every seed must pass; or at least 4 of 5.
4. **5 seeds (recommended) or 3.**
5. **Controls K1 and K2**, including K1's pre-declared 6-month hold and K2 as a non-gated diagnostic.
6. **The G2 adaptation:** beat K1 instead of H014's controls.
7. **The 6 pre-declared perturbations** (SMA 150/250, weekly/daily review, 12/18 slots) and the conditional-robustness trigger (G1–G3 pass).
8. **The run count and runtime** in §16. No new spending.

**STOP.** H015 is not implemented and no backtest is run. H014 is preserved exactly as tested. The Holdout stays locked.
