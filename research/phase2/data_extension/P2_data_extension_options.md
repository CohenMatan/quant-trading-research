# Preparatory Study A: options for extending development history toward 2000 (P2-CP12, 2026-10-03)

- **Scope:** research only. **Nothing was purchased, no account was opened and no trial was started.**
- **Method:**
  - Provider websites are blocked by this environment's network policy (`norgatedata.com`, `data.nasdaq.com`, `sharadar.com`, `eodhd.com`, `tiingo.com`, `polygon.io`, `financialmodelingprep.com`, WRDS / CRSP; all `EGRESS_BLOCKED`). Facts below come from web-search results (sources listed) and QuantConnect's documentation, which is reachable.
  - **Every price and licence term must be re-checked on the provider's own page before any decision.**
- **What a faithful 2000–2021 extension needs** (the D033 standard: a faithful universe, not a proxy):
  1. point-in-time shares outstanding or market cap, **including companies that later died**;
  2. identifier history (ticker changes, re-used tickers, CIK);
  3. corporate actions (splits, dividends, mergers, delistings) and survivorship-free prices;
  4. (for fundamental families) point-in-time statements keyed by the date they became public;
  5. (for event families) earnings dates;
  6. a licence that allows personal research use inside our pipeline;
  7. Python access and a realistic path into the QuantConnect-based architecture.

## 1. What we already have (no purchase)

| Component | 2000–2009 status |
|---|---|
| Prices (AlgoSeek on QuantConnect) | 1998+, survivorship-free (delisted names trade until their end) |
| Corporate actions (QuantConnect Security Master) | 1998+; audited for 2010+ only |
| SPY total return | 1998+ |
| SEC 8-K earnings-release timestamps | 2003–2004+ (P2-CP11 probe), survivorship-safe |
| Point-in-time market cap / shares for the ≥ $2B universe | **Missing:** new Morningstar dataset has no market cap before Oct 2009; dead companies have no fundamentals in either QuantConnect dataset |
| Point-in-time statements | **Missing** for dead companies; SEC XBRL starts 2009–2011 |

**Conclusion:** the universe (point-in-time shares / market cap with dead companies) is the binding gap. Prices and actions are already in hand.

## 2. Provider comparison

