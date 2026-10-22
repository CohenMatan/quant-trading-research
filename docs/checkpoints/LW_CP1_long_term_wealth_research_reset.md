# LW-CP1 — Long-Term Wealth Research Reset — Constraints, Opportunity Set and Next Direction

- **Decision trail:** D288 is the owner direction (verbatim in `docs/owner/2026-10-22_long_term_wealth_research_reset.md`). This document is D289.
- **This is a design and research review only.** There is no hypothesis registered, backtest, return calculation, optimisation, constraint change, purchase, new infrastructure or Holdout access.
- **Sources:** our committed checkpoints, plus published literature. A literature claim marked *(verify)* has to be checked against the source papers before any decision rests on it.
- **Unchanged:** H028 and H032 REJECTED; H031 parked; RR6 INCONCLUSIVE; Holdout sealed.

## 0. Short answer to the final question

**What is credible:**
- **Do not lose to SPY through frictions.** Low turnover, low costs and taxes are not alpha, but over 20–30 years they decide much of terminal wealth.
- **Long-horizon risk premia have the strongest economic case** (smaller-company value / profitability tilts, Direction D1). We cannot test them independently with our resources, and they can lag SPY for a decade or more. That makes them an allocation belief for the owner, not a research question we can settle.
- **The one direction that is both distinct from everything we tested and testable on genuinely unexposed evidence is a narrow event-driven satellite** built on non-fundamental forced selling around **corporate spin-offs** (Direction D2).
  - Its prior is only moderate: the post-2000 evidence is mixed and has to be checked first.
  - It is worth only a small, falsification-first investigation with explicit kill criteria. **No returns are computed until a desk review and a data census pass.**

**Which restrictions block the most promising opportunities:**
- the swing-trading / monthly Top-N framing (wrong horizon for slow premia and event drifts);
- the ≥ $2B floor (excludes where premia and event effects are largest);
- the stocks-only rule (no SPY core for idle cash).

**But the restriction that binds hardest is not a rule. It is the lack of independent historical evidence** (§1, §5).

**Pause is defensible.** If the owner judges a moderate-prior event satellite not worth even a small desk study, the honest recommendation is to pause offensive discovery and hold SPY (§7).

## 1. Why the programme has not produced an offensive strategy that beats SPY

### 1.1 What was demonstrated

All results below come from 2010–2021, ≥ $2B US stocks, point-in-time data and our own frozen nulls.

| Mechanism | Test | Result | Status |
|---|---|---|---|
| Short-horizon technical rules / indicator grammar | C01–C03; H018 (1,533 configurations, full-search null) | p = 0.31; no-edge worlds' "best" configurations beat SPY by +6.8% a year at the median | **Rejected** |
| Cross-sectional momentum (12-1, smooth, trend factor) | H019 signal test, 5,000-world null | top decile −2.2% a year, IC t 0.22 | **Rejected** at signal level (50% MDE 4.5–11% a year) |
| Chart patterns / sector momentum | H020; H021-A (2000–2017) | t 0.27; t −0.35 | **Rejected** |
| Profitability (GP/A) | H016 portfolio; GPA feature in H024 | Sharpe 0.69 vs SPY 0.92; best H024 feature t 1.24 | **Rejected** (portfolio); weak as a feature |
| Earnings-reaction drift | H017 | beat SPY (17.5% vs 14.9% CAGR) but g/SE 0.71 and 74% of the excess in 2014–15 | **Inconclusive**, rejected by gates |
| Multi-factor / weighted / feature-selected scores | H022, H023, H024 | t_IC 0.48; best weighting p 0.41; best model p 0.35 | **Rejected** |
| Insider cluster buying | H025 | t −0.93 | **Rejected** |
| Learned scores | H026–H028 | wealth above SPY, but explained by low-volatility exposure in down markets; H028 null structurally suspect | **Rejected**. A defensive profile, not offensive alpha |
| Business improvement / ΔROA | H029–H030; OC-2 | null inadequate; method not validated | **Not evaluable** (never return-tested) |
| Fundamental surprise (OF-A) | Stage C / LH-CP4 | data partly feasible; power at +3% a year 10–46% | **Never evaluated** |
| Net share reduction (+ cash-flow / growth filters) | H032 | 11.8% vs SPY 16.3%; the unfiltered version also behind | **Rejected** |

