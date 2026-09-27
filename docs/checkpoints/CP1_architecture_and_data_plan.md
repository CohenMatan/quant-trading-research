# CHECKPOINT 1 — Architecture & Data Plan

| Field | Value |
|---|---|
| Project | Phase 1: autonomous swing-trading research on US equities |
| Checkpoint | CP1: Architecture & Data Plan |
| Date | 2026-09-27 |
| Status | **Awaiting owner approval.** No significant implementation until approved. |
| Branch | `claude/laughing-wright-s7jfkd` |

---

## 0. Executive summary (read this if nothing else)

1. **Recommendation:** use **QuantConnect Cloud (the LEAN engine plus QuantConnect's bundled data)** as the only data source and backtesting engine for now. I (Claude Code) drive it through QuantConnect's REST API from Python scripts in this repo. **The GitHub repo is the permanent record.**
2. **Why:** it is the only low-cost option I found that provides all of the following together:
   - Survivorship-bias-free daily US equity data from **January 1998**, including delisted stocks.
   - Corporate actions: splits, dividends, delistings, mergers and ticker changes.
   - **Point-in-time market capitalization** for the $2B universe filter, via Morningstar fundamentals from 1998.
   - A realistic execution simulator.

   That gives about **27.7 years** of history, inside your 25–30-year target.
3. **No server, no backend service, no persistent application, no web UI, no database server, no scheduler.** The repo is a research workspace that I operate through Claude Code. Everything runs as one-off scripts.
4. **Expected cost: about $10–$100/month.** The main cost is a paid QuantConnect tier, which API access requires. The public sources I could reach disagree on its current price, so **you must confirm the price at signup.** QuantConnect's data costs nothing extra when used inside its cloud.
5. **Three blockers need you before Checkpoint 2 can start:**
   - (a) Create a QuantConnect account on a paid tier that includes API access.
   - (b) Add your QuantConnect **User ID** and **API token** to this cloud environment as environment variables `QC_USER_ID` and `QC_API_TOKEN`. Do this in the environment settings. Never paste them into chat.
   - (c) Allow network access to **`www.quantconnect.com`** in the environment's network settings. **It is currently blocked by this environment's egress policy.** I verified this: the proxy returns 403.
6. **Main risks:**
   - QuantConnect/Morningstar data can be restated by the vendor. Morningstar replaced the fundamentals feed for all history on 2026-09-23, four days ago.
   - QuantConnect's licence does not allow exporting raw data, so there is no independent second data source yet.
   - The research itself may find nothing. That is an acceptable outcome.
7. **Proposed data split:**
   - Research: 1999–2014.
   - Validation: 2015–2021.
   - **Final Holdout: 2022-01-01 → 2026-08-31.** It stays locked by code until you approve Checkpoint 5.

---

## 1. Proposed architecture

### 1.1 Components

```
 ┌──────────────────────── GitHub private repo (source of truth) ───────────────────────┐
 │ CLAUDE.md / RESEARCH_PLAN.md / RESEARCH_LOG.md / DECISIONS.md                        │
 │ research/hypotheses/H###.md   strategies/S###/ (LEAN algorithm + pure signal logic)  │
 │ experiments/E###-##/ (config, result metrics, equity curve, trade list, git hash)   │
 │ src/qresearch/ (QC API client, runner, metrics, validation stats, reports)  tests/   │
 └───────────────────────────────────────────────────────────────────────────────────────┘
          ▲  git commit/push                         │ python -m qresearch.run E###-##
          │                                          ▼
   Claude Code session (ephemeral container) ──REST API──► QuantConnect Cloud
   - writes code, runs pytest                               - LEAN engine (backtest)
   - computes metrics / DSR / PBO locally                   - AlgoSeek US equity prices
   - writes reports                                         - Security Master (corp. actions)
                                                            - Morningstar fundamentals (MarketCap)
                                                            ◄── returns orders, equity curve, stats
```

| Component | What it is | Notes |
|---|---|---|
| **Research docs** | Markdown files in the repo | Plan, log, decisions, hypotheses, cycle reports. |
| **Strategy package** `strategies/S###/` | One LEAN algorithm file, a small pure-Python signal module, and a strategy card (`strategy.md`) | The signal logic is pure and deterministic, so it can be unit-tested locally without QuantConnect. |
| **QC API client** `src/qresearch/qc_client.py` | Thin wrapper over QuantConnect REST API v2 | Uploads files, compiles, runs a backtest, polls, downloads orders, equity and statistics. No LEAN CLI or Docker needed. |
| **Experiment runner** `src/qresearch/runner.py` | Runs one registered experiment config | Refuses to run if the git tree is dirty. It records the commit hash, QC backtest ID, LEAN version, parameters and dates, and **enforces the holdout lock**. |
| **Metrics and validation** `src/qresearch/metrics.py`, `validation/` | Local Python | Computes every required metric from the equity curve and trade list. Also computes the Deflated Sharpe Ratio, the probability of backtest overfitting (CSCV), walk-forward results, regime slices and bootstrap trade distributions. The same code serves every strategy, so the numbers are comparable. |
| **Registry** `experiments/INDEX.csv` | Append-only table of every experiment | It is never deleted from and includes failed and invalid runs. It drives the count of trials used by the Deflated Sharpe Ratio. |
| **Tests** `tests/` | Pytest | See section 1.6. |

### 1.2 Libraries

- Python 3.11 (already in the environment).
- `pandas`, `numpy`, `scipy`, `requests`, `pyyaml`, `pytest`.
- `polars` or `pyarrow` only if data volume ever justifies them.
- `matplotlib` for static report charts.
- Nothing else unless a need is demonstrated.

### 1.3 Data provider: QuantConnect bundled datasets, used inside QC Cloud

| Dataset (QC name) | Content | Start | Survivorship-free |
|---|---|---|---|
| **US Equities** (AlgoSeek) | Daily OHLCV for every SIP-listed US stock, about 27,500 securities | Jan 1998 | Yes, including delisted stocks |
| **US Equity Security Master** (QuantConnect) | Splits, dividends, delistings, mergers, ticker changes | Jan 1998 | Yes |
| **US Fundamental Data** (Morningstar) | About 8,000 US equities; `MarketCap` plus other fundamentals; daily delivery | Jan 1998 | Yes; point-in-time by design (see §2.3 caveats) |
| SPY, and other ETFs as benchmarks | Daily prices | 1998 (SPY) | n/a |

### 1.4 Backtesting approach

- **One engine: LEAN in QuantConnect Cloud.** It covers both exploration and realistic validation. I am not building a second, fast engine now, per your instruction. I will measure throughput at Checkpoint 2. If throughput becomes the bottleneck, I will propose a fast research layer with its cost, as described in §4.3.
- **Universe:** common stocks only. Each day, keep stocks whose point-in-time `MarketCap` is **≥ $2B**. Add basic tradability filters: price above a small floor and a minimum dollar volume. I will document these and fix them once, not tune them per strategy.
- **Decision timing:**
  - A signal is computed from day T's completed daily bar.
  - Orders are sent as **market-on-open for day T+1**. They are never filled at T's close.
  - A dedicated test algorithm at Checkpoint 2 verifies this timing.
- **Costs:**
  - Interactive Brokers–style per-share commission model.
  - A base slippage assumption in basis points, with stress runs at 2×, 4× and 6× (see RESEARCH_PLAN).
  - A cash account with no leverage, long-only.
- **Corporate actions:**
  - Signals are computed on split- and dividend-adjusted history.
  - Simulated fills use raw, tradable prices, and dividends are credited as cash, so fills are realistic.
  - Delistings are handled by LEAN, which liquidates at the final available price.
- **Benchmarks:**
  - SPY buy-and-hold with dividends reinvested. This is the S&P 500 proxy.
  - An **equal-weight buy-and-hold of the same ≥$2B universe**. This is the harder, more honest benchmark for a stock picker.
- **Metrics** are computed locally from QC's daily equity curve and order list, never from QC's summary numbers alone. This way every strategy is measured with the same code.

### 1.5 Storage approach

| What | Where |
|---|---|
| Code, config, docs, hypotheses, strategy cards, decisions, logs, reports | Git (GitHub private repo) |
| Per-experiment results: metrics JSON, daily equity curve, trade list, config | Git, under `experiments/E###-##/`. These are small derived results, gzip-compressed when above about 1 MB. |
| Raw market data | **Never in Git.** It stays on QuantConnect's servers. QC's licence forbids exporting it, and we do not need a local copy. |
| Anything temporary | The container scratch space, deliberately disposable |

There is no database. CSV, JSON and Markdown files are enough.

### 1.6 Testing approach (mandatory; a task is incomplete until its tests pass)

| Area | How it is tested |
|---|---|
| Signal calculations | Unit tests on small synthetic price series with hand-computed expected values |
| **Look-ahead prevention** | "Truncation test": a signal at date *t* computed on the full history must equal the same signal computed on history cut at *t*. It runs for every strategy's signal module. |
| Execution timing | A QC canary algorithm asserts that every fill timestamp is after its signal bar. Local tests check that the order-scheduling logic never references a same-day close. |
| Portfolio and metrics | Metric functions are tested against known closed-form cases, e.g. a constant-return series gives a known Sharpe and CAGR. Portfolio accounting is tested with toy trades. |
| Data integrity (on QC) | A data-audit algorithm runs at Checkpoint 2 and checks: (1) the count of stocks ≥ $2B per year; (2) known delisted names appear and exit correctly, e.g. Enron 2001, WorldCom 2002, Lehman 2008 and Bear Stearns 2008; (3) market-cap sanity checks against independently known values; (4) split and dividend handling on known events. |
| Reproducibility | Re-running a registered experiment must give an identical trade-list hash and equity-curve hash. A **canary experiment** is re-run periodically to detect silent vendor data changes. |
| Holdout lock | A test asserts that the runner refuses any date after 2021-12-31 unless the unlock record exists. |
| Strategy consistency | The pure signal module and the LEAN algorithm must produce the same entries on a fixed sample. |

### 1.7 GitHub / repository workflow

- **Development:** I work on the session branch assigned by the environment, currently `claude/laughing-wright-s7jfkd`. I commit at every meaningful milestone and push when the work is complete.
- **Checkpoints:** at each checkpoint I push the branch and stop. **Proposal:** approve each checkpoint by merging that branch into `main` through a pull request. `main` then holds only approved states, and every approval is itself recorded in GitHub. I can open the PR when you ask.
- **Official experiments** only run from a **clean, committed** tree. The runner refuses otherwise. So every result maps to exactly one git commit.

### 1.8 Explicit confirmations

- ✅ **No server is required.**
- ✅ **No backend service is required.**
- ✅ **No persistent application is being built.** There is no daemon, scheduler, queue, REST API, database server, web UI, dashboard or authentication.
- ✅ **The repository is a research workspace operated by Claude Code.** Every action is a one-off script run from a session. QuantConnect Cloud is used as an external, on-demand backtesting service.

---

## 2. Data

### 2.1 Historical period available

- Prices, corporate actions and fundamentals all start in **January 1998** on QuantConnect.
- Indicators need warm-up history, so the **first tradable date is 1999-01-04**.
- Usable span: **1999-01 → 2026-08, about 27.7 years.** This meets the 25–30-year target without buying extra data.

### 2.2 Universe data

- The universe is **defined by point-in-time market cap (≥ $2B)**, not by index membership.
  - This avoids needing a paid historical-constituents dataset.
  - It also avoids index-committee effects.
- This covers the large- and mid-cap stocks of the S&P 500/400, the Nasdaq and the Russell 1000, measured the same way through time.
- Excluded:
  - ETFs. The only exception is SPY and other ETFs used as benchmarks, which are not traded by strategies.
  - ADRs and OTC stocks. Morningstar fundamentals on QC do not cover them.

### 2.3 Market cap: availability and point-in-time status

- QC's `MarketCap` = **the most recent daily close × the most recent *reported* total shares outstanding.** Shares outstanding come from the cover of 10-K and 10-Q filings.
- It is intended to be point-in-time: the shares figure is only known from its filing date.
- **Caveat 1:** the shares count lags reality by up to one quarter. For a $2B threshold this only matters for stocks near the threshold. It is not a look-ahead issue.
- **Caveat 2:** Morningstar migrated QC's fundamentals to a new feed on **2026-09-23**. **The whole history back to 1998 was restated.** A community thread also questions how point-in-time the data really is.
  - Mitigation: we use only `MarketCap`, a simple quantity, and none of the more fragile accounting fields.
  - Checkpoint 2 will run the data audit in §1.6.
  - Every experiment records the date it ran, so data-version drift can be detected.
- **Caveat 3:** coverage in the earliest years (1998–2002) may be thinner. The audit will measure it.
- **Decision for you (default in bold):** the threshold is **$2B nominal**, as you specified. Note that $2B in 1999 is roughly $3.8B in 2026 dollars, so the nominal threshold admits relatively smaller companies in recent years. An inflation-adjusted threshold is the alternative.

### 2.4 Delisted stocks and survivorship bias

- The price data and the Security Master include delisted securities. The universe is rebuilt every day from the stocks that existed and qualified *on that day*.
- Delisting events close positions at the final available price. This can be optimistic for bankruptcies, where the final print may not have been achievable in size. I will note it as a limitation and quantify it in the audit.
- We never use today's constituent lists or today's market caps.

### 2.5 Corporate actions

Splits, dividends, mergers, ticker changes and delistings all come from the QC Security Master and are applied by LEAN. See §1.4 for how adjusted versus raw prices are used.

### 2.6 Data-provider limitations

| Limitation | Impact | Mitigation |
|---|---|---|
| **No raw data export** (licence) | No independent local copy and no second engine on the same data | Pure-Python signal modules stay portable. A future second data source is an option (§4.3). |
| Vendor restatements (for example, the 2026-09-23 Morningstar migration) | Old results may not reproduce exactly | Store all derived results in Git, record run dates, re-run a canary experiment periodically |
| History starts in 1998 | About 27.7 years, not 30+ | Acceptable, within target |
| Fundamentals exclude ADRs, ETFs and OTC stocks | Universe is US-listed common stock only | Consistent with scope |
| QC's cloud engine version changes over time | Tiny result differences are possible | Record the LEAN version per backtest |

### 2.7 Alternatives considered and rejected (for now)

| Option | Why not now |
|---|---|
| **Sharadar (Nasdaq Data Link)**: prices from 1998 with delisted stocks, daily market cap, S&P 500 historical constituents; runs well on Linux | A strong option for a *future* fast local layer or independent cross-check. The price needs a quote; one 2026 source puts the bundle in the "low hundreds of dollars per month", which would exceed the target. Not needed until throughput or cross-validation demands it. |
| **Norgate Data Platinum**: about $630/year, delisted stocks, historical index constituents | The updater is **Windows-only**, which does not fit this Linux cloud workspace. It would need a Windows VM. |
| **EODHD**: from €19.99/month, delisted stocks available | Historical market cap only from about 2019–2020 and only weekly, so it **fails the point-in-time market-cap requirement** for 25+ years. |
| **Local LEAN plus downloaded QC data** | Per-file data download fees; Morningstar fundamentals are expensive to download; the container is ephemeral, so a local cache would not persist |
| **yfinance, Stooq and other free sources** | Survivorship-biased (no delisted stocks) and no historical market cap. Unacceptable except as synthetic test fixtures. |

---

## 3. Repository and backup

### 3.1 Proposed structure

```
CLAUDE.md                     stable operating rules for future Claude sessions
README.md                     what this repo is, how to restore/reproduce
RESEARCH_PLAN.md              methodology, data split, validation protocol, gates
RESEARCH_LOG.md               chronological, append-only research diary
DECISIONS.md                  numbered decision records (D001, D002, …)
docs/checkpoints/             checkpoint reports (CP1, CP2, …)
docs/data/                    data audit results, dataset descriptions
research/hypotheses/H###.md   one file per hypothesis (rationale, prediction, variations)
research/cycles/C##.md        research-cycle reports (what was tested, learned, next)
strategies/S###_<name>/       main.py (LEAN), signals.py (pure logic), strategy.md (rules card)
experiments/INDEX.csv         append-only registry of ALL experiments (incl. failures)
experiments/E###-##/          config.json, result.json, equity.csv.gz, trades.csv.gz
src/qresearch/                qc_client, runner, metrics, validation (DSR, PBO, WFA), reporting
tests/                        pytest suite
pyproject.toml                pinned dependencies
.gitignore                    excludes caches, scratch, any local data
```

### 3.2 How commits are managed

- Commit at each milestone with a clear message, e.g. `E003-02: run S003 v1.1 rsi-pullback on IS 1999–2014`.
- Run the tests before each commit that changes code.
- Push at every checkpoint, and more often during long campaigns.

### 3.3 How research history is preserved

- `experiments/INDEX.csv` and `RESEARCH_LOG.md` are **append-only**. Failed, rejected and invalid (bugged) runs are kept and labelled, never deleted.
- Hypotheses and strategies get permanent IDs. A changed rule creates a new strategy **version** (S003 v1.1). A different idea gets a new ID.
- Each research cycle ends with a cycle report in `research/cycles/`.

### 3.4 How experiments reference Git commits

Each `experiments/E###-##/config.json` and `result.json` records:

- Experiment ID, hypothesis ID, and strategy ID and version.
- Git commit hash. The runner requires a clean tree, so the hash fully identifies the code.
- Exact parameters.
- Date range and split label (IS, VAL, WF or HOLDOUT).
- Universe and cost configuration.
- QC project ID, backtest ID and LEAN version.
- Data provenance (dataset names and run date).
- SHA-256 hashes of the trade list and equity curve.

Example: `E003-02 | S003 v1.1 | commit 1a2b3c4 | lookback=10, exit=5d | IS 1999-01-04..2014-12-31 | QC bt 8f… | trades 1,204 | …`

### 3.5 What is version-controlled and what is not

- **In Git:**
  - All code, tests and configuration.
  - All docs, hypotheses, strategy cards and decisions.
  - All experiment configs and derived results: metrics, equity curves and trade lists.
  - All reports.
- **Not in Git:**
  - Raw market data. It stays at QuantConnect and is not exportable.
  - Python virtualenvs and caches.
  - Credentials. They live only in environment variables.
- There are no large datasets to keep outside Git under this design. If a local dataset is added later, the repo will contain its provider, name, date range, version and download script, never the data itself.

### 3.6 How to restore if the Claude environment is unavailable

1. `git clone` the private repo (on any machine).
2. `pip install -e .` (Python 3.11).
3. Set the `QC_USER_ID` and `QC_API_TOKEN` environment variables.
4. `python -m qresearch.run E###-## --reproduce` re-runs any experiment on QC Cloud from its recorded commit and config, then compares the hashes with the stored result.
5. All conclusions and reports are readable directly from the repo, with no need to re-run anything.

If QuantConnect itself became unavailable:

- Every result, trade list and report survives in Git.
- Re-running would need a new data vendor. The pure-Python signal modules make that port feasible, but it would not be free.

---

## 4. Costs

### 4.1 Immediate cost

**$0 from me.** You would need to start a QuantConnect paid tier before Checkpoint 2 (see §4.2). I make no purchases without your approval.

### 4.2 Monthly cost (expected)

| Item | Monthly | Notes |
|---|---|---|
| QuantConnect paid tier (needed for API access) | **about $8–$60** | Sources disagree: older listings say about $8–$10/month, and 2026 review sites say $60/month. **Please confirm the price on the QC pricing page at signup.** |
| Faster QC backtest node (optional) | about $14–$96 | Only if measured throughput is too slow. I will quantify this at Checkpoint 2 before asking. |
| Market data | $0 | QC datasets are included when used inside QC Cloud. |
| GitHub private repo | $0 | |
| Claude Code | already covered | |
| **Expected total** | **about $10–$100** | Within your target of "closer to $100 than $200" |

### 4.3 Possible future costs (each needs your approval)

- **More or faster QC nodes** if a large campaign is bottlenecked, roughly +$20–$100/month.
- **An independent local dataset**, mainly Sharadar, for a fast vectorized research layer and a second, independent check of the finalist strategy. The price needs a quote; it may be about $50–$300/month. Only if clearly justified.
- Nothing else is foreseen.

---

## 5. Risks

### 5.1 Data

- Vendor restatements: the fundamentals history was replaced on 2026-09-23.
- Questions about how point-in-time the Morningstar data is.
- Shares-outstanding lag.
- Thinner coverage in early years.
- Optimistic delisting prices.
- Universe excludes ADRs.

### 5.2 Technical

- `www.quantconnect.com` is **currently blocked** by this environment's network policy. You need to allowlist it.
- The API requires a paid tier.
- Cloud backtest queueing and throughput are unknown until measured.
- LEAN version drift.
- The container is ephemeral. This is fine, because nothing important is kept locally and everything is pushed.

### 5.3 Research

- **Multiple testing and data snooping:** mitigated by the trial registry, Deflated Sharpe Ratio, PBO, pre-registered hypotheses and a limited number of variations.
- **Researcher hindsight:** you and I both *know* what happened in 2022–2026, for example the 2022 rate-driven bear market and the 2023–24 mega-cap AI rally. The holdout is untouched *by data* but not *by memory*.
  - Mitigation: every hypothesis must be justified by reasoning or literature that predates the holdout.
  - The same mitigation applies to validation.
  - No hypothesis may be motivated by known holdout-era events.
- **Base rate:** simple technical swing strategies on liquid large and mid caps, after realistic costs, often fail to beat buy-and-hold on a risk-adjusted basis. **"No Production Candidate Found" is a realistic outcome.**
- The holdout is only 4.7 years long, which limits statistical power. The holdout verdict will be framed as "consistent / inconsistent with validation", not as proof.

### 5.4 Reproducibility

- Vendor data can change underneath us.
- The QC engine can change.
- Mitigations: record hashes, run dates and LEAN versions; re-run a canary experiment periodically; store all derived results in Git.

### 5.5 Vendor and platform dependency

- A single vendor supplies both data and engine: pricing changes, terms-of-service changes, outages or discontinuation could all hurt us.
- Mitigations:
  - Portable pure-Python strategy logic.
  - All results live in Git.
  - A documented fallback path to an alternative vendor (§2.7).

---

## 6. Proposed dataset separation (please approve or amend)

| Segment | Dates | Years | Regimes included | Use |
|---|---|---|---|---|
| **Research / Training (IS)** | 1999-01-04 → 2014-12-31 | 16 | Dot-com bubble and crash, 2002 bear, 2003–07 bull, 2008–09 GFC, 2010 flash crash, 2011 debt-ceiling sell-off, low-volatility 2013–14 | Exploration, hypothesis screening, choosing among a few variations |
| **Validation (OOS)** | 2015-01-01 → 2021-12-31 | 7 | 2015–16 energy/China sell-off, 2018 Q4 sell-off, 2020 COVID crash and V-recovery, 2021 speculative mania | One frozen-parameter pass per promoted candidate, plus walk-forward |
| **Final Holdout** | 2022-01-01 → 2026-08-31 | 4.7 | 2022 rate-driven bear, 2023–24 narrow AI-led bull, 2025 tariff shock | **Once**, after Checkpoint 5 approval, frozen strategies only |

**Walk-forward (after the validation pass):**

- Expanding training window starting in 1999, with one-year test steps from 2005 to 2021.
- Parameters are chosen in each training window by a **rule fixed in advance**, from the strategy's small pre-declared grid.
- This tests whether the *process* is robust, not just one parameter set.
- Walk-forward reuses validation years for *evaluation only*. Nothing is tuned on them, and the reuse is counted as trials.

**Why this split:**

- IS contains two full boom-bust cycles, so hypotheses cannot rely on a single regime.
- Validation contains a crash and a fast recovery that IS never saw.
- The holdout is the most recent period, the most relevant to future production, and contains a bear market, a bull market and a shock.

**Alternative:** move 2022 into Validation, which makes the holdout 2023-01 → 2026-08. That gives more regime coverage during validation but a shorter, mostly bullish holdout. **I recommend the split in the table above.**

**Holdout protection:**

- The runner rejects any date after 2021-12-31 unless `HOLDOUT_UNLOCK.md` exists.
- That file is only created after your Checkpoint 5 approval and records the frozen commit hashes.
- Every holdout run is logged. Strategies cannot be modified after holdout results are seen.

---

## 7. What I will build after approval (Checkpoint 2 scope)

1. Repo skeleton, `pyproject.toml` and the test suite.
2. QC API client and experiment runner, including the dirty-tree check, holdout lock and provenance recording.
3. The metrics module with all required metrics, plus DSR and PBO (CSCV).
4. Data-audit algorithm and report: universe size by year, delisting checks, market-cap sanity, corporate actions.
5. Execution-timing canary.
6. Benchmarks: SPY buy-and-hold and the equal-weight ≥$2B universe.
7. One simple example strategy, run end to end as a pipeline demonstration and not as research.
8. A reproducibility re-run and throughput measurement.
9. Checkpoint 2 report.

No research campaign starts before your Checkpoint 2 approval.

---

## 8. Decisions requested from you

| # | Decision | My recommendation |
|---|---|---|
| 1 | Approve QuantConnect Cloud as the single data source and engine for Phase 1 (for now) | **Approve** |
| 2 | Sign up for a QC paid tier with API access; confirm its monthly price | Choose the cheapest tier that includes API access |
| 3 | Add `QC_USER_ID` and `QC_API_TOKEN` as environment variables and allow `www.quantconnect.com` in network access | Required to proceed |
| 4 | Approve the data split (IS 1999–2014 / VAL 2015–2021 / Holdout 2022-01 → 2026-08) | **Approve as proposed** |
| 5 | Market-cap threshold: $2B nominal or inflation-adjusted | **Nominal $2B** (your spec); inflation-adjusted as a robustness check only |
| 6 | Assumed account size for cost modelling | **$100,000** (affects minimum commissions only) |
| 7 | Approve checkpoints by merging the checkpoint branch into `main` via PR | **Yes** |

---

## 9. Why this architecture is the best fit

- **Best data quality per dollar:** survivorship-free prices, corporate actions and point-in-time market cap for about 28 years, for roughly the price of a software subscription. The only comparable alternatives cost several times more or do not run on Linux.
- **Realism is built in:** LEAN models market-on-open fills, commissions, slippage, splits, dividends and delistings. We do not have to build and debug our own execution simulator.
- **Nothing to operate:** no servers, databases or local data caches. The ephemeral cloud container is not a problem, because the data lives at QC and the record lives in GitHub.
- **Reproducible and auditable:** every result is tied to a git commit, parameters, dates and a QC backtest ID. The whole history, failures included, is kept in the repo.
- **Upgrade path without rework:** if speed or independence becomes a real need, a local vectorized layer on a second dataset can be added later behind the same experiment registry.

---

## Sources

- [QuantConnect — US Equities (AlgoSeek) dataset](https://www.quantconnect.com/docs/v2/writing-algorithms/datasets/algoseek/us-equities)
- [QuantConnect — US Equity Security Master](https://www.quantconnect.com/docs/v2/writing-algorithms/datasets/quantconnect/us-equity-security-master)
- [QuantConnect — US Fundamental Data (Morningstar)](https://www.quantconnect.com/docs/v2/writing-algorithms/datasets/morningstar/us-fundamental-data)
- [QuantConnect — Morningstar Migration (2026-09-23)](https://www.quantconnect.com/docs/v2/writing-algorithms/universes/equity/morningstar-migration) · [Announcement](https://www.quantconnect.com/announcements/21449/migrating-to-morningstar-039-s-new-equity-data-feeds)
- [QuantConnect forum — Is Morningstar data point-in-time?](https://www.quantconnect.com/forum/discussion/14856/is-quot-us-fundamental-data-morningstar-quot-point-in-time-data/)
- [LEAN CompanyProfile class reference (MarketCap definition)](https://www.lean.io/docs/v2/lean-engine/class-reference/classQuantConnect_1_1Data_1_1Fundamental_1_1CompanyProfile.html)
- [QuantConnect — Tier Features](https://www.quantconnect.com/docs/v2/cloud-platform/organizations/tier-features) · [Pricing](https://www.quantconnect.com/pricing/)
- [QuantConnect review 2026 (pricing claims)](https://newyorkcityservers.com/blog/quantconnect-review)
- [QuantConnect forum — data export not allowed](https://www.quantconnect.com/forum/discussion/4658/Export+Research+Dataframes+to+Excel)
- [Sharadar Core US Equities Bundle](https://data.nasdaq.com/databases/SFA) · [Sharadar SEP](https://data.nasdaq.com/databases/SEP)
- [Norgate Data — packages](https://norgatedata.com/stockmarketpackages.php) · [NDU system requirements](https://norgatedata.com/system-requirements.php)
- [EODHD — Historical Market Capitalization API](https://eodhd.com/financial-apis/historical-market-capitalization-api) · [Pricing](https://eodhd.com/pricing)

Note: most vendor pages above were blocked from direct retrieval by this environment's network policy. Figures come from search-engine extracts and are marked as needing confirmation where they conflict.
