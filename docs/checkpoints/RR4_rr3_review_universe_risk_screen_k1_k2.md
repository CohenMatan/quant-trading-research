# RR4 — RR3 review: universe risk, frozen-ready screen, K1 / K2 feasibility

**Date:** 2026-10-20.
**Decisions:**
- D265: owner direction, verbatim in `docs/owner/2026-10-20_rr3_review_next_research_preparation.md`.
- D266: this checkpoint.

**Status:** **STOPPED awaiting the owner.** Offline documentation and arithmetic only.

**Not done:**
- No QuantConnect run, upload or export. No strategy backtest. No hypothesis registered (no H031).
- No purchase or subscription. No Holdout access. No frozen experiment changed. U-C not implemented.

**Programme totals (unchanged):** 30 hypothesis IDs; 30 research strategy folders; 415 experiment IDs (582 run records).

## 0. Summary

| Item | Verdict |
|---|---|
| RR3 decisions | Recorded as accepted: W1 PASS-A for the measured population only; W0 FAIL; U-B retired (§1) |
| **Universe blind spots** | **Not harmless, and not resolvable offline.** Our own committed universe counts imply that E804 misses about 3–6% of eligible stock-months a year in 2011–2015 that RR3 could not see. The missing names are mostly companies that later disappeared. Under a scenario consistent with all the evidence, 2011–2015 would fail RR3's 3% coverage gate. From 2016 the bound is ≤ 2% (§2). **Owner decision UR-1 needed** |
| Screen and confirmation | P1–P6 kept unchanged. One stage added before any result: because there is no independent historical period, Amendment 3's evidence test (W2) must be passed on development data before the Holdout. The Holdout is then a one-time falsification check, followed by 36 months of forward tracking (§3) |
| **K1** dividend-event drift | **Conditionally feasible.** Events are visible at the ex-date with no announcement look-ahead. There are enough events for 15 slots. Spin-offs, specials and cent-rounding need pre-set filters. The prior is weak (§4.1) |
| **K2** market-trend exposure control | **Not feasible as a broad-market strategy under the current rules.** The only rule-compliant form is a 15-stock basket with a trend switch, which is not broad-market and has very low power. Recommendation: do not register K2 (§4.2) |
| To the first legitimate experiment | About 3–4 sessions and 2–3 aggregate-only cloud runs after your decisions (§5) |

## 1. RR3 decisions and limitations (as accepted under D265)

1. **W1 2010–2021 = PASS-A** for the measured, structurally classified population only. It is not proof that every eligible security was included. Every future report repeats:
   - the missing-cap residue;
   - the no-fundamentals population;
   - blank classification fields;
   - 2021 survivorship not assessable;
   - build and dataset instability.
2. **W0 1999–2009 = FAIL.**
   - No D033 / D035 amendment.
   - The Holdout stays sealed.
   - Confirmation has no independent historical period (handled in §3).
3. **U-B retired.** Its failure evidence stays in RR3 §3 and `UB_result_E804-01.json` and is not used anywhere.

## 2. Remaining universe risk (offline assessment)

### 2.1 Method

- **Inputs:** committed aggregates only, all for the same universe rule (US common, NYSE / Nasdaq / AMEX, PIT cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M, month-end):
  - **E804** (RR3, build 18194): vendor market cap only.
  - **Data v1** (E993-02, old dataset plus our SEC correction layer). Its residual gap was measured against SEC filings at 0.5–1.2% a year (P2-CP7). It is the closest thing we have to a complete reference, but only for 2011–2017.
  - **E996-01** (build 18178): the reason each Data v1 member was missing on the new feed (P7-CP5d).
  - **Data v2 / v2.1** (E998-01 / E801-01, build 18178): vendor cap plus SEC market-cap repairs, 2011–2021.
- **Script:** `research/rr/universe_risk/RR4_universe_reconciliation.py` → `.json`. Arithmetic on these aggregates; no network.
- **Not used:** no QuantConnect export, no identifier, no cloud run.

### 2.2 Reconciliation (stock-months a year)

"Not measured" = Data v1 − E804 − E804's own missing-cap names (M). These are names RR3 could not see: no fundamentals object, blank fields, cap below $2B on the new vendor data, or no dated override.

