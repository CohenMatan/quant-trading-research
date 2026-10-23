# TT-CP1b — Historical Chart Source Feasibility (independent of QuantConnect)

**Date:** 2026-10-23 · **Owner direction:** D294 (`docs/owner/2026-10-23_chart_source_feasibility.md`) · **Decision record:** D295
**Scope:** desk research only. Nothing was downloaded, no chart was extracted or rendered, nothing was bought, no code was written, no backtest was run, and the Holdout was not touched.

---

## 0. Answer in one paragraph

Only one source passes all three tests: an independent source, a stated right to share the data, and enough history. That source is **WIKI Prices**, the free US end-of-day dataset curated by the Quandl community and hosted by Nasdaq Data Link. Its host describes it as **"released into the public domain"**. Because of that statement, sending its charts to Claude is not a licence question. WIKI Prices still has real limits: it stops in March 2018, it covers only about 3,200 US companies, it is probably biased toward survivors, it has no market capitalisation, and its host warns about data quality.

Every licensed source examined grants **personal or internal use only** and forbids redistribution. That covers TradingView, EODHD, Massive (formerly Polygon.io), Tiingo and Norgate. None explicitly allows sending data or charts to an outside AI service, and none was found to allow it. QuantConnect is excluded by its own terms and by D151.

**Decision: CONDITIONAL GO.** Real historical chart analysis is feasible on WIKI Prices only. It is limited to exploratory pattern discovery inside the already-spent 2010–2017 window, and it needs the four owner decisions in §7. Every other source is NO-GO now. If the owner does not accept the conditions, or the first composition audit fails, the choice in §8 applies: quantitative-only research or a pause of the hybrid programme.

## 1. How the terms were verified, and the limits of that check

- The network policy of this environment **blocks every vendor site**: stooq.com, tiingo.com, massive.com, data.nasdaq.com, eodhd.com, tradingview.com, finance.yahoo.com and alphavantage.co all failed DNS resolution or the proxy. Only anthropic.com was reachable.
- The licence wording below therefore comes from **search-engine excerpts of the vendors' own pages**, with the page cited. Where the only source was third-party, the wording is marked *reported*.
- Before relying on any of it, the owner (or a session allowed to reach the host) should read the primary page. That step is condition C1 in §7. Nothing here is legal advice.

## 2. Personal viewing is not the same as transmission to an outside AI (requirement 4)

| Act | What a typical data licence says | Status |
|---|---|---|
| The owner views a chart on a broker, TradingView or a vendor terminal | A personal, non-commercial display licence covers it | Allowed under the owner's own subscription |
| The owner describes a chart **in words** to Claude | No data values or images leave the licensee; this is the owner's own judgement | Generally outside the data licence. Not blind, not reproducible, not representative. |
| A chart image or OHLCV values are sent to Claude (Anthropic) | This is **disclosure to a third party**. A chart reproduces the OHLCV, so it counts as the data. Vendors classify it as redistribution, display to a non-subscriber, or non-display / machine use. | Needs explicit permission, or data free of licence restrictions |
| Data used to train an AI model | Increasingly prohibited or fee-liable. Examples: Nasdaq's Data AI Policy (DN2025-2) says use "including for training of AI models must strictly adhere to the terms of the license"; open-source models are prohibited without written consent; "all models trained on Nasdaq Information may be fee-liable". | Relevant here because of the next row |
| The AI provider's own handling | On Claude Free / Pro / Max, **including Claude Code**, conversations and coding sessions are used for training unless the owner opts out; retention is 5 years if training is allowed, 30 days if not (Anthropic, "Updates to our consumer terms"). API / commercial terms are excluded. | For licensed data, this setting matters. For public-domain data it does not. |

**Conclusion:** a personal viewing licence never implies a right to send images to Claude. Only two things qualify: data that carries no licence restriction, or a written vendor permission naming this use.

## 3. Sources examined (requirements 1–3)

### 3.1 Source A — WIKI Prices (Quandl community; hosted by Nasdaq Data Link): **the only candidate**

