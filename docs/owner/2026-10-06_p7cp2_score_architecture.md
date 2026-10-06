# Owner message 2026-10-06: "Phase 7 — P7-CP2 Score Architecture, Hard Disqualifiers and Market-Regime Design Only"

This is a recorded summary; the full message is in the session transcript. Decision id: **D169**.

## P7-CP1 accepted. Decisions adopted from it

1. **Development window:** 2011-01 → 2017-12. Sector context is reliable from 2011, and year-over-year fundamentals become available.
2. **Fundamental fields:** only the approved seven.
   - Revenue, gross profit, net income and operating cash flow (true TTM).
   - Total assets and equity (PIT snapshots).
   - PIT market cap.
   - Derived features must be economically meaningful, PIT safe, numerically stable, sufficiently covered and defined before any return test.
   - No vendor ratios or other fields.
3. **Financials and REITs** are excluded from the v1 score universe, using the PIT classification rule documented in the spec. There is no technical-only route for them.
4. **Missing data:** a stock without the data for the full score is not eligible on that date. The identical exclusion applies to every future comparison or control universe.
5. **Corporate-event protection:** while an unverifiable split, a spin-off or a similar event contaminates a feature's window, the stock is excluded. The duration follows mechanically from the affected feature's lookback; there is no arbitrary fixed period.
6. **Security-life rule** (D167) kept, with its tests. Earlier phases are unchanged.
7. **Price-series rules:**

   | Use | Series |
   |---|---|
   | Momentum / economic return | Total-return series |
   | Return volatility | Total-return returns |
   | Moving averages / chart trend | Split-adjusted price |
   | Highs, lows, support, breakout, structure | Split-adjusted OHLC |
   | ATR / range | Split-adjusted OHLC |
   | Execution, eventually | Raw price |

   - No total-return synthetic chart for price structure.
   - Every feature states its series.
8. **One share class per company** on each date, chosen deterministically and point in time (e.g. the highest PIT ADV20), with documented tie handling.
9. **Portfolio constraints:**
   - $100,000, long only, no leverage;
   - at most 10% per position;
   - $7 per buy and per sell; 10 bps slippage per side;
   - cash allowed.

   The 10% cap is not lowered to force diversification, and partial investment is acceptable.
10. **Portfolio size** (6 / 8 / 10 / 12) is not chosen yet. A later mechanics-only study chooses it.

## P7-CP2 scope: score architecture and pre-registration ONLY

**The score:**
- **Layers:** Technical Quality, Fundamental Quality and Sector Context. Market Regime is separate and controls exposure only.
- **Structure:** a few economically distinct dimensions, an explicit redundancy map, and modest sector weight (a sector cannot rescue a weak stock).
- **Scale:** an interpretable 0–100 with coarse bands and one primary weighting, justified by evidence, independence, data quality and prior failures.

**Rules around it:**
- a small set of hard disqualifiers;
- a high entry standard;
- entry ≠ holding: hysteresis and a replacement buffer, with numbers deferred;
- winners run (no fixed holding-period exit);
- no forced portfolio filling (any later relaxation ladder needs a hard floor);
- a recommended review frequency and a filing-arrival rule;
- a normalisation method, and a count of all tunable constants.

**Later studies to design** (thresholds may never be selected by returns):
- P7-CP3 availability-only study;
- portfolio-size mechanics (6 / 8 / 10 / 12);
- churn mechanics.

**Testing allowed now:** pure functions plus synthetic or mock-company sanity tests only. Cases A–E for stocks, plus regime cases.

**Not allowed:**
- future returns of any kind (no IC, CAGR or SPY comparison, even as a diagnostic);
- the score run on 2011–2017 market data;
- 2018–2021 and the Holdout;
- purchases.

**Deliverable:** P7-CP2 with 49 items plus answers to A–J. STOP afterwards. Next, after approval: P7-CP3, a Score Availability, Portfolio Capacity and Churn/Cost Mechanics Study.
