# P7-CP1 — Multi-Factor Conviction Score Data & Fidelity Readiness Audit

- **Date:** 2026-10-06.
- **Owner direction:** `docs/owner/2026-10-06_phase7_conviction_score_data_audit.md` (D165).
- **Decisions:** D165–D168.
- **Scope:** data availability, data quality, point-in-time (PIT) fidelity and implementation feasibility **only**.
- **Not done anywhere in this checkpoint:**
  - no future return of any kind, and no test of whether any factor predicts returns;
  - no score, weight, threshold, tier, size or maximum position count;
  - no portfolio backtest;
  - no data from 2018-01-01 onward requested; the Holdout is locked; nothing was purchased.

**Evidence:**

| Kind | Files |
|---|---|
| Runs (all infrastructure, no orders) | E991-01/02 (X991), E992-01/02/03 (X992) |
| Extracts | `research/phase7/P7_audit_E991.json`, `research/phase7/P7_audit_E992.json` |
| SEC check | `research/phase7/P7_sec_sample_check.json` |
| Code | `src/qresearch/lean/qr_p7.py`, `strategies/X991_*`, `strategies/X992_*` |
| Tests | `tests/test_p7_features.py`, `test_p7_canaries.py`, `test_p7_hosts.py` |

The two audits cover 2010-01-04 → 2017-12-31 and use the frozen data-v1 universe:
- market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M, NYSE/Nasdaq;
- the SEC correction layer;
- a history-only warm-up from 2008-07-01.

## Summary for the owner

**Recommendation: READY TO DESIGN SCORE**, subject to the decisions in item 40. This means designing the score (P7-CP2), not running it.

**What we have, verified point in time:**

1. **Technical data.** Daily prices, splits and dividends for every eligible stock 2010–2017. Ten candidate technical features were recomputed independently from fresh history ending at the decision date: **380 / 380 samples agree** (worst difference 7 × 10⁻¹⁴). 0 eligible stock-days without a current price bar.
2. **Fundamental data.** Seven approved fields: revenue, gross profit, net income and operating cash flow as true trailing-twelve-month values; total assets and equity; point-in-time market cap.
   - All leakage checks are 0.
   - In an independent sample checked against the SEC's own filing history, **0 of 268** fundamental snapshots became usable before the company's 10-Q/10-K was public (264 vendor file dates equal the SEC date exactly).
   - For non-financial companies the full core set is available for **77–89%** of eligible stock-months, depending on the year.
3. **Sector data.** The SEC industry code (SIC), as filed at the time, gives a point-in-time sector (Fama-French 12 groups). Coverage is **69% in 2010** and **≥ 92% from 2011**. Morningstar's sector codes are **current-status**: they never changed for any of 1,938 securities in 8 years, so they are unsafe historically.
4. **Market regime data.** Breadth can be computed with the correct point-in-time denominator: delisted companies are counted until they leave. Using survivors only would have been off by up to 3.2 points. SPY is available from 1998 and VIX from 2005.

**Defects found and handled:**

- **(a) Re-used security ids (D167).** A few QuantConnect ids carry two different companies' histories joined across a long gap (e.g. Gardner Denver 2013 / the new Gardner Denver 2017). Repaired for Phase 7 by a "security-life" rule. Exposure: 20 eligible stock-months out of about 102,000.
- **(b) Corporate events.** At a handful of corporate events (spin-off plus reverse split), the price adjustment is unreliable: 11 unverified splits, and 72 large distributions such as spin-offs. These need a data-uncertainty rule in the score.
- **(c) Dividend-feed precision.** The dividend feed rounds amounts to the cent, and it misses 2 Chubb dividends (2016).
- **(d) Blank company id.** Morningstar's company id is blank for many later-delisted companies, so it cannot be used to detect duplicate share classes.

None of these defects changes an earlier result, and no earlier result was re-run.

**Common development window, fixed mechanically by data availability: 2011-01 → 2017-12.**
- Sector classification is reliable only from 2011.
- Year-over-year fundamental change needs 12 months of point-in-time history, so it also starts in 2011.
- If the score uses neither, the window can start in 2010-01.

## 1. Formal Phase-6 closure

- **H021-A** is **Rejected / Did Not Qualify**, preserved exactly as tested (P6-CP2, D164).
- **Phase 6 is CLOSED** (owner, D165).
- Phase 7 does not use, revisit or rescue H021-A. No sector-momentum signal or return from Phase 6 informs this audit.

## 2. Intended Phase-7 architecture (concept only)

**Individual stock conviction** = technical quality + fundamental quality + sector context.

**Market regime** = total portfolio exposure. It is never added as points to every stock.

**Intended mechanics (no numbers yet):**
- a difficult, high entry threshold and a lower exit threshold (hysteresis);
- a replacement buffer;
- few, long-lived positions;
- cash allowed when candidates are scarce.

This checkpoint only establishes which inputs each layer can use safely.

## 3. Complete data inventory

**Legend:**
- **Audit:** ✔ = passed a fidelity audit (this checkpoint, or the one cited).
- **Revisions:** "no" = values as originally reported. Restated values are blocked or delayed by the PIT layer.

| Family | Field / series | Source | Raw / derived | First reliable | Last dev. date | PIT timestamp | Frequency | Expected staleness | Missingness (eligible) | History rewritten? | Audit | Safe for Phase 7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Price** | RAW daily OHLCV | QuantConnect (AlgoSeek) | raw | 1998 (QC), panel 2007-01 | 2017-12-29 | bar close of session t | daily | ≤ 5 sessions (0 stale eligible days) | 0 missing on eligible days | no | ✔ X992 | **A** |
| Price | Split-adjusted chart (C, H, L, V) | RAW × split feed (SCALED_RAW-verified) | derived | 2007 panel | 2017-12-29 | ratios inside windows ending at t | daily | — | 11 unverified splits / 540 | factors dated after t cancel | ✔ 380/380 | **A** (B at corporate events) |
| Price | Total-return close (P) | RAW × split × dividend feed | derived | 2007 panel | 2017-12-29 | as above | daily | — | — | as above | ✔ (ADJUSTED cross-check) | **A** |
| Price | ADJUSTED (QC factor files) | QuantConnect | derived | 1998 | — | uses factors up to today (ratios only) | daily | — | — | no | cross-check only | B (reference only) |
| **Corporate actions** | Split events | QuantConnect split feed | raw | 1998 | 2017 | event day | event | — | 527 / 540 aligned with SCALED_RAW; 11 unverified; 2 outside | no | ✔ | **A** (11 flagged) |
| Corporate actions | Distributions | QuantConnect dividend feed | raw | 1998 | 2017 | ex-day | event | — | amounts rounded to the cent (D162); 2 missing (CB 2016) | no | ✔ (4.39 M steps) | **A** (caveat) |
| **Market cap / liquidity** | Market cap | Morningstar (vendor, PIT; D107) / SEC reconstruction (repaired) | raw / derived | 2009-10 | 2017-12 | daily, previous close | daily | — | universe-defining | no | ✔ (D107, D111, X991) | **A** |
| Market cap / liquidity | ADV20 | vendor dollar volume (harness) | derived | 2009-12 | 2017-12 | previous close | daily | — | universe-defining | no | ✔ | **A** |
| **Fundamentals** | Approved set: revenue, gross profit, net income, OCF (True TTM); total assets, equity (snapshots) | Morningstar + SEC table (repaired names) through the PIT store | derived | 2010-01 (warm-up 2008-07) | 2017-12 | filing date + 1 day (+90 days if estimated) | quarterly | median 91–93 days since period end; p95 123–128 | see item 9 | blocked / quarantined / delayed | ✔ (E975, E976, X991, SEC sample) | **A** |
| Fundamentals | Operating income, FCF, total debt, vendor '*_ttm' as twelve months | Morningstar | raw | — | — | — | — | — | — | — | failed SEC validation / never validated | **C** |
| Fundamentals | Share counts, per-share values, vendor ratios, accession numbers, fiscal-year end | Morningstar | raw | — | — | — | — | — | — | restated to today | unsafe (D107) | **C** |
| **Sector / industry** | SEC SIC at filing → FF12 | SEC XBRL RSS (per filing) | raw | 2011 (2010: 69% coverage) | 2017 | filing date + 1 day | per filing | until the next filing | 2010 30.6%, 2011 7.5%, 2012+ ≤ 4.7% unclassified | no (dated rows) | ✔ (D113, X991) | **A from 2011**, B in 2010 |
| Sector / industry | Morningstar sector / industry codes | Morningstar | raw | — | — | current status | — | — | — | **yes** (0 changes in 8 years) | ✔ (shown unsafe) | **C** |
| Sector / industry | Select Sector SPDR ETFs | QuantConnect | raw | 1998-12-22 | 2017-12-29 | session close | daily | — | 0 | no | ✔ (P6) | B (no PIT stock→ETF map) |
| **Market / breadth** | SPY | QuantConnect | raw | 1998 | 2017-12-29 | session close | daily | — | 0 | no | ✔ | **A** |
| Market / breadth | VIX (index and CBOE) | QuantConnect | raw | 2005-01 | 2017-12-29 | session close | daily | — | 3,272 bars 2005–2017 | no | availability only (E992-01) | **A** (not fidelity-audited) |
| Market / breadth | Breadth: % above SMA50 / SMA200, new highs / new lows | derived from the PIT universe and panel | derived | 2010-01 | 2017-12 | close of t, PIT denominator | daily | — | 7–30 insufficient-history names a day | no | ✔ (survivorship test) | **A** |
| **Delistings** | Last bar; feed exit; LEAN delisting events | QuantConnect | raw | 2008 | 2017 | event day | event | — | events only for subscribed securities | no | ✔ (0 eligible after last bar) | **A** |
| **Calendar** | NYSE sessions | SPY bars | raw | 1993 | 2017-12-29 | — | daily | — | 0 | no | ✔ | **A** |
| **Events** | SEC 8-K earnings events (Event Data v1) | SEC EDGAR | raw | 2010 | 2021 | acceptance time (ET) | event | — | 93.9% coverage | no | ✔ (D122–D124) | **A** (2010–2017 part) |