| Item | Finding |
|---|---|
| Licence | The host's product page says: "End of day stock prices, dividends and splits for 3,000 US companies, curated by the Quandl community and **released into the public domain**." A secondary description of the Quandl wiki licence adds that the data "may be copied, distributed, disseminated or included in other products for commercial and/or noncommercial purposes" (*reported*). The Kaggle mirror lists its licence as "Unknown", so use the Nasdaq-hosted original, not the mirror. Account / site terms of Nasdaq Data Link still govern **access** to the download (not read; see C1). |
| AI transmission | Permitted if the public-domain statement holds: no licence term restricts disclosure. Residual risk: the data's original provenance was community-sourced and is undocumented. |
| Depth | 1962 → **2018-03-27** (frozen; "no longer actively supported … as of April 11, 2018"). Useful window 2010–2017. |
| Coverage | About 3,199 tickers (about 3,000 companies), and some delisted companies are included. **Composition is not verified.** It is likely survivor-skewed: companies that died before the wiki was built are probably missing. Must be audited first (§6 step 1). |
| Adjustments | Raw open, high, low, close and volume, adjusted open, high, low, close and volume, ex-dividend amount and split ratio, per row. Both raw and adjusted charts are possible. |
| Market cap / fundamentals | None. The project's point-in-time ≥ $2B rule **cannot** be reproduced from WIKI. The sample universe must instead be defined by price and dollar volume, or by membership taken from our own identifier-only E981-01 Data v1 list (2,719 securities; identifiers, not prices). |
| Quality | The host itself says "we do not recommend using it for investment or analysis". There are known gaps and errors after 2017. A deterministic spike and gap screen is needed before sampling. |
| Cost | $0. A free Nasdaq Data Link account and API key, or a bulk file of about 1.8 GB CSV. It stays outside Git under the large-data rule. |
| Access from here | **Currently blocked** (DNS). It needs the owner to add the host to the network allowlist and start a new session (condition C4). |
| Blind-analysis suitability | **Good mechanically.** Bars up to the decision date can be rendered by our deterministic renderer with the ticker, dates and price scale removed. The outcome period is never rendered. |

### 3.2 Source B — TradingView (free or already available charting): **NO-GO for transmission**

- **Snapshots:** the Terms grant users "the ability to use snapshots of TradingView charts in analysis, press releases, books, articles, blog posts and other publications" with attribution.
- **Display only:** the same Terms, §3, say market data is licensed "for exclusive display-only use" and prohibit "any form of non-display usage", including "machine-driven processes that do not involve the direct, human-readable display".
- **AI:** there is no clause on outside AI tools.
- **Why that is not enough:** feeding a snapshot to an AI model is machine processing of the data, so the publication clause does not clearly cover it. The underlying exchange-data rights are TradingView's to sub-license, not ours.
- **Delisted coverage:** not confirmed. Search found no TradingView documentation of delisted-symbol history.
- **Sampling:** the owner would have to capture snapshots by hand, which breaks reproducible, frozen, blind sampling.
- **Verdict:** usable only for the owner's **personal** viewing.

### 3.3 Source C — Licensed end-of-day vendors with delisted coverage: **NO-GO now** (best paid route only with written permission)

| Vendor | Licence wording found | Delisted / depth | Cost (reported) | AI transmission |
|---|---|---|---|---|
| **EODHD** | Non-professional users may use the data "solely in a personal capacity", "store, manipulate, and analyze the data for private, non-commercial purposes"; prohibited: "selling, reselling, retransmitting, redistributing, displaying, or granting access to the Information … in its original or repackaged form". | About 60,000 delisted US symbols; end-of-day data only for delistings before 2018; ticker reuse needs care | About $20 / month (end of day; dated report) | Not permitted as worded: "retransmitting / displaying / granting access" covers sending to a third party. No AI clause. |
| **Massive** (Polygon.io until Oct 2025) | Individual plans: "personal, non-business, and non-commercial purposes". Reported 2025-08-28 terms: display use only; non-display use and derivative works barred unless licensed. The **Business** terms §2.6 say information made available "to a non-Massive service, including an AI tool" remains subject to the agreement. | Free 2 years; Starter $29 / 5 years; Developer $79 / 10 years; Advanced $199 / 20+ years. Delisted coverage not confirmed. | $29–199 / month individual; business separate | Individual plans: no. Business terms contemplate AI tools, at business prices (beyond the $200 ceiling with QuantConnect). |
| **Tiingo** | "For Basic and Power accounts, data is for internal and personal use only. You may not redistribute the data in any form." Redistribution needs a separate licence. | End-of-day data from 1962; delisted coverage not confirmed here | Free / about $30 / month | No, unless a redistribution licence or written permission is obtained. |
| **Norgate** (Platinum / Diamond) | Licence terms not found in search. | Delisted from 1990 / 1950, with historical index constituents | $630 / year (Platinum) | Unknown; assume no. |
| *Screened out:* Yahoo Finance | Terms reportedly prohibit "robots, spiders, crawlers, scrapers, or other automated means … to … extract data"; the yfinance package is not a Yahoo licence | Survivors only | Free | No |
| *Screened out:* Stooq | Terms ("Regulamin") exist but could not be read; no licence wording found | Survivors mainly | Free | Unknown, so treated as no |
| *Excluded:* QuantConnect | Licence and new terms (D254 / D257): data and derived images stay in-platform; D151 | — | Already paid | **No** (requirement 6) |

