# P2-CP12 — Amendment 3 freeze, data-extension options and earnings-event data audit (STOP)

- **Date:** 2026-10-03.
- **Status: METHODOLOGY FREEZE + PREPARATORY STUDIES ONLY.**
  - No candidate, factor or strategy run; no factor, post-event or strategy returns computed.
  - No thresholds or holding periods chosen.
  - The Holdout was not accessed; Phase 2 slot 3 is **unused**; nothing purchased.
  - **STOP:** awaiting the owner.
- **QuantConnect runs:** one infrastructure run, **E981-01** (X981), an identifier export of the eligible universe. No prices, returns or orders were exported.
- **Supporting files:**

  | Topic | Files |
  |---|---|
  | Amendment 3 | `research/phase2/P2_amendment3_spec.md` (FROZEN, hash-pinned); `src/qresearch/wealth.py`; `tests/test_wealth.py`; calibration `research/phase2/architecture/P2_amend3_calibration.py/.json` |
  | Earnings events | `src/qresearch/sec_events.py`; `tests/test_sec_events.py` (13 leakage / timing tests); `research/phase2/earnings_audit/` (audit, time-zone conventions, predecessor recovery) |
  | Data extension | `research/phase2/data_extension/P2_data_extension_options.md` |

## Summary

1. **Amendment 3 is frozen.** The terminal-wealth objective is primary; the old +0.25 Sharpe-over-EW gate is now a diagnostic.
   - **W2 (evidence)** uses a serial-dependence-aware standard error, the larger of the independent-days estimate and an exact stationary block bootstrap (126-day blocks). Its critical value is **2.15**, calibrated so that false passes stay at about 5% or less even if relative performance has persistent style regimes.
   - **R2** allows Sharpe up to **0.15** below SPY's (≈ one standard error of the measured difference).
   - **Honest consequence:** with 12 years and 20 positions, a strategy needs a true edge of about **6.3% a year** over SPY for an even chance of qualifying. False passes are about 0.3%.
2. **Longer history is the main lever.**
   - **Sharadar** (via Nasdaq Data Link) is the only option found that combines point-in-time share counts and market caps, dead companies and as-reported fundamentals from 1998, at about **$69 a month** (price to re-verify).
   - Norgate has no historical shares; CRSP / Compustat are not sold to individuals; the free EDGAR reconstruction is estimated at **6–10 weeks** with high identity risk.
3. **The SEC earnings-event data is usable, after two corrections found by the audit.**
   - **(a) Time zones:** SEC's submissions data records timestamps in UTC for 1,759 registrants but in **mislabelled US Eastern time for 935**. Per-registrant conventions were measured against EDGAR's filing pages; 204 of 204 spot-checks then match.
   - **(b) Predecessor registrants:** the vendor's current-status CIKs miss years before holding-company reorganisations. The frozen dated-ticker identity rule recovers **636 of 862** such quarters.
   - **Coverage:** 93.9% of eligible security-quarters as measured; about **96.7%** for domestic filers after predecessor linking. Acquired and bankrupt companies are covered as well as survivors.
4. **Recommendation:** approve the event-data rules as a new, separately frozen "event data v1" component (§19). Decide on a time-boxed Sharadar evaluation only if research is to continue beyond slot 3. Keep slot 3 unused until then.

## 1–3. State confirmations

| Item | State |
|---|---|
| H016 | **Rejected** (D118), preserved exactly as tested (spec hash pinned) |
| Phase 2 slots | **2 of 3 used; slot 3 unused** |
| H017 (Value) | Proposal only; not approved, not implemented, not run |
| Holdout 2022-01-01 → 2026-08-31 | **Locked**, never accessed. The only post-2021 item touched is the calendar date 2022-01-03, used to name the next session after 2021-12-31 in the timing classification (no data) |
| Data infrastructure v1 | Frozen, unchanged (freeze test passes) |

## 4–9. Final frozen Amendment 3

The full text is `research/phase2/P2_amendment3_spec.md`, SHA-256 pinned in `qresearch.wealth.AMENDMENT3_SHA256`.

**Every candidate report begins with:** starting capital; final strategy value; final SPY value; both total returns; both CAGRs; excess CAGR; terminal wealth ratio.

