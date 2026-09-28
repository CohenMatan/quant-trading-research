# Research Cycle C01 — plan (registered before any C01 run)

**Scope.**

- Five hypotheses (H001–H005), five strategies (S001–S005), **19 pre-declared IS variations**.
- IS only: 2010-01-04 → 2017-12-31.
- Settings: $100K account, $7/order commission, 10 bps slippage, $5K minimum position, ≤ 15 positions, ≤ 10% per position.

**Procedure.**

1. Run all 19 IS variations. Every run is registered, including failures.
2. Apply the approved IS screen (D036) to each variation. The benchmark is E901-02 over the same dates.
3. For a hypothesis with at least one variation passing, pick the best-passing variation **by the IS gate metric only** (net Sharpe). Then run the IS robustness battery:
   - parameter plateau at ±20–50%;
   - slippage at 2×, 4× and 6×;
   - sub-periods (thirds of IS);
   - the IS stress episodes;
   - PBO across the hypothesis's variations.
4. Checkpoint 3 reports all results, the trial count, the survivorship-gap disclosure (D043), and proposes which strategies (if any) to promote to VAL.
   - **No VAL, WF or HOLDOUT run happens in C01.**
   - Advanced validation waits for owner approval at CP3.

**Hindsight rule.** No hypothesis or variation may be motivated by events after 2017. All five rely on pre-2018 literature.
