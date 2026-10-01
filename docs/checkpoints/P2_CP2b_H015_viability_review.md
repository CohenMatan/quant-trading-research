# Phase 2: H015 viability review (P2-CP2b): is H015 worth hypothesis slot 2?

- **Date:** 2026-10-01.
- **Status: REVIEW ONLY.** No implementation, no H015 or control backtest, no new market data, the Holdout untouched. **STOP:** awaiting the owner's decision.
- **Inputs:** only committed, already-observed 2010–2021 results, simulations and the literature.
- **Analysis:**
  - `research/phase2/P2_h015_viability.py/.json` (new, simulation seed 20261002);
  - `research/phase2/P2_h015_feasibility.py/.json` (P2-CP2).
- The Phase 2 methodology is unchanged.

## Recommendation in one paragraph

**Do not spend slot 2 on H015. Preserve the slot.**

- **H015's development result is largely predictable** from books we have already seen. The predicted Sharpe difference vs EW is about **+0.03 ± 0.16**, and only about 40% of the systematic uncertainty remains open (central case).
- **Under any defensible seed rule, the chance of reaching +0.25 is about 1–10%.** The central case for an investable rule is about 4%. Most passes would be luck that does not carry forward.
- **Random selection is defensible as a research device but awkward as a production rule.**
- **No deterministic selection rule is both externally justified and uncontaminated** by results we already know.
- **The scientific question (A: does the MA200 filter add value across the population?) does not need a hypothesis slot.** It is not a candidate question, and it cannot by itself make a $100K strategy (question B).
- **Spending slot 2 here would mostly add false-acceptance risk** (each screened hypothesis raises the cumulative no-edge acceptance bound by about 4–5 points) for little chance of a real candidate.

## 1. How independent is H015 from the H014 evidence?

**Not very.**
- H014's six random-uptrend books are the same universe, the same period, random selection among MA200-uptrend stocks, MA200 exits and 12 slots.
- Their Sharpe differences vs EW were −0.12, +0.20, −0.07, +0.01, +0.04 and +0.12 (mean **+0.03**).
- H015 shares their **entire 2010–2021 market path**. It differs only by:
  - a **design shift**: a monthly check, one condition instead of two, no roll or cap, 15 slots;
  - **fresh seed draws**.

**How large can the design shift be?** In the observed books, comparable mechanics changes moved the Sharpe difference by 0.01–0.08:
- random exit B − exit A: +0.06;
- H014 B − A: +0.08;
- C2 B − A: +0.01.

One extreme: trend-only C1, −0.21. That book is momentum-ranked, which concentrates on a few names. H015 is not.

**Prediction of H015's development result** (Sharpe vs EW, one 15-stock book; `P2_h015_viability.json`):

| Assumed design-shift sd | Predicted mean | Predicted sd | Share of systematic uncertainty already resolved |
|---|---|---|---|
| 0.05 | +0.03 | 0.14 | 75% |
| **0.10 (central)** | **+0.03** | **0.16** | **56%** |
| 0.15 | +0.03 | 0.20 | 39% |
| 0.20 | +0.03 | 0.24 | 28% |

**Reading:**
- Much of a fresh H015 result is already known.
- What remains is mostly **seed luck**, about ±0.12 per book, which is noise rather than information.
- The genuinely new information is:
  - the effect of monthly vs daily checking;
  - the population-level filter effect (K2), which no H014 run measured.

## 2. Is random selection acceptable for a production strategy?

| Approach | Live portfolio | Does the research result represent it? | P(pass +0.25), central case | Seed sensitivity | Cherry-picking risk |
|---|---|---|---|---|---|
| **(a) One frozen seed**, declared before results | That seed's 15-stock book, following the same rule live | **Yes, exactly.** But its in-sample luck (±0.12) does not persist: its expected future equals the seed-average expectation | **9%**, mostly luck | Maximal: one draw | None if declared first. **Results of any other seed must never be seen,** or the declaration loses its value |
| **(b) Every seed must pass** | Any one seed | Yes, conservatively: "whichever seed you pick works" | **0.4%** | Measured | None |
| **(c) ≥ 4 of 5 seeds** | Any one seed | Mostly | **1.7%** | Measured | None |
| **(d) Mean of per-seed Sharpes** (each seed a real 15-stock book) | One seed, any | **Yes, as the expected outcome** of running the rule. Unlike the averaged-returns composite, it never describes a 75-stock portfolio nobody holds | **3.9%** | Averaged, also reported | None |
| (e) Averaged returns (my P2-CP2 suggestion) | Not held by anyone at $100K: a 75-stock blend | **No.** It overstates Sharpe through diversification a $100K holder never gets. **Withdrawn.** | 4.0% | Averaged | None |
| (f) Deterministic rule (§4) | Exactly the backtested book | Yes | Similar to (a) | **Hidden, not removed.** One fixed selection path has the same idiosyncratic luck, but it can no longer be measured | Rule choice itself can be hindsight-driven |

**Why the probabilities differ:** the closer a rule gets to the true expected performance (b–d), the less it can pass on luck. The observed evidence puts that expectation near +0.03.

