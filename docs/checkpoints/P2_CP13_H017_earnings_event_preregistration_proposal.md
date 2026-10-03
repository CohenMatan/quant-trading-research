# P2-CP13 — H017 earnings-event continuation: pre-registration proposal (STOP)

- **Date:** 2026-10-03.
- **Status: PROPOSAL ONLY.**
  - S017 not implemented; H017 not run.
  - No post-event, reaction, factor or strategy return computed; no threshold or holding period tested.
  - Holdout untouched; nothing purchased; **Phase 2 slot 3 unused**.
  - **STOP:** awaiting the owner.
- **Files:**

  | Topic | File | Notes |
  |---|---|---|
  | Hypothesis | `research/hypotheses/H017.md` | The exact proposed rules |
  | Literature | `research/phase2/h017/H017_literature_review.md` | Evidence for each design choice |
  | Event frequency, slot occupancy, turnover, costs | `research/phase2/h017/h017_capacity_sim.py/.json` | Event **timing** metadata and the frozen cost model only; no prices |
  | Gate operating characteristics | `research/phase2/h017/h017_power.py/.json` | Completed control books only |
  | Earlier Value draft | `research/hypotheses/H017_value_draft_withdrawn.md` | Kept for the record |

## Summary

**H017 rules:**
- **Signal:** buy stocks whose **two-session, SPY-adjusted reaction** to a verified SEC earnings release is in the **top decile** of the trailing year's reactions.
- **Timing:** enter at the open two sessions after the event session; hold exactly **60 sessions**; no other exit.
- **Portfolio:** **10 slots** of about $9,800; signals ranked by reaction when slots are scarce; extra signals dropped.
- **Controls:** SPY, the same-universe EW, and five random-event books matched day by day to the candidate's number of signals.
- **Data:** existing data only (Event Data v1, QuantConnect prices); no analyst estimates, no volume filter.

**Mechanics (no prices used):**

| Item | Value |
|---|---|
| Eligible events | ≈ 4,500 a year |
| Qualifying signals | ≈ 450 a year |
| Entries | ≈ 40 a year |
| Invested | ≈ 90% |
| Costs at $100K | **≈ 1.36% a year** (1.05% at $200K), within the 1.5% cap. 20 slots would break the cap (≈ 2.0%) |

**Honest outlook:**
- The best post-2005 large-cap evidence says this drift has largely disappeared (Martineau 2022).
- Costs (≈ 1.4% a year) plus cash drag (≈ 10% uninvested) set a structural hurdle of roughly **2.5–3% a year** before the strategy can even tie SPY.
- With 10 positions on 12 years:

  | True edge over SPY | Qualifies under frozen Amendment 3 | Qualifies or "Promising but Not Qualified" |
  |---|---|---|
  | +3% a year | 4% | 18% |
  | +5% a year | 12% | 37% |

- **This is the cleanest available test of a genuinely different mechanism using data we already have, not a likely winner.**

## 1. Current state

| Item | State |
|---|---|
| H014, H016 | Rejected (H016 preserved exactly as tested) |
| Phase 2 slots | 2 of 3 consumed; **slot 3 unused** |
| Holdout | Locked |
| Amendment 3 | Frozen (D121; hash-pinned) |
| Event Data v1 | Approved for use (owner 2026-10-03; P2-CP12 §19 rules) |
| Additional data | **None purchased.** Owner decision: no subscription until a strategy shows a sufficiently promising result on existing data |

## 2. Economic hypothesis

- **Claim:** investors under-react to earnings news. When the market's first two sessions of reaction to a verified earnings release are strongly positive, prices keep drifting up for about one quarter.
- **Sources:** Bernard & Thomas 1989/1990; Chan, Jegadeesh & Lakonishok 1996; Brandt et al. 2008.
- **Mechanisms:** limited attention (Hirshleifer, Lim & Teoh 2009; DellaVigna & Pollet 2009) and under-weighting of the persistence of earnings changes.

## 3. Why it is distinct from H001–H016

