# SO-CP0 — Spin-off research, Stage 0 desk review: NO-GO and PAUSE

- **Decision trail:** D290 is the owner's approval of Stage 0 only (verbatim in `docs/owner/2026-10-22_spinoff_stage0_approval.md`). This checkpoint is D291.
- **What was done:**
  - a literature and product review using web search;
  - a listing of the existing local files.
- **What was not done:** no event census, data retrieval or parsing, QuantConnect run, return calculation, purchase or constraint change. The Holdout was not accessed.
- **Limits of this review (disclosed):**
  - The environment's network policy blocks the hosts that carry the full texts (journal, university and SSRN servers), so the review rests on abstracts and secondary summaries. Claims taken only from summaries are marked *(secondary)*. No number below should be relied on without reading the source paper.
  - Recent spin-off ETF returns turned up in the searches fall inside the sealed Holdout window (2022-01 → 2026-08). **They are deliberately neither recorded here nor used.**

## 1. Result in one paragraph

**The published evidence does not support a clear, positive, post-cost spin-off effect after 2000 against the benchmark we care about (SPY).**
- **Benchmark-dependent:** the long-run outperformance of spun-off subsidiaries is strong against size / book-to-market reference portfolios, but weak or absent against matched firms and factor models.
- **Mixed after 2000:**
  - one study finds a positive effect in 2001–2012, which its authors suggest may be luck;
  - another finds average (not abnormal) returns for conventional spin-offs in 1994–2005;
  - the main spin-off ETF roughly matched the S&P 500 over its first decade, before fees.
- **Mechanism contested:** the direct test found institutions do rebalance at the spin-off, but that the selling is not associated with abnormal price movements.
- **Data:** a complete, verifiable 1998–2009 event list cannot be built from our existing files. Even with new retrieval, there is no ground-truth list to check completeness.
- **Not independent:** 1998–2012 is heavily covered by the published studies that motivated the idea, so it would be a replication, not independent confirmation.
- **Economics at $100,000:** the expected whole-account effect is small and very noisy.
- **Decision gate:** three of the four conditions are not supported. **Recommendation: NO-GO and PAUSE.**

## 2. Published evidence

| Study | Sample | What it measures | Finding | Bearing |
|---|---|---|---|---|
| Cusatis, Miles & Woolridge (1993, JFE) | 146 spin-offs, 1965–1988 | 3-year post-spin returns vs matched firms | Positive for subsidiaries and parents, concentrated in firms later taken over *(secondary)* | Supports; the gain runs mainly through **takeovers**, not forced selling |
| McConnell, Ozbilgin & Wahal (2001, J. Business) | 1989–1995, out of sample after CMW | An **ex ante** strategy | Does **not** beat matched firms or the Fama–French three-factor model; typically beats size / B/M portfolios. "A shaky basis for rejecting the efficient market hypothesis" | **Against / benchmark-dependent** |
| Desai & Jain (1999, JFE) | 1975–1991 | Focus-increasing vs non-focusing spin-offs | Focus-increasing spin-offs outperform *(secondary)* | Conditional support (a selection rule, not all spin-offs) |
| McConnell & Ovtchinnikov (2004, JOIM) | 311 spin-offs, 1965–2000 | Long-run excess returns | Subsidiaries: positive and significant over nearly all horizons after risk adjustments. Parents: none after removing one outlier. About −1.9% in the 15 days after the spin-off, positive after about 60 days *(secondary)* | Supports, over a sample ending 2000 |
| Abarbanell, Bushee & Raedy (2003, J. Business) | About 179 spin-offs, 1980–1996 *(secondary)* | Institutional rebalancing vs price pressure | Institutions rebalance, but this trading is **not associated with abnormal price movements** for parents or subsidiaries | **Against the forced-selling price-pressure mechanism** |
| Brown & Brooke (1993, FAJ) | 74 spin-offs, 1980–1990 | Early price decline vs institutional divestiture | Early decline related to institutional selling | Supports the mechanism (short-term) |
| Klein & Rosenfeld (working paper 2008; published version not verified) | 182 conventional + 57 sponsored, 1994–2005 | 3-year performance | Conventional: **average** performance. Sponsored: significantly **negative** | **Against** for 1994–2005; sponsored deals are worse |
| McConnell, Sibley & Xu (2015, J. Portfolio Mgmt) | 146 spin-offs, 2001–2012 | Buy-and-hold vs size / B/M benchmark; spin-off ETF | Subsidiaries +17.1% over 22 months; parents +3.7% over 15 months; a strategy based on the earlier evidence "would have worked, though perhaps by luck" *(secondary)* | Supports after 2000, but only against **size / B/M**, with a small sample and the authors' own luck caveat |
| Veld & Veld-Merkoulova (2004, Europe) | European spin-offs to about 2000 | Long-run excess returns | Mostly insignificant | Against (outside the US) |

