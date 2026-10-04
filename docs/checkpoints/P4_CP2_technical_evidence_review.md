# P4-CP2: Deep Technical Indicator & Strategy Evidence Review

- **Date:** 2026-10-04
- **Programme:** Phase 4 (design and research only)
- **Decision record:** D141
- **Owner direction:** "Phase 4 — Deep Technical Indicator & Strategy Evidence Review — Evidence-First Research Before Any New Backtest" (`docs/owner/2026-10-04_phase4_evidence_review.md`)
- **Sources:** `research/phase4/P4_CP2_references.md`, which holds the full reference list, verification status, source level, and the post-2017 (†) flags
- **Status:** STOP. Waiting for the owner. Nothing was built or run.

**What this report is.** A literature and evidence review. It asks which technical concepts deserve research time, and in which role and timeframe.

**What this report did not do:**
- It computed **no** indicator, return, ranking or backtest on project data.
- No archetype was tested. No grid was finalised. No optimizer was designed.
- No 2018–2021 data and no Holdout data were touched.
- There is no H019. Nothing was bought.

**Project results used.** The only project results cited are outcomes already recorded and reviewed at earlier checkpoints: the C01–C03 summary table (CP3j) and the H014, H016, H017 and H018 outcomes. They are used to classify **overlap**, not to choose parameters.

**Phase 3 results deliberately not used.** The per-family descriptive results of the Phase 3 search (2010–2017) are **not** used to rank concepts. Doing so would be selection on a search we already ran.

---

## Contents

**Preliminaries**
1. Methodology
2. Source hierarchy
3. Summary

**Concept reviews (4–17)**
4. Trend (moving averages, slope, filters)
5. Cross-sectional momentum / relative strength
6. Time-series momentum
7. 52-week high
8. Breakout / Donchian
9. RSI
10. MACD
11. ADX
12. Volatility
13. Bollinger Bands
14. Volume
15. Pullback / recovery within trends
16. Volatility contraction + breakout
17. Multi-timeframe

**Cross-cutting evidence (18–20)**
18. Post-publication persistence
19. Large-cap applicability
20. Cost / turnover

**Classification tables (21–27)**
21. Evidence matrix
22. Overlap / redundancy matrix
23. Combination matrix
24. Role classification
25. Timeframe classification
26. Exclusion list
27. Compact toolkit

**Archetypes and recommendations (28–33)**
28. Strategy archetypes
29. Comparison to H001–H018
30. Daily / Weekly / Multi-Timeframe recommendation
31. Genuinely new archetypes
32. Future research architecture
33. Owner decisions

**Final answers A–H**

---

## 1. Methodology

**Question.** Which technical concepts have enough evidence to be used, in which **role**, and at which **timeframe**? The setting is this project's universe:
- US common stocks with point-in-time market cap ≥ $2B;
- long-only, $100K, realistic costs;
- objective: terminal wealth above SPY total-return buy-and-hold (Amendment 3).

**Procedure:**
1. For each concept A–N in the owner's list, I collected the primary academic sources plus the main practitioner conventions. Bibliographic details and main findings were verified on 2026-10-04 where possible (publisher, SSRN, RePEc, NBER or author pages). Items cited from memory are marked "Memory" in the references file, and their magnitudes are not relied on.
2. Each concept is graded on six criteria:
   - (a) what it measures;
   - (b) where the evidence comes from: asset class, period, sample, size segment;
   - (c) replication and post-publication persistence;
   - (d) large-cap relevance;
   - (e) turnover and cost robustness;
   - (f) overlap with other concepts and with H001–H018.
3. Each concept gets an evidence tier and a recommended role.
4. Archetypes are built only from concepts that keep a role. Each archetype is compared with the project's history.

**Evidence tiers:**

| Tier | Meaning |
|---|---|
| **A** | Strong, replicated academic evidence (several independent samples, out-of-sample and post-publication tests, international) |
| **B** | Credible academic evidence that is mixed or conditional (holds in some segments or periods, or rests on one main paper) |
| **C** | Practitioner evidence with some academic support (index level, other assets or partial) |
| **D** | Weak: no credible peer-reviewed predictive evidence for this use, or evidence that it fails after costs or after publication |

**Two tiers per concept.** A concept can be Tier A in general and Tier B or C **for our universe**. The matrix (§21) gives both where they differ. Our universe is large caps, long-only, US, 2010+.

**Hindsight rule.** Papers marked † were published after 2017, and their samples may include 2018+ markets. Under CLAUDE.md they are used **only to downgrade or caution**, never to motivate an idea. Every concept that keeps a positive role here has pre-2018 support.

**Three distinctions kept throughout:**
- **Selection alpha vs timing.** Does the concept pick *which* stocks earn more, or *when* to be invested?
- **Alpha vs risk management.** Does it raise expected return, or mainly reduce volatility and drawdown? For a terminal-wealth objective in a mostly rising market, risk reduction usually *lowers* wealth vs SPY unless it is levered back up, and we use no leverage.
- **Information vs wrapper.** Weekly vs daily sampling, crossovers vs levels, and EMA vs SMA are often wrappers around the same information.

---

## 2. Source hierarchy

| Level | Type | How used here |
|---|---|---|
| 1 | Peer-reviewed journals (JF, JFE, RFS, JFQA, Management Science, JEF, Quantitative Finance, JPM, FAJ) | Primary evidence |
| 2 | Working papers (SSRN, NBER, conference papers) | Evidence, weighted below level 1; flagged |
| 3 | Credible quantitative books (Zakamulin; Clenow; Antonacci) | Conventions and implementation; Zakamulin also as evidence (his book summarises his peer-reviewed papers) |
| 4 | Institutional research (AQR: Hurst-Ooi-Pedersen; Man: Harvey et al.) | Evidence, aware of the authors' interests |
| 5 | Reputable practitioner books (Wilder, Appel, Bollinger, Elder, Weinstein, Connors & Alvarez, Granville) | Origin of indicators and conventions **only**; never evidence of profitability |
| 6 | Forums, SEO pages, broker and marketing pages | Popularity only. **Statistics from such pages were found and rejected**, for example "67% vs 49% win rate with multi-timeframe alignment" and "ADX improves risk-adjusted returns by 18.7%" |

Data-snooping literature is treated as first-class evidence: Sullivan-Timmermann-White 1999; Park-Irwin 2007; Bajgrowicz-Scaillet 2012. So is post-publication evidence: McLean-Pontiff 2016; Fang-Jacobsen-Qin 2017. A rule that "worked" in a large search is discounted, as Phase 3 showed in our own data.

---

## 3. Summary

1. **Only one technical concept has Tier A evidence for return generation: intermediate-horizon cross-sectional momentum.**
   - Definition: ranking stocks on roughly their past 6–12 months of return, skipping the most recent month.
   - **For our universe it is downgraded to "A in general, B for us".** It is weaker in large, well-covered stocks (Hong-Lim-Stein 2000). Published anomalies shrink after publication (McLean-Pontiff 2016). A post-2017 study (†, caution only) reports that US momentum largely faded after 2002.
2. **Long-term trend (moving averages, slope, time-series momentum) is Tier B, and mainly a risk / exposure / exit tool, not a stock-selection alpha.**
   - Its best evidence is for indices and asset classes (Brock et al.; Faber; Hurst-Ooi-Pedersen).
   - For individual stocks it works mainly in small, volatile names (Han-Yang-Zhou 2013).
   - Out of sample it mostly reduces drawdowns rather than raising returns (Zakamulin).
   - Close > MA, MA crossovers, MA slope, MACD > 0 and a positive 12-month return all carry **the same trend information** (Marshall et al. 2017; Zakamulin).
3. **Volatility is a risk tool:**
   - Volatility scaling of momentum is Tier B as risk management (Barroso-Santa-Clara 2015). It is one of the few volatility-management cases that survives out of sample (Cederburg et al. †).
   - The low-volatility anomaly is credible, but it is a different strategy. Our H005 already failed Validation.
4. **Two refinements of momentum are credible (Tier B) and are new to this project:**
   - **"frog-in-the-pan" smooth momentum:** momentum earned through many small moves persists more than momentum earned in a few jumps (Da-Gurun-Warachka 2014);
   - a **multi-horizon moving-average trend score** (Han-Zhou-Zhu 2016).
5. **A further refinement is credible but mostly tested here:**
   - **market-state conditioning:** momentum pays after up-markets, not after down-markets (Cooper-Gutierrez-Hameed 2004);
   - this resembles H002 v1.2's market filter.
6. **RSI, MACD, ADX, Bollinger Bands, the squeeze, OBV / A-D and short-horizon pullback buying lack credible evidence as stock-selection alpha for large US caps after costs (Tier D).** Most were also tested in this project and failed:
   - H001: RSI reversal;
   - H004 and H014: pullbacks;
   - H006: breakout + volume;
   - H007: squeeze;
   - H009: volume shock;
   - H018: all of them in a 1,533-configuration grammar.
