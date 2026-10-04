# P4-CP2 source references (Deep Technical Indicator & Strategy Evidence Review)

**Verification:**
- **Verified** = bibliographic details (journal, volume, year) and the stated main finding were checked against the publisher, SSRN, RePEc or an author page on 2026-10-04 (links below).
- **Memory** = cited from memory; verify before quoting magnitudes.

**† = published after 2017.** The sample may include 2018+ data. Under the project's hindsight rule (CLAUDE.md), these are used **only to downgrade or caution, never to motivate** a hypothesis.

**Source levels:** 1 peer-reviewed; 2 working paper; 3 practitioner book (quant); 4 institutional; 5 reputable practitioner; 6 forums / SEO (popularity only, never evidence).

## Momentum (cross-sectional and time-series)

| Ref | Level | Status | Finding used |
|---|---|---|---|
| Jegadeesh & Titman (1993), JF 48, 65–91 | 1 | Memory | 3–12-month winners beat losers over 3–12 months |
| Jegadeesh & Titman (2001), JF 56, 699–720 | 1 | Verified ([pdf](http://www-stat.wharton.upenn.edu/~steele/Courses/434/434Context/Momentum/MomentumStrategiesJF2001.pdf)) | Out-of-sample 1990–98 profits of similar size; long-run reversal in years 2–5 |
| Novy-Marx (2012), JFE 103, 429–453 | 1 | Memory | Intermediate (7–12 month) past returns drive momentum |
| Asness, Moskowitz & Pedersen (2013), JF 68, 929–985 | 1 | Memory | Momentum "everywhere" (asset classes, countries) |
| Asness, Frazzini, Israel & Moskowitz (2014), JPM, "Fact, fiction and momentum investing" | 3/4 | Memory | Practitioner defence: robust, implementable at scale |
| Hong, Lim & Stein (2000), JF 55, 265–295 | 1 | Memory | Momentum is weaker in large, well-covered stocks |
| Daniel & Moskowitz (2016), JFE 122, 221–247 | 1 | Memory | Momentum crashes after market rebounds (mostly the short leg) |
| Barroso & Santa-Clara (2015), JFE 116, 111–120, "Momentum has its moments" | 1 | Verified ([ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0304405X14002566)) | Volatility scaling of momentum reduces crashes |
| Cooper, Gutierrez & Hameed (2004), JF 59, 1345–1365 | 1 | Verified ([Wiley](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.2004.00665.x)) | Momentum profits 0.93% / month after UP markets, −0.37% after DOWN markets (1929–1995) |
| Da, Gurun & Warachka (2014), RFS 27, 2171–2218, "Frog in the pan" | 1 | Verified ([Chapman](https://digitalcommons.chapman.edu/business_articles/115/)) | Momentum is stronger when past returns accrued continuously (information discreteness) |
| Blitz, Huij & Martens (2011), JEF 18, 506–521, "Residual momentum" | 1 | Verified ([RePEc](https://econpapers.repec.org/RePEc:eee:empfin:v:18:y:2011:i:3:p:506-521)) | Ranking on residual returns removes factor exposures and roughly doubles the risk-adjusted momentum return |
| McLean & Pontiff (2016), JF 71, 5–32 | 1 | Memory | Anomaly returns fall ≈ 1/3 (or more) after publication |
| † Ben-David, Li, Rossi & Song (NBER w28624, 2021; JFQA 2023) | 1 | Verified ([NBER](https://www.nber.org/papers/w28624)) | Momentum factors in US stocks **declined sharply after 2002** (≈ 0.92% → 0.16% a month in one cited comparison), linked to a change in mutual-fund feedback trading |
| † Goyal & Jegadeesh (2018), RFS 31, 1784–1824 | 1 | Verified ([SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2610288)) | Time-series vs cross-sectional differences are largely due to the TS strategies' time-varying net long exposure |
| † Huang, Li, Wang & Zhou (2020), JFE 135, 774–794, "Time series momentum: Is it there?" | 1 | Verified ([RePEc](https://ideas.repec.org/a/eee/jfinec/v135y2020i3p774-794.html)) | Asset-by-asset regressions show little TSMOM, in- and out-of-sample |
| † Medhat & Schmeling (2022), RFS 35, 1480–1526, "Short-term momentum" | 1 | Verified ([OUP](https://academic.oup.com/rfs/article-abstract/35/3/1480/6286969)) | 1-month returns **continue** (not reverse) in high-turnover stocks, strongest in the largest, most liquid stocks |

## Trend / moving averages / time-series trend

| Ref | Level | Status | Finding used |
|---|---|---|---|
| Brock, Lakonishok & LeBaron (1992), JF 47, 1731–1764 | 1 | Memory | MA and range-break rules predicted DJIA returns 1897–1986 (index level) |
| Sullivan, Timmermann & White (1999), JF 54, 1647–1691 | 1 | Memory | The best of ≈ 7,800 rules did not persist out of sample |
| Faber (2007), Journal of Wealth Management, "A quantitative approach to tactical asset allocation" | 1/5 | Memory | 10-month SMA timing across asset classes cuts drawdowns |
| Zhu & Zhou (2009), JFE 92, 519–544 | 1 | Memory | MA rules add value in asset allocation under uncertainty |
| Moskowitz, Ooi & Pedersen (2012), JFE 104, 228–250 | 1 | Memory | 12-month time-series momentum in futures |
| Hurst, Ooi & Pedersen (2017), JPM 44(1), 15–29, "A century of evidence on trend-following investing" | 1/4 | Verified ([JPM](https://jpm.pm-research.com/content/44/1/15.abstract)) | Trend following positive in every decade since 1880 (diversified futures); crisis alpha |
| Han, Yang & Zhou (2013), JFQA 48, 1433–1461 | 1 | Memory | MA timing on cross-sectional portfolios works mainly in high-volatility (small, illiquid) deciles |
| Han, Zhou & Zhu (2016), JFE 122, 352–375, "A trend factor" | 1 | Verified ([SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2182667)) | A cross-sectional factor built from MA ratios over short / intermediate / long horizons predicts returns. It earned +0.75% / month in the 2008 crisis while momentum lost −3.88% |
| Marshall, Nguyen & Visaltanachoti (2017), Quantitative Finance 17(3), 405–421 | 1 | Verified ([Taylor & Francis](https://www.tandfonline.com/doi/full/10.1080/14697688.2016.1205209)) | TSMOM and MA rules are highly similar (same trend information) |
| Zakamulin (2017), *Market Timing with Moving Averages* (book); SSRN 2585056 | 1/3 | Verified ([SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2585056)) | Every MA rule is a weighted average of past price changes. Out of sample, the best MA timing is only marginally better than buy-and-hold; no significant outperformance in the second half of the sample |
| Park & Irwin (2007), J. Economic Surveys 21, 786–826 | 1 | Memory | Review: technical profits mostly vanish after the early 1990s in mature markets |
| Bajgrowicz & Scaillet (2012), JFE 106, 473–491 | 1 | Memory | With false-discovery control and costs, no persistent technical-rule outperformance (DJIA) |

## 52-week high, breakout, oscillators, volatility, volume, patterns

| Ref | Level | Status | Finding used |
|---|---|---|---|
| George & Hwang (2004), JF 59, 2145–2176 | 1 | Verified ([pdf](https://www.bauer.uh.edu/tgeorge/papers/gh4-paper.pdf)) | Nearness to the 52-week high dominates past returns in forecasting (equal-weighted, 1963–2001) |
| † Barroso & Wang (2021), working paper / EFMA ("What explains price momentum and 52-week high momentum when they really work?") | 2 | Verified ([EFMA pdf](https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2021-Leeds/papers/EFMA%202021_stage-2049_question-Full%20Paper_id-368.pdf)) | The George–Hwang result is **limited to small stocks**; price momentum explains 52-week-high momentum |
| Wilder (1978), *New Concepts in Technical Trading Systems* | 5 | Memory | Origin of RSI(14), ADX(14), ATR |
| Chong & Ng (2008), Applied Economics Letters 15(14), 1111–1114 | 1 | Verified ([RePEc](https://econpapers.repec.org/RePEc:taf:apeclt:v:15:y:2008:i:14:p:1111-1114)) | MACD and RSI rules beat buy-and-hold on the FT30 **index** over 60 years in most cases (index timing, UK, costs not central) |
| Lento, Gradojevic & Wright (2007), Applied Financial Economics Letters 3(4), 263–267 | 1 | Verified (search record) | Bollinger Bands unprofitable after costs (US / Canada indices, FX, 1995–2004) |
| Fang, Jacobsen & Qin (2017), JPM 43(4), 152–159, "Popularity versus profitability" | 1 | Verified ([JPM](https://www.pm-research.com/content/iijpormgmt/43/4/152)) | Bollinger Bands were profitable before their introduction; they lost predictive ability after popularisation (2001 book) |
| Ang, Hodrick, Xing & Zhang (2006), JF 61, 259–299 | 1 | Memory | High idiosyncratic volatility predicts low returns |
| Frazzini & Pedersen (2014), JFE 111, 1–25 | 1 | Memory | Betting against beta |
| Baker, Bradley & Wurgler (2011), FAJ 67(1) | 1 | Memory | The low-volatility anomaly in large caps |
| Moreira & Muir (2017), JF 72, 1611–1644 | 1 | Memory | Volatility-managed factor portfolios have higher alphas (in sample) |
| † Cederburg, O'Doherty, Wang & Yan (2020), JFE 138, 95–117 | 1 | Verified ([RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:138:y:2020:i:1:p:95-117)) | Across 103 strategies, the in-sample gains of volatility management **hardly translate out of sample**. Momentum is one of the few exceptions |
| † Harvey et al. (2018), JPM 45(1), 14–33, "The impact of volatility targeting" | 1/4 | Verified ([pdf](https://people.duke.edu/~charvey/Research/Published_Papers/P135_The_impact_of.pdf)) | For equities, volatility targeting raises Sharpe ratios and cuts tail events: **risk management** |
| Gervais, Kaniel & Mingelgrin (2001), JF 56, 877–919 | 1 | Verified ([Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00349)) | Unusually high (low) volume over a day or week precedes higher (lower) returns over the next month (visibility) |
| Lee & Swaminathan (2000), JF 55, 2017–2069 | 1 | Verified ([Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00280)) | Volume links momentum and value. Low-turnover firms earn more; high-volume winners reverse sooner over long horizons |
| Lo, Mamaysky & Wang (2000), JF 55, 1705–1765 | 1 | Verified ([MIT pdf](https://web.mit.edu/people/wangj/pap/LoMamayskyWang00.pdf)) | Pattern signals change the conditional return distribution (1962–96). This is not shown to be a profitable after-cost strategy |

## Short-term reversal / pullbacks

| Ref | Level | Status | Finding used |
|---|---|---|---|
| Jegadeesh (1990), JF 45, 881–898; Lehmann (1990), QJE 105, 1–28 | 1 | Memory | 1-week / 1-month reversal |
| Avramov, Chordia & Goyal (2006), JF 61, 2365–2394 | 1 | Verified ([Wiley](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.2006.01060.x)) | Reversals are concentrated in **illiquid** stocks; **profits are smaller than likely transaction costs** |
| Nagel (2012), RFS 25, 2005–2039, "Evaporating liquidity" | 1 | Verified ([RePEc](https://econpapers.repec.org/RePEc:oup:rfinst:v:25:y:2012:i:7:p:2005-2039)) | Reversal returns are compensation for liquidity provision; they spike in turmoil (VIX) |
| Da, Liu & Schaumburg (2014), Management Science 60, 658–674 | 1 | Memory | Reversal within industry, after removing news / cash-flow components, is stronger |

## Practitioner sources (level 3–5): popularity and convention, not proof

| Source | Used for |
|---|---|
| Elder (1993), *Trading for a Living* | The "triple screen" multi-timeframe convention (weekly trend, daily oscillator) |
| Connors & Alvarez (2008), *Short Term Trading Strategies That Work* | RSI(2) pullbacks above a 200-day MA |
| Clenow (2015), *Stocks on the Move* | Momentum ranking + index trend filter + volatility sizing for stocks |
| Antonacci (2014), *Dual Momentum Investing* | Relative + absolute momentum (asset classes) |
| Weinstein (1988), *Secrets for Profiting in Bull and Bear Markets* | The 30-week MA stage analysis |
| Bollinger (2001), *Bollinger on Bollinger Bands* | Bands, %b, the "squeeze" |
| Appel (MACD); Granville (OBV, 1963) | Indicator origins |

**Rejected as evidence** (level 6): search results claiming "67% vs 49% win rates" for multi-timeframe alignment, "ADX improves risk-adjusted returns by 18.7%", and similar unattributed or SEO statistics. They were found during the search and **not used**.
