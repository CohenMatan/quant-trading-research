# RR2 — Simplified Research Programme Proposal: QuantConnect-only, price-first (Option 1)

**Date:** 2026-10-19.
**Decisions:**
- D261: owner direction, verbatim in `docs/owner/2026-10-19_rr1_budget_constrained_direction.md`.
- D262: this proposal.

**Status:** PROPOSAL, documentation only. **STOPPED awaiting the owner.**

**Not done:**
- No purchase, no backtest or QuantConnect run, no implementation.
- No change to a frozen experiment, no new hypothesis registered, no Holdout access.

**Recorded under D261:**
- **SYS-1 is closed: NOT RUN — PLATFORM BLOCKED — NO STRATEGY VERDICT.** H028 remains REJECTED.
- D123 (no new data purchase) and D001 (QuantConnect first) stay in force.
- The cost assumptions and portfolio constraints are unchanged.

**Programme totals so far:**
- 30 hypothesis IDs (H001–H030);
- 30 research strategy folders (S001–S032; no S015 or S019 was built; S032 was never run);
- 414 experiment IDs (581 run records, including reruns, recoveries and failures).

---

## 0. Summary

1. **There is a blocker first.** On QuantConnect's current data, the PIT market-cap ≥ $2B universe is **survivorship-biased** as delivered.
   - Market cap was missing for about 18% of eligible stock-months 2011–2017, mostly companies that later disappeared (D187, measured on build 18178).
   - Under D261 that universe cannot be used without your approval.
   - The plan therefore starts with **one aggregate-only universe baseline run**. It measures the gap on today's data and tests two no-cost repairs. You then choose the universe rule (§3).
2. **Infrastructure:** reuse the existing plain-text harness (`qr_harness.py`, no packed data) as the single programme engine. Each hypothesis becomes a short signal plug-in. One small new module computes SPY-relative results inside the cloud and exports only scalars (§1).
3. **Data:**
   - Prices, splits, dividends and delistings are documented from 1998.
   - Market cap is usable from 2010 with the gap above. Before 2010 it is unknown on today's data.
   - Fundamentals: the stream timing is point-in-time, but values were recalculated. Fundamentals stay secondary (§2).
4. **Research:** a first tranche of **at most 3 pre-registered, economically motivated hypotheses**.
   - Each gets one primary specification, run once, with a fixed run budget (at most 3 cloud runs).
   - A pre-set **"Promising" screen** on 2010–2021 decides only whether a candidate deserves independent confirmation. It never validates anything (§5).
5. **Confirmation:** independent confirmation is **separate and stricter**: the unchanged Amendment 3 gates on data no candidate has seen.
   - First choice: 1999–2009 on QuantConnect, **if** the baseline run shows a faithful point-in-time universe there. This needs your approval to amend D033 / D035.
   - Otherwise: the sealed Holdout, used once, then forward tracking (§6).
6. **Honest expectation:** 17 of our hypotheses were price or technical (H001–H014, H018–H021). Every one that was tested failed on 2010–2021; H012 was removed untested. Price-only selection among ≥ $2B US stocks is heavily mined. "No candidate after the first tranche" is a likely, acceptable outcome. The stopping rules make it cheap (§7).
7. **Minimum work before the next strategy experiment:** about 2–3 sessions and 1–2 aggregate-only QuantConnect runs (§8). The QuantConnect plan stays at $24 / month. The Object Store, $0, is used only if you pick the SEC repair.

## 1. Simplest compliant infrastructure

