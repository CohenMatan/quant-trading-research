# SA-CP1 — Post-H032 strategic architecture review (DESIGN ONLY)

- **Decision trail:** D285 closed H032. D286 is the owner's request for this review (verbatim in `docs/owner/2026-10-22_post_h032_strategic_review.md`). This document is D287.
- **Nothing was run.** There is no new hypothesis, backtest, performance calculation, search, purchase, constraint change or Holdout access.
- **Sources of numbers:**
  - Numbers marked *observed* are already committed (OS-CP3, OS-CP4, P2-CP10, LH-CP4).
  - Numbers marked *illustration* are plain arithmetic on stated assumptions, shown so the reasoning can be checked. They are not estimates of any strategy.
- **Unchanged:** H031 parked; RR6 INCONCLUSIVE; H028 and H032 REJECTED; Holdout sealed.

## 1. Answer in one paragraph

**Yes, the current architecture carries a real structural hurdle, but it is not the main problem.**

The hurdle has two parts:
- **Expected costs:** a concentrated, equal-weight 15-stock book run under our cash and trading rules pays roughly 0.5–1.5 points a year relative to SPY before any selection skill (§2.2).
- **Tracking error:** much more important, it differs from SPY by 6–12 points a year. A modest real edge therefore cannot be told apart from luck within any evidence we can obtain.

**Neither architecture creates a source of return.**
- An SPY core reduces the structural costs and the damage when the selection is wrong.
- But it shrinks any real edge in exactly the same proportion as it shrinks the noise, so it does not make an edge easier to prove.
- Both architectures need the same thing: a stock-selection component with a positive expected edge after costs, for an economic reason that does not come from the 2010–2021 winners. We have not identified one. Thirty-one registered hypotheses failed or could not be evaluated, and the published large-cap evidence is weak after costs and after publication.
- On genuinely independent evidence we can obtain, neither architecture can confirm the modest edges that are plausible.

**Recommendation: PAUSE offensive strategy discovery** (§6). Keep SPY as the offensive baseline. If the work is ever resumed, use Architecture 2, but only after an owner-approved economic thesis and an independent-evidence plan, not as a reason to search again.

## 2. Architecture 1 — standalone Top-15 stock selection (current)

### 2.1 Economic rationale