7. **Multi-timeframe ("weekly trend + daily entry") has practitioner support only (Tier C/D).** The daily entry layer needs a short-term timing signal. In large caps the short-term evidence argues **against** pullback timing: reversal profits are below costs and concentrated in illiquid stocks (Avramov-Chordia-Goyal), and the largest liquid stocks show short-term *continuation* (Medhat-Schmeling †, caution). The daily layer adds degrees of freedom and turnover without an evidence base.
8. **Timeframe answer:** slow decisions, weekly or monthly, for selection, holding and exit. Daily data serves only to compute inputs and to execute at the next open. The academic evidence does not separate weekly from monthly. Pick one in advance and never search over it.
9. **Archetypes:**
   - 9 archetypes are described.
   - 3 are worth considering, all of them **momentum-family selection with slow trend-state holding**:
     - AR1: trend-filtered momentum with a trend exit (already designed in P4-CP1);
     - AR2: smooth / frog-in-the-pan momentum (substantially new);
     - AR3: multi-horizon trend score (meaningfully different).
   - 1 is a risk overlay (AR4).
   - The other 5 are mostly tested here and are not recommended.
10. **The binding constraint is statistical power, not ideas.**
    - P4-CP1 showed that a 12-stock book needs a selection edge of about 6–12% a year to pass our gates, against a plausible 0–3%.
    - The evidence reviewed here does not change that prior. Momentum in large caps after 2010 is, at best, at the low end.
    - So the next step, if any, should be **a few explicit, pre-registered hypotheses**, not an optimizer. Ideally it should start with a **universe-wide signal-level test**, which has far more power than a 12-stock book (§32).
    - **Stopping is a defensible outcome.**

---

## 4. Trend (SMA / EMA, MA slope, trend filters)

**What it measures.** Whether the price is above its own recent average, or whether that average is rising. Every MA rule is a weighted sum of past price changes (Zakamulin). SMA vs EMA, crossover vs price-above-MA, and slope differ only in the weighting.

**Evidence:**

| Source | Asset / period | Finding | Weight for us |
|---|---|---|---|
| Brock, Lakonishok & LeBaron 1992 | DJIA 1897–1986 | MA and range-break rules predicted index returns | Index level; pre-1990 |
| Sullivan, Timmermann & White 1999 | DJIA; ≈ 7,800 rules | The best rule did not persist out of sample once data snooping was controlled | Strong caution |
| Park & Irwin 2007 (review) | many | Technical profits mostly vanished in mature markets after the early 1990s | Caution |
| Faber 2007; Zhu & Zhou 2009 | Asset classes | A 10-month SMA timing rule cuts drawdowns at similar returns | **Asset-class timing, not stock selection** |
| Han, Yang & Zhou 2013 | US stock portfolios sorted by volatility | MA timing pays mainly in **high-volatility (small, illiquid)** deciles | Weak in large caps |
| Zakamulin 2017 (book and papers) | US stock index, long history | Out of sample the best MA timing is only marginally better than buy-and-hold; little or no outperformance in the second half of the sample; the main benefit is in bear markets | Expect risk reduction, not excess wealth |
| Hurst, Ooi & Pedersen 2017 | Diversified futures, 1880+ | Trend following positive in every decade; crisis alpha | Futures; diversification across asset classes, not stocks |
| Weinstein 1988 (practitioner) | Stocks | 30-week MA "stage analysis" | Convention only |

**Assessment:**
- **Tier B in general; Tier C as stock-selection alpha in our universe.**
- **Role: regime filter, exposure or exit (holding) rule.** It is not a ranking signal.
- **Horizon:** long; roughly 6–12 months (≈ 30–50 weeks, ≈ 150–250 sessions). Short MAs (20–50 sessions) add turnover and whipsaw with no better evidence.
- **Cadence:** weekly or monthly evaluation. Daily evaluation of a long MA mainly adds whipsaw trades near the line.
- **Failure regime:** sideways, choppy markets with repeated crossings (whipsaw), and sharp V-shaped recoveries (late re-entry).
- **Project history:**
  - close > SMA200 was the filter in H014, H015 (never run) and H002 v1.2;
  - T1–T3 trend primaries and the cT confirmations were in H018.
  - **None showed an edge.**

---

## 5. Cross-sectional momentum / relative strength

**What it measures.** A stock's past return *relative to other stocks*, over roughly 3–12 months, usually skipping the most recent month to avoid short-term reversal.

**Evidence:**

| Source | Finding | Weight for us |
|---|---|---|
| Jegadeesh & Titman 1993 | 3–12-month winners beat losers over the next 3–12 months | Foundational |
| Jegadeesh & Titman 2001 | Profits of similar size out of sample (1990–98); **long-run reversal in years 2–5** | Replication; holding beyond ≈ 12 months is unsupported |
| Asness, Moskowitz & Pedersen 2013 | Momentum in many countries and asset classes | Broad replication |
| Novy-Marx 2012 | Months 7–12 drive most of the profit | Prefer a 6–12-month window over 3 months |
| Hong, Lim & Stein 2000 | Weaker in large, well-covered stocks | **Our universe is the weak segment** |
| Daniel & Moskowitz 2016 | Crashes after market rebounds, mostly in the short leg | Long-only avoids much of it, not all |
| Cooper, Gutierrez & Hameed 2004 | Profits ≈ 0.93% a month after up-markets and ≈ −0.37% after down-markets (1929–95) | Market state matters |
| Blitz, Huij & Martens 2011 | Residual momentum: about double the risk-adjusted return | Tested here as H008: failed the screen |
| Da, Gurun & Warachka 2014 | "Frog in the pan": continuous information gives more persistent momentum | Refinement (§5.1) |
| McLean & Pontiff 2016 | Anomaly returns fall by about a third or more after publication | General decay |
| † Ben-David, Li, Rossi & Song (NBER 2021) | US momentum declined sharply after 2002 (≈ 0.92% → 0.16% a month in one comparison) | **Caution: the expected edge in our 2010+ sample is small** |

**Assessment:**
- **Tier A in general; Tier B in our universe.** The two downgrades are large caps and US after 2002.
- **Role: primary ranking** (which stocks to hold).
- **Horizon:** roughly 6–12 months of formation, skipping about 1 month (≈ 26–52 weeks, skipping about 4).
- **Holding:** months; profits weaken after about 12 months and may reverse.
- **Turnover:** medium. Monthly-rebalanced top-quantile books replace a large share of names each month. Turnover falls a lot with a holding rule or buffer, i.e. keep a name while it stays in the top half or its trend persists.
- **Failure regimes:**
  - sharp market reversals (momentum crashes; 2009-type rebounds);
  - narrow, rotating leadership.
- **Project history:**
  - H002: 12-1 momentum, monthly top-15. Sharpe 0.38–0.56, failed the screen.
  - H008: residual relative strength. Failed.
  - H018: M1 / M2 / M3 primaries with a fixed 63-session hold. Search failed.
  - P4-CP1: designed a fixed 26-week relative-strength ranking with a trend exit. Not run.
- **Our own momentum tests failed in 2010–2017 in several wrappers.** That is consistent with the post-2002 decay literature, not evidence against it.

### 5.1 Refinements of momentum (credible, Tier B)

| Refinement | What changes | Evidence | Project status |
|---|---|---|---|
| **Smooth / continuous momentum** ("frog in the pan") | Among winners, prefer those whose gains came from many small up-days rather than a few jumps (information-discreteness measure) | Da-Gurun-Warachka 2014 (RFS). One main paper; replications not verified here | **Never tested** |
| **Multi-horizon trend score** | Rank on an *average of price-to-MA ratios over several horizons* instead of one return window | Han-Zhou-Zhu 2016 (JFE): a trend factor that also held up in 2008, when momentum crashed | **Never tested as a composite.** Caution: the paper's factor uses *estimated* regression weights and a broad sample including small stocks. An unfitted equal-weight version is a simplification, so the evidence transfers only partly |
| **Residual momentum** | Rank on stock-specific returns | Blitz-Huij-Martens 2011 | Tested: H008 failed |
| **Market-state conditioning** | Hold momentum only after up-markets | Cooper et al. 2004 | Partly tested: H002 v1.2 had a SPY > SMA200 filter |
| **Volatility-scaled momentum** | Scale exposure by the strategy's recent volatility | Barroso-Santa-Clara 2015; Daniel-Moskowitz 2016 | Partly: H012 was withdrawn for lack of power. This is risk management (§12) |

---

## 6. Time-series momentum

**What it measures.** A stock's (or asset's) *own* past return sign: long if the past ~12-month return is positive.

**Evidence:**
- Moskowitz, Ooi & Pedersen 2012: strong in diversified futures.
- Hurst-Ooi-Pedersen 2017: a century of trend-following evidence (futures).
- **For individual stocks, cautions:**
  - Marshall et al. 2017: TSMOM ≈ MA rules (same information).
  - † Huang et al. 2020: little time-series predictability asset by asset.
  - † Goyal & Jegadeesh 2018: the TSMOM vs cross-sectional difference is mostly a time-varying net long position, i.e. market timing.