| Layer | Proposal | Reuse | New work |
|---|---|---|---|
| Engine | the existing harness `src/qresearch/lean/qr_harness.py` (48k characters, plain text). It already enforces the approved universe filters (D017 / D022 / D023 / D030 / D061), $7 per order (D039), 10 bps slippage (D024), D044 sizing, D051 no-borrowing, D054 / D062 delisting handling and T+1 open execution. It runs on the new dataset (X801, X993–X998) | yes, unchanged in substance | the 12 dated universe / exchange overrides (D065 / D108) are keyed by old QuantConnect id strings; re-key them by ticker + date and resolve in-cloud (Support guidance, D257). The SEC-correction branch stays off |
| Strategy | one programme host; each hypothesis is a signal module (`qr_sig_<name>.py`) chosen by a parameter, as S001–S017 already did through harness subclasses | pattern reused | one host template |
| Evaluation | in-host computation of the comparison statistics, exported as **scalars**: SPY wealth, an equal-weight-universe control, 5 random-selection controls (same mechanics), the W2 statistic, up / down capture, two-year block shares, a cost-stress replay | `qresearch.wealth` (Amendment 3), `qr_sys1` (SPY shadow), X962 random-pick pattern | one module (`qr_rp_eval.py`) + unit tests on synthetic data |
| Output | own strategy equity curve and own orders (Terms §2.6(e)) + scalars. **No** SPY or benchmark daily paths, no per-stock tables (RR1 §6.7) | runner, metrics module | one change to the engineering rule "compute metrics locally": SPY-relative statistics are computed in-host with the same code (tested bit-identical offline). **Your acknowledgement requested** (§9) |
| Upload guard | the runner refuses any project file that imports a compression or encoding package, or exceeds the limits (50 files, 64k characters) | runner | small; prevents a repeat of E032-01 |
| Platform canary | one standing aggregate digest (universe counts, a fixed control book) rerun only when the default build or dataset changes, not per hypothesis | baseline run (§8) | none beyond §8 |

**Not used:**
- Data v1–v3 tables, identity tables and packed ledgers;
- `qr_p7_export`;
- 5,000-world permutation nulls (§5 explains why they are not needed for single pre-registered specifications).

## 2. What historical data is reliably available today

| Data | Period | Status | Evidence |
|---|---|---|---|
| Daily prices, survivorship-free (incl. delisted) | 1998 → | **reliable** (documented); not re-audited by value since the dataset change, and value comparison is impossible without export | RR1 Q11, R7 |
| Splits, dividends (cents-rounded), delistings, ticker changes (Security Master) | 1998 → | reliable, with known quirks (acquisitions without delisting events D062, ticker-id reuse D167) | RR1 R8 |
| Price ≥ $5, ADV20 ≥ $5M (prior close) | 1998 → | enforceable PIT from bars | harness |
| **PIT market cap** | 2010 → | **GAP about 18% of stock-months, survivorship-biased** (D187, build 18178) | RR1 R2 |
| | 1998–2009 | unknown on today's data (absent on the old beta, R4) | U2 |
| Fundamental stream timing | 2008 → | point-in-time in timing (96–99% day after the SEC filing) | D187 |
| Fundamental values | 1998 → | one third recalculated by Morningstar; fields audited for 2011–2021 only; in-cloud value validation is refused (D185) | RR1 Q4, O2 |
| Our SEC data (filing dates, cover share counts, 8-K, Form 4) | 2009 → (XBRL) | reliable, public, keyed by CIK; usable in-cloud only as plain JSON in the Object Store with in-cloud identity | D257 |

## 3. Universe blocker and alternatives (owner decision required before any strategy run)

**Blocker.**
- The approved universe requires a PIT market cap ≥ $2B.
- QuantConnect's current data omits it for a material, survivorship-skewed share of stock-months.
- Using it as delivered would substitute a survivorship-biased universe, which D261 forbids without your approval.

**Alternatives.** Each is tested in the one baseline run (§8). Nothing is chosen now.

| | Design | Cost | Expected result | Residual risk |
|---|---|---|---|---|
| U-A | **Measure first:** count, per year 1998–2021, the securities that pass every non-cap filter but have no QC market cap, and the share of them that later delist | 1 aggregate run | if today's master has closed the gap, no repair is needed | none if the gap is under a pre-set limit |
| U-B | **In-cloud cap from QuantConnect's own data:** QC share count (split-adjusted to today) × split-adjusted price. The splits cancel, giving cap at the time. Validated in-run against QC market cap where both exist (agreement rate, split continuity; aggregates only) | same run | unknown: depends on share-count coverage for the gap names | D107 warned against share counts as *levels with raw prices*; this pairing avoids that, but needs the in-run agreement test |
| U-C | **SEC cover-share repair** (D111 method, Support-endorsed path): SEC JSON in the Object Store, joined in-cloud by dated ticker evidence | 3–5 sessions; $0 | recovered 68.9% of lost stock-months before (with older identity evidence); in-cloud ticker-only matching may recover less | residual gap needs an explicit owner decision (as Gate K, D192) |
| U-D | Accept the residual with disclosure | 0 | — | survivorship bias: **not recommended** |

**Recommendation:**
1. Run U-A and U-B together in the one baseline run.
2. Pre-set pass rule, to be confirmed by you: the unrepaired gap is ≤ 3% of eligible stock-months in every year, and its later-delisting share is not above the universe's.
3. If it fails, U-C. If U-C also fails, report and stop, rather than accept a biased universe.

