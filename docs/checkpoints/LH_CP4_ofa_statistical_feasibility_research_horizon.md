# LH-CP4 — OF-A Statistical Feasibility and Research-Horizon Assessment

**Owner decision:** D245, 2026-10-18 (`docs/owner/2026-10-18_lh_cp4_ofa_statistical_feasibility.md`).

**Nature:** analytical / paper-only. Everything here is metadata counts or equations evaluated on stated assumptions:
- no returns, signals, rankings or models;
- no synthetic simulation, Monte Carlo or null worlds;
- no QuantConnect run;
- no Holdout access.

**Final classification: B — UNDERPOWERED FOR MODEST EFFECTS.**

## In plain words

You approved a narrow, forward-looking restriction: future OF-A design may consider only decision years 2015–2021, and only accounting histories whose fiscal labels were directly verified (no rebuilt or assumed labels). That population exists and is reasonably large:
- about 830 stocks a month;
- 1,500 securities;
- 83 monthly decision dates;
- coverage of at least 72.7% in every year.

**The problem is time, not stocks.** A signal test's precision depends mainly on the number of *independent months*, not the number of stock-months:
- 83 months, reduced further by month-to-month dependence, is a short history;
- most accounting signals only change about four times a year, in four earnings seasons, so there are really only about 28 "fresh" information events in the period.

**What that means for detection.** Under middle-of-the-road assumptions, which are stated and not estimated:
- an effect worth the illustrative +3% a year for a top quintile has roughly a **coin-flip-or-worse chance** of being detected (about 10–79% depending on the assumptions; 80% only under favourable ones);
- effects of +5% a year or more would usually be detected;
- the recent research literature makes such large effects in $2B+ stocks unlikely (RM2 §5).

**The economics are thinner still.** A +3% gross top-quintile edge relative to the eligible universe is not +3% over SPY:
- a $100K book has to hold far fewer names than a quintile (about 165 stocks);
- trading costs alone take about 0.4–2.5% a year;
- the universe's own return relative to SPY is unknown.

## 1. Owner authorisation

Recorded verbatim in `docs/owner/2026-10-18_lh_cp4_ofa_statistical_feasibility.md`. The owner approved three decisions:
1. Accept LH-CP3 = **B — PARTIAL RECOVERY**.
2. A narrow Stage C exception.
3. An analytical feasibility assessment.

## 2. Decision ID (verified)

