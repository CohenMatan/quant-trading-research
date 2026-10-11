# H025 — Insider Cluster Buying: frozen pre-registration (v1)

Owner decision **D204** (`docs/owner/2026-10-11_p10cp1_h025_insider_cluster.md`). This file is hash-pinned in
`qresearch.p10h025` (with the code that implements it) BEFORE any SEC event count, eligibility state, null world or
return exists. Nothing in it may change after a result is seen; any altered definition is H026 or later and needs a
separate owner decision.

## 1. Status, question and periods

* H025 is an EVENT study, not a Score model: no Score v1 / v2 / v3, no H024 feature, no momentum, LOWVOL, REV1M or
  valuation input is used anywhere.
* Question: when at least two distinct corporate insiders (directors and / or officers) buy meaningful amounts of their
  company's common stock in the open market and the purchases become public within ten calendar days, does the stock
  outperform SPY over the following 20 trading sessions?
* **2011–2017 = H025 DEVELOPMENT / TRAINING.** No price after 2017-12-29 is requested (the last session of 2017).
* **2018–2021 = H025-SPECIFIC OOS VALIDATION, NOT PROGRAMME-WIDE PRISTINE HOLDOUT.** It has not been used to design
  H025, but earlier unrelated hypotheses used parts of it (H005 Validation E005-28; Phase 2 H014 / H016 / H017
  development 2010–2021). It is not accessed in this checkpoint.
* **Holdout 2022-01-01 → 2026-08-31: untouched.**

## 2. SEC sources (public, official; nothing purchased)

* **SEC Insider Transactions Data Sets** (Division of Economic and Risk Analysis): quarterly zips
  `https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/{YYYY}q{Q}_form345.zip`, quarters
  2010Q4 … 2017Q4 (29 files; 2010Q4 only so that clusters and cooldowns already running at 2011-02-01 are known). They
  hold every Form 3 / 4 / 5 XML filing of the quarter: SUBMISSION (accession, filing date, document type, issuer CIK,
  issuer name, issuer trading symbol as filed), REPORTINGOWNER (owner CIK, owner name, relationship
  Director / Officer / TenPercentOwner / Other, officer title), NONDERIV_TRANS (security title, transaction date,
  transaction code, shares, price per share, acquired / disposed code, direct / indirect ownership).
* **EDGAR filing header** `https://www.sec.gov/Archives/edgar/data/{issuer CIK}/{accession without dashes}/{accession}.hdr.sgml`
  (if absent, the same path under the reporting owner's CIK): `ACCEPTANCE-DATETIME` = the time the SEC accepted the
  filing (US Eastern wall-clock time; identical to the "Accepted" time on the EDGAR filing index page), `TYPE`,
  `FILING-DATE`.
* Retrieval: `research/phase10/h025_ledger.py --fetch` with the project SEC client (`qresearch.sec_edgar`; contact
  address read at run time only, ≤ 8 requests per second), cached under `data/sec_cache` (outside Git; re-acquirable).
* QuantConnect is NOT a source of insider-event timing. It supplies only the frozen Data v2 universe, identity and
  prices (section 8–9).

## 3. Qualifying purchase lines (evaluated in this order; the first failing rule is the line's exclusion reason)

Only code-P non-derivative lines are read; every other code (A awards, M exercises, C conversions, G gifts, F tax
withholding, S sales, J other, …) and every derivative table line is excluded by construction.

1. `not_form4` — the filing's document type is not `4` (4/A amendments, Form 5 and 5/A never count).
2. `joint_filing` — the filing has more than one reporting owner (the purchase cannot be attributed to one insider).
3. `no_owner_cik` — the owner has no CIK.
4. `not_director_officer` — the relationship contains neither `Director` nor `Officer` (a 10% owner only, or Other,
   never counts; Director / Officer + 10% owner counts through the Director / Officer role).
5. `not_acquisition` — acquired / disposed code is not `A`.
6. `indirect` — ownership is not `D` (direct). Indirect purchases are counted only.
7. `title_not_common` — the lower-cased security title does not match `common|ordinary|capital stock|\bshares?\b`, or
   matches `prefer|\bpref\b|depositary|\bads\b|\badr\b|warrant|right|option|\bnotes?\b|debenture|convertible|\bunits?\b|
   partner|401\s*\(?k|\bfund\b|\bplan\b|phantom|deferred`.
8. `missing_price` — price per share missing or ≤ 0.
9. `missing_shares` — shares missing or ≤ 0.
10. `no_issuer_cik` — the submission has no issuer CIK.

A line passing all ten is qualifying; its value = shares × price. A **qualifying filing** is an original Form 4 with at
least one qualifying line; its value = the sum over its qualifying lines (other lines of the same filing are ignored).

## 4. SEC timing rule

* Information arrives at the filing's SEC acceptance timestamp (Eastern, from the EDGAR header). Never the transaction
  date, never the filing date alone.
* A qualifying filing is usable only if (else excluded, with the reason counted): the header exists
  (`header_missing`); it carries an acceptance timestamp (`acceptance_missing`) with a time of day other than
  00:00:00 (`acceptance_no_time`); its TYPE is `4` (`header_form_mismatch`); its FILING-DATE equals the data set's
  filing date (`header_date_mismatch`); the acceptance date lies in [filing date − 7 days, filing date]
  (`acceptance_outside_filing_date`; Section 16 forms accepted after 22:00 ET carry the next business day's filing
  date); every qualifying line's transaction date exists and is ≤ the acceptance date (`transaction_date_invalid`).
* No fallback is used: a filing without a reliable acceptance timestamp is excluded.
* Headers are fetched for a SUPERSET of the filings that can matter: per issuer, a filing whose filing date lies within
  17 days (10-day window + 7-day lag slack) of a qualifying filing by another owner, or whose owner's qualifying filings
  within 17 days total ≥ $100,000 (single-insider control). The 7-day bound is verified on every fetched header.

## 5. Cluster definition (online)

* Distinct insiders = distinct reporting-owner CIKs; several filings by one owner add up and count once.
* Filings of one issuer (Form 4 issuer CIK) are processed in order of acceptance timestamp (ties: accession). At each
  filing f with acceptance t, the window = the issuer's usable qualifying filings with acceptance ≤ (t, accession of
  f) and acceptance calendar date ≥ date(t) − 9 days (10 calendar days, by public availability).
