# Phase 2 research opportunity review (P2-CP3)

- **Date:** 2026-10-01.
- **Status: REVIEW ONLY.** No H016 defined, nothing implemented, no backtest or diagnostic run, the Holdout untouched. **STOP:** awaiting the owner's decision.
- **Phase 2 capacity:**
  - H014: used and rejected.
  - H015: not adopted before implementation (no slot used).
  - **1 of 3 slots consumed; 2 remain.**
- **Supporting files:**
  - `research/phase2/P2_opportunity_power.py/.json`: required-edge calculation from committed noise estimates; no market data.
  - The evidence table in §3.
  - Citations are from memory. They must be verified against the originals before any number is quoted, and no coefficient here is a claim of ours.

## Summary

- **Price-and-volume families are essentially exhausted.**
  - We have tested 14 hypotheses (H001–H014): every mainstream technical family that fits a long-only, ≥ $2B, weeks-to-months account.
  - None beat equal-weight by a margin that matters.
  - What remains in the technical space is a variation of what already failed.
- **The only genuinely distinct families with strong, pre-2010 evidence and a realistic point-in-time data path are fundamental:**
  1. **profitability/quality;**
  2. **net share issuance (buybacks minus issuance);**
  3. a **two-signal quality-plus-value composite.**
- **All three need a scope change.** CLAUDE.md currently limits selection to "technical price, volume and market-behaviour information only". All three also need a **point-in-time audit of QuantConnect's Morningstar fundamentals** first. Our own audits already found that some Morningstar fields describe **current**, not historical, status (D061), and that shares outstanding are restated for later splits.
- **The structural obstacle applies to every family.** To pass the fixed +0.25 margin with 80% probability over 12 years, a 12–19 stock book needs a **true Sharpe edge over equal-weight of about +0.36 to +0.40**. Published long-only, large-cap, after-cost edges are typically **smaller** than that, and they decay after publication.
- **My honest conclusion: stopping is a fully rational outcome.**
  - If you want one more attempt, the best one is **profitability/quality**, after a data audit and an explicit scope change.
  - If you want certainty of not wasting effort, **close Phase 2 with "No Production Candidate Found"**. A low-cost equal-weight or SPY index fund is then the rational choice for this account.

## 1. Families already sufficiently explored: do not revisit

| Family | Our test | Outcome |
|---|---|---|
| Short-term reversal / dip buying | H001 (C01, remedial re-test) | Rejected |
| 12-1 momentum | H002 | Rejected |
| 52-week-high proximity | H003 | Rejected |
| Pullbacks in momentum leaders | H004 | Rejected |
| Low volatility | H005 (S005 failed Validation) | Rejected |
| Breakout with volume | H006 | Rejected |
| Volatility squeeze | H007 | Rejected (robustness) |
| Residual (idiosyncratic) relative strength | H008 | Rejected |
| Volume shock | H009 | Rejected |
| Gap continuation | H010 | Rejected |
| Calendar-month seasonality | H011 | Rejected |
| Volatility-managed exposure | H012 | Removed (not evaluable with enough power) |
| Lottery-stock (MAX) avoidance | H013 | Rejected |
| Trend + RSI pullback + recovery | H014 | Rejected |
| MA200 trend filter / random uptrend | H015 analysis + H014 controls | Not adopted (pre-observed, ≈ +0.03) |

**Rule for the future:** any idea that is a threshold, window or combination change of these is a repackaging. That includes:
- defensive low-beta (it overlaps low volatility);
- sector or industry momentum (a momentum family);
- medium-horizon reversal (the reversal family, and it overlaps value).

## 2–7. The remaining families, assessed critically

**Legend:**
- **Evidence:** strength and timing of the external evidence.
- **PIT data:** whether point-in-time data exists in our QuantConnect setup.
- **Plausible +0.25?** My qualitative judgement of a path to G1. No claim without a backtest.