- **Earlier hypotheses:** every one conditioned on price/volume patterns or on an accounting ratio.
- **H017:** conditions on a **verified, timestamped information event**, and measures the reaction only after it.
- **Evidence for the distinction:** Chan (2003) and Savor (2012) show that news-driven moves continue while news-less moves reverse.
- **Why the price-only tests don't settle it:** H009 (volume shock) and H010 (gaps) pooled both kinds of move.
- **No unrelated ranking variable:** no momentum, moving average, RSI or 52-week-high input is used.

## 4–5. Event definition and timing (Event Data v1, unchanged)

**Event definition:**
- an original 8-K with Item 2.02;
- the first SEC acceptance, in US Eastern time, using the measured per-registrant time-zone convention;
- 30-day de-duplication; amendments ignored; no inferred dates.

**Excluded events:**
- foreign private issuers;
- ambiguous predecessor links;
- contradicted, unverified and weak identities.

Only links verified by dated ticker evidence or identity v2 are used, plus the frozen unique, time-disjoint predecessor links.

| Class (acceptance on D) | Event session E | Reaction window | Decision | Entry |
|---|---|---|---|---|
| BMO (< 09:30) | D | close D−1 → close D+1 | close D+1 | open D+2 |
| During market | D | close D−1 → close D+1 | close D+1 | open D+2 |
| AMC (≥ close) / non-session | next session D′ | close D′−1 → close D′+1 | close D′+1 | open D′+2 |
| Unknown time | treated as AMC of the filing date | as AMC | as AMC | as AMC |

There is no same-day trading and no trade at the BMO session's own open, because the engine decides only at a close.

## 6. Reaction measurement (one definition)

**AR = [Close(E+1) / Close(E−1) − 1] − [SPY Close(E+1) / SPY Close(E−1) − 1].**

- **Baseline:** Close(E−1), the last close before the information was available.
- **Reaction:** sessions E and E+1 only.
- **Why two sessions:**
  - it mirrors the literature's 3–4-day windows without their pre-event days;
  - it absorbs 8-K timestamps that trail the press release (11.6% of events lag by one or more days) and intraday timing ambiguity.
- **Missing data:** a missing close at E−1, E or E+1 means no signal.

## 7. Strength threshold (one rule)

**Rule:** AR ≥ the 90th percentile of AR over all universe events with a decision session in the previous 252 sessions (strictly earlier), **and** AR > 0.

**Minimum sample:** 400 such events, otherwise no signals. A history-only warm-up from 2009-07-01 lets October 2009 onward (when the point-in-time universe begins) build the first breakpoint.

**Why the top decile:**
- it is the extreme-decile sort used by the reaction-based literature;
- it gives ≈ 450 signals a year, about 11× the book's capacity (≈ 40 entries a year), so the book always holds the strongest reactions available;
- a trailing breakpoint is point-in-time and self-adjusts to volatility regimes (e.g. 2020).

## 8. Volume

**Not included.**
- The evidence for abnormal volume (Gervais et al. 2001; Garfinkel & Sokobin 2006) is real but secondary: a visibility / opinion-divergence effect.
- Including it would create a second threshold dimension.
- It is reported in the event-level diagnostic only.

## 9–11. Entry, holding, exit

| Rule | Detail |
|---|---|
| Entry | Market-on-open at E+2, through the harness, at the D051-sized target |
| Holding | Exactly **60 sessions**: Bernard & Thomas' drift window. A 60-session hold after an E+2 entry ends about one session before the typical next release (≈ 63 sessions), so the book does not take on a second, untested event risk |
| Exit | Fixed holding period only (exit order at the close of the 59th session after entry; executed at the open of session entry + 60). Harness forced exits remain (delisting, acquisition, 10 sessions without data). No stops, targets or technical exits |
| Further events for a stock already held | Ignored (no add, no clock reset) |

## 12–14. Portfolio, capacity, ranking

