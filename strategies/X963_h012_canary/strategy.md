# X963: C03 H012 infrastructure canary

It runs the unchanged S012 code (`s012.py` and `signals.py` are byte copies, pinned by a test) with **non-candidate** parameters: RV(10), weekly rescaling, 2010–2011.

**Checks, on QuantConnect:**

- The SPY RV computed from the harness window equals RV computed from fresh point-in-time history.
- The basket equals the 15 largest by the universe filter's market cap, from that day's selection.
- Orders are placed only on event closes and inside the rebalance window.
- The invested fraction after each completed rebalance, compared with e × 98%.
- Control B's pre-start targets come only from pre-start history.

It is verification, not a trial.