| Gate | Exact rule |
|---|---|
| **W1** | CAGR(H) > CAGR(SPY total return), i.e. terminal wealth above SPY's over the same dates (net, $100K) |
| **W2** | g ≥ **2.15** × SE. Here g = 252 × mean(ln(1 + r_H) − ln(1 + r_SPY)), and SE = max(SE_iid, SE_SB). SE_SB is the exact Politis–Romano stationary-bootstrap standard error of the mean with mean block **126** sessions (deterministic) |
| **W3** | CAGR(H) > CAGR(same-universe EW) **and** > the median CAGR of the five matched random books |
| **R1** | MaxDD(H) at most **10 points** deeper than SPY's |
| **R2** | Sharpe(H) ≥ Sharpe(SPY) − **0.15** |
| **R3** | Total log excess over SPY > 0, and no calendar two-year block > 50% of it |
| **R4** | Costs ≤ 1.5% a year; no leverage; the frozen account / concentration limits |
| **G4′** | ≥ 5 of 6 pre-declared perturbations keep W1; W1 holds at 2× slippage |
| **Holdout / forward** | HO-W: CAGR(H) > CAGR(SPY); HO-R: R1. For market-timing or defensive designs, W1 must also hold on 2023-01 → 2026-08 alone |
| **Diagnostics** (never gates) | Sharpe − Sharpe(EW) (the retired +0.25 gate); Sharpe − Sharpe(SPY); DSR; PBO; the full risk set (volatility, Calmar, worst year, longest recovery, turnover, costs, concentration) |

### 6. How the W2 method was chosen (refinement 2)

All of this uses completed **control** books only: SPY, the same-universe EW, five random 20-stock books, 2010-03 → 2021-12.

- **What the data shows.** The excess returns of 20-stock books over SPY **mean-revert** at long horizons: the one-year variance ratio is 0.58–1.08 (mean 0.76). For such processes the plain independent-days standard error is already conservative, while long-window bootstrap / Newey–West estimates are slightly *too permissive* (6–8% false passes), because long-lag autocovariance estimates are noisy and biased down. Taking the maximum of the two fixes that.
- **What the data cannot rule out.** A real factor tilt may have **persistent** relative performance: style regimes such as value's long underperformance. On 12 years, no standard-error method (independent-days, Newey–West, any block length) holds 5% under such persistence: false passes are 7–21%. The critical value was therefore **calibrated**. 2.15 is the 95th percentile of the statistic under the most persistent process in a declared envelope: one-year variance ratio ≤ 1.25 with half-lives up to about 1 year, already above anything seen in the controls.

### 7. W2 operating characteristics

False passes at zero true edge:

| Process | Independent-days SE, z 1.645 | Frozen W2 |
|---|---|---|
| Control-like (resampled, blocks 21–504 sessions) | 1.9–4.9% | **0.4–1.4%** |
| Persistent, VR(1y) 1.25, half-life ≈ 3 months / ≈ 1 year | 8.0% / 11.4% | **2.5% / 4.6%** |
| Persistent, VR(1y) 1.5 | 10.7–15.0% | 3.3–7.0% |
| Persistent, VR(1y) 2.0 | 15.8–21.5% | 5.1–10.4% |

Full framework (W1–W3, R1–R3; R4 and G4′ not modelled, so these are upper bounds), 12 years, the currently feasible architecture:

| Positions | False pass | +1% | +2% | +3% | +4% | Edge for 50% | Edge for 80% |
|---|---|---|---|---|---|---|---|
| **20** | **0.3%** | 1.1% | 2.6% | 7.1% | 16.3% | **≈ 6.3%** | **≈ 8.6%** |
| 40 | 0.3% | 1.1% | 4.4% | 13.1% | 28.5% | ≈ 5.1% | ≈ 6.9% |

The same full framework at 20 positions with a different W2 critical value, for transparency:

| W2 critical value | False pass | At +3% | Edge for 50% |
|---|---|---|---|
| 1.645 | 1.5% | 17% | 5.2% |
| 1.96 | 0.5% | 11% | 6.0% |
| 2.15 (frozen) | 0.3% | 7% | 6.3% |

**Reading:** the refinements did what you asked. The evidence test is honest about serial dependence and persistence. The price is that **12 years of data cannot distinguish realistic edges (1–3% a year)**. This is a statement about the data, not the rules.

