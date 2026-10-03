# H017 frozen specification: earnings-event continuation (Phase 2, hypothesis 3 of 3)

- **Status:** FROZEN 2026-10-03, after the owner's approval of the H017 specification ("Phase 2 — Approve H017 Specification, Authorise Implementation + Canary Only"). Hash-pinned in `qresearch.p2h017.SPEC_SHA256` (test: `tests/test_p2h017.py`). Any change → STOP and ask the owner.
- **Source of the rules:** `research/hypotheses/H017.md` (approved exactly as proposed) and P2-CP13 §18–§27. This file restates them and adds only the implementation precisions of §9, which fill gaps without changing any approved rule.
- **Implementation:** `src/qresearch/lean/qr_h017.py` (pure logic), `strategies/S017_earnings_continuation/main.py` (all books, one code path), event table v1 (`research/phase2/h017/event_table_v1.json`, payload SHA-256 pinned in `qresearch.p2h017.EVENT_TABLE_SHA256`), evaluation `qresearch.p2h017` + `research/phase2/H017_eval.py`.
- **Unchanged and frozen elsewhere:** Amendment 3 (`research/phase2/P2_amendment3_spec.md`, `qresearch.wealth`); data infrastructure v1 (`research/phase2/data_freeze_v1.json`); Event Data v1 rules (P2-CP12 §19).

## 1. Events (Event Data v1, exactly)

- Original SEC 8-K with Item 2.02 (or its predecessor Item 12); 8-K/A ignored; first SEC acceptance; 30-day de-duplication; no inferred dates.
- Acceptance time converted with the measured per-registrant convention (`tz_conventions.json`); unresolved or unmeasured → unknown time, handled as after the close of the filing date.
- Event session E: BMO or during-market acceptance on session D → E = D; after the close or on a non-session day → the next session; unknown time → the session after the filing date.
- Foreign private issuers excluded (no 8-K). Only identities verified by dated ticker evidence or identity v2. Unique, time-disjoint predecessor links only; ambiguous cases excluded.
- Table window: decision sessions 2009-07-01 → 2021-12-31. Nothing after 2021-12-31.

## 2. Universe on the decision session

Harness-eligible (frozen data v1: US common, NYSE/Nasdaq/AMEX, point-in-time market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M, SEC correction layer). Financials included.

## 3. Signal

- **Reaction:** AR = [Close(E+1) / Close(E−1) − 1] − [SPY Close(E+1) / SPY Close(E−1) − 1], adjusted closes.
- Missing a close at E−1, E or E+1 (stock or SPY) → no signal.
- **Threshold:** AR ≥ the 90th percentile of AR over all universe events whose decision session lies in the previous 252 sessions (strictly before today), and AR > 0. At least 400 such events, else no signal.
- **Decision:** at the close of E+1. **Entry:** market-on-open at E+2.
- No volume filter, technical filter, RSI / moving average / momentum / 52-week rule, stop, target, or alternative reaction, holding period or threshold.

## 4. Holding and exit

- Exactly 60 sessions from the entry open: the exit order is placed at the close of the 59th session after the entry session and executes at the open of entry + 60.
- No other exit except the harness's forced integrity exits (delisting, acquisition, 10 sessions without data).
- Later events of a held stock are ignored (no add, no clock reset).

## 5. Portfolio and costs

- $100K primary account; $200K sensitivity only.
- Maximum 10 positions; target 0.98 / 10 of current equity (≈ $9,800 at $100K); maximum position weight 10%; $4,000 reference minimum for a new position.
- Settled cash only (D051), 2% buffer, 15% gap reserve; **no top-up**; no leverage; long-only.
- $7 per order; 10 bps slippage per side.
- **Capacity:** on each decision date, the qualifying signals are ranked by AR (highest first, ties by security id) and fill the free slots; the excess is dropped (never queued); existing positions are never replaced early.

## 6. Controls and runs

| Run | Book |
|---|---|
| E982-01 (X982, byte copy of S017) | Canary: random-event book seed 0, full window, checks only |
| E017-01 | Candidate, $100K (**consumes Phase 2 slot 3**) |
| E017-02 | EW-H017: same-universe equal weight, first session of each month, 25% band, $10M paper notional (B901 mechanics) |
| E017-03 … 07 | Random-event books, seeds 1, 2, 3, 4, 5 |
| E017-08 | Candidate, $200K (sensitivity only; never decides, never rescues) |
| E983-01 (X983) | Event-level diagnostic (aggregated; never a gate) |
| E017-09 | 2× slippage (PbNQ rule 6 / G4′) |
| E017-10, 11 | 4×, 6× slippage (reported) |
| E017-12 … 17 | P1 hold 40; P2 hold 80; P3 top quintile (80th percentile); P4 one-session reaction (close E−1 → close E, decision at close E, entry at open E+1); P5 8 slots; P6 12 slots |

- **Random-event books:** identical code path, sizing, timing, holding, costs, cash and opportunity dates. On each decision date the book opens at most k_t positions, k_t = the number of the candidate's qualifying signals that day, chosen among all universe events of the day by the fixed key SHA-256("seed|security id|event date"). Never averaged; W3 uses the median CAGR of seeds 1–5.
- **Window:** history-only warm-up from 2009-07-01; official start 2010-03-01; end 2021-12-31. Every comparison uses 2010-03-01 → 2021-12-31 for every book (SPY = E900-07 on those dates).

## 7. Evaluation (Amendment 3, unchanged) and pre-registered outcomes