| | **Sharadar Core US Equities Bundle** (Nasdaq Data Link) | **Norgate Data** (Platinum) | **EODHD** (All-In-One) | **CRSP / Compustat** (WRDS) | Financial Modeling Prep | Tiingo |
|---|---|---|---|---|---|---|
| Historical start | Fundamentals Dec 1997 / Jan 1998; prices 1998 | Prices 1990 | Prices decades; fundamentals history varies by company | 1926 (CRSP), 1950s (Compustat) | Varies | Prices 1962; fundamentals "20+ years"; **delisted ≈ 2015+ only** |
| Coverage | 16,000+ US companies (≈ 9,000 delisted) | US major exchanges + delisted | Global incl. US delisted | Complete US | US + global | ≈ 14,000 assets |
| Dead companies | **Yes** | **Yes** (prices) | Yes (flag `delisted=1`) | **Yes** | Delisted list (free tier) | Partly (≈ 2015+) |
| Historical shares | **Yes:** `sharesbas` per filing, keyed by `datekey` | **No** (current only) | Yes (`outstandingShares` history) | Yes | Unclear | Unclear |
| Historical market cap | **Yes:** daily `marketcap` (shares × price × share factor) | **No** (current only) | Partly | Yes | Yes ("historical market cap" endpoint) | Daily metrics |
| Fundamentals | ≈ 150 indicators; **as-reported (ARQ/ARY/ART) and restated (MRQ…) dimensions** | Current snapshot only | Full statements (as-of status unclear) | Yes (Compustat point-in-time products) | Yes | Yes |
| Earnings / events | Filing dates (`datekey`); "events" table (8-K items) | No | Earnings calendar (also sold on QuantConnect from 1998, with estimates) | IBES separately | Earnings calendar | No |
| Point in time? | **Yes** for ARQ rows: use the first session strictly after `datekey` (filing date) | Prices / constituents yes; fundamentals no | **Unverified** | Yes (with care) | Unverified | Unverified |
| Survivorship-safe? | Yes | Yes (prices, historical index constituents back to the 1990s) | Claimed | Yes | Partly | Partly |
| Format / API | Nasdaq Data Link REST / bulk CSV; Python | Desktop app NDU (**Windows only**) + Python package | REST; Python | WRDS SQL / Python | REST | REST |
| QuantConnect compatibility | Indirect: QuantConnect supports Nasdaq Data Link custom data with an API key, or we pre-compute a derived monthly universe table and upload it | Poor (Windows desktop; our engine is cloud Linux) | Partial (QuantConnect sells EODHD calendars; fundamentals via custom data) | Not for individuals | Custom data | Custom data |
| Licence | Personal, non-transferable; **no redistribution or sharing of raw or reverse-engineerable derived data**; professional use needs a professional licence | Personal subscription | Personal plans | **Academic / institutional only** | Personal plans | Personal plans |
| Price (to re-verify) | **≈ $69/month or $499/year full history** (≈ $29/mo 5 years; ≈ $49/mo 10 years) | **$630/year** ($346.50 / 6 months) | **$99.99/month** ($999.90/year) | Not available to individuals | Not verified | Not verified |
| Integration effort (estimate) | 2–4 weeks: download, identity map (Sharadar ticker / permaticker table → QuantConnect security ids for 2000–2009), derived universe table, audit + canaries, freeze v2 | Large (Windows VM) and does not solve shares / market cap | 3–5 weeks plus an independent point-in-time audit | — | Unknown | Not sufficient (delisted 2015+) |
| Major risks | Mapping dead tickers to QuantConnect ids; `sharesbas` share-class subtleties (multi-class firms); licence for storing derived tables in QuantConnect; budget (+$69/mo → total ≈ $93/mo, within the $100 target) | No historical fundamentals or market cap at all; Windows dependency | Point-in-time status unverified (restated statements would leak); cost at the budget limit (+$100 → ≈ $124/mo) | Not purchasable by us | Data provenance / point in time unverified | Delisted coverage too short |

