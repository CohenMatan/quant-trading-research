# TT-CP1c R1 — WIKI Prices audit on the downloaded data

**Date:** 2026-10-24 · **Owner direction:** D300 (`docs/owner/2026-10-24_wiki_audit_resume.md`) · **Decision record:** D301
**Code:** unchanged frozen protocol (pin 39a926b8…) and engine from PR #139. **Results:** `research/tt/wiki_audit/WIKI_AUDIT_result.json`. **Post-hoc diagnostics** (explain the result, never change it): `WIKI_DIAGNOSTICS_posthoc.json`.
**Handling:** everything was computed by code and only aggregates are reported. I did not see any price row, ticker-level series or chart, and none was rendered.

## Result (frozen gates): **INSUFFICIENT**

| Gate | Result | Measured | Frozen bound |
|---|---|---|---|
| A1 frame coverage (strict) | **PASS** | 90.1% overall; every year 85.6–94.2% | ≥ 90% overall and ≥ 85% each year |
| A2 leavers | **INCONCLUSIVE** | ACQUIRED (254 registrants) 74.0%; leavers 71.9% vs non-leavers 91.3% (gap 19.3 points); FAILED / DELISTED-OTHER / UNKNOWN each < 20 registrants | PASS needs ≥ 80% and gap ≤ 10; FAIL < 65% or gap > 20 |
| A3 strata | **PASS** | Lowest stratum with ≥ 50 registrants: foreign-style names 76.8%; financial / REIT 87.0% | none < 70% |
| A4 identity | **FAIL** | AMBIGUOUS 14.1% of frame registrant-months; UNRESOLVED-IDENTITY 9.1% | AMBIGUOUS ≤ 2% (FAIL > 5%) |
| A5 bar integrity | **FAIL** | Missing 0.055%, spikes 0.00005%, invalid bars 0.0037%, dividend factors 98.9% agree: all pass. **Adjustment ratio changes explained 82.7%**, which fails; split cross-check 88 / 100 agree, which is between the bounds | ≥ 99.5% explained (FAIL < 97.5%) |
| A6 curation decay | **FAIL** | 2017 strict coverage 85.6% vs mean 2014–2016 91.3%: a drop of 5.8 points | PASS ≤ 2; FAIL > 5 points |
| A7 chart sufficiency | **PASS** | Smallest year × size cell: 138 chart-ready registrants; 134 chart-ready leaver registrants | ≥ 20 per cell; ≥ 30 leavers |

Under the frozen rules, any FAIL makes the overall result INSUFFICIENT. Nothing was re-tuned.

## 1. Download

- **Source:** official free route, `https://data.nasdaq.com/databases/WIKIP`, via the API bulk export. No cost.
- **Access checks:** metadata request → HTTP 200; dataset not marked premium; schema matches the protocol; a zero-row query → 200.
- **File:** CSV of 1,797,003,576 bytes, 15,389,314 rows, SHA-256 `ca7fb174…3d003`. Data snapshot 2026-02-03; the dataset was last refreshed 2018-03-27.
- **Storage:** under `data/wiki/`, outside Git.

## 2. Stocks and daily observations, 2010–2017

| | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 |
|---|---|---|---|---|---|---|---|---|
| Tickers | 2,709 | 2,804 | 2,923 | 3,083 | 3,163 | 3,073 | 2,883 | 2,681 |
| Daily rows | 667,900 | 694,884 | 716,567 | 755,324 | 783,202 | 746,725 | 695,773 | 638,379 |

- **Totals:** 3,196 tickers and 5,698,754 rows in the window. Rows with any missing field: 0.0097%.
- **Trading calendar:** the derived calendar matches published NYSE session counts exactly, except 2017 (250 vs 251).
- **Ticker count over time:** falls after 2014, consistent with names delisting while few new ones were added.

## 3. What was measured (independent SEC frame: 1,614 registrants, 74,280 registrant-months)

