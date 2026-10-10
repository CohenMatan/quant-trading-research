# P7-CP5e — Universe Repair Feasibility Study

**Date:** 2026-10-10. **Decisions:** D188 (owner approval of option b), D189. **Status:** STOPPED awaiting the owner.

## Short answer

Both questions have a positive answer. Every success criterion was fixed and committed before any repair result existed (commit 0e63a03), and every one is met.

**Question A — market cap.** QuantConnect's new feed has no market cap for many companies. That market cap can be rebuilt from public SEC data, using the existing D111 method unchanged:

> SEC cover-page share count, usable from the day after filing, × splits since the cover date × raw price.

| Test | Result |
|---|---|
| Share count available for the stocks that lost their market cap | 86% |
| Continuous across splits | 223 of 224 splits |
| Agrees with QuantConnect's market cap on the $2B decision, away from $2B | 98.4% |
| Same, within ±10% of $2B | 95.7% |
| Median difference from QuantConnect's market cap | 0.03% |

**The survivorship bias found in P7-CP5d essentially disappears:**
- The repaired universe recovers 69% of the lost stock-months: 371 of 560 securities, including 232 of the 339 that later disappear.
- Its share of members still present at end-2017 is 84.1%. Data v1 had 83.3%; the delivered new feed had 90.0%.

**Question B — identity before 2011.** Public EDGAR filing histories can verify each company's SEC registrant before its first XBRL filing:
- 1,333 securities are SAFE and 474 have a bounded start.
- 105 were rejected: genuine reorganisations such as spin-offs and renamed successors.

Reports matched through these rows agree with SEC figures as often as normally matched reports:

| Field | Extension rows | Identity-v2 rows |
|---|---|---|
| Revenue | 92.8% | 91.6% |
| Total assets | 97.9% | 98.2% |

With M2 and the verified identity, fully scored stocks per month become:

| Year | Without the extension (E997-02) | With it (E997-01) |
|---|---|---|
| 2011 | 0–41, median 10 | 304–378, median 360 |
| 2012 | 46–210 | 359–406 |
| 2013–2017 | — | 407–734 |

Data v1 had 196–612 a month. A 2013 start is therefore **not forced**. Its cost is quantified anyway in section 35–36: it would raise the 50%-power IC from 0.033 to 0.050.

All three QuantConnect runs (default build 18178) passed the compliance review and completed with 0 orders. Two independent runs reproduced each other exactly.

**GO — universe can be repaired PIT-safely and Data v2 design can proceed.**

Nothing has been built or frozen. The proposed Data v2 architecture is in section 50; it needs the owner's approval. No return, IC or H022 statistic was computed.

## 1. Actual LEAN builds

| Run | What | Build | Result |
|---|---|---|---|
| E997-01 | X997 v1.0: M2 + shadow repaired universe + verified earlier identity | **18178** (default, recorded) | completed, 0 orders, 635 s |
| E997-02 | X997 v1.0: the same without the identity extension (the "before" baseline) | **18178** | completed, 0 orders |
| E997-03 | X997 v1.1 (adds per-security target counts only): identical rerun of E997-01 | **18178** | completed, 0 orders; reproduces E997-01 exactly |

## 2–6. Target population (frozen before any repair; `research/phase7/cp5e/target_population.json`)

- **Rule:** in the data-v1 universe (E993-02) but not in the new feed's universe (E993-03) at the same month-end review.
- **Size:** 560 securities and 18,915 stock-months (SHA-256 `f751460b…`). X997 recomputed the list in-cloud and matched the frozen digest.

**Stock-months by year:**

| Year | Stock-months |
|---|---|
| 2011 | 2,527 |
| 2012 | 2,363 |
| 2013 | 2,808 |
| 2014 | 3,131 |
| 2015 | 3,064 |
| 2016 | 2,638 |
| 2017 | 2,384 |

**Why each target stock-month was lost (in-cloud, at the review):**

| Reason | Stock-months | Share |
|---|---|---|
| **QuantConnect market cap missing** (all other filters pass) | **15,235** | **80.5%** |
| No fundamentals object on the new feed (and not in the D111 SEC layer) | 2,212 | 11.7% |
| New-feed market cap below $2B | 1,300 | 6.9% |
| Not common-stock type | 168 | 0.9% |