**Sources (search results, 2026-10-03):**
- [Sharadar datasheet](https://resources.quandl.com/a/res-hub/Sharadar_Datasheet_final.pdf);
- [Sharadar SF1 documentation](https://data.nasdaq.com/databases/SF1/documentation);
- [Sharadar fundamentals docs](https://sharadar.com/docs/fundamentals);
- [Sharadar subscribe](https://sharadar.com/subscribe);
- [QuantRocket Sharadar pricing](https://www.quantrocket.com/pricing/data/sharadar/);
- [Nasdaq Data Link terms](https://data.nasdaq.com/terms);
- [QuantConnect Nasdaq Data Link docs](https://www.quantconnect.com/docs/v2/writing-algorithms/datasets/nasdaq/data-link);
- [Norgate stock market packages](https://norgatedata.com/stockmarketpackages.php);
- [Norgate fundamental field definitions](https://norgatedata.com/fundamental-field-definitions.php);
- [norgatedata on PyPI](https://pypi.org/project/norgatedata/);
- [EODHD pricing](https://eodhd.com/pricing);
- [EODHD fundamentals API](https://eodhd.com/financial-apis/stock-etfs-fundamental-data-feeds);
- [EODHD delisted data](https://eodhd.com/financial-apis/delisted-stock-companies-data-2);
- [WRDS / CRSP access](https://www.tidy-finance.org/python/wrds-crsp-and-compustat.html);
- [FMP historical market cap](https://site.financialmodelingprep.com/developer/docs/stable/historical-market-cap);
- [FMP delisted companies](https://site.financialmodelingprep.com/how-to/how-to-handle-delisted-companies-and-historical-symbols-with-a-free-api);
- [Tiingo fundamentals](https://www.tiingo.com/documentation/fundamentals);
- [Tiingo delisted (AmiBroker forum)](https://forum.amibroker.com/t/tiingo-and-delisted-stocks/26140);
- [QuantConnect EODHD Upcoming Earnings](https://www.quantconnect.com/data/eodhd-upcoming-earnings).

## 3. The free route: EDGAR reconstruction (about 2000–2009)

**Goal:** point-in-time shares outstanding for every US company that would have been ≥ $2B, including the dead ones, from SEC filings. Market cap = shares × the QuantConnect raw close.

| Item | Estimate |
|---|---|
| Source | 10-K / 10-Q cover pages ("As of [date], N shares … outstanding"). Plain-text / HTML only before 2009 (no XBRL `dei` facts) |
| Volume | About 1,500–2,500 registrants × 4 filings a year × 10 years ≈ **60,000–100,000 documents**, about 0.2–2 MB each. The request budget is fine at 8/s (≈ 3–4 h), but the disk allowance forces streaming extraction (keep numbers only) |
| Extraction | Regex + table parsing of cover pages. Hard cases: multiple share classes, "as of" dates far from period end, numbers in words, exhibits, amended filings. Expected first-pass error rate: high single digits to low double digits (%); needs manual review loops |
| **Identity mapping** (the hardest part) | No structured ticker ↔ CIK history before 2009. Dead registrants must be matched to QuantConnect security ids from company names (EDGAR "former names"), ticker mentions in press-release exhibits ("NYSE: LEH"), and price-continuity fingerprints (implied market cap vs known values). Our 2010+ identity work (identity v1/v2) needed multiple iterations and still left about 0.5–1.2% unresolved a year; pre-2009 is harder (no XBRL instance prefixes) |
| Audit burden | Independent verification has no free reference. Possible partial checks: the old QuantConnect dataset's market cap for **survivors** (retired by QuantConnect on 2026-10-31, i.e. it would have to be used within weeks), known index weights, spot checks. Then a canary series and a freeze v2 |
| Engineering time | **≈ 6–10 weeks** of focused work, plus owner review cycles |
| Maintenance | Low after the build (historical, static), but every later bug fix means a new freeze version |
| Main risks | Silent identity errors (wrong company ↔ security), class-share errors (2× market cap), missing dead companies (survivorship bias re-enters), exceeding the disk allowance |

## 4. Paid vs free, and what is worth considering

1. **Data integrity first.**
   - Sharadar is the only option found that provides **point-in-time share counts and market caps, dead companies and as-reported fundamentals from 1998** in one dataset, at a price inside the budget target.
   - Its weaknesses: a second identity map (Sharadar → QuantConnect ids) and a licence that forbids sharing raw or reverse-engineerable derived data.
2. **The EDGAR route is free but slow and riskier.**
   - Its hardest part, identity for dead registrants, is exactly where silent survivorship bias would re-enter.
   - It is not recommended as the primary route.
3. **Norgate is excellent for survivorship-free prices and historical S&P 500 membership.**
   - It does not provide historical shares or market cap, and needs Windows.
   - It does not meet requirement 1. It would only make sense if a future hypothesis were defined on S&P 500 membership rather than ≥ $2B market cap (a separate owner decision).
4. **EODHD:** point-in-time status unverified and costlier; second choice at best, after a point-in-time audit.
5. **CRSP / Compustat:** the research standard, but not purchasable by an individual.

**Is it worth it?**
- Power: P2-CP11 §7 and Amendment 3 calibration show that about 22 years instead of 12 roughly halves the edge needed for an even chance. That is the single largest improvement available.
- Cost: ≈ $69/month (or $499/year) plus 2–4 weeks of integration and audit.
- I consider it **worth a time-boxed, read-only evaluation** (e.g. one month, after verifying licence terms for derived tables in QuantConnect) before any commitment, **only if** you intend to continue research beyond the final Phase 2 slot.
- If Phase 2 is the end of the programme, it is not worth buying.