- **Where any edge must come from:** SPY is the cap-weighted market. Before costs, the average active dollar earns the market return (Sharpe's "arithmetic of active management", 1991). A standalone book beats SPY only by holding different weights for a reason other investors underprice:
  - a **risk premium** (value, profitability, momentum, size);
  - a **behavioural or information lag** (post-earnings drift, insider buying, issuance);
  - a **structural constraint** other investors face (for example leverage aversion).
- **The evidence for long-only large caps after 2000 is thin:**
  - Published anomalies lose about a quarter of their returns out of sample and roughly half after publication (McLean & Pontiff 2016).
  - They are weakest in large, liquid stocks: the ≥ $2B universe.
  - Low-volatility and leverage-aversion effects deliver better risk-adjusted returns, not more wealth than SPY in a rising market. Without leverage they work against the stated objective.
- **The programme's own record agrees.** Each source above was tested on ≥ $2B US stocks and none qualified:
  - profitability (H016), earnings drift (H017), momentum and technical rules (H018–H020);
  - multi-factor and learned scores (H022–H028), insider buying (H025);
  - business improvement (H029–H030, not evaluable), ΔROA (OC-2, method not validated);
  - net share reduction (H032).

### 2.2 Structural disadvantages relative to SPY

| Item | Expected effect (structural, generalisable) | What 2012–2021 showed (*observed*, not generalisable) |
|---|---|---|
| **Weighting:** equal weight vs cap weight | A tilt toward the smaller names in the ≥ $2B universe. Its **expected** sign is uncertain (the large-cap size premium is weak), but it adds a large **regime-dependent** gap: some decades favour equal weight, others cap weight | The equal-weight pool was 2.1 points a year behind SPY. That was a mega-cap decade. It is a property of the period, not a law |
| **Concentration:** 15 names | Single-stock returns are strongly right-skewed: most stocks trail the index and a few drive it (Bessembinder 2018). A small book usually misses them. Its **typical** outcome is below the index even when its average is not. Higher volatility also lowers compound growth: an *illustration* of 18–20% vs 16% volatility costs about **0.3–0.7 points a year** (σ² / 2) | Random 15-name books from the pool: median 12.72% vs the equal-weight pool's 14.24%. That is −1.5 points, including turnover and costs |
| **Cash drag** | 2% buffer, plus the D051 rule that settled cash fund buys with a 15% gap reserve, plus unfilled slots. *Illustration:* 2–5% average cash × a 5–6% equity premium ≈ **0.1–0.3 points a year** | H032's lowest cash level was 2.7% |
| **Turnover and costs** | $7 per order plus 10 bps. Monthly Top-N rules turn over about 100–150% a year → **about 0.3–0.6 points a year** at $100,000. SPY costs about 0.09% a year, already inside its price | H032: 139% turnover, 0.45% a year |
| **Sector exposure** | Unconstrained 15-name books take large industry bets. These have no expected return of their own but add a great deal of tracking error | H032 had 37–43% in retail in 2016–2017 |
| **Breadth** | By Grinold's law (information ratio ≈ IC × √breadth), 15 names reviewed monthly turn a weak signal into a very noisy portfolio result | — |

**Total:**
- **Expected structural cost:** about 0.5–1.5 points a year before selection.
- **Regime-dependent gap:** zero or uncertain on average, but several points either way in any decade.
- **Tracking error vs SPY:** about 6–12 points a year (*assumption*, typical of concentrated large-cap books).

OS-CP4's "3–4 point hurdle" therefore combines about 1 point that is structural with about 2 points that belonged to the 2012–2021 regime. **It should not be carried forward as a general constant.**

### 2.3 What would need to change

- **Nothing, to keep running it:** this is the current architecture.
- **Changes that would reduce the structural hurdle**, each an owner constraint decision, to be judged on structure and never on observed results:
  - more names (the 15-position limit; the D044 / $5,000 rules make N > 15 need more capital);
  - sector caps;
  - benchmark-aware (cap-tilted) weights;
  - slower turnover.
- **The catch:** each of these moves the book toward SPY. Taken far enough, it becomes Architecture 2.

### 2.4 Data and infrastructure

- **Complete today:** harness, S033-style host, shadow engine verified against LEAN, SEC objects in the Object Store, QuantConnect at $24 a month.
- **Binding limits:**
  - the universe is RR6 INCONCLUSIVE;
  - QuantConnect's plain-text and 50-file rules;
  - no pre-2010 history on QuantConnect (RR3 W0 FAIL).

## 3. Architecture 2 — SPY core plus a smaller offensive stock component

### 3.1 Economic rationale

- **The core:** SPY earns SPY minus a negligible cost. **It generates no alpha by construction.** SPY's strong 2010–2021 is not a reason to prefer it, and picking it for that reason would itself be hindsight.
- **What the core does:**
  - makes the account's market exposure equal to the benchmark;
  - removes most structural costs (§2.2) from the share it covers;
  - limits how far the account can fall behind SPY.
- **Any excess return comes from the satellite.** With satellite weight w and satellite edge α (after the satellite's own costs):
  - excess return ≈ w × α;
  - tracking error ≈ w × satellite tracking error.
- ***Illustration:*** w = 30% and α = 3% a year gives about +0.9 points a year. Over 30 years that would compound to about 30% more wealth, which is meaningful **if the edge is real.**

### 3.2 The key limitation: an SPY core does not make an edge easier to prove

- The evidence ratio t = (w × α) √T / (w × TE) = α √T / TE **does not depend on w**.
- Shrinking the satellite reduces the cost of being wrong but gives exactly the same statistical evidence as running the satellite alone.
- ***Illustration*** (TE = satellite tracking error):

| | Years needed for one-sided 5% evidence, (1.645 × TE / α)² | t-statistic over the 4.67-year Holdout |
|---|---|---|
| α 3%, TE 8% | about 19 | 0.81 |
| α 3%, TE 6% | about 11 | 1.08 |
| α 5%, TE 8% | about 7 | 1.35 |
| α 2%, TE 8% | about 43 | — |

### 3.3 Structural disadvantages

- **The satellite is even more concentrated at $100,000.** With the $5,000 minimum and 2% buffer:
  - a 20% satellite holds at most 3 names;
  - 30% → 5 names;
  - 50% → 9 names.
  - The fixed $7 commission weighs more on a small sleeve.
- **Long-only limits active bets.** The satellite can only overweight. Underweighting a mega-cap is possible only by shrinking the core, and the stocks it holds are already partly owned through SPY.
- **Rebalancing:** keeping the core / satellite split adds turnover. It is small if done rarely.
- **Advantages:**
  - core cash drag and core turnover are close to zero;
  - sector and weighting bets are limited to the satellite's share.

### 3.4 What would need to change (owner decisions; none made here)

- **Scope:** ETFs are outside "US common stocks". SPY as a holding needs a scope amendment. RR7 Path B noted this; SYS-1's OD-1 granted it for SYS-1 only.
- **Position rules:** SPY exempt from the 10% cap and from the 15-position count (the OD-1 precedent).
- **Allocation:** a fixed core / satellite split with a rebalancing rule.
- **Account size:** a larger satellite or a larger account (the OD-2 precedent was $200,000, for SYS-1 only).
- **Gates:** evaluation measured on the satellite's active return, because whole-account gates hide it.

### 3.5 Data and infrastructure

- **Data:** SPY is available on QuantConnect; nothing needs to be bought.
- **Accounting:** the SYS-1 ledger engine `qr_sys1` (built and tested offline, never run) is a precedent for SPY-plus-sleeve accounting.
- **To be built:** an ETF-aware harness rule. That is infrastructure development, not authorised now.
- **Universe limits:** the same as Architecture 1. The satellite still depends on the RR6 INCONCLUSIVE universe.

## 4. Is either advantage economically plausible, independent of the 2010–2021 winners?

- **Architecture 1:** only if a selection rule has an expected edge above about 1–1.5 points a year after costs, and enough of it to survive several points of regime-dependent drift. Documented large-cap premia after costs are about that size or smaller, and our tests did not find them. **Not credible on present evidence.**
- **Architecture 2:** the structural argument (lower costs, bounded shortfall) is real and general. But it is risk control, not return. Excess return still requires the same satellite edge. **No new source of return.**
- **Not used as evidence:** the observed winners (momentum diagnostic MOM 19.55%, B0, SPY's own decade). Using them would be choosing on 2012–2021 outcomes.

## 5. How a future hypothesis could get genuinely independent evidence

This is the same for both architectures:

| Source | Status | Power for a 3% a year edge (*illustration*, TE 6–8%) |
|---|---|---|
| 2010–2021 | Spent for selection (D261, OS-CP4); exposed development data only | — |
| Holdout 2022-01 → 2026-08 | One use, one candidate programme-wide (D267) | t ≈ 0.8–1.1 |
| True forward test after a freeze | Free, but slow | 11–19 years to one-sided 5% |
| Pre-2010 history | Not on QuantConnect (RR3 W0 FAIL); needs licensed point-in-time data (RR1 Option 3; D123 / D124 purchase rule) | 10+ additional years would help materially |
| Other markets | Out of scope (US equities only) | — |

**Conclusion:** with existing resources, only an edge of about **5% a year or more** could be confirmed within a decade. That is larger than anything the large-cap literature supports.

## 6. Recommendation and owner decisions

1. **PAUSE offensive strategy discovery.**
   - No new score, signal or hypothesis.
   - Neither architecture offers a credible, testable source of additional return with our existing data, budget and evidence.
2. **Keep SPY as the offensive baseline** (OC-CP6). That is a statement about cost and evidence, not a claim that SPY "wins".
3. **Record Architecture 2 as the preferred framework if offensive selection is ever resumed.** It bounds structural costs and shortfall. Its constraint changes (§3.4) should be decided only together with a specific thesis, and not now.
4. **Conditions to resume** (all needed; owner decision):
   - (a) an ex-ante economic thesis for a large-cap edge after costs, written before any data is examined;
   - (b) an independent-evidence plan that can detect the claimed size: a prospective forward test and/or licensed pre-2010 data, the latter a separate purchase decision under D123 / D124;
   - (c) the Architecture 2 constraint package approved on structural grounds.
5. **Other options for the owner** (not recommended now):
   - resume Architecture 1 searches on 2010–2021 (no: spent data, structural hurdle, no detectable edge);
   - adopt Architecture 2 now with an existing signal (no: there is none and rejected lines may not be reused);
   - start a data-purchase review (possible later; outside this checkpoint's restrictions).

**STOP:** awaiting the owner.

## 7. Programme totals

- **Hypotheses:** 31 registered (H001–H030 and H032), plus H031 as a parked draft.
- **Strategies:** 88 strategy ids.
- **Experiments:** 588 logged.
- **Production candidates:** none.