- 415 of the 560 securities lack a market cap in at least one month.
- P7-CP5d's ~85% checked market cap before price and ADV; here price and ADV are checked first.

**Later-disappearing share:**
- 339 of 560 securities (60.5%) are no longer in the data-v1 universe at 2017-12-29.
- So are 50.1% of the lost stock-months.

**Fate at end-2017** (public EDGAR filings dated ≤ 2017-12-31; `target_fate_shares.json`):

| Fate | Securities |
|---|---|
| Still in the universe | 221 |
| Acquired or merged (deregistration or exchange removal with merger filings) | 266 |
| Delisted for another reason | 0 |
| Still filing but outside the universe (fell below a filter) | 52 |
| Stopped filing, no deregistration found | 4 |
| No SEC identity | 17 |

## 7–12. SEC market-cap method

**7 — Source.**
- The cover-page `dei:EntityCommonStockSharesOutstanding` of each 10-K / 10-Q, taken from XBRL company facts:
  - only the filing's own cover;
  - only one unambiguous non-dimensional value.
- Multi-class registrants that report per class are left unresolved, as in D111.
- Weighted-average shares are never used.
- 65,604 cover counts from 104,053 periodic filings of 3,289 registrants. Counts are used from filings made from 2010-06 onwards.

**8 — Coverage of the targets:**
- A fresh SEC count exists for 87.4% of target stock-months (offline, all loss reasons).
- In-cloud, a fresh SEC market cap is computable for **85.95%** of the 15,235 stock-months that lack a QuantConnect market cap.

  | Status | Stock-months |
  |---|---|
  | Repaired | 13,038 |
  | SEC market cap below $2B | 57 |
  | Share count stale | 456 |
  | No SEC identity at the time | 757 |
  | Registrant without counts in the table | 927 |

**9 — Timing.**
- Each count has two dates: the cover date (when it was measured) and the filing date (when it was published).
- A count is usable only from filing date + 1 day.
- The latest usable count by cover date is used, and only while it is ≤ 135 days old.
- The repair is computed at the end of the run from values recorded at each review. Only filings, splits and prices up to the review day enter.
- Typical age when used: median 60 days, 90th percentile 93.

**10–11 — Splits.** QuantConnect split events with ex-date after the cover date and on or before the day multiply the count. If a split falls between the cover date and the filing, the count is not adjusted when the previous filing shows the reported count already reflects it (the D111 rule).

The test covers every split of 2011–2017 (factor ≥ 1.4) of a panel security that has SEC counts:

| Result | Splits |
|---|---|
| SEC market cap continuous across the split (does not jump with the raw price) | **223** |
| Ambiguous | 1 |
| Jumps with the price | 0 |
| Not evaluable: no SEC identity | 34 |
| Not evaluable: no count | 10 |

**12 — Issuance and buybacks.**
- The last public count is held until a newer filing publishes a new one. There is no interpolation.
- Between quarterly covers the error is the change in share count over that quarter (typically < 1–2%).
- That is small next to the 0.03% median and 2.0% 90th-percentile differences from QuantConnect's market cap.

## 13–15. SEC market cap vs QuantConnect market cap (where both exist; 91,693 review stock-months)

| Measure | Result |
|---|---|
| SEC market cap available | 88,322 (96.3%) |
| Relative difference ≤ 2% / 2–5% / 5–10% / > 10% | 90.1% / 3.7% / 1.7% / 4.5% |
| Median / 90th percentile of the absolute difference | 0.03% / 1.96% |
| **Eligibility agreement, QuantConnect market cap outside $1.8–2.2B** | **98.42%** (81,504 / 82,809) |
| **Eligibility agreement, inside $1.8–2.2B** | **95.65%** (5,273 / 5,513) |

**Disagreements:**
- **Away from the threshold:** 1,305.
  - 1,184 have the SEC market cap above $2B while QuantConnect's is below $1.8B, with a difference > 10%. The pattern fits multi-class companies, where one cover count covers several share classes.
  - 121 the other way.
- **Near the threshold:** 240.
  - 121 (2.2%) are within 10% of each other (staleness, issuance, timing);
  - 119 (2.2%) are larger differences.
