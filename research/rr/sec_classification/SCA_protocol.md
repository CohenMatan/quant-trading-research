# SEC Classification Audit SCA-1 — frozen protocol (UR-1 option A)

**Decision:** D267 (owner, 2026-10-20), UR-1 option A of RR4 §2.5.

**Run:** E805-01 on host X805 v1.0. **Retry:** E805-02, only after a documented infrastructure failure, with identical code, settings and SEC object.

**Kind:** infrastructure, aggregate-only, 0 orders, no returns, no performance analysis.

**Frozen before the run.**
- This file, the host, `qr_sca`, the SEC builder and the offline evaluation rule are SHA-256-pinned in `qresearch.rr_sca`.
- The SEC reference object's SHA-256 is pinned there too, and the host refuses any other object.
- No definition, threshold or outcome rule changes after the run. A genuine defect: STOP, document, ask the owner.

## 1. Question

Does QuantConnect's vendor-market-cap universe (RR3 W1, the approved rule: US common, NYSE / Nasdaq / AMEX, PIT market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M) miss, in 2010–2021, US common stocks that independent public SEC data shows to be ≥ $2B? Does any such omission bias the universe's survivorship enough to matter?

This is measurement only. It **does not repair** any universe (no U-C), and no result of it changes the universe used later.

## 2. Inputs

### 2.1 SEC reference (independent, public)

`build_sca_sec.py` builds `data/sec_derived/sca_sec_v1.json` from the local SEC cache only:
- the XBRL RSS filing index;
- companyfacts;
- EntityPublicFloat frames.

It is uploaded once, unchanged, to the Object Store key `rr/sca_sec_v1.json` (owner-approved under D267; plain JSON; D257).

It contains no QuantConnect output and no identifier from any earlier extraction.

| Element | Rule |
|---|---|
| Registrants | 10-K / 10-Q XBRL filers 2009-06 … 2021-12 with a public float ≥ $0.5B in some frame 2009–2021. Excluded: non-common names or SICs (partnership / LLC / fund / ETF / trust forms; SIC 6726, 6770, 6792, 6221), blank-check names, investment-vehicle trusts (TRUST / FUND names under SIC 6700–6799 except REITs 6798, 6199, 6221) |
| Ticker evidence | Each XBRL instance prefix (upper case, without '.', '-'), valid from its first filing − 100 days to its last filing + 100 days. **Evidence, not proof** |
| Cover shares | The filing's own non-dimensional `EntityCommonStockSharesOutstanding` (one value), dated by the **filing date** |
| Public float | Non-dimensional `EntityPublicFloat` facts (as-of date, value), dated by the filing date. Unit errors are dropped: float / cover shares outside $0.10–$5,000 per share, or float > 100 × total assets when no share count exists |
| Last periodic filing | The last 10-K / 10-Q filing date in the index (SEC-side exits) |

### 2.2 In-cloud (generated in the run, never exported)

At every month-end session 2010-01 … 2021-11, every security QuantConnect passes to universe selection gives:
- its key and current ticker (`symbol.value`);
- its raw price;
- ADV20 (the harness rule);
- `has_fundamental_data`;
- the harness `is_us_common` test (no dated overrides);
- the vendor exchange code;
- the vendor market cap.

The run is 2009-11-02 … 2021-12-31, so ADV20 exists at the first point. Nothing from the Holdout is read.

## 3. Definitions at an audit point t (the month-end session; SEC data filed strictly before t)

### 3.1 QuantConnect category (exactly one per security)