**Never evaluated by this programme:**
- smaller-cap segments;
- standalone value;
- holding horizons of a year or more;
- corporate events other than earnings and insider trades (spin-offs, index changes);
- **any** stock-selection evidence outside 2010–2021.

### 1.2 Diagnosis

Ranked by weight of evidence:

| Candidate cause | Assessment | Basis |
|---|---|---|
| **Economic weakness of conventional signals in large caps** | **Main cause (demonstrated within power limits).** Several independent signal-level tests with calibrated nulls found near-zero predictive power | H019, H022–H025 |
| **Insufficient statistical power** | **Binding (demonstrated).** Detectable edges were about 4–15% a year, so modest real edges (1–3% a year) could never be confirmed. "Not found" ≠ "absent" | P4-CP3R2, P7-CP4, LH-CP4, SA-CP1 |
| **Concentrated equal-weight construction** | **Contributing (demonstrated as structural cost).** About 0.5–1.5 points a year plus 6–12 points of tracking error. It does not explain the signal-level nulls | SA-CP1 |
| **Benchmark-relative regime** | **Contributing (observed, interpretation).** 2012–2021 was a mega-cap decade: the equal-weight pool trailed SPY by 2.1 points a year, and most factor tilts (value, size, low volatility) had weak or negative decades | OS-CP4 |
| **Large-cap restriction** | **Plausible, untested by us (interpretation).** The literature finds most anomalies concentrated in smaller stocks and much weaker in large caps (Hou, Xue & Zhang 2020) | Literature |
| **Data quality / survivorship** | **Second-order for returns, first-order for operations.** Bias bounds were up to about 1.3 points; platform changes blocked H022, SYS-1 and H029, and made old work non-reproducible | RR3–RR6, SYS1-CP0–2 |
| **Prior searching / overfitting** | **Controlled, but it has spent the data.** The nulls prevented false positives, not true ones. Any new finding on 2010–2021 would carry a large selection penalty | D139, D261, OS-CP4 |

## 2. Constraints

Kinds: **I** = protects research integrity; **O** = limits the opportunity set; **P** = practical / cost realism.

