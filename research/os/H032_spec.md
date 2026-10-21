# H032 — Cash-Generating, Growing Net Share Reducers (OS-1 revised): specification and evaluation protocol (FROZEN)

- **Owner decisions:** D274 (offensive stock-selection direction), D276 (quality filters), **D278** (revised design approved; this freeze; the canary only).
- **Design record:** `docs/checkpoints/OS_CP1_offensive_score_candidate_selection_first_experiment_design.md` §5–§8 and §11 (Revision 1).
- **Frozen before any strategy return.** SHA-256-pinned with the host, the modules, the builder, the comparative verification, the canary evaluation rule and both SEC objects in `qresearch.os1` (`tests/test_os1_canary.py`). Nothing here may change because of a canary or strategy result. A genuine bug → STOP, document, ask the owner.
- **Status of everything H032 produces: EXPLORATORY.** 2010–2021 is exposed development data and never independent validation (D261). RR6 stays INCONCLUSIVE: the repaired universe's residual survivorship uncertainty is not resolved. H031 stays DRAFT and parked. The Holdout (2022-01-01 → 2026-08-31) stays sealed.
- **Authorised now (D278):** this freeze and ONE aggregate-only canary C-OS1 (E807-01; E807-02 only after a documented infrastructure failure). **Not authorised:** any strategy return, the R1 / R2 runs of §9, the Holdout, any purchase, a new data source, identity repair, or any change to thresholds.

## 1. Hypothesis

Among US common stocks of at least $2B market cap, companies that **generate operating cash**, whose **revenue is growing**, and that have **reduced their share count the most over the last twelve months** outperform SPY after realistic costs.

- The repurchase ranking is the signal. The two financial conditions are **eligibility filters**, not scoring factors, and their thresholds are signs (> 0). Nothing is weighted, learned or tuned.
- **Caveats stated before any result** (D278 item 1):
  - positive operating cash flow does not prove that repurchases were funded from operations;
  - positive revenue growth does not establish future outperformance;
  - beating random books from the filtered pool (B2) supports the incremental ranking hypothesis, but does not show that the filters improve the original unfiltered strategy.

## 2. Data (public SEC data only; no purchase; no new source)

| Object | Object Store key | SHA-256 | Content |
|---|---|---|---|
| UCR-1 per-filing object (D270, unchanged) | `rr/ucr_sec_v1.json` | `ba3ab515f6fad602f8638279927c4b5b3c417577851f7748891ff23be52a4a82` | per registrant: periodic filings [filed, ticker prefix, common flag, cover share count, cover as-of date] and public floats |
| H032 extension (D278 item 6, separate) | `rr/os1_sec_v1.json` | pinned in `qresearch.os1` (manifest `research/os/os1_sec_v1_manifest.json`) | per registrant: SIC of every periodic filing (parallel to the UCR-1 filing list) and every **original** 10-K / 10-KT as [filed, period end, OCF, revenue, prior-year revenue] |

- The extension is built by `research/os/build_os1_sec.py` from the same local SEC cache (XBRL filing index, companyfacts). It checks the parent object's SHA-256. The original object is not modified.
- Values come only from facts carrying **that filing's accession number**: annual duration 350–380 days, ending within 7 days of the filing's period end. The prior-year comparative ends 355–375 days before the period end and comes from the **same tag** as the current value, in the **same filing**. Several different values → ambiguous → missing.
- The same-filing comparative was verified offline before this freeze against a pre-registered criterion (`research/os/os1_verify_comparatives.py` → `.json`): **ADEQUATE** (pooled 2013–2021 joint coverage 81.4% vs 79.4% for consecutive filings; every year 2013–2021 at least 79%).

## 3. Universe, point-in-time rules and identity

At each month-end session t from 2010-01 to 2021-11 (the session calendar; QuantConnect selection is stamped the next calendar day):

1. **Repaired universe** (primary): QuantConnect vendor-eligible securities (US common on the approved exchanges, vendor market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M) **plus** the securities restored by the frozen UCR-1 repair (`qr_ucr.Repair`, unchanged).
2. **Vendor universe** (shadow): vendor-eligible securities only.
3. **Identity** (`qr_os1.identity`, the UCR-1 rules applied to every security): a registrant claims its ticker prefix from its latest periodic filing filed **strictly before t**, at most 200 days old and common; a claim is used only if exactly one registrant claims the prefix, exactly one QuantConnect ticker normalises to it, and that ticker carries no class suffix ('.' or '-'). Unmatched securities have no SEC inputs.
4. **SEC rows** are usable only from the day after their filing date. A row filed on t is never used at t.
5. **H032 scope** (D278 item 3, for H032 only): exclude a security whose registrant's **latest periodic filing filed before t** carries SIC 6000–6799 (financials, insurers, REITs). Unknown SIC (no identity or missing SIC) cannot be verified as non-financial and is not selectable.
6. **H032 denominator** = eligible securities not known to be financial (unknown SIC included and counted as not covered).