| Year | Data v1 | E804 | E804 short by (net) | RR3 measured (M) | **Not measured by RR3** | No-fundamentals group on 18178 | Gap_A (RR3) | **Gap if that group is still missing (S1)** |
|---|---|---|---|---|---|---|---|---|
| 2011 | 11,069 | 10,112 | 957 (8.6%) | 276 | **681 (6.2%)** | 400 | 1.8% | **5.5%** |
| 2012 | 11,182 | 10,379 | 803 (7.2%) | 256 | **547 (4.9%)** | 378 | 1.7% | **5.1%** |
| 2013 | 12,860 | 12,062 | 798 (6.2%) | 256 | **542 (4.2%)** | 416 | 1.5% | **4.7%** |
| 2014 | 14,380 | 13,570 | 810 (5.6%) | 261 | **549 (3.8%)** | 445 | 1.3% | **4.4%** |
| 2015 | 14,667 | 13,991 | 676 (4.6%) | 290 | **386 (2.6%)** | 339 | 1.2% | **3.5%** |
| 2016 | 14,156 | 13,721 | 435 (3.1%) | 174 | 261 (1.8%) | 192 | 0.7% | 2.0% |
| 2017 | 15,373 | 14,938 | 435 (2.8%) | 169 | 266 (1.7%) | 42 | 0.6% | 0.9% |
| **2011–17** | **93,687** | **88,773** | **4,914 (5.2%)** | **1,682** | **3,232 (3.4%)** | **2,212** | | |

**2018–2021:** there is no Data v1 reference.
- E804 is 1.3%, 1.7%, 2.0% and 2.3% short of Data v2.1.
- Data v2.1 itself never had the no-fundamentals group, so these figures are lower bounds.

### 2.3 What this means

1. **RR3 measured about one third of the shortfall.** It measured 1,682 of 4,914 net stock-months in 2011–2017. The rest sits in the categories RR3 disclosed as unmeasured.
2. **The no-fundamentals group is a known, survivorship-skewed set.**
   - On build 18178, 2,212 Data v1 stock-months had no fundamentals object: 68 securities.
   - **67 of them later disappeared from the universe.**
   - Our SEC repair could not recover any of them (P7-CP5e).
   - Whether today's build 18194 still lacks them cannot be established offline. The net shortfall above is larger than the no-fundamentals group, so the data are consistent with the group still being missing.
3. **Effect on the frozen gates, if the group is still missing (S1):**
   - **Coverage:** 2011–2015 would exceed the 3% gate (5.5 / 5.1 / 4.7 / 4.4 / 3.5%).
   - **Survivorship:** the excess 24-month exit rate needed to break the 0.50-point bias gate is 13–16 points (2011–2014) and 21 points (2015). E's own exit rate is 3–8%. A group that almost entirely disappeared later could plausibly exceed that, but it is not measured.
   - **From 2016 the bound is small:** S1 ≤ 2.0%; 2018–2021 1.3–2.3% (lower bound).
4. **Return effect: direction unknown.** Many of these companies were acquired (acquisition premiums), and others declined. Without returns, the sign of the bias cannot be set.

**Limits of this reading:**
- All comparisons are net: names only E804 has offset names only Data v1 has.
- Data v1 used the old vendor's market caps.
- Boundary flips around $2B occur in both directions. On 18178 they roughly offset: 131–221 Data v1-only against 218–386 new-only a year.
- **A count-only SEC cross-check is inconclusive.** The number of SEC registrants with public float ≥ $2B is 75–92% of E804's monthly count. Float is below market cap by a varying amount, so a gap of 2–5% cannot be resolved that way.

### 2.4 What can and cannot be established without exporting Platform Data or new runs

| Question | Offline? |
|---|---|
| Size of the potentially hidden population | **Yes, bounded** (§2.2): about 2–6% a year in 2011–2015, ≤ 2% from 2016 |
| Its survivorship character | **Partly:** 67 of 68 known securities later disappeared (aggregate from P7-CP5e). Their 24-month exit rate is not available |
| Whether those names are still missing on today's build | **No.** It needs today's identifiers, which may only be generated in-cloud (D257) |
| Classification of today's no-fundamentals and blank-field names | **No.** Exporting their identifiers would be a Platform Data export |

### 2.5 A narrow free SEC classification check: feasible, not implemented

- **Design (measure only, no repair):**
  - Build a plain JSON list from our cached public SEC data: registrants whose public float or cover-share market cap is ≥ $2B, by month, with dated ticker evidence (the existing Phase 2 identity code).
  - Upload it to the Object Store. Support confirmed SEC JSON is allowed there (D257).
  - In-cloud, match it by ticker and date to the universe objects. Count, per year, how many SEC ≥ $2B companies fall in E804's E / below-$2B / missing-cap / no-fundamentals / blank-field / not-found groups, with their 24-month exit rates.
  - Export aggregates only.
- **Effort:** about 1.5–2 sessions; 1 run plus at most 1 retry; $0.
- **Risks:**
  - QuantConnect's compliance review refused one earlier validation export (E995-05). Similar aggregate-only audits were accepted (X996, X997, X804). A refusal would STOP the check.
  - Ticker-only matching misses some names, so the result is a lower bound.
  - Float ≤ market cap, so the SEC list is a subset.
  - It covers 2010–2021 only. The Holdout years can be measured only when the Holdout is opened (§3).