| Family | Rationale | Evidence (pre-2010?) | Survives costs? | Hold / turnover | PIT data in our setup | Distinct from tested? | Plausible +0.25? | Main risks |
|---|---|---|---|---|---|---|---|---|
| **A. Profitability / quality** (e.g. gross profits ÷ assets; low accruals; Piotroski F-score) | Profitable firms are under-priced relative to their cash generation (or are safer). Accruals signal low earnings quality | **Strong.** Sloan 1996 (accruals); Piotroski 2000; Fama & French 2006/2008; Novy-Marx 2013 (data 1963–2010); Asness, Frazzini & Pedersen QMJ (2013 WP). Data mostly pre-2010; Novy-Marx published 2013 | **Yes.** Slow-moving, annual/quarterly rebalance. Novy-Marx reports it works among large stocks | 6–12 months; turnover low (about 1–2× a year); costs well below 0.5% a year | **Probably.** Morningstar income statement and balance sheet in QC since about 1998. **Must audit:** filing-date lag, restatements, field coverage | **Fully** (no fundamental signal tested yet) | **Possible but uncertain.** Long-only top-bucket edge over EW plausibly +1–3% a year with defensive drawdowns. In Sharpe terms likely +0.1 to +0.3 | Publication decay (McLean & Pontiff 2016: anomaly returns fall substantially after publication). Definitional freedom (which quality measure): needs **one** pre-fixed measure. Data PIT |
| **B. Net share issuance / buybacks** | Firms issue stock when overvalued and buy back when undervalued; insiders time the market | **Strong.** Ikenberry, Lakonishok & Vermaelen 1995 (buybacks); Loughran & Ritter 1995 (issuers underperform); Daniel & Titman 2006; Pontiff & Woodgate 2008; Fama & French 2008 (robust in big stocks) | **Yes.** Annual signal, low turnover | About 12 months; turnover about 1× a year | **Probably, with care.** Needs shares outstanding at two dates. Our known quirk: share counts are split-adjusted to today. The ratio is valid if both dates are adjusted consistently, but this **must be audited** | **Fully** | **Uncertain to modest.** It mostly avoids heavy issuers (a short-side effect); the long-only buyback leg is weaker | The effect is concentrated in issuers (avoidance), so a long-only edge may be small. Share-count data quality |
| **C. Quality + value composite** (two signals, equal-rank) | Value (cheapness) and quality offset each other's failure modes ("quality at a reasonable price") | **Strong for each;** combination documented (Novy-Marx 2013; Asness et al.). Value: Fama & French 1992; Lakonishok, Shleifer & Vishny 1994 | **Yes,** low turnover | 6–12 months | As A, plus price ratios (simple) | **Fully** | **Uncertain.** Value had a widely known poor 2010–2020. Including it tilts against the known development period; excluding it because of that would be hindsight too. Disclose either way | Two signals = more freedom. Value's known recent history = contamination in both directions |
| D. Post-earnings announcement drift (PEAD) | Investors under-react to earnings news | Strong historically (Ball & Brown 1968; Bernard & Thomas 1989/1990). Weakening in large caps after the 2000s (Chordia et al. 2009; later caution: Martineau 2021, "Rest in peace PEAD") | Weak for large caps after costs | About 60 days; turnover moderate-high (event-driven, about 4 events per stock a year) | **Weak.** Exact announcement dates and consensus estimates are not in our subscription. Morningstar filing dates lag announcements by days to weeks, so the drift is partly missed. Paid event data would need your spending approval | Fully | **Unlikely:** a decayed effect in our universe, data mismatch | Data timing; a decayed effect |
| E. Analyst revisions / estimate momentum | Slow diffusion of analysts' information | Good historically (Womack 1996; Chan, Jegadeesh & Lakonishok 1996) | Moderate | 1–3 months | **Not available** in our setup: point-in-time estimates and revisions need paid datasets of uncertain history and survivorship | Fully | Cannot be validated | Data cost and PIT reliability: **downgraded out** |
| F. Defensive / low-beta (BAB) | Leverage-constrained investors overpay for high beta | Black, Jensen & Scholes 1972; Frazzini & Pedersen 2014 | Yes | Months | Yes (prices) | **No:** long-only it is close to low volatility (H005, failed) | Unlikely | Repackaging |
| G. Sector / industry relative strength | Industry-level momentum | Moskowitz & Grinblatt 1999 | Moderate | 1–6 months | Classification is likely **current, not point-in-time** (the same issue as D061); must be audited | **No** (momentum family) | Unlikely | Repackaging; data PIT |
| H. Medium/long-term reversal | Overreaction over 3–5 years | De Bondt & Thaler 1985 | Yes | 12+ months | Yes (prices) | Partly (overlaps value and the reversal family) | Unlikely | Weak post-1990 evidence; overlaps value |
| I. Seasonality | Calendar effects | Heston & Sadka 2008 | Mixed | — | Yes | **No** (H011, failed) | Unlikely | Repackaging |
| J. Portfolio-level risk overlay (index trend / volatility targeting) on a separately justified stock selection | Avoid long bear markets | Faber 2007; Moreira & Muir 2017 | Yes | Months | Yes | Partly (H012 removed; the H015 analysis covers the trend part) | **Not as an alpha source.** 2010–2021 has only one, V-shaped crash, so the test has almost no power | Hindsight about 2020; it cannot add +0.25 vs EW in this sample |