* Per owner: window aggregate = sum of its filings' values in the window. Qualifying insiders = owners with aggregate
  ≥ **$25,000**. Cluster aggregate = sum over the qualifying insiders.
* A **cluster event triggers at t** when there are ≥ **2** qualifying insiders and the cluster aggregate ≥
  **$100,000**: trigger timestamp = t (the acceptance that completes the cluster). It is never moved earlier.
* Its insiders, accessions, values and classification are those of the window AT t. Later qualifying filings within
  ten days are recorded descriptively (`later_accessions`) and change nothing.
* **Cooldown:** a trigger whose entry session index is < the issuer's previous cluster event's entry session index +
  **20** is suppressed (no event). The cooldown runs on the SEC ledger of every issuer before any universe filter
  (an ineligible event still starts a cooldown), by issuer CIK.
* An independent brute-force implementation (every acceptance timestamp re-evaluated from scratch) must reproduce
  every trigger, entry and insider set exactly.

## 6. Calendar, entry, exit and window

* Sessions: LEAN trading sessions (committed `experiments/E976-04/equity.csv.gz`), verified again in-host against
  QuantConnect's own session list; nothing after 2017-12-29.
* **Entry session** = the first regular-session open strictly after the trigger: the trigger date itself if it is a
  session and the trigger is before 09:30 ET; otherwise the next session after the trigger date. Never intraday.
* **Exit** = the close of the 20th session counting the entry session as the first (entry index + 19).
* Development events: trigger date ≥ 2011-02-01 (the first Data v2 review, 2011-01-31, must be strictly earlier) and
  exit session ≤ 2017-12-29 (`window_status` = `in_window`; else `before_window` / `exit_after_2017`).

## 7. Event ledger

`research/phase10/ledger/h025_sec_ledger.csv.gz` (SEC side; built offline, no price or return column):
event_id, kind (`cluster`, or `single` for the diagnostic control), issuer CIK, symbol as filed, trigger timestamp,
trigger date, entry session, exit session, window status, insider count, insider CIKs, names, roles (D / O / T, C =
CEO / CFO title), per-insider values, cluster value, CEO / CFO flag, director-only flag, number of qualifying filings
and purchase lines, accessions, acceptance timestamps, transaction dates, shares, prices, line values, median filing
delay, later accessions, near-cluster flag. The in-host part (section 8: review date, security id, eligibility result,
identity status, exclusion reason, FF12, market-cap quintile) is exported by the no-return audit run and joined
offline; **EVENT_LEDGER_SHA256** = SHA-256 of the joined ledger (`research/phase10/ledger/h025_event_ledger.csv`),
pinned before any return is attached.

