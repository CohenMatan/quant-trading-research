# P14-CP6a — Null #3 (B2 Event-Copy Relay): pre-implementation synthetic feasibility → STOP

**Result: STOP — B2 FAILS ITS OWN CONTINUITY REQUIREMENT UNDER REALISTIC UNIVERSE CHURN. NO REAL-DATA NULL #3 WORLD WAS GENERATED.**

**What happened:**
- I implemented the B2 design approved in D237 offline and tested it on synthetic panels before any QuantConnect run.
- The panels are calibrated to the H029 universe and carry **no predictive signal**, so the "real" selection's persistence there is a purely structural property that a valid null must reproduce.
- B2 does not reproduce it. Its null portfolios change **0.10–0.15 more of their names per month** than the no-signal real selection: 7–10 times the gap that made Null #2 fail.
- A refinement I tried (continuing with the same origin company where possible) is also clearly inadequate.

**Why I stopped rather than ran:**
- Running B2 as approved would, on this evidence, almost certainly fail the formal adequacy gates, which closes H029 / H030 under the anti-fork rule.
- Changing the design into something else would be a fourth null in substance, which is not authorised.
- So the decision returns to you.

**What did not happen:**
- No QuantConnect run, no G-TURN-29 pin, no canary, no null world, no threshold.
- No return of any kind.
- No Holdout access.

**Status (unchanged):** H029 / H030 BLOCKED, neither qualified nor rejected.

---

## 1. What was done (owner D237)

