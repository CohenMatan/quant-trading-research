# H028 Offensive Complement — Existing-Data Candidate Selection and Test Design (OC-CP1)

**Owner decision:** D246, 2026-10-18 (`docs/owner/2026-10-18_h028_offensive_complement_direction.md`).

**Nature:** design and candidate selection only. It uses committed evidence:
- no new return, backtest, null world, performance curve, optimisation or model;
- no purchase and no Holdout;
- no new active hypothesis.

**Recommendation in one line:** the evidence supports **SPY itself** as H028's offensive complement. **No stock-selection offensive candidate is currently credible enough to test.** I propose **one** executable account-level system test (SYS-1) that can falsify the "defensive sleeve + SPY" idea cheaply. It is development evidence only, and it stops the stock-selection offensive search on existing data.

## In plain words

**What H028 actually lacks.** H028 already keeps up with SPY in most rising months: up-capture 0.97. It lags only in the strongest months (0.87 when SPY rises 5% or more). Its whole advantage came from falling months, mostly 2018 and 2020. Its real weaknesses are therefore:
- it is unproven (its significance test was faulty, and it failed its own B4 gate);
- it is episodic;
- it is sensitive to the number of stocks held;
- it trades a lot.

An "offensive" sleeve cannot fix those.

**Why stock selection is not the answer.** To add upside participation without giving up wealth, an offensive sleeve needs either:
- more market exposure, which SPY gives almost for free; or
- genuine stock-selection skill.

Thirty hypotheses on this universe and period found no validated stock-selection skill: momentum, trend, quality, growth, profitability, value-type scores, learned scores, earnings events and insider buying. The one untested idea (business improvement, H029) is limited by data and power. A seventh year of momentum or a repackaged quality score would repeat a known failure.

**What I propose instead.** Treat SPY as the offensive sleeve. Then run one cheap, honest test of whether a defensive sleeve added to SPY is worth its complexity at the level of a real account with real costs:
- the defensive sleeve is H028, a transparent low-volatility rule, or a low-volatility ETF;
- the comparison controls for the lower market exposure the defensive sleeve brings.

**How to read the result.** Because H028's 2015–2021 history is already known, a *pass* would not prove anything. A *fail* would be decisive and would let us stop the H028-based system.

## 1. Verified current project state