| Rule | Kind | Why it exists | What it costs us | If relaxed: possible benefit / new risk / data available? | Recommendation |
|---|---|---|---|---|---|
| Point-in-time data, next-session execution | I | No look-ahead | Nothing real | — | **Keep** (non-negotiable) |
| Realistic commissions and slippage | I/P | Backtests must survive real costs | Our $7 per order is above many current retail commissions, but spreads in smaller stocks are larger than 10 bps | Recalibrating to the owner's **actual** broker costs, with a spread model for smaller names, is realism, not relaxation. Needs owner information | **Keep; recalibrate only from real broker facts** |
| US equities only | P | Data, licence, simplicity | Excludes international premia | Not a source of excess return over SPY by itself; no point-in-time international fundamentals on our subscription | **Keep** |
| Long-only | I/P | Ruin risk, borrow cost, owner preference | Cannot short overpriced stocks; long-only captures maybe half of a long-short premium | Shorting adds unbounded-loss risk and borrow fees | **Keep** |
| No leverage | P (owner risk) | Ruin risk, borrowing cost | **The most direct lever on terminal wealth.** Modest leverage of a cheap index raises expected wealth if the equity premium exceeds the borrowing cost (life-cycle argument, Ayres & Nalebuff 2010) | Volatility drag, margin calls, path risk; this is a personal risk decision, not a research question | **Keep** (owner instruction); recorded as the main constraint on terminal wealth |
| Market cap ≥ $2B | O/I | Liquidity, data coverage, survivorship control | Excludes the segment where value, profitability, size and event effects are largest | Lowering to about $300–500M opens small / mid caps. Costs: wider spreads, thinner data, **worse survivorship on QuantConnect** (missing caps cluster in disappearing firms, P7-CP5d / RR5); a new universe audit is needed | **Reconsider, only for a specific direction and after a universe audit** |
| Price ≥ $5 | I | Excludes penny-stock microstructure | Negligible above $300M | — | **Keep** |
| ADV20 ≥ $5M | O/P | Liquidity | Excludes many smaller firms; at $100,000 a $6,700 position is tiny relative to $1M of daily volume | A position-relative rule (e.g. order ≤ 1% of ADV) keeps liquidity safe and opens smaller names | **Reconsider together with the cap floor** |
| ≤ 15 positions; ≥ $5,000 each | P | Fixed $7 commission at $100,000 (D044) | Forces concentration: about 0.3–0.7 points a year of variance drag and missed right-tail winners (Bessembinder 2018) | More names are viable only if real per-order costs are lower; otherwise costs rise | **Reconsider after cost recalibration** |
| ≤ 10% initial position | I | Concentration risk | Little | — | **Keep** |
| $100,000 account | P | Owner's research scale | Fixed costs bite; small sleeves hold very few names (SA-CP1) | A larger account is a funding decision, not research | **Keep** (disclose size dependence) |
| **Holding period "days to weeks / weeks to months"; monthly Top-N** (mission, D094) | O | Original swing-trading mission | **Wrong horizon for a 20–30-year objective.** Slow premia and event drifts work over 1–3 years; monthly churn adds cost and tax | Needs a mission / scope update to long-horizon, low-turnover equity investing | **Reconsider (most important framing change)** |
| Stocks only, no ETFs (SPY cannot be held) | O | Mission scope | No cheap core for idle capital, so every architecture carries cash or concentration drag | SPY as core needs a scope amendment (OD-1 precedent, SYS-1 only) | **Reconsider** (needed for any satellite design) |
| Taxes not modelled | — (missing realism) | Research simplification | In a taxable account, 100–150% annual turnover can cost about 1–2 points a year against buy-and-hold SPY *(illustration; depends on rates)* | Needs the owner to say whether the account is taxable | **Add as an owner fact** |
| 2010–2021 is development; Holdout sealed; 1999–2009 stress only (D035) | I | Integrity | Leaves no independent historical window for stock selection | A direction whose event list comes from SEC data might use 1998–2009 legitimately (§5). That needs a D035 amendment for that direction only (D160 precedent) | **Keep; possible narrow amendment** |

## 3. Directions: two pass the bar, others were considered and not proposed

### D1 — Long-horizon size / value / profitability premia in a broader universe (low turnover)

1. **Source of return:** compensation for distress and illiquidity risk, plus extrapolation errors (Fama & French 1993; Lakonishok, Shleifer & Vishny 1994; Novy-Marx 2013). Quality controls revive the size effect (Asness et al. 2018).
2. **Why it might persist:** risk-based parts cannot be arbitraged away, and behavioural parts require patience most investors lack (decade-long tracking error).
3. **Evidence:** strongest of any equity premium: about 90 years in the US, replicated across many countries (Fama & French 2012; Asness, Moskowitz & Pedersen 2013).
4. **After publication and costs:**
   - Premia shrink after publication (McLean & Pontiff 2016).
   - Value had a historic 2007–2020 drawdown, and it is debated whether it is impaired or cyclical (Arnott et al. 2021; Israel, Laursen & Richardson 2021).
   - Low-turnover implementation keeps costs small.
5. **Distinct from previous tests?** **Only partly.** Profitability (H016) and book-to-market (an H024 feature) were tested in large caps over 2010–2021. The new elements are the universe and the horizon, not the mechanism.
6. **Without leverage:** yes.
7. **Risks:** **10–15-year periods of trailing SPY** are documented. Higher volatility; small-cap crashes.
8. **Data:** needs point-in-time small-cap fundamentals and market caps. On QuantConnect these are missing for about 18% of stock-months and concentrated in disappearing firms (survivorship). SEC XBRL starts in 2009.
9. **Feasible with existing resources?** Only for 2010–2021 (spent, and an unusually bad decade for these premia), with uncertain small-cap data.
10. **Independent validation:**
    - **Not feasible** for us. Pre-2010 point-in-time fundamentals would require a purchase.
    - A forward test needs decades to discriminate.
    - The real evidence is the published out-of-sample record, which we can read but not add to.