**Paid-route verdict:**
- A vendor with real delisted coverage (EODHD or Norgate) would fix the survivorship gap. Its standard licence still forbids the transmission we need.
- The route would require **(i)** written permission from the vendor naming "sending rendered charts / OHLCV to Anthropic's Claude for internal research, no redistribution, no model training" and **(ii)** a purchase, which D123 / D124 currently block until a strategy shows a promising result on existing data.
- This should not be pursued before the free route has been tried.

## 4. Can a representative, outcome-blind sample be built? (requirement 5)

| Requirement | WIKI Prices | Licensed vendor (if permitted) |
|---|---|---|
| Frozen random draw, seed committed before any viewing | Yes | Yes |
| Point-in-time universe without look-ahead | Partly: price and dollar-volume rules can be computed point-in-time from the data itself; no market cap | Yes for price and volume; market cap only with Norgate-type extras |
| Includes later-delisted names | Some; **share unknown, to be measured** | Yes (EODHD, Norgate) |
| Blind (no ticker, date, price level; bars ≤ decision date only) | Yes (render locally; normalise the price axis) | Yes |
| Outcome-blind (labels committed before any forward return is computed) | Yes, procedurally | Yes |
| Representative of the ≥ $2B universe of the time | **Only if the composition audit passes** (§6 step 1) | Largely |

**Residual bias:**
- Claude may recognise famous charts from training knowledge despite blinding. Mitigations: normalised scales and shuffled presentation order. Any label that names a company or event is recorded and excluded.
- A survivor-skewed population can make patterns that predict *survival* look like patterns that predict *returns*. That is why the composition gate exists.

## 5. Can separate chart-development and QuantConnect backtesting sources be used without contaminating validation? (requirement 7)

**Yes, but only with a split by time window. Using a different vendor is not enough.** Two vendors' charts of the same stock-dates show the same market history, so viewing WIKI's 2005 charts would contaminate a QuantConnect 1999–2009 test exactly as viewing QuantConnect's own would.

Proposed partition:

