# P7-CP5e pre-registration — universe repair success criteria (D188)

Fixed and committed **before** any repair is computed or any X997 run exists.

**Target population:** frozen in `target_population.json` (rule in `target_population.py`; SHA-256 `f751460b…`).
- 560 securities and 18,915 stock-months: data-v1 eligible (E993-02) but not new-build eligible (E993-03) at the same review.
- 221 of them are still in the data-v1 universe at 2017-12-29.

## Question A — market-cap repair

**Method (the existing D111 methodology, `qr_sec_corrections.SECCorrections`, unchanged):**
- PIT market cap on selection day T = cover-page `dei:EntityCommonStockSharesOutstanding` × split multiplier × raw price on T.
  - The cover-page count is an instant count measured at the cover date; it becomes usable only from the filing date + 1 day.
  - The count used is the latest-cover-date count among filings usable on T.
  - The split multiplier covers QuantConnect split events with ex-date in (cover date, T].
- Only the filing's own single unambiguous non-dimensional value is used. Multi-class filings without one give no market cap.
- A count older than 135 days on T gives no market cap.
- No interpolation between filings; the count is held until a newer filing is public.
- Securities are mapped to SEC registrants by the identity-v2 dated rows only. The identity extension of question B is not used for market cap, so that the universe repair is independent of it.

**Shadow universe:**
- QuantConnect market cap if > 0; else the SEC-repaired market cap if available; else ineligible.
- Every other filter is unchanged (US common, exchange, price ≥ $5, ADV20 ≥ $5M).
- The data-v1 SEC correction layer (securities without vendor fundamentals) is unchanged.

**Success — all must hold:**

| # | Criterion |
|---|---|
| MC1 PIT | By construction, plus offline truncation tests: no filing before its filing date + 1, no split after T, no vendor share count |
| MC2 coverage | A fresh SEC market cap is computable for ≥ 75% of the target stock-months that (in-cloud) lack a QuantConnect market cap and pass every other filter |
| MC3 splits | ≥ 95% of evaluable splits (2011–2017) give a continuous SEC market cap (not jumping with the raw price) |
| MC4 agreement away from $2B | Where both exist, eligibility agreement ≥ 97% when the QuantConnect market cap lies outside [$1.8B, $2.2B] |
| MC5 near $2B | Disagreement inside [$1.8B, $2.2B] ≤ 30%, and median absolute relative difference (SEC vs QuantConnect) ≤ 5% |
| MC6 recovery | ≥ 60% of target stock-months recovered overall, and ≥ 60% of those belonging to later-disappearing securities |
| MC7 bias | Stock-month-weighted share of members still in the data-v1 universe at 2017-12-29: repaired universe within **2.0 points** of data v1 (83.27%) overall, and within **4.0 points** in every year. Delivered new universe: 90.01% (+6.7 points); data v1 by year 2011–2017: 74.5 / 78.3 / 78.1 / 79.1 / 82.8 / 90.1 / 95.7% |
| MC8 no future data | No SEC filing after T, no split after T, no identity row after T for market cap |
| MC9 deterministic | Identical repaired-eligibility digests in the two X997 runs |

## Question B — earlier SEC identity

**Evidence:**
- public EDGAR submissions of the CIK on a security's first identity-v2 row: periodic forms, filing dates, report dates, former names with dates, deregistration forms;
- identity v2 and the v1 correction table.

No vendor data. Today's CIK is never projected backwards on name or ticker similarity.

**Rule (per security):**
- D0 = the first identity-v2 row date; X = its CIK.
- Walk back through X's original periodic filings (10-K, 10-Q, 10-KT) before D0.
- The chain continues while consecutive filings are ≤ 200 days apart.
- The proposed start is the earliest filing date in the unbroken chain, floored at 2008-07-01 (the warm-up start).
- The start is bounded later by:
  - any former-name change of X inside the interval;
  - any deregistration form (15-12B, 15-12G, 15-15D) of X in the interval;
  - any other security linked to X (identity v2 or v1 table) whose link ends after the proposed start.

**Categories:**

| Category | Meaning |
|---|---|
| SAFE | Chain reaches the floor, no bound applies |
| SAFE WITH BOUNDED START | Start later than the floor because of a bound or the chain start, but earlier than D0 |
| AMBIGUOUS | No submissions file, or report dates missing |
| REJECT | A bound falls within 120 days before D0 (identity discontinuity right before the first evidence), or X filed no periodic report before D0 |

Only SAFE and bounded rows are used. In-cloud, an extended row is used only while the security's QuantConnect feed presence has been continuous (no absence > 60 days) since the row start. Breaks are counted.

**Additional reference completion:**
- M2's "SEC original filing date" is taken from EDGAR submissions: the earliest 10-K / 10-Q / 10-KT with that report date; amendments only if no original. This covers pre-XBRL filings.
- The M2 rule itself is unchanged: max(first seen, that date + 1), period ends matched within 6 days.

**Success:**

| # | Criterion |
|---|---|
| ID1 | Every used row has a public evidence record; no blind backdating |
| ID2 | First-seen vendor values of reports mapped only through extended rows match an SEC value for the period at a rate no more than 3 points below reports mapped through identity v2 (revenue and total assets) |
| ID3 | Successor / predecessor and deregistration bounds applied (counts reported) |
| ID4 / ID5 salvageable | Under M2 + verified identity + repaired universe, every month of 2011 and of 2012 has ≥ 150 fully scored stocks, with a median ≥ 250 in each year. The counts are shown to the owner either way; a 2013 start is never chosen automatically |

## Runs (default build, recorded; 0 orders; aggregates and digests only)

- **E997-01:** M2 + repaired universe + submissions reference + verified identity extension.
- **E997-02:** the same without the identity extension (the "before identity repair" baseline on the same universe).

Window: 2011-01-03 → 2017-12-31, warm-up from 2008-07-01. No 2018–2021, no Holdout, no returns.
