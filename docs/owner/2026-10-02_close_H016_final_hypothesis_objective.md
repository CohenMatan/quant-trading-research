# Owner message 2026-10-02: "Close H016 and Design the Final Hypothesis Around the Original Objective"

This is a recorded summary; the full message is in the session transcript.

1. **H016 is closed as Rejected.** It is preserved exactly as tested, with no change to GP/A, portfolio size, rebalance frequency, ranking or any parameter. Phase 2 has used 2 of 3 slots; **one remains.**
2. **Objective (unchanged, explicit):** find an investable long-only strategy that **outperforms S&P 500 buy-and-hold after realistic trading costs.**
   - Not the objective:
     - minimising drawdown;
     - smoother returns;
     - beating equal weight while earning less than SPY;
     - lower volatility at the cost of return;
     - a defensive higher-Sharpe portfolio.

   Those are secondary properties only.
3. **Define "beat SPY" exactly before H017 is frozen.** At minimum:
   - higher net CAGR than SPY over the common development period, after commissions and slippage;
   - no leverage;
   - no clearly unreasonable concentration or drawdown risk.

   Sharpe, MaxDD and Calmar are reported as safeguards. A candidate earning materially less than SPY must not qualify on better risk metrics. The rule is frozen before any H017 backtest.
4. **Review G1–G4 for alignment.**
   - Do not remove the same-universe EW +0.25 Sharpe hurdle automatically.
   - Explain whether it is still a useful screen, whether SPY return superiority should become an additional hard gate, and whether any rule could pass a strategy that trails SPY.
   - Recommend the smallest amendment; do not weaken statistical safeguards.
5. **H017 must be genuinely different.** Not RSI, MA, pullback, breakout, reversal, 12-1 momentum alone, volume, gap, low volatility, MA200 trend, GP/A, or another profitability ratio.
6. **Opportunity review:**
   - Value (e.g. book equity / market cap; one measure only), and other point-in-time-safe fundamental families, only if independently justified.
   - Do not force three alternatives.
7. **Value deserves special, critical consideration:**
   - the large-cap premium;
   - post-publication decay;
   - beating SPY after costs;
   - long underperformance;
   - sector concentration;
   - value traps;
   - accounting comparability;
   - power.
8. **No data mining:** no historical comparisons of B/M, E/P, S/P, CF/P, EV/EBIT or composites. Choose the measure before any strategy-return backtest, from literature, rationale, data reliability and feasibility.
9. **Literature review:** separate pre-2010 evidence, later evidence, practitioner conventions and our inference.
10. **Constraints:**
    - $100K primary, $200K sensitivity;
    - US equities, long-only;
    - no leverage, options or intraday trading;
    - $7 per order and realistic slippage;
    - low turnover; point-in-time data only;
    - prefer holding for months.
11. **SPY is the practical target.** Report CAGR, total return, Sharpe, MaxDD and Calmar vs SPY. The same-universe EW stays as the selection test.
12. **Controls** must separate the universe effect, ranking effect, random luck and the factor effect. They are defined before execution.
13. **Holdout stays locked.** No post-2021 performance may be used for the choice.
14. **Do not force the final slot.** If nothing is credible, say so. The options are then:
    - preserve the slot and reconsider the architecture;
    - get new data or capabilities;
    - start a new programme later.

    Never change the goal from beating SPY.
15. **Deliverable:** the Final Phase 2 Hypothesis Opportunity and H017 Proposal (17 items).

**STOP CONDITION:**
- do not implement or run H017;
- do not calculate competing factors' historical returns;
- do not choose on 2010–2021 performance;
- do not consume slot 3;
- do not access the Holdout;
- commit and stop.