## 4. Technical-data availability

**Panel:** 1,996 securities eligible on at least one selection day 2010–2017, over 2,769 sessions (2007-01-03 → 2017-12-29).

**Eligibility vs bars:** 2,146,562 eligible stock-days, with:
- 0 without a bar at the decision session;
- 0 after the last bar;
- 0 stale (more than 5 sessions without a bar).

**Candidate technical features** (eligible stock-months with a value):

| Year | Month-ends | Eligible | All 10 features | SMA200 | 52-week high/low | 12-1 momentum | 6-1 momentum | SMA50 | ATR14 / vol60 / ADV20 |
|---|---|---|---|---|---|---|---|---|---|
| 2010 | 12 | 9,698 | 98.9% | 99.2% | 98.9% | 98.9% | 99.5% | 99.9% | ≈ 100% |
| 2011 | 11 | 10,169 | 98.4% | 98.7% | 98.4% | 98.4% | 99.2% | 99.7% | ≈ 100% |
| 2012 | 13 | 12,077 | 98.1% | 98.6% | 98.1% | 98.1% | 99.2% | 99.9% | ≈ 100% |
| 2013 | 12 | 12,856 | 97.7% | 98.3% | 97.7% | 97.7% | 99.0% | 99.7% | ≈ 100% |
| 2014 | 12 | 14,373 | 96.7% | 97.4% | 96.8% | 96.7% | 98.5% | 99.6% | ≈ 100% |
| 2015 | 12 | 14,684 | 97.3% | 98.1% | 97.4% | 97.3% | 98.9% | 99.7% | ≈ 100% |
| 2016 | 11 | 12,901 | 98.4% | 98.9% | 98.5% | 98.4% | 99.5% | 99.9% | ≈ 100% |
| 2017 | 12 | 15,309 | 97.7% | 98.1% | 97.7% | 97.7% | 98.8% | 99.7% | ≈ 100% |

- **The gaps are young stocks** (fewer than 252 own bars: 1.1–3.2% of eligible stock-months, item 21).
- **Month-end convention.** A snapshot is the first universe selection of each calendar month. QuantConnect stamps a selection with the calendar day AFTER the session it reflects. The snapshot session t is therefore the last session of the month, or the first session of the next month when a weekend or holiday falls at the boundary. That is 11–13 snapshots per year.
  - Each snapshot is point-in-time coherent.
  - P7-CP2 should define decision dates from the session calendar (the last session of each month), not from the selection stamp.

**Which series serves which purpose** (recommended; to be confirmed in P7-CP2):

| Purpose | Series | Why |
|---|---|---|
| Technical chart indicators using highs/lows (52-week high/low, ATR, structure) | **Split-adjusted chart series (C, H, L)** | Highs and lows exist only as split-adjusted bars. It is not dividend-adjusted, so a large distribution (spin-off) appears as a price drop: flag such windows (item 32) |
| Trend and moving averages | **Total-return closes (P)**, or the chart series with the same flag | A spin-off or special dividend must not look like a breakdown. Choosing one series per feature is an explicit P7-CP2 decision; the two are never mixed inside one feature |
| Momentum (12-1, 6-1, relative strength) | **Total-return closes (P)** | The economic return including distributions |
| Volatility | **Total-return log returns** | Avoids artificial ex-dividend moves |
| Total-return measurement (later, portfolio stage) | **P** (RAW × split × dividend feed) | Verified against ADJUSTED within cent rounding |
| Actual execution | **RAW open of T+1** (harness) | The real traded price, never adjusted |

## 5. Technical-data fidelity results

**Primary vs independent implementation** (`qr_p7.features_at` vs `features_slow`): a vectorised version against a loop version, with no shared code.

| Check | Result |
|---|---|
| Synthetic (tests) | Exact to 10⁻¹²: gaps, splits, distributions, IPOs, the security-life rule |
| Real data | **380 / 380 (security, month-end) pairs agree**, worst relative difference 7.2 × 10⁻¹⁴. The independent path uses a **fresh RAW history request ending at t**, with split and dividend events up to t applied directly, without SCALED_RAW verification or multiplier arrays. 265 of the 380 windows contain a corporate action. Last-bar dates are identical in 380 / 380 |
| Point in time | Changing anything after t, truncating the data at t, or adding a corporate-action factor dated after t leaves every feature at t unchanged (exact; tests) |
| Breadth states | The calendar-state implementation equals the primary features on every row (test) |

**No discrepancy was found.** The features verified were: close / SMA50, close / SMA200, SMA50 / SMA200, close / 252-day high and low, 12-1 and 6-1 total-return momentum, ATR14 / close, 60-day volatility and 20-day average dollar volume.

## 6. Fundamental field inventory

Every field is read only through the PIT store, which enforces the whitelist and fails loudly on anything else.

| Field | Meaning | Flow / stock | Basis | Investors knew it | How availability is set | Staleness limit | Amendments | Status |
|---|---|---|---|---|---|---|---|---|
| `revenue_ttm4q` | total revenue, last 4 quarters | flow | true TTM (sum of 4 consecutive visible quarters; Q4 validated against the fiscal year within 1%) | when the newest quarter was filed | filing date + 1 day (+90 days after period end if the vendor date is estimated) | newest quarter ≤ 200 days old | replace their quarter only from their own availability | **A** (SEC-validated 95.1% within 0.5%) |
| `gross_profit_ttm4q` | gross profit | flow | true TTM | same | same | same | same | **A** for coverage where reported (not reported by most financials; 81–88% of non-financials) |
| `net_income_ttm4q` | net income | flow | true TTM | same | same | same | same | **A** (96.5%) |
| `operating_cash_flow_ttm4q` | operating cash flow | flow | true TTM | same | same | same | same | **A** (97.4%) |
| `total_assets` | total assets | balance-sheet snapshot | latest visible report | same | same | report ≤ 200 days old | same | **A** |
| `stockholders_equity` | shareholders' equity | snapshot | latest visible report | same | same | same | same | **A** (can be negative) |
| `market_cap` | market capitalisation | daily | PIT vendor value; SEC cover shares × price for repaired names | previous close | daily | — (cover count ≤ 135 days for repaired names) | — | **A** |
| `operating_income_ttm4q`, `free_cash_flow_ttm4q` | — | flow | true TTM | — | — | — | — | **C** (48% / 74% agreement with the SEC) |
| `total_debt` | — | snapshot | — | — | — | — | — | **C** (never validated) |
| vendor `*_ttm` | latest fiscal year (not a rolling 12 months) | flow | fiscal year | — | — | — | — | **C** as a 12-month value (used only by the Q4 gate) |
| quarterly `*_q` | single-quarter values | flow | quarter | — | — | — | — | **B** (components of TTM; not validated alone) |
| share counts, EPS, book value per share, vendor ratios, accession numbers, fiscal-year end, Morningstar sector | — | — | — | — | — | — | — | **C**: restated to today or current-status (D107, item 12) |

**Derived inputs the approved fields allow** (availability in item 9, overlap in item 31):