## 4. Data availability and implementation feasibility (our setup: QuantConnect + Morningstar + AlgoSeek + Security Master)

| Data | Available? | Point-in-time? | Known issues / what must be verified first |
|---|---|---|---|
| Prices, volumes, corporate actions | Yes | Yes (verified in C01–P2) | Dividend-factor last-digit difference (D097), immaterial |
| Market cap | Yes | Yes (our universe) | Audited in CP2 (E951) |
| Income-statement / balance-sheet items (gross profit, assets, accruals inputs) | Yes (Morningstar, about 1998+) | **To verify.** Values should appear as of the filing date, but restatement handling and the lag between period end and availability must be audited | **Required:** a fundamentals PIT audit (infrastructure run) before any design is frozen |
| Shares outstanding (for issuance) | Yes | **Partly.** Split-adjusted to today (CLAUDE.md quirk) | The issuance ratio must be computed consistently. Audit share-count continuity across splits and mergers |
| Sector / industry classification | Yes | **Doubtful** (current-status pattern, D061) | Downgrades family G |
| Earnings announcement dates | Not reliably (filing dates only) | — | Downgrades family D |
| Consensus estimates / revisions | No (paid) | — | Family E out unless you approve spending, and even then PIT is doubtful |

**Implementation complexity:**
- Families A–C need a new fundamentals layer in the harness: point-in-time snapshots on rebalance dates, with an availability lag.
- That is moderate engineering, plus new canaries for look-ahead in fundamentals. The classic failure is using a value before it was published.

## 5. Turnover and cost profile

| Family | Expected turnover | Expected costs ($100K, 15–19 positions) |
|---|---|---|
| A. Profitability / quality | About 1–2× a year | About 0.2–0.4% a year |
| B. Net issuance | About 1× a year | About 0.2% a year |
| C. Quality + value | About 1–2× a year | About 0.2–0.4% a year |
| D. PEAD | About 4–8× a year | About 1–2% a year |
| J. Overlay | Low | Low |

All of A–C sit comfortably below the 1.5% ceiling, and below everything we tested in Programme 1.

## 6. Statistical and economic potential (`research/phase2/P2_opportunity_power.json`)

| Positions | Selection noise (Sharpe sd) | True edge needed for 80% chance of passing +0.25 | False pass with no edge |
|---|---|---|---|
| 12 | 0.13 | +0.41 | 9.6% |
| 15 | 0.12 | +0.40 | 8.5% |
| 19 (most allowed at $100K by the $5,000 minimum) | 0.10 | +0.40 | 7.5% |
| 30 (needs ≥ about $150K) | 0.08 | +0.39 | 6.1% |
| If a strategy tracks EW twice as closely (e.g. a broad factor tilt), 12–50 positions | — | +0.33 to +0.37 | 0.4–5% |

**Reading:**
- Even a genuinely good strategy needs a true edge of about **+0.35 to +0.40 Sharpe** over equal-weight to pass reliably on 12 years.
- **Long-only, large-cap, after-cost factor edges in the literature are usually smaller,** especially after publication.
- So even the best family (A) has, in my judgement, **well under a 50% chance** of qualifying, even if the effect is real.
- This is a property of the +0.25 margin (which you approved and which should not be lowered) combined with 12 years of data and a concentrated account. It is not a defect of any family.

## 7. Major risks across families