## 8. Universe and identity (in-host, frozen Data v2)

* Review = the latest Data v2 monthly review date strictly before the trigger date. Eligible = the frozen Data v2
  eligible set of that review (US common stock, NYSE / Nasdaq, PIT market cap ≥ $2B — QuantConnect's, else the D111
  SEC market cap — price ≥ $5, ADV20 ≥ $5M; financials included). No later review is ever used.
* Identity: the issuer CIK must equal the Data v2 verified identity CIK of an eligible security at the review
  (`qr_v2.Identity.m2`: identity-v2 dated rows, else a verified SAFE / BOUNDED extension row while feed presence is
  continuous). Status:
  * `ELIGIBLE` — exactly one eligible security carries the CIK;
  * `ELIGIBLE_MULTICLASS` — several do (share classes): the one with the highest ADV20 at the review (ties: smallest
    security id);
  * `IDENTITY_UNRESOLVED` — none carries the CIK, but an eligible security WITHOUT a verified identity carries the
    as-filed symbol: possible identity gap, excluded and reported (the symbol is never used to map);
  * `NOT_ELIGIBLE` — otherwise (issuer outside the universe at the review).
* No modern ticker or name matching. All exclusions are reported.

## 9. Responses (only after the ledger hash is pinned)

* Panel: the frozen Data v2 panel (RAW open / close, verified split × dividend multiplier M, unverified-split rows).
* Stock TSR over [e0 = entry row, x0 = e0 + 19]: entry = the first row in [e0, x0] with a valid open and close; exit =
  the close of x0, else the last real close (delisting / halt; cash afterwards); TSR = C[x]·M[x] / (O[e]·M[e]) − 1
  (`qr_p7_pred.response` conventions). No bar in the window, or an unverified split inside it → NaN (not evaluable,
  counted).
* SPY TSR: SPY RAW open / close with its split × dividend multiplier, bought at the open of the stock's entry row e and
  held to the close of x0.
* **Primary response = stock TSR − SPY TSR (20 sessions).** Win = excess > 0.
* Diagnostics (never gated): 5 / 10 / 40 / 60-session excess (x0 = e0 + h − 1; NaN when x0 is after 2017-12-29),
  raw stock TSR, sector-relative TSR (stock TSR − mean TSR of the other eligible same-FF12 securities at the review
  over the same window).

## 10. Statistic

* Monthly series: for each calendar month (of the trigger date) with ≥ 1 evaluable event, the mean primary excess of
  its events; months without events are omitted; ordered by month.
* t_EVENT = mean / Newey-West (Bartlett) standard error with **lag 2**. Each 20-session window ends at most ~29 calendar
  days after its month, so it overlaps only the next month's windows; lag 2 covers that overlap (decided before any
  return).

## 11. Matched null (5,000 worlds, before the real result)

* For every evaluable real event (same date, same window e0 … x0): candidates = the eligible securities at the
  event's review with a verified identity CIK at that review (unverified securities cannot be checked for H025
  events) and a finite primary response over the same window, excluding the event's security and any security with
  the issuer's CIK, and excluding ("blocked") any security that has an H025 cluster event of ANY window
  status in the SEC ledger (mapped by its verified CIK at the review) whose entry session is within 19 sessions of the
  event's entry session.
* Cell: FF12 (Data v2 SIC at the review) × market-cap quintile (average-rank quintile among the eligible securities
  of the review with a valid market cap). Hierarchy: **L1** same FF12 and quintile; **L2** same FF12, nearest quintile
  (distance 1, then 2, …; the lower quintile first at equal distance); **L3** same quintile, any sector; **L4** any
  candidate. Levels used are reported.
* World w (seeds 1 … 5,000): every event's excess is replaced by the excess of one candidate drawn uniformly from its
  pool (numpy PCG64 seeded with (w, 25)); the world statistic = t_EVENT of the resulting monthly series. Also recorded:
  mean, median, win rate (random-event control).
* **c_EVENT = max(the 50th largest null t of 5,000 (empirical one-sided 99th percentile; the `qr_xs.critical_value`
  convention), 2.326).**
