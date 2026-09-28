# CHECKPOINT 2 — Research Infrastructure

> **Amended 2026-09-28.** The owner approved CP2. The data-remedy options in §7 were resolved by D033: 2010+ only, MarketCap ≥ $2B, size proxy rejected. The split, the gates in §6 and the commission model are replaced by `CP2_amendment_2010_split.md`.

| Field | Value |
|---|---|
| Project | Phase 1: autonomous swing-trading research on US equities |
| Checkpoint | CP2: Research Infrastructure Ready |
| Date | 2026-09-27 |
| Status | **Awaiting owner approval. STOPPED.** No research campaign has started. |
| Branch | `claude/laughing-wright-s7jfkd` |
| Hypotheses / strategies / research experiments tested | **0 / 0 / 0.** 14 infrastructure, benchmark and demo runs are registered; see §5. |

---

## 0. Executive summary (read this if nothing else)

1. **The infrastructure works.**
   - I can drive QuantConnect Cloud end to end from this repo: upload, backtest, download, local metrics, registry, report.
   - Execution timing is verified on 4,628 fills. Every order fills at the next session's open, with zero exceptions. No fill ever happens at the signal bar's close.
   - Splits, dividends and delistings are handled correctly.
   - A re-run reproduced results **bit for bit**.
   - The test suite passes: **81 of 81**.