1. **Scope change.** Fundamentals are outside the current technical-only scope and need your explicit approval.
2. **Point-in-time fundamentals.** Look-ahead through restated or late-arriving data is the classic failure of fundamental backtests. This needs a dedicated audit and canaries before any design is frozen.
3. **Definitional freedom.** "Quality" has dozens of definitions. Choosing one after looking would be a hidden parameter search: exactly **one** pre-fixed, literature-standard measure.
4. **Publication decay.** Most strong evidence was published before or during our development period. Returns after publication are typically materially lower (McLean & Pontiff 2016).
5. **Hindsight about 2010–2021 factor history** (e.g. value's well-known poor decade). It must be disclosed, and it must not steer the choice either way.
6. **Concentration.** 15–19 positions leave about ±0.10–0.12 Sharpe of selection luck.

## 8. Shortlist (at most 3): research families worth deeper design work

| Rank | Family | Independence | Evidence | PIT data | Edge after costs | Fit for $100K–$200K | Overfitting risk |
|---|---|---|---|---|---|---|---|
| **1** | **Profitability / quality** (one pre-fixed measure, e.g. gross profits ÷ assets) | High | Strong, mostly pre-2010 data | Probably, after an audit | Plausible but modest | Good (low turnover, few trades) | Moderate (definitional; mitigated by one fixed measure) |
| 2 | Net share issuance / buyback yield | High | Strong (robust in big stocks) | Probably, after a share-count audit | Modest long-only | Good | Low-moderate |
| 3 | Quality + value composite (two signals, equal ranks) | High | Strong per signal | As 1 | Uncertain (value's known recent history) | Good | Moderate-high (two signals; contamination both ways) |

**Downgraded out:**
- PEAD (data timing, decay);
- analyst revisions (data unavailable);
- low-beta, sector momentum, reversal, seasonality (repackaging);
- risk overlays (no alpha path vs EW in this sample).

## 9. Preferred family for possible H016 design

**Profitability/quality, using a single literature-standard measure fixed before any data is examined.**

- It is the **most independent** family from everything we have tested: the first fundamental signal.
- It has the **strongest and oldest** evidence, including in large stocks.
- It has the **lowest turnover and cost.**
- Its data path is **plausible in our current subscription** (no new spending), provided a point-in-time audit passes first.

**Even so:** in my judgement the probability that it clears +0.25 with an edge that is real is **well below 50%** (§6).

## 10. Reasons not to continue (they are strong)

1. **Fourteen hypotheses, no candidate.** Technical families are exhausted for this account shape.
2. **The bar is structurally high.** Passing +0.25 reliably needs about +0.35–0.40 true Sharpe edge over a passive equal-weight universe, more than most published long-only, large-cap, after-cost effects.
3. **The remaining credible families need a scope change, new infrastructure and a data audit.** Effort rises, while the plausible edge does not.
4. **Every further hypothesis raises the false-acceptance risk** of the Holdout process (the approved bound grows from ≤ 5.7% to ≤ 10.5% to ≤ 14.7%).
5. **The passive alternative is strong and cheap.**
   - Over 2010–2021, SPY earned a 0.91 Sharpe and equal-weight 0.80, before any research effort.
   - For a $100K–$200K personal account, a low-cost index fund captures that with negligible cost and no model risk.

**My overall view:**
- **Stopping Phase 2 with "No Production Candidate Found"** is a fully defensible, arguably the more rational, conclusion.
- If you value one final, well-founded attempt, the right one is the profitability/quality family. It requires:
  - an explicit fundamentals scope change;
  - a point-in-time data audit first;
  - an acceptance in advance that "not qualified" is the most likely result.

## 11. Exact owner decisions required next

1. **Direction:**
   - (a) **Close Phase 2: No Production Candidate Found.** Keep passive investing as the conclusion; Programme 1 and Phase 2 records are preserved.
   - (b) **Authorise design work** (still no backtest) for **one** shortlisted family. Recommended if continuing: profitability/quality.
   - (c) **Pause** without deciding.
2. **If (b):** approve the **scope change** permitting point-in-time **fundamental** data for stock selection. CLAUDE.md currently allows only technical price, volume and market-behaviour information.
3. **If (b):** approve a **fundamentals point-in-time data audit** as the first step. This is an infrastructure run, not a strategy test, and not a hypothesis slot. It checks filing-date availability, restatements, coverage and share-count continuity before any H016 rule is written.
4. **Confirm** the downgrades:
   - PEAD (data timing);
   - analyst revisions (data unavailable; no paid data);
   - repackaged technical families.
5. **Confirm** that the methodology (development 2010–2021, +0.25 margin, G1–G4, locked Holdout, budget 2 slots left) stays unchanged for any future hypothesis.

**STOP.** No H016 is defined, nothing is implemented, no backtest or diagnostic was run, and the Holdout stays locked.
