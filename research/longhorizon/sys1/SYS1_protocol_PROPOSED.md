# SYS-1 (corrected) — defensive sleeve + SPY, single-account implementation test — PROTOCOL (PROPOSED — NOT APPROVED, NOT FROZEN)

> **SUPERSEDED (D252, 2026-10-19):** the owner approved OD-1..OD-7; the finalised, frozen protocol is `SYS1_protocol.md` (this draft is kept unchanged below as the D251 record).

**Owner decision:** D251 (`docs/owner/2026-10-19_oc2_closure_sys1_redesign.md`). Design only.

**Status: PROPOSED.** Nothing in this file is authorised to run.
- It becomes executable only after an owner decision that:
  - answers OC-CP6 §16 items OD-1 to OD-7;
  - approves the canary and the one evaluation run.
- On approval, the chosen options are written in, the file is frozen (SHA-256 recorded), and the run configurations are written. No result exists, and none was computed for this design.

Checkpoint: `docs/checkpoints/OC_CP6_oc2_closure_corrected_sys1_design.md`.

## 1. Question and interpretation

**Question.** In one investable account with real costs, does a fixed allocation of a defensive stock sleeve plus SPY give an economically meaningful benefit over SPY buy-and-hold? Two parts:
- **Q1:** does it improve risk-adjusted or downside behaviour?
- **Q2:** does the defensive component add enough wealth to justify its complexity?

**Interpretation limits:**
- The period is 2015–2021, already examined for H028, LV15 and SPY.
- A favourable result is **development-consistent only**. It cannot validate H028, establish stock-selection alpha, or justify opening the Holdout by itself.
- An unfavourable result weakens the case for the tested architecture at the tested weight, not for every defensive allocation.
- H028 remains **REJECTED — Frozen Defensive Research Reference**.

## 2. Account and capital (requires OD-2)

- **One account:**
  - capital **$200,000** (OD-2; the programme baseline remains $100,000, under which the stock-sleeve systems are infeasible: OC-CP6 §5);
  - long only; no leverage; no borrowing; cash never negative.
- **Cash** earns 0% in every arm (as in the frozen H026–H028 simulator). This is disclosed; T-bill yields were 0–2.4% in 2015–2021.

## 3. Allocation rule (fixed, not optimised)

- **Split:** 50% defensive sleeve / 50% SPY. This is a round equal split, proposed in OC-CP1 before this design. It is not fitted to any result, and there is no weight grid.
- **Sleeve sizing basis:** at every monthly review, the sleeve's basis is 50% of account equity at the entry open. Each **new** sleeve position is bought at basis / 15. Held positions are kept, not trimmed or topped up (frozen H028 rule).
- **SPY:** absorbs the residual. After the sleeve's sells and buys at the entry open, SPY is bought or sold so that cash returns to 0 (E1) or to the buffer (E2).
- **No other rebalancing,** and no calendar rebalancing to exactly 50 / 50. The sleeve weight floats with its holdings between reviews.

## 4. Position limits and sizes (requires OD-1)

- **Stock positions:** at most 15 (H028 / LV15 Top-15, FF12 cap 3: frozen).
- **ETF holdings (SPY, SPLV, USMV)** under OD-1:
  - not counted in the 15-position limit;
  - exempt from the 10% single-position cap;
  - subject to every cash, cost and execution rule.
- **Minimum new stock position: $5,000** (D041 / D044).
  - A new sleeve buy whose amount, after any cash scaling, is below $5,000 is **skipped**. The slot stays empty and the cash goes to SPY.
  - Skipped buys are counted and reported.
  - At the start the target is $6,667; it would bind only after a 25% fall of the account below $200,000.
- **10% initial cap:** satisfied by construction. At entry a stock is 3.3% of the account and 6.7% of the sleeve.

## 5. Arms (one run; fixed list; no selection among arms)