- **Coverage.**
  - **Strict** coverage (WIKI bars on at least 90% of the month's sessions, among non-ambiguous registrant-months) is 90.1%.
  - **Resolved** coverage, counting only registrants whose ticker could be identified, is **99.1%**: where identity is known, WIKI almost always has the prices. The shortfall is mostly in **identity matching**, not in missing price histories.
  - Missing price histories proper are 501 registrant-months (0.7%).
- **Identity** (diagnostic):
  - Of the 10,471 AMBIGUOUS registrant-months, **7,532** come from a ticker prefix that another CIK filed under *in the same period*: parent and subsidiary co-filers, which is an SEC-side artefact.
  - **2,720** are genuine sequential ticker reuse.
  - **219** have a missing or shared prefix within the month.
  - Counting only the last two would give about 4.0%. That is still above the 2% PASS bound, so A4 would still not pass.
- **Adjustments** (diagnostic):
  - The 4,230 unexplained ratio changes sit in **21 tickers**, almost all in 2010–2014.
  - 94% of them are tiny, between 0.01% and 0.1%, most likely rounding of stored adjusted prices. Only 9 exceed 1%.
  - The frozen protocol removes those 21 tickers' affected months from any sample in any case.
  - Split cross-check against SEC share counts: 88 of 100 agree.
- **2017 decay** (diagnostic):
  - The 2017 shortfall is mostly identity classes among older registrants (AMBIGUOUS 1,814; UNRESOLVED 1,257).
  - There is also a genuine WIKI-side rise in whole months with no bars: 173 out-of-life months in 2017, against 19–63 in earlier years.
  - Resolved coverage is 97.9% in 2017 vs 99.2–99.7% in 2012–2016. A real but smaller decline, consistent with community curation ending in early 2018.
- **Liquidity:** measured from WIKI dollar volume only. 2014 tercile cuts were about $3.4M and $21.1M median daily dollar volume.

### Confirmed market exits vs registrants that only stopped filing (owner item 5)

- **Definition of a leaver:** a registrant whose last SEC 10-K / 10-Q is before 2018. That alone does **not** prove a market exit.
- **Leavers with frame months:** 275 registrants.

| Group | Registrants | Evidence |
|---|---|---|
| **Confirmed exit, acquired** | 254 | Merger proxy or tender-offer filings within 24 months before the exit |
| **Confirmed exit, failed** | 6 | 8-K Item 1.03 (bankruptcy) |
| **Confirmed exit, delisted (other)** | 5 | Form 25 without merger forms |
| **Stopped filing only (unconfirmed)** | 10 | No exit evidence in the cached SEC submissions |

**Price-side cross-check:** of the 145 confirmed-exit registrants that WIKI matches, **134 (92%) have WIKI histories that end within ±3 months of the SEC exit**. Six end earlier and five continue more than 3 months later, which suggests ticker reuse. WIKI therefore does contain the price histories of most **acquired** large caps up to their exit.

**Failures:** only **6** large-cap failures exist in the frame, and WIKI matches just 39% of their months. Failure representation cannot be established.

## 4. Can about 300 representative charts be supported?

- **On quantity: yes.** Every year 2011–2017 × size tercile cell has at least 138 chart-ready registrants (a full 252-session history), and there are 134 chart-ready leaver registrants, almost all acquired.
- **Under the frozen audit: no.** The data is classified INSUFFICIENT because of identity ambiguity (A4), adjustment consistency (A5) and 2017 decay (A6). A2 is inconclusive because acquired leavers are under-covered (74%), mainly through unresolved or ambiguous identity.
- **Fairness of the sample:** a sample drawn from the SEC frame would not select only historical winners. Acquired leavers are present in usable numbers. **Failed companies are effectively absent**, which reflects both the $2B frame and WIKI.

## 5. Limitations that remain

- **Not survivorship-free.** WIKI is not shown to be survivorship-free, and failures are barely represented.
- **Identity matching relies on SEC instance prefixes.** About 9% of registrant-months stay unresolved, and parent/subsidiary co-filers inflate ambiguity.
- **Adjustment defects.** 21 tickers have small inconsistencies, 9 changes exceed 1%, and 12 of 100 sampled splits disagree with the SEC share counts.
- **2017 is weaker** (curation decay).
- **No independent price source** beyond internal checks and SEC share counts.
- **Unresolved licensing:** transmission rights to Claude are still unresolved (Addendum 1). No chart has been rendered or sent.

## 6. Smallest next step

This is an owner decision; nothing proceeds without it.
- **(a)** Accept INSUFFICIENT and stop the WIKI route. Then choose quantitative-only research or a pause (TT-CP1b §8).
- **(b)** Grant an explicit, documented owner exception for **exploratory sampling only**. It would be recorded like earlier exceptions, with the failing gates staying recorded as FAILED, and these restrictions:
  - exclude AMBIGUOUS and UNRESOLVED identities;
  - exclude the 21 tickers with adjustment defects;
  - draw leavers from confirmed acquisitions only;
  - state that failures are absent;
  - optionally exclude 2017.

  Licensing (Nasdaq's confirmation of AI transmission) must still be resolved before any chart is rendered for Claude.

My assessment:
- **A4 and A5 fail largely for definitional or cosmetic reasons:** SEC co-filers, and tiny rounding concentrated in 21 tickers.
- **A6 and the leaver and failure coverage are substantive.**
- **For hypothesis discovery** (not evidence), option (b) is defensible but not certain. The choice is yours.

**Not done, as instructed:** no purchase, no change to any threshold, no strategy, no backtest, no chart, no 1999–2009 inspection, no Holdout. **STOPPED.**