## 4. Strategy categories feasible with these data

The categories already examined on 2010–2021 are closed to re-testing and to redesign (D261). They are listed only to rule them out:
- short-term reversal (H001);
- 12-1 momentum (H002, H019);
- 52-week high (H003);
- momentum pullback (H004);
- low volatility (H005; LOWVOL in H027 / H028);
- breakout, squeeze, residual momentum, volume shock, gap, seasonality (H006–H011);
- lottery stocks (H013);
- trend + pullback (H014);
- technical grammar search (H018);
- smooth momentum and the trend factor (H019);
- chart score (H020);
- sector-ETF momentum (H021-A);
- earnings-reaction continuation (H017);
- insider clusters (H025);
- profitability, quality and learned scores (H016, H022–H028).

**Untested categories that fit the data** (candidates for the first tranche; none is registered):

| # | Category | Data | Economic motivation (pre-2018 literature) | Fit / caveats |
|---|---|---|---|---|
| K1 | **Dividend-event drift**: dividend initiations and large increases | Security Master dividends (PIT at ex-date) + prices | under-reaction to payout signals (Michaely, Thaler & Womack 1995; Grullon & Michaely 2002) | only the ex-date is known, not the announcement, so the signal is late. Event counts among ≥ $2B firms need a non-return count first |
| K2 | **Market-state exposure control on a broad large-cap portfolio**: equal-weight eligible universe, cash when SPY is below a slow trend line | prices | time-series momentum / trend as a drawdown tool (Moskowitz, Ooi & Pedersen 2012; Faber 2007) | aligned with the D226 downside objective. **Low power on 2010–2021** (few bear markets): it can rarely be "promising" in development, so its value depends on the confirmation window |
| K3 | **Long-horizon reversal**: 36-month losers among ≥ $2B stocks | prices | overreaction (De Bondt & Thaler 1985) | weak in large caps after the 1990s; low prior |
| K4 | **Equal-weight / diversification structure**: equal-weight largest-N vs cap-weight SPY | prices + cap | rebalancing / size-diversification premium (Plyakha, Uppal & Vilkov 2012) | a structural tilt rather than selection skill. The B901 benchmark exists for 2010–2021, so it is exposed |

Fundamental or SEC signals are admitted only after U-C exists, and only for fields whose PIT integrity is shown on today's data. Not in tranche 1.

**My ranking for tranche 1:**
1. K1, the newest to the programme and the cleanest point-in-time data;
2. K2, the most objective-aligned, but power-limited;
3. K3 or K4, both with a lower prior.

You choose. Each hypothesis is written (`H031`…) and frozen before its run. No hypothesis may be motivated by post-2017 market events.

## 5. Finding candidates efficiently: discovery screen (PROPOSED)

**Window:** development 2010-01 → 2021-12, or 2011 → if the universe needs the SEC repair. **Exposed:** a pass means "worth confirming", never "validated".

**Per hypothesis:**
- one primary specification;
- at most 2 pre-registered sensitivity replays: 20 bps slippage, and a $200K account. These are not selection trials;
- no post-result variants;
- a failed hypothesis is closed.

**"Promising" requires all of:**

| | Criterion |
|---|---|
| P1 | terminal wealth > SPY total return after costs (same capital and dates) |
| P2 | evidence ratio g / SE ≥ 1.0, where SE = max(iid, stationary bootstrap block 126) as in Amendment 3. (The confirmation gate stays at 2.15.) |
| P3 | beats the equal-weight universe control and at least 4 of 5 random-selection controls with the same mechanics |
| P4 | no two-year block contributes more than 50% of the excess log wealth |
| P5 | still > SPY at 20 bps slippage per side |
| P6 | up-capture ≥ 0.85, or down-capture ≤ 0.85 (the D226 participation / protection standard, at least one side clearly good) |

**Why no permutation null:**
- A single pre-registered specification has no search to correct for.
- The D139 lesson (best-of-many configurations beats SPY by chance) applies only to searches, and searches are excluded.
- Multiplicity across the tranche is handled at confirmation (Holm over the tranche).
- The trial count is carried forward in the ledger.