- The repair applies only where QuantConnect has **no** market cap. This 1.4% upward-classification risk is the main residual error of the repaired universe.

**Threshold bands for the repaired candidates** (SEC market cap, 23,228 candidate stock-months with a fresh count):

| Band | Stock-months |
|---|---|
| < $1.5B | 6,593 |
| $1.5–1.8B | 2,022 |
| $1.8–2.0B | 1,158 |
| $2.0–2.2B | 922 |
| $2.2–2.5B | 1,290 |
| > $2.5B | 11,243 |

379 stock-months lie within $1.8–2.2B with a count older than 90 days, the months where staleness could plausibly flip eligibility.

## 16–22. Shadow repaired universe and survivorship

**16 — Rule:**
- the QuantConnect market cap if > 0;
- else the SEC-repaired market cap above;
- else ineligible.

All other filters are unchanged. SEC identity comes from identity-v2 rows only, so the universe is independent of question B. The repaired-universe digests are identical in all three runs.

**17–18 — Recovered:**
- 371 securities (232 of the 339 later-disappearing);
- **13,038 stock-months (68.9%)**, of which 66.8% of the later-disappearing stock-months.

Repaired members per month (mean, not limited to the targets):

| Year | Repaired members |
|---|---|
| 2011 | 140 |
| 2012 | 136 |
| 2013 | 164 |
| 2014 | 186 |
| 2015 | 183 |
| 2016 | 161 |
| 2017 | 150 |

**19–20 — Survivorship before and after** (stock-month-weighted share of members still in the data-v1 universe at 2017-12-29):

| Year | Data v1 | New feed as delivered | **Repaired universe** | Gap after repair (points) |
|---|---|---|---|---|
| 2011 | 74.5% | 85.4% | **77.2%** | +2.7 |
| 2012 | 78.3% | 87.5% | **80.1%** | +1.8 |
| 2013 | 78.1% | 87.3% | **79.7%** | +1.6 |
| 2014 | 79.1% | 87.7% | **80.4%** | +1.3 |
| 2015 | 82.8% | 89.7% | **83.6%** | +0.8 |
| 2016 | 90.1% | 94.2% | **89.8%** | −0.3 |
| 2017 | 95.7% | 95.5% | **93.7%** | −2.0 |
| **All** | **83.3%** | **90.0% (+6.7)** | **84.1%** | **+0.8** |

**21 — Remaining bias:**
- 5,877 data-v1 stock-months (6.3%) are still lost; 46% of them belong to securities present at end-2017.
- By security, 189 targets are never recovered:

  | Reason at the security's last lost month | Securities |
  |---|---|
  | No fundamentals object on the new feed | 68 (67 later disappear) |
  | New-feed market cap below $2B | 74 |
  | Market cap missing and no usable SEC count | 44 |
  | Not common type | 3 |

- 417 repaired stock-months belong to securities that data v1 never included (5.5% survivors). These are mostly companies near $2B whose SEC market cap is above the threshold.
- The pre-registered bias criterion is met: within 2.0 points overall and within 4.0 points in every year.

**22 — Market-cap repair: GO.** All of MC1–MC9 pass:

| # | Criterion | Result | Threshold |
|---|---|---|---|
| MC1 | PIT | By construction, plus tests | — |
| MC2 | Coverage | 86.0% | ≥ 75% |
| MC3 | Splits | 99.6% | ≥ 95% |
| MC4 | Agreement away from $2B | 98.4% | ≥ 97% |
| MC5 | Disagreement near $2B; median difference | 4.35%; 0.03% | ≤ 30%; ≤ 5% |
| MC6 | Recovery; later-disappearing | 68.9%; 66.8% | ≥ 60% each |
| MC7 | Bias gap overall; by year | +0.8; −2.0 to +2.7 | 2.0; 4.0 |
| MC8 | No future data | By construction | — |
| MC9 | Deterministic | Identical digests in E997-01/02/03 | — |

## 23–28. Earlier SEC identity

**23 — The gap.**
- Identity-v2 rows begin at each company's first XBRL filing, which is ticker-evidenced. For universe securities the first rows fall in:

  | First-row year | Securities |
  |---|---|
  | 2009 | 402 |
  | 2010 | 717 |
  | 2011 | 433 |
  | Later | the rest |