**Products** (only pre-2022 information used):
- **Invesco / Guggenheim S&P Spin-Off ETF (CSD):** launched 2006, expense ratio about 0.65%.
  - Until May 2016 it tracked the Beacon Spin-off Index (factor-ranked, about 40 names, cap-weighted). Since then it tracks the S&P U.S. Spin-Off Index (spin-offs of at least $1B float cap, held up to 4 years at launch, now 5; float-cap weighted with caps).
  - A trade-press report gives about +74.6% for CSD vs +76.9% for SPY from inception to roughly 2016 *(secondary; date not confirmed)*, with higher volatility.
  - A later critique reports roughly half the S&P 500's total return after the 2016 index change *(secondary; window not stated)*.
- **Reading:** the most direct investable implementation did not clearly beat SPY over its first decade, even before considering its fee. Composition (a factor screen, then float-cap weighting) differs from the equal-weight samples in the papers.

**Methodology caveat:**
- Most positive results use buy-and-hold returns against size / B/M reference portfolios.
- That method is known to be biased in favour of newly listed firms (Barber & Lyon 1997; Lyon, Barber & Tsai 1999), and spin-offs are new listings.
- Results that survive matched-firm and factor-model benchmarks are the relevant ones, and those are the weakest.

## 3. The exact investable mechanism and what it excludes

**Investable return:**
- buy the **new company** at the open of the first regular-way trading session after the distribution, or later;
- hold it 12–24 months;
- measure against **SPY** after costs.

**Not investable for us, or a different event:**

| Item | Why it is excluded |
|---|---|
| Announcement returns | They accrue to existing parent holders before we could act |
| Parent returns | A separate question; the weak, outlier-driven results are not the target |
| When-issued trading before the distribution | Thinly traded and not in our data |
| **Sponsored spin-offs** | Outside capital invested before the spin; Klein & Rosenfeld find negative returns. Excluded |
| **Split-offs** | Exchange offers: holders choose to exchange, so there is no forced receipt. Different mechanism |
| **Carve-outs / IPOs** | Selling shares to new investors; IPOs have their own documented long-run under-performance. Excluded, although carve-out-then-spin two-step deals blur the line |