| Group | Inputs |
|---|---|
| Profitability | GP / assets, NI / assets, OCF / assets, NI / equity (equity > 0) |
| Earnings quality | accruals (NI − OCF) / assets |
| Balance sheet | equity / assets |
| Valuation | NI, OCF, revenue or GP ÷ market cap; equity ÷ market cap (B/M) |
| Change | year-over-year revenue / GP / NI / OCF growth; change in NI / assets |

**Not available:**
- debt, current assets/liabilities, interest coverage, capex and share issuance (share counts are restated);
- analyst estimates and news.

## 7. Fundamental point-in-time chronology

**For decision date t** (data through the close of session t; orders at the open of the next session):

1. **Observation.** Every vendor report is observed on the day QuantConnect delivers it. This happens for every company with fundamentals, every day, from 2008-07-01. SEC-repaired companies are fed from the SEC table, with values as first filed.
2. **Availability.** A report becomes **usable on its filing date + 1 day**.
   - If the vendor date is its estimate (period end + 45 days), it becomes usable at period end + 90 days.
   - It is never usable before its availability date, even if delivered earlier (canary: delivery 20 days early changes nothing).
3. **Protections before exposure:**
   - **quarantine:** an accession number from a later year means a later filing (637 quarantined, 20 released by an SEC-verified list, 134 field-level releases);
   - **restatement guard:** values first filed after the vendor date (306 blocked in 2010–2017);
   - **SEC timing holds:** 27 applied;
   - **impossible timing** (filing before period end, or unknown): 608, never exposed.
4. **Amendments** (58 in 2010–2017) replace their period **only from their own availability date**.
5. **True TTM** at t uses the four most recent quarters **visible at t**, all consecutive, the newest ≤ 200 days old. It is available from the day after the newest component's filing (C10 = 0: no component filed on or after t).
6. **Year-over-year change** compares the TTM at t with the TTM **recorded at the snapshot 12 months earlier**, as known then. Nothing is recomputed backwards.
7. **Metadata.** No current-status metadata enters (fiscal-year end, Morningstar sector). The financial/REIT category comes from the SEC SIC **visible at t**.

**Proof on real data (E991-02):**
- 145,500 vendor reports observed and 102,067 eligible stock-months;
- C1, C3, C10, C11 and C12 all **0**;
- 0 reports with a file date after first delivery; 0 with a file date before period end;
- 285 deterministic cross-domain snapshots, every component dated on or before the decision morning (item 22);
- the independent SEC check (item 29).

## 8. Fundamental leakage tests

**Reusable canary suite** (`tests/test_p7_canaries.py`; offline, synthetic, built on the frozen PIT store):

| Test | What it proves | Result |
|---|---|---|
| Future-filing invariance | Deleting or changing every filing after t leaves every input at or before t identical; early vendor delivery changes nothing | pass |
| Dataset truncation | Feeding only data up to t gives exactly the full-replay snapshot at t (3 dates) | pass |
| Amendment timing | An amendment changes nothing before its own availability | pass |
| Restatement protection | A blocked (restated) report and a quarantined report are never exposed; True TTM falls back to the previous visible quarters (exact values checked) | pass |
| Estimated filing date | Hidden until period end + 90 days | pass |
| Determinism | Two replays are byte-identical | pass |

**Real-data counterparts:** E991-02 checks C1/C3/C10/C11/C12 = 0, plus the SEC sample (item 29).

## 9. Fundamental coverage by year

**Point in time, eligible stock-months; per month = the yearly average.**

| Year | Eligible / month | Non-fin. / month | NI + assets | GP + assets | NI + assets + OCF | NI + assets + equity | Full core (rev, NI, OCF, assets, equity) | Core + GP | Full core, share of ALL eligible |
|---|---|---|---|---|---|---|---|---|---|
| 2010 | 808 | 679 | 86.7% | 81.3% | 86.6% | 86.7% | 83.7% | 78.3% | 70.3% |
| 2011 | 924 | 759 | 80.8% | 70.3% | 80.4% | 80.8% | **76.7%** | 68.7% | 63.0% |
| 2012 | 929 | 757 | 89.4% | 80.7% | 87.9% | 89.4% | 83.9% | 78.1% | 68.4% |
| 2013 | 1,071 | 868 | 90.3% | 80.7% | 89.3% | 90.3% | 84.5% | 78.3% | 68.4% |
| 2014 | 1,198 | 954 | 91.2% | 84.5% | 90.2% | 91.2% | 87.0% | 82.7% | 69.3% |
| 2015 | 1,224 | 958 | 92.7% | 84.9% | 91.7% | 92.7% | 87.1% | 83.3% | 68.1% |
| 2016 | 1,173 | 904 | 93.2% | 87.7% | 92.7% | 93.1% | 89.3% | 86.1% | 68.8% |
| 2017 | 1,276 | 980 | 89.3% | 86.7% | 88.6% | 89.3% | 85.4% | 82.1% | 65.6% |

- **Technical availability is ≈ 98%** (item 4). The young stocks that lack technical history also lack four quarters of fundamentals, so combined technical + fundamental coverage is close to the fundamental figure (at least the product, at most the minimum).
- **Non-financial share:** the financial/REIT policy (SEC SIC) excludes 16–23% of eligible stock-months (rising with REIT listings).
- **Year-over-year change** (non-financial):

  | Year | Revenue | Gross profit | Net income | OCF |
  |---|---|---|---|---|
  | 2010 | 0% (no 12-month PIT history yet) | 0% | 0% | 0% |
  | 2011 | 62% | 54% | 65% | 68% |
  | 2013 | 68% | 63% | 72% | 72% |
  | 2015 | 75% | 72% | 79% | 80% |
  | 2017 | 73% | 71% | 73% | 77% |

- **Valuation inputs** (approved field ÷ PIT market cap) have the same coverage as the field itself.
- **2018–2021** coverage exists from P2-CP7, but it is **deliberately not used** in Phase 7.

## 10. Fundamental staleness

E991-02. "Age" is measured at the decision session.

| Year | Current record: days since period end (median / p95 / max) | Days since it became usable (median / p95) | True TTM newest quarter (median / p95) | Newest TTM filing age p95 |
|---|---|---|---|---|
| 2010 | 91 / 127 / — | 52 / 95 | 91 / 124 | 94 |
| 2011 | 91 / 128 / — | 48 / 95 | 91 / 123 | 95 |
| 2012 | 93 / 123 / 190 | 52 / 90 | 93 / 123 | 90 |
| 2013–2017 | 90–92 / 123–125 / ≤ 200 | 41–52 / 90–92 | 90–92 / 123–125 | 90–92 |

**Reading:** a typical fundamental input is one quarter old (period end about 3 months before), and was filed about 7 weeks before the decision. The 200-day freshness limit removes stale records (72 stock-months a year fail TTM for staleness). **No stale fundamental is used silently.**

## 11. Fundamental missingness risks

Non-financial eligible stock-months 2010–2017. "Missing" = the full core set is unavailable.

| Characteristic | Missing share |
|---|---|
| **Listing age < 12 months** (first seen in the vendor feed within a year) | **93.2%** |
| Listing age 12–24 months | 35.1% |
| Listing age ≥ 24 months / present since 2008 | 11.8% / 12.7% |
| **SEC-repaired securities** (no vendor fundamentals) | **54.1%** (XBRL for smaller filers only from mid-2011) |
| Native securities | 12.7% |
| Size tercile T1 (smallest) / T2 / T3 | 16.7% / 15.2% / 13.2% |
| FF12 Energy / Telecom / Shops / Health / Non-durables | 23.0% / 18.0% / 16.0% / 15.9% / 15.9% |
| FF12 Business equipment / Chemicals / Durables | 10.5% / 10.9% / 10.9% |
| SIC unavailable ("Unclassified") | 25.4% |
| **Left the data feed (delisted / acquired / bankrupt) within 12 months** | missing names **5.7%** vs complete names **3.6%** |
| By year | 16.3% (2010), **23.3% (2011)**, 16.1%, 15.5%, 13.0%, 12.9%, 10.7%, 14.6% (2017) |

**Interpretation (no return was computed):**
- Requiring complete fundamentals **systematically removes new listings, SEC-repaired names (often smaller or later-acquired companies) and Energy, and slightly more of the smallest third**.
- It also removes companies about 1.6× as likely to leave the universe within a year.
- That is exactly the selection that can look like "quality alpha" if missing names are simply dropped from the candidate set but kept in the benchmark.