- The XBRL-only filing reference of P7-CP5d also lacked pre-XBRL filings.
- Under M2, earlier vendor reports cannot be matched to an SEC filing. True-TTM chains and 12-month revenue baselines therefore start late. E997-02 shows the result: 2011 median 10 scored stocks.

**24 — Sources used** (public, no vendor data):
- EDGAR submissions:
  - every filing with form, filing date and report date (pre-XBRL included);
  - former names with dates;
  - deregistration forms.
- Identity v2 and the v1 correction table.

**Not used:**
- Morningstar's CIK (current status);
- today's tickers (EDGAR lists only current ones);
- name or ticker similarity;
- CUSIP (not in the public submissions data).

The M2 "SEC original filing date" now also comes from EDGAR submissions, so pre-XBRL 10-Qs / 10-Ks count. The M2 rule itself is unchanged.

**25–27 — Results** (1,968 universe securities; `identity_extension.json`, one evidence record each):

| Category | Securities | Meaning |
|---|---|---|
| SAFE | **1,333** | The registrant filed every periodic report back past 2008-07-01, with no material name change, deregistration or predecessor security |
| SAFE WITH BOUNDED START | **474** | 368 because the registrant began filing after 2008-07 (the chain starts there); 106 bounded by a deregistration form (61) or a material name change (51) |
| AMBIGUOUS | 0 | — |
| REJECT | **105** | A material name change (92) or deregistration (13) within 120 days before the first XBRL row, i.e. a successor registrant. Examples: Alcoa Upstream → Alcoa (2016 spin-off), Alkermes plc, A&B II → Alexander & Baldwin, Antero Midstream GP. Not used |
| No identity row at all | 56 | Unchanged |

**28 — Continuity checks:**
- Unbroken periodic-filing chain, with no gap over 200 days.
- Material former-name change. Each name is compared with the name that replaced it, after normalisation, so "Apple Computer Inc" → "Apple Inc" counts and a change of case does not.
- Deregistration forms.
- A predecessor security linked to the same CIK: none found.
- **In-cloud:**
  - an extended row is used only while the security's QuantConnect feed presence has been continuous since the row start (179 lookups refused);
  - first-seen vendor values of reports matched through extension rows agree with the SEC first-filed value as often as normally matched reports: revenue 92.8% vs 91.6%, total assets 97.9% vs 98.2% (263 and 339 compared). ID2 passes.
- One caveat for the owner:
  - The evidence that a company *continued* (its first XBRL filing) is dated after the reports it is used for.
  - That evidence is public identity metadata, not market data.
  - It is used only to decide which SEC filing date gates a report.
  - A report still becomes usable only after its own SEC filing.

## 29–34. M2 coverage before and after identity repair (repaired universe, no returns)

| Year | Before (E997-02): H2, non-financial | Before: scored / month (mean) | **After (E997-01): H2** | **After: scored / month (mean)** | Securities mapped to an SEC registrant |
|---|---|---|---|---|---|
| 2011 | 98.0% | 13.2 | **46.2%** | **355** | 97.3% |
| 2012 | 76.4% | 159.6 | **42.5%** | **388** | 97.7% |
| 2013 | 47.2% | 410.9 | **40.2%** | **465** | 97.6% |
| 2014 | 30.5% | 606.8 | 28.2% | 627 | 97.5% |
| 2015 | 25.2% | 659.4 | 23.4% | 675 | 97.5% |
| 2016 | 21.4% | 671.5 | 21.2% | 674 | 97.7% |
| 2017 | 23.8% | 711.8 | 23.8% | 712 | 97.4% |

**Fully scored stocks per month (E997-01):**

| Period | Min | Median | Mean | Max |
|---|---|---|---|---|
| **2011** | **304** | **360** | 355 | 378 |
| **2012** | **359** | **389** | 388 | 406 |
| **2013+** | **407** | **662** | 631 | 734 |
| All 84 reviews | 304 | 631 | 557 | 734 |

- Data v1's H022 population was 196–612 a month (mean 479).
- Without identity repair (E997-02): 2011 had 0–41 (median 10), 2012 had 46–210.