| Item | Rule |
|---|---|
| Slots | **10** |
| Target position | 0.98 / 10 of current equity (≈ $9,800 at $100K; ≈ $19,600 at $200K) |
| Maximum position weight | 10% |
| Minimum new position | $4,000 (reference; rarely binding) |
| Cash | D051 settled cash only, 2% buffer, 15% gap reserve. A slot freed at an open is usable from that day's close. No top-up |
| Leverage | None |
| Capacity | Free slots at each close are filled with that day's qualifying signals |
| Ranking | **AR, highest first** (ties by security id). Signals that do not fit are dropped; never queued, never replacing a holding |

**Why 10 slots** (mechanical, not return-based):

| Slots | Cost a year at $100K |
|---|---|
| 8 | 1.23% |
| **10** | **1.36%** |
| 12 | 1.48% |
| 15 | 1.68% |
| 20 | 2.01% |

- **The cap:** R4 caps realised costs at 1.5% a year. 12 slots leave almost no margin; 15 or more fail R4 structurally.
- **The trade-off:** 10 slots means higher selection noise (§22 shows the power cost).
- **This is an account-model constraint:** with $7 per order, a $100K account cannot hold a wide event book at a 60-session turnover.

## 15–17. Frequency, turnover and costs

Mechanical simulation with no prices: 20 random-selection seeds, 2010-03 → 2021-12.

| Item | $100K, N = 10 | $200K, N = 10 |
|---|---|---|
| Eligible verified events a year | ≈ 4,490 (2,758 in partial 2010 → 6,334 in 2021) | same |
| Qualifying signals a year (top decile) | ≈ 452 | same |
| Entries (= round trips) a year | ≈ 40 | ≈ 40 |
| Mean slots occupied | 9.4 of 10 (5.6% idle, mostly between earnings seasons) | 9.4 |
| Mean invested | ≈ 90% | ≈ 90% |
| Average position | ≈ $8,800 | ≈ $17,900 |
| Commissions a year | ≈ 0.60% | ≈ 0.30% |
| Slippage a year | ≈ 0.76% | ≈ 0.76% |
| **Total trading cost a year** | **≈ 1.36%** | **≈ 1.05%** |

**Structural hurdle (disclosed):**
- Costs ≈ 1.4% a year, plus ≈ 10% uninvested capital (≈ 1.3% a year of foregone SPY return at 2010–21 rates), ≈ 2.7% a year in total.
- So the selected events must beat SPY by about **0.75% per 60-session trade** just to tie SPY.

## 18–20. Controls