**Best defensible method, if randomness stays:** **(d) for the decision**, plus a guard that **(a)'s pre-declared seed** must also pass. That is, decide on the expected investable outcome, and confirm that the actual live book is not the unlucky case.
- Its power is near (d)'s, about 4% here.
- Against a hypothetical true +0.25 edge, it is about 50% (the unconditional reference in the P2-CP2 feasibility table).

**Acceptability.**
- A random rule is **investable and reproducible**: a published seed plus the date.
- It is **unusual for a production strategy**, because the realised book carries about ±0.12 Sharpe of pure luck over 12 years, which no reasonable investor would treat as edge.
- It is acceptable as a research device. It is weak as a product unless the population edge is large enough to dominate the luck. **Here it is not:** an expected +0.03 against ±0.12 of luck.

## 3. Statistical power and selection noise

**Diversification of the observed 12-stock books:**
- tracking error vs EW about **11.8% a year**;
- correlation 0.78, so **only 61% of daily variance is the market**;
- seed-to-seed Sharpe sd about **0.13**, about 0.12 at 15 stocks.

**How large an edge a 15-stock book needs to be seen reliably:**
- To pass +0.25 with 80% probability, a single book needs a true edge of about **+0.40**.
- The seed-averaged rule needs about **+0.37**.

**What the evidence says about the edge:**
- The external evidence (Han, Yang & Zhou 2013: MA effects weakest in large, low-volatility stocks) and our observed books (+0.03) both put the plausible edge **far below** that.
- A 12–15 stock portfolio is **too concentrated to reveal** a trend-filter edge of the size the evidence suggests (≤ +0.1).

## 4. Can a deterministic investable selection rule be independently justified?

**Not one that is both relevant to the trend hypothesis and uncontaminated.**

| Candidate rule | External justification (pre-existing) | Problem |
|---|---|---|
| Largest market cap | Liquidity and capacity only. Return evidence points the **other** way: the size effect (Banz 1981; Fama & French 1992) predicts large caps **lag** an equal-weight universe | Our own benchmarks already showed large caps (SPY) beat EW over 2010–2021. Choosing it now would load on an observed result, and its only argument (liquidity) is moot in a ≥ $2B universe |
| Smallest market cap within ≥ $2B | Size effect (pre-2010) | Tests size, not trend. EW < SPY over 2010–2021 is already observed |
| Closest to the 52-week high (George & Hwang 2004) | Genuine pre-2010 trend-strength evidence | It is a momentum-type **ranking**, and the closest observed analogue (12-1-ranked trend-only C1) was −0.21 and −0.42 vs EW. Choosing it is as contaminated as rejecting it. It would also turn H015 into a ranking hypothesis |
| Low volatility within uptrend | Pre-2010 low-volatility evidence (Haugen & Baker 1991; Ang et al. 2006) | A different factor, already tested in programme 1 (H005/S005 failed Validation) |
| Systematic rotation / ID order / alphabetical | None needed: neutral | **Exactly equivalent to one random seed.** Deterministic in form, random in effect, with unmeasurable luck |
| Hold every qualifying stock | Literature-neutral | ≈ 700 names: impossible at $100K with the $5,000 minimum. This is K2, a diagnostic |

**Conclusion:** there is **no defensible deterministic selection rule** for an investable H015. Every candidate either adds a different factor bet or rests on information we have already seen.

## 5. Are K1 and K2 fair and useful?

**K1 as proposed** (random eligible, 6-month hold) is **not fair**.
- Its exit (time) differs from H015's (trend failure), so G2 would mix the entry filter, the exit rule and turnover in one comparison.
- A **more comparable K1′**: random eligible stocks with **the same exit as H015**, "sell at a review when Close ≤ SMA200 after having been above it at the previous review". This is a downward cross, which is what H015's exit always is for a held stock.
  - A stock bought below its average is held until it first rises above and then breaks down.
  - Entry is then the **only** difference, so K1′ isolates the filter.
- If K1′ is ever used, it replaces the 6-month K1.

**K2** (equal weight in every trend-qualified stock, monthly, $10M, B901 construction):
- **Fair and useful for question A**: same construction as the EW benchmark, only the membership filter differs.
- **Not investable at $100K**, never a candidate, and it says nothing direct about a 15-stock book (question B).

## 6. Question A vs question B

| | Question A: scientific | Question B: practical |
|---|---|---|
| Question | Does the MA200 filter add value across the eligible population? | Can a 12–15 stock, low-turnover portfolio built on it beat EW by +0.25 Sharpe? |
| Best instrument | K2 vs EW (one run) | H015 with a seed rule (§2) |
| Needs a hypothesis slot? | **No.** A benchmark-kind diagnostic is not a candidate and is never promoted | Yes |
| Evidence so far | Not measured | Closest analogue +0.03, about 4% chance of passing (central case) |
| Can A rescue B? | **No.** Even a sizeable population edge reaches a 15-stock book diluted by about ±0.12 of selection luck and a tracking correlation of 0.78 | — |

**Caution on A.** Running K2 is still another look at the 2010–2021 data. If its result shaped hypothesis 3, that would be mild data snooping, and it would have to be disclosed in any later pre-registration.