- **Verdict:** **economically the most credible, but not researchable by this programme.** If the owner believes in these premia, it is a portfolio-policy decision (low-cost diversified implementation, accepting long underperformance), not a hypothesis to backtest.

### D2 — Forced-selling event drift: corporate spin-offs, held 12–24 months, as a satellite

1. **Source of return:** non-fundamental selling pressure.
   - Parent-company holders receive shares they did not choose: index funds, mandate-constrained or size-constrained funds.
   - The new company has little analyst coverage and is often dropped from the parent's index.
   - Selling pressure can depress prices below fundamental value for months.
   - Part of the documented gain comes from later takeovers (Cusatis, Miles & Woolridge 1993).
2. **Why it might persist:** the selling is driven by mandates and indexing rules, not by information. Passive-fund growth may have *increased* it. Capacity is small, which matters little at $100,000.
3. **Evidence:**
   - Strong in early samples (Cusatis et al. 1993; Desai & Jain 1999; McConnell & Ovtchinnikov 2004 *(verify)*).
   - Post-2000 evidence is mixed and must be reviewed, including the record of dedicated spin-off funds and ETFs since 2006 *(verify)*. **I do not assert that the effect has survived.**
4. **After publication and costs:** possibly decayed. Costs are small (one buy, one sell per event; 12–24-month holds).
5. **Distinct from previous tests?** **Yes.** No spin-off, index-change or forced-selling test exists in H001–H032. It is not a renamed score.
6. **Without leverage:** yes.
7. **Risks:**
   - single-company risk (diversify across concurrent events);
   - few events, so it is lumpy;
   - small, newly listed firms;
   - long stretches with no edge if the effect has decayed.
   - As a 20–30% satellite on an SPY core, the account-level drawdown stays close to SPY's.
8. **Data:**
   - The event list comes from **SEC EDGAR** (free; spin-off registration filings, Form 10, since 1996), so it is independent of QuantConnect's universe.
   - Prices come from QuantConnect, which carries daily data for later-delisted US stocks before 2009 (RR3: 2–7% exits in the non-cap set).
   - Size can be screened by dollar volume and price, which QuantConnect has. **Point-in-time market caps are not needed.**
   - Ticker-to-security matching must happen in-cloud (D257).
9. **Feasible with existing resources?** **Yes**, with modest work: an SEC event census offline, plus one aggregate-only in-cloud coverage check. No purchase.
10. **Independent validation:** **feasible.** Spin-off events from **1998–2009** were never examined by this programme and are outside the exposed 2010–2021 selection work. A forward test from the freeze date adds more.
    - *Illustration (power, assumption):* a per-event 12-month abnormal-return standard deviation of 35–45% and about 200 eligible events give a standard error of about 2.5–3.2%.
    - A 10% 12-month effect would be clear (t ≈ 3–4).
    - A 5% effect would be marginal (t ≈ 1.6–2).
    - The census must establish the real event count first.
- **Verdict:** **a moderate prior, but the only direction that is both distinct and independently testable.** Worth a small, kill-criteria-first investigation.

### Considered and not proposed

| Idea | Reason |
|---|---|
| Leverage (life-cycle index leverage) | The most direct terminal-wealth lever, but excluded by the owner (no leverage) and a personal risk decision, not research |
| Market timing / trend exits | Defensive. Long-only and unleveraged, it lowers expected terminal wealth on average (P4-CP2: a risk tool, not a return source) |
| Low-volatility / defensive tilt | Exactly what H026–H028 turned out to be; raises Sharpe, not long-run wealth versus SPY |
| Microcaps | Strongest anomalies, but costs and QuantConnect data quality / survivorship are worst there; untestable credibly |
| More large-cap scores (quality, momentum, ML) | Tested repeatedly with null results (§1); would recycle rejected lines |
| Tax-loss harvesting / direct indexing | Real after-tax gain in taxable accounts (Chaudhuri, Burnham & Lo 2020) but not pre-tax market outperformance, and depends on the owner's tax situation. Noted as a planning item |

## 4. Comparison