**Costs and constraints, unchanged:**
- $100,000 account;
- $7 per order and forced-liquidation fee (D039 / D049);
- 10 bps slippage per side (D024);
- D044: minimum position $5,000, at most 15 positions;
- 10% maximum initial position;
- D051 no-borrowing with a 15% gap reserve;
- long-only, no leverage, T+1 open.

## 6. From candidate to independent confirmation

A "Promising" candidate is frozen exactly as tested. Confirmation uses the **unchanged Amendment 3 gates**: W1, W2 with g ≥ 2.15 × SE, W3, R1–R4, plus the D226 participation report, with Holm adjustment across the tranche. It runs **once** per candidate, on data the candidate has not seen, in this order:
1. **1999–2009 on QuantConnect.** Only if the baseline run shows PIT market cap with delisted companies there (U2), and only after you amend D033 / D035 (today that window is a stress test only).
   - Costs nothing.
   - It is about 11 years of history our strategies have never seen. The literature has seen it, so pre-registration must not lean on dot-com or 2008 facts.
2. **The sealed Holdout 2022-01-01 → 2026-08-31.** Once, for at most one candidate, after written CP5 approval. About 4.7 years: a falsification check, not proof.
3. **Forward tracking** after a full freeze (D094 category F).
4. **Only then:** you may revisit D123 / D001 (licensed data, RR1 Option 3) for broader independent validation.

If (1) is unavailable, confirmation rests on (2) and (3) alone. That is honest but weak, and the report would say so.

## 7. Stopping rules and budget

| Rule | Value |
|---|---|
| Hypotheses in tranche 1 | at most 3 |
| Cloud runs per hypothesis | at most 3 (primary, determinism rerun, one documented retry) |
| Runs per tranche | at most 12, including baseline and platform canary |
| Session budget | about 6–8 sessions for tranche 1 |
| Stop: zero candidates | 0 of 3 Promising → STOP and report; recommend stopping the programme or a new owner direction |
| Stop: candidate found | ≥ 1 Promising → STOP and propose the confirmation path (§6) |
| Stop: platform | any compliance, engine or dataset blocker → STOP and report; no workaround |
| No rescue | no post-result variants, re-tuning or re-runs of failed hypotheses |
| Money | QuantConnect $24 / month unchanged; Object Store $0 (S-MICRO) only if U-C; nothing else |

## 8. Minimum work before the next strategy experiment

All of this is offline except steps 4 and 5. Nothing starts without your approval.
1. **Programme protocol:** freeze §5–§7 as a pinned document after your review. Offline, about 0.5 session.
2. **Engine hygiene:**
   - re-key the 12 overrides by ticker + date;
   - keep the SEC branch off;
   - add the upload guard;
   - tests. About 0.5 session.
3. **Evaluation module** `qr_rp_eval.py`:
   - SPY shadow wealth, equal-weight and random controls, W2, capture, blocks, cost replay → scalars;
   - offline tests bit-identical with `qresearch.wealth`. About 1 session.
4. **Universe baseline run:** one infrastructure run, aggregates only, plain text.
   - It covers U-A, U-B and the pre-2010 coverage question (U2), and becomes the standing platform canary.
   - **One QuantConnect run, plus at most one retry.**
5. **Your universe decision** (§3), then the first hypothesis write-up for your approval.

## 9. Limitations from the examined history

- **2010–2021 has been used by 30 hypotheses and thousands of variants.** Any pass there is conditioned on that history. It is never independent validation (D261).
- The ≥ $2B price-only space is well mined. A low success rate is expected.
- The new dataset differs from the one most earlier phases used. Past failures remain valid conclusions about the old data, and nothing is re-tested to check them.
- Price values were never compared across datasets (RR1 R7).
- The engine changes weekly and cannot be pinned (O1), so determinism holds only within a snapshot.
- Fundamental values were recalculated and cannot be value-validated in-cloud. They stay out of tranche 1.
- The Holdout is short. Without a valid 1999–2009 window, confirmation power is limited.

## 10. Owner decisions requested

1. Approve this programme structure (§1, §5–§7), or ask for changes.
2. Approve the universe baseline run (§3, §8.4) and its pass rule: gap ≤ 3% of eligible stock-months per year, and no survivorship skew.
3. Acknowledge in-host computation of SPY-relative statistics (§1).
4. Choose the tranche-1 hypothesis categories (§4; recommended K1, K2, then K3 or K4).
5. Note in advance: if the baseline shows a faithful pre-2010 universe, a D033 / D035 amendment will be requested for confirmation use (§6).
