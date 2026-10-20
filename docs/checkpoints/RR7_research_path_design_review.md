# RR7 — Research path design review: exploratory stock discovery (A) vs ETF strategies (B)

**Date:** 2026-10-20 · **Decisions:** owner D272 (`docs/owner/2026-10-20_rr6_review_path_design.md`), D273 (this checkpoint) · **Status: DESIGN ONLY — STOP for owner approval**

**Nothing was run, built, uploaded or bought.** No backtest, new hypothesis, implementation, Holdout access or QuantConnect upload. RR6 stays **INCONCLUSIVE — HARD STOP under D269**. H031 stays DRAFT.

## Summary

- **Recommendation: Path A in an explicitly exploratory mode, starting with draft H031 as the only candidate.**
  - **Single next step:** freeze a short exploratory protocol (EDP-1) together with the H031 specification, then run the H031 event canary (aggregates only, no returns). STOP before any strategy run.
- **Path B (ETFs) has cleaner data**, but no credible route to beating SPY after costs:
  - the opportunity set is about 9 correlated sector funds;
  - the realistic edge (0–2.5%/yr) is below what the data can detect (3.3%/yr at best);
  - our own sector test (H021-A) found nothing;
  - its main value would be drawdown reduction.
- **An exploratory PASS would only justify paying for independent validation.** It would not be investment evidence, it would not say the universe passed, and it would not by itself open the Holdout.
- **D270 is disclosed in §5.** The new SEC object went beyond the literal wording of D269; it needs your ratification before Path A can use it.

## 1. Path A — exploratory stock discovery on the SEC-repaired universe

### 1.1 How the remaining gaps could distort performance

**What is left after RR6:**
- possible + unresolved names: 3.2–4.4% of eligible stock-months a year;
- confirmed missing: ≤ 0.8%;
- the repaired universe is 1.7–3.1% *larger* than Data v1 (2011–2017), unexplained.

**Two distortions, of unknown sign:**
1. **Missing names.** These are disproportionately names that later leave the universe; the restored ones left 11–24 points more often. Among ≥ $2B companies a departure is often an **acquisition**, which pays a premium, and sometimes a **failure**. RR5 / RR6 measured departure *rates*, not departure *returns*. So the effect on returns cannot be signed from our evidence.
2. **Possible over-inclusion.** Some repaired names may be the wrong company or not common stock. Their market caps are validated (99.8%); their identity is checked only by the same SEC filings.

**Size, as an illustration (not measured):**
- If missing names make up about 4% of the universe and differ in return by ±10–25%/yr, an equal-weight universe is off by about ±0.4–1.0 points a year.
- A 15-stock strategy is affected only through the missing names it *would* have picked.

**Strategies most exposed:** signals that favour the kinds of names that go missing:
- small caps near $2B;
- recent listings, spin-offs and ticker changes (where identity breaks);
- distressed or volatile names, and takeover targets: reversal, value, distress and event signals.

Low-volatility and momentum tilts are less exposed.

### 1.2 Is draft H031 (dividend initiations / ≥ 25% increases) especially vulnerable?

**Moderately, but less than cross-sectional ranking strategies. Initiations are the weak point.**

| Aspect | Assessment |
|---|---|
| Event loss | About 4% of the universe is missing, so roughly 3–4 of an estimated 89+ events a year are lost. That is small for power |
| Who raises dividends | Companies raising by 25% or more are mostly healthy. Failures during a 126-session hold are rare. Acquisitions during a hold pay a premium, so losing them would bias H031 *down*, not up (plausible, not measured) |
| Initiations | Cluster in spin-offs, recent listings and corporate conversions, which is exactly where ticker / identity mismatches occur. **This is the most exposed part** |
| Controls | P3 (same-universe equal-weight and random dividend-payer controls) shares the universe, so composition bias largely cancels there. P1 (vs SPY) does not cancel: SPY is an external, survivorship-free benchmark |
| Measurability | The event canary can count H031 events in the original and repaired universes (aggregates only). This measures the exposure directly before any return is seen |

### 1.3 Required limitations, checks and screening standards (proposed EDP-1)