### 8. R2 (refinement 1)

- **Noise level:** the measured Sharpe difference between a no-edge 20-stock book and SPY has a standard deviation of **0.137** over 12 years.
- **Choice:** tolerance **0.15** ≈ 1 SE. That is the midpoint between "no true deficit" and a material true deficit of 0.30 (about one-third of SPY's Sharpe), with ≈ 14% error each way.

| Tolerance | Wrongly rejects a candidate with equal true Sharpe | Max volatility allowed at +3% excess (× SPY's) |
|---|---|---|
| 0 | 50% | 1.20× |
| 0.05 | 36% | 1.27× |
| 0.10 | 23% | 1.34× |
| **0.15** | **14%** | **1.43×** |
| 0.20 | 7.6% | 1.53× |

Your example (13.5% vs 10.5% CAGR, Sharpe 0.77 vs 0.80, MaxDD −39% vs −35%) passes R1 and R2; this is a test case.

### 9. W3, R1, R3, R4, G4′

As in the table above. W3 fails unless all five random books completed. R1 and R2 are tested with your two examples (`tests/test_wealth.py`).

## 10. Rolling-horizon reporting (never a gate)

`wealth.rolling_report` covers 1, 3, 5 and 10 years over every start date. It reports:
- the share of start dates on which the strategy beat SPY;
- the mean and median excess CAGR;
- the 10th and 90th percentiles;
- the worst and best windows;
- the **number of independent windows**.

It is always shown beside the same-universe EW and the five random books. Windows longer than half the sample are labelled **not evidence**.

## 11–13. Data-extension options

Full study: `research/phase2/data_extension/P2_data_extension_options.md`. Provider websites are blocked by this environment's network policy; facts come from web-search results (sources listed there) and must be re-verified on the providers' pages.

| Option | Dead companies | Historical shares / market cap | Point-in-time fundamentals | Price (to verify) | Fit |
|---|---|---|---|---|---|
| **Sharadar Core US Equities Bundle** (Nasdaq Data Link) | Yes (≈ 9,000 delisted) | **Yes** (`sharesbas`, daily `marketcap`; from 1998) | **Yes:** as-reported ARQ rows keyed by the filing date | **≈ $69/mo or $499/yr** full history | **Best fit.** Needs a Sharadar → QuantConnect identity map; personal licence forbids sharing raw or reverse-engineerable derived data |
| Norgate Data Platinum | Yes (prices; historical index constituents) | **No** (current only) | No | $630/yr | Fails the core requirement; Windows-only |
| EODHD All-In-One | Yes | Partly | **Unverified** | $99.99/mo | Second choice at best, after a point-in-time audit |
| CRSP / Compustat (WRDS) | Yes | Yes | Yes | Not sold to individuals | Not available |
| FMP / Tiingo | Partly | Partly | Unverified | Not verified | Insufficient (Tiingo delisted ≈ 2015+) |
| **EDGAR reconstruction** (free) | Must be rebuilt | From cover pages (text) | — | $0 | **6–10 weeks.** Identity of dead registrants is the main risk (silent survivorship bias). Audit burden high; the old QuantConnect dataset that could cross-check survivors is retired on 2026-10-31 |

**Budget:** Sharadar (+≈ $69/mo) keeps the total at ≈ $93/mo (target ≈ $100, ceiling $200). EODHD would bring it to ≈ $124/mo.

## 14–18. SEC earnings-event audit, 2010–2021 (no returns)

**Population:**
- 2,719 securities ever eligible on a month start (E981-01; 169,415 eligible stock-months);
- 2,706 registrants;
- **85,537 earnings events** after de-duplication.

### Mapping (point in time)

| Identity status of the security ↔ CIK link | Securities | Coverage of their quarters |
|---|---|---|
| Verified by dated ticker evidence (XBRL instance prefix = the security's ticker within ±3 months) | 2,411 | 94.7% |
| Verified by identity v2 (SEC-corrected securities) | 190 | 95.2% |
| Weak (one dated match) | 46 | 70.6% |
| Contradicted (prefixes never match) | 25 | 70.8% |
| Unverified (no prefix evidence in span) | 47 | 6.8% |

The 72 contradicted or unverified securities are mostly wrong current-status CIKs. They are excluded or need repair before any use; nothing is guessed.

### 14. Coverage by year

Eligible security-quarters with at least one earnings event:

| Year | Eligible securities | Expected | Observed | Coverage |
|---|---|---|---|---|
| 2010 | 943 | 3,339 | 3,140 | 94.0% |
| 2011 | 1,086 | 3,890 | 3,621 | 93.1% |
| 2012 | 1,074 | 3,881 | 3,631 | 93.6% |
| 2013 | 1,231 | 4,419 | 4,149 | 93.9% |
| 2014 | 1,363 | 4,994 | 4,680 | 93.7% |
| 2015 | 1,411 | 5,150 | 4,816 | 93.5% |
| 2016 | 1,379 | 4,931 | 4,641 | 94.1% |
| 2017 | 1,460 | 5,284 | 4,965 | 94.0% |
| 2018 | 1,535 | 5,612 | 5,271 | 93.9% |
| 2019 | 1,497 | 5,494 | 5,181 | 94.3% |
| 2020 | 1,625 | 5,564 | 5,249 | 94.3% |
| 2021 | 1,955 | 6,977 | 6,564 | 94.1% |
| **All** | | **59,218** | **55,587** | **93.9%** |

**By end-of-life status:**

| Status | Securities | Coverage |
|---|---|---|
| Continuing (eligible at end-2021) | 1,683 | 94.3% |
| Acquired / merged | 596 | 94.1% |
| Bankruptcy (8-K Item 1.03 observed) | 43 | 97.2% |
| Left the universe, still trading | 375 | 91.8% |
| Delisted / other | 22 | 49.1% |

**No survivorship skew:** dead companies are covered as well as survivors. SEC keeps every registrant's filing history.

### 15. Timing classification and earliest legal execution

Rules (frozen in `sec_events`): first SEC acceptance in US Eastern time, on the acceptance date D.

| Class | Rule | Share | Event session | Earliest decision / execution (our engine) |
|---|---|---|---|---|
| Before market open (BMO) | D a session, < 09:30 | 40.1% | D | close D / open D+1 |
| During trading | 09:30 ≤ t < 16:00 (13:00 on early-close days) | 8.9% (17% in 2010 → 3% in 2021) | D | close D / open D+1 |
| After market close (AMC) | ≥ close | 50.9% | next session D+1 | close D+1 / open D+2 |
| Non-session (weekend / holiday) | — | 0.2% | next session | its close / next open |
| Unknown | no usable time (or the registrant's time-zone convention unresolved) | 0% of events (the 12 unresolved registrants have no 2010–21 earnings 8-Ks) | as AMC of the filing date (conservative) | — |

**Execution rules:**
- **No same-period look-ahead:** an after-close release can never trade before the open of D+2.
- A trade at the BMO session's own open would be legal in reality, but our engine decides only at a close.

**Lag of the 8-K behind the release:**
- 87.6% of 8-Ks are accepted on the "date of report" (the release date);
- 6.3% one day later;
- ≈ 5% two or more days later.

Using the SEC acceptance is therefore point-in-time safe but **sometimes late**: the market can see a press release before SEC does. Any future reaction window must be anchored to the SEC-visible time, never to the release date.

### 16. Duplicates and amendments

| Item | Count (2010–2021) |
|---|---|
| Original earnings 8-Ks collapsed as duplicates (same registrant within 30 days of an event: re-filings, pre-announcement + full release, co-registrant filings) | 6,059 (≈ 7%) |
| Same-day duplicate filings | 1,040 |
| 8-K/A amendments (never create or modify an event) | 835 |

**De-duplication (deterministic):** an original Item 2.02 8-K starts a new event only if no event of that registrant began within the previous 30 calendar days. The event keeps the **first** acceptance.

### 17. Missing events (no dates invented)

The 3,627 eligible security-quarters without an event:

| Cause | Quarters | Fixable? |
|---|---|---|
| Foreign private issuer / transition filer (results on 6-K / 20-F, not 8-K) | 1,074 | Exclude such issuers from an event universe (or a separate 6-K rule; not proposed) |
| Registrant has no SEC filings around the quarter: **predecessor / successor CIK** (vendor CIK is current-status) | 809 | **Mostly yes:** the frozen dated-ticker rule links a unique predecessor for **636 of 862** such quarters (Exxon, Disney, Cigna, Google, Dow, Linde, Bunge, BlackRock, Xerox…); 194 ambiguous, 26 none |
| Periodic report filed; results possibly released under 8-K Item 7.01 / 8.01 | 688 | Not under the Item 2.02 rule; no inference |
| Periodic report filed without any earnings 8-K (e.g. companies that publish results only with the 10-Q) | 382 | Genuinely no 8-K event |
| Other (no earnings 8-K, no periodic report in the quarter) | 320 | — |
| Timing shift (two events in an adjacent quarter) | 235 | Not missing (calendar artefact) |
| CIK contradicted by ticker evidence | 119 | Mapping repair needed |

**Projected coverage:** with predecessor linking and foreign issuers excluded, ≈ **96.7%** of domestic-filer security-quarters.

### 18. Point-in-time leakage canaries

| Canary | Result |
|---|---|
| Filing invisible before SEC acceptance | Unit test passes |
| After-close event cannot trade the same day or the next open | Unit test passes |
| Amendments do not modify historical signals | Unit test passes |
| Duplicates cannot create duplicate opportunities | Unit test passes |
| Time-zone conversion (UTC vs mislabelled Eastern) | Unit test passes |
| **Timestamp canary:** converted acceptance time vs EDGAR index page (Eastern), 204 events stratified 17 a year | **204 / 204 exact matches** (the first, uncorrected attempt matched 35 of 48, which is how the time-zone defect was found) |
| Filing date vs acceptance date (EDGAR assigns the next business day after 17:30 ET) | 80,982 same date; 4,543 later after 17:30; only **12** inconsistent (was 1,258 before the correction) |

## 19. Is the earnings-event data reliable enough to support a hypothesis?

**Yes, for US domestic filers, with conditions.** The conditions, to be approved and frozen as an "event data v1" component (separate from data infrastructure v1, which is unchanged):
1. the per-registrant time-zone conventions as measured (`tz_conventions.json`), with unresolved registrants treated as unknown time;
2. the timing classes and earliest-execution rules of `sec_events`;
3. 30-day de-duplication; amendments ignored;
4. predecessor linking only by the frozen dated-ticker rule (unique, time-disjoint), with ambiguous cases excluded;
5. foreign private issuers excluded from any event-driven universe;
6. the residual ≈ 3% of missing domestic quarters disclosed (no inferred dates).

The data supports **event timing**. It says nothing about whether any event strategy works; no post-event return was computed.

## 20. Is longer-history data worth considering?

**Yes, conditionally.** Power is the binding constraint (§7): on 12 years a real 2–3% edge qualifies only 3–7% of the time. History back to about 2000–2004 roughly halves the edge needed.
- For **event-driven** work, SEC events exist from 2003–04, so the universe (point-in-time market caps with dead companies) is the only missing piece.
- For **value**, Sharadar's as-reported fundamentals would also be needed.

**My view:** worth a **time-boxed evaluation** (licence check for derived tables used in QuantConnect, a one-month subscription, a read-only mapping and audit) **only if** you intend to continue research beyond slot 3. If slot 3 is the programme's last test, do not buy.

## 21. Exact owner decisions required next

1. **Acknowledge the frozen Amendment 3** (W2 critical value 2.15 with SE = max(iid, stationary bootstrap block 126); R2 tolerance 0.15; R1 10 points), or instruct a change **before** any hypothesis is chosen.
2. **Approve "event data v1"** (§19, rules 1–6) as a frozen component for any future earnings-event hypothesis. Approve the predecessor-linking rule and the foreign-issuer exclusion.
3. **Data extension:**
   - (a) authorise a time-boxed Sharadar evaluation: verify licence terms for derived tables inside QuantConnect; a one-month subscription (≈ $69) only after your explicit purchase approval; a read-only identity map and audit; or
   - (b) stay with 2010–2021.
4. **Slot 3:** keep it unused. After your decisions on 2–3, I will return with **one** pre-registered hypothesis (earnings-event continuation or value), whose parameters come from external evidence, with an account-model proposal for that family.
5. **No change** to the account model, the $4,000 reference minimum, or any closed result until then.

**STOP.** Only E981-01 (identifier export) was run on QuantConnect. Nothing else was run, no returns were computed, slot 3 is unused, and the Holdout is locked.