| Control | Exact definition |
|---|---|
| **SPY** | E900-07 total return on 2010-03-01 → 2021-12-31 |
| **EW-H017** | Equal weight of the exact H017 universe (eligible ∩ verified domestic 8-K filers), first session of each month, 25% band, $10M paper notional (the approved B901 mechanics). Answers the universe effect |
| **Random-event books, seeds 1, 2, 3, 4, 5** | The identical S017 code, sizing, cash, costs, timing and 60-session holding. On each decision date the book opens at most **k_t** positions (k_t = the candidate's qualifying-signal count that day), chosen from **all** eligible events with that decision session, by the key SHA-256("seed\|security id\|event date"). Answers whether picking strong positive reactions beats random event participation at the same moments. Each is reported individually; W3 uses their median CAGR; streams are never averaged |
| Canary book, seed 0 | Infrastructure checks only |

## 21. Event-level diagnostic (pre-declared; never a gate or a design input)

A separate non-trading infrastructure run (E983-01; aggregated statistics only, no raw data export) computes, for every eligible event 2010-03 → 2021-12:
- its reaction decile (the same point-in-time breakpoints);
- its excess return over SPY from the open of E+2 to the open of E+62 (the candidate's timing).

**Reported:**
- the mean / median for the top decile, deciles 2–9 and the bottom decile;
- month-clustered t-statistics;
- two-year blocks;
- splits by timing class (BMO / during / AMC) and abnormal-volume tercile.

**Purpose:** show whether the event effect itself is visible across thousands of events, even if a 10-position book is noisy.

## 22. Amendment 3 mapping (unchanged)

| Gate | Applied to H017 |
|---|---|
| W1 | CAGR(E017-01) > CAGR(SPY), $100K, 2010-03-01 → 2021-12-31 |
| W2 | g ≥ 2.15 × max(iid, stationary-bootstrap block 126) SE |
| W3 | CAGR > EW-H017 and > the median CAGR of random-event seeds 1–5 |
| R1 / R2 / R3 / R4 | MaxDD ≤ SPY − 10 points; Sharpe ≥ SPY − 0.15; no two-year block > 50% of the excess; costs ≤ 1.5% a year, no leverage, the 10-slot limits |
| G4′ (only if all the above pass) | ≥ 5 of 6 perturbations (§25) keep W1; W1 holds at 2× slippage |

**Operating characteristics, 10 positions, 12 years** (control-book noise; R4 / G4′ not modelled, so upper bounds):

| True edge over SPY | 0% | 1% | 2% | 3% | 4% | 5% | 6% | 8% |
|---|---|---|---|---|---|---|---|---|
| Qualifies | 0.3% | 0.9% | 1.8% | 4.0% | 7.0% | 12.1% | 20.1% | 43.3% |
| Promising but Not Qualified (§23) | 3.2% | 5.4% | 9.2% | 13.6% | 19.7% | 24.5% | 28.6% | 23.0% |
| Either | 3.4% | 6.3% | 11.1% | 17.5% | 26.8% | 36.6% | 48.7% | 66.2% |

## 23. Proposed "Promising but Not Qualified" (PbNQ) rule

**All must hold.** They are evaluated in this order, frozen before H017 runs.

1. **W1** passes.
2. **Material excess:** CAGR(H) − CAGR(SPY) ≥ **+1.0 point a year**. This prevents promoting a trivially positive result.
3. **Some statistical support:** the W2 statistic g / SE ≥ **1.0**, while W2 itself (2.15) fails. If W2 passes, the case is "qualified", not PbNQ.
4. **W3** passes (beats EW-H017 and the median random-event book).
5. **R1, R2, R3, R4** all pass. A promising result must already be investable: risk and costs are not relaxed.
6. **Cost stress:** at 2× slippage (run E017-09, executed only when 1–5 hold) W1 still holds.
7. **Mechanism visible at event level:** the top-decile events' mean 60-session excess return over SPY is > 0 with a month-clustered t ≥ 2.0, and exceeds the mean of deciles 2–9 (E983-01).

**Meaning:**
- **Rule 7** uses the event diagnostic **only** for this spend decision, never for qualification.
- **Without rules 6–7**, a no-edge book meets PbNQ ≈ 3.2% of the time (10 positions, 12 years); rules 6–7 lower that further.
- **PbNQ = NO Holdout, NO production, NO declaration of success.** Its only consequence: you may consider buying more history to re-test **the same frozen strategy**.

## 24. Decision tree (pre-registered)

| Case | Condition | Consequence |
|---|---|---|
| **C: development-qualified** | W1, W2, W3, R1–R4 pass and G4′ passes (conditional runs E017-09..17) | Freeze everything; STOP; ask for explicit approval before any Holdout access |
| **B: Promising but Not Qualified** | §23 rules 1–7 hold | H017 stays frozen exactly; Holdout locked; STOP; you may consider data purchase solely to re-test the same frozen H017 on a longer history |
| **A: clear failure** | Anything else (e.g. CAGR ≤ SPY, fails W3, any R fails, or PbNQ conditions unmet; also W1–R4 passing but G4′ failing) | H017 rejected; no data purchase to rescue it; no tuning. Phase 2's three slots are then used; Phase 2 ends with "No Production Candidate Found" unless you decide otherwise |

Nothing in H017, the gates, the controls or this tree may change after any H017 result.

## 25. Robustness perturbations (G4′; defined now, run only if Case C's prerequisites hold)

| ID | Perturbation |
|---|---|
| P1 | Holding 40 sessions |
| P2 | Holding 80 sessions |
| P3 | Threshold: top quintile (80th percentile) |
| P4 | One-session reaction (close E−1 → close E), decision at close E, entry at open E+1 |
| P5 | 8 slots |
| P6 | 12 slots |
| Slippage | 2× (the G4′ item, also PbNQ rule 6), 4×, 6× (reported) |

## 26. QuantConnect runs and runtime (after approval)

| Run | Purpose |
|---|---|
| X982 / E982-01 | Canary: random-event book seed 0 + checks |
| E017-01 | Candidate, $100K (**consumes Phase 2 slot 3**) |
| E017-02 | EW-H017 |
| E017-03 … 07 | Random-event books, seeds 1–5 |
| E017-08 | Candidate, $200K (sensitivity only) |
| X983 / E983-01 | Event-level diagnostic (non-trading, aggregated) |
| E017-09 | 2× slippage: only if PbNQ rules 1–5 or the Case C prerequisites hold |
| E017-10, 11, 12 … 17 | 4×, 6× slippage, P1–P6: only if W1–W3 and R1–R4 pass |

**Estimated time:** ≈ 15–25 min of compute each, plus 0–75 min of result download. ≈ 3–6 h for the committed set; no extra QuantConnect cost.

**Implementation estimate** (after approval):
- an event-table builder (Event Data v1 frozen manifest + hash);
- packing the event table into QuantConnect project files (≈ 85,000 events; 64 KB per-file limit, like the SEC table);
- `qr_h017` pure logic (reaction, trailing breakpoint, capacity) with unit tests;
- S017 (candidate / random / EW books, one code path);
- canary and evaluation scripts.

About 1–2 days of work.

## 27. Data / leakage canaries required before the candidate run

1. **Event table frozen** (hash) and reproducible from the cached SEC data. Tests:
   - de-duplication;
   - amendments excluded;
   - time-zone conventions applied (re-check a 50-event sample against EDGAR index pages);
   - foreign issuers and unverified identities excluded;
   - predecessor links unique and time-disjoint;
   - no event with a decision session after 2021-12-31 (Holdout lock).
2. **Unit tests (truncation):**
   - AR uses only the closes at E−1 and E+1 (and SPY's);
   - the breakpoint uses only events with an earlier decision session;
   - adding future events never changes past signals;
   - the capacity ranking is deterministic.
3. **Canary E982-01**, checked offline from fills and logged identifiers (no returns):
   - every entry fills at the open of E+2 of its event and is never earlier;
   - every exit fills exactly 60 sessions after entry (or is a logged forced exit);
   - at most 10 positions; no duplicate entry per event; held-stock events ignored;
   - no negative cash; $7 per order;
   - breakpoint sample sizes ≥ 400 from 2010-03-01;
   - first decision ≥ 2010-03-01, with warm-up only before it;
   - the random book's daily entries ≤ k_t;
   - candidate and control mechanics byte-identical (the same code file).
4. Data infrastructure v1 freeze test passes; Amendment 3 hash unchanged.

## 28. Exact owner decisions required to authorise implementation

1. **Approve H017 as specified** (`research/hypotheses/H017.md`):
   - two-session SPY-adjusted reaction;
   - top decile on a trailing 252 sessions with AR > 0;
   - entry at E+2; 60-session fixed hold; no volume; no other exit;
   - 10 slots, AR-ranked capacity, drop the excess; no top-up;
   - financials included.

   Or instruct changes **now**, before freezing.
2. **Approve the controls** (SPY, EW-H017, random-event seeds 1–5 with day-matched k_t; canary seed 0) and the event-level diagnostic.
3. **Approve the PbNQ rule** (§23, rules 1–7) and the decision tree (§24).
4. **Approve the account model for this family:** N = 10, ≈ $9,800 target, $4,000 minimum (reference), D051 without top-up. Acknowledge the ≈ 1.36% a year cost and ≈ 90% invested.
5. **Authorise implementation and execution:**
   - infrastructure, tests, the canary, then E017-01..08 + E983-01, and conditional runs only per §26;
   - **E017-01 consumes Phase 2 slot 3**;
   - STOP at the development checkpoint.

   Or authorise implementation only, with a separate approval before E017-01.
6. **Confirm** that no data purchase will be made before H017's outcome is known (as you decided).

**STOP.** Nothing implemented or run, no returns computed, slot 3 unused, Holdout locked.