2. **But I found a serious data problem that blocks the approved research design. You need to decide how to proceed before any research starts.**
   - QuantConnect's market-cap data (Morningstar) cannot support the approved universe, "point-in-time market cap ≥ $2B, 1999 onward", without bias:
     - **Old dataset** (QuantConnect's default until Oct 10, retired Oct 31):
       - It has market caps from 1999.
       - But it **never has one for companies that later failed or were acquired**. Enron, WorldCom, Lehman, Bear Stearns, Merrill Lynch, Countrywide, old GM and Lucent are all missing.
       - That is survivorship bias, the exact bias we must avoid.
     - **New dataset** (the only one after Oct 31):
       - It has **essentially no market caps before 2009**: 3–27 companies ≥ $2B per year, when the real number is about 1,000. Even Microsoft and GE read $0.
       - From 2010 on it looks good: about 700–1,500 companies ≥ $2B, with values matching public figures.
       - It still misses some companies that disappeared later: 3 of 12 checked.
   - Price data itself is fine and survivorship-free from 1998. Only the **market-cap filter** is the problem.
3. **My recommendation:**
   - (a) Ask QuantConnect whether the new dataset's missing pre-2009 market caps are a known gap they will fill. Their own documentation says it starts in 1998. I have drafted the message (§8).
   - (b) Approve me to build and test, at $0, a **size proxy** that keeps the 1999 start. It would use a liquidity-based ranking from survivorship-free prices, calibrated to match the ≥ $2B universe where market cap is reliable.
   - (c) Decide between the options in §7 once both answers are in.
   - Research stays stopped until then.
4. **Cost:** unchanged at **$24/month**, with no other spend. QuantConnect also shows a $200 welcome credit, which I have not used.
5. **Throughput:**
   - Small backtests take about 20 s.
   - Full-universe strategy backtests take about 3–7 minutes.
   - Only one backtest runs at a time on our node.
   - That is roughly **10–15 universe-strategy backtests per hour, or 150–300 per day**, far more than the research plan needs (a few hundred in total).
6. **Also for approval (§6):** proposed standard settings for tradability filters, base slippage, portfolio constraints and screening criteria. They are **not yet applied** to any research.

---

## 1. What was built

All of this lives in the repo. Nothing runs as a service; everything is a one-off command.

| Component | Where | What it does |
|---|---|---|
| QC API client | `src/qresearch/qc_client.py` | Authenticated calls to QuantConnect's REST API: project files, compile, backtest, results. Credentials come only from env vars and are scrubbed from every error message. |
| **LEAN harness** | `src/qresearch/lean/qr_harness.py` | Shared code uploaded into every backtest, so every strategy is measured identically. See the list below. |
| Experiment runner | `python -m qresearch.run E###-##` | Runs one experiment. See the list below. |
| Registry | `experiments/INDEX.csv` | Append-only record of every run, including failures. Prefix-verified on every write. |
| Metrics | `src/qresearch/metrics.py` | All metrics in RESEARCH_PLAN §6, computed locally from the equity curve and trades with one shared module. |
| Validation statistics | `src/qresearch/stats.py` | Probabilistic and Deflated Sharpe Ratio (trial count from the registry), PBO via CSCV, profit concentration, best-trade removal, bootstrap confidence intervals. |
| Trade builder | `src/qresearch/trades.py` | Round-trip trades from fills. Split-aware, long-only enforced. |
| Integrity checks | `src/qresearch/integrity.py` | 14 checks on every run, e.g. fills after signals, no leverage, complete equity curve. |
| Look-ahead checker | `src/qresearch/lookahead.py` | The "truncation test" for any signal function. |
| Reports | `report.md` per experiment; `python -m qresearch.audit` for the data audit | Human-readable output. |
| Infrastructure algorithms | `strategies/X950…X952` | Timing canary, data audit, corporate-action and delisting check. |
| Benchmarks | `strategies/B900`, `B901` | SPY buy-and-hold (dividends reinvested); equal-weight ≥ $2B universe, rebalanced monthly. |
| Pipeline demo | `strategies/S000_pipeline_demo` | One simple rule run end to end. **Not research.** |
| Tests | `tests/` (81 tests) | See §3. |

The LEAN harness:

- sets dates, cash and costs;
- enforces the holdout lock a second time, inside QuantConnect;
- builds the ≥ $2B universe;
- accepts orders only at the daily close and only as market-on-open for the next session;
- plans cash so there is no leverage;
- keeps point-in-time adjusted price windows for signals;
- self-checks every fill;
- exports the daily equity curve.

The experiment runner:

- refuses to run from an uncommitted tree;
- enforces the holdout lock;
- reads code and config **from the git commit**;
- pins the QuantConnect engine version;
- downloads orders, logs and the equity curve;
- checks integrity and computes metrics;
- writes `result.json`, compressed equity, fills and trades, and `report.md`;
- appends the registry;
- `--reproduce` re-runs a recorded experiment and compares result hashes.

**Execution model, as built:**

- The signal uses day T's completed bar. The order is market-on-open on T+1.
- Fills use raw prices ± slippage.
- IB commissions ($0.005/share, $1 minimum, 1% maximum).
- Dividends are credited as cash.
- LEAN force-liquidates positions on delisting.
- Signals use point-in-time split- and dividend-adjusted windows.
- No leverage is enforced by the harness's cash planning. A run fails if cash drops below −1% of equity at any close. See D015.

## 2. What works: evidence from real QuantConnect runs

| Check | Experiment | Result |
|---|---|---|
| API authentication and dataset access (precondition) | 5 probe backtests | ✅ Prices incl. delisted, Security Master, Morningstar, SPY all accessible (log 2026-09-27) |
| **Execution timing** | E950-02 (1999–2021, 8 stocks, 579 rebalances) | ✅ 4,628 fills. **0** fills on the signal day, **0** later than the next session. Fill price = next open ± slippage for every fill (max deviation 3.5e-16). |
| Splits | E952-02 | ✅ AAPL 2:1 (2005): 131 → 262 shares. AAPL 7:1 (2014): 262 → 1,833 shares, fraction paid in cash. KO 2:1 (2012). Portfolio value continuous to the cent. |
| Dividends | E952-02 | ✅ 93 of 93 dividend events credited exactly. |
| Delistings | E952-02 | ✅ Positions force-sold: Enron 2002-01-12 at $0.67; WorldCom 2002-07-30 at $0.24; Bear Stearns 2008-05-31 at $9.34 (the JPM deal value); Lehman 2008-09-18 at $0.14. |
| Local metrics vs QuantConnect's own figures | canary | ✅ Net profit and total fees identical. |
| Large universe on our node | E901-01 | ✅ Up to 1,625 securities subscribed at once (the node's nominal "500 assets" is not enforced). |
| Reproducibility | E950-02 and E000-01 re-runs | ✅ **Identical** equity, fill and trade hashes. |
| No leverage | all runs | ✅ Minimum cash/equity: +1.9% (EW), +0.3% (demo), +1.3% (canary). |

## 3. Tests executed

`python -m pytest`: **81 passed, 0 failed, 0 skipped** at the report commit.

| Required area | Tests |
|---|---|
| Look-ahead (truncation test) | S000's signal passes the truncation test. The checker also correctly *catches* two deliberately look-ahead signals (tomorrow's price; full-sample normalisation). The selection depends only on its signal window. The LEAN algorithm imports the same pure signal module. |
| Execution timing | A fill on the signal day is flagged. The harness contains exactly one order call (market-on-open) and a timing guard. No strategy places orders directly. The canary run shows 0 violations. |
| Metrics | CAGR, volatility, Sharpe, Sortino, drawdown and its duration, calendar returns, trade statistics, turnover, exposure and beta, all against hand-computed values. PSR/DSR, PBO (dominant strategy → 0, noise → ≈ 0.5, constructed overfit → 1), bootstrap. |
| Portfolio accounting | Round trips, scaling in and out, forced delisting exits, splits and reverse splits, long-only violations. Local net profit and fees on a real run equal QuantConnect's. |
| Data integrity | Parsing of QuantConnect payloads (New York dates). Detection of unsorted, duplicate, negative or out-of-window equity, leverage and an incomplete chart. Every committed result re-hashes to its recorded hash. |
| Reproducibility | Hashes are independent of download order. Formats are fixed. Compressed files are byte-identical. Every recorded reproduction is identical. |
| Holdout lock | Dates after 2021-12-31 are rejected unless `HOLDOUT_UNLOCK.md` exists. The file does not exist. The LEAN-side lock is present. No committed config reaches 2022. |
| Other | Registry is append-only. Config validation (IDs, split vs dates, research needs a hypothesis). Clean-tree check. Files read from the commit. Auth hashing. Credentials never appear in errors or URLs. |

## 4. Data coverage (data audit)

The full measured tables are in `docs/data/`:

- E951-01: old dataset.
- E951-02 and E951-03: new dataset; E951-03 is the corrected run.

Market cap was also checked against public values for known companies on known dates, and I tracked companies that later failed or were acquired.

### 4.1 Companies with MarketCap ≥ $2B (US common stock, primary listing), yearly average

| Year | Old dataset (E951-01) | New dataset (E951-03) | Comment |
|---|---|---|---|
| 1999 | 344 | **4** | Real count is roughly 1,000 |
| 2003 | 390 | **7** | |
| 2007 | 608 | **22** | |
| 2009 | 476 | 305 | New dataset starts filling in |
| 2010 | 575 | 708 | |
| 2014 | 879 | 1,048 | |
| 2018 | 1,138 | 1,204 | |
| 2021 | 1,543 | 1,536 | |

**Price data** (US Equities, AlgoSeek): complete and survivorship-free from 1999. About 6,500–9,400 listed securities per year, delisted ones included.

### 4.2 Survivorship check: companies that later disappeared

| Company | Disappeared | Old dataset MarketCap | New dataset MarketCap |
|---|---|---|---|
| Enron, WorldCom, Lehman, Bear Stearns, Merrill Lynch, Countrywide, Wachovia (old), WaMu, GM (old), Lucent | 2001–2009 | **never present** | **never present** |
| Dell, EMC, Yahoo, Monsanto, Celgene, Raytheon, Express Scripts, Whole Foods, Linear Tech | 2013–2020 | not checked | ✅ present, plausible values |
| Heinz, Sears, Time Warner | 2013–2018 | not checked | ❌ missing |

**Surviving** companies match public values closely, e.g. MSFT and GE in Jan 2000 (old dataset), and AAPL in 2012 and 2014 (new dataset, within 0.2%).

### 4.3 Other data facts discovered

- In the old dataset, about 45–56% of all dollar volume through 2015 trades in securities without a market cap. Part of this is ETFs, which have no fundamentals, but many are large common stocks.
- The fundamentals' **shares-outstanding fields are split-adjusted to today**. For example, GE shows 1.24B shares in 2000 because of its 2021 1:8 reverse split. So "price × shares" is **not** a point-in-time market cap unless it is corrected, and it must not be used naively.
- The new dataset renamed exchange codes (NYSE, AMEX). This is handled (D022).
- QuantConnect switches its default engine to the new dataset on **2026-10-10** and removes the old one on **2026-10-31**. All CP2 runs except E951-01 are pinned to the new-dataset engine build (18131).

### 4.4 What this means

- The approved universe rule cannot be applied faithfully to 1999–2009 with QuantConnect's data.
- The old dataset would silently remove every future failure from the universe. That flatters any strategy, because it never holds a stock that is about to blow up.
- The new dataset has no universe at all before 2009.
- See §7 for the options.

## 5. Example backtests, benchmarks and the registry

All numbers are net of costs (10 bps slippage per side, IB commissions), using the provisional settings in §6. **Benchmarks and the demo are infrastructure outputs, not research results.**

| Experiment | What | Period | CAGR | Sharpe | Max DD | Notes |
|---|---|---|---|---|---|---|
| E900-02 | SPY buy-and-hold (dividends reinvested) | 1999–2021 | 7.8% | 0.50 | −54.4% | IS 5.0% / 0.35; VAL 14.6% / 0.87 |
| E901-01 | Equal-weight ≥ $2B universe | **2010**–2021 | 14.3% | 0.83 | −38.1% | Starts 2010 because of §4. Average 1,034 names. Its trade statistics are not meaningful: survivors stay open. |
| E000-01 | **Pipeline demo** (5-day reversal, 10 slots) | 2010–2014 (IS) | 3.2% | 0.25 | −45.0% | 2,470 trades. Clearly worse than the EW benchmark (−14.2%/year). No research meaning. |
| E950-02 | Timing canary | 1999–2021 | — | — | — | 4,628 fills, 0 timing violations |
| E952-02 | Corporate actions and delistings | 2001–2014 | — | — | — | All checks pass |

**Registry totals:**

- 14 runs across 11 experiment IDs: 11 original runs plus 3 reproduction runs.
- 3 runs are recorded **failures**. They are kept, never deleted.
  - E950-01 and E900-01: the equity chart was read too early.
  - One E000-01 reproduction: fill events were read too early.
- Hypotheses 0, research strategies 0, research experiments 0.
- DSR trial count so far: 1, the demo, which is counted conservatively.
- In addition, 14 unregistered development runs of infrastructure code were made: 11 API/data probes and 3 harness scratch runs. None were research, as D020 allows.

## 6. Proposed standard settings (for your approval, not yet applied to research)

Once approved, these are fixed for all strategies and never tuned per strategy.

| Item | Proposal | Why |
|---|---|---|
| **Tradability filters** | Raw price ≥ **$5**, and 20-day average dollar volume ≥ **$5M**, both as of the prior close | Removes penny-stock and illiquid-print effects. At $100K, positions are about $10K, so $5M/day means we would trade at most 0.2% of a day's volume. |
| **Base slippage** | **10 bps per side**; stress runs at 20/40/60 bps. Commissions: IB fixed. | Conservative for the opening auction of ≥ $2B stocks with small orders. It covers the wider spreads before 2001 decimalization better than 5 bps would. |
| **Portfolio constraints** | Long-only; no leverage; ≤ **10%** of equity per position at entry; ≤ 20 positions; 2% cash buffer; minimum position $2,000 | Diversification floor. Keeps commission drag small. |
| **Screening gate (in-sample), at base costs** | ≥ 100 closed trades; Sharpe ≥ 0.5 **and** ≥ equal-weight benchmark Sharpe + 0.1 over the same dates; max drawdown ≤ 35% and no worse than the benchmark's; profit factor ≥ 1.2; 95% bootstrap CI of expectancy above 0; positive in ≥ 60% of years; no single year > 40% of profit; expectancy still > 0 without the best 5% of trades; Sharpe ≥ 0.4 at 2× slippage | "Better than simply owning the universe, on a risk-adjusted basis, robustly." |
| **Robustness gate (in-sample)** | ≥ 80% of ±20–50% parameter perturbations keep ≥ 70% of base Sharpe; Sharpe > 0 at 4× slippage; positive Sharpe in each third of the in-sample period | Plateau, not peak. |
| **Validation gate** | Sharpe ≥ 0.4 and ≥ 50% of in-sample Sharpe; beats the EW benchmark's Sharpe; max drawdown ≤ 35%; **Deflated Sharpe ≥ 0.90** using the registry trial count; **PBO ≤ 0.30** across the hypothesis's variations | Guards against the multiple-testing and overfitting found in the literature. |
| **Holdout (CP5)** | To be defined in writing before CP5 as "consistent with validation" criteria. Not needed yet. | |

## 7. The data decision: options

| Option | What | Cost | History | Bias | Keeps your spec? |
|---|---|---|---|---|---|
| **A. Shorten history** | Use the new dataset's MarketCap ≥ $2B from 2010. Re-split, e.g. IS 2010–2017, VAL 2018–2021, holdout unchanged. | $0 | about 12 years before the holdout (target was 25–30) | Small residual: 3 of 12 later-disappeared companies missing | Yes, but loses 2000–02 and 2008–09 |
| **B. Size proxy** *(recommended to test first)* | Keep 1999. Define size eligibility from survivorship-free prices and volume (a dollar-volume rank), calibrated so that in 2010–2014 it matches the ≥ $2B MarketCap membership as closely as possible. Report the agreement. Exclude ETFs with a fixed, documented list. | $0, about 1 day of work | Full 1999–2021 | Survivorship-free by construction; the proxy is imperfect and its error is measured | Approximately; a change needs your approval |
| **C. Buy point-in-time market-cap data** | E.g. Sharadar with delisted companies. Import a derived eligibility list into QuantConnect. | Unknown: quote needed, possibly above budget | Full | Low | Yes |
| **D. Ask QuantConnect** | Their migration page says the new dataset starts in January 1998, but the measured data does not. It may be a fixable gap before the Oct 10 switch. | $0 | — | — | — |

**Recommendation:**

1. Do **D now**. You would send the note in §8, or allow me to post it if you prefer. I do not contact third parties on my own.
2. Let me build **B** as a CP2 addendum, with agreement statistics against the reliable 2010–2014 overlap.
3. Choose between A, B and C when both are in.

**Option A is the fallback** if B's agreement is poor and C is too expensive.

## 8. Draft note to QuantConnect support (for you to send, or approve me to post)

> In the new Morningstar dataset (LEAN branch `morningstar-edf-new-data-points`, build 18131), `Fundamental.MarketCap` is 0 for almost all US equities before 2009. For example, on 2000-01-03 it is 0 for MSFT and GE, and only 4–27 companies per year from 1999–2008 have MarketCap ≥ $2B. In both the old and the new dataset, companies that later delisted (Enron, WorldCom, Lehman, Bear Stearns, Merrill Lynch, Countrywide, Lucent) have no fundamental data at all while they traded. Is historical MarketCap for 1998–2008, and fundamentals for delisted companies, going to be populated before the dataset becomes the default on Oct 10?

## 9. Known limitations

- **Data (§4) — the main one.** No unbiased ≥ $2B universe before 2010 on QuantConnect today.
- **Delisting prices.**
  - Force-liquidation happens at the last price, e.g. Lehman at $0.14.
  - That is realistic for bankruptcies traded down to the end.
  - It cannot capture trading halts where no exit was possible.
- **Engine and data drift.**
  - Runs are pinned to build 18131, a QuantConnect feature branch.
  - QuantConnect may retire it. The runner then refuses to run, rather than silently switching builds.
  - A re-run of the canary will reveal any change.
- **Trade-level PnL excludes dividends.** Portfolio metrics include them.
- **Risk-free rate.** Sharpe uses a 0% risk-free rate. This understates cash's opportunity cost in 1999–2007; it applies equally to benchmarks.
- **Share classes.** Dual-class shares: only the primary share is eligible, so BRK.B is excluded.
- **Result delivery.**
  - QuantConnect delivers some results asynchronously.
  - The runner now waits until they are complete, which caused two recorded failures before the fix.
  - Custom charts are limited to 10 series per algorithm.
- **Single backtest node.** Runs are sequential, and a second submission is refused, not queued.
- **Missing SPY comparison for the demo.** E000-01's config pointed at the failed E900-01, so its report has no SPY comparison. Its config is kept as history.
- **Audit gap.** The audit's dollar-volume-share column is blank for 2020–21 on the new dataset: some volumes are missing. Counts are unaffected.

## 10. Current cost

| Item | Monthly |
|---|---|
| QuantConnect Researcher seat | $10 |
| B2-8 backtest node | $14 |
| Everything else | $0 |
| **Total** | **$24** (budget target $100, ceiling $200) |

Notes:

- A $200 QuantConnect welcome credit appears on the account. It is unused.
- The organization's product list also shows a **"Tradier" module line at $1**. It is not among the active subscriptions. Please glance at your QuantConnect billing to confirm you are not charged for it.

## 11. Throughput (measured)

| Backtest type | Backtest time | Wall time incl. upload and download |
|---|---|---|
| Few symbols, 23 years (canary, SPY) | about 15–20 s | about 25–35 s |
| Full-universe strategy, ~800–1,000 names, 5 years (demo) | 175 s | about 3 min |
| Full-universe, ~1,000–1,600 names, 12 years (EW benchmark) | 391 s | about 7 min |
| Full fundamental-universe scan, 23 years (audit) | 210–400 s | about 4–7 min |

**Estimate:** 10–15 universe-strategy backtests per hour, or about 150–300 per day if run continuously, one at a time. The research plan (a few hundred experiments in total) needs no extra node (D002 stands).

## 12. Problems discovered and fixed during CP2

| # | Problem | Fix | Record |
|---|---|---|---|
| 1 | ObjectStore export is blocked for non-Institutional accounts; logs are capped at 100 KB | Results are exported via a daily custom chart plus the orders API | D013 |
| 2 | QuantConnect silently dropped the equity chart when an algorithm had > 10 custom series | The audit writes compact log lines instead; an integrity check fails if the equity curve is missing | D013 |
| 3 | The chart was read before QuantConnect finished building it | The runner waits for the expected number of points | E950-01 and E900-01 recorded as failed, re-run as E950-02 and E900-02 |
| 4 | Order fill events were read before QuantConnect finished them | The runner waits until every filled order has its events | Failed E000-01 reproduction kept on record; the re-reproduction is identical |
| 5 | Master engine = old dataset, retired Oct 31 | Every run is pinned to an explicit engine build and verified | D021 |
| 6 | New dataset renamed exchange codes | The filter accepts both | D022; E951-02 superseded by E951-03 |
| 7 | Corporate-action check mis-flagged same-day dividends | Fixed in X952 v1.1 | E952-01 → E952-02 (93 of 93 correct) |
| 8 | Metrics crashed on an empty equity curve | Guarded; the run is marked integrity-failed | — |
| 9 | I overwrote the repo's `.gitignore` | Restored the original secret, data and cache entries | commit eeef866 |

## 13. Git

- Report commit and push: see the final entry in `RESEARCH_LOG.md`. The branch is `claude/laughing-wright-s7jfkd`, pushed to GitHub.
- To approve CP2, merge the branch into `main` through a PR, as agreed at CP1. Please also record your decision on §6 and §7.

## 14. Decisions requested

| # | Decision | My recommendation |
|---|---|---|
| 1 | Approve CP2 infrastructure | **Approve** |
| 2 | Data: send the note in §8 (or let me post it) | **Yes** |
| 3 | Data: authorize me to build and test the size proxy (option B) as a CP2 addendum, at $0 | **Yes**. The fallback is option A. |
| 4 | Approve the standard settings in §6 (filters, slippage, constraints, gates) | **Approve**, or amend |
| 5 | Confirm the "Tradier $1" line is not billed | Please check |