| | D1 premia, broader universe | D2 spin-off satellite |
|---|---|---|
| Expected advantage (literature, before decay) | About 1–3 points a year as a long-only tilt *(verify)* | Early studies: double-digit 2–3-year abnormal returns; now unknown |
| Credibility after publication and costs | Moderate (risk-based part durable) | Low-to-moderate (must verify post-2000) |
| Risk | Decade-long underperformance; small-cap crashes | Idiosyncratic and lumpy; bounded by satellite size |
| Transaction costs | Low (annual rebalancing) | Low (two trades per event) |
| Distinct from H001–H032 | Partly | Yes |
| Data on existing resources | Weak (small-cap survivorship) | Adequate in principle (SEC + QuantConnect prices); to be verified |
| Independent validation feasibility | **No** (would need purchased pre-2010 data or decades) | **Yes** (1998–2009 events + forward) |
| Constraint changes needed | Cap / ADV floor, horizon, possibly ETFs | Horizon (12–24 months), size floor for events, SPY core (ETF scope), narrow D035 amendment |

## 5. Recommendation

**Investigate D2 with a three-stage, falsification-first plan.** Each stage ends in a STOP, and **no strategy return is computed before Stage 3 is frozen.**

| Stage | Work | Output | Kill criterion (pre-set) |
|---|---|---|---|
| 0. Desk review | Read the spin-off literature after 2000 and the record of dedicated spin-off funds; write the expected effect size and mechanism. No data | Go / no-go memo | Post-2000 evidence shows no positive effect after costs → **stop, pause** |
| 1. SEC event census (offline) | Count spin-off distributions 1998–2021 from EDGAR filing indexes; define event dates point-in-time. Counts only, no prices | Census and definitions | Fewer than about 150 eligible events in 1998–2009, or dates not reliably point-in-time → **stop** |
| 2. Coverage canary (in-cloud, aggregate-only, 0 orders) | Share of census events with QuantConnect price data, including later-delisted firms, by year | Coverage table | Coverage < 85% or skewed toward survivors → **stop** |
| 3. Pre-registration (H033, only on owner approval) | Frozen rule, a 1998–2009 confirmatory window, a forward test from the freeze, power analysis before any return | Frozen spec | Power < 50% at the Stage 0 effect size → **stop** |

**Owner decisions needed:**
1. Pursue D2 at Stage 0 only, or pause (§7).
2. Accept in principle that a successful D2 would need:
   - holding periods of 12–24 months, beyond D094;
   - an event size floor defined by price and dollar volume rather than the ≥ $2B point-in-time cap;
   - SPY as the core holding (ETF scope, OD-1-type exemption);
   - a D035 amendment for D2 only, making 1998–2009 its confirmatory window.
   These are decided at Stage 3, not now.
3. Provide two facts: actual broker costs, and whether the account is taxable.
4. Treat D1 as a portfolio-policy question outside the research programme, or set it aside.

**Effort:** Stage 0 is a document. Stages 1–2 reuse the existing SEC client / cache and the aggregate-only canary pattern, with no new platform infrastructure. Nothing is purchased.

## 6. What would make the research programme credible again (any direction)

- Choose a mechanism with an economic story **before** looking at data, never from 2010–2021 outcomes.
- Require **independent evidence** (an unexamined period from independent event data, or a forward test).
- Fix the **horizon and turnover** to match a 20–30-year objective.
- Use an **SPY core** so failures cost little and idle capital stays invested.
- Accept that **only large effects are confirmable**; small premia are beliefs, not findings.

## 7. Alternative recommendation: pause

If the owner judges D2's prior too weak for even Stage 0:
- **pause offensive strategy discovery**;
- hold SPY as the offensive baseline;
- keep all records and infrastructure frozen.

That outcome is consistent with the evidence. Thirty-one hypotheses produced no robust large-cap edge, and the most credible remaining premia (D1) are not testable by us.

## 8. Programme totals

- **Hypotheses:** 31 registered (H001–H030 and H032), plus H031 as a parked draft.
- **Strategies:** 88 ids.
- **Experiments:** 588 logged.
- **Production candidates:** none.

**STOP:** awaiting the owner.