**D245.** The last entry in `DECISIONS.md` before this checkpoint was D244, the last merged PR was [PR #109](https://github.com/CohenMatan/quant-trading-research/pull/109) (main = 77f3bad), and the working tree was clean.

## 3. Explicit record of the Stage C exception

The record is `research/longhorizon/STAGE_C_EXCEPTION_D245.json`; its rule is implemented in `research/longhorizon/cp4/lh_cp4_power.py::approved` and tested.

| Aspect | Rule |
|---|---|
| Decision years | 2015–2021 only |
| Fiscal labels | Directly verified **L0 / L1** for **all 13 quarters**; no L2 / L3 |
| Period validation | LH-CP2 **rule V**: labels known and consistent (cycle + same-quarter pairs), no transition form, no mapping failure |
| Excluded | P-assume, rule P, unknown or invalid histories, identity-flagged histories, anything filed after 2021-12-31 |
| Preserved | SEC identity rules, PIT availability (filed ≤ D − 1), every historical integrity restriction |
| Nature | Prospective restriction of the usable research population, **for future design consideration only** |
| Not authorised | Stage B, Stage D, real signals, rankings, returns, backtests, the Holdout, purchases |

## 4. Earlier results unchanged

| Item | Status |
|---|---|
| LH-CP1 Stage C | **C — NOT FEASIBLE** (protocol ff97789b… unchanged) |
| LH-CP2 | **C — INSUFFICIENT EVIDENCE** (f7cbac94… unchanged) |
| LH-CP3 | **B — PARTIAL RECOVERY** (protocol 38d790e5…, rules 9a72c5c8… unchanged) |
| H028 | REJECTED |
| H029 / H030 | NOT EVALUABLE |
| Production candidate / active hypothesis | None / none |
| Selection ledger | Unchanged apart from a new row 4 (design / analysis only) |

No frozen protocol, result or artifact was edited.

## 5. The restricted 2015–2021 population (from committed LH-CP3 metadata; `LH_CP4_population.json`)

**Definition.** These are the stock-months that pass the D245 rule. They equal **LH-CP3 Scenario A** restricted to 2015–2021, reproduced exactly (a test asserts every numerator and denominator).

**Review dates.** 83 monthly reviews, 2015-01-30 → 2021-11-30. The run ends on 2021-12-31, so the last review is November.

**Eligible universe.** About 909–1,328 non-financial eligible stocks a month (E981-01 denominator; 2021 is larger).

**Approved stocks per month:**

| Candidate | Min | Median | Max | Mean |
|---|---|---|---|---|
| C1 | 686 | 824 | 1,028 | 827 |
| C2 | 648 | 782 | 1,004 | 787 |
| C6 | 647 | 782 | 1,004 | 787 |

**Annual coverage:** C1 74.8–83.0% (lowest in 2021), C2 72.8–78.5% (lowest in 2015), C6 72.7–78.5% (lowest in 2015). **All years meet the provisional 70% floor.**

**Breadth.** 1,488 registrants and 1,500 securities. A security spans a median of 16 distinct quarterly histories in the window.

**Exclusions** relative to C1-complete stock-months 2015–2021: 96.4% are approved overall, entrants 95.0%, leavers 96.1%. The larger structural exclusion happens *before* completeness: in LH-CP1, leavers and newcomers were much less likely to have complete histories at all (C1 64% and 37% versus 78–79%). That bias persists in this population.

**Sectors.** 11 FF12 groups (financials excluded), mean HHI 0.125. Stocks per month range from business equipment (163) to telecom (23).

**Remaining PIT / accounting limitations** (inherited from LH-CP1 to LH-CP3):
- earnings releases precede the structured filing by about 1 day (median), and their values are never numeric XBRL;
- the monthly calendar adds about 14 sessions of delay;
- truth labels themselves carry about 0.05% tagging errors;
- the Data v1 denominator (§18).

## 6. Directly verified L0 / L1 and rule V requirements

Every one of the 13 required quarters must have a fiscal label taken from:
- **L0:** the period's own original 10-Q / 10-K XBRL `fp`, through the XBRL index; or
- **L1:** the same `fp`, through local submissions, with the mapping and filing-date checks of LH-CP3 §2.

The 13 labels must then satisfy rule V:
- every consecutive pair is one step apart in the cycle;
- every same-quarter pair is equal (q0 = q4 = q8, and so on);
- there is no 10-KT / 10-QT inside the span;
- no quarter fails the mapping check.

Identity-flagged histories are excluded. No label may be reconstructed or assumed.

## 7. Expected effective sample-size limitations

| Quantity | Value | Basis |
|---|---|---|
| Monthly cross-sections | **83** | Review calendar |
| Stock-month observations (C1) | ≈ 68,700 | Metadata count |
| Independent *time* observations for inference | **≈ 45–83** monthly means | AR(1) dependence ρ 0–0.3 (assumed): T_eff = T(1 − ρ)/(1 + ρ) |
| Fresh-signal share of stock-months | **33.7%** | New quarter since the previous review |
| Fresh share by month | Feb 75%, May 61%, Aug 58%, Nov 55%; Apr / Jul / Oct 31–36%; other months 7–16% | Metadata count |
| Earnings-season cross-sections | **28** (Feb / May / Aug / Nov × 7) | Calendar |
| 3-month overlapping horizon | ≈ 28 non-overlapping equivalents | T / h |

**Why 68,700 stock-months are not 68,700 observations.**
- Every month's cross-section shares one market, one set of sector shocks and the same factor returns.
- Fama–MacBeth inference therefore rests on the time series of monthly cross-sectional statistics (T ≈ 83), not on N × T.
- Signals are stale between filings (about two-thirds of stock-months repeat the previous quarter's value), so consecutive months re-use the same information.
- Filings cluster in four seasons, so new information arrives in about 28 bursts.
- **For a surprise-type signal whose information is used up within weeks, the effective sample is closer to 28 than to 83.**

## 8. Fama–MacBeth feasibility analysis (RM2 §12 design)

Design: each month, regress the cross-sectionally demeaned next-month return on the signal percentile, FF12 dummies (10), and log market cap, LOWVOL, book-to-market, GP/A, 12-1 momentum, asset growth and beta (7). Then test the time-series mean slope. Each point below is reviewed:

1. **Time observations.** 83, reduced by dependence (§7, §11). This is the binding constraint.
2. **Cross-section.** About 650–1,030 stocks for about 19 regressors. Per-month degrees of freedom are ample, and cross-sectional sampling error is small: the independent-return floor of the IC standard deviation is 1/√(N − 1) ≈ 0.035, well below the assumed 0.06–0.12.
3. **Serial correlation** of monthly slopes comes from persistent signals, persistent controls and persistent factor regimes. It needs Newey–West or block standard errors and reduces T_eff (§11).
4. **Sector correlation** is absorbed in level by the FF12 dummies. Sector-specific shocks still enter the monthly slope's dispersion, and the time-series standard error accounts for them.
5. **Persistence.** Two-thirds of stock-months carry a stale signal, which dilutes a fresh-only effect: if stale signals are uninformative, the full cross-section's IC = f × IC_fresh with f ≈ 0.34 (§10).
6. **Unbalanced coverage.** The cross-section ranges from about 650 to 1,030 stocks and grows over time, with weaker early years. Equal-weighting months gives early, thinner months the same weight.
7. **Common filing seasons.** Fresh information arrives in 4 bursts a year. Months between seasons contribute little information but full noise to the mean slope. A season-only design halves T (§10, design D3).
8. **Missingness** among entrants, leavers and smaller firms (§5) changes the population the slope describes. It is not a source of bias in the standard error, but it limits generalisation.
9. **Controls.** Controls that explain a share R² of the signal's cross-sectional variance inflate the sampling part of the slope's dispersion by 1/(1 − R²). With σ_IC dominated by factor variation, the effect is small: main σ 0.090 becomes 0.092 / 0.094 / 0.100 at R² 0.2 / 0.4 / 0.6. The larger consequence is conceptual: the test targets the **incremental** effect beyond growth, profitability and momentum, which is smaller than the raw effect if a surprise partly proxies them (RM2 S4 / S5).
10. **Multiple hypotheses** (§12): up to 2 signal hypotheses (RM2 budget), plus the programme's long record of prior looks.

**Design feasibility versus calibration.** The design is *computable* on this population. Whether its standard errors are *correct* under event-time updates, churn and priced correlated factors is exactly what Stage B would have to show. This analysis does not establish it.

## 9. Analytical power assumptions and equations

Let s_t be the monthly statistic: the rank IC or the standardised Fama–MacBeth slope.
- Mean μ, time-series standard deviation σ, T monthly values.
- T_eff = T(1 − ρ)/(1 + ρ) for AR(1) dependence, and T/h for an h-month overlapping horizon.

Equations:
- **Test statistic:** t = μ̂ √T_eff / σ. Two-sided critical value c = t_{1 − α/(2m)}(T_eff − 1), Bonferroni over m hypotheses.
- **Minimum detectable effect at power π:** MDE = (c + t_π) σ / √T_eff.
- **Power at μ:** π(μ) = 1 − F_t(c − μ √T_eff / σ).
- **IC → top-quintile excess** (assumptions in §13): E[top quintile − universe] per month = IC · σ_cs · E[Z | Z > z_0.8] = 1.400 · IC · σ_cs, so per year = 12 × 1.400 × IC × σ_cs.

**Assumed parameter ranges** (labelled assumptions; **none estimated from returns**):

| Parameter | Values | Source of the range |
|---|---|---|
| σ_IC | optimistic 0.06 / main 0.09 / pessimistic 0.12 | The noise scenarios assumed in the committed P7-CP4 synthetic study ("typical of composite equity factors"). Not measured here |
| ρ | 0, 0.1, 0.2, 0.3 | Illustrative dependence of monthly statistics |
| σ_cs | 5%, 6.5%, 8% a month | Illustrative cross-sectional return dispersion of ≥ $2B stocks. P7-CP4 used 4.5–8.5% idiosyncratic volatility bands, and its committed Q5 − Q1 result implies about 6.7% |
| Tests | α ∈ {5%, 1%}, m ∈ {1, 2} | Owner request; the RM2 budget allows at most 2 signal hypotheses |

**Realistic-structure factor 1.34.** This is not a new estimate. The committed P7-CP4 synthetic study (same 83-month length, σ_IC ≈ 0.09, critical value 2.50) needed IC 0.033 for 50% power. The naive formula gives 0.0247 under the same inputs. The ratio, 1.34, measures how much ties, churn, persistence and coarse ranks cost relative to the textbook formula. It is reported as a sensitivity ("inflated") and cannot be calibrated for OF-A without Stage B.

The helper `lh_cp4_power.py` and the tables `LH_CP4_power.json` (`LH_CP4_power_tables.py`) are tested in `tests/test_lh_cp4.py`.

## 10. Approximate minimum detectable effects

**80%-power MDE, main σ_IC 0.09, ρ 0.1**

| Design | T_eff | 5%, 1 hyp. | 5%, 2 hyp. | 1%, 1 hyp. | 1%, 2 hyp. |
|---|---|---|---|---|---|
| D1 monthly, 1-month horizon | 67.9 | IC 0.031 | 0.034 | 0.038 | 0.041 |
| D2 monthly, 3-month overlapping | 22.6 | 0.056 | 0.062 | 0.070 | 0.075 |
| D3 earnings-season months only | 22.9 | 0.055 | 0.061 | 0.069 | 0.075 |

**D1 in economic units** (top-quintile minus universe per year; assumptions §13; "inflated" = × 1.34)

| Test | σ_cs 5% | σ_cs 6.5% | σ_cs 8% |
|---|---|---|---|
| 5%, 1 hypothesis | 2.6% (3.5% inflated) | 3.4% (4.5%) | 4.2% (5.6%) |
| 5%, 2 hypotheses | 2.9% (3.9%) | 3.7% (5.0%) | 4.6% (6.2%) |
| 1%, 1 hypothesis | 3.2% (4.3%) | 4.2% (5.6%) | 5.1% (6.9%) |
| 1%, 2 hypotheses | 3.4% (4.6%) | 4.5% (6.0%) | 5.5% (7.4%) |

**Power at the illustrative +3% a year** (σ_cs 6.5% → IC 0.0275; design D1)

| σ_IC, ρ | 5%, 1 | 5%, 2 | 1%, 1 | 1%, 2 |
|---|---|---|---|---|
| Optimistic 0.06, ρ 0 (naive / inflated) | 98% / 87% | 97% / 80% | 94% / 69% | 90% / 59% |
| **Main 0.09, ρ 0** | **79% / 54%** | 69% / 42% | 56% / 29% | 46% / 21% |
| Main 0.09, ρ 0.2 | 61% / 38% | 49% / 27% | 35% / 17% | 26% / 11% |
| Pessimistic 0.12, ρ 0 | 54% / 34% | 42% / 24% | 29% / 14% | 21% / 10% |

**Power at +5% a year:**
- main σ, ρ 0.2, inflated: 79% / 70% / 57% / 46%;
- pessimistic σ, ρ 0, inflated: 73% / 63% / 49% / 39%.

**At +2% a year:** main σ, ρ 0, naive: at most 45%.

**Where reliable power cannot be calculated:**
- the true σ_IC and ρ of an OF-A signal;
- how much of its information is used up after the first month;
- the size of the incremental effect after controls;
- whether the standard errors are calibrated under event-time updates.

These are exactly the quantities that are unknown without either real returns (not authorised) or a Stage B synthetic calibration. The tables above are therefore conditional sensitivities, **not** estimates of OF-A's power.

## 11. Sensitivity to statistical dependence

- Raising ρ from 0 to 0.3 cuts T_eff from 83 to 45 and raises every MDE by about 36%.
- A 3-month horizon, or concentration of information in earnings seasons, cuts T_eff to about 23–28 and raises MDEs by about 75–80% relative to D1.
- If only fresh signals carry information and the test uses every stock-month, the observable IC is diluted by f ≈ 0.34: a full-cross-section IC of 0.0275 then requires a fresh-signal IC of about 0.08.
- **Dependence is the most important unknown,** and every plausible form of it works against detection.

## 12. Multiple-hypothesis implications

- **One hypothesis to two** (Bonferroni) raises the critical value from 1.96 to 2.24 at 5%, and from 2.58 to 2.81 at 1%. MDEs rise by about 8–10%, and power at +3% falls by about 10 points (§10).
- **The programme's history matters too.** H001–H030 and several 2015–2021 looks (H026–H028 trained on 2011–2021) mean the 2015–2021 period is **not pristine**. A conservative 1% threshold, as used in H019 / H022, is the defensible choice. At 1% with 2 hypotheses, power at +3% is **11–46%** under the main and pessimistic assumptions.

## 13. Economic versus statistical significance

These quantities are distinct:
- regression slope;
- rank IC;
- top-quintile gross excess;
- portfolio alpha;
- CAGR advantage;
- terminal wealth over SPY.

The §9 conversion from IC to top-quintile excess **requires**:
1. bivariate normal signal and returns, with rank IC ≈ Pearson correlation;
2. a constant IC and constant cross-sectional dispersion σ_cs across months;
3. equal-weighted quintiles relative to the equal-weighted *eligible universe*, not SPY;
4. no compounding or rebalancing effects;
5. a linear relation across the whole distribution, whereas real effects are often concentrated in the tails.

Further translations are **not justifiable without returns**:
- **Universe → SPY.** The universe's own return relative to SPY is an unknown size and style tilt that can be positive or negative.
- **Quintile → investable book.** A long-only K-name book (K ≪ 165 at $100K) carries idiosyncratic tracking error that the quintile does not.
- **Gross → net.** Costs, cash drag and turnover (§14) all subtract.

**Portfolio-level evidence is weaker still.** A net edge e with tracking error TE over 7 years has t ≈ e√7 / TE:

| Edge | TE 4% | TE 6% | TE 8% | TE 10% |
|---|---|---|---|---|
| 1% | 0.66 | 0.44 | 0.33 | 0.26 |
| 2% | 1.32 | 0.88 | 0.66 | 0.53 |
| 3% | 1.98 | 1.32 | 0.99 | 0.79 |

So even a real, economically meaningful edge would not be *statistically* demonstrated at the portfolio level in 7 years. Signal-level testing is necessary but not sufficient.

**Compounding arithmetic (not forecasts).** A sustained net 0.5% / 1% / 2% / 3% a year compounds to 1.16 / 1.35 / 1.81 / 2.43× SPY's wealth over 30 years. A *weak* signal that survives costs with 0–0.5% therefore has little terminal-wealth value relative to its complexity and tracking risk.

## 14. Illustrative after-cost hurdles (frozen $7 / order, 0.10% / side; hypothetical books)

Annual cost = 2τK × $7 / capital + 2 × 0.10% × τ, where τ is the one-way annual turnover and K the number of positions. These are **not** specifications.

| Capital | Positions (trade size) | τ = 1× | τ = 2× | τ = 4× |
|---|---|---|---|---|
| $100K | 15 ($6,667) | 0.41% | 0.82% | 1.64% |
| $100K | 20 ($5,000) | 0.48% | 0.96% | 1.92% |
| $100K | 30 ($3,333) | 0.62% | 1.24% | 2.48% |
| $100K | 165 = a full quintile ($606) | 2.51% | 5.02% | 10.04% |
| $200K | 20 ($10,000) | 0.34% | 0.68% | 1.36% |
| $200K | 30 ($6,667) | 0.41% | 0.82% | 1.64% |

**Reading the table.**
- A quarterly-refreshed signal held through full replacement each quarter implies τ up to about 4×.
- A full-quintile long-only book is uneconomic at $100K.
- At 15–30 names, costs take about 0.4–2.5% a year.
- Cash drag adds to this: H017 (P2-CP13) showed costs plus cash drag can create a structural hurdle of about 2.5–3% a year.

**Bottom line.** A gross +3% top-quintile edge could plausibly shrink to about 0–2% net *before* the unknown universe-versus-SPY gap. The economically meaningful gross effect is therefore probably **above** 3% a year. That is exactly the region where detection becomes plausible, but also where the literature prior for $2B+ stocks is weakest.

## 15. Monthly versus daily versus filing-driven decisions (conceptual; nothing selected)

| Aspect | A Monthly | B Daily review opportunity | C Filing-event-driven |
|---|---|---|---|
| Latency from release (LH-CP1) | Median **18** sessions (p90 27) | Median about 2 sessions (E1) | Same as B |
| Possible decision dates, 2015–2021 | 83 | About 1,760 | About 23,000 stock-level events (≈ 68,700 × 0.337) |
| Independent time units for inference | About 45–83 months; information arrives in 28 seasons | **Not more independent**: the same 28 seasons | Same: event clustering in seasons |
| Data freshness | Mixed (about 34% fresh) | Always the newest report | By construction fresh |
| Computation | Low | Daily checks over a fundamentals store (existing hosts already observe fundamentals daily) | As B |
| Potential turnover / commissions | Batched; minimum-trade-size friendly | Same number of name changes but spread out; more small trades | As B. Each event can trigger a trade, which needs a slot / cash rule |
| Dependence | Monthly cross-sections | Overlapping event windows | Event-time clustering; needs calendar-time aggregation for valid SEs |
| Complexity | Lowest; existing frameworks | Moderate | Highest: slot, cash and conflict rules |

**Reading.**
- Faster review does **not** create more independent statistical information. It removes up to about 16 sessions of delay.
- If the OF-A effect is short-lived after the filing, that delay could remove a material part of it. This cannot be judged without returns, and earlier trading is not assumed to be more profitable.
- **Recommendation for later evaluation:** test the signal in **event time with calendar-time aggregation** (design D3-like), with a daily-review / next-open execution variant as the timing choice worth evaluating. Monthly decisions remain appropriate as the **baseline** for slowly moving fundamentals (C2 revenue trends). For a surprise / drift signal, monthly is likely to understate a short-lived effect.

## 16. Operational and QuantConnect constraints

- **The verified population is offline.** The D245 population is defined from offline SEC metadata (L0 / L1 labels, rule V). Any future QuantConnect use must upload it as a packed reference table, within the 50-file and 64,000-character limits, and without exporting QuantConnect data (licence and compliance review, D185).
- **Memory.** Data v2.1 hosts already peak at 7.6–8.2 GB on the B2-8 node. A daily-review host adds state and needs memory work first.
- **Engine.** The engine pin is unavailable (default build, digest-verified policy).
- **Costs.** One backtest node ($24 / month) means slow iteration. No purchase is needed for any of this.

## 17. Consequences of having only seven development years

- **Power.** 83 months with about 28 earnings seasons limits the test to large effects (§10).
- **Regimes.** About one market cycle is covered (2015–2021). The 2018 Q4 and 2020 episodes dominate several earlier results (H026 / H028 post-mortems). A single-cycle sample cannot separate a signal from regime luck.
- **No internal out-of-sample.** The window is the development set, and 2015–2021 has already been looked at by H026–H028. The Holdout (about 4.7 years) is the only fresh data. It has even less power and is single-use.
- **Fragility.** Half-period stability checks (RM2 gate form) split into about 3.5-year halves with about 14 seasons each. Such checks will often fail by chance even for real effects.

## 18. Data v1 versus Data v2.1 denominator

- **Coverage denominators** come from the **E981-01 (Data v1) eligible universe**, which is the same denominator as LH-CP1 to LH-CP3.
- **Identity and filing tables** come from Data v2.1.
- **The exact Data v2.1 per-stock-month universe was never exported,** so the two populations are **not** claimed identical. Market-cap repair and identity rules differ between v1 and v2.1 (P7-CP5e / CP5f), so a future in-cloud population would differ at the margin. That difference is not quantified here.

## 19. Evidence limitations and assumptions

1. Every power number is **conditional on assumed** σ_IC, ρ, σ_cs and on the information-decay model. None was estimated, and none can be without returns or Stage B.
2. The P7-CP4 factor of 1.34 comes from a different signal (Score v1), a different period and a different statistic. It is an order-of-magnitude reminder, not a calibration.
3. Normal-theory conversions ignore tail concentration, skewness and the distinction between rank and Pearson correlation.
4. The literature prior is low: PEAD has largely disappeared in large caps since about 2006 (Martineau 2022, RM2 §5).
5. The analysis is metadata-based: the population is described by counts, not by stock characteristics such as volatility or size distributions.

## 20. Final classification

**B — UNDERPOWERED FOR MODEST EFFECTS.**

**Evidence:**
- For the illustrative +3% a year top-quintile effect, 80% power is reached only under favourable assumptions (optimistic noise, or main noise with no dependence, a single 5% test and no realistic-structure penalty).
- Under realistic dependence, a conservative 1% threshold, two hypotheses and the structure penalty, power is **about 10–46%**.
- Effects of at least about **5% a year** are usually detectable; the 80%-power MDE is about 2.6–7.4% a year depending on the assumptions.

**Why not A:** A would rest on a favourable parameter set, which the owner explicitly excluded.

**Why not C:** the design is computable, the population is adequate, and strong effects remain detectable.

**Why not D:** a meaningful conditional conclusion is possible, and the remaining unknowns are listed (§10).

## 21. Is a future Stage B worthwhile?

**Not as the next step, in my judgement.** Stage B (the RM2 §13 synthetic validity study) would:
- calibrate the size of the Fama–MacBeth test under event-time updates, churn and priced correlated factors — genuinely useful, and the only way to obtain a defensible σ_IC / ρ / inflation for the design;
- **mostly confirm** what is already clear: 80% power is reached only for effects well above +3% a year.

Stage B becomes worthwhile **only if** the owner first pre-declares the economically meaningful effect at a level the history can detect (about ≥ 5% a year top-quintile gross, given the §14 cost hurdles). The owner would also have to accept that the realistic prior for an effect of that size in $2B+ US stocks is low. Otherwise Stage B would spend effort to confirm insufficient power.

## 22. Exact next owner decision required

Choose one:
1. **Stop OF-A on the existing data.** Record OF-A as "not evaluable with adequate power for modest effects under the 2015–2021 verified population". This is my recommendation if the meaningful effect is about 3% a year or less.
2. **Pre-declare a large-effect objective** (for example ≥ 5% a year top-quintile gross, or an explicit IC) and then approve Stage B (synthetic validity + power calibration; protocol frozen first). This is my recommendation only if the owner accepts the large-effect framing and its low prior.
3. **Revisit the research horizon.** This would need a separate owner decision. It could mean either:
   - a design-only feasibility review of longer histories, such as validated L2 labels for 2013–2014, which D245 excludes, or the D124 no-purchase policy for pre-2010 data;
   - a different research direction.

In every case: no signal computation, returns, backtest, Stage B or Holdout without that decision.

## 23. Confirmation: no return analysis and no synthetic experiment

- **Nothing computed:** no stock return, price, signal value, ranking, IC, regression, model or portfolio was calculated or read.
- **Nothing run:** no synthetic panel, Monte Carlo, bootstrap of real data or null world.
- **The only computations:**
  - counts from cached SEC metadata (`LH_CP4_population.py`);
  - closed-form equations on stated assumptions (`LH_CP4_power_tables.py`).
- **Cross-references:** the cluster-bootstrap helper of LH-CP3 was not used. P7-CP4 / P7-CP5f numbers are quoted from committed artifacts only.

## 24. Confirmation: the Holdout remained sealed

The 2022-01-01 → 2026-08-31 Holdout was not accessed, and `HOLDOUT_UNLOCK.md` does not exist. No information dated after 2021-12-31 was used; the population aggregates pass `assert_no_post_cutoff`. No QuantConnect run and no purchase took place.

---

**Counts.** Hypotheses tested: 0. Strategies: 0. Experiments: 0. Network requests: 0.

**STOPPED — awaiting owner review.**