- **Gates:** W1 CAGR(E017-01) > CAGR(SPY); W2 g ≥ 2.15 × max(iid, stationary-bootstrap block 126) SE; W3 CAGR > EW-H017 and > the median CAGR of seeds 1–5; R1 MaxDD ≥ SPY's − 10 points; R2 Sharpe ≥ SPY's − 0.15; R3 total log excess > 0 and no two-year block > 50% of it; R4 realised costs ≤ 1.5% a year, no leverage, the 10-slot limits; G4′ (only if all pass) ≥ 5 of 6 perturbations keep W1 and W1 holds at 2× slippage.
- **Promising but Not Qualified (PbNQ), all must hold, in this order:**
  1. W1 passes;
  2. CAGR(H) − CAGR(SPY) ≥ +1.0 point a year;
  3. g / SE ≥ 1.0 while W2 (2.15) fails;
  4. W3 passes;
  5. R1, R2, R3, R4 pass;
  6. W1 passes at 2× slippage (E017-09);
  7. event level (E983-01): the top-decile mean 60-session excess return over SPY > 0, with month-clustered t ≥ 2.0, and above the mean of deciles 2–9.

  PbNQ means NO Holdout, NO production, NO declaration of success.
- **Decision tree:**
  - **Case C (development-qualified):** W1, W2, W3, R1–R4 and G4′ pass → freeze everything; STOP; request Holdout approval.
  - **Case B (PbNQ):** rules 1–7 hold → H017 frozen; Holdout locked; STOP; the owner may consider a data purchase only to re-test the same frozen H017.
  - **Case A (failure):** anything else (including W1–R4 passing but G4′ failing) → H017 rejected; no tuning; no data purchase.
- **Conditional runs:** E017-09 only if PbNQ rules 1–5 or the Case C prerequisites hold; E017-10 … 17 only if W1–W3 and R1–R4 pass. E983-01 only after its separate authorisation.

## 8. Event-level diagnostic E983-01 (pre-declared; never a gate or a design input)

- **Events:** every universe event (§2) with a valid reaction (§3), decision session 2010-03-01 → 2021-12-31, whose exit session E+62 is on or before 2021-12-31 (no Holdout data).
- **Reaction decile:** decile d = 1 + the number of the trailing breakpoints p10, p20, …, p90 (same point-in-time sample and interpolation as §3) that AR is at or above. **Top decile** = the candidate's qualifying events (AR ≥ p90 and AR > 0); events with d = 10 but AR ≤ 0 are reported separately and belong to neither group. **Deciles 2–9** = d in 2…9.
- **Excess return:** [Open(E+62) / Open(E+2) − 1] − [SPY Open(E+62) / SPY Open(E+2) − 1], adjusted prices (the candidate's timing). Entry requires a real open at E+2. If the stock has no real bar at E+62 (delisting / acquisition), its last real close before E+62 is the exit price (the harness's convention).
- **Month-clustered t:** for a group with values x_i in decision months m: t = mean / SE, SE = sqrt(M / (M − 1) · Σ_m (Σ_{i∈m} (x_i − mean))²) / n.
- **Reported:** mean and median for the top decile, deciles 2–9 and the bottom decile; t-statistics; two-year blocks; splits by timing class (BMO / during / AMC / other) and by abnormal-volume tercile (volume of E and E+1 over the mean volume of the 20 sessions ending at E−1; terciles from the same trailing 252-session sample).

## 9. Implementation precisions (no approved rule changed)

1. **Event table v1:**
   - A security's events from its linked registrants are merged; a linked (predecessor) registrant's event is used only if filed outside the mapped registrant's own SEC filing span (event-level time-disjointness; this removes co-registrants filing combined 8-Ks).
   - A security-level 30-day de-duplication applies to the merged stream (1 cross-registrant duplicate).
   - Unmeasured predecessor conventions → unknown time.
   - The 2008–2009 NYSE early closes complete the early-close list for warm-up events only.
2. **Reaction prices:** split- and dividend-adjusted closes as known at the decision close (LEAN SCALED_RAW history, real bars only, dated by session). A stock's or SPY's missing real bar at E−1, E or E+1 → no signal.
3. **Universe event:** a table event whose security is harness-eligible on the decision session and has a valid reaction. The breakpoint sample, the random books' choice set and k_t all use exactly these events.
4. **Percentile:** linear interpolation between order statistics (numpy's default).
5. **k_t:** the count of the day's qualifying signals before held stocks are skipped. The candidate takes its ranked signals and the random books their key-ranked universe events, each skipping held or pending stocks, up to min(free slots, k_t).
6. **Free slots:** 10 − held positions − pending buys. A position whose exit order is placed at this close still occupies its slot until the exit executes at the next open: under D051 its proceeds are not settled cash at this close. This matches the approved capacity simulation.
7. **EW-H017 membership on session t:** eligible, and the security has a table event whose decision session lies in the trailing 252 sessions (t − 252 < index ≤ t). That is: a verified domestic 8-K earnings filer, point in time.
8. **Sessions:** counted on real SPY bars (harness); "held 0" is the entry day.
9. **P5 (8 slots):** the 10% maximum position weight still caps each position (≈ 80% invested); P6 (12 slots) targets 0.98/12.
10. **R4 inputs:**
    - realised costs = (commissions + traded notional × slippage rate) / mean equity / years (`p2spec.cost_drag`), on the common window;
    - no leverage = maximum gross exposure ≤ 1 and no negative cash;
    - limits = at most 10 positions (the run's slot count for P5/P6) and every entry ≤ 10% of equity when placed.