**Assessment:**
- **Tier B for futures / asset classes; Tier C for single stocks.**
- **Role:** the same as trend (§4): an absolute filter, exposure or exit rule. It is **not** independent of a moving-average filter (high overlap).
- **Horizon:** about 12 months.
- **Do not count a positive 12-month return and close > SMA as two separate confirmations.**
- **Project history:**
  - M2 / M3 primaries and the cM_r126 / cM_r252s confirmations in H018;
  - the P4-CP1 grammar's "direction group".

---

## 7. 52-week high

**What it measures.** How close the price is to its 12-month high. Investors anchor on the high and under-react near it.

**Evidence:**
- George & Hwang 2004: nearness to the 52-week high dominated past returns as a predictor and reversed less (equal-weighted sample, 1963–2001).
- † Barroso & Wang 2021 (working paper; caution): the effect is **limited to small stocks**, and price momentum explains 52-week-high momentum.

**Assessment:**
- **Tier B in general; Tier C for large caps.**
- **Role:** an alternative *ranking* to momentum, or a confirmation. It overlaps strongly with momentum: stocks near their high are usually recent winners.
- **Horizon:** 12 months, by definition.
- **Turnover:** low to medium.
- **Project history:**
  - H003: Sharpe 0.14–0.73, failed the screen;
  - B1 primaries and the cB_hi252 confirmation in H018.
- **Not recommended** as a separate archetype.

---

## 8. Breakout / Donchian

**What it measures.** The price crosses above its N-day high (Donchian channel).

**Evidence:**
- Brock et al. 1992: range-break rules on the DJIA.
- Donchian / "Turtle" rules are a staple of *futures* trend following (practitioner; Hurst et al. for the general family).
- Sullivan-Timmermann-White 1999 (snooping) and Bajgrowicz-Scaillet 2012 (no persistent rule after false-discovery control and costs) caution.
- No credible peer-reviewed evidence was found that short-window breakouts select large-cap US stocks profitably after costs.

**Assessment:**
- **Tier C / D for stock selection.**
- A **long-window** breakout (≈ 12 months) is nearly the 52-week-high concept (§7). A **short-window** breakout (20–55 sessions) is an entry-timing device with high turnover and no evidence for our universe.
- **Role:** at most entry timing within a trend book; not recommended.
- **Project history:**
  - H006: breakout + volume, Sharpe 0.74–0.90, failed;
  - B1 primaries in H018.

---

## 9. RSI

**What it measures.** The ratio of average up-moves to average down-moves over n sessions, scaled to 0–100 (Wilder 1978). It is used in two opposite ways:
1. **Overbought / oversold (30/70, or RSI(2) ≤ 10):** a short-term *reversal* bet.
2. **RSI > 50–60:** a *momentum / trend confirmation*, which is just recent relative strength.

**Evidence:**
- Chong & Ng 2008: MACD and RSI rules beat buy-and-hold on the UK FT30 **index** over 60 years. This is index timing, without a central cost treatment.
- No credible peer-reviewed evidence was found for RSI as a large-cap US *stock selector*. Practitioner RSI(2) pullback rules (Connors & Alvarez 2008) are level 5.
- Use 1, reversal, inherits the short-term reversal literature:
  - profits are smaller than costs and concentrated in illiquid stocks (Avramov-Chordia-Goyal 2006);
  - they are compensation for providing liquidity, which pays in turmoil (Nagel 2012);
  - † Medhat-Schmeling 2022 (caution): the largest, most liquid stocks show short-term **continuation**, not reversal.
- Use 2, confirmation, is redundant with momentum.

**Assessment:**
- **Tier D as standalone alpha for our universe.**
- **Role: not used.** Use 1 has no large-cap after-cost evidence; use 2 duplicates momentum.
- **Weekly RSI vs daily RSI** changes only the horizon: weekly RSI(14) ≈ a 3-month relative-strength measure, already covered by momentum.
- **Project history:**
  - H001: RSI oversold reversal; 4 of 5 lost money, cost drag 6–14% a year;
  - R1 primaries and cM_rsi / cR_rsi5 confirmations in H018.

---

## 10. MACD

**What it measures.**
- The MACD line = EMA(12) − EMA(26). "MACD > 0" is exactly an EMA(12) > EMA(26) crossover.
- The signal-line cross (MACD vs its 9-period EMA) measures *acceleration* of a short trend.

**Evidence:**
- Chong & Ng 2008 (index level, UK).
- Zakamulin shows every MA-based rule, MACD included, is a weighted sum of past price changes, so MACD carries no information beyond MA trend rules.
- No credible large-cap stock-selection evidence was found.

**Assessment:**
- **Tier D.**
- **Redundant** with short MA crossovers; the acceleration variant has no evidence.
- **Role: not used.**
- **Project history:** cT_macd0 and cM_macdsig confirmations in H018.

---

## 11. ADX

**What it measures.** The *strength* of a trend, not its direction (Wilder 1978). It is a smoothed ratio of directional movement to true range.

**Evidence:**
- No peer-reviewed predictive evidence for stocks was found.
- Search results claiming large improvements (for example "+18.7% risk-adjusted") were unattributed SEO statistics and were rejected (level 6).

**Assessment:**
- **Tier D.**
- **Role: not used.** A trend-strength confirmation duplicates the distance-from-MA or momentum magnitude, which already measures trend strength.
- **Project history:** the cT_adx confirmation in H018.

---

## 12. Volatility

There are four separate uses. They must not be mixed.

