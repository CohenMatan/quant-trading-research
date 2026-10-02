# Owner message 2026-10-02: "Approve H016 Position-Sizing Option A With One-Time Top-Up Rule"

This is a recorded summary; the full message is in the session transcript.

1. **Minimum new position:** $4,000 for H016 and its matched books only (candidate, 5 random controls, $200K sensitivity, robustness variants; the same-universe benchmark where applicable). Prior experiments are not modified.
2. **The D051 15% gap reserve is kept** (not reduced to 5%). The initial buy uses the existing order planner and reserve logic.
3. **At most ONE top-up order per newly opened position**, after the initial fill, once actual settled cash is known. There is no further resizing until the next scheduled rebalance.
4. **The top-up is toward the original equal-weight target.** It must never:
   - borrow;
   - exceed the target;
   - violate the position count;
   - make cash negative after commissions and slippage.

   It aims for about 90–100% of the target where cash permits, without forcing 100%.
5. **Minimum top-up amount:** frozen before execution; simple and pre-declared; it considers the $7 commission; it is identical for every book; it is not chosen from returns.
6. **No ongoing resizing:** no top-up on a price fall, no trim on a rise, no restoring equal weight between rebalances.
7. **Replacement positions follow exactly the same process** as the March 2010 formation.
8. **Costs:** top-ups pay the normal commission, slippage and timing.
   - Reported separately: initial buys, top-up orders, top-up commissions, top-up slippage, and the annualised incremental cost.
   - The cost gate (≤ 1.5% a year) is unchanged.
9. **Offline verification with the actual order planner:**
   - $100K: 20 positions form; no new purchase below $4,000 after reserve scaling; top-ups bring investment near the target; no negative cash; no leverage; no repeated top-ups.
   - $200K: the same logic, with no special rule.
   - Also tested: price gaps, commissions, partial slot replacement, insufficient settled cash, a top-up below the threshold, multiple simultaneous fills.
10. **Canary** (non-candidate) verifies:
    - 20 positions form; the reserve is preserved;
    - at most one top-up per new position; the threshold is respected;
    - no leverage; cash reconciles; commissions and slippage are correct;
    - candidate and control mechanics are identical.

    It must not reveal candidate performance.
11. **Freeze the complete H016 spec** ($4,000 minimum, 15% reserve, the exact top-up rule and threshold, the quarterly schedule, 20 positions and all earlier rules), hash-pinned before the first candidate run. Any later change: stop and ask.
12. **Execution authorised** once tests, the offline checks and the canary pass and the spec is frozen. The first candidate run consumes Phase 2 slot 2. **If any prerequisite fails, stop and report; never weaken the rule.**

**STOP CONDITION:**
- no Holdout;
- no change to GP/A, the portfolio size or the reserve;
- no repeated top-ups;
- no new variants.

Produce the development checkpoint and stop.