* Determinism: a second complete null run must reproduce every world bit-for-bit (digest).
* Null failure (STOP): fewer than 5,000 worlds, a non-finite world statistic, a determinism mismatch, or a response
  panel digest differing between runs.
* Pinned before the real run: c_EVENT, the null result SHA-256, EVENT_LEDGER_SHA256, RESPONSE_PANEL_SHA256.

## 12. Gates (all required; evaluable primary events only)

| Gate | Requirement |
|---|---|
| G1 | t_EVENT > c_EVENT and mean event excess > 0 |
| G2 | mean 20-session SPY-relative excess ≥ +2.0% (not annualised) |
| G3 | median event excess > 0 and win rate > 50% |
| G4 | mean excess > 0 in 2011–2014 and in 2015–2017, and ≥ 5 of the 7 calendar years (trigger year) positive |
| G5 | ≥ 100 evaluable events and ≥ 5 calendar years with ≥ 10 events |

Feasibility gate (before any return, on the joined ledger): ≥ 100 in-window cluster events with status `ELIGIBLE` or
`ELIGIBLE_MULTICLASS`, and ≥ 5 calendar years with ≥ 10 such events; else STOP (H025 BLOCKED — SEC EVENT DATA /
SAMPLE INSUFFICIENT), definition unchanged.

Result: all five gates → **DEVELOPMENT CANDIDATE — H025 PASSED, VALIDATION NOT YET RUN** (freeze, STOP; 2018–2021
not accessed); any gate fails → **H025 REJECTED — NO ROBUST INSIDER-CLUSTER EDGE**.

## 13. Diagnostics (non-gating; reported after the gates; never a new primary)

2 vs 3+ insiders; cluster value $100K–250K / $250K–1M / > $1M; CEO / CFO involved vs not; director-only clusters;
number of qualifying filings 2 / 3 / 4+; median filing delay (acceptance date − earliest transaction date of each
qualifying filing) ≤ 2 / 3–5 / > 5 days; 5 / 10 / 40 / 60-session excess; raw TSR; sector-relative; results by year
and by half; the matched random-event control (null worlds' mean / median / win rate); the single-insider control.

**Single-insider control:** the same online machinery with kind `single`: triggers when exactly one owner has a window
aggregate ≥ $25,000 and that aggregate is ≥ $100,000 (own 20-session cooldown); excluded if a cluster event of the same
issuer has its entry within 19 sessions (`near_cluster`); same universe, identity, response and statistics. It is not
an alternative H025 specification.

## 14. Run order, provenance and STOP conditions

1 parser → 2 SEC ledger → 3 rules frozen (this file) → 4 no-return audit run (QuantConnect, eligibility / identity
only, no price read for responses) → 5 sample check → 6 independent rebuild (offline brute force + a second audit run)
→ 7 pin EVENT_LEDGER_SHA256 → 8 canary (synthetic returns only) → 9 response / null machinery (real responses never
summarised) → 10 5,000 null worlds + identical rerun → 11 pin c_EVENT → 12 ONE real evaluation → 13 G1–G5 →
14 diagnostics → 15 STOP. Every QuantConnect run: S027 on frozen Data v2, default build (digest verified), 0 orders,
aggregates and event-level derived values only, no logs.

STOP without weakening the hypothesis if: SEC timing cannot be made PIT-safe; identity mapping is unreliable; the
sample is below the minimum; the null calibration fails; determinism fails; or the real H025 fails any gate.

## 15. Not allowed

Any re-definition after results (5-day window, 3 insiders, $50K, $250K, indirect ownership, 10% owners, other holds);
combining with any score or feature; any portfolio statistic (CAGR, wealth, Sharpe, drawdown, sizing, concurrency,
turnover); any 2018+ price; the Holdout; any purchase.

## 16. Future H025 validation (pre-registered concept; NOT authorised)

Only if H025 passes G1–G5 and the owner approves: build a PIT-safe 2018–2021 SEC event ledger and response panel with
IDENTICAL rules, freeze both, run a fresh 5,000-world matched null, pin c_EVENT_VALIDATION, then ONE real mapping.
V1 t > c_EVENT_VALIDATION and mean > 0; V2 mean ≥ +2.0%; V3 median > 0 and win rate > 50%; V4 2018–2019 and
2020–2021 means > 0; V5 ≥ 50 evaluable events and ≥ 10 in each of the four years. All must pass. The Holdout stays
closed regardless.
