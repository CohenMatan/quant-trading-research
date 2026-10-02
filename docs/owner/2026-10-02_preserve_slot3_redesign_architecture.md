# Owner message 2026-10-02: "Preserve Slot 3 and Redesign the Research Architecture Around Beating S&P 500 Buy & Hold"

This is a recorded summary; the full message is in the session transcript.

- **State unchanged:**
  - H016 Rejected;
  - 2 of 3 Phase 2 slots consumed; slot 3 unused;
  - **H017 = Value NOT approved**, not implemented or run;
  - Holdout locked.

  Do not run Value or any other candidate yet.

1. **Objective:** starting with the same capital on the same date, the strategy's terminal wealth after realistic costs must exceed S&P 500 buy-and-hold (total return, dividends reinvested).
   - The comparison uses the same capital, start and end, with no leverage, realistic commissions and slippage.
   - Not the objective: beating SPY every year or regime, minimum drawdown, maximum Sharpe, a defensive portfolio, or merely beating same-universe equal weight.
2. **The horizon is not fixed** (1/2–3/5/10 years / full history). Trade holding periods follow the edge's economic source.
3. **New evaluation framework:**
   - **A.** a full-period terminal-wealth table;
   - **B.** rolling 1/3/5/10-year analysis: share of start dates beating SPY, median/mean excess CAGR, distribution, worst and best window. Not required to win every window.
4. **Risk as safeguards.**
   - Report Sharpe, MaxDD, Calmar, volatility, concentration, turnover, costs, worst year and longest recovery.
   - Reconsider the +0.25 Sharpe gate (do not simply remove it): 13% vs 10.5% CAGR with Sharpe 0.93 vs 0.80 should not be rejected automatically.
   - +0.5% CAGR with catastrophic drawdowns must not qualify.
5. **Revisit power.** Separate false-positive protection from the investment objective. Estimate the detectable excess CAGR / terminal wealth for 2010–2021 and for about 2000–2021, using only completed controls and non-candidate information.
6. **Feasibility of extending history toward 2000.** Cover prices, delistings, survivorship, corporate actions, fundamentals, SEC, earnings data, market-cap reconstruction, point-in-time requirements, universe, benchmark and adjustments. Say which families can go back safely. No factor backtests.
7. **Value is not assumed.** Run a broader review of genuinely different sources of edge; no recycled variations of H001–H016.
8. **Families to investigate:**
   - **A.** event-driven / earnings swing (high priority; point-in-time earnings data first);
   - **B.** relative strength vs market/sector (only if genuinely different);
   - **C.** catalyst + continuation (vs price-only breakouts);
   - **D.** medium-term fundamentals (value, investment, issuance/payout, distinct quality, justified combinations).
9. **"Swing" is a style, not a hypothesis.** For each: source of edge, persistence, triggering event, gross edge per trade, duration, frequency, turnover, survival of $7 per order + slippage.
10. **Capital:** $100K primary, $200K sensitivity (never selects or rescues). Portfolio construction is per family. If the $4,000 minimum makes a strategy noisy, identify it as an account-model constraint; do not change it yet.
11. **Process:** evidence → point-in-time feasibility → exact pre-registration → frozen parameters → development → terminal wealth + rolling + controls → robustness → Holdout only if qualified. No parameter search.
12. **The Holdout stays untouched** for every choice; slot 3 unused.
13. **External research by period:** before 2000 / before 2010 / after 2010; decay; large-cap US; long-only; practical evidence. Academic anomaly vs realistic personal-account strategy.
14. **Deliverable:** the "Phase 2 Research Architecture and Final-Slot Opportunity Review" (20 items).

**STOP CONDITION:**
- no H017, Value, PEAD or swing runs;
- no candidate-factor return comparisons;
- no optimisation;
- no Holdout;
- slot 3 not consumed.

Data/metadata inspection, non-return integrity audits, literature, and completed-control power analysis are allowed. Commit and STOP.