**Required handling (P7-CP2):**
- missing fundamentals are **never filled**;
- an unscorable name is excluded from the candidate set **and** from every comparison universe (the same-universe rule, as in P2-CP7);
- the excluded share is reported every period;
- an explicit young-stock rule is applied identically to all books.

## 12. Sector-classification availability

| Source | PIT? | Earliest reliable | Coverage of eligible stock-months | Changes | Verdict |
|---|---|---|---|---|---|
| **SEC SIC at filing** (XBRL RSS, D113) → Fama-French 12 | Yes: effective the day after each periodic filing | **2011** | 2010: 69.4% from SIC (30.3% fall back to the filing-structure rule, which gives a financial/operating category but no FF12 group); 2011: 92.5%; 2012–2017: 95.3–97.8% | 4–13 SIC changes a year among eligible names (2–7 crossing FF12 groups; 0–4 crossing the REIT boundary) | **A from 2011**, B in 2010 |
| Morningstar sector / industry code | **No** | — | ≈ 100% | **0 changes for all 1,938 securities over 2010–2017**: current-status values projected backwards | **C** (unsafe) |
| Select Sector SPDR ETFs | Prices: yes | 1998-12-22 | — | — | B: no PIT stock→GICS map, so a stock cannot be assigned to an ETF point in time |

## 13. Sector PIT fidelity

- **The SIC lookup is point in time:** the code visible at t is the one carried by the latest periodic filing filed before t (test `test_sector_classification_is_point_in_time`: a later REIT code is not projected back).
- **Real data, alignment sample:** 250 of 254 sampled SIC filing dates are periodic filings in the registrant's own SEC history. The 4 not found belong to successor-CIK cases.
- **Known limits (P2-CP7):**
  - the SIC can lag a business change (e.g. Host Hotels coded 7011);
  - 433 native securities without SEC filings (foreign filers) have no FF12 group and remain "Unclassified" (2–3% from 2012).

## 14. Sector-context feature feasibility

**FF12 group sizes** (eligible names per month-end, median; Money = financials):

| Year | BusEq | Chems | Durbl | Enrgy | Hlth | Manuf | Money | NoDur | Other | Shops | Telcm | Utils | Unclassified |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2010 | 60 | 14 | 11 | 39 | 38 | 45 | 83 | 26 | 57 | 49 | 13 | 25 | 318 |
| 2011 | 127 | 30 | 23 | 55 | 64 | 93 | 163 | 46 | 102 | 91 | 21 | 39 | 78 |
| 2013 | 149 | 35 | 27 | 57 | 80 | 103 | 202 | 54 | 130 | 119 | 31 | 46 | 44 |
| 2017 | 180 | 40 | 30 | 58 | 104 | 109 | 295 | 65 | 163 | 116 | 30 | 58 | 31 |

| Feature | Required data | Available | Clean start | PIT | Computation |
|---|---|---|---|---|---|
| Sector relative strength (sector index momentum vs the universe) | PIT sector membership plus total-return prices | ✔ (SEC SIC FF12; panel) | **2011** | ✔ (membership at t; returns inside windows ending at t) | Trivial (group means) |
| Sector trend (sector index vs its own SMA) | same | ✔ | 2011 | ✔ | Trivial; equal-weight index rebuilt each date (no survivorship) |
| Stock vs sector relative strength | same | ✔ | 2011 | ✔ | Trivial |
| Sector breadth (% of the sector above SMA200) | same, plus states | ✔ | 2011 | ✔ (item 16) | Trivial; **Durables and Telecom have only 23–30 names**, so a noisy share; Chemicals 30–40 |
| SPDR ETF sector strength | ETF prices; stock→GICS map | prices ✔, map ✗ | — | ✗ for the stock assignment | Not recommended |

## 15. Market-regime feature availability

| Input | Data | Earliest | PIT | Verdict |
|---|---|---|---|---|
| SPY trend (vs SMA200, slope) | SPY bars | 1998 | ✔ | **A** |
| SPY volatility (realised) | SPY bars | 1998 | ✔ | **A** |
| VIX level | VIX index / CBOE VIX (3,272 bars 2005-01 → 2017-12) | 2005 | session close | **A** (availability verified; a fidelity check on gaps is a P7-CP2 item) |
| Breadth: % eligible above SMA200 / SMA50 | PIT universe + panel | 2010-01 | ✔ (item 16) | **A** |
| New 52-week highs − lows | same | 2010-01 (252 own bars) | ✔ | **A** |
| Breadth momentum (change in breadth) | breadth series | 2010-02 | ✔ | **A** |
| Interest rates, credit spreads, macro | not in the project | — | — | **D** |

**Breadth levels** (% of eligible names above their own SMA200; descriptive only, not a return):

| Year | Mean | Min | Max |
|---|---|---|---|
| 2010 | 72% | 30% | 94% |
| 2011 | 63% | 9% | 94% |
| 2012 | 70% | 46% | 88% |
| 2013 | 84% | 72% | 93% |
| 2014 | 72% | 33% | 84% |
| 2015 | 57% | 23% | 77% |
| 2016 | 62% | 17% | 82% |
| 2017 | 72% | 57% | 82% |

## 16. Breadth PIT feasibility

- **Denominator at t:** the securities **eligible at t**, from the frozen universe's own selection for that day; 1,994 selection days.
- **Numerator:** each security's state from its own bars up to t.
  - "Insufficient history" (fewer than 200 / 50 own bars) or a stale last bar (> 5 sessions) is counted separately, never as "above" or "below".
  - Insufficient names: 7–30 a day (young stocks).

## 17. Breadth survivorship audit

| Check | Result |
|---|---|
| Stock-days in breadth denominators belonging to securities that later stopped trading (acquired, delisted, bankrupt) before 2017-12-29 | **240,986** (counted while eligible, never after: 0 eligible stock-days after a last bar) |
| Survivors-only denominator (only names still eligible on the last day) vs the PIT denominator | % above SMA200: mean difference −0.46 points, **mean absolute 0.79, maximum 3.17 points**. % above SMA50: max 3.83. New highs: max 3.0. New lows: max 1.5 |
| Entrants (IPOs, spin-offs, companies crossing $2B) | Enter the denominator only from their first eligible day: 289–429 entrants a year, of which 15–73 first seen in the data within 365 days |
| Exits | 210–417 a year (most fall below a size or liquidity limit); 19–65 a year stop trading (delisted, acquired or bankrupt) |
| Synthetic canary (`test_breadth_survivorship_entrants_and_exits`) | An IPO is absent before listing; acquired and bankrupt names are counted before and not after their exit; survivors-only differs |

**Verdict:** historical breadth can be computed **without survivorship bias** from the existing PIT universe. A survivors-only shortcut would bias it by up to about 3 points.

## 18. Candidate-universe fidelity

The universe was not modified.

| Item | Result |
|---|---|
| Market-cap timing | Vendor market cap is PIT (D107). For 495 SEC-repaired securities: cover shares filed before t × price, split-adjusted only for splits observed live (D111; canaries C4/C5/C6 = 0 in E976) |
| Market-cap staleness | Market cap unchanged while price changed: 2–14 stock-months a year (≈ 0.05%). Implied share count (cap ÷ price) jumping > 25% month-on-month: 31–68 a year (≈ 0.5%; mergers, issuance, repaired-name cover updates). No systematic staleness |
| ADV20 | The harness 20-day mean of vendor dollar volume, as of the previous close |
| Common-stock classification | Morningstar flags are current-status (D061) and handled with dated overrides (D057/D065). Funds, BDCs, LP/LLC units, royalty trusts and SPACs are excluded. **Morningstar `company_id` is blank for many later-delisted companies** (39–87 eligible securities share one blank id in sampled months), so it cannot detect duplicate share classes |
| Duplicate share classes (real) | 2–7 companies at a time with two eligible classes: BRK.A/B, DISCA/DISCK, NWSA/NWS, GOOG/GOOGL (2017), HEI/HEI.A, LBDA/LBDK, UA/UAA. **P7-CP2 needs a one-class-per-company rule**, using a PIT company key such as the SEC CIK of the filings, not Morningstar's id |
| Ticker changes | 81 of 1,938 eligible securities changed ticker in 2010–2017. Identifiers are QuantConnect security ids, so ticker changes do not break histories |
| IPO entry / delisting exit / corporate actions / stale holdings | Items 19–21; harness D059/D062 stale-holding exits unchanged |

## 19. Corporate-action fidelity

