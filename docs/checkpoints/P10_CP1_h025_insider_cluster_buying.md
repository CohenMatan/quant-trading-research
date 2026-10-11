# P10-CP1 — H025 Insider Cluster Buying

**Date:** 2026-10-11. **Decisions:** D204 (owner approval; frozen pre-registration), D205 (this checkpoint).
**Status:** STOPPED, awaiting the owner.

## Short answer

H025 asked whether a large US stock beats SPY over the next 20 trading sessions after this event:

- two or more of its directors or officers buy the stock in the open market with their own money;
- each buys at least $25K, and together at least $100K;
- the purchases become public on EDGAR within ten calendar days.

**It does not.**

| Measure | Result | Gate |
|---|---|---|
| Events (2011–2017, ≥ $2B universe) | **605** | G5 ✔ |
| t_EVENT (monthly series, Newey-West lag 2) | **−0.93** vs c_EVENT **2.47** | G1 ✘ |
| Mean 20-session excess vs SPY | **+0.07%** (needs ≥ +2.0%) | G2 ✘ |
| Median excess / win rate | +0.02% / 50.4% | G3 ✔ (barely) |
| 2011–2014 / 2015–2017 mean | −0.69% / +0.75%; 2 of 7 years positive | G4 ✘ |
| Share of null worlds with t ≥ real | **93%** (p = 0.93) | — |
| Matched random-stock control (null worlds) | mean +0.30%, median +0.15%, win 51.2% | — |

```
H025 REJECTED — NO ROBUST INSIDER-CLUSTER EDGE
```

The insider-cluster stocks did no better than randomly chosen stocks of the same sector and size on the same dates, and slightly worse on the monthly statistic. No diagnostic shows a robust pattern. Nothing is frozen, and H025 is preserved exactly as tested.

## What was done (run order of D204, item 34)