| id | arm | role |
|---|---|---|
| A0 | SPY buy-and-hold ($200,000) | main wealth benchmark |
| A1 | **H028 sleeve (frozen S030, λ = 100, Top-15) + SPY, 50 / 50** | **primary system** |
| A2 | LV15 sleeve (frozen `qr_h027.lv15`) + SPY, 50 / 50 | transparent stock-defensive comparator |
| A3 | SPLV + SPY, 50 / 50 (two ETF holdings; at each monthly review SPLV is traded back to 50% of account equity at the next open and SPY takes the rest — the ETF analogue of the sleeve-basis rule) | transparent ETF-defensive comparator (OD-4; only if the canary verifies SPLV) |
| BM-X(Ai) | SPY + cash at the ex-ante beta of Ai (§7), one per A1–A3 | exposure-matched control per system |
| D1 | H028 alone, $100,000 (replay of E030-05) | historical reference; reproduction check |
| D2 | 90% SPY + 10% cash, fixed | non-gating diagnostic (OC-CP1 control; disclosed mismatch) |
| D3 | USMV + SPY, 50 / 50 | non-gating diagnostic, only if verified |

- QQQ is excluded (owner D251).
- No $100,000 stock-sleeve arm: it is infeasible (OC-CP6 §5).

## 6. Execution and costs (requires OD-3)

- **Decision:** the frozen H028 month-end review. Execution at the next session open. Universe, features, PIT rules and selection are exactly frozen S030 / Data v2.1.
- **E1 (recommended):** the frozen H028 shadow-book convention for **every** arm:
  - notional, fractional orders at the open price;
  - buys at open × 1.001 and sells at open × 0.999;
  - $7 per executed order;
  - total-return valuation of every holding (dividends reinvested inside the position, for stocks and ETFs alike);
  - delisted stocks valued at the last real close and turned into cash at the next review.
- **E2 (alternative):** the D051 whole-share model (2% buffer, 15% gap reserve, settled cash) for every arm. This changes H028's frozen mechanics, so A1 would be labelled "H028 under D051", not frozen H028.
- **Robustness:** every arm repeated at 0.20% slippage per side, with the same selections and no refit.
- **ETF expense ratios** are embedded in ETF prices; nothing is added.

## 7. Ex-ante exposure-matched control BM-X (prospective)

- At each review t, the control holds SPY weight w_t = β̂_t(Ai), the ex-ante beta of the system's **current planned holdings**:
  - Σ weight × Blume-adjusted (0.67 β + 0.33) trailing-252-session daily OLS beta to SPY, using prices before t only;
  - SPY = 1; SPLV's own trailing beta for A3.
- The rest is cash at 0%.
- The SPY position is traded to w_t at the next open, at the same costs.
- The rule uses no 2015–2021 outcome. It never uses H028's realised 0.76.
- The truncation test (canary C7) proves that β̂_t uses only data before t.

## 8. Data (dependencies for the canary)

**Already verified:**
- SPY prices and dividends (E028-05 / E029-05 / E030-05, SPY $262,325.46 at $100,000);
- frozen Data v2.1 universe and features;
- LV15 picks.

**Not yet verified** (canary C4; QuantConnect prices only, aggregates only, no data export):
- **SPLV** (QuantConnect id SPLV UWBCA8CFMB1H; inception 2011-05-05);
- **USMV** (V0WRDXSSH205; inception 2011-10-18).

The ids are present in QuantConnect's security master (E970 identifier export), but no price, split or dividend history was ever checked.

**Not available:**
- SPY constituent weights, so look-through overlap uses a proxy (§10);
- a verified T-bill ETF, so cash earns 0%.

## 9. Canary (X032 / E032-01) — all must pass, otherwise STOP and report