| Use | What it is | Evidence | Tier | Role |
|---|---|---|---|---|
| **Low-volatility anomaly** (select low-vol stocks) | Alpha / defensive selection | Ang et al. 2006; Baker-Bradley-Wurgler 2011 (large caps); Frazzini-Pedersen 2014 | **A / B** (replicated; partly a beta / leverage-constraint effect) | A separate strategy, not a technical add-on. **H005 passed the screen and failed Validation** (frozen; may not be re-validated on 2018–2021) |
| **Volatility filter on a selection book** (exclude the most volatile names) | Risk filter | Indirect: lottery / high-idiosyncratic-volatility stocks underperform (Ang et al.) | B as risk | **Risk filter.** H013 (lottery avoidance) failed; the H018 risk axis showed no edge |
| **Volatility-scaled momentum** (scale exposure down when the book's volatility is high) | Risk management | Barroso-Santa-Clara 2015; Daniel-Moskowitz 2016; Moreira-Muir 2017 (in sample); † Harvey et al. 2018 (raises Sharpe and cuts tails); † Cederburg et al. 2020 (caution: most volatility management fails out of sample, **momentum is an exception**) | **B (risk)** | Exposure / sizing. **Without leverage it can only reduce exposure**, which lowers terminal wealth in rising markets. Relevant to the wealth objective only through avoiding crashes |
| **Volatility-based position sizing** (inverse-volatility weights) | Risk balance | Practitioner (Clenow) | C | Optional sizing; changes risk more than return |

**Horizon:**
- volatility for scaling: about 1–6 months of daily returns;
- volatility for low-vol selection: from 1 month to several years (rankings are very persistent).

**Turnover:** low, if evaluated weekly or monthly.

**Conclusion.** Volatility is a **risk tool** here. It is not a new alpha source; its alpha version (H005) is already spent.

---

## 13. Bollinger Bands (mean reversion, squeeze, bandwidth)

**What it measures.**
- The price relative to a moving average ± k standard deviations: %b, the position within the bands.
- Bandwidth: the band width relative to the average, i.e. volatility.

**Evidence:**
- Lento-Gradojevic-Wright 2007: Bollinger rules unprofitable after costs (US and Canadian indices, FX, 1995–2004).
- Fang-Jacobsen-Qin 2017: the bands had predictive ability **before** their popularisation, which disappeared after Bollinger's 2001 book. This is a clean post-publication decay case.
- The "squeeze" (low bandwidth followed by a breakout) is practitioner-only.

**Assessment:**
- **Tier D.**
- %b is a short-term reversal measure (same caveats as §9 and §15). Bandwidth is just volatility (§12).
- **Role: not used.**
- **Project history:**
  - H007: squeeze; passed the screen, then failed robustness (5/8 plateau);
  - R3 primaries in H018.

---

## 14. Volume (relative volume, OBV, accumulation / distribution, breakout confirmation)

**What it measures.** Trading activity. OBV and A/D are cumulative signed-volume indicators (Granville 1963; practitioner).

**Evidence:**
- Gervais-Kaniel-Mingelgrin 2001: unusually high volume over a day or week precedes higher returns over the next month (a visibility effect).
- Lee-Swaminathan 2000: high-volume winners reverse sooner over long horizons; low-turnover firms earn more. **The sign of "volume confirms momentum" is ambiguous**, or even negative at long horizons.
- No credible peer-reviewed evidence was found that OBV or A/D add predictive power in large caps.

**Assessment:**
- **Tier B / C** for the high-volume premium, which is a separate event effect.
- **Tier D** for OBV / A-D and for volume as a breakout or trend confirmation.
- **Role: not used** in a slow trend / momentum book.
- **Project history:**
  - H006: breakout + volume, failed;
  - H009: volume shock, failed (Sharpe 1.01 vs a bar of 1.02);
  - the cP_rv confirmation in H018.

---

## 15. Pullback / recovery within trends

**What it measures.** A short-term dip, by RSI, distance below a short MA, or %b, inside a longer uptrend. The bet is that the dip reverses while the trend continues.

**Evidence:**
- It is the intersection of two literatures:
  - short-term reversal: Jegadeesh 1990; Lehmann 1990;
  - medium-term momentum.
- In the short-term reversal literature:
  - Avramov-Chordia-Goyal 2006: reversal profits are concentrated in illiquid stocks and are smaller than likely costs;
  - Nagel 2012: they are a liquidity-provision premium, earned mainly in turmoil;
  - Da-Liu-Schaumburg 2014: reversal is stronger within industries and after removing news, which we cannot observe without news data;
  - † Medhat-Schmeling 2022 (caution): in large, high-turnover stocks, 1-month returns *continue*.
- Practitioner support: Connors & Alvarez's RSI(2) rules (level 5).

**Assessment:**
- **Tier D for large caps after costs.**
- **Role: not used** as an entry-timing layer.
- **Project history: the most heavily tested idea in this programme, and it failed every time:**
  - H001: RSI reversal;
  - H004: pullbacks in momentum leaders;
  - H014: trend + pullback + recovery (Phase 2);
  - R1–R3 primaries and cR confirmations in H018.

---

## 16. Volatility contraction + breakout

**What it measures.** A period of compressed range (low ATR or bandwidth, "VCP" or "squeeze") followed by a breakout.

**Evidence:**
- Practitioner only: Bollinger's squeeze; popular trading-book "volatility contraction patterns".
- Volatility clustering is real (the GARCH literature), but a *directional* forecast after contraction was not found in peer-reviewed work for stocks.
- Lo-Mamaysky-Wang 2000 show that pattern signals change the conditional distribution of returns. They do not show an after-cost strategy.

**Assessment:**
- **Tier D.**
- **Role: not used.**
- **Project history:** H007 (failed robustness).

---

## 17. Multi-timeframe

**What it is.** The higher timeframe defines the trend (weekly). The lower timeframe times entries and exits (daily). Elder's "triple screen" (1993) is the canonical practitioner version.

**Evidence:**
- **No peer-reviewed study** of multi-timeframe stock-selection rules was found.
- Statistics found online ("67% vs 49% win rate when timeframes align") are unattributed SEO and were rejected.
- The academic support for each layer must therefore be judged separately:
  - **Weekly trend layer:** Tier B / C as an exposure / exit rule (§4).
  - **Daily entry layer:** in practice an oscillator pullback or a short breakout. Both are Tier D for large caps (§9, §15, §8).

**Structural costs:**
- More parameters, so more degrees of freedom (the Phase 3 lesson).
- More turnover from the daily layer.
- A daily entry delay can *miss* trend entries.
- For a weekly trend signal the information is the same whether it is read on Friday or on a daily chart. Daily data adds only *timing precision*. That is valuable only if short-term timing has an edge, and in large caps the evidence says it does not.

**Assessment:**
- **Tier C / D.**
- **Role: an architecture choice, not an alpha.**
- The defensible form is "slow decisions; daily only for input computation and next-open execution". This is not a daily *signal* layer.

---

## 18. Post-publication persistence

| Concept | Publication | Post-publication evidence | Verdict |
|---|---|---|---|
| Cross-sectional momentum | 1993 | Jegadeesh-Titman 2001: persisted 1990–98. McLean-Pontiff: anomalies generally decay by a third or more. † Ben-David et al.: sharp US decay after 2002 | **Persisted for about a decade, then weakened in the US** |
| 52-week high | 2004 | † Barroso-Wang: limited to small stocks | Weak where we trade |
| MA / trend rules (stocks) | Brock et al. 1992 | Sullivan-Timmermann-White 1999; Park-Irwin 2007: profits vanished in mature markets after the early 1990s | **Decayed** |
| MA / trend (asset classes, futures) | Faber 2007; Moskowitz et al. 2012 | Hurst et al. 2017 (century); † Huang et al. 2020 (caution) | Holds better for futures than for single stocks |
| Bollinger Bands | 2001 (book) | Fang-Jacobsen-Qin 2017: predictive ability lost after popularisation | **Decayed** |
| Technical rules generally | — | Bajgrowicz-Scaillet 2012: no persistent outperformance after false-discovery control and costs | **Decayed** |
| Volatility-managed portfolios | Moreira-Muir 2017 | † Cederburg et al. 2020: mostly fail out of sample; momentum an exception | Survives for momentum (risk) |
| Low volatility | Ang et al. 2006; Baker et al. 2011 | Widely implemented (crowding); in our own Validation H005 failed | Uncertain |
| Short-term reversal | 1990 | Avramov et al. 2006; Nagel 2012: illiquid, cost-bound | Not exploitable in large caps |

**Lesson.** The more popular and the easier to compute a rule is, the more its published edge has decayed. Indicator-based rules from trading books (RSI, MACD, Bollinger, ADX) are the most exposed. Momentum survived longest because it carries risk (crashes) and is costly to trade, but in the US it too has weakened.

---

## 19. Large-cap applicability (≥ $2B)

| Concept | Large-cap evidence | Main problem |
|---|---|---|
| Cross-sectional momentum | Present but weaker (Hong-Lim-Stein) | Smaller edge; post-2002 decay |
| Smooth momentum (frog in the pan) | Not separately verified for large caps here | Unknown: verify before relying on it |
| Multi-horizon trend score | Not separately verified; the paper's sample includes small stocks | Unknown: verify |
| Trend / MA on stocks | Weak (Han-Yang-Zhou: high-volatility small stocks) | Risk reduction only |
| Time-series momentum on stocks | Weak (†Huang et al.; Goyal-Jegadeesh †) | Mostly a net long exposure |
| 52-week high | Weak († Barroso-Wang) | Small-stock driven |
| Low volatility | Present (Baker-Bradley-Wurgler) | H005 failed Validation |
| Volatility-scaled momentum | Applies to the book, so size-agnostic | Lowers exposure without leverage |
| Short-term reversal / pullbacks | **Negative**: illiquid stocks only; continuation in large liquid stocks (†) | Costs |
| Breakout (short) / RSI / MACD / ADX / Bollinger / OBV | None credible | — |

Evidence driven mainly by microcaps is downgraded throughout. Our ≥ $2B universe sits in the segment where most technical effects are weakest.

---

## 20. Cost / turnover

**Turnover classes:**

| Class | Holding / rebalance | Typical concepts |
|---|---|---|
| Very low | Holding of 6 months or more; annual review | Low volatility; quality |
| Low | Quarterly; trend-state holds lasting months | Trend-state exits evaluated weekly or monthly; 52-week high |
| Medium | Monthly rebalance of a top-quantile ranking | Cross-sectional momentum (less with buffers or holding rules) |
| High | Weekly signals with short holds | Short breakouts; weekly oscillators |
| Very high | Daily signals, holds of days | RSI(2) pullbacks; gaps; short-term reversal |

**Project-measured cost drag** (C01–C03, $7 an order plus slippage; recorded at CP3j, cited here only to show scale):
- H001 (RSI reversal, daily): **6.4–14.0% a year**.
- H004 (pullbacks): 4.1–7.5% a year.
- H002 (monthly momentum): 0.7–1.3% a year.
- H005 (low volatility): 0.5–1.1% a year.

**At $100K:**
- With about 12 positions of roughly $8K, the $7 commission alone is ≈ 0.09% per side before slippage.
- **Any concept in the "high" or "very high" class needs a large gross edge just to break even.** No such edge is credible in large caps.

**Implication.** Only low- or medium-turnover concepts are cost-robust here: slow momentum, slow trend states and volatility. Daily timing layers are not.

---

## 21. Evidence matrix

| Concept | Tier (general / ours) | Best role | Best horizon | Turnover | Large-cap evidence | Cost robustness | Overlap (main) | Recommended? |
|---|---|---|---|---|---|---|---|---|
| Cross-sectional momentum (6–12-1) | **A / B** | Ranking (primary) | 6–12 months, skip ~1 | Medium | Weaker; post-2002 decay † | Good if slow | 52-week high; TSMOM; trend | **Yes**: the core alpha candidate |
| Smooth momentum (frog in the pan) | B / B? | Ranking refinement | 12 months (daily inputs) | Medium | Unverified | Good if slow | Momentum (high, by construction) | **Yes, as a variant** |
| Multi-horizon trend score | B / B? | Ranking (alternative) | Several horizons, long weighted | Medium | Unverified | Medium (short MAs add turnover) | Momentum; trend | **Yes, as a variant** (long horizons only) |
| Long-term trend (MA, slope) | B / C | Exit / holding rule; regime filter | 6–12 months (30–50 weeks) | Low | Weak as alpha | Good at weekly / monthly | TSMOM; MACD; momentum | **Yes, as an exit / risk rule only** |
| Time-series momentum | B / C | Same as trend | 12 months | Low | Weak | Good | Trend (≈ identical) | Only as the trend rule (not both) |
| Market state (index trend / past return) | B / B | Portfolio exposure | 12 months / 10-month MA | Very low | Index-level, size-free | Good | Trend applied to SPY | **Optional** (tested in H002 v1.2) |
| Volatility scaling / filter | B (risk) | Risk / sizing | 1–6 months | Low | Size-agnostic | Good | Low-vol | **Yes, as risk only** |
| Low volatility (as alpha) | A–B / B | Separate strategy | 1 month – years | Very low | Present | Very good | Volatility filter | No (H005 spent) |
| 52-week high | B / C | Ranking / confirmation | 12 months | Low–medium | Weak † | Good | Momentum (high) | No (H003; small-cap) |
| Breakout / Donchian | C–D / D | Entry timing | 20–250 sessions | Medium–high | None | Poor if short | 52-week high (long window) | No (H006) |
| RSI (overbought / oversold) | C (index) / D | — | Days–weeks | High–very high | Negative | Poor | Reversal; Bollinger %b | **No** (H001) |
| RSI > 50 (confirmation) | D | — | Weeks | — | — | — | Momentum (high) | No: redundant |
| MACD | C (index) / D | — | Weeks | Medium–high | None | Poor | MA crossovers (≈ identical) | No |
| ADX | D | — | Weeks | — | None | — | Distance from MA / momentum magnitude | No |
| Bollinger mean reversion / %b | D (decayed) | — | Days–weeks | High | None | Poor | RSI; reversal | No |
| Squeeze / bandwidth / volatility contraction | D | — | Weeks | Medium–high | None | Poor | Volatility | No (H007) |
| Volume / OBV / A-D | B–C (event) / D (confirmation) | — | Days–month | High | Weak | Poor | Event effects | No (H006, H009) |
| Pullback / recovery | D | — | Days–weeks | High–very high | Negative † | Poor | Reversal; RSI | **No** (H001, H004, H014) |
| Multi-timeframe (weekly trend + daily timing) | C–D | Architecture | — | Higher than single slow | None | Worse | Trend + pullback | No (as a signal layer) |

"?" = the tier for our universe is not verified. The paper's sample was broad, and the large-cap result must be checked before relying on it.

---

## 22. Overlap / redundancy matrix

**H** = high (largely the same information) · **M** = medium · **L** = low · **C** = complementary (different jobs; low information overlap)

| | XS-mom | Smooth-mom | Trend-score | MA trend | TSMOM | 52w-high | Breakout | RSI | MACD | ADX | Vol | Volume | Pullback |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **XS-mom** | — | H | H | M | M | H | M | M | M | L | C | L | L (opposite) |
| **Smooth-mom** | | — | M | M | M | M | L | L | L | L | M | L | L |
| **Trend-score** | | | — | H | H | M | M | M | H | M | L | L | L |
| **MA trend** | | | | — | H | M | M | M | H | M | L | L | C* |
| **TSMOM** | | | | | — | M | M | M | H | L | L | L | L |
| **52w-high** | | | | | | — | H | M | M | L | M | L | L |
| **Breakout** | | | | | | | — | M | M | M | M | M | L |
| **RSI** | | | | | | | | — | M | L | L | L | H |
| **MACD** | | | | | | | | | — | M | L | L | M |
| **ADX** | | | | | | | | | | — | M | L | L |
| **Vol** | | | | | | | | | | | — | M | L |
| **Volume** | | | | | | | | | | | | — | L |

**Reasons for the key cells:**
- **XS-mom / 52w-high: H.** Stocks near their 12-month high are mostly 12-month winners. † Barroso-Wang report that momentum explains the 52-week-high effect.
- **MA trend / TSMOM / MACD / trend-score: H.** Every MA-based rule is a weighted sum of past price changes (Zakamulin). Marshall et al. 2017: TSMOM ≈ MA rules. MACD > 0 is an EMA crossover.
- **XS-mom / MA trend: M.** Different questions: relative rank vs own direction. In a broad rally most stocks pass the trend test, so trend alone cannot rank. Combined they are **complementary in job**: a ranking plus a holding / exit rule.
- **XS-mom / Vol: C.** Volatility does a different job: risk scaling or filtering. Momentum winners tend to be more volatile, so a volatility filter changes the momentum book's composition (moderate interaction).
- **RSI / Pullback: H.** Oversold RSI is the usual pullback trigger.
- **XS-mom / Pullback: L (opposite).** A pullback buys short-term *losers* among medium-term winners. That mixes two effects with opposite signs, and the short-term one is the side with weak large-cap evidence.
- **MA trend / Pullback: C\*.** Complementary only in the practitioner sense ("buy dips in uptrends"). The evidence for the pullback half is weak (§15).
- **Breakout / 52w-high: H** for long windows; M for short windows.
- **ADX / trend-score: M.** Both measure trend strength in different units.

**Practical rule.** Never count two signals from an H cell as independent confirmations.

---

## 23. Combination matrix

| Combination | Economically rational? | Academic support | Practitioner support | Complementary or redundant? | Tested in this project | Verdict |
|---|---|---|---|---|---|---|
| **Trend filter + momentum ranking** | Yes: rank by relative strength; hold only while the stock's own trend persists | Indirect: momentum (A) + trend as risk / exit (B). No direct peer-reviewed test for large-cap long-only books found | Strong (Clenow; Antonacci for asset classes) | **Complementary** (different jobs) | Partly: H002 (fixed monthly rebalance), H018 (fixed 63-session hold), P4-CP1 (designed, not run) | **Most defensible combination** |
| **Momentum + smoothness (frog in the pan)** | Yes: continuous information is under-reacted to more | Da-Gurun-Warachka 2014 | Little | Refinement (same family) | No | **Worth a pre-registered test** |
| **Momentum + market state** | Yes: momentum works after up-markets | Cooper et al. 2004 | Common (index filter) | Complementary (timing vs selection) | H002 v1.2 (SPY > SMA200) | Optional; mostly tested |
| **Momentum + volatility scaling** | Yes: lowers crash exposure | Barroso-Santa-Clara; Daniel-Moskowitz; † Cederburg (survives for momentum) | Common (Clenow sizing) | **Complementary** (alpha + risk) | H012 withdrawn (power) | **As a risk overlay only**; lowers exposure without leverage |
| **Momentum + 52-week high** | Partly | George-Hwang (52-week high subsumes momentum, equal-weighted); † Barroso-Wang (the reverse, small stocks) | Some | **Redundant** | H003 | No |
| **Trend + pullback** | Practitioner logic ("buy dips in uptrends") | Weak: the pullback half has no large-cap after-cost support | Strong (Connors) | Complementary in form, weak in evidence | H004, H014, H018 | **No**: exhausted |
| **Trend + volatility filter** | Yes, as risk control | Indirect (low-vol, vol-managed) | Common | Complementary | H018 risk axis | As risk only |
| **Breakout + volume** | Practitioner logic (participation) | Weak or ambiguous sign (Lee-Swaminathan) | Strong | Partly redundant (both are event-ish) | H006 | **No** |
| **Weekly trend + daily timing** | Practitioner logic (Elder) | None found | Strong | Adds a short-horizon layer with weak evidence | H004 / H014 in spirit; H018 (trend confirmation + pullback primary) | **No**: daily timing has no large-cap support |
| **RSI + MACD** | Little: both are short-horizon price transforms | Index-level only (Chong-Ng) | Popular | **Redundant** | H018 confirmations | No |
| **ADX + trend** | Little: ADX restates trend strength | None found | Popular | Redundant | H018 | No |
| **Volatility contraction + breakout** | Practitioner logic | None found for stocks | Popular | — | H007 | No |

---

## 24. Role classification

| Concept | Primary / ranking | Confirmation | Entry timing | Exit / holding | Risk filter / sizing | Not used |
|---|---|---|---|---|---|---|
| Cross-sectional momentum (6–12-1) | **●** | | | | | |
| Smooth momentum | **●** (refined ranking) | | | | | |
| Multi-horizon trend score | **●** (alternative ranking) | | | | | |
| Long-term trend (MA / slope) | | ○ (eligibility) | | **●** | ○ | |
| Time-series momentum | | | | ● (only if used *instead* of the MA trend) | | |
| Market state (index trend) | | | | | **●** (portfolio exposure) | |
| Realised volatility | | | | | **●** | |
| Low volatility (alpha) | | | | | | ● (H005 spent) |
| 52-week high | | | | | | ● (redundant, small-cap) |
| Breakout / Donchian | | | | | | ● |
| RSI | | | | | | ● |
| MACD | | | | | | ● |
| ADX | | | | | | ● |
| Bollinger / squeeze | | | | | | ● |
| Volume / OBV / A-D | | | | | | ● |
| Pullback / recovery | | | | | | ● |
| Multi-timeframe | (architecture choice, §30) | | | | | |

● = recommended role · ○ = acceptable secondary role.

**Gap in the evidence.** No credible evidence supports any **entry-timing** layer in our universe. Entries should simply happen at the next open after a slow selection decision.

---

## 25. Timeframe classification

| Concept | Horizon in the evidence | Input data | Decision cadence | Broad lookback range |
|---|---|---|---|---|
| Cross-sectional momentum | Monthly formation and holding (3–12 months) | Daily or monthly closes | Monthly (or weekly with a holding buffer) | 6–12 months, skip ≈ 1 month |
| Smooth momentum | Monthly | **Daily** returns (share of up vs down days) | Monthly / weekly | ≈ 12 months |
| Multi-horizon trend score | Monthly, in the paper | Daily closes | Monthly / weekly | Several MAs from ~1 month to ~1 year (long end only, to limit turnover) |
| Long-term trend | Monthly (Faber) or weekly (Weinstein) | Daily / weekly closes | Weekly or monthly | 30–50 weeks / 7–12 months |
| Time-series momentum | Monthly | Monthly returns | Monthly | ≈ 12 months |
| Market state | Monthly | Index closes | Monthly / weekly | 10–12 months |
| Volatility scaling / filter | Daily returns aggregated | Daily | Weekly / monthly | 1–6 months |
| Execution | — | Daily | Next session's open after the decision | — |

**No result depends on a precise lookback.** Ranges are given on purpose. Any future test must pre-register **one** conventional value per concept and treat neighbours only as robustness checks, never as a search.

---

## 26. Exclusion list

| Excluded | Reason |
|---|---|
| RSI overbought / oversold (30/70; RSI(2) ≤ 10) | Short-term reversal: below costs and in illiquid stocks (Avramov et al.); liquidity premium (Nagel); † large liquid stocks continue (Medhat-Schmeling). H001 failed with 6–14% a year cost drag |
| RSI > 50 / 60 as confirmation | Redundant with momentum |
| MACD crossovers / histogram | Equivalent to EMA crossovers (Zakamulin); index-level evidence only |
| ADX thresholds | No peer-reviewed predictive evidence; the claims found were SEO |
| Bollinger mean reversion / %b | Unprofitable after costs (Lento et al.); decayed after popularisation (Fang et al.) |
| Squeeze / volatility contraction → breakout | Practitioner only; H007 failed robustness |
| Volume confirmation, OBV, A/D | Ambiguous sign (Lee-Swaminathan); no credible large-cap evidence; H006 and H009 failed |
| Short MA crossovers (e.g. 5/20, 10/50 days) | Turnover and whipsaw; no evidence beyond long MAs; decayed (Park-Irwin) |
| Short Donchian breakouts (20–55 days) | Futures convention; no stock-selection evidence; H006 |
| Pattern recognition (head-and-shoulders, flags, VCP) | Lo-Mamaysky-Wang: changes the distribution, not shown profitable after costs |
| Pullback / dip-buying timing layers | §15; H001, H004, H014 and H018 failed |
| Daily timing under a weekly trend (MTF) | §17: no evidence; adds degrees of freedom and turnover |
| 52-week-high ranking as a separate strategy | Redundant with momentum; small-cap driven (†); H003 |
| Residual momentum as a new hypothesis | Already tested (H008) |
| Gap and seasonality rules | Already tested (H010, H011) |
| Any broad multi-indicator optimizer | The Phase 3 lesson: no-edge worlds always produce SPY-beating "best" configurations |

---

## 27. Compact toolkit

**Alpha (selection) concepts, 2–3:**
1. **Cross-sectional intermediate momentum:** 6–12-month return, skipping about 1 month.
2. **Smooth momentum:** momentum restricted to, or tilted towards, stocks with continuous gains (frog in the pan).
3. **Multi-horizon trend score:** an equal-weighted average of price-to-MA ratios at long horizons. An alternative ranking that is not fitted to the data.

These three are **variants of one information family** (past returns). They are *not* three independent alpha sources. At most one should be the primary ranking of any hypothesis.

**Supporting / timing concepts, 2:**
1. **Long-term trend state** (≈ 40-week / 10-month MA, or the 12-month sign) as the **holding and exit rule**: hold while the trend persists, so winners can run with low turnover.
2. **Slow decision cadence** (weekly or monthly) with next-open execution. This is a rule, not an indicator.

**Risk concepts, 1–2:**
1. **Realised volatility:** a filter (exclude the most volatile names) or sizing / book-level scaling.
2. **Market state:** an index trend or past return for portfolio exposure. Optional: without leverage it lowers exposure and usually lowers terminal wealth vs SPY in rising markets.

**Everything else is excluded (§26).**

---

## 28. Strategy archetypes

For each archetype:
- **Overlap** is with H001–H018 and P4-CP1.
- **Distinct?** answers whether it is distinct enough to deserve a test.

### AR1: Trend-filtered momentum with a trend-state exit

- **Economic hypothesis:** stocks with strong intermediate-term relative strength keep outperforming (under-reaction, disposition effect). Holding them while their own long-term trend persists lets winners run at low turnover.
- **Signals:**
  - primary: cross-sectional 6–12-1 momentum rank;
  - confirmation (eligibility): close above its long-term MA.
- **Entry / exit:**
  - entry: buy the top-ranked eligible names at the next open when a slot is free;
  - exit: sell when the long-term trend state turns negative (slow cadence).
- **Timeframe and holding:** weekly or monthly decisions; holds of months.
- **Turnover:** low to medium.
- **Failure regime:** momentum crashes (sharp rebounds), choppy markets (whipsaw exits), narrow leadership.
- **Overlap:** **partial**.
  - Momentum information: H002, H008, H018 M1.
  - Trend filter: H015 (never run), H018 cT.
  - New: the trend-state exit with relative-strength ranking, which is **exactly the P4-CP1 design**.
- **Evidence:** A / B (momentum) + B / C (trend as exit).
- **Distinct?** Only in the holding / exit structure. It is already fully designed (P4-CP1), with a power study showing that a ≈ 6–12% a year edge is needed.

### AR2: Smooth ("frog-in-the-pan") momentum

- **Economic hypothesis:** investors under-react more to information that arrives gradually, in many small moves, than to salient jumps. Momentum built from continuous small gains is more persistent (Da-Gurun-Warachka 2014).
- **Signals:**
  - primary: 12-1 momentum rank restricted to, or tilted towards, stocks whose up-days outnumber down-days most consistently (information-discreteness measure);
  - confirmation: none needed (it *is* the confirmation).
- **Entry / exit:** monthly (or weekly) reselection at the next open. Exit by reselection, or by AR1's trend-state rule.
- **Timeframe:** monthly decisions; daily inputs only to compute the measure.
- **Holding:** months.
- **Turnover:** medium.
- **Failure regime:** the same as momentum; possibly fewer crash-prone names, since jump-driven winners are excluded.
- **Overlap:** **substantially new** in mechanism. No previous hypothesis used the *path* of past returns. The information family (past returns) is shared with H002 and H008.
- **Evidence:** B (one main peer-reviewed paper, pre-2018; large-cap persistence not verified here).
- **Distinct?** Yes. It is the most distinct concept left in the technical family.

### AR3: Multi-horizon trend score

- **Economic hypothesis:** investors react to trend information at several horizons. A composite of price-to-MA ratios captures trend persistence more robustly than any single window (Han-Zhou-Zhu 2016).
- **Signals:**
  - primary: rank on the *equal-weighted* average of price / MA(L) − 1 over a few pre-set long horizons (no fitted coefficients);
  - confirmation: none.
- **Entry / exit:** monthly or weekly reselection at the next open; optionally AR1's trend-state exit.
- **Timeframe:** monthly or weekly.
- **Holding:** months.
- **Turnover:** medium (more if short horizons are included, which is why they are excluded).
- **Failure regime:** trend reversals. The paper reports resilience in 2008, when momentum crashed.
- **Overlap:** **meaningfully different** as a ranking. H018 had single-window trend *conditions* ranked by their own strength, not a multi-horizon composite. The information overlaps strongly with momentum.
- **Evidence:** B for the paper's fitted factor. **Less for an unfitted large-cap version**, because the evidence transfers only partly.
- **Distinct?** Moderately. It is a sensible alternative ranking to AR1 / AR2, not a new information source.

### AR4: Risk-managed momentum book (volatility scaling / volatility filter)

- **Economic hypothesis:** momentum's risk is predictable. Scaling the book down when its realised volatility is high avoids crashes without giving up much return (Barroso-Santa-Clara 2015).
- **Signals:**
  - primary: any of AR1–AR3;
  - risk overlay: book-level exposure scaled by realised volatility (no leverage, so ≤ 100%), and / or exclusion of the most volatile names.
- **Entry / exit:** as the underlying book; exposure reviewed weekly or monthly.
- **Timeframe:** the underlying book's.
- **Turnover:** low additional turnover.
- **Failure regime:** volatility spikes followed by fast rebounds (de-risked at the bottom); long calm bull markets (no benefit; cash drag).
- **Overlap:** **partial**. H012 (volatility-managed exposure) was withdrawn for lack of power; the H018 risk axis; H005 / H013 (stock-level volatility).
- **Evidence:** B as risk management.
- **Distinct?** Not as alpha. It is a **risk overlay** whose benefit cannot be confirmed with our power (the H012 lesson). Without leverage it lowers expected terminal wealth vs SPY in rising markets.

### AR5: Market-state-conditioned momentum

- **Economic hypothesis:** momentum pays after up-markets and fails after down-markets (Cooper et al. 2004). Hold the momentum book only when the market's 12-month return, or its trend, is positive; otherwise hold SPY or cash.
- **Signals:**
  - primary: momentum rank;
  - confirmation (portfolio level): market state.
- **Entry / exit:** as AR1, plus a switch of the whole book at state changes.
- **Timeframe:** monthly.
- **Turnover:** low to medium.
- **Failure regime:** whipsaw in the market state (2011-, 2015–16-type corrections), late re-entry after rebounds.
- **Overlap:** **mostly tested.** H002 v1.2 used SPY > SMA200.
- **Evidence:** B.
- **Distinct?** No, as a new hypothesis. It is an acceptable *design option* inside AR1–AR3. Switching to SPY rather than cash is the version consistent with the wealth objective.

### AR6: Weekly trend + daily pullback entry (multi-timeframe)

- **Economic hypothesis (practitioner):** buy temporary dips in established uptrends for a better entry price.
- **Signals:**
  - primary: weekly trend state;
  - entry timing: daily oscillator or pullback condition.
- **Entry / exit:** buy on a daily pullback signal inside a weekly uptrend; exit on the weekly trend state or a target.
- **Timeframe and holding:** weekly plus daily; weeks to months.
- **Turnover:** high.
- **Failure regime:** strong trends without pullbacks (missed entries); falling knives.
- **Overlap:** **mostly tested.** H004, H014 and the H018 pullback primaries with trend confirmations.
- **Evidence:** C / D.
- **Distinct?** **No. Not recommended.**

### AR7: Breakout / 52-week high with volume confirmation

- **Economic hypothesis:** anchoring on prior highs; volume signals informed demand.
- **Signals:**
  - primary: a new 52-week (or N-day) high;
  - confirmation: relative volume.
- **Entry / exit:** buy at the next open after the breakout; trailing or trend exit.
- **Timeframe:** daily or weekly.
- **Turnover:** medium to high.
- **Failure regime:** false breakouts in range-bound markets.
- **Overlap:** **mostly tested.** H003, H006, H009, and the H018 B1 + cP_rv cells.
- **Evidence:** C.
- **Distinct?** **No. Not recommended.**

### AR8: Volatility contraction → breakout

- **Economic hypothesis (practitioner):** compressed volatility precedes directional expansion.
- **Signals:**
  - primary: low bandwidth / ATR percentile;
  - confirmation: a breakout.
- **Entry / exit:** buy the breakout; exit on a trend or time rule.
- **Timeframe:** daily or weekly.
- **Turnover:** medium to high.
- **Failure regime:** contraction that resolves downward or sideways.
- **Overlap:** **mostly tested** (H007).
- **Evidence:** D.
- **Distinct?** **No. Not recommended.**

### AR9: Defensive trend (low volatility within uptrends)

- **Economic hypothesis:** low-volatility stocks earn similar returns with less risk; restricting them to uptrends avoids value traps.
- **Signals:**
  - primary: low-volatility rank;
  - confirmation: long-term trend state.
- **Entry / exit:** monthly or quarterly; trend-state exit.
- **Timeframe and holding:** monthly; months to a year.
- **Turnover:** very low.
- **Failure regime:** strong high-beta rallies, which are bad for a terminal-wealth-vs-SPY objective.
- **Overlap:** **mostly tested.** H005 (low volatility) failed Validation and may never be re-validated on 2018–2021. The trend overlay is a minor wrapper.
- **Evidence:** A / B (low volatility), but its alpha is not well aligned with beating SPY's wealth: it tends to lag in bull markets.
- **Distinct?** **No**, and it is poorly aligned with the objective. Not recommended.

### Archetype summary

| Archetype | Evidence | Overlap with the project | Distinct enough? | Recommendation |
|---|---|---|---|---|
| AR1: trend-filtered momentum + trend exit | A / B + B / C | Partial (= P4-CP1) | Only in exit structure | **Consider** |
| AR2: smooth momentum (frog in the pan) | B | **Substantially new** | Yes | **Consider (first)** |
| AR3: multi-horizon trend score | B (partial transfer) | Meaningfully different | Moderately | **Consider** |
| AR4: risk-managed momentum (overlay) | B (risk) | Partial (H012) | Not as alpha | Overlay option only |
| AR5: market-state momentum | B | Mostly tested (H002 v1.2) | No | Design option only |
| AR6: weekly trend + daily pullback | C / D | Mostly tested | No | **Do not pursue** |
| AR7: breakout / 52-week high + volume | C | Mostly tested | No | **Do not pursue** |
| AR8: volatility contraction → breakout | D | Mostly tested | No | **Do not pursue** |
| AR9: defensive trend (low volatility) | A / B, misaligned | Mostly tested | No | **Do not pursue** |

---

## 29. Comparison to H001–H018

| Prior hypothesis | Concept | Outcome | Archetypes it covers | Classification of that archetype |
|---|---|---|---|---|
| H001 | RSI oversold reversal | Rejected (4/5 lost money) | AR6 (timing layer) | Mostly tested |
| H002 | 12-1 momentum, monthly top-15 (v1.2 with a SPY filter) | Failed screen (Sharpe 0.38–0.56) | AR1 (information), AR5 | Partial / mostly tested |
| H003 | 52-week-high proximity | Failed screen | AR7 | Mostly tested |
| H004 | Pullbacks in momentum leaders | Failed screen | AR6 | Mostly tested |
| H005 | Low volatility | Passed screen; **failed Validation** | AR9; AR4 (stock-level) | Mostly tested |
| H006 | Breakout + volume | Failed screen | AR7 | Mostly tested |
| H007 | Squeeze | Failed robustness | AR8 | Mostly tested |
| H008 | Residual relative strength | Failed screen | AR1 variant | Mostly tested (the residual variant) |
| H009 | Volume shock | Failed screen | AR7 (volume) | Mostly tested |
| H010 / H011 | Gap / seasonality | Failed | — | Excluded |
| H012 | Volatility-managed exposure | Withdrawn (power) | AR4 | Partial |
| H013 | Lottery avoidance | Rejected | AR4 (volatility filter) | Partial |
| H014 | Trend + pullback + recovery | Rejected | AR6 | Mostly tested |
| H015 | Close > SMA200, random selection, trend exit | Not adopted (never run) | AR1 (exit structure) | Partial |
| H016 / H017 | GP/A; earnings continuation | Rejected | — (not technical) | — |
| H018 | 1,533-configuration technical search | Rejected (T 0.0127 < τ 0.0284) | AR1 information (M1 + cT), AR6, AR7, AR8 | Mostly tested as *daily, fixed 63-session* rules |

**Explicit non-repetition check:**
- **AR6 is H014 in a multi-timeframe wrapper.** It is **not** proposed.
- **No archetype here is a re-parameterised H018.** AR1 differs from H018 in the trend-state exit and the relative-strength ranking, but it uses the same information. Its test, if any, must count the momentum family's prior trials (§32).

---

## 30. Daily / Weekly / Multi-Timeframe recommendation

| Criterion | Daily decisions | Weekly decisions | Multi-timeframe (weekly structure + daily timing) |
|---|---|---|---|
| Noise | Highest: many decisions on noise | Lower: fewer, slower decisions (the information is the same; a weekly close is a daily close) | Weekly structure is low-noise; the daily layer re-adds it |
| Persistence of signals | Momentum and trend signals change slowly anyway; daily re-evaluation adds churn near thresholds | Matches the persistence of 6–12-month signals | Mixed |
| Number of observations | Most (but highly autocorrelated for slow signals: little extra *independent* information) | ≈ 1/5 of daily, with little loss of independent information for slow signals | Same as daily |
| Turnover | Highest (threshold churn) | Low to medium | Higher than weekly |
| Cost impact | Highest; daily timing strategies here had 4–14% a year cost drag | Low | Medium to high |
| Overfitting risk | High (more choices: lookbacks, thresholds, timing) | Lower | **Highest** (two layers of parameters) |
| Entry precision | Highest, but only valuable if short-term timing has an edge (not supported in large caps) | A one-week delay at most; immaterial for months-long holds | High, but see daily |
| Trend capture | Earliest exits and entries, plus whipsaws | Slightly later exits; fewer whipsaws | Daily entries can *miss* trend entries while waiting for a dip |
| $100K suitability | Poor: commission and slippage per trade on ~$8K positions | **Good** | Poor to medium |

**Recommendation:**
- **Selection, holding and exits on a slow cadence:** weekly or monthly. The evidence for momentum and trend is monthly (academic) and weekly (practitioner). It does not distinguish the two.
- **Daily data only to compute inputs** (for example smooth momentum's up / down-day counts, and realised volatility) and to **execute at the next open**.
- **"Weekly structure + daily timing" is not supported** as a *signal* design for our universe. It would add the one layer (short-term timing) with negative large-cap evidence and the worst cost and overfitting profile. It has also already failed here in several forms (H004, H014, H018).
- **Weekly vs monthly** must be fixed **before** any test and must not be varied. Monthly matches the academic momentum evidence and minimises trades. Weekly exits a broken trend earlier at slightly higher turnover. **Suggested default: monthly ranking, with the trend-state exit checked weekly.** This is the one multi-cadence choice with a reason: the exit is a risk control, and the ranking is slow information. It is an owner decision (§33).

---

## 31. Genuinely new archetypes

**Substantially new to this project (never tested here, distinct mechanism, pre-2018 peer-reviewed support):**
- **AR2: smooth / frog-in-the-pan momentum.**

**Meaningfully different (new construction of shared information):**
- **AR3: multi-horizon trend score** (unfitted, long horizons).
- **AR1's trend-state exit structure:** designed in P4-CP1, never run.

**Not new:** AR4–AR9 (§28–§29).

**Honest framing.** All three "new" items use the **same past-return information family** that H002, H008 and H018 already tested in 2010–2017 without success. They are refinements of *how* that information is used. A new information source would be event, fundamental or data-purchase research, and those are outside this review's technical remit.

---

## 32. Future research architecture

**What the evidence implies:**
1. There are at most **2–3 worthwhile hypotheses** (AR2, AR3, AR1), all in one information family.
2. **No optimizer.** Phase 3 showed that searching produces fake winners that beat SPY. The Phase 4 Weekly search (P4-CP1) has no realistic power.
3. **Power is the binding constraint.** A 12-stock book over 2010–2017 can only detect edges of roughly 6–12% a year (P4-CP1 §power). The literature suggests ≈ 0–3% a year for large-cap momentum after 2002.

### Options

| Option | Description | Power | Trials added | Assessment |
|---|---|---|---|---|
| **S. Stop** | Close the technical-indicator line: No Production Candidate Found across all technical families tested | — | 0 | **Defensible.** The evidence review adds no reason to expect a detectable large-cap edge |
| **P. Signal-level pre-test, then at most one book** | Step 1: test 2–3 *pre-registered* ranking signals (plain 12-1 momentum as reference, smooth momentum, multi-horizon trend score) **universe-wide** on 2010–2017, using cross-sectional rank correlations / decile spreads over all eligible ≥ $2B stocks, each signal against its own permutation null, with fixed conventional parameters (no grid) and multiple-testing correction across the 2–3 signals. Step 2: only a signal that passes may be wrapped in **one** pre-registered book (AR1 structure), judged under Amendment 3 against random twins and SPY, then the one-shot 2018–2021 check, then the Holdout only with owner approval | **Much higher at step 1**: uses ~1,000+ stocks a month instead of 12 positions | 2–3 signal tests + ≤ 1 book | **Recommended if continuing.** It answers "is there information at all in our universe?" cheaply before the expensive and low-power book question. Caveat: 2010–2017 has already been used by H002 / H008 / H018 for this family, so trial counting must include them |
| **H. Explicit hypothesis books directly** | 1–3 pre-registered books (AR1 / AR2 / AR3), each with matched random controls (Amendment 3 style) | Low (≈ 6–12% a year needed) | 1–3 | Feasible but likely uninformative: a fail cannot separate "no edge" from "too little data" |
| **W. P4-CP1 Weekly search** | 240-configuration search with a null | Low | 240 | **Not recommended** (P4-CP1 conclusion stands) |

**Recommendation:**
- **If the owner wants to continue technical research: option P, with at most 3 signals and at most 1 book.** Otherwise, **option S**.
- In either case:
  - no 2018–2021 data before a frozen book exists;
  - no Holdout without CP5 approval;
  - no purchase. The existing QuantConnect data suffices for P.

**What option P would need before running (not done now):**
- a written pre-registration per signal (the definition with one conventional parameter set, the test statistic, the null, the pass rule);
- a signal-level evaluation harness inside QuantConnect (derived statistics only; no raw data export);
- canaries and look-ahead tests;
- a trial-accounting rule;
- owner approval of each step.

---

## 33. Owner decisions

1. **Accept P4-CP2** as the evidence basis for any further technical research, including the exclusion list (§26) and the role assignments (§24).
2. **Choose the direction:**
   - **(S)** stop the technical-indicator line;
   - **(P)** design a universe-wide signal-level pre-test of at most 3 pre-registered ranking signals (12-1 momentum reference, smooth momentum, multi-horizon trend score), followed by at most one book — *recommended if continuing*;
   - **(H)** go directly to 1–3 explicit hypothesis books;
   - **(W)** implement the P4-CP1 Weekly search (not recommended).
3. **If (P) or (H): the risk concepts.**
   - Should volatility scaling (AR4) and market-state switching (AR5) be allowed as **pre-registered overlays**?
   - Without leverage they reduce expected terminal wealth vs SPY in rising markets. Recommendation: exclude them from the first test, and report them only as diagnostics.
4. **If (P) or (H): the cadence**, fixed in advance. Recommendation: monthly ranking with a weekly trend-state exit check.
5. **Trial accounting for the momentum family:** confirm that H002, H008 and H018's momentum cells count towards the multiple-testing burden of any new momentum-family test on 2010–2017.
6. **No purchase** is needed for any option.

**Nothing in this checkpoint changes:**
- the Holdout lock;
- the frozen Phase 3 history;
- Amendment 3;
- data freeze v1.

---

## Final answers A–H

**A. Which technical concepts have the strongest evidence for return generation?**
- **Cross-sectional intermediate momentum** (6–12 months, skip ≈ 1 month): Tier A in general, **Tier B in large US caps after 2002**.
- Its credible refinements: **smooth / frog-in-the-pan momentum** and the **multi-horizon trend score** (Tier B, never tested here).
- Nothing else in the technical family has credible return-generation evidence for our universe.

**B. Which concepts are better for risk management?**
- The **long-term trend state** (MA / 12-month sign) as a holding and exit rule.
- **Realised-volatility** scaling or filtering (volatility-scaled momentum survives out of sample).
- **Market state** for portfolio exposure.
- All three mainly reduce drawdowns and crash exposure. Without leverage they do not raise expected wealth vs SPY.

**C. Which popular indicators have weak incremental evidence?**
- RSI (both uses), MACD, ADX, Bollinger Bands (decayed after popularisation), the squeeze / volatility-contraction patterns, OBV / A-D and volume confirmation, short MA crossovers, short Donchian breakouts, and chart patterns.

**D. Which indicator combinations are genuinely complementary?**
- **A momentum ranking + a long-term trend-state exit:** selection plus holding rule.
- **Momentum + volatility scaling:** alpha plus risk.
- **Momentum + market state:** selection plus exposure, though mostly tested.
- Combinations of trend-type indicators (MA + MACD + ADX + TSMOM) are **redundant**. Trend + pullback and breakout + volume are complementary only in form; their second component lacks evidence.

**E. Which timeframe should be used for each role?**

| Role | Timeframe |
|---|---|
| Ranking | Monthly (or weekly), on 6–12-month information |
| Trend-state exit | Weekly (or monthly), on a ≈ 30–50-week trend |
| Risk | Weekly / monthly reviews of 1–6-month realised volatility |
| Execution | Next daily open |
| Entry timing | None |

**F. Is Daily, Weekly or Multi-Timeframe best for our goal?**
- **Slow decisions (weekly or monthly), with daily data only for inputs and execution.**
- A daily signal layer, including "weekly structure + daily timing", is not supported for large-cap US stocks after costs. It has failed here repeatedly.

**G. What are the best 3–5 strategy archetypes worth considering?**
- **AR2:** smooth momentum.
- **AR3:** multi-horizon trend score.
- **AR1:** trend-filtered momentum with a trend-state exit.
- Plus **AR4** only as a risk overlay, and **AR5** only as a design option.

**H. Which ideas should we stop spending time on?**
- Pullback and dip-buying timing (RSI, Bollinger, short-MA distance).
- Breakout + volume.
- Squeeze / volatility contraction.
- ADX / MACD / RSI confirmations.
- Daily timing layers under weekly trends.
- 52-week-high as a separate strategy.
- Residual-momentum reruns.
- Low-volatility reruns.
- Gap and seasonality rules.
- **Any broad indicator search or optimizer.**

---

## Programme totals (unchanged by this checkpoint)

- **No new hypothesis, strategy or experiment.** No QuantConnect run, no indicator return computed, no 2018–2021 or Holdout access, no purchase.
- **Phase 4:** P4-CP1 (design, not implemented) and P4-CP2 (this evidence review).

STOP: waiting for the owner's decisions (§33).