| Code | Rule |
|---|---|
| I | ADV20 undefined, price < $5 or ADV20 < $5M (not liquid) |
| N | liquid, no fundamentals object |
| B | liquid, fundamentals, but not `is_us_common` **or** a blank exchange code (non-structural, incl. blank fields) |
| X | liquid, structural common, exchange code present but outside NYSE / Nasdaq / AMEX |
| M | liquid, structural common, listed, vendor market cap missing / 0 |
| A_lt | as M, vendor cap in (0, $2B) |
| **E** | as M, vendor cap ≥ $2B — **the vendor-eligible universe** (RR3's E) |

### 3.2 SEC values of registrant r at t

- **S_r(t):** cover shares from the latest filing filed before t, at most 200 days old.
- **F_r(t):** public float from the latest filing filed before t whose float as-of date is at most 456 days (~15 months) before t.

### 3.3 Matching (QuantConnect side generated in the run)

1. **Ticker:** the QuantConnect securities whose ticker equals one of r's valid prefixes at t.
   - Exactly one distinct security: matched.
   - More than one: **ambiguous**.
2. **Fingerprint** (only when step 1 did not match and S_r(t) exists): the securities in E or A_lt with |S_r(t) / (vendor cap / raw price) − 1| ≤ 2%.
   - Exactly one: matched.
   - More than one: multi, not matched.

### 3.4 SEC evidence for a matched registrant

Cap_r(t) = S_r(t) × the matched security's raw price.

| Evidence | Rule |
|---|---|
| **strong** | Cap_r(t) ≥ $2B **and** F_r(t) ≥ $2B **and** Cap_r(t) / F_r(t) ∈ [0.5, 10] (identity plausibility) |
| **weak** | otherwise Cap_r(t) ≥ $2B, or no Cap but F_r(t) ≥ $2B |
| none | otherwise (not SEC-eligible) |

Public float is only a **lower bound** of market cap. Float ≥ $2B therefore shows the company was ≥ $2B at the float's as-of date. It is not an exact substitute for market cap at t.

### 3.5 Audit classes

| Class | Rule |
|---|---|
| **Matched** | a registrant matched to an E security. The vendor universe contains it |
| **Confirmed missing** | a registrant with **strong** evidence matched to an M, N or B security: liquid, SEC-eligible, absent from E because data is missing |
| **Possible missing** | the same with **weak** evidence |
| **Unresolved** | a registrant with F_r(t) ≥ $2B and no match (no ticker, ambiguous, no unique fingerprint). **Not proof of absence:** it may be in E under another ticker, or not listed in QuantConnect's US equities at all |

Reported but **not missing**:
- A_lt (the vendor's own PIT cap is below $2B: the approved rule's definition, a disagreement);
- X (other exchange: legitimately excluded);
- I (illiquid: legitimately excluded);
- matched securities without SEC evidence.

Unresolved registrants with only a weak float are counted separately and not used.

A QuantConnect security matched by several registrants counts once per point, in the best class (matched > confirmed > possible).

## 4. Measures (per calendar year y; stock-months)

**Gaps:**
- Gap_C = C / (E + C)
- Gap_CP = (C + P) / (E + C + P)
- **Gap_max** = (C + P + U) / (E + C + P + U)

Here E = all E stock-months, C = confirmed, P = possible and U = unresolved registrant-months.

**Survivorship, QuantConnect side** (as UB-1):
- Exit = the security's last day in the run before call(t) + h months.
- h = 24 months, or 12 where 24 is not assessable. Follow-up is censored at the run's last selection; 2021 is unassessable.
- b_C = e(E ∪ C) − e(E); b_CP = e(E ∪ C ∪ P) − e(E).
- 95% interval by bootstrap over securities, B = 1,000, seed 20261020.

**Survivorship, SEC side, for the unresolved:**
- Exit = the registrant's last 10-K / 10-Q filed before call(t) + h.
- Assessable only if call(t) + h ≤ 2021-12-31 − 150 days.
- b_U = e(E-matched ∪ U) − e(E-matched), with exits of both groups on the same SEC definition. Bootstrap over registrants.

**Instrument checks** (per year):
- **reach:** E-matched / E;
- **agreement:** among ticker-matched E securities with an SEC cap, the share with Cap ≥ $2B;
- also the shares within 5% and within 2× of the vendor cap.

## 5. Interpretation rule (frozen; per year, then per window)

Thresholds are those of RR3 / UB-1: coverage 3%; survivorship 0.50 points at h = 24, 0.25 points at h = 12.

| Year verdict | Rule |
|---|---|
| **FAIL** | Gap_C > 3%, **or** the point estimate of b_C > the survivorship threshold |
| **PASS** | not FAIL, **and** Gap_max ≤ 3%, **and** (upper bound of b_CP + max(0, upper bound of b_U)) ≤ the threshold (or survivorship unassessable: listed), **and** reach ≥ 80%, **and** agreement ≥ 95% |
| **INCONCLUSIVE** | anything else |

**Window W1 2010-01 … 2021-11:**
- FAIL if any year is FAIL;
- PASS if every year is PASS;
- else INCONCLUSIVE.

**Windows W1a 2011-01 … 2021-11 and W1b 2016-01 … 2021-11:** the same rule, **reported for the owner only**. Neither is a decision, and no option B, C or D follows from either automatically.
- W1a is added before the run for a known instrument limit: XBRL started for large accelerated filers with float of $2–5B only with periods after 2010-06-15. Before mid-2010 the SEC reference therefore has no ticker evidence or cover shares for many ≥ $2B companies (measured on the SEC side only: 1,262 registrants with valid ticker evidence on 2010-06-30, against 2,769 on 2013-06-30), and 2010's reach can fall below 80%.
- W1b is the sub-window RR4 §2.6 option B referred to.

**Owner-facing rules (D267):**
- Every outcome STOPS for owner review.
- INCONCLUSIVE or FAIL means the universe-bias risk is **not** shown to be acceptably bounded.
- Ticker-matching failures are never read as absence.
- A QuantConnect compliance refusal of the code or the object STOPS the audit, with no workaround.

## 6. Exported aggregates

- **Per year:** counts of every category and class; securities and registrants; Gap_C / Gap_CP / Gap_max; b_C / b_CP / b_U with intervals and exit-rate differences; instrument counters; the verdict and its reasons.
- **Per window:** the outcome.
- **Run:** checks, audit points, the SEC object's SHA-256, and a digest of the monthly E counts.
- **Excluded:** no identifier, ticker, CIK, per-security value, price or return.

## 7. What this run does not do

- No strategy, order, return or performance figure. No U-C, repair or change to any universe.
- No Holdout data (the run ends 2021-12-31). No change to any frozen experiment.

## 8. Known limits (stated before the run)

- Registrants below the $0.5B float screen and non-XBRL filers are outside the SEC list. The SEC list is a subset, so C and P are lower bounds; U partly compensates.
- Multi-class registrants often have no single cover-share count: no SEC cap, so weak evidence at most.
- Ticker evidence uses filings up to 100 days after t (identity evidence, not a signal).
- One data snapshot (RR1 R5–R6): the E counts are compared with E804-01 as a snapshot check, reported only.
