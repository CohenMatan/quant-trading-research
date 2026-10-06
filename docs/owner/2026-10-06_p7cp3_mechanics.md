# Owner message 2026-10-06: "Phase 7 — P7-CP3 — Score Availability, Portfolio Capacity, Churn and Cost Mechanics Study. NO FUTURE RETURNS — NO PERFORMANCE TESTING"

This is a recorded summary; the full message is in the session transcript. Decision id: **D171**.

## Frozen (P7-CP2 accepted)

1. **Score v1 is FROZEN exactly as P7-CP2 specified** (`research/phase7/P7_score_spec.md`, `qr_p7_score.py`, hash-pinned in `qresearch.p7score`):
   - Technical 40: trend 15, 12-1 total-return momentum 15, low volatility 10.
   - Fundamental 45: GP/A 15, cash conversion 10, equity/assets 10, YoY revenue growth 10.
   - Sector 15: sector breadth vs market breadth.
2. **The seven hard disqualifiers stay unchanged** and may not be relaxed.
3. **All data, fidelity and price-series rules are frozen.** A genuine bug is documented; if fixing it would change the score definition: STOP and ask.
4. **Review cycle:** monthly full review; a weekly check looks only at hard disqualifiers of holdings (no entries, re-ranking or rotation). Filings update the score at the next monthly review, earlier only through a hard disqualifier.
5. **10% is the maximum INITIAL position**, not a rebalance target. Winners are not trimmed. P7-CP3 may only *propose* candidate concentration caps for grown winners (e.g. 15% / 20%); they are not backtested.
6. **No forced filling.**
7. **Rejected:** the earlier automatic selection rules ("strictest threshold with ≥ 10 candidates", "largest K ≥ 80% filled"). Claude does not choose final parameters: present trade-offs and STOP.

## What P7-CP3 measures (scores and mechanics only)

- Entry thresholds exactly **90, 85, 80, 75** (nothing lower).
- Candidate counts, score and layer distributions, composition, persistence, crossings, sector concentration, market-regime frequency (regime never changes a score or its order; exposure percentages NOT frozen).
- Capacity for Max 6 / 8 / 10 / 12 positions per threshold, with the 10% cap implication (6 → 60% maximum initial gross, 8 → 80%, 10 → 100%, 12 → 100% with 10%-capped sizing).
- Ranking when slots are limited: frozen total score, then deterministic ties.
- Churn profiles for entry E: **H1 Tight** exit E − 5, buffer 3; **H2 Balanced** exit E − 10, buffer 5; **H3 Patient** exit E − 15, buffer 10. Replacement: candidate ≥ held + buffer. Disqualifier exits independent; a freed slot may be filled by a candidate. No time exit.
- Cost mechanics only: $7 per buy and per sell, 10 bps slippage per side, a documented mechanical $100K notional ($200K sensitivity); classes < 0.5%, 0.5–1.0%, > 1.0% of capital per year; no automatic ≤ 1% rule.
- Relaxation ladder: design only. Weekly disqualifier burden. One-share-class audit. Exclusion funnel per year. Missing-data protection kept.
- One **non-trading** QuantConnect score / data export run (expected 0 orders), then offline mechanics.

## Not authorised

- Future returns of any kind (no `future_return`, `next_month_return`, `forward_*`, `alpha`, `future_SPY` columns; preferably such data are never retrieved); strategy returns; SPY returns, CAGR or excess; Sharpe, drawdown, win rate, profit factor; IC or bucket returns.
- Selecting any parameter because it would have made more money; choosing the final entry, exit, buffer, max positions, regime ceilings, relaxation ladder or grown-winner cap (the owner selects them).
- Tuning the score, its weights or disqualifiers.
- 2018–2021 data; the Holdout (2022-01-01 → 2026-08-31); purchases.

## Implementation readings recorded by Claude before the run (D171, minor implementation decisions)

1. **Reviews from the session calendar:** monthly review = the last session of each calendar month (LEAN exchange calendar: the next market open falls in another month), 2011-01 → 2017-12 = 84 reviews. Weekly check = the last session of each ISO week, from the first week after the 2011-01 review to 2017-12-29. The data of a review are those of the universe selection reflecting that session's close (QuantConnect stamps it the next calendar day).
2. **Run window:** official start 2011-01-03, end 2017-12-31, history-only warm-up from 2008-07-01 (the 2010 reviews exist only as the revenue-baseline ledger; nothing is scored in 2010). Price history from 2007-01-01 (as X992) to 2017-12-29.
3. **Revenue baseline ledger:** the revenue True TTM recorded at the month-end review 12 calendar months earlier **for the securities eligible at that review** (the X991 v1.1 construction audited in P7-CP1). A stock not eligible 12 months earlier has no recorded baseline → H2. A diagnostic (not used by the score) counts how many such H2 cases had a vendor revenue True TTM in the store 12 months earlier.
4. **Weekly hard-disqualifier check:** H1, H2 and H7 from the point-in-time SIC and fundamentals known at the weekly selection (H2 / H7 use the revenue baseline of the score in force, i.e. of the latest monthly review); H3, H4, H5, H6 from the price panel at the weekly session. Frozen holdings (H4) skip H3, H4, H6 (frozen `weekly_check`). A holding is sold at a weekly check only for a hard disqualifier.
5. **Ranking / ties when slots are limited:** the frozen `plan_review` order — total score desc, then PIT ADV20 desc, then security id asc. The weakest holding (replacement, regime cap) is the lowest score, then the lower ADV20, then the smaller id.
6. **Sell-then-rebuy (whipsaw), pre-registered before counting:** a security bought at a review within **3 monthly reviews** after it was sold (normal exit, disqualifier exit or replacement) in the same security life. Reported per profile as events per year and as a share of exits.
7. **Holding duration:** calendar sessions from the entry review to the exit (monthly review or weekly check), reported in months (21 sessions); positions open on 2017-12-29 are censored (reported separately; not counted as exits).
8. **Cost notional (mechanical, not equity):** every buy and every sell is charged on the same notional = $100K × min(10%, 100% / K) (K = max positions): $7 commission per order + 10 bps × notional slippage. $200K sensitivity: the same with $200K. Annual cost as % of the respective capital. No price, equity or return is used.
9. **Capacity:** at each monthly review, the number of eligible candidates ≥ the threshold (after one share class per company) vs K; "all slots fillable" = candidates ≥ K. A separate shadow-book utilisation (holdings / K after each review, no returns) is reported for the churn profiles.
10. **Regime cap:** not applied in the churn study (regime ceilings are not frozen); regime frequency is reported separately.
