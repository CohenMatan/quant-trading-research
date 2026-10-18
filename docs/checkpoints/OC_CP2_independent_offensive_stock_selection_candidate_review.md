# OC-CP2 — Independent Offensive Stock-Selection Candidate Review

**Owner decision:** D247, 2026-10-18 (`docs/owner/2026-10-18_independent_offensive_stock_selection.md`).

**Nature:** candidate discovery and research design only. Evidence used:
- committed results and committed **non-return** aggregates (coverage, correlations, PIT audits);
- literature;
- analytical power equations (`research/longhorizon/oc_cp2/OC_CP2_power.py` → `OC_CP2_power.json`, built on the LH-CP4 equations).

Nothing else was done:
- no backtest, return, curve, real-stock signal, synthetic experiment or optimisation;
- no QuantConnect run, no purchase, no Holdout;
- no new active hypothesis; H028 unchanged; SYS-1 not run.

**Answer in one line:** one genuinely distinct, testable stock-selection candidate remains on our data.
- It is **OC-2 — profitability improvement (ΔROA)**: a single business-improvement signal, tested at the signal level over **118 monthly reviews (2012-02 → 2021-11)**.
- It is worth one disciplined test, but only **moderately powered**: about +4% a year top-quintile effects are usually detectable, about +2% a year effects are not.
- There is **no credible backup**. If OC-2 fails, the honest conclusion is that SPY is the offensive complement.

## In plain words

**What OC-CP1 got wrong.** OC-CP1 said every stock-selection family was exhausted. That is right for price-based ideas and for "quality / growth level" scores. It overstated the case for **business improvement**, for two reasons:
- **It never failed on the economics.** H029 was never return-tested. Its two significance tests were broken by the null method (D234–D237), and a broken null says nothing about the idea.
- **OC-CP1 shortened its window without need.** It assumed that a business-improvement signal must obey the 2015–2021 fiscal-label restriction made for OF-A (D245). Our frozen Data v3 signals do not use fiscal labels at all: they compare consecutive SEC quarters by date spacing. So the usable history is about ten years, not seven.

**What I recommend testing.** One signal, chosen now for non-return reasons: **the change in a company's return on assets over the past year** (trailing-twelve-month net income / assets now, minus the same a year earlier).
- **The idea.** Companies whose profitability is improving tend to keep improving, and prices are slow to price that in ("fundamental momentum"). This is one of the better-documented accounting anomalies.
- **Why it is new here.** Profitability *levels* (GP/A, cash-based profitability) failed in H016, H022 and H024. Profitability *change* was never tested. In committed data it is nearly uncorrelated with every feature H028 uses (|ρ| ≤ 0.18; LOWVOL −0.05).
- **The test.** A universe-wide cross-sectional test of whether the signal predicts next-month returns after controlling for sector, size, beta, low volatility, momentum, value, profitability level, asset growth and accruals. No portfolio and no permutation null.
- **Before it runs.** A frozen synthetic calibration must show that the test does not produce false positives.

**What the test can and cannot tell us.** The test uses about ten years of development data that earlier hypotheses have already examined.
- **A pass** would justify one standalone-portfolio test, and only then one combination test with H028. It would not prove an edge.
- **A failure** would close the stock-selection offensive search on existing data. SPY would then be the offensive complement.

## 1. Verified repository state and authorisation