- It is a measurement of the gap, not U-C, and does not repair the universe.

### 2.6 Owner decision UR-1: how to treat the blind spot

| Option | What | Cost | Consequence |
|---|---|---|---|
| **A (recommended)** | Approve the §2.5 check: one SEC JSON upload and one aggregate-only run | 1.5–2 sessions, $0 | If the gap is ≤ 3% with no survivorship skew, 2010–2021 stays the development window. Otherwise go to B. A compliance refusal also leads to B |
| B | Start the development window on 2016-01-04 (bound ≤ 2%) | none | 6 years instead of 12. The edge needed for a 50% pass rises from ≈ 6% to roughly 9% a year |
| C | Keep 2010–2021 and accept the residual with disclosure | none | A survivorship bias of unknown sign in half the window. **Not recommended**: you asked not to accept the bias by default |
| D | U-C repair | 3–5 sessions | It cannot recover names with no SEC identity. Out of scope under D265 |

## 3. Candidate screen and confirmation (ready to freeze)

The full text is in `research/rr/programme/RR_screen_confirmation_PROPOSED.md`, written before any RR strategy exists. On your approval it is frozen and its hash pinned.

| Stage | Rule | Label |
|---|---|---|
| D1 Promising | **P1–P6 unchanged** (RR2): wealth > SPY; g/SE ≥ 1.0; beats the equal-weight control and 4 of 5 random controls; no two-year block > 50% of the excess; holds at 20 bps; up-capture ≥ 0.85 or down-capture ≤ 0.85 | DEVELOPMENT — EXPOSED |
| **D2 Development-qualified (new)** | Amendment 3 §3 in full (W1, W2 2.15 × SE, W3, R1–R4, G4′), with Holm across the tranche: z thresholds 2.15 / 2.41 / 2.57 for tranche sizes 1 / 2 / 3 | DEVELOPMENT — EXPOSED |
| C1 Holdout, once | At most 1 candidate per tranche, written CP5 approval. Amendment 3 §4 unchanged: beats SPY; drawdown ≤ SPY's + 10 points; a defensive or timing strategy must also beat SPY in 2023–2026 alone. The universe audit is computed in the same run | HOLDOUT — NOT FALSIFIED |
| C2 Forward | Reviews at +12 / +24 / +36 months after the freeze. +36 is decisive | FORWARD — TRACKED |

**Why D2 (justified before any result):**
- RR2 put the strict evidence test on a 1999–2009 confirmation window that does not exist.
- Amendment 3's Holdout gates test wealth and drawdown only. Over 4.7 years a candidate with no edge beats SPY about half the time.
- Without D2, nothing in the chain tests the strength of the evidence.

**Honest power:** the full Amendment 3 framework passes half the time only at a true edge of about 6% a year (12 years; about 9% a year if option B is chosen). A "Production Candidate" needs D1, D2, C1, the +36-month review and a separate owner decision.

## 4. K1 and K2 feasibility (no hypothesis registered)

### 4.1 K1 dividend-event drift: CONDITIONALLY FEASIBLE

| Check | Finding |
|---|---|
| Point-in-time availability | QuantConnect delivers a dividend in a corporate-action slice at midnight on the **ex-date**, before that day's bars (`qr_harness`, the "corporate-action-only slice"; to be confirmed by the event canary). The declaration date is not in the feed |
| Announcement vs ex-date | The signal can only use the ex-date. That is typically 2–4 weeks after the declaration, which is already public, so there is **no look-ahead**, but the signal is late. The literature's drift is measured from the announcement, and the announcement-day reaction is already in the price |
| Mechanical ex-dividend drop | Entry at the first open **after** the ex-date: the price drop has already happened. Signals use distribution amounts, not prices. Returns are total return (later dividends are credited as cash; fills at raw prices). A pre-set in-run check counts any order dated on or before its event's ex-date (must be 0) |
| Feed hazards (pre-set filters needed) | Spin-offs arrive unlabelled as dividends (D145): exclude distribution / reference price > 10%. Specials and frequency changes: compare only with the previous regular distribution at the same cadence. Cent rounding (D162): previous dividend ≥ $0.05, increase ≥ 25% |
| Event frequency | Estimated from cached public SEC XBRL (`research/rr/k1k2/RR4_k1_event_frequency.py`), among ≥ $2B-float companies 2011–2021. These are lower bounds (fourth quarters mostly untagged; an estimated 60–70% of payers tag a quarterly dividend per share): increases ≥ 10% ≈ 143 a year; ≥ 25% ≈ 60 (32–78); ≥ 50% ≈ 35; initiations ≈ 29 (8–49, noisy) |
| 15-slot capacity | ≥ 25% increases plus initiations ≈ 89 events a year (lower bound). That gives ≈ 22 concurrent events with a 63-session hold and ≈ 44 with 126. Slots fill most of the time; a pre-set queue rule is needed (first-come, then largest increase). 2020 is thin (32 increases) |
| Constraints and costs | 15 × $5,667 slots (15% reserve). Every slot ≥ $5,000 and ≤ 10%. One round trip ≈ $14 commission + $11 slippage ≈ 0.45% of the slot. 63-session holds with full slots: ≈ 60 round trips ≈ 1.5% a year, at the R4 limit. 126-session holds: ≈ 0.8% a year. **A hold of 126 sessions or longer fits the cost model** |
| Prior | Weak and contested. Michaely, Thaler & Womack (1995) found drift after initiations; Boehme & Sorescu (2002) found initiation drift not robust to method; Benartzi, Michaely & Thaler (1997) found that dividend increases do not predict future earnings growth. Large caps after 2000 are not well studied. Expect "no candidate" |