**Other counts (E997-01):**
- Candidates (no hard disqualifier): 270 / 307 / 414 / 515 / 447 / 468 / 559 per month, 2011 → 2017.
- 80+ stocks: 7.1 a month, with 1 month at zero. E997-02: 5.6, with 16 months at zero.

**Missing-input causes in 2011** (presence among non-financial stocks):

| Input | Present |
|---|---|
| Revenue TTM | 66% |
| Gross profit TTM | 63% |
| Net income TTM | 68% |
| Operating cash flow TTM | 68% |
| Total assets | 97% |
| Equity | 97% |
| Valid 12-month baseline | 74% |

H2 stays higher in 2011–2013 (40–46%) than later (21–28%). Early vendor quarters in the new stream are patchier, and True TTM needs four consecutive quarters. The population nevertheless stays above 300 stocks every month.

**34 — 2011–2012 are salvageable:**
- ID4 / ID5 pass: every month ≥ 150 (minimum 304) and median ≥ 250 (360 and 389).
- ID1–ID3 pass.

## 35–36. If the window started in 2013 instead (quantified, not chosen)

**Size of the design:**
- 59 monthly decisions (2013-01-31 → 2017-11-30) instead of 83: 24 fewer (−29%).
- Any 2013 start would be forced by data availability, never chosen from returns. It is not forced now.

**Power.** The P7-CP4 synthetic study (real data-v1 score tables, synthetic returns, identical seeds and gates; `power_2013.json`):

| Scenario | Decisions | Synthetic c_IC | 50% power: IC (80+ excess / yr) | 80% power: IC (80+ excess / yr) | Pass rate at an edge of 0.4% / month |
|---|---|---|---|---|---|
| Main | 83 | 2.50 | 0.033 (+6.3%) | 0.047 (+10.2%) | 94% |
| Main | **59** | 2.70 | **0.050 (+10.7%)** | **0.090 (+18.8%)** | **59%** |
| Optimistic | 83 / 59 | 2.49 / 2.54 | 0.027 / 0.038 | 0.040 / 0.066 | 98% / 75% |
| Pessimistic | 83 / 59 | 2.48 / 2.73 | 0.040 / 0.064 | 0.056 / 0.112 | 84% / 38% |

- The null calibration stays valid: false promotion is 0–0.3%.
- But power deteriorates materially. A 2013-start H022 would detect only edges of about 11% a year or more with even odds.

## 37–41. Compliance, files, effort, runs, cost

**37 — Compliance.**
- All three runs passed QuantConnect's build-time compliance review and completed. None was stopped.
- The pattern was the same as P7-CP5d:
  - public SEC reference data uploaded;
  - vendor data kept in-cloud;
  - only counts, distributions and SHA-256 digests exported.

**38 — File budget.**
- X997 uses **47 of 50** project files:
  - 33 base files: main, harness, score and SEC modules, plus the 20-file data-v1 SEC table;
  - 14 for the new packed table: 13 parts plus a loader, about 790 KB.
- The identity value-check table was limited to periods ending by 2012-12-31 to fit.
- Production Data v2 should merge the data-v1 SEC table and the new table into one compact v2 table (estimated 25–28 files in total). That would remove the 47–50 fragility.
- Object Store reads would be an alternative but were not tested. Exporting from it is blocked.

**39 — Engineering effort, if approved:** about 3–4 sessions:
- one consolidated v2 reference table plus a freeze manifest;
- the X993-v2 score export host (M2 + repaired universe + identity rows + restatement guard);
- tests and canaries;
- P7-CP3R-equivalent mechanics;
- a power study on v2 tables;
- then the H022 canary, null and the one real evaluation.

**40 — QuantConnect runs, if approved:** about 12–14:
- 1–2 v2 export and verification runs;
- 1 canary;
- 5 null batches (5,000 worlds);
- 1 real evaluation;
- reserves.

**41 — Cost:** $0 beyond the existing $24 / month. No data purchase, no upgrade.

## 42–49. Confirmations