| Item | State |
|---|---|
| `main` / working tree | 01d3828 (merge of [PR #111](https://github.com/CohenMatan/quant-trading-research/pull/111)); clean before this checkpoint |
| Latest owner decision before this one | D246 (OC-CP1), so this direction is **D247** |
| Holdout | Sealed: `HOLDOUT_UNLOCK.md` does not exist; 2022-01-01 → 2026-08-31 never accessed |
| H028 | REJECTED; "Frozen Defensive Research Reference" (descriptive, D241); unchanged |
| H029 / H030 | NOT EVALUABLE (never return-evaluated; D240) |
| OF-A | Unqualified; LH-CP4 = B — UNDERPOWERED FOR MODEST EFFECTS under the D245 population; the D245 exception is unchanged |
| SYS-1 | Proposed in OC-CP1 §19; **not approved, not run** (owner D247: "Do not proceed with SYS-1 yet") |
| Active hypothesis / experiment | None |
| Frozen protocols | Stage C ff97789b…, LH-CP2 f7cbac94…, LH-CP3 38d790e5… (rules 9a72c5c8…); all unchanged |

**Authorisation (D247):**
- **Approved:** candidate discovery and research design; one concrete test proposal; roadmap and ledger updates; a documentation-only PR.
- **Not approved:** backtests, returns, curves, real-stock signals, synthetic experiments, optimisation, reopening frozen hypotheses, changes to H028, SYS-1, the Holdout, purchases, or automatic advance.

## 2. Critical assessment of OC-CP1's "all families exhausted" conclusion

| OC-CP1 claim (§10) | Re-examination | Verdict |
|---|---|---|
| **A — Leadership / momentum is exhausted** | Price-based ideas were tested at the **signal level** with a valid, calibrated method: H019, 2011-01 → 2017-11, S1 12-1 momentum, top-decile excess −2.18% a year, IC t 0.22. They were also tested in portfolio, search and grammar form (H002–H004, H006–H011, H014, H018, H021-A, and MOM / HI52 in H024). This is an economic failure: the effect was absent, not mis-measured. 2018–2021 was never signal-tested for momentum, but MOM entered H026–H028, so that period is not unseen | **Stands.** No distinct price mechanism with an offensive rationale remains. That is a statement about ≥ $2B US stocks 2010–2021, not a proof that momentum cannot work |
| **B — Quality-growth is a duplicate** | Profitability and growth **levels** failed: H016 GP/A (Sharpe 0.69 vs EW 0.85); H022 composite (t_IC 0.48); H024 11 single features (best t 1.24 vs c_FEATURE 3.45). H024's high threshold came from searching 11 features / 415 models, so part of that failure is multiplicity. But no single level feature was even close, and H022's direct test had no search | **Stands for levels.** "Growth + confirmation" is either a level (weak or negative prior: growth stocks and high asset growth earn less) or a combination of old factors, which the owner excludes |
| **C — Business improvement: untested but limited to 2015–2021 and underpowered** | (i) H029 failed only on **methodology**: both nulls inadequate (D232, D234), and the third null was infeasible (D237). P14-CP6a showed these adequacy failures carry no information about H029 itself. (ii) The 2015–2021 limit was **imported by analogy** from OF-A (OC-CP1 §6: "as it should for consistency"). But D245 is scoped to OF-A (`STAGE_C_EXCEPTION_D245.json`: "future DESIGN CONSIDERATION"). OF-A's seasonal-surprise definitions need 13 fiscally labelled quarters. Data v3's H029 signals do not: they use consecutive SEC periods 80–100 days apart (Data v3 spec §5) and the frozen True-TTM fiscal-year reconciliation (D113). A fiscal-year change breaks the chain, and the signal is then **missing** (it fails safe). No fiscal label is used | **Overstated.** The mechanism is untested economically. Its PIT-safe window is about 2012–2021 (§4). It is the one family that deserves a fair test |
| **D — Other mechanisms weak or misaligned** | High beta: not alpha, and SPY supplies beta more cheaply. Equal weight: a weak size tilt. Earnings-announcement premium: distinct, but calendar-based and turnover-heavy (§5). Net issuance (F7): distinct and well documented, but a mature / repurchase (defensive-value) tilt, not an offensive one | **Stands**, with one honest note: these were set aside on rationale, not on evidence |

**Net correction:** OC-CP1's conclusion holds for two of the three serious families, but not for business improvement. The recommendation therefore changes from "SPY now" to "one disciplined business-improvement signal test first, SPY if it fails".

## 3. Previously tested versus genuinely untested mechanisms

| Family | What was tested | Failed economically | Failed on method / data | Never evaluated | Would duplicate | Genuinely untested and distinct |
|---|---|---|---|---|---|---|
| Price leadership / trend | H002 12-1; H003 52-week high; H004 pullback in leaders; H006 breakout; H007 squeeze; H008 residual; H009 volume shock; H010 gap; H011 seasonality; H014; H018 (1,533 configs); H019 S1–S3; H021-A sectors; H024 MOM / HI52 / REV1M | H019 (all three signals, valid method); H018 (p 0.31); H021-A (IC −0.011) | Early C01 / C02 portfolio screens were partly structural (D080: the no-skill book handicap) | Momentum signal-level on 2018–2021 | Any new lookback, skip, smoothing, residualisation, filter or confirmation | **None with an offensive rationale** |
| Profitability / quality levels | H016 GP/A; H022 Score v1; H023 weights; H024 GPA, CBOP, EQA, CFP, ACC | H016; H022; H024 | H024 multiplicity (11 / 415) | — | Any level composite | None |
| Growth levels | H022 revenue-growth layer (composite only); H024 AG | H022 composite; AG within H024 | — | Revenue-growth level as a standalone signal | H022 / H024 repackaging | Not distinct: the prior is weak or negative |
| Learned / defensive scores | H026–H028 (Ridge on the 11 features) | H026 D1 / D3; H027 A4; H028 B4 | Nulls structurally suspect (D238); repaired null not validated (D239) | — | Any learned re-weighting | None (H028 is the defensive reference) |
| Event-driven | H017 8-K reaction continuation; H025 insider clusters | H025 (t −0.93) | H017: direction right (W1 pass, CAGR 17.5% vs 14.9%), but evidence weak (W2 g/SE 0.71) and concentrated (74% in 2014–15). Restart forbidden (D128) | Earnings-announcement premium (calendar) | Any reaction-based drift | EAP: distinct, but not offensive (§5) |
| **Business improvement (fundamental momentum)** | H029 composite F1–F8 + H030 blend: **designed, never return-evaluated** | **None** | Both null designs inadequate; Null #3 infeasible (D232–D237) | **Every single signal and the composite** | The H029 composite / Top-K / null design (closed) | **Yes: one narrowly defined improvement signal, tested at the signal level** |
| Earnings surprise (OF-A C1–C6) | Data / PIT audits and power only (LH-CP1–CP4) | — | Fiscal-label chain (Stage C = C; exception D245) | All | — | Same economic family as business improvement; see §6 |
| Capital structure | F7 net issuance (H029 input only) | — | — | Standalone | — | Distinct, but defensive-value (§5) |

## 4. Existing-data coverage matrix

Coverage is the share of the non-financial eligible universe with a valid value, from committed **non-return** audits:
- P14-CP1 (`research/phase14/cp1/P14_CP1_audit.json`, Data v2.1 basis, yearly means of monthly values);
- P14-CP2 (`research/phase14/cp2/P14_CP2_audit.json`, Data v3, by period).

| Candidate | Fields (frozen definitions) | Earliest usable decision | Coverage | PIT status | Preparation needed | Statistical limit |
|---|---|---|---|---|---|---|
| **OC-2 ΔROA (F5)** | TTM net income, total assets (Data v3; guard v3 covers NI and TA) | **2012-02** (first review after which coverage stays ≥ 60%: rule in §10 item 5) | 2011 56%, 2012 62%, 2013 66%, 2014 78%, 2015–2021 76–84% (P14-CP1); Data v3: 62.8% / 81.7% / 80.6% for 2011–14 / 2015–17 / 2018–21; valid median 753 stocks / month (min 360) | Data v3 PASS: every PIT check 0. **Best vendor-vs-SEC agreement of all signals**: rank moves > 0.20 in 0.44% / 0.25% / 0.07% of stock-months by period | A signal-test host on the frozen Data v3 layer (aggregates only), controls from the frozen H024 feature store, plus one new control (252-session beta) | 118 reviews; §9 |
| F1-Q revenue acceleration | Quarterly revenue (guarded) | 2011 | 67% → 86% | PASS; vendor-vs-SEC rank moves 3.0–4.1% | Same | Not proposed (§6) |
| F2 gross-margin change | TTM GP, revenue | 2012–2013 | 49% → 75% | PASS; F2 vendor / SEC availability disagree often (vendor-only 4,320) | Same | Not proposed |
| F4 ΔOCF / assets | TTM OCF, TA | 2012 | 55% → 79% | PASS | Same | Not proposed (ρ with ACC 0.27, CBOP 0.25) |
| F8 Δasset turnover | TTM revenue, TA | 2012 | 55% → 80% | PASS | Same | Not proposed (ρ with AG 0.47) |
| F7 net issuance | SEC cover shares (split-restated) | 2012 (2011 32%) | 80–86% | PASS (F7 split test) | Same | Distinct but defensive (§5) |
| Earnings-announcement premium | Event Data v1 (88,723 8-K events 2010–2021; 93.9% coverage); expected month = the event ±1 year earlier | 2011 | ≈ 94% of eligible names | Frozen (D123); acceptance-time conventions (D122) | Expected-date rule and a host | Monthly rotation; costs (§5) |
| Momentum / trend | Prices | 2011 | ≈ 100% | Verified | — | Duplicate (§3) |

**Universe throughout:** the frozen Data v3 universe U_H029 = Data v2.1 eligible (≥ $2B PIT market cap, price ≥ $5, ADV20 ≥ $5M, US common stocks) minus SIC 6000–6999 and stocks without SIC.

**Hard constraint:** all inputs are QuantConnect Morningstar data or SEC data already frozen. Values never leave QuantConnect; only aggregate statistics are exported (compliance, D185).

## 5. The three serious families compared

The three families compared in detail are:
- **A**, business improvement;
- **B**, price leadership;
- **D**, other existing-data mechanisms (best representatives: the earnings-announcement premium and net issuance).

Family C (growth with confirmation) collapses into A (if it is a change) or into the rejected levels (§2), so it is not a separate serious family.

| Criterion (owner §5) | A — Business improvement (OC-2 ΔROA) | B — Price leadership | D1 — Earnings-announcement premium | D2 — Net issuance (F7) | Baseline — SPY |
|---|---|---|---|---|---|
| Source of return | Under-reaction to persistent operating improvement (Piotroski 2000; Balakrishnan, Bartov & Faurel 2010; Novy-Marx 2015; Hou, Xue & Zhang 2015 / 2020) | Under-reaction / herding | Announcement-risk or attention premium (Frazzini & Lamont 2007; Barber et al. 2013) | Managerial timing / undervaluation (Pontiff & Woodgate 2008; Fama & French 2008) | Equity risk premium |
| Market / style exposure | Near-neutral to H028's features: ρ LOWVOL −0.05, MOM 0.18, ACC −0.18, GPA 0.11, AG 0.08 (P14-CP1) | High beta in rallies | Neutral | Value / low growth / defensive | Beta 1 |
| Potential upside participation | Plausible (improving businesses; no low-volatility tilt), but not a design target and not yet measured | Plausible, but no edge on our data | Not targeted | Low | Full |
| Concentration risk | Moderate: cross-sector, earnings-season clustering | Sector / episode | Calendar | Sector | None |
| Turnover / costs | Quarterly signal; a book's one-way turnover is assumed to be about 1.5–3.5 a year; 0.6–1.4% a year for 15 names at $100K | High | Near-monthly rotation; about 2–3% a year or more at $100K | Low | ≈ 0.1% |
| PIT quality | Strongest of all fundamentals (§4) | Clean | Clean (frozen events) | Clean | — |
| Statistical detectability | 118 months; moderate (§9) | Tested; null | 131 months; but the premium concentrates in small stocks in the literature | 118 months | Not needed |
| Implementation effort | Medium: a new host on frozen layers | — | Medium-high | Medium | Minimal |
| Incremental value beyond beta | Possible: a distinct mechanism | Not found | Possible, but not offensive | Defensive, so a poor fit | None (it *is* beta) |
| **Assessment** | **Preferred** | Exhausted on our data | Not a fit for the owner's goals 3 and 6 | Not a fit for goal 3 | Baseline |

## 6. Preferred candidate: OC-2 — profitability improvement (ΔROA)

**Why one signal, and why this one.** The choice is made now, before any return, on non-return grounds only:
1. **Literature.** Change in profitability (ΔROA / ΔROE) is the most widely replicated single business-improvement variable. The F-score's ΔROA component, profit-announcement drift and Hou-Xue-Zhang's ΔROE all point the same way. Revenue acceleration (F1-Q) and gross-margin change (F2) have thinner single-variable evidence.
2. **Data quality.** F5 has the lowest vendor-vs-SEC disagreement of all six signals (§4). Net income and total assets are both guarded by guard v3.
3. **Distinctness.** Its largest |ρ| with any H024 / H028 feature is 0.18 (MOM, ACC). F8 is 0.47 with AG; F4 is 0.27 with ACC.
4. **Composite rejected.** The six-signal H029 score would reopen a closed hypothesis and add five choices. The owner asked for "one clearly motivated signal".

**Honest disclosures:**
- **Same family as OF-A C1 / C5** (earnings and gross-profit surprises; RM2 §11). OC-2 is the simpler construction: a TTM change scaled by assets, with no standardisation by 8 prior seasonal differences and no 13-quarter fiscal-label chain. **If OC-2 is approved, it should replace OF-A as the programme's single earnings-improvement test.** Testing both would be two looks at one idea.
- **Reuses an H029 input definition** (F5, frozen in Data v3 spec §5). H029's composite, Top-K portfolio, gates and nulls stay closed. No H029 return was ever computed, so no H029 result is being re-mined. Reusing the definition still needs the owner's explicit approval (CLAUDE.md: do not restart H026–H030).
- **Development data.** 2012–2021 has been examined by H022–H028. The candidate's motivation (the literature) is independent of those results, but the data are not fresh. A new name does not change that.
- **Large-cap decay.** Published anomalies weaken after publication (McLean & Pontiff 2016) and are weaker in large caps. A realistic prior is a small effect, which is exactly where power is thin (§9).

## 7. Why it might complement H028 (and what it cannot do)

- **Different source.** H028 earns (if at all) through low-volatility, defensive stock choice: beta 0.76, down-capture 0.69, its edge almost entirely in SPY-down months. OC-2's candidate source is firm-specific operating improvement, which is nearly uncorrelated with LOWVOL (−0.05).
- **Possible upside role.** A book of improving businesses has no built-in low-volatility tilt. It could therefore participate more in sustained rallies. This is a hypothesis about its exposure, to be **measured** later (up / down capture is a non-gating diagnostic), never a selection target.
- **What it cannot do:**
  - repair H028's failed validation (B4, D238 / D239);
  - make H028 a production component;
  - justify a combination on correlation alone.
- **Not used to select it:** H028's losing months or years, and correlation with H028's returns.

## 8. Why SPY remains the baseline

- **SPY is the bar.** It supplies the market's upside at about 0.1% a year, with no selection risk and no overfitting.
- **An individual-stock offensive sleeve must earn its complexity.** After costs it must beat SPY *beyond its beta*. That means positive excess return after controlling for market exposure, not merely a different return stream.
- **If OC-2 fails**, the recommendation returns to SPY (OC-1) and SYS-1 or option 2 of OC-CP1 §23.
- **If OC-2 passes the signal test**, SPY remains the comparator at every later stage (§10 item 10; §12).

## 9. Statistical feasibility and limitations

From `OC_CP2_power.json`: LH-CP4 equations; labelled assumptions σ_IC 0.06 / 0.09 / 0.12, σ_cs 6.5%, structure factor 1.336; no returns.

**80%-power minimum detectable effect (MDE), top-quintile excess a year. Main case σ_IC 0.09; figures are naive / with the realistic-structure factor:**

| Window (reviews) | ρ | One-sided 2.5% | **One-sided 1% (proposed)** |
|---|---|---|---|
| **2012-02 → 2021-11 (118)** | 0.1 | IC 0.026 → 2.8% / 3.8% | **IC 0.029 → 3.2% / 4.3%** |
| 2012-02 → 2021-11 (118) | 0.2 | 0.029 → 3.1% / 4.2% | 0.033 → 3.6% / 4.8% |
| OF-A 2015-01 → 2021-11 (83) | 0.1 | 0.031 → 3.4% / 4.5% | 0.035 → 3.9% / 5.2% |

**Power at a given true effect (118 reviews, ρ 0.1, one-sided 1%), naive / structure:**

| True effect | σ_IC 0.06 | σ_IC 0.09 | σ_IC 0.12 |
|---|---|---|---|
| +2% a year | — | 36% / 19% | — |
| **+3% a year** | 98% / 84% | **74% / 45%** | 45% / 25% |
| +4% a year | — | 95% / 73% | — |

**If only freshly updated signals carry information** (34% of stocks a month): power at +3% falls to about 9%.

**Reading:**
- The ten-year window improves on OF-A (power at +3%: 45% vs 31% with the structure factor), but it does not remove the limit.
- A **+4% a year** effect is usually detectable. **+3%** is a coin toss under realistic structure. **+2% is not detectable.** This is a limit of our history, not evidence against small effects.
- The test is worth running only if the owner accepts that a failure leaves effects of about +2–3% a year unresolved.

**Portfolio-level evidence is weaker still** (t ≈ e·√years / TE, 9.8 years): a +2% a year net edge at 6% tracking error gives t ≈ 1.0. No portfolio or combination test over our history can be significant. They are falsification and implementation checks.

**Stock-selection, portfolio and combination evidence are separate questions:**
- **OC-2** answers only the stock-selection question.
- **A later book** answers implementability and wealth.
- **A combination** answers incremental value.
- No stage can substitute for an earlier one.

## 10. Exact first test specification (OC-2; proposed, frozen only on approval; NOT run)

| # | Item | Specification |
|---|---|---|
| 1 | Economic mechanism | Prices under-react to persistent improvements in operating profitability. Improving return on assets partly persists, and the market updates slowly ("fundamental momentum"). Literature: §5 |
| 2 | Exact distinction | **Change** in profitability, not level (H016 / H022 / H024: GPA, CBOP, EQA, CFP, ACC). Accounting values, not a price reaction (H017). One signal at the universe level, not the H029 composite / Top-K / tether null. TTM / assets, not the OF-A seasonal surprise (OF-A is superseded if OC-2 is approved; §6). Not a lookback / filter variant of anything rejected |
| 3 | Why it could complement H028 | §7: a distinct, non-defensive source (ρ LOWVOL −0.05); upside exposure to be measured, never targeted |
| 4 | Data | Frozen **Data v3** (`data_freeze_v3.json`): True-TTM net income, total-assets snapshots, guard v3, M2 availability (max of first seen in QuantConnect's stream and SEC filing + 1 day). Frozen universe U_H029. Controls: frozen H024 definitions (LOWVOL, MOM, GPA, BM, AG, ACC), PIT log market cap, FF12 sector (SEC SIC). One new control: 252-session OLS beta against SPY (≥ 200 sessions; daily total returns). Response: the frozen `qr_p7_pred.response` conventions |
| 5 | PIT-safe research period | Decision reviews **2012-02-29 → 2021-11-30 (118)**; responses end 2021-12-31. Window rule fixed now from a committed non-return aggregate: the first review from which P14-CP1 F5-A coverage stays ≥ 60% (`OC_CP2_power.py::window_from_coverage`). Quarterly history from the frozen warm-up (≥ 2008-07-01). **D245 does not apply** (no fiscal labels; §2), which the owner must confirm. The 2015-01 → 2021-11 sub-window is a non-gating diagnostic. Holdout excluded |
| 6 | Signal definition | **F5 = NI_TTM(q0) / TA(q0) − NI_TTM(q4) / TA(q4)** exactly as Data v3 spec §5. The chain is consecutive visible reports 80–100 days apart; q0 ≤ 200 days old. Missing when any TTM or snapshot is missing or TA ≤ 0; never imputed. Converted to a cross-sectional percentile among valid stocks of U_H029 on the selection day. No winsorising (ranks), no sector neutralisation (sector is a control) |
| 7 | Update / holding frequency | Monthly review (month-end session; selection stamped the next calendar day; trade at the next open). A stock's signal changes when a new quarter becomes visible (about quarterly). The test response is one month. A later book would hold names while they stay in the top group (expected several months; not estimated) |
| 8 | Investability | U_H029 liquidity filters. Long-only. A later book: K = 15 equal weight at $100K (≈ $6,500 positions; D044 caps a $100K book at 15 names with a $5,000 minimum), sector cap, no leverage; K = 20 is possible at $200K (D083 S2 convention). Capacity is not a constraint at this size |
| 9 | Primary independent signal test | Monthly Fama–MacBeth cross-sectional regression of the demeaned next-month TSR on the F5 percentile with the item 4 controls (rank-transformed) and FF12 dummies. Statistic: t of the mean slope, **one-sided**, with the standard-error method (Newey–West, fixed lag, or stationary block bootstrap) **chosen by the frozen calibration (item 11) before any real data**. No identity-tether, permutation, matched-twin or factor-time-series significance test (D235, D238, D239) |
| 10 | SPY and style-matched benchmarks | Signal stage: the equal-weight universe (demeaning) and **style matching by regression controls** (sector, size, beta, LOWVOL, MOM, value, GPA, AG, ACC). Descriptive, non-gating: top-quintile raw return vs SPY and vs the universe; within-sector quintile spreads. A later book: SPY, the equal-weight universe, and a same-sector × size-quintile equal-weight basket (descriptive) |
| 11 | Required statistical calibration | A **Stage B-OC2 synthetic protocol**, frozen and hash-pinned before any synthetic result: the RM2 §13 scenarios relevant to a quarterly-refreshing accounting signal: S0, S1, S3, S4 (signal correlated with priced growth / profitability / MOM), S5 (noisy controls), S6 (time-varying premia, sector shocks), S7 (churn 0 / 1 / 2×), S8 (event-time updates, stale between), S10 (thin early coverage, heavy tails), plus planted P1–P3. Parameters only from committed non-return aggregates. **Hard size rule:** rejection ≤ 2.0% at nominal 1% and 3.5–6.5% at nominal 5% in every null scenario; ≥ 1,000 panels each. **Power is reported, not a pass mark**, except a feasibility floor: if the 50%-power effect exceeds +4% a year, STOP (uninformative). At most one pre-specified revision |
| 12 | Economically meaningful effect | Controls-adjusted top-quintile excess **≥ +3.0% a year before costs**. That is about +1.5–2.5% after the 0.6–1.4% a year cost of a 15-name book at $100K (item 14): the least that could justify a stock sleeve over SPY |
| 13 | Analytical power limitations | §9: 80% MDE ≈ 3.2% naive / 4.3% realistic at one-sided 1%; power at +3% ≈ 45–74%; +2% undetectable; fresh-only information is far weaker |
| 14 | Trading costs | $7 per order and 0.1% per side (programme standard). K = 15 at $100K: 0.6 / 1.0 / 1.4% a year; K = 20 at $200K: 0.5 / 0.9 / 1.2%; for one-way turnover 1.5 / 2.5 / 3.5 a year (assumed). The signal test is before costs; costs enter the economic gate (item 12) and every later stage |
| 15 | Stop / failure criteria | **PASS requires all of:** G1 t above the calibrated one-sided 1% threshold; G2 top-quintile adjusted excess ≥ +3.0% a year; G3 positive mean slope in both halves (2012-02 → 2016-12 and 2017-01 → 2021-11); G4 no calendar year supplies > 50% of the sum of monthly slopes (the H017 lesson). **Any failure = FAIL.** Pre-run STOPs: a calibration size failure or the feasibility floor (item 11); canary PIT audit ≠ 0; F5 coverage more than 5 points below P14-CP1 in any year; compliance rejection (D185); memory above the node limit |
| 16 | Multiple-testing treatment | One signal, one statistic, one window, one horizon, one SE method (fixed by calibration). F1-Q / F2 / F4 / F8 / F7 / the composite are **not** tested now or after a failure. One-sided α = 1% because of the programme's many prior looks at 2011–2021. Ledger entry before any result. Non-gating diagnostics cannot rescue a FAIL: SPY up / down months, the 2015–2021 sub-window, 2- / 3- / 6-month decay, fresh vs stale signals, sector-neutral IC, coverage bias |
| 17 | What would justify a combined-portfolio test | PASS G1–G4 → (separate approval) **one** pre-registered standalone book (K = 15 at $100K, monthly, a fixed entry / exit buffer, sector cap, costs). It must beat SPY in net terminal wealth, show positive excess beyond its beta (CAPM alpha point estimate > 0; descriptive) and beat the style-matched basket. Only then (separate approval) one combination with frozen H028 under §12 |
| 18 | What would stop this research line | G1 or G2 fails, or the calibration fails. Then the business-improvement family closes on existing data (no other F-signal, no composite, no OF-A surprise test unless the owner decides otherwise), and the offensive complement reverts to SPY (OC-1) |

**IDs on approval:** hypothesis H031 (assigned only when approved); synthetic protocol `research/longhorizon/oc2/`; host S033 / canary X033 (a subclass on the frozen Data v3 layer). Runs gated by `owner_approval_required`. Offline evaluation script committed before any real run.

**Run order on approval (each step needs its own approval):**
1. Stage B-OC2 protocol frozen → synthetic calibration → checkpoint → STOP.
2. Host + canary (coverage / PIT / determinism; no returns) → checkpoint → STOP.
3. ONE real evaluation → checkpoint → STOP.

## 11. Why not a backup: justified STOP

There is no second candidate that is both distinct and fit for the owner's goals:
- **Another business-improvement signal** after an OC-2 failure would be a second look at the same family (forking).
- **The H029 composite** reopens a closed hypothesis.
- **The earnings-announcement premium** is calendar-based, not an upside-participation mechanism, and turnover-heavy at $100K.
- **Net issuance** is a defensive-value tilt.
- **Price leadership** is exhausted (§2–§3).

**Recommendation if OC-2 fails or is not approved:** stop the stock-selection offensive search on existing data and adopt SPY (OC-1) as the offensive baseline. SYS-1 remains available as the account-level test of the defensive side.

## 12. Combined-portfolio requirements (for later; nothing here is authorised)

- **One account.** Real costs ($7 per order, 0.1% per side; 0.2% robustness) and aggregate limits (≤ 10% initial per position, sector caps across both sleeves, cash rules D051).
- **Comparators:**
  - SPY;
  - H028 alone;
  - OC-2 book alone;
  - H028 + SPY;
  - transparent defensive (LV15 or a verified USMV / SPLV) + SPY;
  - transparent defensive + OC-2 book;
  - and H028 + OC-2 book.
- **Weights.** Fixed ex-ante (50 / 50, the H030 / SYS-1 convention); never fitted. One weight policy only.
- **Minimum position feasibility** (D044: minimum $5,000 per new position; at most min(15, ⌊equity × (1 − buffer) / $5,000⌋) positions):

| Account | Sleeves | Names | Position size | Feasible? |
|---|---|---|---|---|
| $100K | 50% H028 (15) + 50% OC-2 (15) | 30 | $3,333 | **No** (size and the 15-name cap) |
| $100K | 50% H028 (15) + 50% SPY | 15 + ETF | $3,333 | **No** under D044 (this also affects SYS-1 P3 as specified in OC-CP1 §16) |
| $100K | OC-2 alone (15) | 15 | ≈ $6,500 | Yes |
| $200K | 50% H028 (15) + 50% OC-2 (15) | 30 | $6,667 | Position size yes; the 15-name cap needs an owner rule for two-sleeve accounts |
| $200K | 50% H028 (15) + 50% OC-2 (20) | 35 | $6,667 / $5,000 | Borderline (the cash buffer pushes the OC-2 sleeve below $5,000) |

**Reading:** a two-stock-sleeve account is feasible by position size at $200K, not at $100K. Either way it needs an owner rule on the D044 name cap, and at $100K also a lower minimum (or fewer names) for combination tests. Changing H028's K is excluded (Top-K fragility; H028 is frozen). This must be settled before any combination is pre-registered.

- **H028 constraints.** H028 is never modified and never a production component without independent evidence.

## 13. Governance

- **Development only.** Every result on 2012–2021 is development evidence; the data have been seen by H022–H028. Independent confirmation can only come from the sealed Holdout (one use, one frozen system, owner approval in `HOLDOUT_UNLOCK.md`) or genuine forward data.
- **Budget (RM2 §22, proposed).** OC-2 would use **one** of the ≤ 2 signal-hypothesis slots. Because it replaces OF-A, the second slot stays unused.
- **No invalid nulls.** No identity-tether, permutation, matched-twin or factor-time-series significance tests (D235, D238, D239).
- **No hindsight targets.** No H028 losing months or years and no 2018 / 2020 episodes used in design.
- **Ledger.** Row 6 of `research/longhorizon/SELECTION_LEDGER.md`, entered before any result.

## 14. Next explicit owner approval required

Choose one:
1. **Approve OC-2 for Stage B-OC2 only**: freeze the synthetic calibration protocol (§10 item 11), run the synthetic calibration offline, write a checkpoint, STOP. This requires four confirmations:
   - (a) reuse of the frozen Data v3 F5 definition as a single-signal test (not a restart of H029);
   - (b) D245 does not govern this construction (window 2012-02 → 2021-11);
   - (c) OC-2 supersedes OF-A as the single earnings-improvement test;
   - (d) acceptance of the §9 power limits (+2% a year effects are undetectable).
2. **Adopt SPY (OC-1) now** and close the stock-selection offensive search; SYS-1 or OC-CP1 option 2 then follows.
3. **Stop** the H028-complement line.

## 15. Recommendation

**Option 1: one disciplined, pre-calibrated test of OC-2 (profitability improvement), then STOP.**
- It is the only remaining stock-selection mechanism that is untested economically, distinct from every rejected family, supported by the strongest data layer we have, and testable over about ten years.
- It should be approved with open eyes: a pass is development evidence only, and a failure would leave effects below about +3% a year unresolved.
- If the owner prefers not to spend a signal slot on a moderately powered test, option 2 (SPY) is the defensible alternative.