| check | requirement |
|---|---|
| C1 | Engine at s = 1, $100,000, no $5,000 overlay → reproduces E030-05 exactly: wealth $328,294.91, the same 84 pick lists, commissions $5,789 |
| C2 | s = 0 → SPY buy-and-hold $262,325.46 at $100,000 (and × 2 at $200,000 within cent rounding of the fixed $7 costs) |
| C3 | LV15 at s = 1 → $220,156.03 |
| C4 | SPLV / USMV daily bars 2014-01 → 2021-12: sessions present = SPY sessions; no gap > 3 sessions; dividends and splits present (counts only) |
| C5 | Single-ledger identity every session: cash + Σ holdings = equity; cash ≥ 0; ≤ 15 stocks; no new stock buy < $5,000 with the overlay on |
| C6 | Costs recomputed by hand for one review |
| C7 | BM-X β̂_t unchanged when data after t is truncated |
| C8 | Peak memory ≤ the node limit; project files ≤ 50 (S030 uses 50: S032 must replace null-mode files, not add) |
| C9 | QuantConnect compliance: aggregates and digests only; a rejection means STOP (D185) |

## 10. Reported outputs (descriptive, every arm)

- terminal wealth, CAGR, volatility, Sharpe, MaxDD, time under water;
- beta, up- and down-capture (P11-CP2 definitions), strong-up capture (diagnostic);
- yearly log-relatives versus A0 and versus the arm's BM-X;
- 2015–2017 and 2018–2021 sums; the result without 2018 and 2020 (descriptive);
- rolling 36-month share ahead;
- commissions, slippage, turnover, cash share, skipped buys;
- sleeve versus SPY contributions;
- look-through overlap proxy: for each held stock, its PIT market cap / Σ PIT market cap of the ≥ $2B eligible universe, × the SPY weight. Diagnostic only, no netting.

## 11. Falsification screens (prospective; not tuned; for A1, and reported for A2 / A3)

| screen | criterion | note |
|---|---|---|
| FS-1 | Canary passes; run complete; zero account-rule violations | implementation |
| FS-2 | Terminal wealth Ai > BM-X(Ai), net at 0.10% | value beyond reduced exposure (redesigned P-2) |
| FS-3 | Terminal wealth Ai ≥ A0 (SPY), net at 0.10% | primary wealth question (P-1); for A1, predictable from known components (OC-CP6 §11) |
| FS-4 | FS-2 and FS-3 still hold at 0.20% slippage per side | cost robustness (P-5) |
| FS-5 | Versus BM-X(Ai): no calendar year > 50% of Σ yearly log-relative, Σ 2015–2017 > 0, and Σ 2018–2021 > 0 | not episodic (P-4, as defined in OC-CP1) |
| FS-6 (A1 only) | Terminal wealth A1 > A2 and > A3 (if A3 exists) | complexity justified (P-3) |

**Classification:**
- **NOT EXECUTABLE** if FS-1 fails.
- **NOT SUPPORTED** if any of FS-2 to FS-6 fails.
- Otherwise **NOT FALSIFIED — DEVELOPMENT-CONSISTENT**. This is never "qualified" or "validated".

Q1 is answered descriptively. Q2 is answered by FS-2, FS-3 and FS-6.

## 12. Stop conditions and budget

- **Runs:** one canary (E032-01) and one evaluation (E032-02), which computes all arms and both slippage levels in one run.
- **Retries:** at most two technical retries for documented infrastructure failures, with identical code and settings.
- **No changes after any result:** no tuning, no weight / K / arm changes and no additional arms.
- **Cost:** within the existing $24 a month QuantConnect plan. No purchase.

## 13. Explicit limitations

- In-sample, examined data; 84 months; no significance claim.
- H028's edge is unvalidated: its p-value is structurally suspect (D238) and the repair was not validated (D239).
- H028 is Top-K fragile (Top-10 / Top-20 S 0.095 / 0.062 vs 0.224) and has high turnover (about 7.5× a year).
- Its advantage came from SPY-down months, concentrated in 2018 and 2020.
- The cash yield is 0%. E1 fills are idealised notional orders.
- Look-through overlap is a proxy.
- Results at $200,000 do not carry over to $100,000, where this design is infeasible.