**Mechanism candidates:**
1. **Forced or mandate selling** by parent holders whose index or mandate excludes the new company (smaller, different sector, dropped from the parent's index).
   - Plausible, and passive-fund growth since 2000 could strengthen it.
   - The direct test (Abarbanell et al.) found no associated price pressure. The supporting evidence (Brown & Brooke) is short-term only.
2. **Takeover channel:** spun-off firms become targets (Cusatis et al.). Real, but it is takeover risk, not mispricing from forced selling, and it is lumpy.
3. **Focus / incentive improvements:** an operating story, with partial support (Desai & Jain).

**Conclusion:** an economically clear forced-selling mechanism is **not** established by the evidence we could check.

## 4. Historical event-data availability (existing files only)

**What we have** (`data/sec_cache`, about 1.8 GB):

| Content | Scope | Use for spin-offs |
|---|---|---|
| `data.sec.gov` submissions JSON | 4,944 registrants plus continuation pages | Registrants gathered for our post-2009 large-cap work, so survivor-biased. Spin-off subsidiaries that disappeared before 2009 are largely absent |
| `www.sec.gov` filing headers and index pages | 53,568 `.hdr.sgml` + 8,308 index pages | Form 4 headers (H025) and LH-CP3 headers. Not spin-off filings |
| Monthly XBRL RSS | 2009-06 → 2021-12 | Starts after the proposed window |
| XBRL company facts / frames | Post-2009 XBRL | No pre-2009 coverage |

There are **no EDGAR form-type indexes** (full-index) for 1996–2009 in the cache. I did not count spin-off filings in the cache, because that would be the unauthorised census.

**What a complete 1998–2009 list would need** (new retrieval and parsing, not authorised):
1. EDGAR quarterly full-indexes 1996–2009, to find Form 10-12B / 10-12G registrations.
2. Their information statements (EX-99.1) for the distribution ratio and record / distribution dates.
3. The parents' 8-Ks (completion), and withdrawals (RW) for abandoned deals.
4. A separate search for spin-offs registered another way, or by already-reporting subsidiaries.

**What cannot currently be verified:**
- **Completeness.** Studies use CRSP distribution codes or SDC; we have neither (purchase, D124). There is no ground-truth list to measure coverage against.
- **Event-type classification** (pro-rata vs sponsored vs split-off vs carve-out-then-spin) from filings text alone at scale.
- **First regular-way trading date** without exchange records; when-issued trading is not in our data.
- **Pre-2009 price coverage of these specific names on QuantConnect.** RR3 shows delisted names exist before 2009, but coverage of spin-off subsidiaries is untested. Market caps are absent before late 2009.
- **Identity:** ticker reuse and successor CIKs need dated point-in-time mapping (our earlier identity work began in 2009).

## 5. Feasibility of the proposed independent window

- **Not independent of the literature:**
  - 1998–2009 lies inside published samples: McConnell & Ovtchinnikov to 2000, Klein & Rosenfeld 1994–2005, McConnell, Sibley & Xu 2001–2012.
  - Our own test there would be a **replication with our data and rules**, informative about implementability but not independent confirmation of a published anomaly.
  - The literature itself is mixed in exactly this window.
- **Genuinely new evidence would come only from:**
  - a prospective forward test after a freeze (years of events at roughly 10–25 a year); or
  - a period no study covers. After 2012 that means our exposed development window (2013–2021), which is unused for spin-offs but not pristine.
- **Feasibility as a confirmatory window:** low.

## 6. Economic relevance for a $100,000 long-only, unleveraged portfolio

**Opportunity frequency:**
- Published samples imply roughly 6–9 qualifying US spin-offs a year before 2000, about 12 a year in 2001–2012 (MSX), and about 20 a year in 1994–2005 under looser filters (Klein & Rosenfeld).
- Activity is **strongly clustered**: peaks around 2000, 2007 and the mid-2010s, and collapses after market falls (MSX).
- Overlapping 12–24-month holds would therefore give anywhere from a few to about 40 concurrent candidates, unevenly.

**Capacity at $100,000:**
- With the $5,000 minimum, a 20–30% satellite holds at most 4–6 names; even 50% holds about 9.
- The book could hold only a fraction of concurrent events (a selection rule is needed: first-come or size-ranked). It would carry large idiosyncratic and industry risk, and sit partly idle in event droughts (idle capital back in SPY).

**Costs and taxes:**
- Two trades per event and mid-cap spreads: small.
- Holds of at least 12 months qualify for long-term capital-gains treatment in a taxable account.
- Costs are not the obstacle.

**Whole-account effect** (scaling only, no expected return assumed):
- Excess return versus SPY ≈ satellite weight × (event-level excess − the satellite's factor tilt versus SPY − costs).
- Spin-offs are smaller, value-leaning new listings. Their return relative to SPY includes size and value exposure that can be negative for a decade, which is not alpha.
- The **evidence ratio does not improve with a small satellite** (SA-CP1): the satellite must prove its edge on its own events.

**Evidence a credible portfolio-level power analysis would need** (none is available without new work):
- the true event count per year under our filters;
- event-level SPY-relative return dispersion;
- **cross-event correlation** (same-month clustering, industry waves);
- the capacity-constrained selection rule;
- a decay-adjusted effect size from post-2000, factor-adjusted studies.

## 7. Decision gate

| Condition (owner D290) | Assessment |
|---|---|
| Credible evidence of a plausible positive **post-cost** effect **after 2000** | **Not supported.** Positive results are benchmark-dependent (size / B/M only), the one post-2000 study flags luck, conventional spin-offs show average returns in 1994–2005, and the main spin-off ETF roughly matched the S&P 500 over its first decade before fees |
| An economically clear forced-selling mechanism remains | **Not supported.** The direct test found no price pressure; the strongest historical channel is takeovers |
| A sufficiently complete, reproducible 1998–2009 event list appears feasible | **Not supported with existing resources.** No indexes in cache; no ground-truth list to check completeness without purchased CRSP / SDC data; event typing and first-trading dates unverifiable |
| A realistic path to meaningful portfolio-level terminal-wealth improvement | **Weak.** 4–6 concurrent names at $100,000, clustered events, factor tilt versus SPY, no evidence-ratio gain from a small satellite |

**Recommendation: NO-GO and PAUSE.**
- Do not design an event census.
- **Pause offensive strategy discovery** (consistent with SA-CP1 and LW-CP1 §7), and keep SPY as the offensive baseline.

**Evidence gaps that could reopen the question** (only by separate owner decision):
1. Full texts of McConnell, Sibley & Xu (2015) and the published Klein & Rosenfeld, with matched-firm and factor-model results after 2000.
2. A credible academic study covering spin-offs after 2012.
3. A licensed, complete event source (CRSP / SDC; a purchase decision under D124).

## 8. Status

- **Hypotheses:** no hypothesis registered (31 registered remain H001–H030 and H032; H031 parked draft).
- **Rejected / inconclusive lines:** H028 and H032 REJECTED; RR6 INCONCLUSIVE.
- **Holdout:** sealed; no Holdout-period product returns recorded or used.
- **Nothing was run, retrieved, built or bought.**

**STOP:** awaiting the owner.

## References (as located; full texts not accessible from this environment)

- McConnell, Ozbilgin & Wahal (2001), Spin-offs, Ex Ante, J. Business 74(2): 245–280 — https://www.researchgate.net/publication/24103336_Spin-offs_Ex_Ante ; https://econbiz.de/Record/spin-offs-ex-ante-mcconnell-john/10001578059
- McConnell & Ovtchinnikov (2004), Predictability of Long-Term Spinoff Returns, JOIM 2(3) — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=569283 ; https://www.researchgate.net/publication/228289308_Predictability_of_Long-Term_Spin-Off_Returns
- Klein & Rosenfeld, The Long-Run Performance of Sponsored and Conventional Spin-offs (working paper) — https://archive.nyu.edu/handle/2451/27458
- McConnell, Sibley & Xu (2015), The Stock Price Performance of Spin-Off Subsidiaries, Their Parents, and the Spin-Off ETF, 2001–2013, JPM 42(1): 143–152 — https://www.researchgate.net/publication/283556164
- Abarbanell, Bushee & Raedy (2003), Institutional Investor Preferences and Price Pressure: The Case of Corporate Spin-Offs, J. Business 76(2): 233–262 — https://ideas.repec.org/a/ucp/jnlbus/v76y2003i2p233-262.html
- Brown & Brooke (1993), Institutional Demand and Security Price Pressure: The Case of Corporate Spinoffs, FAJ — https://rpc.cfainstitute.org/en/research/financial-analysts-journal/1993/institutional-demand-and-security-price-pressure-the-case-of-corporate-spinoffs
- Veld & Veld-Merkoulova, Do spin-offs really create value? The European case — https://dspace.stir.ac.uk/bitstream/1893/451/1/Spinoff-jbf.pdf ; review (2009) https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1468-2370.2008.00243.x
- S&P U.S. Spin-Off Index launch / methodology — https://press.spglobal.com/2015-08-04-S-P-Dow-Jones-Indices-Launches-Spin-Off-IPO-and-Activist-Interest-Indices ; https://spglobal.com/spdji/en/documents/methodologies/methodology-sp-us-ipo-and-spin-off-indices.pdf
- CSD history (trade press) — https://www.etftrends.com/2016/03/spin-off-etf-tries-to-get-its-groove-back/ ; https://www.etf.com/sections/news/index-choice-key-spinoff-etfs
- Cusatis, Miles & Woolridge (1993, JFE); Desai & Jain (1999, JFE); Barber & Lyon (1997, JFE); Lyon, Barber & Tsai (1999, JF): standard references, cited from secondary summaries here.
