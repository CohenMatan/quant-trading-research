# P6-CP1 references — sector / industry momentum and rotation

## How to read this file

**Verification status:**
- **Verified** = the citation and the summary claim were checked on 2026-10-05 against publisher, RePEc, SSRN or author search records.
- **Memory** = from memory; verify before quoting any magnitude.

**Post-2017 publications (†)** are used only as context or caution. They never motivate a hypothesis (CLAUDE.md: no hindsight).

**Evidence tiers:**

| Tier | Meaning |
|---|---|
| A | Strong, replicated academic evidence |
| B | Credible but conditional or mixed |
| C | Practitioner evidence / convention |
| D | Weak or unsupported |

## Industry / sector momentum (cross-sectional, the unit of prediction for Phase 6)

| Ref | Status | Finding | Tier |
|---|---|---|---|
| Moskowitz & Grinblatt (1999), "Do Industries Explain Momentum?", JF 54(4), 1249–1290 ([Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00146), [RePEc](https://econpapers.repec.org/RePEc:bla:jfinan:v:54:y:1999:i:4:p:1249-1290)) | Verified (abstract) | **Industry momentum is strong** and accounts for much of individual-stock momentum. Buying past-winning industries and selling past losers was profitable after controls for size, book-to-market, stock momentum and microstructure. US, 20 industries, 1963–1995 (sample: Memory). The effect is strongest at short (1-month) formation, and 6-month formation / 6-month holding is the headline (Memory) | **A** for the 1963–1995 US sample |
| Grundy & Martin (2001), RFS 14 ([search record](https://www.researchgate.net/publication/273882004_Understanding_the_nature_and_risks_and_the_sources_of_rewards_to_momentum_investing)) | Verified (search summary) | Industry momentum depends on **no skip month**: with a one-month gap between formation and holding, industry momentum returns become insignificant. Much of it is first-order (short-horizon) industry autocorrelation | B (a key qualification) |
| Lewellen (2002), RFS 15, "Momentum and Autocorrelation in Stock Returns" ([search record](https://www.semanticscholar.org/paper/Momentum-and-Autocorrelation-in-Stock-Returns-Lewellen/c1beb3f4001492b9c07daf5888655d32b28133b0)) | Verified (search summary) | Momentum also exists in industry, size and B/M **portfolios**. It is driven mainly by **negative cross-serial correlation** (excess covariance), not by positive own autocorrelation | B (mechanism contested) |
| Hong, Torous & Valkanov (2007), "Do industries lead stock markets?", JFE 83(2), 367–396 ([RePEc](https://ideas.repec.org/a/eee/jfinec/v83y2007i2p367-396.html)) | Verified | Some industries lead the market by up to two months (gradual information diffusion). This is a **lead-lag** effect, not own momentum. It is relevant to the null design (cross-serial predictability) | B (context) |
| O'Neal (2000), "Industry Momentum and Sector Mutual Funds", FAJ 56(4), 37–49 ([T&F](https://www.tandfonline.com/doi/abs/10.2469/faj.v56.n4.2372)) | Verified | Industry momentum was strong in **sector mutual funds** over about 10 years (to the late 1990s), with tradable instruments and known costs. Higher total risk than market indexes | B/C (tradable, short pre-2000 sample) |
| Andreu, Swinkels & Tjong-A-Tjoe (2013), "Can Exchange Traded Funds be Used to Exploit Industry and Country Momentum?", Financial Markets and Portfolio Management 27, 127–148 ([search record](https://www.semanticscholar.org/paper/Can-Exchange-Traded-Funds-be-Used-to-Exploit-and-Andreu-Swinkels/73cba79097b1da8ca0c39ba70d7d963c9fcd07ed)) | Verified (abstract) | With actual **ETF** prices, country and industry momentum gave **≈ 5% a year** excess return over the ETF trading periods. Not explained by Fama-French exposures; ETF spreads well below break-even costs. Country and industry are combined in the headline, and the exact industry-only sample is Memory | B |
| "Market states and momentum in sector exchange-traded funds", Journal of Asset Management (2014) ([Springer](https://link.springer.com/article/10.1057/jam.2014.24)) | Verified (abstract) | 10 **iShares** sector ETFs (Dow Jones US sector indexes), 2000–2011; formation 1/3/6/9/12 months, holding 1/6 months, with and without a gap. **No momentum in sector ETFs** and no market-state dependence in that decade. A clean post-1999 out-of-sample test | **B (negative)** |
| † Arnott, Clements, Kalesnik & Linnainmaa, "Factor Momentum" (SSRN 3116974; published 2021+) ([SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3116974)) | Verified (search summary) | Industry predictability is strongest at the 1-month horizon. **Industry momentum is a by-product of factor momentum**: controlling for factor momentum, industry-momentum alpha falls close to zero. Post-2017: caution only | Context |
| Momentum decline after 2000 (survey, e.g. [CXO "Loss of momentum"](https://www.cxoadvisory.com/momentum-investing/loss-of-momentum/); NBER w28624) | Verified (search summary) | US equity momentum profitability fell sharply after the early 2000s (stock level). This is post-publication decay context for momentum generally | Context |

## Practitioner / rotation frameworks

| Ref | Status | Finding | Tier |
|---|---|---|---|
| Faber (2010), "Relative Strength Strategies for Investing", SSRN 1585517 ([SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1585517)) | Verified (abstract); details Memory (the PDF host was blocked by the network policy) | A relative-strength model on **Fama-French US sector data back to the 1920s**: higher returns with equity-like risk; outperformed buy-and-hold in about 70% of years. Adding a **trend filter** lowers volatility and drawdown. Memory: about 10 sectors, monthly, lookbacks 1–12 months, top 1–3 sectors, 10-month SMA filter | C (practitioner backtest on index data, not tradable before ETFs) |
| Antonacci, "Dual Momentum" (relative + absolute momentum) ([paper](https://www.emiratescapitalassetmanagement.com/uploads/2/5/5/4/25541321/risk_premia_harvesting_through_dual_momentum.pdf)) | Verified (search summary) | Relative momentum chooses among assets; absolute momentum (excess return vs T-bills) decides whether to hold them. Claimed benefit: left-tail truncation (drawdown reduction) | C |
| Moskowitz, Ooi & Pedersen (2012), "Time Series Momentum", JFE 104(2), 228–250 ([NYU](https://w4.stern.nyu.edu/facdir/lpederse/papers/TimeSeriesMomentum.pdf)) | Verified | The past-12-month excess return of each of 58 liquid futures (equity indexes included) predicts its own future return. Persists about 12 months, then partially reverses | **A** (absolute trend on indexes / futures; not sector ETFs specifically) |
| Stangl, Jacobsen & Visaltanachoti, "Sector rotation over business cycles" ([search record](https://www.researchgate.net/publication/228425439_Sector_rotation_over_business-cycles)) | Verified (search summary) | Even with **perfect foresight** of business-cycle stages and no costs, conventional sector rotation would have beaten the market by at most about 2.3% a year since 1948; realistic versions much less | B (sets an upper bound for macro-timed rotation) |
| Conover, Jensen, Johnson & Mercer (2008), "Sector Rotation and Monetary Conditions", J. Investing 17(1), 34–46 ([JOI](https://joi.pm-research.com/content/17/1/34)) | Verified | Monetary-regime rotation (cyclicals when the Fed eases) earns excess returns over 33 years. A macro signal, **not** momentum; out of scope | C (out of scope) |

## Instruments and data facts

| Item | Status | Source |
|---|---|---|
| The nine Select Sector SPDRs (XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY): prospectus dated **1998-12-16**; first QuantConnect daily bar **1998-12-22** for all nine | Verified (SEC N-1A / 497 records; QuantConnect probe E988-01) | [SEC 497](https://www.sec.gov/Archives/edgar/data/0001064641/000095012398010785/0000950123-98-010785.txt); `research/phase6/p6_data_probe.json` |
| XLRE began trading **2015-10-08** (QuantConnect first bar 2015-10-08) | Verified | [Morningstar](https://www.morningstar.com/funds/biggest-financials-sector-etf-undergoes-makeover); probe |
| XLF distributed **0.139146 XLRE per XLF share** to holders of 2016-09-16 (real estate left XLF; QuantConnect dividend-feed event 2016-09-19, 18.8% of the reference price) | Verified | [Nasdaq](https://www.nasdaq.com/articles/fallout-financial-sector-spdr-etfs-divorce-reits-2016-09-29); probe |
| XLC inception **2018-06-18** (QuantConnect: no bar up to 2017-12-29; no backfill) | Verified | [SSGA](https://www.ssga.com/us/en/intermediary/etfs/state-street-communication-services-select-sector-spdr-etf-xlc); probe |
| iShares US sector ETFs (e.g. IYW 2000-05-15); QuantConnect first bars 2000-05-19 → 2000-07-14, with gaps (up to 54 missing sessions) | Verified | [etfdb IYW](https://etfdb.com/etf/IYW/); probe |
| Vanguard sector ETFs (VGT, VFH 2004-01-26); QuantConnect first bars 2004-01-30 / 2004-09-29 | Verified | [Vanguard VFH](https://advisors.vanguard.com/investments/products/vfh/vanguard-financials-etf); probe |
| Kenneth French Data Library (industry portfolios, free, monthly / daily from 1926) | Verified exists (Faber used it); **not reachable** from this session (the network policy blocks the host) | — |