## 4. Signal: net share issuance (unchanged from OS-CP1 §5.1)

For a matched security at t (`qr_os1.nsi_score`):

1. New count S₁: the registrant's latest single-value cover count filed before t and at most 200 days old; as-of date e₁ < t.
2. Old count S₀: among counts filed before t, the one whose as-of date e₀ is closest to e₁ − 365 days, with |e₀ − (e₁ − 365)| ≤ 45 days (ties: the earlier filing).
3. Split adjustment: S₀ₐ = S₀ × F(e₁) / F(e₀), where F(d) is QuantConnect's split factor for the security at the session close of day d, recorded live from the universe stream. Unknown F at either date → missing.
4. Sanity bound: S₁ / S₀ₐ outside [2/3, 3/2] → missing.
5. NSI = ln(S₁ / S₀ₐ) × 365 / (e₁ − e₀); **OS = −NSI** (more repurchase → higher).

## 5. Filters (`qr_os1.Ext.annual`)

From the registrant's **latest original 10-K / 10-KT filed strictly before t**, with period end < filing date and t − period end ≤ 456 days:

| Filter | Rule |
|---|---|
| F-OCF | operating cash flow (`NetCashProvidedByUsedInOperatingActivities`; continuing-operations variant if absent) **> 0** |
| F-REV | revenue / same-filing prior-year revenue − 1 **> 0** (prior > 0) |

- No fallback to another filing or definition (D278 item 2). A missing input → not selectable and counted as not covered.
- **Covered** = identity, known non-financial SIC, OS, OCF and revenue growth all present. **Passing** = covered and both filters > 0.

## 6. Coverage gates and the mechanical start (D278 item 4)

| Gate | Rule |
|---|---|
| G-COV1 | **Start review** = the first review with joint coverage (covered / H032 denominator, repaired universe) ≥ 70%. From it, coverage ≥ 65% at every review |
| G-COV2 | Coverage of stock-months whose security is still in the stream 24 months later minus coverage of those whose security leaves within 24 months ≤ 10 points, pooled over the reviews from the start whose 24-month horizon ends by the last stream day (2021-12-31). Later reviews are **CENSORED** (reported, never treated as passed; the Holdout is never read). Exit information is a retrospective audit only, never used for selection |
| G-COV3 | Coverage of restored (SEC-repaired) stock-months ≥ coverage of vendor stock-months − 10 points, pooled from the start |

- **Subperiods:** A = start → 2015-12; B = 2016-01 → 2021-11. The 2016 boundary is fixed. If A has fewer than 36 reviews → **SHORT**: reported before any return analysis, STOP for the owner.
- Coverage is reported separately for vendor-only, restored and later-disappearing securities, and for the vendor universe.

## 7. Books (selection by name; identical timing for all)

Reviews from the start review; a book's holdings change only at reviews. Ties: ADV20 descending, then security id.

| Book | Pool and rule |
|---|---|
| **B1 (primary)** | passing securities of the repaired universe; Top 15 by OS; a holding stays while its rank ≤ 30 and it still passes (`qr_os1.plan`) |
| B0 (diagnostic only) | original OS-1: every scored security of the repaired universe (no filters, no SIC exclusion); same rule. **Never promoted if B1 fails** |
| B2 × 5 | random from the **passing** pool, seeds 20261121–25; turnover-matched: as many names replaced as B1 enters at that review (`qr_os1.random_step`) |
| Random × 5 | random from the **covered** pool (H032 scope, before filters), seeds 20261131–35, turnover-matched |
| Beta-matched × 5 | one control per B1 holding from the covered pool's ex-ante beta quintile of the B1 name (252 sessions of daily adjusted closes vs SPY total return, ≥ 200 return pairs), seeds 20261141–45 (`qr_os1.beta_step`) |
| Equal weight | the covered pool |
| Momentum 12-1 Top-15 | covered pool ranked by adjusted close at the review one month back / twelve months back − 1; same Top-15 / 30 rule (known-factor comparison) |
| Vendor-universe B1 | B1's rule on the vendor universe, with the same filters wherever SEC data exist (D278 item 5) |
| SPY | total-return buy-and-hold |

## 8. Canary C-OS1 (the only authorised run)

**X807** on QuantConnect's default build, 2009-05-01 → 2021-12-31, no warm-up, **0 orders, no returns**, no identifiers exported (`OS1|` aggregate lines only). It builds the universes, identity, signal, filters, coverage, start and books by name, and recomputes every book from stored inputs at the end. The evaluation rule `research/os/OS1_eval.py` (pinned) applies:

| # | Gate |
|---|---|
| C1 | Point in time: 0 SEC rows used on or after the review day (cover counts, annual reports, SIC) |
| C2 | Identity: 0 reviews with a registrant matched twice; 0 restored securities without the point-in-time identity |
| C3 | Same-filing annual inputs: from the start, every calendar year's pooled F-OCF input coverage and F-REV input coverage ≥ 70% of the H032 denominator |
| C4 | Share counts and splits, pooled from the start: unknown split factor ≤ 5% of count pairs; bound exclusions ≤ 5% of pairs with known factors; split-adjusted pairs inside the bound ≥ 90% (at least 20 such pairs) |
| C5 | G-COV1 (start found and equal to the in-run start; ≥ 65% thereafter) |
| C6 | G-COV2 (gap ≤ 10 points; at least 30 leaving stock-months, else UNEVALUABLE = not passed; censored reviews reported) |
| C7 | G-COV3 (gap ≤ 10 points; at least 30 restored stock-months, else UNEVALUABLE = not passed) |
| C8 | Feasibility: B1, vendor B1, B0, B2 × 5 and random × 5 hold 15 names at ≥ 99% of reviews from the start; momentum at ≥ 99% of reviews where momentum exists; beta-matched controls drawn for ≥ 95% of B1 entries |
| C9 | Determinism: every book's in-run recomputation equals its online digest |
| C10 | Subperiod A ≥ 36 reviews |

- **PASS:** all of C1–C10. **SHORT:** only C10 fails → STOP for the owner before any return. **FAIL:** anything else → STOP; no redesign, relaxation or second canary (one documented infrastructure retry only).
- Reported, never gating: share of eligible companies removed as financials; FF12 sector shares of the denominator, the passing pool and B1 holdings; NSI and growth quantiles; reasons for missing inputs; identity outcomes; B1 entries and distinct names per year; coverage by group and by year.
- A canary PASS authorises nothing. R1 / R2 need a separate owner decision.

## 9. Evaluation protocol for R1 / R2 (frozen now; NOT authorised)

**Mechanics** (OS-CP1 §5.2): $100,000; review every month-end session; market orders at the next session's open; new position = equity / 15 capped at 10% of equity, $5,000 minimum, D051 settled-cash funding with the 15% gap reserve; no trimming, top-ups or leverage; idle cash earns nothing; $7 per order; slippage 10 bps per side (R1) and 20 bps (R2); delistings and acquisitions by the harness rules (D054 / D062). B1 trades in LEAN; every control is a shadow book with the same mechanics and costs. Decisions from the start review through 2021-11-30; the run ends 2021-12-31.

**Fidelity pre-gate:** the shadow engine replays B1 itself; terminal wealth within 1% of LEAN's and every monthly return within 0.5 points. Otherwise R1 is void → STOP.

**Regimes** (labels only): B1 SPY-up months (SPY total return > 0); B2 bull state (SPY trailing 12-month total return > 0 at the previous month-end); B3 strong-up months (SPY ≥ +3%).

**Gates** (all on R1 unless stated):

| # | Gate |
|---|---|
| O1 | Terminal wealth > SPY after costs **and** CAGR excess ≥ +1.0 point a year |
| O2 | g / SE ≥ 1.0 (Amendment 3 W2 statistic: d = daily log excess vs SPY, g = 252 × mean(d), SE = max(iid, stationary bootstrap q = 1 − 1/126)) |
| O3 | Upside capture in SPY-up months ≥ 1.00 and capture spread (up − down) ≥ +0.05 |
| O4 | Monthly regression on SPY: alpha > 0 with t ≥ 1.0 (Newey–West lag 2); beta reported |
| O5 | CAGR above the equal-weight book, above ≥ 4 of 5 random books, above ≥ 4 of 5 beta-matched books **and above ≥ 4 of 5 B2 books** |
| O6 | Excess over SPY and over equal weight positive in both subperiods A and B |
| O7 | No calendar two-year block contributes more than 50% of the summed log excess |
| O8 | O1's wealth condition holds at 20 bps (R2) |
| O9 | The vendor-universe B1 beats SPY and its own equal-weight book |

- **Reported only:** B1 vs B0, B1 vs momentum (and correlation), downside capture, drawdown, volatility, Sharpe, excess in B2 / B3 regimes, turnover, costs, coverage, the share of profit from restored names, sectors, the largest years and months.
- **Any gate fails** → H032 NOT PROMISING; B0 is not promoted; the offensive programme returns to the owner.
- **All pass** → "EXPLORATORY PASS — UNIVERSE INCONCLUSIVE (RR6)". STOP. The only next step is a proposal for independent validation (licensed point-in-time data). No Holdout request on exploratory evidence.
- One primary specification; R1 and R2 only, at most one documented infrastructure retry each. No other N, buffer, bound, horizon, threshold or universe.

## 10. Prohibitions

No threshold or definition change after any output; no fallback revenue definition; no use of exit information for selection; no data after 2021-12-31; no Holdout; no purchase; no QuantConnect data export beyond aggregate statistics; no workaround of a QuantConnect compliance refusal.