| Item | State |
|---|---|
| `main` / working tree | 70b1d7d (merge of [PR #110](https://github.com/CohenMatan/quant-trading-research/pull/110)); clean |
| Latest owner decision | **D245**, so this checkpoint is **D246** |
| Holdout | Sealed (`HOLDOUT_UNLOCK.md` does not exist); 2022-01-01 → 2026-08-31 never accessed |
| H028 | REJECTED (B4 failed; conditional-null p structurally suspect, D238; repaired null not validated, D239). Descriptive label "Frozen Defensive Research Reference" (D241) |
| H029 / H030 | NOT EVALUABLE (never return-evaluated) |
| OF-A | Unqualified. D245 exception (2015–2021 verified L0 / L1 labels, rule V) unchanged; LH-CP4 = **B — UNDERPOWERED FOR MODEST EFFECTS** |
| Active hypothesis / experiment | None |
| Frozen protocols | Stage C ff97789b…, LH-CP2 f7cbac94…, LH-CP3 38d790e5… (rules 9a72c5c8…); all unchanged |

## 2. Exact owner authorisation

Recorded verbatim in `docs/owner/2026-10-18_h028_offensive_complement_direction.md`.

- **Approved:** a design and candidate-selection checkpoint; inspection of committed evidence; a frozen test proposal; roadmap and ledger updates; a documentation-only PR.
- **Not approved:** any new real-return experiment, backtest, null world, performance curve, optimisation, model, purchase, Holdout access, gate change, or reopening of rejected hypotheses.

## 3. H028 structural weakness map (every row verified against committed artifacts)

Sources:
- E030-05 (`research/phase13/cp1/P13_CP1_result.json`);
- P13-CP2 / CP3 / CP4 post-mortems;
- RM2 §4.

All figures are 2015–2021 development data.

**Structural (style-driven)**

| Weakness | Evidence | Verdict |
|---|---|---|
| Lower market beta | Beta 0.76 (LV15 0.53) | Real |
| Weak participation in *strong* rallies | Up-capture 0.97 overall, 0.94 in SPY ≥ +2% months, **0.87 in SPY ≥ +5% months** (won 4 of 12). Up months as a whole contributed **−27%** of relative log wealth | Real but **modest**. Average upside participation is near-full |
| Low-volatility / conservative tilt | LOWVOL-factor regression: alpha 3.3% a year, t 1.26, R² 0.29 | Real. Most of the style is LOWVOL-like, and the residual is not significant |
| Limited growth / momentum exposure | Not measured: holdings and exposures were never exported (P13-CP2) | **Unverified.** It is plausible from the LOWVOL tilt, but no artifact shows it |

**Construction**

| Weakness | Evidence | Verdict |
|---|---|---|
| Top-15 concentration / Top-K fragility | S_WEALTH 0.224 (Top-15) versus 0.095 (Top-10) and 0.062 (Top-20) | Real and serious |
| Turnover and cost | 63% of equity a month (about 7.4–7.8× a year); about 0.8–1.7% of equity a year in costs; $5,789 commissions over 7 years | Real |
| Monthly rebalancing / sector cap | Frozen rules; no artifact isolates their effect | Not separable from committed evidence |

**Historical observations (not economic laws)**

| Observation | Evidence |
|---|---|
| Excess from SPY-down months | 127% of relative log wealth; March 2020 alone 49% of S_WEALTH |
| Episode dependence | Without 2018 + 2020: −1.39 points a year versus SPY; synthetic leave-both-out ahead in only 9.3% of paths |
| Calendar years ahead of SPY | 3 of 7 (2017, 2018, 2020) |

**What follows from the map.**
1. H028's upside shortfall is a style consequence of low beta and low volatility. It can be offset by **more market exposure**, and no new alpha is needed for that.
2. H028's serious problems are a non-validated edge, episode dependence, Top-K fragility and turnover. An offensive sleeve **cannot** repair them.
3. No row may be used as an optimisation target, in particular H028's losing years 2015, 2016, 2019 and 2021.

## 4. H028 historical limitations and qualification status

- **Status:** REJECTED (B4: trailed LV15 over 2015–2017, Σ log-relative −0.006; D220).
- **Significance:** B1's p ≈ 0.0004 is not reliable evidence. The conditional null used pointer-tether donors, with about 17.6% re-pairing a month under churn (D238). A repaired exposure-matched null was infeasible (D239).
- **Design history:** post-hoc. It was motivated by H026 / H027 on 2011–2021 (D217).
- **Trading window:** only 2015-01 → 2021-12 (84 months), because the learned score needs earlier training years.
- **Usage:** H028 is a development reference and comparator only. It is never production and never a Holdout candidate without a separate owner decision.

## 5. Inventory of existing research data (verified)

| Source | Coverage | Status | Notes |
|---|---|---|---|
| QuantConnect US equity prices (raw bars + split / dividend feeds) | ETFs from 1998; stocks 1998+ | Usable (default build 18179, digest-verified policy) | Universe eligibility needs market cap, which is **absent before Oct 2009**, so stock research starts in 2010 |
| SPY | 1998+ | Verified (DB1; every H0xx comparison) | — |
| Nine original Select Sector SPDRs | 1998-12-22+ | Verified (E988-01) | XLRE 2015, XLC 2018 |
| QQQ | Listed in QuantConnect's universe from 1999+ (E951 audits) | Present; **price history not yet verified in a run** | — |
| SPLV / USMV / QUAL / T-bill ETF | 2011 / 2011 / 2013 / ? | **[GAP] not verified in QuantConnect** (RM2 DB3 / DB6 / DB7) | Must be verified in a canary before use |
| E981-01 PIT eligible universe (Data v1 denominator) | 2010–2021 monthly masks | Committed | ≥ $2B, price ≥ $5, ADV20 ≥ $5M |
| Data v1 | 2010–2017 | Frozen; **not reproducible** on the default build (D183) | Historical only |
| Data v2 / Data v2.1 | 2011–2017 / **2011–2021** | Frozen (v2.1 owner exception D213) | Universe, identity, SEC SIC, fundamentals, H024 / H026 feature store |
| Data v3 | 2011–2021 | Frozen (H029 guard v3) | Coverage ≥ 5 of 6 signals 76.1% |
| Event Data v1 (8-K earnings events) | 2010–2021 | Frozen (88,723 events) | H017 |
| SEC caches (companyfacts, submissions, XBRL index) | ≤ 2021 (cut-off loaders) | Local, re-acquirable | LH-CP1–CP3 |
| D245 verified fiscal-label population | 2015–2021 | Prospective exception | OF-A only |
| Committed monthly H028 / LV15 / SPY returns | 2015–2021 (84 months) | Committed (P13-CP3 / CP4 inputs) | Development; already examined |

## 6. Existing-data historical coverage by candidate family

| Family | Data | Earliest valid decision | Monthly decisions to 2021-11 | Constraint |
|---|---|---|---|---|
| A Sustained leadership (price) | QuantConnect prices + Data v2.1 universe | 2011-01 (12-1 needs 13 months) | **131** | None, but the family was already tested (§7) |
| B Quality growth | Data v2.1 fundamentals + prices | 2011-01 (2011 coverage thinner) | 131 | Repackaging risk |
| C Fundamental improvement | Data v3 quarterly flows | **2015-01** if the D245 verified-label rule applies to quarterly comparisons, as it should for consistency (LH-CP1–CP4) | **83** | LH-CP4: underpowered for modest effects |
| D1 High-beta tilt | Prices + universe | 2011-01 | 131 | No alpha mechanism (§8) |
| D2 Equal-weight universe | Universe | 2011-01 | 131 | Weak mechanism |
| D3 Earnings-announcement premium | Event Data v1 | 2011-01 | 131 | Not an upside-participation mechanism |
| OC-1 SPY / QQQ exposure | ETF prices | 1999 (prices); research window 2015–2021 for H028 combinations | 84 | None |

## 7. Review of prior relevant hypotheses

All periods are development or IS data; "economics" means a valid test found no edge.

| Family | Hypotheses | Rationale | Period | Evaluated? | Status | Failure type | Relevance to complementarity |
|---|---|---|---|---|---|---|---|
| Momentum / trend / leadership | H002 12-1 momentum; H003 52-week high; H004 pullbacks in leaders; H008 residual momentum; H014 trend + pullback; H018 1,533-config technical search; H019 S1 momentum / S2 smooth momentum / S3 trend factor; H021-A sector momentum; H024 MOM / HI52 features | Under-reaction, information diffusion | 2010–2017 (H014 2010–2021; H021-A 2000–2017) | Yes | REJECTED / no signal qualified | **Economics:** H019 top-decile S1 −2.18% a year, IC t 0.22; H018 p 0.31; H021-A IC −0.011 | Directly relevant, and **exhausted**: plain, residual, smooth, trend-factor, 52-week-high, sector and technical variants all failed |
| Quality / profitability / growth | H016 GP/A top-20; H022 Score v1 (technical + GP/A, cash conversion, equity/assets, revenue growth, sector); H023 weights; H024 11 features / 415 models | Profitability premium, quality growth | 2010–2021 (H016); 2011–2017 (H022–H024) | Yes | REJECTED / closed | **Economics:** H016 Sharpe 0.69 vs EW 0.85; H022 t_IC 0.48; H024 best model t 2.48 (null p 0.35) | Family B **is** this space; "quality growth + confirmation" ≈ Score v1 |
| Learned / defensive | H026 Ridge Top-15; H027 LOWVOL-controlled; H028 λ = 100 | Learned combination | 2011–2021 (portfolio 2015–2021) | Yes | REJECTED | **Gates + method:** D3 / A4 / B4 fail; nulls structurally suspect | The defensive reference itself |
| Low volatility / lottery | H005; H013 | Low-volatility anomaly | IS 2010–2017; VAL 2018–2021 (H005) | Yes | REJECTED | Economics (H005 failed Validation) | Same style as H028, not a complement |
| Event-driven | H017 8-K earnings continuation; H025 insider clusters | Post-event drift; insider information | 2010–2021 (H017); 2011–2017 (H025) | Yes | REJECTED | H017: W1 **pass** (CAGR 17.5% vs 14.9%) but W2 evidence fail (g/SE 0.71) and R3 concentration (74% in 2014–15); H025 t −0.93 | H017 was the closest to an offensive profile. It cannot be restarted (D128) |
| Business improvement | H029 F1–F8; H030 50/50 with H028 | Fundamental momentum | 2011–2021 (planned) | **No** | **NOT EVALUABLE** (nulls inadequate) | **Methodology**, not economics | The only untested mechanism (Family C); data- and power-limited |
| Exposure management | H012 volatility-managed exposure | Volatility timing | — | No | REMOVED (power) | — | Regime-type rules are excluded by owner §8 |

**Failed significance-testing approaches to avoid** (owner §13):
- identity-tether / pointer permutation nulls (D235, D238);
- matched twins (D239);
- time-series factor regression as the significance test (R3 miscalibration, D239).

## 8. Candidate families and their economic mechanisms

- **A — Sustained leadership.** Momentum / trend persistence through institutional demand and slow diffusion. Its mechanism raises upside participation in trending markets.
- **B — Quality-growth participation.** Profitable growers compound in expansions. Mechanism: the profitability and growth premia.
- **C — Fundamental improvement.** Accelerating revenue, margins and cash flow; "fundamental momentum" (Novy-Marx 2015) under-reacted by prices.
- **D1 — High-beta tilt.** More market sensitivity. CAPM says higher beta means a higher expected return, but the low-beta anomaly (betting-against-beta) says high-beta stocks earn *less* than their beta implies.
- **D2 — Equal-weight universe.** Size / rebalancing premium within large caps.
- **D3 — Earnings-announcement premium.** Higher returns in scheduled announcement months: risk or attention.
- **OC-1 — Market exposure (SPY).** The equity risk premium, the most durable documented return mechanism. **QQQ** is a growth / technology-concentrated variant without a separate premium theory.

## 9. Why each might complement H028

| Family | Complement argument | Counter-argument |
|---|---|---|
| A | High up-capture in trending rallies, opposite to LOWVOL | Our own tests found no momentum edge in ≥ $2B US stocks 2010–2017; a seventh variant is forking |
| B | Growth exposure H028 lacks | It *is* Score v1 / H024 territory; repackaging |
| C | Cyclical / growth exposure plus a distinct (fundamental) mechanism | Untested, but the data window is 2015–2021 and LH-CP4 shows low power; H029's null problems |
| D1 | Directly raises beta | Beta is cheaper through SPY; high-beta stocks historically lose risk-adjusted value; no alpha mechanism |
| D2 | Broader participation | Weak, period-dependent mechanism; no strong prior for ≥ $2B stocks |
| D3 | Distinct mechanism | Does not target bull-market participation; event-driven costs |
| **OC-1 SPY** | **Restores exactly the missing beta; zero selection risk; near-zero cost** | Adds no alpha, which is also its virtue: it cannot fail through overfitting |
| QQQ | Higher beta and growth tilt | Choosing it is **hindsight-tainted**: its 2010–2021 technology leadership is known. Comparison only |

## 10. Prior failure and duplication analysis

- **A** is exhausted. H002, H003, H004, H008, H014, H018, H019 S1–S3, H021-A and H024 MOM / HI52 cover plain, residual, smooth, 52-week-high, trend-factor, technical-grammar and sector momentum. Any new momentum test would be **a restart of rejected hypotheses** (owner §11), not a new mechanism.
- **B** is a duplicate. H016, H022 and H024 together contain profitability (GP/A, CBOP), growth (Score v1 revenue growth, asset growth), quality (equity/assets, accruals) and market confirmation (trend / momentum layers).
- **C** is the only genuinely untested mechanism. H029's F1–F8 definitions were frozen before any return was seen, and no H029 / H030 performance was ever computed. But:
  - reusing them needs an explicit owner decision (CLAUDE.md: do not restart H026–H030);
  - the same quarterly-comparability rules apply (D245 → 2015–2021);
  - the analytical power is LH-CP4's;
  - and H029's null failures show that a valid inference method is still missing.
- **D1 / D2 / D3** have weak or misaligned mechanisms (§9).
- **Conclusion:** **no genuinely distinct, adequately powered stock-selection offensive candidate remains on existing data.** C is the only defensible backup, conditionally.

## 11. Simple SPY / QQQ offensive baseline

- **SPY** supplies broad market participation (beta 1) at about 0.09% a year expense and minimal trading.
- **The arithmetic of a 50 / 50 combination.** The committed capture ratios imply, by linear arithmetic (an illustration, **not a backtest or estimate**), an up-capture of about 0.98 and a down-capture of about 0.84 for H028 + SPY. The combination therefore gives up roughly half of H028's downside protection in exchange for a small gain in upside participation. Whether the *wealth* trade-off is favourable depends on H028's unvalidated edge. That is exactly what the system test must check at the account level.
- **Bar for any stock-selection offensive sleeve.** It must beat SPY *after costs and beyond its beta*. Nothing in our evidence meets that bar.
- **QQQ** is a transparent growth comparison. Because its 2010–2021 dominance is public knowledge, it is **non-gating** and cannot be selected in this cycle.

## 12. Transparent defensive alternatives (RM2 DB1–DB7)

| ID | Benchmark | Availability |
|---|---|---|
| DB1 | SPY | Verified |
| DB2 | **LV15** (15 lowest 60-day-volatility eligible stocks, sector cap 3, same costs) | Frozen rule; 2015–2021 in the H027 / H028 hosts; can be built from 2011 |
| DB3 | SPLV / USMV ETF | **[GAP] to verify** |
| DB4 | 50 / 50 SPY + DB3 | As DB3 |
| DB5 | SPY + DB3 at an ex-ante beta target (round number, e.g. 0.8; never H028's 0.76) | As DB3 |
| DB7 | **SPY + cash (or a verified T-bill ETF) at a fixed beta-matched weight** | Cash always; T-bill ETF **[GAP]** |

DB7 and DB5 are the right controls for any claim that a defensive sleeve adds value, because they remove the "lower beta" explanation (RM2 §6).

## 13. Comparative feasibility matrix

| Criterion | A | B | C | D1 | D2 | D3 | **OC-1 SPY** |
|---|---|---|---|---|---|---|---|
| Addresses a structural H028 weakness (upside) | Yes | Partly | Partly | Yes | Partly | No | **Yes** |
| Distinct from H028's mechanism | Yes | Partly | Yes | Yes | Partly | Yes | **Yes (beta)** |
| Not already tested / rejected | **No** | **No** | Yes (not evaluable) | Mostly | Yes | Yes | n/a |
| Data available, long window | 131 months | 131 months | **83 months** | 131 months | 131 months | 131 months | **Yes** |
| Valid inference available | No (needs calibration) | No | No (needs Stage B) | No | No | No | **Not needed** (no alpha claim) |
| Power for a modest effect (≈ 2–3% a year) | Low (§15) | Low | **Very low** | Low | Low | Low | n/a |
| Implementation cost | Medium-high | Medium | Medium | Medium | High (≈ 900 names) | High | **Minimal** |
| Overfitting risk | High (forking) | High | Medium | Low | Medium | Medium | **None** |
| **Rank** | 5 | 6 | **2 (backup)** | 4 | 7 | 8 | **1 (preferred)** |

## 14. Preferred candidate and optional backup

### Preferred: OC-1 — Market-exposure completion with SPY

| # | Item | Answer |
|---|---|---|
| 1 | Mechanism | The equity risk premium; SPY restores the beta that a defensive sleeve gives up |
| 2 | H028 weakness addressed | Low beta → lagging strong rallies (0.87 capture at SPY ≥ +5%). SPY raises the combined beta toward 1 |
| 3 | Data | QuantConnect SPY prices (verified); H028 sleeve = frozen S030 rules on Data v2.1 |
| 4 | Earliest decision | 2015-01 (H028 sleeve). Transparent-only arms could start 2011-01 (diagnostic) |
| 5 | PIT | SPY: none beyond next-open execution. Sleeve: the frozen H028 / LV15 PIT rules |
| 6 | Overlap | No new hypothesis. It is the "H028 + SPY" combination listed by the owner (§7 item 3). It differs from H030 (H028 + H029) |
| 7 | Horizon | Buy-and-hold SPY sleeve, rebalanced monthly to the target weight |
| 8 | Turnover | SPY sleeve: tiny cash-absorption trades. Sleeve: about half of H028's account-level turnover |
| 9 | Complexity | Low: a wrapper around the frozen sleeve |
| 10 | Power | No alpha claim, so no power requirement for SPY. The **system's** advantage over beta-matched SPY is statistically undetectable in 7 years (§15). Evidence will be economic and consistency-based, not significance-based |
| 11 | False success | Lower beta during falls (2018, 2020), or H028's episodic edge |
| 12 | Falsification | The H028 + SPY system fails to beat beta-matched SPY + cash, or a transparent defensive + SPY, net of costs, on the very data where H028 looked best |
| 13 | Better than SPY alone? | Only if the defensive sleeve adds value **beyond its beta**. That is the test |
| 14 | First test | **SYS-1** (§19) |

### Optional backup (not started): OC-B — Fundamental improvement as a stock-selection offensive signal

- **Signal:** H029's frozen F1–F8 definitions (never return-evaluated), as a signal-level test.
- **Data and period:** Data v3; the D245-consistent verified population, 2015–2021, 83 months.
- **Inference:** universe-wide Fama–MacBeth with controls (RM2 §12).
- **Preconditions:**
  1. An explicit owner decision to reuse H029's definitions; this is not a restart of H029's portfolio test.
  2. Stage B synthetic calibration first (§20).
  3. Acceptance of LH-CP4's power limits: the 80% MDE is about 3.4–6.7% a year top-quintile.
- **Ranking:** second, because it is the only untested mechanism. Not recommended now.

## 15. Statistical-power limitations

These come from the LH-CP4 equations (`lh_cp4_power.py`), on the same labelled assumptions: σ_IC 0.09, σ_cs 6.5%, normal-theory conversion.

**Stock-signal tests, 80%-power MDE (top-quintile excess a year, naive / with the P7-CP4 structure factor 1.34):**

| Window | ρ | 5%, 1 hypothesis | 1%, 2 hypotheses |
|---|---|---|---|
| 2011–2021 (131 months; families A / B / D) | 0.1 | IC 0.025 → 2.7% / 3.6% | 0.032 → 3.5% / 4.7% |
| 2011–2021 | 0.2 | 0.027 → 3.0% / 4.0% | 0.036 → 3.9% / 5.2% |
| 2015–2021 (83 months; family C) | 0.1 | 0.031 → 3.4% / 4.5% | 0.041 → 4.5% / 6.0% |

**Reading.**
- The 2011–2021 history halves the problem, but only for families A / B / D, and those are exhausted or weak.
- For family C the window is 83 months, with about 28 earnings-season bursts.
- **A modest durable edge (1–2% a year) is not detectable in any family.** That is a limitation of our history, not proof that no such edge exists.

**System-level (portfolio) tests** have t ≈ e·√years / TE:

| Net edge e | TE 3% | TE 4% | TE 6% |
|---|---|---|---|
| 1% a year | 0.88 | 0.66 | 0.44 |
| 1.5% | 1.32 | 0.99 | 0.66 |
| 2% | 1.76 | 1.32 | 0.88 |

These are for 7 years. Eleven years would multiply each figure by about 1.25.

No system-level comparison over our history can reach conventional significance. SYS-1 is therefore designed as a **falsification and implementation** test, not a significance test.

**Stock-months versus time.** About 830–1,000 stocks a month make tens of thousands of stock-months, but inference rests on **84–131 monthly cross-sections**. Market and sector shocks are common to all stocks.

## 16. Portfolio construction and costs (for SYS-1)

- **One account.** The defensive sleeve's position sizing uses **50% of account equity** as its equity basis (frozen H028 / LV15 internal rules unchanged: Top-15, sector cap 3, 10% initial cap, no resizing). **SPY holds the remainder.**
- **Rebalancing.** At each monthly review (next-open execution), SPY trades only to absorb the sleeve's net cash. The sleeve's own trades follow its frozen rules.
- **Weights.** 50 / 50 is a fixed, equal capital split: prospective and not optimised (the same convention as H030). The beta-matched control weight uses a round ex-ante sleeve beta of 0.8 (RM2 DB5 rule; never H028's measured 0.76): 0.5 × 0.8 + 0.5 × 1.0 = **0.9**, so the control is 90% SPY + 10% cash.
- **Costs.** $7 per order and 0.10% per side on every net trade. A 0.20% per side robustness check (as A6 / B6).
- **Overlap.** SPY contains the sleeve's stocks (implicit overlap, disclosed). There is no netting of ETF against stock positions.
- **Expected cost order of magnitude.** About half of H028's 0.8–1.7% a year at the account level, plus small SPY trades. This is an illustration from committed turnover, not an estimate.

## 17. Measures of complementarity (pre-specified; one market-state definition)

Market state = sign of SPY's monthly total return (up / down). A single "strong" bucket (SPY ≥ +5%) is a diagnostic only.

Reported per portfolio:
- terminal wealth and CAGR;
- wealth ratio versus SPY and versus the beta-matched control;
- up-capture and down-capture (mean-ratio definition, P11-CP2);
- strong-up capture (diagnostic);
- beta;
- correlation of sleeve returns with SPY and with each other;
- maximum and relative drawdown;
- net contribution of each sleeve;
- turnover and costs;
- share of excess from SPY-down months;
- largest single calendar-year share of the excess;
- 2015–2017 and 2018–2021 sub-period sums;
- 36-month rolling share ahead.

Correlation alone is never treated as complementarity.

## 18. Prospective qualification gates (two separate questions)

**Q-STANDALONE (signal value).**
- SPY makes no alpha claim, so the question is not applicable.
- The H028 sleeve's standalone status stays **REJECTED**. SYS-1 cannot requalify it.
- A future stock-selection offensive candidate (OC-B) would need its own calibrated signal-level gate (§20). Portfolio diversification can never establish that alpha.

**Q-PORTFOLIO (incremental system value; development, non-qualifying).** All must hold for the class **DEVELOPMENT-CONSISTENT**:

| Gate | Criterion |
|---|---|
| P-1 | Net terminal wealth of the H028 + SPY system > SPY |
| P-2 | System > the beta-matched control (90% SPY + 10% cash) |
| P-3 | System > LV15 + SPY **and** > USMV-or-SPLV + SPY (the ETF named before the run; if neither is available, P-3 uses LV15 only and says so) |
| P-4 | Not episodic: no single calendar year supplies > 50% of Σ yearly log-relative (system vs control), **and** Σ 2015–2017 > 0 **and** Σ 2018–2021 > 0 |
| P-5 | P-1 and P-2 still hold at 0.20% slippage per side |

- **Any failure:** the class is **NOT SUPPORTED**.
- **Neither class is automatically decisive.** Both go to owner review (owner §9).

## 19. One minimal real-data test plan — SYS-1 (proposed, frozen on approval; NOT run)

| Element | Specification |
|---|---|
| Question | Does a defensive sleeve + SPY, in one account with real costs, beat SPY and a beta-matched SPY + cash control? And does H028's complexity beat transparent defensive sleeves? |
| Period | 2015-01-02 → 2021-12-31 (84 monthly reviews; H028's frozen window). Data end enforced at 2021-12-31 |
| Universe | Frozen Data v2.1 eligible universe (≥ $2B, price ≥ $5, ADV20 ≥ $5M, US common stocks, financials as in H028); ETFs SPY, QQQ, SPLV / USMV, T-bill ETF if verified |
| Signals | None new. H028 = frozen S030 (λ = 100, Top-15). LV15 = frozen `qr_h027.lv15_scores` |
| Timestamps | Frozen H028 PIT rules (decision at month-end review, next-open execution) |
| Unit of analysis | Account-level monthly total returns per portfolio |
| Portfolios (gating) | P1 SPY; P2 H028 alone (reference; must reproduce E030-05); **P3 50% H028 + 50% SPY**; P4 50% LV15 + 50% SPY; P5 50% USMV-or-SPLV + 50% SPY; P6 90% SPY + 10% cash (beta-matched control) |
| Portfolios (non-gating) | P7 QQQ alone; P8 50% H028 + 50% QQQ (hindsight-tainted comparison); P9 $200K capital for P3; P10 2011–2014 transparent arm (LV15 + SPY vs 90 / 10) |
| Inference | **No significance claim.** Amendment 3's W2 evidence ratio (frozen stationary bootstrap, block 126; D121) is reported **descriptively**. No permutation, tether or twin nulls (D235, D238, D239) |
| Primary criterion | Q-PORTFOLIO gates P-1 to P-5 (§18) |
| Economically meaningful effect | System versus control: at least +1% a year net, reported. Not a gate, because it is undetectable statistically |
| Costs | $7 per order, 0.10% per side (0.20% robustness); $100K |
| Negative controls | P6 (beta-matched, no selection); P4 / P5 (transparent defensive); P2 replay equality |
| Robustness | 0.20% slippage; $200K; 2015–2017 / 2018–2021 sums; QQQ substitution (non-gating) |
| Canary first | (i) P2 reproduces E030-05 within the D218 tolerance table; (ii) P1 reproduces SPY $262,325; (iii) ETF availability (prices only; no data export); (iv) memory ≤ the node limit; (v) file count ≤ 50 (S030 is already at the limit, so the wrapper must not add files beyond it) |
| Stop conditions | Canary failure → STOP and report; any compliance rejection → STOP (D185); gate result → STOP (no tuning, no weight or K changes, no extra arms) |
| Multiple testing | One gating system (P3) against fixed comparators, gated as an intersection; no variants or weight grid; QQQ arms are non-gating and cannot be selected; reruns only for logged technical failure |
| IDs (on approval) | Host S032 (subclass wrapper of frozen S030 / S029); canary X032; runs E032-01 … ; configs gated by `owner_approval_required`; offline evaluation script committed before any run |
| Separate owner approval needed for | The run itself; any Holdout use; any change of weights / K / sleeves; OC-B; reuse of H029 definitions |
| Interpretation | **NOT SUPPORTED** → stop the H028-based system; the evidence then favours SPY alone (or a transparent defensive sleeve). **DEVELOPMENT-CONSISTENT** → necessary, not sufficient (in-sample, H028 favoured by hindsight). It only allows an owner decision on freezing **one** system for a single-use Holdout confirmation |

**What SYS-1 can establish against owner §13:**

| Owner question | SYS-1 |
|---|---|
| Mechanism exists | The beta mechanism is given |
| Upside participation | Measured |
| Not duplicating SPY / H028 | P6 / P4 / P5 isolate selection versus beta |
| Plausible net wealth | P-1 / P-2 with costs |
| Justifies combined evaluation | It *is* the combined evaluation, at the account level |

## 20. Required statistical-validation prerequisites

- **SYS-1:** none. It makes no significance claim, so no null calibration is needed. This avoids the D238 / D239 failure modes by design.
- **W2 ratio.** The W2 ratio is reused only descriptively. Its calibration was done for single-strategy wealth gaps (Amendment 3, D121); its limitation is low power and no factor control.
- **OC-B (backup) would need, before any real-data run:**
  - a frozen Stage B protocol (RM2 §13–14): S0–S10 null scenarios including priced, correlated LOWVOL / growth / profitability, noisy controls, churn and event-time updates;
  - rejection rates at nominal 1% / 5% within bounds;
  - planted-effect power;
  - a declared economically meaningful effect.

## 21. Multiple-testing controls

- One gating system. Fixed comparators. Intersection gates with no α-spending across variants, because no variant selection exists.
- Non-gating arms (QQQ, $200K, 2011–2014) cannot be promoted.
- **Programme-level disclosure:** 2015–2021 has been examined by H026–H028, and its two dominant episodes are known. SYS-1's development verdict carries that reuse. The budget (RM2: ≤ 2 signal hypotheses, 1 standalone portfolio, 1 combination, ≤ 1 Holdout candidate) is unchanged. SYS-1 would consume the **combination** slot.

## 22. Explicit Holdout protection

- The SYS-1 data end is 2021-12-31, enforced in the configuration and checked post-run.
- The Holdout (2022-01-01 → 2026-08-31) stays sealed. It may be used once, only for **one** frozen system, only after a written owner approval recorded in `HOLDOUT_UNLOCK.md`.
- **Holdout power.** At 4.7 years and TE 3–4%, a 1.5% a year edge gives t ≈ 0.8–1.1. A Holdout pass would be consistency evidence, not proof. The owner should decide in advance what a Holdout result would change.

## 23. Exact next owner approval needed

Choose one:
1. **Approve SYS-1 as specified** (§19): canary X032 → E032 runs P1–P10 → offline evaluation (script committed first) → checkpoint → STOP. Optionally name the ETF for P5 in advance (USMV preferred, SPLV fallback, verified in the canary).
2. **Adopt OC-1 (SPY) as the offensive complement without testing** and close the offensive stock-selection search on existing data. Next step: a design-only decision on whether any defensive sleeve is worth evaluating at all.
3. **Approve the backup OC-B path instead.** This needs a decision to reuse H029's frozen F1–F8 definitions plus a Stage B synthetic calibration first, accepting LH-CP4's power limits.
4. **Stop** the H028-complement line.

## 24. Recommendation

**PROCEED with SYS-1 only, and STOP the search for a stock-selection offensive alpha sleeve on existing data.**

**Why SYS-1:**
- It is cheap: about 9–11 QuantConnect runs on the existing $24 a month subscription.
- It is executable at the account level, with real costs.
- It is free of the null-calibration traps.
- It answers the decision that actually matters: is a defensive sleeve + SPY better than SPY, and better than beta-matched SPY, after costs?

**Why its value is asymmetric:**
- a **failure** on H028's most favourable data would close the H028-based system honestly;
- a **pass** would only justify asking for one frozen system's single-use Holdout confirmation.

**Why stop the stock-selection search:** thirty hypotheses found no validated stock-selection edge in this universe and period. The remaining families are exhausted, duplicative, weak or underpowered. Forcing a new one would mostly test our luck.

---

**Counts.** Hypotheses tested: 0. Strategies: 0. Experiments: 0. No new hypothesis registered (SYS-1 / S032 are proposals). Network requests: 0.

**STOPPED — awaiting owner review.**
