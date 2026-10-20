# H031 — Dividend-event drift among large US stocks (K1): specification DRAFT, frozen-ready

**Status:** DRAFT prepared under D267 item 3 (K1 conditional GO). **Not registered, not frozen, not implemented, not run.** No return, event count or price was computed for it.

On owner approval:
- it is copied to `research/hypotheses/H031.md` with status FROZEN, and its SHA-256 is pinned with the frozen screen protocol (`research/rr/programme/RR_screen_confirmation.md`);
- then come the implementation, the event canary (C) and, on a separate approval, the strategy runs R1 / R1d / R2 / R3.

**Prior and motivation (pre-2018 literature only):**
- Michaely, Thaler & Womack (1995): price drift after dividend initiations (positive) and omissions (negative).
- Grullon & Michaely (2002); Benartzi, Michaely & Thaler (1997): dividend changes do not predict future earnings growth.
- Boehme & Sorescu (2002): the long-run initiation drift is not robust to methodology.
- **The prior is weak.** Large US stocks after 2000 are not well studied. "No candidate" is the expected outcome.
- Not motivated by any post-2017 market event.

## 1. Hypothesis

US common stocks in the approved ≥ $2B universe that **initiate** a regular cash dividend, or **raise** their regular quarterly dividend by at least 25%, earn higher total returns than the market over the following 126 sessions, after realistic costs. The effect is measured from the first open after the ex-date, so it uses only information public by then.

## 2. Universe, window and data

- **Universe:** the approved rule on QuantConnect's vendor market cap (US common, NYSE / Nasdaq / AMEX, PIT cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M), evaluated at the selection stamp that precedes the ex-date. The universe limits accepted with UR-1 apply.
- **Window:** the development window the owner sets after RR5 (default 2010-01-04 → 2021-12-31).
  - History-only warm-up from 2008-07-01, to build each security's dividend cadence: no decision, order or equity record before the official start (harness D114).
  - The Holdout is never read.
- **Data:** QuantConnect's dividend events (Security Master), raw daily prices for fills, total-return accounting (cash dividends credited). Every eligible security is subscribed (daily), so its dividend events are received.

## 3. Event definitions (all decided before any count or return)

**Inputs at the ex-date x of security s:**
- d = distribution amount (QuantConnect feed, whole cents, D162);
- p = the reference price (the close before x);
- the dividend history H of s over the 400 days before x (from the warm-up onward).

| Item | Rule |
|---|---|
| Spin-off / special filter | **Excluded** if d / p > 10% (spin-offs arrive unlabelled as dividends, D145), or if a split occurs within ±5 sessions of x |
| Quarterly cadence | At least 3 prior distributions in H with consecutive spacings of 70–110 days; the previous regular amount d₋ = the last prior distribution |
| **Regular increase** | Quarterly cadence, d₋ ≥ $0.05, spacing x − (last ex-date) ∈ [70, 110] days, and 1.25 ≤ d / d₋ ≤ 2.5. A ratio > 2.5 is **excluded as ambiguous** (special or cadence change) |
| **Initiation** | No distribution in the 365 days before x; the security has traded for at least 365 days before x; d / p ≤ 5% |
| Ambiguous cadence | Monthly, semi-annual, annual or irregular payers never produce increase events. Initiations are judged without cadence |
| One event per security | A security already held, or with an event in the last 126 sessions, produces no new event |

## 4. Timing, execution and accounting

- **Observability:** the dividend arrives in the corporate-action slice at midnight on the ex-date, before that day's bars (harness). The event is used at that session's close.
- **Execution:** market order at the **next session's open** (T+1 after the ex-date). The ex-dividend price drop has already happened. Fill at the raw open; 10 bps slippage per side; $7 per order (D039).
- **No announcement date is used.** The feed has none, and the declaration always precedes the ex-date, so there is no look-ahead. The signal is late: typically 2–4 weeks after the announcement.
- **Holding:** exactly 126 sessions. The sell order goes to the open after the 126th close. No early exit except delisting or acquisition (harness D054 / D062: last real close).
- **Returns:** total return (later dividends credited as cash; raw fills). Signals use distribution amounts only, never prices.

## 5. Portfolio rules

| Item | Rule |
|---|---|
| Account | $100,000 (R3: $200,000, report only) |
| Slots | at most 15 positions; target 1/15 of current equity per new position, capped at 10% of equity; minimum $5,000 (D044); D051 settled-cash funding with the 15% gap reserve; no leverage; no top-up, trim or rebalancing |
| Queue (same day, more events than free slots) | Initiations first; then increases by d / d₋ descending; ties by ADV20 descending, then security id. Events not filled that day are **dropped** (no waiting list) |
| Cash | idle cash earns nothing (as in all earlier books) |

## 6. Controls (shadow books in the same run, same mechanics and costs)

- **SPY** total return, buy-and-hold.
- **Equal-weight universe control** (Amendment 3 W3 definition).
- **5 event-matched random controls** (seeds 20261101 … 20261105, fixed now). Each event is replaced by a randomly chosen eligible security that has a **regular, unchanged** quarterly dividend (0.95 ≤ d / d₋ ≤ 1.05) with an ex-date on the same day, else within the same week. Entry, hold, queue and sizing are identical.
  - This isolates the dividend-change information from ex-date timing and dividend-payer status.

## 7. Evaluation

The frozen RR screen protocol v2:
- **D1:** P1–P6 on R1, P5 on R2.
- **D2:** Amendment 3 with Holm, m = 1 → W2 ≥ 2.15. G4′ only on a separate approval, with perturbations fixed now:
  1. 20% increase threshold;
  2. 33% increase threshold;
  3. 105-session hold;
  4. 147-session hold;
  5. 12 slots;
  6. initiations excluded.
- **Holdout:** at most once in the whole programme, on separate written approval.

## 8. Expected costs and turnover (estimate, before any run)

- **Event frequency** (public SEC XBRL, RR4 §4.1; lower bounds): increases ≥ 25% ≈ 60 a year; initiations ≈ 29 a year. That is about 89+ events a year, against a capacity of about 30 entries a year (15 slots × 252 / 126). Slots should be mostly full; the queue rule decides which events enter.
- **Costs:** ≈ 30 round trips a year × (2 × $7 + 2 × 10 bps × $5,667) ≈ $760 a year ≈ 0.8% a year at $100K. That is below R4's 1.5%.
- **Turnover:** ≈ 200% a year of the invested book.

## 9. Event canary C (before any strategy run; aggregate only)

**Exports per year:**
- event counts by class (initiation / increase / excluded spin-off-special / excluded ambiguous / cadence classes);
- d / d₋ quantiles;
- the share of events whose order date is after the ex-date (must be 100%), and the number of orders placed on or before an ex-date (must be 0);
- slot utilisation (from the queue simulation without prices);
- monthly E counts (universe snapshot check).

**Not exported:** no returns, prices or security-level data.

**Pass conditions (fixed now):**
- the timing checks are exact;
- at least 20 increase events and at least 5 initiations a year on average;
- at most 10% of raw dividend events are unparseable.

Otherwise: STOP and report.

## 10. Stopping conditions

- The canary fails, or QuantConnect refuses the code: STOP, no workaround.
- D1 fails: H031 is closed (no variant, threshold or hold change, no rerun).
- D1 passes: STOP for the owner. G4′ and D2 completion only on approval.
- D2 fails: closed.
- D2 passes: STOP. The Holdout is requested only on separate written approval and only for this one programme candidate.
- **Run budget:** C, R1, R1d, R2, R3, plus G1–G6 only if approved, plus at most one documented infrastructure retry. Nothing else.