## 7. Costs, turnover, exposure and timing vs selection

- **Costs and turnover:**
  - expected costs about 0.4–0.7% a year (P2-CP2 §8; the model is conservative);
  - turnover about 3–5× a year;
  - mean hold about 6–10 months.
- **Exposure:** about 92–94% invested. Slots stay filled because roughly 700 stocks qualify on a typical day.
- **The practical portfolio is mostly a stock-selection problem, not trend timing.**
  - It never goes to cash in sell-offs, the mechanism behind most external MA evidence (Faber, Siegel).
  - 39% of its daily variance is stock-specific selection, versus 61% market.

## 8. Is spending slot 2 justified? Expected-value comparison

| | Spend slot 2 on H015 | Preserve slot 2 |
|---|---|---|
| Chance of a development-qualified candidate | ≈ 1–10% (central about 4%), mostly luck | Depends on a future hypothesis. The approved budget analysis gives 61–84% acceptance for a real +0.5 edge (P2-CP0c) |
| Chance it survives the Holdout given qualification | Low: a qualified H015 would most likely be a lucky draw from an edge near +0.03. The Holdout criterion (HO1 ≥ EW + 0.10) passes a no-edge book about 30% of the time | — |
| Effect on false-acceptance risk | Adds a screened hypothesis. The approved bound rises from ≤ 5.7% (1 hypothesis) toward ≤ 10.5% (2) for little gain | No added risk |
| New information | Monthly-vs-daily mechanics; seed spread; plus K1′/K2 | None now. K2 can be run separately if wanted (question A) |
| Cost | About 5–7 hours of committed runs; no new spending | None |

**Conclusion:**
- **Not justified.** The probability of a real investable candidate is very small, and most of what H015 would teach is either already known or obtainable without a hypothesis slot.
- **Preserving the slot is the correct decision.** It is not a failure to declare a weak hypothesis not worth testing; forcing it would only spend budget and add false-acceptance risk.

## 9. Provenance of every H015 rule (as proposed in P2-CP2)

| Rule | Classification | Note |
|---|---|---|
| Universe ≥ $2B, price ≥ $5, ADV ≥ $5M | Inherited (infrastructure, D033) | Unchanged |
| Long-only, no leverage, $100K, $200K sensitivity | Inherited (account constraints) | Unchanged |
| $7/order, 10 bps slippage, D051 cash, $5K minimum, next-open execution | Inherited (infrastructure) | Unchanged |
| Close > SMA200 | **External, pre-2010** (Brock et al. 1992; Siegel; Faber 2007) | The single standard condition |
| No MA50 > MA200 condition | **Principled** (no separate evidence; parsimony) | Not chosen from H014 results (H014 never tested it alone) |
| Monthly review | **External** (Faber 2007) | Also matches the EW benchmark calendar |
| Exit Close ≤ SMA200 at a review | **External** (the same rule's sell side) | — |
| No time stop, no stop-loss | **Principled** (parsimony; Kaminski & Lo caution) | Not because H014's capped exit B looked better; it did, which argues the other way |
| 15 slots | **Inherited** (owner range 12–15) + **principled** (least noise) | — |
| Seeded random selection | **Principled** (factor-neutral sample of the trend population) | **This is the rule most exposed to H014's observation** (random uptrend > momentum-ranked). Disclosed |
| No rebalancing | **Principled** (lowest turnover) | — |
| K1 6-month hold | Principled but **unfair** (§5) | Replace with K1′ if ever used |

**Disclosure:** no rule was set to a value that maximised any observed H014 result. The **choice to study this family at all** was prompted by H014's controls. That is why the development test is not independent (§1).

## 10. If H015 is not adopted

- **Correct decision: simply preserve slot 2.** Close the H015 proposal as "not adopted before implementation". It consumes no hypothesis budget and is not a failed hypothesis (as with H012 in C03).
- **Do not force a replacement.** A third Phase 2 idea should come from a genuinely different, externally motivated question, written without looking at more 2010–2021 results first.
- **Optional:** K2 vs EW as a single benchmark-kind diagnostic, if you want question A answered for its own sake. It is not a candidate, and its result must be disclosed in any later proposal.

## 11. Decisions requiring your approval

1. **H015:**
   - (a) **not adopted; slot 2 preserved** (recommended);
   - (b) adopted with the revised seed rule and K1′;
   - (c) deferred.
2. **If (b):**
   - the seed rule: (d) mean of per-seed Sharpes plus a pre-declared live seed that must also pass (recommended among the random options), or another option from §2;
   - K1′ replacing the 6-month K1;
   - K2 as a non-gated diagnostic.
3. **K2 diagnostic run** (one benchmark-kind run on 2010–2021, not a hypothesis), or not:
   - recommended: **not now**, unless question A matters to you on its own;
   - if run, its result is disclosed in any future pre-registration.
4. **Confirm the averaged-returns ("composite") decision rule from P2-CP2 is withdrawn.** It describes a portfolio nobody would hold at $100K.

**STOP.** H015 is not implemented and nothing was run. No replacement hypothesis is proposed. The Holdout stays locked. H014 remains preserved exactly as tested.