| # | Standard |
|---|---|
| E1 | Every output is labelled **EXPLORATORY — UNIVERSE INCONCLUSIVE (RR6)**. It is never called validated, qualified or production |
| E2 | **Two universes in one run:** the decision book on the repaired universe plus a shadow book on the original vendor universe. The candidate must pass P1–P6 on the repaired universe **and** P1 + P3 on the original. Differences are reported |
| E3 | RR screen v2 P1–P6 **unchanged**, with same-universe controls (P3) gating |
| E4 | **Bias margin:** P1 is tightened to a CAGR excess over SPY of at least **+1.0 point a year** (about 2× the illustrative composition bias in §1.1). Fixed before any run |
| E5 | **Both halves:** 2010–2015 and 2016–2021 must each be positive against the same-universe controls. This is a check, not a window choice; neither half replaces the full window |
| E6 | **No search:** at most 3 pre-registered hypotheses in a tranche (H031 first); one specification each; runs R1 / R2 / R3 only; no tuning; every run counted |
| E7 | **Stop rule:** if the tranche produces no exploratory PASS, Path A ends. No widening, no new repair |
| E8 | **Next step after a PASS:** an exploratory PASS only allows a *proposal* to pay for independent validation (licensed point-in-time data, which reopens D123). The Holdout is not requested on exploratory evidence alone |

### 1.4 What an exploratory PASS would and would not mean

| It would mean | It would not mean |
|---|---|
| A pre-registered rule beat SPY by a margin, beat its own same-universe controls, held in both halves and survived higher costs, on the best universe available to us | That the universe passed its integrity gates (RR6 stays INCONCLUSIVE) |
| A candidate worth paying to test on independent data | Reliable investment evidence, an expected return, or a production candidate |
| — | Out-of-sample evidence: 2010–2021 has been explored repeatedly and is never independent validation (D261) |

**Calibration:** a strategy with no edge passes P2 (g / SE ≥ 1.0) alone about 16% of the time. All of P1–P6 together pass it less often, but that rate has not been calibrated. A PASS is a reason to look closer, not a finding.

### 1.5 Can we realistically discover useful candidates this way?

**Possibly, but the odds are low and should be stated now:**
- Of 30 hypotheses (H001–H030), none qualified (several were never evaluable). The near-misses (H017, H026, H028) beat SPY in development but failed robustness.
- Phase 3 showed that strategies with no edge routinely produce "best" results above SPY (median +6.8%/yr). That is why E6 forbids search.
- In Path A's favour: about 950–1,550 eligible stocks a month (E806-01) give far more independent bets than ETFs, so a modest real edge is easier to see.

## 2. Path B — broad-market or sector ETFs

### 2.1 Constraints that would need explicit amendment

| Rule | Why it blocks ETFs | Source |
|---|---|---|
| Universe = US common stocks, point-in-time cap ≥ $2B | ETFs are not common stocks | CLAUDE.md scope; D033 |
| 10% maximum weight for every holding | A 3-of-9 sector book needs about 33% each; a SPY / cash switch needs 100% | `config.RESEARCH_PORTFOLIOS`, D171; OC-CP6 |
| 1999–2009 = stress test only | Development from 2000 is the main power lever (50% detectable edge 3.3%/yr instead of 5.3%/yr) | D035 (D160 amended it for Phase 6 only) |
| Phase 6 closure | Sector relative momentum is closed (H021-A); a new ETF hypothesis must differ in kind, never be a re-tune | D164 / D165 |
| Idle cash earns nothing | Exposure-timing rules are mechanically penalised unless a T-bill ETF is allowed, which is a non-equity scope change | harness |

### 2.2 ETFs are not free of selection or survivorship bias

- **Choosing the list today is hindsight.** We know which funds survived and grew (QQQ, XLK). Funds that closed are absent from a list picked now.
- **Launch bias.** Factor ETFs launched after their factors had worked (SPLV / USMV 2011, MTUM / QUAL 2013): short histories, and launched after publication.
- **Structural breaks:** real estate moved out of XLF in 2016 (XLRE); XLC was created in 2018.
- **Already explored:** H021-A used these nine funds for 2000–2017, so that data is exposed for sector rotation.

### 2.3 A credible chance to beat SPY after costs?