| Step | Result |
|---|---|
| 1 SEC Form 4 parser | `src/qresearch/h025_form4.py`; 33 synthetic tests (rules, timing, clusters, cooldown, leakage, brute-force equivalence) |
| 2 Event ledger | SEC data sets 2010Q4–2017Q4 + 53,567 EDGAR headers; `research/phase10/ledger/` |
| 3 Freeze rules | `research/phase10/H025_spec.md`, pinned in `qresearch.p10h025` before any count |
| 4 No-return audit | E027-01 (S027 audit mode): eligibility and identity only |
| 5 Minimum sample | 605 events, all 7 years ≥ 59 → **PASS** |
| 6 Deterministic rebuild | Offline independent rebuild identical; brute-force triggers 0 mismatches; E027-02 identical to E027-01 |
| 7 Pin ledger hash | EVENT_LEDGER_SHA256 `23d3a74a…` |
| 8 Canary | E027-03, 17/17 (synthetic returns only) |
| 9–10 Null | E027-04 (5,000 worlds) + identical rerun E027-05 |
| 11 Pin c_EVENT | 2.4667, commit 49b61b6, merged in [PR #84](https://github.com/CohenMatan/quant-trading-research/pull/84) before the real run |
| 12 Real evaluation | E027-06, once |
| 13–14 Gates, diagnostics | Pre-committed `research/phase10/cp1/P10_CP1_result.py` |
| 15 STOP | This checkpoint |

Runs (all QuantConnect default build LEAN 18178, digest verified, 0 orders, nothing after 2017-12-29):

| Run | Commit | Backtest |
|---|---|---|
| E027-01 audit | 15461f8 | 8e9ec9d6… |
| E027-02 audit repeat | a3ddf48 | cc5ee447… |
| E027-03 canary | dd42328 | 3909c6c0… |
| E027-04 null | 7a20dbf | 7a54a964… |
| E027-05 null rerun | 9e65f82 | 1a0ae320… |
| E027-06 real | fa3ec07 (merge of PR #84) | 2308a4dc… |

## The 67 required items

1. **Owner decision ID:** D204 (`docs/owner/2026-10-11_p10cp1_h025_insider_cluster.md`, verbatim).
2. **H022:** closed as REJECTED (E024-07), unchanged and not re-run.
3. **H023:** closed as NO ROBUST SCORE V2 CANDIDATE (E025-08), unchanged.
4. **H024:** closed as NO ROBUST H024 FEATURE MODEL (E026-08), unchanged. No score or feature was used in H025.
5. **SEC source:** the official SEC *Insider Transactions Data Sets*: quarterly structured extracts of every Form 3/4/5 XML filing (SUBMISSION, REPORTINGOWNER and NONDERIV_TRANS tables), 29 quarters 2010Q4–2017Q4. Also each filing's EDGAR header `<accession>.hdr.sgml`, whose ACCEPTANCE-DATETIME is in US Eastern time and equals the "Accepted" time on the EDGAR index page. Public and free; nothing purchased.
6. **SEC retrieval:** `research/phase10/h025_ledger.py --fetch` with the project SEC client. The contact address is read at run time only. ≤ 8 requests per second. Cached in `data/sec_cache` (outside Git; re-acquirable). 53,567 headers fetched, 0 missing.
7. **Timing rule:** information arrives at the SEC acceptance timestamp. A filing is usable only if:
   - its header exists, with a time of day;
   - the header form is 4 and its filing date matches;
   - the acceptance date is within [filing date − 7 days, filing date];
   - every transaction date is ≤ the acceptance date.

   There is no fallback. 53,528 of 53,567 filings are usable; 17 are excluded for acceptance outside the filing date and 22 for invalid transaction dates. Entry is the first regular-session open strictly after acceptance: that day's open if the acceptance is before 09:30 ET on a session, else the next session.
8. **Form 4 parsing:** one row per non-derivative code-P line. A qualifying filing's value is the sum of shares × price over its qualifying lines. Duplicate accessions across quarters must be identical (checked).
9. **Transaction codes:** only P. Every other code (awards, exercises, conversions, gifts, tax withholding, sales, J) and every derivative line is excluded by construction. Acquired/disposed code must be A (806 P lines excluded). Original Form 4 only; 4/A and Form 5 excluded (14,202 lines).
10. **Insider roles:** the relationship must contain Director or Officer. Ten-percent-owner-only or Other owners are excluded (31,447 lines). A Director/Officer who is also a 10% owner counts. Distinct insiders are counted by reporting-owner CIK. Joint (multi-owner) filings are excluded because the purchase cannot be attributed to one insider (48,827 lines).
11. **Ownership:** direct only. 43,079 indirect P lines are counted only.
12. **Per-insider threshold:** at least $25,000 in the window. Not optimised.
13. **Cluster threshold:** at least $100,000 summed over the qualifying insiders. Not optimised.
14. **Window:** 10 calendar days by acceptance date ([D − 9, D]).
15. **Minimum insiders:** 2.
16. **Online trigger:** the acceptance that first makes the criteria true. It is never backdated, and later purchases are descriptive only. An independent brute-force implementation reproduces every trigger, entry and insider set (0 mismatches).
17. **Cooldown:** 20 trading sessions per issuer, applied on the pre-universe SEC ledger. 0 violations in the canary.
18. **Universe:** the latest frozen Data v2 monthly review strictly before the trigger date. Filters: US common stock, NYSE/Nasdaq, PIT market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M.
19. **Identity:** the issuer CIK must equal the Data v2 verified identity CIK (identity v2 or verified extension, recorded live at the review) of an eligible security.
    - Several share classes: the one with the highest ADV20 (2 events).
    - Unresolved (an unverified eligible security carries the as-filed symbol): excluded, 29 events.
    - No modern ticker or name matching.
20. **Development period:** triggers 2011-02-01 → exits ≤ 2017-12-29. 2011–2017 only.
21. **Form 4 filings inspected:** 1,369,349 Form 4 submissions in 1,543,377 Form 3/4/5 submissions; 262,426 code-P non-derivative lines.
22. **Qualifying purchases:** 114,711 lines in 74,106 filings of 6,030 issuers.
23. **Pre-universe clusters:** 3,721 in all. 3,587 in the window (2,008 issuers); 90 before the window; 44 with exit after 2017.
24. **Post-universe events:** **605** (368 issuers).
25. **Events by year:** 2011 93 · 2012 59 · 2013 61 · 2014 71 · 2015 103 · 2016 108 · 2017 110.
26. **Insiders per event:** 2 → 592; 3 → 11; 4 → 2.
27. **Cluster value:** p5 $121K, p25 $187K, median $350K, p75 $805K, p95 $2.43M. Buckets: $100K–250K 213; $250K–1M 262; > $1M 130.
28. **Identity exclusions:**
    - 29 unresolved (in window);
    - 2,953 issuers not in the eligible universe at the review;
    - 2 mapped by the multi-class rule;
    - identity source v2 603, verified extension 2.
29. **Timing / data exclusions:**
    - 0 missing headers;
    - 17 acceptance outside the filing date;
    - 22 invalid transaction dates;
    - 1,653 missing / zero prices and 18 missing shares (lines);
    - 7,683 non-common titles;
    - all 605 events evaluable (no unverified split, no missing bar).
30. **Sample adequacy:** **PASS** (605 ≥ 100; 7 years ≥ 10).
31. **Event-ledger hash:** EVENT_LEDGER_SHA256 `23d3a74a24ee1ac9273db5375f99068db239c9ec4cfc212cbea0a759317864c7`.
    - Ledger: `research/phase10/ledger/h025_event_ledger.csv.gz`, no return column.
    - In-host part: `7adbb0b9…`.
    - SEC payload: `92632242…`.
32. **Determinism:** PASS.
    - Offline independent rebuild identical.
    - Brute force 0 mismatches.
    - E027-02 rows, counts and in-host digest identical to E027-01.
    - Null rerun bit-identical.
33. **Canary:** E027-03, **17/17** (`research/phase10/cp1/P10_CP1_canary.json`).
    - Ledger / review / identity / calendar / cooldown / entry / exit: 0 violations.
    - SPY total return and corporate actions vs fresh histories: ≤ 4.4e-16.
    - Synthetic next-open timing exact.
    - Planted +4% passes all gates; 0 effect fails.
    - No real response computed.
    - Note: in the truncated class, 11 of 25 status labels differ only by name ('no_bar' vs S024's 'no_bar_after_t'); values identical.
34. **Response construction:** the frozen Data v2 panel: RAW open/close with the verified split × dividend multiplier (`qr_p7_pred.response` conventions; equality checked). SPY uses its RAW open/close with its own split × dividend multiplier (44 dividends).
35. **Primary response:** stock TSR from the entry-session open to the 20th-session close, minus SPY TSR over the same rows (SPY to the planned exit if the stock stops trading).
36. **Null matching:**
    - Pool: eligible securities at the event's review with verified identity and a finite response.
    - Excluded: the issuer (and its CIK), and any security with an H025 cluster entry within 19 sessions.
    - Matching levels: L1 same FF12 sector and market-cap quintile (604 events); L2 nearest quintile, same sector (1); L3 / L4 not used.
    - Median pool size 22; no empty pool.
37. **Null worlds:** 5,000 (seeds 1–5,000).
38. **Null determinism:** E027-05 bit-identical to E027-04; same response panel `bc4d17c8…`.
39. **Null distribution of t:** mean 0.43, sd 0.90, p50 0.44, p95 1.89, p99 2.46, max 3.59.
40. **c_EVENT:** **2.4667** (50th largest of 5,000; above the 2.326 floor). Null result `c1d55bcd…`.
41. **Real events:** 605 evaluable, 0 not evaluable.
42. **Mean 20-session SPY-relative return:** **+0.075%**.
43. **Median excess:** +0.023%.
44. **Win rate:** 50.41%.
45. **Monthly mean event excess:** **−0.42%** (77 months, NW SE 0.45%). The event-weighted mean is positive only because the heavy-event months of 2016–2017 were positive; the average month was negative.
46. **t_EVENT:** **−0.93**.
47. **Null percentile:** 93.2% of null worlds have t ≥ −0.93; p = 0.93.
48. **G1:** FAIL (t −0.93 < 2.47).
49. **G2:** FAIL (+0.07% < +2.0%).
50. **G3:** PASS (median +0.02% > 0; win 50.4% > 50%), by a negligible margin.
51. **G4:** FAIL (2011–2014 −0.69%; only 2 of 7 years positive).
52. **G5:** PASS.
53. **By year (mean, n):** 2011 −0.77% (93) · 2012 −1.02% (59) · 2013 −0.12% (61) · 2014 −0.78% (71) · 2015 −0.05% (103) · 2016 +1.55% (108) · 2017 +0.71% (110).
54. **Halves:** 2011–2014 **−0.69%**; 2015–2017 **+0.75%**. The sign flips between halves.
55. **Other horizons (non-gating; mean, NW t):** 5 sessions +0.24% (t −0.06); 10 sessions −0.11% (t −1.49); 40 sessions −1.13% (t −1.32; n 586); 60 sessions −0.74% (t −0.41; n 585). Raw stock TSR +1.38% (win 59%: the market rose). Sector-relative −0.16% (t −1.07).
56. **Cluster size:** 2 insiders +0.09% (n 592, t −0.88); 3+ insiders −0.66% (n 13). Qualifying filings: 2 → +0.01% (n 558); 3 → +1.10% (n 41, t 1.36); 4+ → −1.13% (n 6).
57. **Dollar size:**
    - $100K–250K: −0.22% (n 213, t 0.15).
    - $250K–1M: +0.23% (n 262, t −0.75).
    - > $1M: +0.24%, median −0.36% (n 130, t −1.23).
58. **CEO/CFO:**
    - CEO/CFO involved: +0.07% (n 284, t −0.10).
    - Not involved: +0.08% (n 321, t −1.18).
    - Director-only clusters: −0.09%, median −0.53%, win 46% (n 204, t −1.82).
    - With an officer: +0.16% (n 401, t −0.54).
    - Filing delay ≤ 2 days −0.18% (n 434); 3–5 days +0.47% (n 163); > 5 days +6.1% (n 8: too few to mean anything).
59. **Single-insider control (one insider ≥ $100K, no cluster; non-gating):**
    - n 1,605; mean +0.38%, median +0.56%, win 54.2%; NW t 0.64.
    - It was no worse than the clusters, so a second insider adds nothing here.
60. **No definition changed after results:** spec, code, ledger and thresholds are all pinned before the run (hash tests pass). No subgroup is promoted.
61. **No portfolio evaluated:** no CAGR, wealth, Sharpe, drawdown, sizing, concurrency or turnover.
62. **2018–2021 not accessed for H025:** no SEC filing after 2017Q4 and no price after 2017-12-29.
63. **Disclosure:** 2018–2021 is an H025-SPECIFIC OOS VALIDATION period, NOT a programme-wide pristine holdout. Earlier unrelated hypotheses used parts of it (H005 Validation; Phase 2 H014/H016/H017 development).
64. **Holdout:** 2022-01-01 → 2026-08-31 untouched.
65. **Nothing purchased:** official SEC data only. QuantConnect is unchanged ($24/month).
66. **Final result:** **H025 REJECTED — NO ROBUST INSIDER-CLUSTER EDGE.**
67. **Exact next owner decision:** whether to:
    - (a) **close H025 / Phase 10 as Rejected** (recommended; H025 preserved exactly as tested, never re-run or re-defined); or
    - (b) name a new, materially different research direction. Any altered insider definition (5-day window, 3 insiders, other thresholds, indirect ownership, 10% owners, other holds) would be H026+ and need its own owner decision, and the clear null here is evidence against such variants.

    No 2018–2021 validation is warranted, because H025 did not pass development.

## Interpretation (plain language)

- In 2011–2017, among large US companies, insider-buying clusters were rare (about 85 a year) and mostly involved exactly two insiders spending a few hundred thousand dollars.
- After such a cluster became public, the stock did essentially what a random stock of the same sector and size did over the next month.
- The positive raw return (+1.4%) came from a rising market, not from the insiders.
- The literature's insider effect is concentrated in small, thinly traded stocks. This test confirms it is not detectable in the ≥ $2B universe this programme can trade.

## Files

- Spec / hypothesis: `research/phase10/H025_spec.md`, `research/hypotheses/H025.md`.
- Pins: `src/qresearch/p10h025.py`.
- Parser / ledger: `src/qresearch/h025_form4.py`, `research/phase10/h025_ledger.py`, `research/phase10/ledger/`.
- In-host module: `src/qresearch/lean/qr_h025.py`, `src/qresearch/lean/qr_h025_events*.py`.
- Host: `strategies/S027_h025_insider/main.py`.
- Analysis: `research/phase10/cp1/P10_CP1_{configs,audit,canary,null,result}.py` and their JSON outputs.
- Tests: `tests/test_p10_h025*.py`.

## Totals

- Programme: 25 hypotheses (H001–H025).
- This phase: 1 hypothesis (H025); 1 strategy host (S027); 6 experiments (E027-01..06; 5 infrastructure, 1 research).
- All runs are logged in `experiments/INDEX.csv`.