| Step | Status |
|---|---|
| Owner approval recorded | `docs/owner/2026-10-13_p14cp6_null3_approval.md`, verbatim |
| Amendment 2 written, including both owner amendments | `research/phase14/H029_H030_amendment2_event_copy_relay.md`: cross-sectional gates S1–S4 with bounds fixed from sampling theory; fallback ≤ 5% with reporting by review and sector; the q_exit / q_entry rule for G-TURN-29; P1 / P2; canaries A–H. **Marked DRAFT — NOT FROZEN** after this finding; never pinned or used. |
| Null #3 implemented offline | `src/qresearch/lean/qr_h029n3.py`: event plan, relay, constructibility, P1, P2, q rule, S1–S4, adequacy, canary synthetics. A separate module, **not uploaded by any host**. The pinned `qr_h029` is byte-identical, so the Null #1 / #2 records stay intact. |
| Guarantee tests | `tests/test_p14_null3.py`, **all pass**: no artificial reset (a continuing non-event stock's copy never changes, whatever other stocks do); same-sector copies; no self-copy; exact bijection on event groups; ≥ 5 of 6 valid; PIT truncation; determinism; fallback and NOT-CONSTRUCTIBLE stop; statistics checked against hand computations |
| Synthetic feasibility study | `research/phase14/cp6/P14_CP6a_synthetic_feasibility.py` → `.json` (SHA-256 fb2cf31a…; reproduced bit-identically) |

## 2. The synthetic feasibility study

**Panels** (no market data, no returns, no signal):
- 765 stocks and 11 sectors, with about 18 exits and 21 entries a month: the H029 universe's measured churn.
- Six persistent signals per stock, updated on staggered quarterly filing cycles.
- One sector move a month.
- Variant: off-cycle single-signal missing-value changes.
- Control: no churn.
- 3 panel seeds × 8 null worlds for each null.

**Calibration:** the **frozen Null #2** on these panels shows a turnover gap of +0.012 to +0.019, which matches its real-data gap of +0.016 (P14-CP4). So the panels reproduce the real universe's relevant structure.

**Results** (H029 name turnover; real = the no-signal selection):

| Panel | Real | Null #2 (frozen) | **B2 as approved** | B2 + continuation (exploratory) |
|---|---|---|---|---|
| realistic, seed 9 | 0.207 | 0.221–0.227 | **0.311–0.333** | 0.227–0.250 |
| realistic, seed 10 | 0.217 | 0.227–0.240 | **0.336–0.357** | 0.250–0.295 |
| realistic, seed 11 | 0.214 | 0.221–0.240 | **0.304–0.333** | 0.241–0.267 |
| + off-cycle missing, seed 9 | 0.285 | 0.296–0.302 | **0.403–0.447** | 0.377–0.411 |
| + off-cycle missing, seed 10 | 0.294 | 0.301–0.315 | **0.417–0.448** | 0.384–0.430 |
| + off-cycle missing, seed 11 | 0.272 | 0.279–0.298 | **0.400–0.444** | 0.377–0.407 |
| no-churn control, seed 9 | 0.197 | 0.197–0.199 | 0.200–0.213 | 0.203–0.214 |

**Top-15 survival among continuing names (P2)** points the same way. In the realistic panels: real 0.80–0.82; Null #2 0.78–0.80; B2 approved 0.66–0.72; B2 + continuation 0.73–0.79.

**In every realistic panel the real value lies outside every world of every null.**

## 3. Why B2 fails

The P14-CP5 analysis was **wrong on one point**:
- It claimed that coupling at events by rank (recipient's null previous rank ↔ donor's real previous rank) would carry over the real persistence dynamics.
- That holds only when the group of stocks with events in a sector is the **same set** from one filing cycle to the next. Then the coupling re-creates the previous pairs:
  - small no-churn test panel: 99.6% same origin, turnover 0.164 vs 0.162;
  - realistic no-churn control: only a small residual gap (+0.003 to +0.016) from the first filing cycle after the random start.

Under realistic churn it breaks down in three ways:
1. **Rank shifts cascade.** Every entry, exit or sector move inside an event group shifts the ranks, so many recipients are coupled to a *neighbouring* company instead of their previous origin. With about 23 event stocks per sector a month, one rank step is a large jump near the Top-15 cutoff (only about 2% of the cross-section).
2. **Off-cycle events are full replacements.** In the real data, a small off-cycle change (one signal becoming missing, a share-count update) barely moves the score. In B2 it replaces the whole vector with another company's.
3. **Continuation does not fix ownership changes.** The refinement keeps the same origin company when it also files at that review. That removes the cascade, but whenever a stock leaves the universe its origin's future vintages still have to move to a new name. This is the same transfer mechanism that defeated Null #2, delayed to the next event.

**Implementation correctness:** the no-churn control and the guarantee tests rule out a coding error. The failure is in the design.

## 4. An observation the owner should know (information, not a recommendation)

- In these no-signal panels, **Null #2 also fails** the pre-registered turnover rule. The real value lies below every null world, with gaps of +0.012 to +0.019, exactly as on the real data.
- So in a universe with this much churn, an identity-randomizing null that hands real paths to other names produces more turnover than the real selection **even when the signal carries no information at all**.
- The failures of Null #2 (and of B2) therefore say **nothing about H029's predictive content**. They are a structural property of this null family under the pre-registered adequacy rule.
- This is reported as information only. The owner has ruled out weakening the adequacy rule, and nothing here proposes it.

## 5. Owner decision required

1. **Close H029 / H030 as NOT EVALUABLE now (recommended).**
   - The approved Null #3 cannot meet the persistence requirement it was designed for, and the anti-fork rule excludes a fourth design.
   - Closing now costs nothing and records the finding honestly: H029 / H030 are neither qualified nor rejected; they cannot be evaluated under the pre-registered null-adequacy standard with this universe's churn.
2. **Run B2 exactly as approved on real data**, to obtain the formal adequacy result:
   - run order: structural pre-run → canary → 5,000 worlds → rerun → adequacy;
   - before any world, freeze the Amendment 2 draft unchanged except for its status line;
   - expected outcome on this evidence: failure, so NOT EVALUABLE;
   - cost: about 3–4 hours of the existing backtest node; no extra spend.
3. **Authorise a different null design.** **Not recommended.** It would be a fourth null in substance, contrary to the anti-fork rule. The obvious refinement (continuation) already fails.

## 6. Integrity

| Item | Value |
|---|---|
| QuantConnect runs in this checkpoint | 0 |
| Real-data Null #3 worlds | 0 |
| Thresholds | None (`C_UP_H029` / `C_INCREMENTAL_H030` = `None`) |
| G-TURN-29 status | Not computed or pinned (the structural pre-run was not executed) |
| Returns of any kind | None accessed |
| H029 / H030 | BLOCKED; neither qualified nor rejected |
| Experiments | None added; E031-11..16 never created |
| Holdout | Sealed |

**STOP. Awaiting the owner's decision (section 5).**
