# P4-CP3 / P4-CP3R source references (cross-sectional technical signal validation, H019)

**Verification** follows the same convention as `P4_CP2_references.md`:
- **Verified** = details checked on 2026-10-04 against search records of the publisher, SSRN, RePEc or the author's page.
- **Memory** = from memory; verify before quoting any magnitude.

**Access limits.** The network policy of this session blocks the paper PDFs (author pages, archive.org, Semantic Scholar, practitioner sites). The formulas below therefore rest on the papers' abstracts and on several independent search records that quote the definitions. **Before freezing the specification, the two formulas should be checked against the full texts.**

**† = published after 2017.** Used only to caution, never to motivate.

## Signal definitions

| Ref | Status | What is used |
|---|---|---|
| Jegadeesh & Titman (1993), JF 48, 65–91; Fama-French "prior (2–12)" convention | Memory (convention widely documented) | **S1:** cumulative return from month t−12 to t−2, i.e. skipping the most recent month |
| Da, Gurun & Warachka (2014), "Frog in the pan: continuous information and momentum", RFS 27(7), 2171–2218 | Verified (search records: [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1745247), [Chapman](https://digitalcommons.chapman.edu/business_articles/115/)) | **S2.** ID = sgn(PRET) × [%neg − %pos]: %pos and %neg are the percentages of positive and negative daily returns in the formation period; sgn(PRET) = +1, −1 or 0. PRET is the cumulative return over the past twelve months, skipping the most recent month. The strategy uses a sequential double sort on PRET and then ID. Reported: six-month momentum falls monotonically from 5.94% (continuous information) to −2.07% (discrete information) at similar formation returns; continuous-information momentum does not reverse in the long run |
| Gray & Vogel (2016), *Quantitative Momentum* (Wiley) | Memory (chapter list verified: [O'Reilly](https://www.oreilly.com/library/view/quantitative-momentum/9781119237198/c08.xhtml)) | Practitioner adoption of the frog-in-the-pan measure as the "quality of momentum" screen applied after a momentum sort (level 3; pre-2018) |
| Grinblatt & Moskowitz (2004), JFE 71(3), 541–579 | Verified ([RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:71:y:2004:i:3:p:541-579)) | Rejected alternative: consistency of past *monthly* returns (and tax-loss selling) |
| Han, Zhou & Zhu (2016), "A trend factor: any economic gains from using information over investment horizons?", JFE 122(2), 352–375 | Verified ([RePEc](https://ideas.repec.org/a/eee/jfinec/v122y2016i2p352-375.html), [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2182667)) | **S3.** MA of lag L for stock j at month t = the average of the last L daily closes ending on the last trading day of the month. It is normalised by that day's close (Ã = A / P). Lags 3, 5, 10, 20, 50, 100, 200, 400, 600, 800 and 1,000 days. Monthly cross-sectional regressions of next-month returns on the normalised MAs; the expected-return forecast uses the past twelve months' average coefficients. The factor captures short-term (reversal), intermediate (momentum) and long-term (reversal) trends together |
| Marshall, Nguyen & Visaltanachoti (2017), Quantitative Finance 17(3) | Verified (P4-CP2) | MA rules and time-series momentum carry the same information, so S3 is expected to overlap with S1 |

## Inference and testing

| Ref | Status | What is used |
|---|---|---|
| Fama & MacBeth (1973), JPE 81(3), 607–636 | Memory | Cross-section per date, then the time series of the per-date statistics |
| Newey & West (1987), Econometrica 55(3), 703–708 | Memory | HAC (Bartlett) standard error of the time-series mean |
| Hansen & Hodrick (1980), JPE 88(5) | Memory | Overlapping-horizon returns create moving-average dependence of order h − 1 |
| Grinold & Kahn (2000), *Active Portfolio Management* (2nd ed.) | Memory | Information coefficient: the rank correlation of a signal with subsequent returns |
| Romano & Wolf (2005), Econometrica 73(4); White (2000), Econometrica 68(5) | Memory | Max-statistic (family-wise) resampling control over a set of strategies |
| Freedman & Lane (1983), J. Business & Economic Statistics 1(4) | Memory | Residual-permutation test for partial effects (considered; not adopted, §29 of P4-CP3) |
| Chung & Romano (2013), Annals of Statistics 41(2) | Memory | Studentised permutation statistics stay valid when the null distribution's variance differs; reason for permuting t-statistics, not raw means |
| Moskowitz & Grinblatt (1999), JF 54(4), 1249–1290 | Memory | Industry momentum explains part of stock momentum (sector diagnostic) |
| Fama & French 12-industry classification from SIC codes (Kenneth French Data Library) | Memory | Sector groups for the sector-neutral diagnostic, mapped from point-in-time SEC SIC codes (`qr_industry`, data v1) |
| Patton & Timmermann (2010), JFE 98(3), 605–625 | Memory | Formal monotonic-relation test (considered; the simpler pre-registered monotonicity rule is used instead) |
| McLean & Pontiff (2016), JF 71(1) | Memory | Post-publication decay: expect smaller effects than published |
| † Ben-David, Li, Rossi & Song (NBER w28624) | Verified (P4-CP2) | Caution: US momentum weakened after 2002 |


## P4-CP3R verification of the two primary definitions (2026-10-04)

**What was reachable.** This session's network allowed only GitHub (git) and the web-search tool. Every journal, SSRN, NBER, RePEc, author and archive host was blocked, so the full papers were again unavailable.

**What was used:**
- Search records quoting the papers.
- For the trend factor, a **complete independent reproduction**: Chen & Zimmermann, "Open Source Cross-Sectional Asset Pricing" (Critical Finance Review 2022; code `github.com/OpenSourceAP/CrossSection`, commit 8db8924, 2025-10-22). Files: `Signals/pyCode/Predictors/TrendFactor.py`, `Signals/LegacyStataCode/Predictors/TrendFactor.do`, `SignalDoc.csv`. OSAP rates its replication of TrendFactor "1_good" and the original evidence "1_clear" (t = 15.0, EW quintile long-short, 1.63% a month, 1930–2014).

### Da, Gurun & Warachka (2014), "Frog in the Pan" — verified vs uncertain

| Item | Status | Source |
|---|---|---|
| ID = sgn(PRET) × (%neg − %pos); +1 = discrete, −1 = continuous; range [−1, 1] | **Verified** (several independent records quote the same formula) | Search records of the paper and of replications (SSE thesis 2022; EFMA 2024 paper; Lee, Huang, Song & Xiang, JFE 2022 †) |
| PRET = the cumulative return over the past twelve months, skipping the most recent month | **Verified** (quoted verbatim in two independent records) | Search records |
| %pos / %neg = the percentages of days in the formation period with positive / negative (daily) returns | **Verified** (wording) | Search records |
| Sequential double sort: first on PRET, then on ID | **Verified** | Search records ("double-sorted portfolios sequentially that first condition on formation-period returns (PRET), then information discreteness") |
| PRET groups are quintiles | Probable (one replication record says "quintile sorting") | Search record |
| Zero-return days in the denominator | Implied by "percentage of days"; not quoted explicitly | — |
| A minimum number of daily returns | Not found; **project rule: 200** | — |
| sgn(0) = 0 | Verified in the formula records ("equals 0 when PRET = 0") | Search records |

**Materiality.**
- The formula, the window and the sort order are verified.
- The unverified items affect only ties and bucket granularity:
  - zero-return days are rare for liquid stocks ≥ $5 and ≥ $2B;
  - the quintile grid is the replicated convention.
- They are frozen as explicit conventions. **Assessed as not material.**

### Han, Zhou & Zhu (2016), "A Trend Factor" — verified vs uncertain

| Item | Status | Source |
|---|---|---|
| MA lags 3, 5, 10, 20, 50, 100, 200, 400, 600, 800, 1,000 days | **Verified** | Search records and the OSAP code |
| A_L = mean of the last L daily closes ending on the last trading day of the month, normalised by that day's close | **Verified** | Search records and the OSAP code |
| Monthly cross-sectional OLS of next-month returns on the 11 normalised MAs | **Verified** | OSAP code (`asreg fRet A_*`, intercept added) and search records |
| E[β] = the average of the past 12 months' coefficients, using only regressions whose returns are already realised | **Verified** | OSAP code (`shift(1).rolling_mean(12)`; "leaving out most recent one to not use future information") and search records |
| Expected return = Σ E[β_L] × A_L; sort into quintiles | **Verified** | OSAP code and SignalDoc |
| Price = |prc| / cfacpr (split-adjusted, not dividend-adjusted) | **Verified** (OSAP) | OSAP code; the ratio is unaffected by later splits |
| Minimum observations for an MA | **Paper silent** (OSAP comment); OSAP allows partial windows (min 1). **Adopted** | OSAP code |
| Partial 12-month beta windows | OSAP allows (min 1). **Not adopted: 12 required** (the paper's stated 12-month average) | OSAP code |
| Regression sample | Paper / OSAP: NYSE / AMEX / Nasdaq common stocks, price ≥ $5, size ≥ the NYSE 10th percentile. **Adapted: the H019 eligible universe** (≥ $2B, price ≥ $5, ADV20 ≥ $5M), the only point-in-time cross-section available here | OSAP code and SignalDoc |

**Materiality.**
- The construction is fully specified.
- The only deviation is the estimation cross-section, a documented adaptation forced by the data. **Assessed as not material for the method.**
- The resulting factor is **"the Han-Zhou-Zhu trend factor estimated within the ≥ $2B universe"**.
