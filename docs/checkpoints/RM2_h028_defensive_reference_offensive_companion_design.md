# H028 Defensive Reference + Offensive Companion — Long-Horizon Architecture Design

**Owner decision D241, 2026-10-18. DESIGN ONLY.** The message is recorded verbatim in `docs/owner/2026-10-18_h028_defensive_reference_offensive_companion.md`.

**Nothing was run for this checkpoint:**
- no backtest;
- no synthetic experiment;
- no null world;
- no QuantConnect run;
- no H028 recalculation;
- no Ridge fit;
- no signal computed;
- no data purchased;
- no Holdout access.

No frozen result, gate, threshold, data manifest or implementation changed. **H028 remains REJECTED. No candidate exists. The Holdout remains sealed.**

**Labels used throughout:**

| Label | Meaning |
|---|---|
| **[V]** | Verified repository record (source given) |
| **[L]** | Published literature, checked for this checkpoint by web search (bibliographic details only; findings as stated in abstracts or the committed reviews) |
| **[I]** | My interpretation or arithmetic |
| **[P]** | A proposal that needs owner approval |
| **[GAP]** | Source material missing; nothing invented |

This document extends the D240 roadmap (`docs/checkpoints/RM1_long_term_defensive_offensive_equity_roadmap.md`). Where they overlap, this one is more specific; nothing in RM1 is withdrawn.

---

## 1. Verified current project status [V]

