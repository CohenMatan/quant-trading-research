# P5-CP1 references — structured historical chart analysis

**How verification is marked.** This follows the convention of `research/phase4/P4_CP2_references.md`:
- **Verified** = the citation and summary claim were checked on 2026-10-05 against publisher, RePEc, SSRN or author search records.
- **Memory** = from memory; verify before quoting any magnitude.

**Post-2017 publications (†).** These are used only to caution or to give context. They never motivate a hypothesis (CLAUDE.md: no hindsight).

**Evidence tiers:**
- **Academic:** peer-reviewed evidence.
- **Practitioner:** books and frameworks. These supply definitions, not statistical proof.
- **Our inference:** design choices made in this checkpoint.

## Academic evidence on chart structure and technical rules

| Ref | Status | Relevance |
|---|---|---|
| Lo, Mamaysky & Wang (2000), "Foundations of Technical Analysis: Computational Algorithms, Statistical Inference, and Empirical Implementation", JF 55, 1705–1765 ([Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00265), [NBER w7613](https://www.nber.org/papers/w7613)) | Verified | **The closest academic precedent.** Algorithmic, reproducible detection of visual patterns (kernel-smoothed local extrema) on US stocks 1962–1996. Conditional return distributions after several patterns differ from unconditional ones ("some incremental information"), more for Nasdaq than NYSE / AMEX stocks. Effect sizes are modest. |
| Savin, Weller & Zvingelis (2007), "The predictive power of 'head-and-shoulders' price patterns in the US stock market", J. Financial Econometrics 5(2), 243–265 ([search record](https://mebfaber.com/2007/07/26/head-and-shoulders-journal-of-financial-econometrics/)) | Verified | Uses the LMW algorithm with practitioner filters; S&P 500 and Russell 2000, 1990–1999. Patterns predict excess returns, but a stand-alone strategy is not profitable. |
| Brock, Lakonishok & LeBaron (1992), "Simple technical trading rules and the stochastic properties of stock returns", JF 47, 1731–1764 ([Wiley](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1992.tb04681.x)) | Verified | Moving-average and trading-range-break (support / resistance breakout) rules on the DJIA 1897–1986, with a bootstrap null. Index level, pre-1987. |
| Sullivan, Timmermann & White (1999), "Data-snooping, technical trading rule performance, and the bootstrap", JF 54, 1647–1691 ([Wiley](https://onlinelibrary.wiley.com/doi/10.1111/0022-1082.00163)) | Verified | Reality-check correction over the full rule universe. The best rule's apparent edge does not persist out of sample. **This is the reason the design has one fixed rubric and a full-procedure null.** |
| George & Hwang (2004), "The 52-week high and momentum investing", JF 59, 2145–2176 ([Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.2004.00695.x)) | Verified | Nearness to the 52-week high dominates past return as a predictor. **This is a chart-visible fact**, and it was already tested here as H003. |
| Osler (2000), "Support for resistance: technical analysis and intraday exchange rates", FRBNY Economic Policy Review 6(2), 53–68 ([RePEc](https://ideas.repec.org/a/fip/fednep/y2000ijulp53-68nv.6no.2.html)) | Verified | Published support / resistance levels predict intraday FX trend interruptions. This is FX and intraday, so it is not stock selection. |
| Kavajecz & Odders-White (2004), "Technical analysis and liquidity provision", RFS 17, 1043–1071 ([SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=315660)) | Verified | Support / resistance levels coincide with limit-order-book depth peaks. This explains why S/R may matter **without** implying a return edge. |
| Gervais, Kaniel & Mingelgrin (2001), "The high-volume return premium", JF 56, 877–919 ([Wiley](https://onlinelibrary.wiley.com/doi/10.1111/0022-1082.00349)) | Verified | Unusually high volume precedes higher returns over the next month. Volume as information was tested here as H009. |
| Lee & Swaminathan (2000), "Price momentum and trading volume", JF 55, 2017–2069 ([Wiley](https://onlinelibrary.wiley.com/doi/10.1111/0022-1082.00280)) | Verified | High-volume winners reverse faster. Volume interacts with trend, so the sign of a "volume quality" effect is not obvious. |
| Jegadeesh & Titman (1993), JF 48 | Memory | Momentum; the reference for the weekly-trend component (failed here in H002 and H019) |
| † Jiang, Kelly & Xiu (2023), "(Re-)Imag(in)ing price trends", JF 78(6), 3193–3249 ([Wiley](https://onlinelibrary.wiley.com/doi/10.1111/jofi.13268)) | Verified (abstract) | A CNN on OHLC chart **images** finds patterns that predict returns, beyond standard trend signals. **Published after 2017 and estimated on data that extends past 2017.** Cited only as context: image-based information is an open research question. It is not evidence for a hand-written rubric in ≥ $2B US stocks 2011–2017. |

## Practitioner frameworks (definitions, not statistical proof)

| Framework | Status | Concepts adopted as definitions (thresholds unchanged, not tuned) |
|---|---|---|
| Stan Weinstein, *Secrets for Profiting in Bull and Bear Markets* (1988), stage analysis ([search record](https://www.chartmill.com/documentation/technical-analysis/indicators/92-Weinstein-Stage-Analysis-Indicators)) | Verified (concept) | Four stages read from the 30-week moving average. Stage 2 = price above a rising 30-week MA after a base breakout. Adopted: 30-week MA and its slope (category W); below the 40-week MA = disqualifier. |
| William O'Neil, *How to Make Money in Stocks* (CAN SLIM; cup-with-handle) ([search record](https://www.luxalgo.com/library/concept/cup-with-handle-base/)) | Verified (concept) | Bases of at least ~5–7 weeks; normal base depth ≤ ~33%; breakout volume ≥ ~40–50% above average; buy within ~5% of the pivot. Adopted for categories B and T and for extension. |
| Mark Minervini, *Trade Like a Stock Market Wizard* (2013): trend template and volatility contraction pattern ([search record](https://www.chartmill.com/trading-ideas/645-Mark-Minervinis-Trend-Template-TTP)) | Verified (template); Memory (VCP details) | Price above the 150- and 200-day MAs; 200-day MA rising; within 25% of the 52-week high; successive pullbacks shrinking (VCP). Adopted: within 25% of the 52-week high (W); shrinking pullbacks (B). |
| Thomas Bulkowski, *Encyclopedia of Chart Patterns* ([failure-rate study](https://thepatternsite.com/FailureRates.html)) | Verified (summary) | Practitioner pattern statistics. Failure rates of chart patterns roughly doubled in 2003–2007 versus the 1990s. This is a caution against expecting large pattern edges in our sample. |
| Classical trading-range-break / Donchian breakout | Memory | Breakout above an established range; tested here as H006 / H007 / H018. |

## Data, licence and tooling facts used in P5-CP1

| Item | Status | Source |
|---|---|---|
| QuantConnect: downloaded data is for internal LEAN use only and may not be redistributed or converted. **Chart images may be shared only if the original data can't be reconstructed from the image.** | Verified (documentation search record) | [QuantConnect: Downloading Data](https://www.quantconnect.com/docs/v2/local-platform/datasets/downloading-data); [Licensing](https://www.quantconnect.com/docs/v2/cloud-platform/datasets/licensing); [Terms](https://www.quantconnect.com/terms/) |
| Finviz Elite (live): about 24 years of charts, pattern recognition (head-and-shoulders, triangles, channels, double tops), trendline drawing tools, screener CSV export, daily-data backtests of about 100 indicators | Verified (review search records) | e.g. [review](https://www.liberatedstocktrader.com/finviz-review/) |
| Claude API (cached model table 2026-09-25): see the list below this table | Verified (bundled API reference) | `claude-api` skill reference |

Claude API facts used for the cost and reproducibility analysis:
- **Prices per million tokens:**
  - Opus 5.5: $4 input / $20 output;
  - Sonnet 5.5: $2 / $10;
  - Haiku 4.5: $1 / $5.
- **Batch API:** 50% discount.
- **Images:** high-resolution models accept up to 2,576 px on the long edge, ≈ 4,784 image tokens at the cap.
- **Sampling control:** on Opus 5.5 and Sonnet 5.5, `temperature`, `top_p` and `top_k` are removed (400). Opus 5.5 thinking cannot be disabled.
- **Retirement:** models are deprecated and retired on a schedule (e.g. Opus 4.1 retired 2026-08-05).