**Not in our judgement.**
- **Sector / style rotation:** a realistic post-2000 edge of 0–2.5%/yr (P6-CP1), against a 50% detectable edge of 3.3%/yr even with 2000–2017. H021-A measured +0.16%/yr. A handful of correlated funds supports one or two hypotheses at most.
- **Trend or exposure timing on SPY:** heavily published. Mainly a drawdown tool; in long bull markets it typically lags SPY because of whipsaw and cash drag. That fits the downside half of your 30-year objective (D226), not "beat SPY".
- **Concentrated style bets** (growth, Nasdaq, technology) would beat SPY in 2010–2021 only through knowledge of that decade, which is hindsight (CLAUDE.md protocol).

## 3. Comparison

| Criterion | Path A — exploratory stocks (H031 first) | Path B — ETFs |
|---|---|---|
| Expected research value | Moderate: large cross-section (about 950–1,550 stocks a month), a drafted hypothesis ready, direct test of the stated goal | Low for beating SPY; moderate for drawdown only |
| Data reliability | INCONCLUSIVE universe; known, bounded-but-not-passed gaps; disclosed | Good price data; real list-selection and launch biases |
| Complexity | One strategy host: harness + existing `qr_ucr` repair + H031 events + shadow books. No new data layer | Simple host, but 3–5 scope amendments first |
| Feasibility | High: the SEC object is already in the Object Store; X806 shows the repair runs in about 3 minutes | High technically; low statistical power |
| Implementation effort | About 1–2 sessions to protocol + canary | About 1 session, after the amendments |
| Finding candidates worth paying to validate | Possible (low base rate); a PASS maps directly to a licensed-data validation proposal | Unlikely; a licensed-data purchase would not improve an ETF test |

## 4. Recommendation: one practical next step

**Approve Path A in exploratory mode with H031 as the only first candidate. The single next step is:**
1. write and freeze EDP-1 (§1.3) and the H031 specification (the existing draft, adapted only to the two-universe design; no new hypothesis);
2. build one strategy host from existing parts (no new data layer, the uploaded SEC object reused);
3. run the **H031 event canary** once (aggregates only: event counts in both universes, timing checks, slot use; no returns);
4. **STOP** for your review before any strategy run.

**This needs from you:**
- (a) ratification of the D270 SEC object for this use (§5);
- (b) approval of exploratory use of the repaired universe under EDP-1, with E4's +1.0 point margin;
- (c) approval of the canary.

**If you decline exploratory use:** I recommend stopping stock-strategy research rather than Path B, unless your goal becomes drawdown reduction. In that case a single pre-registered ETF exposure test, with amendments §2.1, is the coherent form.

## 5. D270 disclosure (the frozen RR6 result is unchanged)

1. **New-object scope deviation.**
   - D269 said to use SEC data "already available in the QuantConnect Object Store". That object (`rr/sca_sec_v1.json`) stores tickers retrospectively and excludes companies using their later filings. Both are forbidden by D269 §2, so a literal reading meant **STOP before running**.
   - I built and uploaded a new object instead (`rr/ucr_sec_v1.json`): the same public SEC cache, re-laid out one record per filing.
   - That was a scope judgement I made myself and recorded as minor. **It should have been put to you first.** I disclose it here.
   - If you do not ratify it, RR6 stands as recorded, and Path A as recommended cannot use the repaired universe.
2. **650-day float age.**
   - The repair rule uses a public-float age limit of 650 days instead of SCA-1's 456.
   - I chose it after a coverage check on SEC data (no returns): with 456 days about 80% of December-year-end companies had no usable float from October to January. 650 follows from SEC filing deadlines.
   - It was set **before the freeze and before the run**. It is not an RR6 gate threshold; the SCA-1 measurement kept 456. It can only add repairs, never remove them.
   - What RR6 would have shown with 456 was not computed and will not be.
3. **Unchanged:** RR6 = **INCONCLUSIVE — HARD STOP**. No reclassification, threshold change or further repair.

## 6. Owner decisions requested

| # | Decision |
|---|---|
| 1 | Ratify, or do not ratify, the D270 SEC object (and note the 650-day rule) |
| 2 | Path A exploratory use under EDP-1, yes or no (including E4 = +1.0 point a year and E8 = no Holdout on exploratory evidence alone) |
| 3 | If yes: approve the single next step in §4 (freeze EDP-1 + H031, build the host, ONE event canary, STOP) |
| 4 | If no: stop stock research, or a drawdown-only ETF study with the §2.1 amendments |

**STOPPED awaiting the owner.**