**Before freezing K1:**
1. Write the H031 specification: event definitions, filters, a 126-session hold, the queue rule, and controls (random dividend-paying stocks without an event, on the same dates).
2. Run one aggregate-only **event canary**: per-year counts by event class, filter hits, cadence-detection outcomes and the in-run timing check. No returns. It needs your run approval.

### 4.2 K2 market-trend exposure control: NOT FEASIBLE AS A BROAD-MARKET STRATEGY

| Check | Finding |
|---|---|
| Broad equal-weight universe | 757–1,628 eligible names a month. At most 15 positions with a $5,000 minimum means at most 2% of the universe is held. **Infeasible** |
| SPY ↔ cash (the textbook form) | ETFs are outside the stock-only universe (the ETF rule OD-1 was approved for SYS-1 only). A single holding is capped at a 10% initial allocation. **Needs two rule exceptions** |
| Rule-compliant form (K2-15) | A 15-stock equal-weight basket (for example the 15 largest) plus an SPY trend switch. Mechanically feasible: $5,667 per slot. But it is not broad-market: a random 20-stock book has ≈ 9.8% a year tracking error vs SPY (Amendment 3 calibration). Any result would mix selection noise with the timing effect |
| Cost model | A full switch out and back is 30 orders: ≈ $210 commission + ≈ $170 slippage ≈ 0.4% of the account. Five round trips a year would use about 2%, above R4's 1.5% |
| Evaluation | Amendment 3's defensive exception requires a market-timing strategy to beat SPY over 2023–2026 alone. 2010–2021 has only two short drawdowns, so development power is very low |

**Recommendation:** do not register K2. Its intended form (broad market exposure with cash) needs ETF and single-holding exceptions, which are scope decisions for you. Even then, the trend switch on SPY is a heavily published rule with low development power. If you keep K1 alone, tranche 1 has m = 1, so the W2 threshold stays at 2.15.

## 5. Minimum actions before the first legitimate strategy experiment

| # | Action | Who / cost |
|---|---|---|
| 1 | Decisions: **UR-1** (A / B / C / D); approve or amend the screen protocol (§3); K1 go / no-go; K2 dropped | Owner |
| 2 | If UR-1 = A: SEC JSON, X805 host, one aggregate-only run, short report | 1.5–2 sessions, 1 run, $0 |
| 3 | Freeze the screen protocol (hash pin + test) | 0.25 session |
| 4 | Engine hygiene: re-key the 12 dated overrides by ticker + date (resolved in-cloud); digest check in the host (the upload guard already exists, RR3) | 0.5 session |
| 5 | Evaluation module `qr_rp_eval` (in-host SPY shadow, equal-weight and random controls, W2, capture, blocks, cost replay → scalars) with offline tests bit-identical to `qresearch.wealth` | 1 session |
| 6 | H031 = K1 specification for your approval, then frozen | 0.5 session |
| 7 | K1 event canary (aggregate only, no returns) | 1 run |
| 8 | First strategy run (H031 primary), only on your explicit authorisation | 1 run |

**Total before step 8:** about 3–4 sessions and 2–3 aggregate-only runs. QuantConnect stays at $24 a month; the Object Store is $0. Nothing has started.

## 6. Owner decisions requested

1. **UR-1:** A, B, C or D (§2.6). Recommended: A.
2. Approve the screen and confirmation rules for freezing (§3), including the new D2 stage, or ask for changes.
3. K1: approve the H031 write-up and event canary (§4.1), or stop.
4. K2: confirm it is dropped, or decide the ETF and single-holding exceptions (§4.2).