| Window | Use | Why |
|---|---|---|
| 1962–2009 | **Never viewed** | Keeps 1999–2009 available as TT-CP1's possible independent QuantConnect window (Phase 1b), and pre-1999 for stress tests |
| **2010-01 → 2017-12** | **WIKI chart development** (viewing, labelling, rule drafting) | Already spent for selection on QuantConnect; matches the IS end and the "no post-2017 motivation" rule |
| 2018-01 → 2018-03 | Never viewed (WIKI's last months) | Post-2017 hindsight rule |
| 2010–2021 on QuantConnect | Exploratory screen of the coded rules only (development evidence, never confirmation) | Exposed data |
| 1999–2009 on QuantConnect | Confirmatory test, **only if** the Phase 1b price / volume universe audit passes | Never viewed |
| 2022-01 → 2026-08 | Holdout (one candidate programme-wide, D267) | Sealed |
| After the freeze | Forward test | Independent by construction |

**Other rules:**
- Rules are frozen as deterministic code before any QuantConnect run.
- QuantConnect data never leaves QuantConnect; WIKI data never needs to enter it.
- A small translation canary checks that the coded rule computes the same features on WIKI and QuantConnect bars over the development window. Only aggregate agreement counts may leave QuantConnect, as in earlier canaries.

## 6. Recommended compliant workflow (if the owner approves; nothing here is authorised yet)

0. **Owner confirms the licence basis (C1)** and network access (C4). Optionally, the owner disables "Help improve Claude"; this is not required for public-domain data but is good practice.
1. **Composition audit (metadata only, no charts, no forward returns).**
   - Download WIKI.
   - Measure coverage against the identifier-only E981-01 Data v1 eligible stock-months for 2010–2017, matched by ticker and date with ticker-reuse checks.
   - Proposed gate, for the owner to approve before measuring:
     - ≥ 90% of eligible stock-months have WIKI bars;
     - ≥ 75% for securities that later left the universe through delisting or acquisition;
     - no single year below 80%.
   - Fail → stop, and the §8 decision applies.
2. **Frozen sampling protocol, committed before any rendering:**
   - about 300 (stock, decision-date) pairs from the covered eligible set, 2010–2017;
   - stratified by year and by dollar-volume tercile;
   - seed committed;
   - a data-quality screen;
   - fixed chart format: daily and weekly panels, bars ≤ decision date, anonymised, price normalised.
3. **Blind viewing.** Claude records structured observations, using the existing deterministic vocabulary where it fits (`qr_chart`: swings, HH / HL, zones, bases, breakouts) plus free-text "behaviour" notes. Labels are committed **before** any forward return exists.
4. **Outcome reveal (separate commit).** Forward returns for the sampled pairs are computed from WIKI; this is exploratory only. Candidate behaviours are translated into **deterministic rules**, at most a small pre-declared number.
5. **Then the normal chain:** the TT-CP1 Phase 1b audit (if approved), a frozen rule specification, a QuantConnect exploratory screen, and confirmatory evidence only on unviewed windows (§5).

**Effort:**
- Steps 1–2: about one session.
- Step 3: a few sessions, depending on chart count.
- Data cost: $0. QuantConnect cost: none until step 5.

## 7. Owner decisions needed

| # | Decision | Recommendation |
|---|---|---|
| C1 | Accept WIKI's stated public-domain basis after reading the host page `data.nasdaq.com/databases/WIKIP` and the Nasdaq Data Link site terms. Or ask Nasdaq Data Link for a one-line written confirmation. | Accept if the page reads as quoted |
| C2 | Approve the time-window partition in §5. WIKI viewing is limited to 2010–2017; 1962–2009 and 2018 are never viewed. | Approve |
| C3 | Approve the composition gate (§6 step 1) **before** it is measured, and the sampling protocol outline | Approve the thresholds as proposed, or tighten them |
| C4 | Allow `data.nasdaq.com` (and its download host) in the environment's network policy, and supply a free API key as an environment variable. It is never committed. | Required for any step |
| — | Paid vendors (EODHD / Norgate / Massive): not now; revisit only with written AI permission **and** a purchase decision under D124 | Defer |

## 8. If the conditions are not accepted or the composition gate fails: the owner's choice

- **Option Q — quantitative-only technical research.**
  - Continue TP-1 without chart viewing.
  - Rules come from the published literature and the deterministic vocabulary.
  - Evidence comes only from QuantConnect, if Phase 1b passes, and from forward testing.
  - The hybrid "Claude looks at real charts" element is dropped.
- **Option P — pause the hybrid programme.** SPY remains the baseline, and the programme waits until a source with explicit AI permission is affordable and approved.
- **Not an option:** synthetic charts as a replacement for empirical market analysis. Synthetic charts can test the renderer and the vocabulary; they cannot show how real stocks behave.

If the WIKI route fails, the recommendation is **Option Q only if** the owner still wants to pursue TP-1 on its quantitative merits (TT-CP1 rated its prior low to moderate); otherwise **Option P**.

## 9. GO / NO-GO

| Source | Decision |
|---|---|
| WIKI Prices (public domain, 2010–2017 window) | **CONDITIONAL GO**, for exploratory chart discovery only, subject to C1–C4 and the composition gate |
| TradingView | NO-GO for AI transmission (owner's personal viewing only) |
| EODHD / Massive / Tiingo / Norgate | NO-GO now (licence forbids; would need written permission plus a purchase decision) |
| Yahoo / Stooq | NO-GO (automated extraction prohibited / terms unverifiable) |
| QuantConnect data or images | NO-GO (requirement 6, D151) |

**STOPPED for owner review.** No data downloaded, no chart rendered or viewed, no purchase, no code, no backtest, Holdout sealed.

## Sources (accessed through search on 2026-10-23; vendor hosts blocked from this environment)

- Nasdaq Data Link, WIKI Prices product page and documentation: https://data.nasdaq.com/databases/WIKIP, https://data.nasdaq.com/databases/WIKIP/documentation
- Kaggle mirror (licence "Unknown"): https://www.kaggle.com/datasets/marketneutral/quandl-wiki-prices-us-equites
- Quandl wiki licence description (secondary): https://quanturf-dataset-alpha.readthedocs.io/en/latest/Docs/quandl.html
- Zipline issue on the WIKI freeze: https://github.com/quantopian/zipline/issues/2145
- ML4T WIKI provider notes: https://ml4trading.io/docs/data/providers/wiki_prices/
- TradingView Terms of Use: https://www.tradingview.com/policies/ (also https://in.tradingview.com/policies)
- EODHD Terms and Conditions: https://eodhd.com/financial-apis/terms-conditions; delisted data: https://eodhd.com/financial-apis/review-delisted-stock-companies-data
- Massive terms: https://massive.com/legal/individuals-terms-of-service, https://massive.com/legal/market-data-terms-of-service, https://massive.com/legal/businesses-terms-of-service, https://massive.com/terms/market_data_terms.pdf; pricing (third-party): https://algodataindex.com/vendors/massive/
- Tiingo: https://app.tiingo.com/tos/, https://www.tiingo.com/documentation/general/overview
- Norgate packages: https://norgatedata.com/stockmarketpackages.php
- Nasdaq Data AI Policy: https://www.nasdaqtrader.com/TraderNews.aspx?id=DN2025-2, https://www.nasdaqtrader.com/content/AdministrationSupport/AgreementsData/Data_AI_Policy.pdf
- Anthropic, Updates to our consumer terms (fetched directly): https://www.anthropic.com/news/updates-to-our-consumer-terms
- Yahoo automated-access clause (secondary): https://geonode.com/blog/how-to-scrape-yahoo
- Stooq (no terms text found): https://github.com/api-evangelist/stooq