| Check (2007–2017 panel, 1,996 securities) | Result |
|---|---|
| Split events (`SPLIT_OCCURRED`) | 540: **527 aligned** with QuantConnect's SCALED_RAW jump, 0 realigned, **11 unverified**, 2 outside the bar range |
| The 11 unverified | BTU 2015 (known vendor inconsistency, D148), DISCK 2014 (share-class dividend), DNY 2016, EXPE 2011 (TripAdvisor spin-off and reverse split), MOT 2011 (Motorola Mobility spin-off and 1-for-7 reverse split), PCS 2013 (reverse merger), PXT 2013/2015, SAI 2013 (Leidos split-off and reverse split), SUNH 2010: **combined spin-off / reverse-split events** |
| Distributions | 39,245 events. Cross-checked against ADJUSTED over **4,394,438 day-steps**: 49 event steps beyond the cent-rounding tolerance (REIT stock dividends 2008–09, a few others); **2 non-event deviations (Chubb 2016-03-29 and 2016-06-28, about 0.52%: dividends present in QuantConnect's factor file but missing from the dividend feed)** |
| Large distributions (> 25% of price: spin-offs, specials) | 72 (71 residual "down" steps of the dividend factor match them) |
| Factor steps not explained by either feed (SCALED_RAW vs our construction) | 5 small, in 3 securities; 0 big; 11 securities whose SCALED_RAW last value ≠ RAW (rescaled; cross-check only) |
| Raw bar integrity | 0 duplicate bars, 0 out-of-order, 0 off-calendar, 0 non-positive or NaN OHLC, **0 OHLC inconsistencies**, 4 zero-volume bars, 0 stale runs (≥ 5 identical zero-volume closes) |
| Chart moves > 50% in a day on ELIGIBLE days | **149**: 16 are the first bar of a new security life (item 25); **7 near unverified split events**; **24 near large distributions** (spin-offs: the chart series is not adjusted for them); **102 other** (biotech results, takeovers, crashes; 0 one-day spikes that reverse); **2 unexplained**: MKL 2010-04-19 (× 0.069) and NOX 2016-09-16 (× 0.155) |

## 20. Delisting handling

- **378** panel securities' last bar is before 2017-12-29.
- **0 eligible stock-days after a last bar** and 0 stale.
- The universe drops a security when it leaves the fundamental feed: 19–65 stopped trading a year among eligible names.
- **LEAN delisting events** reach the algorithm only for **subscribed** securities. For a holding, the harness closes at the last real close after 10 sessions without data (D062).
- Breadth and the PIT universe count a delisted security until its exit (item 17).

## 21. IPO / young-stock handling

| Year | Eligible month-rows with < 252 own bars | < 504 bars |
|---|---|---|
| 2010 | 1.1% | 1.9% |
| 2011 | 1.6% | 3.2% |
| 2012 | 1.9% | 4.0% |
| 2013 | 2.2% | 4.9% |
| 2014 | **3.2%** | 6.4% |
| 2015 | 2.6% | 6.7% |
| 2016 | 1.5% | 4.4% |
| 2017 | 2.3% | 4.3% |

- Young names lack 12-month features (NaN, never filled) **and** fundamentals: 93% have no True TTM in their first year.
- New listings enter the universe after 20 sessions (ADV20) once they reach $2B.
- **A score requiring 12-month technical and 4-quarter fundamental history automatically excludes them.** That is a deliberate, disclosed rule, applied to every comparison book.

## 22. Cross-domain timing alignment

**Sample:** 285 deterministic (security, month) samples. The selection is a hash of the security id and date, 3 a month, identical in X991 and X992.

**Example** (Autoliv, decision morning 2010-02-02; data through the 2010-02-01 close):

| Component | Date |
|---|---|
| Technical / price data through | 2010-02-01 close; last bar 2010-02-01 (X992 `AP` line) |
| Market cap | 2010-02-01 close |
| Fundamental record | 10-Q for 2009-09-30, filed 2009-10-21, usable from 2009-10-22 |
| True TTM newest quarter | 2009-09-30, filed 2009-10-21 |
| Sector (SEC SIC) | none visible yet (2010, pre-XBRL) → "Unclassified" by the structure rule |
| Breadth | denominators and states through 2010-02-01 |

**Results:**
- every component of all 285 samples is dated on or before the day before the decision morning: **0 alignment violations in X991 and 0 in X992** (380 price-side samples);
- **0 components from a later information set.**
- 3 samples had no fundamental record (young / foreign names).

## 23. Earliest clean date per data family

| Family | Earliest reliable date | Limiting factor |
|---|---|---|
| Technical (eligible universe) | **2010-01-29** (first month-end) | Universe market cap from 2009-10; windows use history from 2007 |
| Fundamentals: levels (True TTM, snapshots) | **2010-01** | True TTM needs 7 quarters (warm-up 2008-07). 2011 coverage dips to 77% (quarantine), disclosed |
| Fundamentals: year-over-year change | **2011-01** | Needs the PIT TTM recorded 12 months earlier |
| Sector (SEC SIC → FF12) | **2011-01** | 2010: 31% unclassified (pre-XBRL filers); 2011+: ≤ 7.5% |
| Breadth / market regime | **2010-01** (breadth); SPY 1998; VIX 2005 | Universe |
| Earnings events (SEC 8-K) | 2010 | Event Data v1 |

## 24. Recommended common Phase-7 development window

**2011-01-31 → 2017-12** (month-end decisions; about 84). This follows mechanically: it is the latest of the per-family earliest reliable dates for the full intended information set (sector context and fundamental change both start in 2011).

- If P7-CP2 drops both sector context and year-over-year fundamentals, the rule gives 2010-01-29 instead.
- **The start was not chosen by any result.** No return exists.
- **2018–2021 stays untouched** (reserved for a later, separately approved stage). The Holdout stays locked.

## 25. Data-error findings

| # | Finding | Severity | Status |
|---|---|---|---|
| E1 | **Re-used ticker-based security ids join two companies' histories across a long gap** (40 securities with a new "life"; e.g. GDI 2013/2017, HCC 2015/2017, GPRO 2012/2014, LSI 2014/2016, QWST 2011/2013). Bar-based features of the new listing would include the old company's prices | Material for the affected names; **20 eligible stock-months** in 2010–2017 | **Repaired for Phase 7** (D167, item 26) |
| E2 | 11 split events disagree with QuantConnect's own SCALED_RAW (combined spin-off / reverse-split events) → 7 artificial > 50% chart moves on eligible days | Low (few names), but invisible without a check | **Flag** (data-uncertainty disqualifier, item 32) |
| E3 | Spin-offs are not price-adjusted in the split-adjusted chart series (72 large distributions; 24 artificial > 50% chart moves on eligible days) | Medium for chart / trend features | **Flag**, plus a series-choice rule (item 4) |
| E4 | The dividend feed rounds amounts to the cent (≤ $0.005 per distribution) | Negligible | Disclosed (D162) |
| E5 | Two Chubb dividends (2016) missing from the dividend feed (≈ 0.5% each) | Negligible | Disclosed |
| E6 | 49 distribution steps differ from ADJUSTED beyond cent rounding (REIT stock dividends 2008–09) | Low | Disclosed |
| E7 | Morningstar `company_id` blank for many later-delisted companies | Medium for duplicate-class detection | Do not use; use a PIT company key (item 18) |
| E8 | Morningstar sector / industry codes are current-status (0 changes in 8 years) | High if used | Excluded (C) |
| E9 | 2 unexplained one-day chart moves: MKL 2010-04-19 (× 0.069) and NOX 2016-09-16 (× 0.155) | Unknown (2 stock-days) | Open; listed in item 37 |
| E10 | Vendor period ends are normalised to calendar month-ends for 52/53-week filers (SEC: true Friday / Saturday) | None for timing (filing dates match) | Disclosed |
| E11 | The universe-selection stamp is the calendar day after the session it reflects, so the monthly snapshot session varies at month boundaries | Low | P7-CP2 defines decisions from the session calendar |

**No defect was found in:** fundamental timing (0 early exposures), duplicate or out-of-order bars, OHLC consistency, stale prices on eligible days, delisting exits, breadth denominators, or the independent feature recomputation.

## 26. Infrastructure fixes made

1. **Security-life rule** (`qr_p7.LIFE_GAP = 60`, D167). More than 60 missing sessions between two bars starts a new life, and no feature window crosses it. It is implemented in the primary, independent and calendar-state code, with a dedicated test. With it, X992 v1.2 (E992-03) still agrees 380 / 380.
2. **Audit tooling (new; no frozen code changed):**
   - `qr_p7` (features, breadth, sampling, combinations, alignment);
   - the X991 / X992 audit hosts;
   - the SEC sample check;
   - the P7 canary suite.
3. **Runner / config:** `qr_p7` upload; a config rule pinning P7-CP1 audits to 2010-01-04 → 2017-12-31 with the data-v1 universe.

No change was made to the harness, the PIT store, the SEC table, the universe or any frozen spec. Data infrastructure v1 is unchanged (`tests/test_data_freeze.py` passes).

## 27. Whether fixes affect earlier phases

- The security-life rule exists only in Phase-7 code. Earlier hosts (H019 X985, H020 X987 panels, harness windows) used gap-blind windows.
- **Exposure:** at most the 40 re-used ids, binding on 20 eligible stock-months of about 102,000 (0.02%) in 2010–2017.
- Every earlier conclusion was far from its gates:
  - H019 F 1.31 vs c 2.87;
  - H020 t 0.27 vs 2.33;
  - Phase 3: no cluster near τ;
  - H021-A was ETFs only.
- **Assessment:** this cannot change any earlier conclusion. **No earlier result is re-run or modified**; doing so would need owner approval.

## 28. Full canary results

| Canary | Where | Result |
|---|---|---|
| PIT universe (eligible after last bar, stale eligibility, no bar at t) | X992 | 0 / 0 / 0 |
| Prices (duplicates, order, OHLC, splits vs SCALED_RAW, distributions vs ADJUSTED) | X992 | 0 / 0 / 0 / 11 unverified / see item 19 |
| Corporate actions (synthetic: later factors cancel) | test_p7_features | pass |
| Fundamental availability (C1, C3 quarantine / blocks / holds, C10, C11, C12) | X991 v1.1 | **all 0** |
| Fundamental leakage (future filing, truncation, amendment, restatement, estimated date) | test_p7_canaries | pass |
| Sector classification PIT | test_p7_canaries; X991 | pass; 250 / 254 SIC filings found at the SEC |
| Market breadth (PIT denominator, survivorship) | X992; test_p7_canaries | 240,986 dead-stock days counted; survivors-only max error 3.2 points |
| Cross-domain alignment | X991 (285), X992 (380) | **0 violations** |
| Future-data invariance / dataset truncation (technical) | test_p7_features | exact |
| Determinism | test_p7_canaries; sampling | pass |
| Independent recomputation (technical) | X992 | 380 / 380 |
| Independent SEC verification (fundamental timing) | P7_sec_sample_check | 268 matched; **0** exposed before the SEC filing |

**Test totals:**
- 18 new P7 tests (7 features, 9 canaries, 2 host pipelines, offline against a fake QuantConnect);
- the full suite passes (item 26).

## 29. Independent / manual sample verification

**Deterministic sample:** 285 (security, month) pairs. These are the same pairs as the alignment lines, chosen by a hash of the id and date (not hand-picked).

1. **Technical:** 380 pairs. These are the 285 plus one extra per month, recomputed from fresh history (item 5): **0 discrepancies**.
2. **Fundamental timing vs the SEC's own records** (data.sec.gov submissions):

   | Measure | Result |
   |---|---|
   | Records | 282 |
   | Matched to the SEC 10-K/10-Q of that period | **268** (report date within 7 days for 52/53-week filers; 1 by filing date because the SEC report-date field is wrong) |
   | **Became usable on or before the SEC filing date** | **0** |
   | Decision morning on or before the SEC filing date | 0 |
   | Vendor file date = SEC filing date | 264 |
   | Vendor date later than the SEC date (conservative) | 3 (6–21 days) |
   | Vendor date before the SEC date | 1 (NetSuite FY2012: the vendor's estimated date, period end + 45; the +90-day rule held it until 2013-03-31, after the 10-K of 2013-02-28) |
   | Not matched | 14: foreign private issuers filing 20-F / 6-K (QGEN, CHKP, SINA, NXPI, SSYS, ABY) and successor registrants (LBTYA, AVGO, BLK, APA: the current-status CIK, D111) |

3. **Sector:** 250 / 254 sampled SIC filing dates are real periodic filings of the registrant.

## 30. READY / CAVEAT / UNSAFE / UNAVAILABLE matrix

**Legend:** A = ready, trustworthy PIT; B = usable with a caveat; C = insufficient or unsafe; D = unavailable.

### Technical

| Component | Class | Note |
|---|---|---|
| Long-term trend (close / SMA200, SMA50 / SMA200) | **A** | Series choice: item 4 |
| Medium-term trend (close / SMA50) | **A** | |
| Momentum 12-1, 6-1 (total return) | **A** | |
| Proximity to 52-week high / low | **A** | Chart series; spin-off flag |
| Volatility (60-day, ATR14) | **A** | |
| Liquidity (ADV20) | **A** | |
| Relative strength vs the universe / SPY | **A** | |
| Price structure / breakout (H020 chart machinery) | **B** | Computable and verified (P5), but rejected as a predictive score; only as a disqualifier |
| Volume confirmation, RSI, MACD, Bollinger | **B** | Computable; Tier D evidence (P4-CP2); redundant (item 31) |
| Intraday / order-book data | **D** | |

### Fundamental

| Component | Class | Note |
|---|---|---|
| Profitability (GP/A, NI/A, OCF/A) | **A** | GP lower coverage |
| ROE (NI / equity > 0) | **B** | Unstable near zero equity |
| Cash-flow quality (accruals, OCF/NI) | **A** | |
| Balance sheet (equity / assets, negative equity) | **A** | |
| Leverage via debt | **C** | total_debt unvalidated |
| Revenue / GP / NI / OCF growth (YoY) | **A from 2011** | 62–80% coverage |
| Deterioration / improvement (Δ NI/A) | **A from 2011** | |
| Valuation (E/P, CF/P, S/P, B/M) | **A** | PIT market cap; negative earnings handling to be designed |
| Operating income, FCF, debt-based ratios | **C** | |
| Share issuance (share counts) | **C** | Counts restated; implied cap ÷ price proxy unvalidated |
| Analyst estimates, guidance, news | **D** | |

### Sector

| Component | Class | Note |
|---|---|---|
| Sector membership (SEC SIC → FF12) | **A from 2011** (B 2010) | |
| Sector relative strength, sector trend, stock vs sector | **A from 2011** | |
| Sector breadth | **B** | Small groups (Durables, Telecom 23–30 names) |
| Morningstar sector codes | **C** | Current-status |
| GICS / SPDR mapping of stocks | **D** | |

### Market regime

| Component | Class | Note |
|---|---|---|
| SPY trend, SPY volatility | **A** | |
| Breadth (% above SMA50 / 200), new highs − lows, breadth momentum | **A** | PIT denominators verified |
| VIX | **A** (availability) | Gap / fidelity check in P7-CP2 |
| Rates, credit, macro | **D** | |

## 31. Information-overlap map

The averages below are of month-end cross-sectional **Spearman correlations between features**. No return is involved.

**Technical** (E992-03; 95 month-ends; eligible names with all features):

| | SMA50 | SMA200 | 50/200 | 52w-high | 52w-low | Mom 12-1 | Mom 6-1 | ATR | Vol60 | ADV |
|---|---|---|---|---|---|---|---|---|---|---|
| close / SMA200 | 0.65 | 1 | **0.86** | 0.73 | 0.76 | 0.60 | **0.75** | −0.05 | −0.02 | −0.04 |
| SMA50 / SMA200 | 0.24 | 0.86 | 1 | 0.57 | 0.71 | **0.72** | **0.90** | −0.01 | −0.02 | −0.03 |
| ATR / price | −0.06 | −0.05 | −0.01 | −0.48 | 0.29 | 0.02 | −0.02 | 1 | **0.83** | 0.01 |

**Fundamental** (E991-02; 83 month-ends; non-financial names with all inputs):

| | GP/A | NI/A | OCF/A | Accruals | E/A | E/P | CF/P | S/P | B/M | Rev growth | ΔNI/A |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NI/A | 0.60 | 1 | **0.69** | 0.23 | 0.32 | 0.41 | −0.19 | −0.20 | −0.42 | 0.11 | 0.42 |
| OCF/A | 0.58 | 0.69 | 1 | **−0.45** | 0.28 | 0.09 | 0.09 | −0.29 | −0.45 | 0.10 | 0.21 |
| B/M | **−0.53** | −0.42 | −0.45 | 0.10 | 0.18 | 0.29 | **0.51** | 0.44 | 1 | −0.23 | −0.18 |

**Clusters (count each once in a future score):**

| Cluster | Members | Evidence |
|---|---|---|
| **T1 trend / T2 momentum** | SMA200 ratio, SMA50/SMA200, 6-1 momentum, 52-week high/low | ρ 0.72–0.90 among them. 12-1 momentum is partly separate (ρ 0.60–0.72). One trend/momentum block, not three to five inputs |
| **T3 risk** | ATR, volatility | ρ 0.83: one input. Low volatility relates to proximity to the 52-week high (−0.48) |
| **Liquidity** | ADV | Independent of everything (|ρ| ≤ 0.05): a filter, not points |
| **F1 profitability** | GP/A, NI/A, OCF/A | ρ 0.58–0.69: one input |
| **F2 accruals** | (NI − OCF) / A | Algebraically tied to F1 (−0.45 with OCF/A) |
| **F5 valuation** | E/P, CF/P, S/P, B/M | ρ 0.29–0.53 among them. **B/M is opposed to profitability (−0.42 to −0.53)**: combining value and quality points partly cancels |
| **F3 change** | Revenue growth, ΔNI/A | ρ 0.35: related but distinct |
| **S1 sector strength** | Sector momentum | Contains part of a stock's own momentum by construction. Use sector strength **or** stock-vs-sector strength next to stock momentum, not both |
| **M1 regime** | SPY trend, breadth | Overlap. Regime controls exposure only |


## 32. Hard-disqualifier feasibility

Kinds only. No definitions or thresholds are set here.

| Kind | Data | Feasible PIT? |
|---|---|---|
| Severe downtrend (far below SMA200; new 52-week low) | prices (A) | **Yes** |
| Extreme volatility | prices (A) | **Yes** |
| Insufficient liquidity | ADV20 (A) | **Yes** |
| Insufficient history (young stock) | own bars (A) | **Yes** |
| Stale price | last bar age (A) | **Yes** |
| **Corporate-event data uncertainty** (window contains an unverified split, a > 10% distribution or a new security life) | split / dividend feeds, life rule (A) | **Yes**, and **recommended** given E1–E3 |
| Stale fundamentals (no TTM, or newest quarter older than N days) | PIT store (A) | **Yes** (the 200-day limit already applies) |
| Negative equity | equity snapshot (A) | **Yes** |
| Debt-based leverage | total_debt (C) | **No** |
| Profitability collapse (negative TTM NI / OCF) | True TTM (A) | **Yes** |
| Fundamental deterioration (YoY decline) | ledger (A from 2011) | **Yes**, from 2011 |
| Financial / REIT (outside a profitability framework) | SEC SIC (A from 2011) | **Yes** |
| Quarantined report / restatement block / SEC-repaired name without fundamentals | store and SEC-layer flags (A) | **Yes** |
| Duplicate share class | PIT company key (SEC CIK) | **Yes** (Morningstar id unusable) |
| Upcoming earnings date | no calendar data; only past 8-K events | **No** (past events only) |
| Going-concern opinions, fraud, analyst downgrades, news | — | **No** (unavailable) |

## 33. Design of the later availability-only threshold study

**Purpose:** choose how strict entry is from portfolio feasibility alone, after the score is defined and approved (P7-CP2), without seeing any return.

**Allowed inputs:** the score of every eligible security at every decision date of the development window, plus the PIT universe. **Not allowed:** any price after the decision date (except to know whether a security still exists, which the universe already says), any return, anything from 2018.

**Procedure (fixed before any score value exists):**

1. A pre-declared grid of score thresholds θ (for example every 5 points), written before the score is computed.
2. For each θ and decision date, measure:
   - **N(θ):** candidates with score ≥ θ (median, 10th and 90th percentile by year; the share of dates with N(θ) < the planned slots);
   - **persistence:** consecutive decisions a candidate stays above the exit level (median, 25th percentile), i.e. the implied holding period;
   - **churn:** the share of the candidate set replaced between decisions;
   - **cash utilisation:** expected filled ÷ planned slots;
   - **concentration:** the largest FF12 share of candidates, and the share of dates where one sector holds more than half;
   - **cost burden:** orders a year × $7 plus 10 bps of traded value, as % of capital.
3. **Selection rule, written before the study runs:** the strictest θ that meets every feasibility floor (fixed at P7-CP2: e.g. median N(θ) ≥ 1.5 × slots, implied holding ≥ the cost model's minimum, cost ≤ a fixed %/yr) on at least 80% of dates in every year.
4. **Report every θ, not just the chosen one.** The choice cannot be revisited after any return is seen.

**It answers:** how many high-score stocks normally exist, how often the book would be partly in cash, how long names stay high-score, and how often replacements occur. It never asks which threshold made money.

## 34. Design of the mechanical portfolio-size study

**Question:** with the score and threshold fixed, which K of 6, 8, 10 or 12 positions is mechanically sensible at $100K. No returns.

**Metrics per K:**

| Metric | K = 6 | 8 | 10 | 12 |
|---|---|---|---|---|
| Position size (2% cash buffer) | $16.3K | $12.3K | $9.8K | $8.2K |
| Weight per name | 16.7% | 12.5% | 10% | 8.3% |
| Round-trip cost per position ($7 × 2 + 10 bps × 2) | $47 (0.29%) | $39 (0.32%) | $34 (0.35%) | $30 (0.37%) |
| Cost per 100% annual turnover, % of capital | ≈ 0.29% | 0.32% | 0.35% | 0.37% |

Also measured from the score itself (item 33): orders a year, cash usage given N(θ), sector concentration, and the **dilution of best ideas** (the score gap between the 1st and K-th candidate).

**Binding constraint:** D051's maximum weight of 10% means **K < 10 needs an owner decision**. The $4,000 minimum and 15% gap reserve also apply.

**Selection rule, written before the study runs:** the smallest K with expected cash usage ≥ 80% and cost burden ≤ the ceiling, within the weight limit. **Performance is never consulted.**

## 35. Design of the hysteresis / churn-control study

**Mechanics:**
- entry threshold E > exit threshold X (a holding is kept while its score ≥ X);
- a replacement buffer Δ (a new candidate replaces a holding only if it scores at least Δ higher and no slot is free);
- an optional minimum holding period m (no exit before m decisions except by a hard disqualifier).

**Measured on a pre-declared (E, X, Δ) grid, from scores only:**
- round trips a year;
- median and 25th-percentile holding period;
- exits by cause (crossed X / replaced / disqualified);
- the **whipsaw rate** (exits re-entered within k decisions: BUY–SELL–BUY around one threshold);
- cash usage;
- cost burden.

The book is a deterministic score-only simulation: slots, T+1 timing, D051 sizing, and existence only from prices.

**Selection rule, written before the study runs:** among grid points with whipsaw ≤ a fixed limit and cost ≤ the item 34 ceiling, take the smallest E − X gap, with Δ the smallest value meeting the whipsaw limit.

**Data lineage (item 35 of the request).** Every future score input will carry a generated lineage row:

> input → source (RAW bars | split feed | dividend feed | approved PIT field | SEC table row | SEC SIC row | universe) → transformation (function and file hash) → PIT rule (e.g. filing + 1 day, +90 days if estimated, quarantine / blocks / holds, freshness 200 days; life rule) → value at (security, decision date).

- Features can be computed only through this registry.
- Each decision snapshot stores the input dates that prove it was knowable (as the X991 `A|` and X992 `AP|` lines now do).
- A canary recomputes a sample independently.
- **No number can enter the score without a lineage row.**

## 36. Expected runtime / resources

| Item | Value |
|---|---|
| Eligible securities per month (2010–2017) | 808–1,276 (≈ 1,000 average); 1,996 distinct securities |
| Decision dates (monthly, development window) | ≈ 84–95 |
| Daily panel | 2,769 sessions × 1,996 securities × 5 series ≈ 28 M values (≈ 220 MB in float64) |
| Fundamentals | 145,500 vendor reports observed; 102,067 eligible stock-months |
| X992 (prices, features, breadth, fidelity) | **443–495 s wall, 3.4 GB peak memory** (B2-8 node: 8 GB) |
| X991 (fundamentals, sector, alignment, warm-up from 2008-07) | **470–495 s** |
| A full score computation (both layers in one host, monthly) | ≈ 15–20 min per run and ≈ 4 GB. Fits one node without batching; the 64,000-character file limit means feature code stays in shared modules |
| Cost | Within the existing $24/month subscription; no extra node needed |

## 37. Exact remaining data gaps

1. **Sector in 2010** is 31% unclassified. This is the reason for the 2011 window start.
2. **Fundamental coverage dip in 2011:** 77% full core (quarantined mixed-period reports).
3. **SEC-repaired names have no vendor fundamentals.** XBRL starts mid-2011 for smaller filers, so 54% of their months are missing.
4. **New listings** (< 1 year) have no True TTM, and young stocks lack 12-month technical history. They are excluded by construction.
5. **Corporate-event price adjustment:** 11 unverified splits and 72 large distributions. Requires the item 32 data-uncertainty flag.
6. **Two unexplained one-day moves:** MKL 2010-04-19 and NOX 2016-09-16. They should be checked against an independent price source before P7-CP2 freezes anything; none was available here (licence: QuantConnect prices cannot be exported).
7. **Foreign private issuers** (20-F / 6-K, about 2–3% of names): their quarterly timing cannot be verified against 10-Q/10-K filings. The vendor date + 1 day rule applies.
8. **Not available at all:**
   - debt, current assets/liabilities, capex (operating income and FCF failed validation);
   - PIT share counts (issuance);
   - analyst estimates; news;
   - GICS sectors;
   - forward earnings dates;
   - rates and credit.
9. **VIX:** availability verified; a gap / fidelity check is pending.
10. **Duplicate share classes:** a one-class-per-company rule is needed (PIT company key).

## 38. Would a data purchase materially improve the architecture?

**Not for designing the score.** Every layer has trustworthy PIT data from 2011.

Two purchases would help **later**, and only with owner approval (none made):

1. **Longer history** (e.g. Sharadar Core US Fundamentals / SEP, ≈ $69/month, P2-CP12) for statistical power. 2011–2017 gives about 84 monthly decisions. Every phase so far has had about 50% power only for edges of about 3–5%/yr. More years would matter more than more fields.
2. **PIT GICS classification / debt fields** (institutional vendors; typically far above the $200/month ceiling). This would only refine sector context and leverage.

**Recommendation:** no purchase now. Revisit only if a design passes its development tests (consistent with D124).

## Answers to the owner's questions A–J

**A. Do we have enough reliable data to build Technical + Fundamental + Sector + Market Regime without lookahead?**
**Yes, from 2011.**

| Layer | Status |
|---|---|
| Technical | Verified 380 / 380 point in time |
| Fundamental | 0 leakage; 0 / 268 exposed before the SEC filing |
| Sector | SEC SIC at filing, ≥ 92% from 2011 |
| Regime | Breadth with PIT denominators; SPY; VIX |

In 2010 only sector context is weak (31% unclassified).

**B. Which fundamental fields are trustworthy?**
- **True TTM:** revenue, gross profit (where reported), net income, operating cash flow.
- **Snapshots:** total assets and stockholders' equity.
- **Daily:** point-in-time market cap.
- **Derived from these:** profitability, accruals, equity/assets, valuation ratios, and from 2011 year-over-year change.
- **Not trustworthy:** operating income, free cash flow, total debt, vendor '*_ttm' as 12-month values, share counts, per-share values, vendor ratios.

**C. Can sector information be used point in time?**
- **Yes:** the SEC-assigned SIC carried by each filing, effective the day after it, mapped to FF12. Coverage is ≥ 92% from 2011 and 69% in 2010.
- **No:** Morningstar sector codes (current-status: 0 changes in 8 years).
- **No:** SPDR ETFs for stock assignment (no PIT GICS).

**D. Can historical breadth be computed without survivorship bias?**
- **Yes.** The denominator is the frozen universe's own eligible set on each day.
- Securities that later delisted contribute 240,986 stock-days before their exit and none after.
- A survivors-only shortcut would err by up to 3.2 points.

**E. Earliest date all required information coexists reliably?**
- **2011-01** (month-end 2011-01-31), with the development window to 2017-12.
- **2010-01** if neither sector context nor year-over-year fundamentals are used.

**F. Hidden data-quality issues that could invalidate the score?**
**Found and handled:**
1. Re-used security ids joining two companies across a gap: repaired by the security-life rule; 20 stock-months affected.
2. Corporate-event mis-adjustment (11 unverified splits, 72 spin-offs) creating artificial chart moves: needs a data-uncertainty disqualifier.
3. Morningstar's company id and sector codes are unusable historically.
4. Duplicate share classes.
5. Missing fundamentals concentrated in new listings, repaired names and Energy, and in companies more likely to exit: needs the same-universe rule.

**Small, disclosed issues:**
- cent-rounded dividends;
- 2 missing Chubb dividends;
- 2 unexplained one-day moves.

**None invalidates a score designed with the item 40 rules.**

**G. What should be excluded as unsafe or too incomplete?**
- **Unsafe** (class C/D in item 30): debt-based leverage, operating income, free cash flow, share issuance, vendor ratios and per-share values, Morningstar sector/industry and company metadata, analyst / news / earnings-calendar data, macro, GICS.
- **Too incomplete:** sector context in 2010, fundamental growth in 2010, and sector breadth for the smallest FF12 groups (Durables, Telecom).

**H. Can we build a high-conviction score without excluding most of the universe?**
**Yes.**
- **Fundamentals:** non-financial names with the full core set are 77–89% of non-financial eligible stock-months (about 580–840 names a month).
- **Technical:** coverage ≈ 98%.
- **Scorable share of all eligible names:** about 63–70% if financials and REITs are excluded by policy. The exclusions are mainly by design (financials/REITs) plus new listings.
- **Year-over-year inputs** cut coverage to 62–80%; P7-CP2 should weigh that.

**I. Can the strategy maintain a small, low-turnover portfolio?**
**Mechanically yes:**
- several hundred scorable names a month;
- round-trip costs of 0.29–0.37% of a position at $100K, so about 0.3–0.4% of capital per 100% of annual turnover.

Two things are still open:
- **Persistence and churn** depend on the future score. They will be measured, with returns never consulted, by the item 33–35 studies.
- **The D051 10% maximum weight** forces at least 10 positions unless the owner relaxes it.

**J. Is the project technically ready to design the score?**
**Yes: READY TO DESIGN SCORE** (item 39), subject to the owner decisions in item 40.

## 39. Recommendation

# READY TO DESIGN SCORE

- **Why:**
  - every intended layer has point-in-time data that passed independent recomputation (technical, 380 / 380), independent SEC timing verification (fundamental, 0 / 268 early) and cross-domain alignment (0 / 665 violations);
  - every leakage canary is 0;
  - the defects found are either repaired (the security-life rule) or have a clear, data-only handling rule for P7-CP2 (corporate-event flags, series choice, one class per company, the same-universe rule for missing fundamentals).
- **Conditions:**
  - the owner decisions in item 40;
  - P7-CP2 designs the score, its pre-registration and its frozen specification only;
  - **no score is computed and no backtest is run before separate approval.**

## 40. Owner decisions required next

1. **Approve P7-CP1** and the move to **P7-CP2 Actual Score Architecture Design** (design and pre-registration only).
2. **Development window:** approve the mechanical window **2011-01 → 2017-12** (or 2010-01 if P7-CP2 excludes sector context and fundamental change). 2018–2021 and the Holdout stay locked.
3. **Approved input classes:** confirm that only class-A / class-B components (item 30) may enter the score, and that class C/D are excluded.
4. **Missing fundamentals:** confirm the **same-universe rule**. An unscorable name (missing core fundamentals, young, unclassified) is excluded from the candidate set **and** from every comparison book, never filled, and the excluded share is reported.
5. **Financials and REITs:** excluded from a profitability-based score (D113 policy, about 16–23% of eligible names), or scored by a separate technical-only path?
6. **Corporate-event data-uncertainty rule:** approve a hard disqualifier while a feature window contains an unverified split, a > 10% distribution or a new security life (thresholds set in P7-CP2).
7. **Price-series policy** (item 4): total-return closes for trend, momentum and volatility; the split-adjusted chart for high/low/range features with the corporate-event flag.
8. **One share class per company** (PIT company key from SEC filings).
9. **Portfolio size:** D051 caps weight at 10%, so K ≥ 10 unless the owner relaxes it for a high-conviction book of 6–8 names.
10. **Studies:** approve the designs of the availability-only threshold study, the portfolio-size study and the hysteresis study (items 33–35), to be run only after the score is frozen.
11. **No data purchase now** (item 38).

**STOP.** No score, weight, threshold, entry/exit rule, position count, return or backtest was produced. 2018–2021 and the Holdout are untouched.

---

**Programme totals (registry):**
- 19 hypotheses tested (H001–H021). Phase 7 has no hypothesis yet.
- 63 strategy / infrastructure ids, of which 20 are strategies.
- **This stage's runs** (all infrastructure; no trial):

  | Run | Outcome |
  |---|---|
  | E991-01, E991-02 | Completed |
  | E992-01 | `integrity_failed`: VIX subscription vs the runner's equity-dates check (D166); audit content complete |
  | E992-02, E992-03 | Completed |