| # | Confirmation |
|---|---|
| 42 | **Score v1 unchanged:** the frozen `qr_p7_score` (hash-pinned), features, weights, thresholds, H1–H7, mechanics |
| 43 | **M2 unchanged:** max(first seen, SEC original filing + 1 day). Only its SEC filing reference was completed with pre-XBRL filings from EDGAR submissions |
| 44 | **No future return of any kind computed.** Power figures use synthetic returns only |
| 45 | **No IC / H022 statistic computed** on real data |
| 46 | **No portfolio:** 0 orders in E997-01/02/03 |
| 47 | **2018–2021 untouched.** Runs end on 2017-12-31; SEC filings only up to 2017-12-31 |
| 48 | **Holdout untouched** |
| 49 | **Nothing purchased, no upgrade** |

All earlier records are preserved:
- P7-CP3R, P7-CP4, P7-CP5a–d;
- E993-02 and E996-01/02/03;
- the old null worlds and c_IC (data v1 only, never used on a new panel).

The universe threshold ($2B) and all filters are unchanged.

**Records:**
- experiments E997-01, E997-02, E997-03 (H022-family infrastructure experiments: 21);
- `research/phase7/cp5e/` (target population, pre-registration, identity extension, fate and shares, power for a 2013 start, reference builder, `x997_analysis.py` / `x997_summary.json`);
- host `strategies/X997_universe_repair/`;
- tests `tests/test_p7_cp5e_repair.py`.

## 50. Final recommendation

```
GO — universe can be repaired PIT-safely and Data v2 design can proceed
```

**Proposed Data Infrastructure v2** (nothing built or frozen):

| Layer | Proposed v2 rule |
|---|---|
| **Universe** | Unchanged conceptual rules: US common, NYSE/Nasdaq, PIT market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M. Market cap = QuantConnect's if > 0, else the D111 SEC market cap (cover-page count usable from filing + 1, ≤ 135 days old, × splits after the cover date, × raw price; single unambiguous count only), else ineligible. The data-v1 SEC correction layer (securities without vendor fundamentals) is kept |
| **Fundamental timing** | M2: a report (security, period) is usable from max(first seen in the historical stream, SEC original 10-Q / 10-K filing + 1 day). The original filing comes from EDGAR submissions (pre-XBRL included), with period ends matched within 6 days; a report with no matched filing is never used. The first-seen value is never rewritten; a revision enters from its own first-seen day. No vendor file date, no +90-day estimate rule |
| **SEC identity** | Identity-v2 dated rows, plus the verified extension rows (SAFE and bounded only; `identity_extension.json` rule), each used only while the security's feed presence is continuous since the row start. REJECT and ambiguous rows never used |
| **Restatement guard** | New (P7-CP5d section 11): block any report whose first-seen quarterly revenue or total assets equals only a later SEC value that was not yet filed on the day seen (≈ 0.26% of reports). This is the v1 restatement-guard analogue |
| **Score v1** | Unchanged (hash-pinned), on the v2 inputs |
| **Research window** | 2011-01 → 2017-12 (83 decisions), as frozen. Identity repair makes 2011–2012 usable. The 2013 alternative is quantified above and not recommended |
| **Regenerate** | v2 score tables, mechanics statistics (P7-CP3R equivalent), power study, H022 canary, 5,000 null worlds, new c_IC, then the one real evaluation. The old c_IC is never used |
| **Known residuals** | 6.3% of data-v1 stock-months stay unrecovered (survivor gap +0.8 points overall, +2.7 in 2011); ≈ 1.4% upward classification risk from multi-class cover counts; identity continuity evidence dated after the reports it maps; 47-of-50 file budget until the tables are consolidated |

## 51. Exact next owner decision

1. **Approve or amend the Data v2 architecture** in section 50, including:
   - the restatement guard;
   - accepting the residuals listed.
2. **Confirm the research window:** 2011-01 → 2017-12, as frozen (recommended), or the quantified 2013 alternative.
3. **Authorise** building and freezing Data v2 (consolidated tables, v2 export host, canaries, P7-CP3R-equivalent mechanics), returning at a v2 freeze checkpoint before any H022 null or real run.

Until then: STOP. No Data v2 freeze, no P7-CP3R rerun, no H022, no null worlds, no new threshold, no returns, no portfolio, no 2018–2021, no Holdout.