| Item | State | Source |
|---|---|---|
| `main` before this checkpoint | `d7fbe6b` (merge of PR #105, D240); working branch identical; tree clean | git |
| Last decision before this one | D240 | `DECISIONS.md` |
| Experiments | 580 rows, last E031-09; unchanged | `experiments/INDEX.csv` |
| Phases 13 and 14 | **CLOSED** | D240; `docs/checkpoints/RC1_research_cycle_closure_phases_13_14.md` |
| H028 | **REJECTED** (B4 failed; conditional-null p structurally suspect; repaired null not validated) | D220, D238, D239, D240 |
| H029 / H030 | **NOT EVALUABLE — NO VALID REAL-DATA EVALUATION** (historical BLOCKED) | D232, D234, D237, D240 |
| Production candidate | **None** | D240 |
| Active hypothesis / experiment | **None** | `research/hypotheses/STATUS.md` |
| Holdout 2022-01-01 → 2026-08-31 | **Sealed**; never accessed; no `HOLDOUT_UNLOCK.md` | git |
| Session checks | QuantConnect credentials present (values never printed); site reachable | session start |

Governance rules in force and relevant here:
- prospective research standard (D226);
- no data purchase before a promising result on existing data (D124);
- the post-2017 hindsight rule (`CLAUDE.md`, Research protocol);
- no daemon or scheduler (scope);
- the QuantConnect compliance rule against data-validation exports (D185).

## 2. Owner approval and exact scope [V]

**Approved (D241):** a design-only checkpoint for a three-part architecture:
1. frozen H028 as a defensive research reference;
2. an independently motivated offensive stock-selection strategy;
3. a future combined portfolio.

Allowed for this checkpoint:
- recording the instruction;
- reviewing committed documentation and published research;
- this checkpoint and roadmap updates;
- a documentation-only PR.

**Not approved:**
- H031;
- any backtest, synthetic experiment or null world;
- recalculating H028 from real data or retraining its Ridge;
- modifying H028;
- training or implementing OF-A;
- implementing a combined portfolio;
- Holdout access or data purchase;
- changing frozen gates or results;
- reopening Phase 13 or 14.

**Designation:** H028 is called the **Frozen Defensive Research Reference (FDRR)**. This is a descriptive label only. Its qualification status stays REJECTED, and it must not be used in production.

## 3. Frozen H028 specification and formal status [V]

| Element | Frozen value | Source |
|---|---|---|
| Specification | `research/phase13/H028_spec.md`, hash-pinned in `qresearch.p13h028` (with `qr_h028`, the S030 host, the null tolerance table and c_WEALTH_H028 = 0.0561) | D217–D219 |
| Data | Data v2.1 (manifest SHA-256 `ef0a7a66…`, D207; owner exception D213); ends 2021-12-31 | D207, D213 |
| Features | The 11 H024 features with their PIT formulas (`qr_h024`): MOM, LOWVOL, GPA, ACC, BM, AG, REV1M, CBOP, HI52, CFP, EQA | H026 spec §3 |
| Transform | Within-review percentile, x = 2p − 1 | H026 spec §3 |
| Target | 63-session TSR minus SPY TSR, cross-sectionally rank-transformed; a label enters training only if its exit session is before the cutoff | H026 spec §4 |
| Model | Monthly-equal-weighted Ridge, all 11 features, **λ = 100 fixed**, one fit per outer year at that year's first decision review on all prior available labels | H028 spec §3 |
| Portfolio | Top-15 by score, at most 3 per FF12 sector, equity/15 initial size (≤ 10%), held names kept without trimming, monthly review, next-open execution, fractional shares, cash if fewer than 15 | H026 spec §7 |
| Costs | $7 per order plus 0.10% slippage per side | H026 spec §7 |
| Evaluation | Outer years 2015–2021; $100,000 against SPY total return with the same dates and costs | H028 spec §3 |
| Real result | E030-05 | P13-CP1 |

**Formal status:** REJECTED (D220). The status is permanent and unchanged by D238–D241.

**What "frozen" means for any future use [I]:**
- The frozen object is the **procedure**, including its annual λ = 100 refit on the labels available at each cutoff. No final coefficient vector was ever fitted: H028 spec §12 only allowed that after all gates passed.
- Running the frozen procedure on any post-2021 data would therefore mean:
  - a blind Data v2.1 extension;
  - new refits under the unchanged rules.
- That is a **new evaluation of H028** and needs its own owner approval. It is not authorised now.

## 4. H028's historical economic behaviour (development data only) [V]

Source: `research/phase13/cp1/P13_CP1_result.json` (E030-05), P13-CP2, P13-CP3 and P13-CP4.

| Metric, 2015–2021 | H028 | SPY | LV15 (frozen control) |
|---|---|---|---|
| Terminal wealth | $328,295 | $262,325 | $220,156 |
| CAGR | 18.5% | 14.8% | 11.9% |
| Volatility | 16.2% | 17.7% | 11.0% |
| Max drawdown | −26.1% | −33.7% | −16.5% |
| Beta (monthly) | 0.76 | 1.00 | 0.53 |
| Up-capture | 0.97 | 1.00 | 0.62 |
| Down-capture | 0.69 | 1.00 | 0.41 |
| Calendar years ahead of SPY | 3 of 7 (2017, 2018, 2020) | — | — |

The owner's table in the D241 message matches these records.

**Where the excess came from:**
- **SPY-down months.** They supplied 127% of the relative log wealth; up months contributed −27% (P13-CP4).
- **March 2020 alone** supplied 49% of S_WEALTH.
- **Strong up months.** In SPY's strongest months H028 lagged: up-capture 0.87 in months of +5% or more, and only 4 of 12 such months were won (P13-CP4).
- **Without 2018 and 2020:** up-capture 0.90, down-capture 0.81, and −1.39 points a year versus SPY (P13-CP4 Q5).

**Rolling windows ahead of SPY (P13-CP4):**
- 12-month windows: 58%.
- 36-month windows: 92%.
- 60-month windows: 100%, but every 60-month window contains 2018.

**Synthetic year-block bootstrap (P13-CP3, conditional diagnostics, not probabilities):**
- H028 ahead of SPY in 78 / 89 / 97 / 99% of paths at 5 / 10 / 20 / 30 years.
- With 2018 and 2020 both left out: 9.3%.
- Median longest losing streak: 5 years.

**Sensitivity to the number of holdings** (frozen non-gating diagnostic in E030-05):

| Book | S_WEALTH | Terminal wealth |
|---|---|---|
| Top-15 | 0.224 | $328,295 |
| Top-10 | 0.095 | $288,585 |
| Top-20 | 0.062 | $279,089 |

**Trading:**
- Monthly turnover averaged 63% of equity, about 7.4–7.8 times a year in 2016–2020.
- Commissions plus slippage were about $1,600–2,500 a year (`equality.per_year`). [I] That is about 0.8–1.7% of average equity a year at this capital.
- Total commissions over 2015–2021: $5,789.

**Factor regression:** on a LOWVOL factor the annualised alpha was 3.3% (t 1.26, R² 0.29, n = 84).

## 5. Reasons H028 is not validated [V / I]

1. **It failed its own pre-registered gate B4.** Over 2015–2017 it trailed LV15 (Σ log-relative −0.006; D220). The gate is not relaxed (owner §2).
2. **Its significance is unreliable.**
   - B1's p ≈ 0.0004 came from a conditional null whose persistent donor pairing re-forms about 17.6% of pairs a month under churn. That penalises null worlds structurally (D238).
   - Null worlds also drew the ten other features marginally, giving up-capture 0.71 against real 0.97 (P13-CP6 §5).
3. **A repaired, exposure-matched null was infeasible.** A concentrated Top-15 sits in the joint tail of the controlled exposures (D239). The factor-regression fallback was miscalibrated: 14% false rejections at nominal 1% when growth and profitability are priced.
4. **It was designed post-hoc on seen data.** H028 was explicitly motivated by H026 and H027 results on 2011–2021 (D217). It is development evidence only.
5. **Its result is episodic.** The excess comes from two already-observed episodes (2018, 2020). [I] Seven years contain too few independent down-market episodes to establish a persistent asymmetry.
6. **It is fragile to an arbitrary construction choice.** S falls from 0.224 to 0.095 at Top-10 and to 0.062 at Top-20 (§4). [I] A robust selection edge would not be so sensitive to K.
7. **No independent data has ever been used.** The Holdout is sealed, and Data v2.1 ends 2021-12-31.

## 6. What would establish genuine defensive value [P]

"Defensive value" must be split into two claims, because they need different evidence:

| Claim | What it means | How to test it | Cheapest alternative |
|---|---|---|---|
| D-1 Defensive profile | Lower beta, shallower drawdowns, down-capture below 1 | Descriptive; needs several independent down-market episodes | A low-volatility ETF or SPY + cash at the same ex-ante beta gives this at about 0.1% a year |
| D-2 Asymmetric capture beyond the profile | Up-capture minus down-capture higher than transparent alternatives **at comparable beta**, i.e. stock-selection value | Comparison against beta-comparable transparent benchmarks on data not used to design it | None: this is the only part that could justify H028's complexity |

**Evidence that would establish D-2 (proposal):**
- **On independent data only:** the Holdout (single use), properly audited pre-2010 data, or forward paper trading. Never 2011–2021.
- **The comparisons:**
  - S(H028 vs SPY) > 0;
  - **and** S(H028 vs DB5, the beta-target SPY + low-vol ETF) > 0;
  - **and** S(H028 vs DB7, SPY + cash at the same ex-ante beta) > 0.
- **Spread across episodes:** the asymmetry must hold over **at least two separate down-market episodes**, defined mechanically (for example, SPY at least 15% below its running peak), not by name.
- **No single episode** may supply more than a pre-set share of S. A proposed 50%, the same form as H026's D3.

**Honest limit [I]:**
- Against a beta-matched benchmark the tracking error is plausibly 6–10% a year.
- With the 4.7-year Holdout, the standard error of the annualised excess is then about 3–5% a year.
- So the Holdout **can contradict** D-2 but **cannot confirm** a modest D-2.
- The most the available data can give is "not contradicted, plus economically consistent".

**Hindsight risk [I]:** the Holdout contains a widely known bear market (2022). Any defensive test designed now is designed with public knowledge of that. Per `CLAUDE.md` this counts as a design contamination, and must be disclosed in any Holdout result.

**Practical consequence [I]:** unless D-2 is supported on independent data, a transparent defensive ETF sleeve is preferable to H028. It delivers D-1 at near-zero cost and complexity, which answers owner §11.

## 7. Transparent defensive alternatives [V / L / P]

| ID | Benchmark | Inception / availability | Role |
|---|---|---|---|
| DB1 | SPY buy-and-hold, total return | QuantConnect, 1998+ [V] | Primary benchmark |
| DB2 | LV15: frozen H027 rule (15 lowest 60-day-volatility eligible stocks, sector cap 3, same costs) | Data v2.1, 2011–2021 [V] | Stock-level low-volatility control |
| DB3a | SPLV (Invesco S&P 500 Low Volatility) | 2011-05-05 [L: third-party listings] | Investable low-volatility ETF |
| DB3b | USMV (iShares MSCI USA Min Vol Factor) | 2011-10-18 [L: third-party listing] | Investable minimum-volatility ETF |
| DB4 | Fixed 50/50 SPY + one pre-named DB3 ETF, annual rebalance | From the later inception | Simple combined benchmark |
| DB5 | SPY + DB3 mix to an **ex-ante beta target**, e.g. 0.8 (a round number, never H028's 0.76) | As DB3 | Separates beta from selection |
| DB6 | QUAL (iShares MSCI USA Quality Factor) | 2013-07-16 (some listings say 07-18) [L] | Quality-exposure benchmark |
| DB7 (new) | SPY + T-bill ETF at a fixed 80/20, annual rebalance | T-bill ETF availability in QuantConnect **[GAP: not verified]** | The plainest beta-matched benchmark: lower exposure, no factor tilt |

**Rules [P]:**
- **Weights and rebalance are fixed before any use.** Nothing is optimised retrospectively.
- **Verify before any test:**
  - each ETF's QuantConnect data;
  - corporate actions and dividends;
  - exact inception dates against the prospectus.
- **No back-filled index history** (index values from before an ETF's launch) may stand in for an investable benchmark. Such histories are themselves constructed with hindsight.
- **Overlap with the evaluation window [I]:** these ETFs cover only part of 2011 and all of 2012–2021. Before 2011 none exists, so the pre-2010 alternative (RM1 §10) could use only DB1, DB2-type stock-level rules and DB7.
- **Primary defensive comparator [I]:** for any defensive claim it should be **DB5 or DB7**, because they control beta. LV15 is extreme (beta 0.53, up-capture 0.62) and is better used as a factor control than as the bar.

## 8. OF-A economic hypothesis [L / I]

**Claim:** investors under-react to the *persistence* of news in newly reported fundamentals. When a firm's newly filed quarter departs strongly from what its own earlier public statements implied, returns continue in the same direction over the following one to three quarters.

**Supporting literature [L]:**

*Committed references (P2-CP3 table, family D; H017 proposal P2-CP13 §2):*
- Ball & Brown (1968);
- Bernard & Thomas (1989, 1990): earnings changes are positively autocorrelated at lags 1–3, and prices behave as if they were not;
- Chan, Jegadeesh & Lakonishok (1996);
- Brandt et al. (2008);
- limited attention: Hirshleifer, Lim & Teoh (2009); DellaVigna & Pollet (2009).

*Checked for this checkpoint:*
- **Jegadeesh & Livnat (2006a).** "Revenue surprises and stock returns", *Journal of Accounting and Economics* 41(1–2), 147–171. The working-paper abstract reports significant post-announcement abnormal returns for large revenue surprises **after controlling for earnings surprises**.
- **Jegadeesh & Livnat (2006b).** "Post-earnings-announcement drift: the role of revenue surprises", *Financial Analysts Journal* 62(2), 22–34.
- **Novy-Marx (2015).** "Fundamentally, momentum is fundamental momentum", NBER WP 20984. Earnings-surprise measures subsume past returns in cross-sectional regressions, and price momentum's time-series returns are explained by its covariance with earnings momentum.

**Why it might be under-priced:**
- attention constraints during clustered reporting seasons;
- anchoring on the latest level rather than its persistence;
- slow diffusion of quarterly detail (revenue, margins) beyond the headline number.

**Why it might persist in modern large caps:** these behavioural frictions do not vanish with size, and a quarterly signal needs patient capital that many short-horizon arbitrageurs do not supply. [I] This is weak reasoning, not evidence.

**Why it has probably weakened (stated in full):**
- **[L] Martineau (2022), *Critical Finance Review* 11(3–4), 613–646.** The drift is **absent in large stocks since 2006**: prices absorb surprises on the announcement day.
- **[V] Chordia et al. (2009)**, cited in P2-CP3: the effect is concentrated in illiquid stocks.
- **[L]** A 2025 commentary reports that two 2025 papers dispute Martineau, attributing the disagreement to research design. **[GAP]** I could not open that commentary or identify those papers, so nothing from them is used here.
- **[V]** The programme's own earlier review rated PEAD "**Unlikely**" for this universe (P2-CP3, family D).
- **[V]** H017 (the price-reaction form) was rejected (D128).

**Relevance to long-term compounding [I]:**
- Each surprise is a short-lived, about one-quarter, effect. It is renewed by every filing, so it compounds only if harvested repeatedly.
- That makes OF-A a **turnover-bearing** return source, not a buy-and-hold one. Its long-run value is the after-cost sum of many quarterly effects.
- A second channel is plausible but unproven: firms with repeated positive surprises may be businesses with persistent operating improvement. That is closer to the business-improvement idea (H029, never evaluated).

**Verdict on distinctness:** see §9. **Prior [I]:** low for at least $2B US stocks after 2006. OF-A deserves only a **cheap, clean falsification test**, with "not qualified" the most likely outcome (as in RM1 §21).

## 9. Distinction from prior hypotheses [V / I]

| Prior work | What it used | Relation to OF-A | Distinct? |
|---|---|---|---|
| H017 (D128, REJECTED) | 2-session SPY-adjusted **price reaction** to the 8-K earnings release; top decile; 60-session hold | Price-based. OF-A uses the **accounting content** of the filing. Literature treats announcement return and accounting surprise as separate predictors (Brandt et al. 2008) | **Yes** |
| H016 (D117, REJECTED) | GP/A **level** | A level, not a change relative to expectation | **Yes** |
| H022–H024 (D198, D201, D203) | Score v1 layers (incl. revenue-growth **level**), the 11 features (GPA, ACC, BM, AG, CBOP, CFP, EQA, MOM, LOWVOL, REV1M, HI52) | None is a surprise against the firm's own seasonal history | **Yes**, but a **revenue-growth level** form would be a repackaging and is excluded |
| H026–H028 (REJECTED) | Learned Ridge on the same 11 features | No surprise feature | **Yes** |
| H029 F1 (NOT EVALUABLE) | (r0/r4 − 1) − (r1/r5 − 1): quarterly same-quarter YoY revenue-growth **acceleration** (Data v3 spec §5) | **Overlaps.** Acceleration equals a revenue surprise against a "last quarter's YoY growth persists" expectation. Never evaluated, so not a failed factor, but the same design source | **Only partly.** Must be disclosed and counted in the ledger |
| H029 F2, F4, F5, F8 | Year-on-year **improvement** in TTM margins and returns | Slow TTM changes; OF-A is quarterly surprise | Mostly yes; a TTM-change form would duplicate H029 |
| H030 (NOT EVALUABLE) | Fixed 50/50 blend of frozen H028 + H029 ("upside signal") | **This programme's Question C is the same architecture question.** The H030 attempt failed on null design, not on returns | Distinct only if the method changes (signal-first, no identity null, no preset 50/50) |
| H002 / H019 S1 (REJECTED) | Price momentum; E020-06 did not reproduce momentum (top decile −2.18%/yr) | If price momentum is fundamental momentum (Novy-Marx 2015), its absence here **lowers** OF-A's prior | Distinct signal; negative inference to disclose |

**Disclosure [I]:** this checkpoint was written with knowledge of all the above development-period results, including the momentum and H017 failures. A future OF-A pre-registration must state that.

**Recommendation:** pursue OF-A only in its **accounting-surprise** forms (§11, C1–C3, C5), with acceleration forms (C4) counted as overlapping H029 F1. **Do not** pursue growth levels, TTM-change forms or H029's composite under a new name.

## 10. Required OF-A data and PIT constraints [V / I]

| Need | Available without purchase | Source / constraint |
|---|---|---|
| Quarterly revenue, net income, gross profit, operating cash flow, total assets, 2008–2021 | **Yes:** Data v3 (frozen, D230) | Restatement guard v3 (> 1.5%) on all five; 1,018 of 116,639 vendor versions blocked [V] |
| Fourth-quarter values | Derived as fiscal year minus nine months; a year-to-date value is never taken as a quarter [V] | Data v3 spec §3.3 |
| Availability time | max(first seen in QuantConnect's stream, SEC filing + 1) (M2 rule, D187/D230) [V] | 10-Q median 35 days after period end (90th percentile 40); 10-K median 56 days (P7-CP5c) [V] |
| Earnings-release time | 8-K Item 2.02 acceptance times (Event Data v1, 88,723 events, D125) [V] | **Release exhibits are not XBRL-tagged**, so values are verifiable only at the 10-Q / 10-K (P7-CP5c item 10). [I] OF-A is knowable only at the periodic filing, often days to weeks after the release; part of any drift is missed |
| Operating income | **Not approved** (48% SEC agreement, D113; P14-CP1 class C) [V] | "Operating-profit improvement" must use gross profit or operating cash flow, never operating income |
| EPS, share counts as levels | **Unsafe** (split-adjusted to today, D107) [V] | Use net income (scale-free surprise) or SEC cover-page share counts (Data v3 F7 rule); never vendor per-share fields |
| Analyst consensus | **No** (paid; PIT unverified; P2-CP11) [V] | Analyst-based SUE excluded |
| Sector | SEC SIC at filing → FF12; financials excluded (`qr_industry`) [V] | — |
| Coverage | F1-type quarterly revenue chains: 73% (2011–14), 87% (2015–17), 86% (2018–21) of the eligible non-financial universe (P14-CP1) [V] | Early-year thinness must be modelled in synthetic tests |

**PIT design issues the pre-registration must settle (none decided now) [P]:**
1. **Comparison-quarter vintage.** The q−4 value can be taken as first reported, or as known at t (possibly recast). Recasts for discontinued operations make "as known at t" more comparable. Both are PIT-legitimate; one must be chosen ex ante.
2. **Fiscal irregularities.**
   - 52/53-week years (14-week quarters);
   - fiscal-year changes and transition periods;
   - Data v3's ±6-day period matching and 80–100-day chain gaps.
   - A same-quarter comparison is invalid across a fiscal-year change.
3. **Missing quarters.** Standardised surprises need about 8 prior consecutive quarters, which lowers coverage, especially in 2011–2012 (XBRL phase-in).
4. **Non-comparable items.** Net income includes special items. Known accounting regime changes inside 2011–2021 [I, from public accounting standards]:
   - the late-2017 US tax-reform deferred-tax remeasurement;
   - ASC 606 revenue recognition (2018);
   - ASU 2016-01 equity fair value through net income (2018);
   - ASC 842 leases (2019, total assets).
   - Revenue- and gross-profit-based forms are less exposed than net income.
5. **Negative earnings.** Never use growth ratios with net-income denominators. Scale by the firm's own surprise volatility, total assets or market cap.
6. **Outliers.** Use cross-sectional ranks. Any winsorisation is fixed ex ante.
7. **Restatements.** Guard v3 blocks vendor versions that already carry a later restated value (> 1.5%). Restatements of 1.5% or less pass.

## 11. Candidate surprise and acceleration definitions (NOT implemented, NOT chosen) [P]

All use only values public at the decision time. X is quarterly revenue (REV), net income (NI) or gross profit (GP). q is the newest visible quarter, and E[X_q] is the expectation formed from earlier public statements.

| ID | Expectation model | Definition (sketch) | Literature | Notes |
|---|---|---|---|---|
| C1 SUE-NI | Seasonal random walk with drift | (NI_q − NI_{q−4} − d) / σ, where d and σ are the mean and SD of the firm's prior 8 seasonal differences | Foster, Olsen & Shevlin-type SUE; Bernard & Thomas | Scale-free; handles negative earnings; exposed to special items |
| C2 SUE-REV | Same, for revenue | (REV_q − REV_{q−4} − d) / σ | Jegadeesh & Livnat (2006a) | Revenue is guarded and less manipulable; coverage best |
| C3 Price-scaled surprise | Seasonal random walk | (NI_q − NI_{q−4}) / market cap at the prior month-end (PIT market cap) | Common SUE variant | No 8-quarter history needed; size-correlated |
| C4 Acceleration | "Last quarter's YoY change persists" | (X_q − X_{q−4}) − (X_{q−1} − X_{q−5}), scaled | Foster (1977)-type model | **Overlaps H029 F1** (§9) |
| C5 GP surprise / assets | Seasonal random walk | (GP_q − GP_{q−4}) / total assets_{q−4} | Profitability-change literature | "Operating improvement" without operating income |
| C6 Dual surprise | C1 and C2 agree in sign and are both large | Rank-average or joint top-group | Jegadeesh & Livnat (2006b) | Two inputs: more freedom; must be pre-registered as one signal |

**Excluded:**
- analyst-consensus surprise (no data);
- operating-income forms (not approved);
- EPS (per-share unsafe);
- press-release text parsing (unstructured, error-prone and a major new data project);
- growth levels (already used in H022);
- TTM-change forms (H029).

**Proposal:**
- A future pre-registration chooses **at most two** of C1–C6 (e.g. one earnings form and one revenue form), with the choice justified by literature and data quality alone, before any real-data statistic.
- C4 counts against the hypothesis budget as an H029-related variant.
- **Signal timing:** a stock's signal updates at its filing's availability day. It is used at the next monthly review if it is at most one quarter old (an ex-ante freshness rule); otherwise it is missing.

## 12. Proposed universe-wide signal evaluation method [P]

**Unit of analysis:**
- monthly reviews 2011–2021 (development data);
- every eligible stock with a fresh, valid signal: the same baseline universe (≥ $2B, price ≥ $5, ADV20 ≥ $5M, NYSE/Nasdaq common stocks; financials and REITs excluded as in every Phase 7–14 population, D169);
- no Top-N selection.

**Response:**
- next-month total shareholder return, from next-session open to the next review close, with the frozen corporate-action and delisting conventions (`qr_p7_pred.response`);
- minus the equal-weight eligible-universe return (cross-sectional demeaning).
- Horizons of 2, 3 and 6 months are **decay diagnostics** (overlapping) and never the primary test.

**Primary statistic: Fama–MacBeth with stock-level controls.**
- Each month, regress the response on:
  - the signal percentile;
  - FF12 sector dummies;
  - log market cap, LOWVOL (60-day volatility), book-to-market, GP/A (profitability), 12-1 momentum, asset growth and trailing beta.
- Controls are measured exactly as in H024, rank-transformed.
- The statistic is the time-series mean of the signal slope, with a **pre-registered** standard error: Newey–West (fixed lag) or a stationary block bootstrap, whichever the synthetic study (§13) shows is calibrated.

**Pre-registered secondary statistics:**
- **long-only relevance:** the controls-adjusted mean return of the top signal quintile minus the universe;
- raw and residual rank IC;
- within-sector quintile spreads;
- persistence: the slope using signals from the **previous** filing only;
- decay curve over horizons.

**What is NOT used:**
- identity-tether or permutation nulls (D235, D238);
- matched-twin portfolios (D239);
- time-series factor regressions as the significance test (R3 failure, D239);
- any Top-15 book as the significance test.

**Gate form:** the slope's t exceeds a threshold **fixed by the synthetic calibration**, the top-quintile excess is economically meaningful (a pre-set floor after estimated costs), and it holds in both halves of the period.

**Status:** development evidence only, because 2011–2021 has been seen.

## 13. Synthetic validation requirements [P]

The inference method (§12) is approved only if it passes a protocol frozen before any synthetic result. Every owner scenario is included, and each is generated as an extension of the existing offline generator `qresearch.r1synth` (D239).

| # | Scenario | Purpose |
|---|---|---|
| S0 | No signal, no priced factors | Basic size |
| S1 | No signal; priced LOWVOL | The H027 / H028 failure mode |
| S2 | No signal; priced growth | The R3 failure mode |
| S3 | No signal; priced profitability | The R3 failure mode |
| S4 | No signal; growth and profitability priced, **signal correlated with them** (ρ calibrated to plausible surprise–growth correlation) | A surprise that only proxies a priced exposure must not be "significant" |
| S5 | S4 with **noisy controls** (the priced factor observed with error) | Residual exposure leaks into a correlated signal: a classic false-positive source |
| S6 | No signal; **time-varying** premia; sector-level shocks (cross-sectional correlation) | SE robustness |
| S7 | No signal; churn (entries, exits, delistings, sector moves) at 0×, 1× and 2× the calibrated rate | The D235 / D238 mechanism |
| S8 | No signal; persistent characteristics; **event-time updates** (signals refresh at irregular filing dates, stale between) | OF-A's real data structure |
| S9 | No signal; overlapping forward returns (2-, 3- and 6-month diagnostics) | Overlap-correct errors |
| S10 | No signal; heavy-tailed returns, thin early coverage (2011–2012 pattern) | Realism |
| P1–P3 | **Planted signal** at three strengths, with all of S4–S8 active | Power and MDE |

## 14. False-positive calibration and power requirements [P]

**Size:**
- At least 1,000 synthetic panels per null scenario (binomial SE about 0.3% at 1%).
- Rejection rate at nominal 1% must be ≤ 2.0%, at nominal 5% between 3.5% and 6.5%, in **every** null scenario S0–S10.
- p-values must be approximately uniform (Kolmogorov–Smirnov, with a pre-set bound).

**Power:**
- Reported as the planted effect needed for 50% and 80% rejection.
- It must reach **80% at a pre-declared economically meaningful effect**, for example a long-only top-quintile excess of about +3% a year before costs.
- [I] Anchor: H022 on Data v2 needed IC ≈ 0.049 for 80% power over 83 months (P7-CP5f, D191). Over 131 months this scales to roughly 0.039.

**Fail rule:**
- If any size criterion fails, or power is below 80% at the declared effect, the method is **NOT VALIDATED**, and OF-A is not run on real data.
- At most **one** pre-specified method revision may be proposed to the owner. There is no iterative tuning to pass.

**Freeze:** the protocol (scenarios, parameters, seeds, panel counts, criteria) is committed and hash-pinned before the first synthetic result, as in P13-CP5 and P13-CP6.

## 15. Standalone offensive portfolio design principles [P]

These apply only if the signal qualifies at Stage D, and only with a separate approval.

- **Pre-registered before any portfolio result:**
  - K, scoring, sizing and sector cap;
  - rebalance and holding rules;
  - buffer and cash rules;
  - execution and costs.
- **K is set by mechanics and diversification, not returns.**
  - [I] H028's sensitivity to K (§4) argues for a broader book (K ≥ 20–30) and an explicit test that results do not hinge on K.
  - K = 15 / 20 / 30 should be reported as pre-declared diagnostics.
- **Holding period** aligned to the filing cadence (about 63 sessions), with a replacement buffer to cut turnover.
- **Position limits:** at most 10% initial per stock, at most 3–4 per FF12 sector. No leverage. Cash allowed.
- **Costs:** $7 per order + 0.10% per side, with a 2× cost stress.
- **"Offensive" means growth potential with bounded risk** (owner §8):
  - beta reported, not targeted;
  - no microcaps, options or leverage;
  - no concentration beyond the caps.
- **Benchmarks** (owner §10):
  1. SPY;
  2. the equal-weight eligible universe;
  3. a **transparent style benchmark**. This is a rule-based book with the same K and mechanics that ranks on the strategy's main pre-declared exposures (e.g. 12-1 momentum + sales growth). Or, where one exists for the period, a growth or momentum ETF named ex ante.
  - [I] Matched twins are infeasible (D239), so style is controlled with transparent rule books, not matching.
- The offensive candidate is judged on its **standalone** economics. Its correlation with H028 in seen years is never a criterion.

## 16. Future combined-portfolio mechanics [P]

Combined = w_D × Defensive + w_O × Offensive, with w_D + w_O = 1 and no leverage.

**Allocation policy, chosen once, before any combined result:**
- **Fixed strategic weights.** One value, chosen by an explicit, non-return argument (for example the investor's maximum tolerable relative drawdown) and stated as a round number, never optimised.
- **Or an independently justified risk budget.** Equal ex-ante volatility contribution from trailing PIT volatility, re-set annually.
- **Not allowed:**
  - optimising weights against 2011–2021;
  - assuming 50/50;
  - any regime switch or crash filter (owner §12).
- **Rebalancing:** annual, or when a weight drifts beyond a fixed band (e.g. ±10 points). The band is fixed ex ante.

**One investable account:**
- one cash balance;
- component targets summed into one target book;
- trades netted per security;
- aggregate limits: total single-stock weight at most 10% initial; total FF12 sector weight capped; portfolio beta reported;
- costs charged on **net** trades;
- drawdown and every metric computed on the combined equity.
- **Two separately computed equity curves are never averaged.**

## 17. Portfolio overlap and trading-cost treatment [P]

**Overlap:**
- Each month, report the share of combined weight held by both sleeves and the effective number of stocks.
- A stock in both sleeves is one position. Its weight is the sum, subject to the aggregate cap; any excess goes to cash or to the next name by a pre-set rule.

**Rebalance timing:** if sleeves review on different calendars (monthly vs quarterly), the combined book trades only on the union of review days with net orders. Cash from one sleeve's sales funds the other's purchases on the same day.

**Costs:**
- $7 per **net** order plus slippage on net traded value.
- Attribute costs to the sleeve that caused the trade, and report netting savings separately.
- 2× cost stress.

**Cash:** uninvested cash is reported, with its drag on S. [I] H017 showed cash drag plus costs can create a 2.5–3%/yr structural hurdle (P2-CP13).

**Small capital:** at $100,000 and about 30 positions, a $7 order is about 0.2% of a position. The research capital stays $100,000, with a $200,000 diagnostic (frozen convention).

## 18. Five-architecture comparison [I / P]

Not ranked by historical returns; no returns were computed for this comparison.

| | A — H028 alone | B — SPY + defensive ETF | C — Offensive alone | D — H028 + Offensive | E — Defensive ETF + Offensive |
|---|---|---|---|---|---|
| Expected return source | Market beta below 1, defensive / quality tilts, possibly selection (unproven) | Market beta plus any low-vol / quality premium | Market beta plus the signal's alpha plus growth / momentum style | A's + C's sources | B's + C's sources |
| Expected risk exposures | Low-vol, value, quality; Top-15 idiosyncratic risk; sector tilt | Lower beta; low-vol sector tilts (utilities, staples) | Growth, momentum; possibly higher beta; momentum-crash risk | Mix; overlap risk | Mix; offensive idiosyncratic risk only |
| Complexity | High: 11 features, annual Ridge refits, Data v2.1, an 8 GB host | Minimal | Moderate: one signal, Data v3 | **Highest:** two models, two data stacks, netting | Moderate |
| Data requirements | Data v2.1 **extended blindly** past 2021 for any new evaluation | ETF prices (from 2011–2013) | Data v3 (2011–2021); extension for the Holdout | Both, extended | Data v3 + ETF prices |
| Trading costs | High: about 7.5×/yr turnover; about 0.8–1.7% of equity a year (§4) | About 0.1%/yr (annual rebalance) | Moderate–high (quarterly signal) | High, partly netted | Moderate (one active sleeve) |
| Need for independent evidence | Defensive value D-2 on independent data (§6); none exists | None for selection: it **is** the benchmark | Full chain: signal (D), portfolio (E), independent (G) | A's and C's **plus** a combination test | C's chain plus a combination test against DB4 |
| Principal weaknesses | REJECTED; episodic (2018 / 2020); fragile to K; post-hoc; lags in strong bulls; heavy to run | [I] Below-1 beta likely costs terminal wealth vs SPY unless defensive premia exceed the lost equity premium; long bull-market lag | Low prior in large caps after 2006 (Martineau 2022); filing-date lag; may be a style bet | Inherits H028's unvalidated status; repeats H030's design question; most researcher degrees of freedom | Offensive alpha must offset the defensive sleeve's beta drag and its own costs |
| What would make it preferable to SPY | Forward / Holdout asymmetric capture beating DB5 / DB7 over several down episodes | A persistent low-vol / quality premium large enough to offset lower beta (doubtful for terminal wealth) | After-cost alpha beyond SPY, EW universe and the style benchmark, on independent data | Combination beats SPY, **both components, DB4 and E** | Combination beats SPY, DB4 and C alone |
| What could disqualify it | Trails DB5 / DB7 on independent data; asymmetry vanishes outside 2018 / 2020-type episodes | Not disqualifiable as a benchmark; dropped as the *goal* if terminal wealth < SPY | Signal fails the calibrated test; alpha explained by style; costs exceed edge | Fails vs E (H028 adds nothing over an ETF) or vs DB4 | Fails vs DB4 or vs C alone |

**Break-even arithmetic for B and E [I]:**
- Assume an equity premium of about 5% a year (an assumption, not a measurement). A defensive sleeve at beta about 0.8 then costs about 1% a year of expected return on that sleeve, unless defensive premia compensate.
- In E with w_O = 0.5, the offensive sleeve must therefore earn about 1% a year of alpha (after its own costs) just to offset that drag, and more to beat SPY materially.
- This is why the **offensive alpha is the crux** of every architecture except A and B.

**Recommendation: investigate C first, signal-first.**
- **Wrapper:** E is the default portfolio wrapper, if and only if C qualifies.
- **H028:** A and D stay **reference comparators only**. H028 can be shown as a frozen reference curve on already-seen data, never as a component, until D-2 is supported on independent data.

**Why:**
- C is the only architecture whose missing piece can be tested now with existing data and a validated method.
- E isolates the offensive sleeve's contribution against DB4 with a fully transparent defensive sleeve.
- D adds a rejected, heavy, unvalidated component and repeats the H030 question, which failed for methodological reasons.

## 19. SPY and simple defensive benchmark requirements [P]

- **SPY:** total return with dividends reinvested through its price multiplier; bought at the same first entry open with the same capital and costs; sold at the same final close (frozen `qr_h026.spy_simulate` convention).
- **Benchmarks per architecture:**

  | Architecture | Benchmarks |
  |---|---|
  | Every architecture | SPY and DB4 (fixed SPY + defensive ETF) |
  | Defensive claims | Add DB5 and DB7 (beta-comparable) and DB2 (LV15) |
  | Offensive | Add the EW eligible universe and the style benchmark (§15) |
  | Combined | Add both components alone and E-vs-D where relevant |

- **Same treatment:** every benchmark uses the same dates, capital, cost model (ETFs: $7 per order + 0.10%) and rebalance calendar. Weights and instruments are named before any result.
- **Incremental value without conditional nulls (owner §13):**
  - incremental value is the **paired** log-wealth difference S(Combined vs benchmark);
  - its evidence is assessed with the Amendment 3 W2-type standard error: max(iid, stationary block bootstrap), threshold pre-registered (D121);
  - no permutation or identity-tether null is used for any portfolio-level question.
  - Portfolio tests are **economic** evidence. The **statistical** test of skill is the signal-level test (§12).

## 20. Long-horizon 30-year objective and metrics [P]

- **Primary:** S = ln(W_strategy / W_SPY) after all costs, with the same capital and dates.
- **Supporting metrics, all reported:**
  - CAGR, excess CAGR, relative terminal wealth;
  - rolling 3-, 5- and 10-year relative results; 15- and 20-year where history allows (it does not for 2011–2021);
  - MaxDD, relative drawdown, time underwater, recovery time;
  - up- and down-capture;
  - return concentration;
  - turnover and costs;
  - beta, style and sector concentration;
  - calendar-year results (diagnostic only; **no annual win-rate gate**, owner §2 and §14; D226).

**Balancing long-horizon wealth against fragility:** qualification needs a positive S **plus** passing pre-set fragility screens. The thresholds below are proposals for the owner; each future pre-registration fixes its own before any result.

| Screen | Proposed rule | Why |
|---|---|---|
| F1 Episode concentration | No single mechanically defined episode supplies more than 50% of positive contributions to S | H017 (74% in 2014–15) and H028 (49% in March 2020) patterns |
| F2 Leave-best-out | S > 0 after removing the best 12 months, and separately the best calendar year | A single extraordinary episode must not carry the result |
| F3 Regime breadth | S vs SPY not negative in **both** SPY-up and SPY-down months for offensive or combined books; for defensive books, up-capture at least a pre-set floor (e.g. 0.85) | Prevents a pure crash bet or a pure beta bet |
| F4 Investor tolerance | Relative drawdown vs SPY no deeper than a pre-set level (e.g. −25%), longest stretch below a relative high no longer than a pre-set level (e.g. 7 years; P13-CP3 measured 7.6 for H028) | Owner §2: can the investor realistically hold it? |
| F5 Long-horizon synthetic robustness | Year-block bootstrap as P13-CP3, including leave-episode-out, reported as conditional diagnostics, never as probabilities | The D226 standard |
| F6 Cost robustness | S > 0 at 2× costs | — |

**Not allowed:**
- extrapolating any 7- or 11-year CAGR into a "30-year" claim;
- a 30-year backtest, which is impossible with available data (at most 1998–2021 plus the Holdout, and only after a purchase; RM1 §10).

## 21. Evidence limitations and independent-data constraints [V / I]

| Constraint | Effect |
|---|---|
| 2011–2021 seen by H001–H030 | Every result there is development evidence; OF-A included |
| Data v2.1 and Data v3 end 2021-12-31 | Any Holdout or forward use needs a **blind** extension (built and audited without looking at returns) |
| Holdout 2022-01-01 → 2026-08-31, about 4.7 years, single use | Low power (§6); reserved for at most one frozen candidate; never opened for power or allocation choice |
| 2026-09-01 → freeze: locked unseen (D094) | Not forward testing |
| Pre-2010 | Not usable without new data: no market cap before Oct 2009, dead-firm fundamentals missing, no XBRL; Sharadar-type purchase blocked by D124; licence unverified (RM1 §10) |
| Defensive ETFs start 2011–2013 | No investable defensive benchmark before 2011 |
| QuantConnect default build changes | Data v1 does not reproduce on the current build (D183); any new run needs default-build digest verification |
| QuantConnect compliance | Data-validation exports are rejected (D185); PIT audits must be aggregates-only or offline from public SEC data |
| Public macro knowledge (2008, 2020, 2022) | Design-hindsight risk for defensive claims; disclose |
| Forward paper trading | Slow; manual periodic runs only (no scheduler, by scope) |

## 22. Multiple-testing and selection governance [P]

- **Ledger:** `research/longhorizon/SELECTION_LEDGER.md` (created by this checkpoint; no entries yet). Every hypothesis, variant, construction and selection decision of this programme is recorded before its result, cross-referenced to `research/hypotheses/STATUS.md` and `experiments/INDEX.csv`.
- **Fixed budget, proposed before any real-data test:**

  | Stage | At most |
  |---|---|
  | D, signal hypotheses | 2 pre-registered together, with Holm across them; C4 counts as one, labelled H029-related |
  | E, standalone portfolio | 1 frozen portfolio, only for a qualifying signal |
  | F, combined architecture | 1, with **one** pre-registered weight policy |
  | G, Holdout | At most 1 candidate, with written approval in `HOLDOUT_UNLOCK.md` |

- **Sequential gatekeeping:**
  - F is tested only if D and E pass;
  - a combined pass cannot rescue a failed standalone (owner §5: C cannot validate A or B);
  - failing at any stage ends that line, with no variants.
- **Labelling:**
  - the OF-A **signal** is literature-motivated (pre-2010 sources), and its test must make no reference to H028;
  - the **architecture role** (an offensive companion) is development-motivated by H028's observed profile and is labelled so;
  - any construction choice influenced by H028's weaknesses is labelled development-motivated.
- **Prior looks:** about 30 hypotheses have touched 2011–2021. Reported as context; a DSR-style diagnostic only (D069 precedent).
- **No fishing:** no testing of offensive models until one complements H028. Correlation with H028 is never a selection criterion.

## 23. Staged roadmap with STOP gates [P]

Every stage ends in a checkpoint and **STOP**. Nothing advances automatically.

| Stage | Research question | Required input | Deliverable | Objective stop condition | Owner decision before continuing |
|---|---|---|---|---|---|
| **A Design** (this checkpoint) | What would a credible programme look like? | Repository records, literature | RM2 (this) | — | Approve Stage B, or stop |
| **B Synthetic validation** | Does the §12 method control false positives in S0–S10, with power at the declared effect? | `r1synth` extended (event-time signals, noisy controls); protocol frozen first | Calibration report; PASS / NOT VALIDATED; MDE | Any size criterion fails, or power < 80% at the declared effect → STOP (at most one pre-specified revision) | Approve Stage C |
| **C PIT data feasibility** | Are C1–C6 inputs computable PIT with adequate coverage and correct timing? | Data v3; Event Data v1; public SEC filings offline; aggregates-only QuantConnect run if needed | Coverage by year; timing (filing vs release lag); restatement and vintage handling; fiscal-irregularity counts | Coverage below a pre-set floor (e.g. 70% of eligible stock-months a year after 2012), any PIT violation, or a compliance rejection → STOP | Choose at most 2 signals; approve the pre-registration |
| **D Signal research** | Does the signal predict returns across the eligible universe beyond controls? | Frozen pre-registration; Data v3 2011–2021 | One real run; gates; decay; diagnostics | Gates fail → OF-A REJECTED, no variants | Approve Stage E |
| **E Standalone portfolio** | Does a frozen offensive book beat SPY, the EW universe and the style benchmark after costs? | Frozen portfolio spec | One development run | S ≤ 0 vs any required benchmark, or a fragility screen fails → STOP | Approve Stage F |
| **F Architecture** | Does one pre-registered combination (E-type by default) beat SPY, both components and DB4 as one investable portfolio? | Frozen weight policy; ETF data verified | One combined development run | Fails vs DB4 or vs the offensive sleeve alone → STOP | Approve Stage G (blind data extension + Holdout) |
| **G Independent confirmation** | Does the frozen candidate hold on unseen data? | Blind Data v3 extension to 2026-08-31; `HOLDOUT_UNLOCK.md` | One Holdout evaluation | Pre-registered Holdout criteria fail → no production candidate | Approve Stage H |
| **H Forward monitoring** | Does it behave as expected prospectively? | Frozen candidate | Periodic manual paper-trade reports (no scheduler) | A pre-set relative-drawdown or tracking breach → review | Any live investment decision (outside research scope) |

## 24. One recommended next checkpoint [P]

**Stage B — OF-A signal-inference synthetic validation (offline; synthetic data only).**

1. **Write and hash-pin the protocol before any synthetic result:**
   - scenarios S0–S10 and P1–P3 (§13);
   - generator extensions (event-time signal refresh, noisy controls, signal–control correlation, overlapping horizons, heavy tails);
   - estimators (Fama–MacBeth with stock-level controls; Newey–West at a fixed lag; stationary block bootstrap);
   - criteria (§14), seeds, at least 1,000 panels per null scenario, and the declared economic effect.
2. **Commit, then run the offline study.**
3. **Report:** PASS or NOT VALIDATED, with the calibrated standard-error choice and the 50% and 80% MDE.
4. **STOP.**

**Why this first:**
- It is the cheapest decisive step. It needs no real data, no QuantConnect run and no purchase.
- It attacks the documented failure point (inference: D235, D238, D239).
- If no valid test exists, the programme stops before touching any return.

**Not included:**
- real data;
- signal definitions applied to any real company;
- H028 runs;
- the Holdout.

## 25. Exact next owner approval required

Choose one:

1. **"Approve Stage B: OF-A signal-inference synthetic validation, offline and synthetic only, with the protocol (scenarios S0–S10, P1–P3, estimators, criteria, seeds, declared economic effect) committed and hash-pinned before any result. STOP after the report."**
   - Also confirm, or amend, the proposed budget (§22: ≤ 2 signals, 1 portfolio, 1 combination, ≤ 1 Holdout candidate) and the fragility screens F1–F6 (§20) as the programme defaults.
2. Approve instead a Stage C data-feasibility audit first (non-return; offline public SEC data plus aggregates-only QuantConnect if needed).
3. Stop the programme.

**Until then:** H028 REJECTED (Frozen Defensive Research Reference, descriptive only); H029 / H030 NOT EVALUABLE; no candidate; no active hypothesis; Holdout sealed.

---

**Literature sources checked for this checkpoint (bibliographic verification only):**
- Jegadeesh & Livnat, *Revenue surprises and stock returns*: [working paper](https://pages.stern.nyu.edu/~jlivnat/JAE%20submission.pdf), [RePEc](https://ideas.repec.org/a/eee/jaecon/v41y2006i1-2p147-171.html); *FAJ* 2006 [RePEc](https://ideas.repec.org/a/taf/ufajxx/v62y2006i2p22-34.html).
- Novy-Marx, *Fundamentally, momentum is fundamental momentum*: [paper](https://mysimon.rochester.edu/novy-marx/research/FMFM.pdf), [RePEc](https://ideas.repec.org/p/nbr/nberwo/20984.html).
- Martineau, *Rest in Peace Post-Earnings Announcement Drift*: [CFR](https://cfr.ivo-welch.info/published/papers/martineau2021rest.pdf), [RePEc](https://ideas.repec.org/a/now/jnlcfr/104.00000122.html).
- ETF inception dates (third-party listings, to be verified against prospectuses and QuantConnect data): [SPLV vs USMV](https://www.etfcentral.com/compare-etfs/SPLV-vs-USMV), [QUAL](https://www.etfcentral.com/fund/QUAL), [QUAL (ETF Database)](https://etfdb.com/etf/QUAL/).
