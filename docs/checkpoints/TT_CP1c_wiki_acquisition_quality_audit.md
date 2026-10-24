# TT-CP1c — WIKI Prices acquisition and data-quality audit

**Date:** 2026-10-24 · **Owner direction:** D298 (`docs/owner/2026-10-24_wiki_acquisition_quality_audit.md`) · **Decision record:** D299

## Result: **INCONCLUSIVE / ACCESS BLOCKED**

The dataset could not be downloaded from this session. Both permitted sources are refused by the environment's network policy, and no credentials exist for either. Nothing was downloaded, so **no WIKI number exists**: the six questions below are answered from facts.

Everything that does not need the file is now built, frozen and tested:
- the audit protocol, with thresholds fixed before any data;
- the independent SEC reference frame;
- the audit engine;
- an acquisition script.

The real audit is therefore two commands away once access exists.

## Answers to the six questions

**1. Was the dataset downloaded? From where?**
**No.** See `research/tt/wiki_audit/ACQUISITION_LOG.md`.
- **Official route:** `https://data.nasdaq.com/databases/WIKIP`, API `https://data.nasdaq.com/api/v3/datatables/WIKI/PRICES`. The session's egress proxy refused the connection (`connect_rejected`, gateway 403 to CONNECT, 2026-10-24 12:58 UTC). No Nasdaq Data Link API key is configured.
- **Fallback:** `https://www.kaggle.com/datasets/marketneutral/quandl-wiki-prices-us-equites`. The proxy also refused the connection (12:59 UTC). No Kaggle credentials are configured. This listing's licence is "Unknown", so it would need your decision on reuse even if reachable.
- No other mirror was tried and no restriction was bypassed. No synthetic data was used in its place.

**2. How many stocks and daily observations exist for 2010–2017?**
**Not measured;** the file was not obtained. The engine will report unique tickers, rows by year, rows with missing fields, and reference trading sessions per year against the published NYSE counts.

**3. Which quality and composition issues were actually measured?**
- **On WIKI: none.**
- **On the independent SEC reference frame, measured from cached public SEC data only** (`SEC_REFERENCE_summary.json`). The frame contains registrants with a 10-K public float ≥ $2B, point-in-time by filing date; funds, partnerships and blank-check companies are excluded:

| Year | Registrants | Registrant-months | Leaver months (24 months before exit) |
|---|---|---|---|
| 2010 | 250 | 2,133 | 63 |
| 2011 | 501 | 4,782 | 174 |
| 2012 | 841 | 8,716 | 411 |
| 2013 | 929 | 9,485 | 588 |
| 2014 | 1,018 | 10,883 | 907 |
| 2015 | 1,159 | 12,457 | 1,209 |
| 2016 | 1,246 | 13,246 | 913 |
| 2017 | 1,233 | 12,578 | 275 |

Further facts about the frame:
- **Size:** 1,614 registrants in total.
- **Leavers:** 299 registrants stopped filing before 2018: **ACQUIRED 265**, **FAILED 14**, **DELISTED-OTHER 6**, **UNKNOWN 14**.
- **Categories:** 16,470 financial / REIT registrant-months and 4,328 with foreign-style names.
- **Identity:** 219 registrant-months have a missing or shared ticker prefix. These will be classed as ambiguous.

These numbers say something before any WIKI data is seen:
- **2010–2011 is thin in the reference.** That reflects the SEC's XBRL phase-in, not WIKI.
- **Few large companies actually failed.** Only the ACQUIRED group is large enough (≥ 20 registrants) to be judged under gate A2. Failures and other delistings will be reported but cannot by themselves pass A2.

**4. Is the data sufficient for about 300 representative charts?**
**Unknown until the audit runs.** The test is fixed in advance as gate A7, alongside A1–A6:
- at least 20 chart-eligible registrants in every year (2011–2017) × size tercile;
- at least 30 chart-eligible leaver registrants;
- each chart-eligible case needs a full 252 sessions of prior bars.

**5. Limitations that remain** (fixed in protocol §7, true whatever WIKI shows):
- WIKI cannot be shown survivorship-free.
- Leaver coverage is measured only inside an SEC frame that itself starts with XBRL.
- Price accuracy beyond internal consistency and an SEC split cross-check cannot be verified.
- Foreign 20-F / 40-F issuers and large caps whose float is below $2B are outside the frame.
- Names whose ticker differs from the SEC prefix stay "unresolved identity". They are bounded, not counted as missing.
- Exit types are UNKNOWN outside the cached SEC submissions.
- Licensing: sending charts to Claude remains unresolved (Addendum 1). The audit keeps all rows and charts out of the AI's view; only aggregates are reported.

**6. The smallest next step.** Two environment changes by you, then a **new session**:
1. **Network access:** in the cloud environment settings (session title bar → environment → Edit → Network access), add **`data.nasdaq.com`** to Allowed domains. Also add the host of the export file it hands out (historically Amazon S3, e.g. `s3.amazonaws.com`). If that host is still refused, I will name it exactly from the proxy log.
2. **API key:** create a free Nasdaq Data Link account and add its API key as an environment secret named **`NASDAQ_DATA_LINK_API_KEY`**. Do not paste it into the chat.

Then I run:
- `python research/tt/wiki_audit/acquire_wiki.py`, which downloads, then records the URL, date, size, row count and SHA-256 in the manifest;
- `python research/tt/wiki_audit/sec_reference.py`, then `python research/tt/wiki_audit/wiki_audit.py data/wiki/<file>.csv`;

and report the classification. If you prefer the Kaggle copy instead, it needs `www.kaggle.com` and `storage.googleapis.com` allowed, Kaggle credentials, and your explicit acceptance of its "Unknown" licence. I recommend the official route.

## What was built (committed; no market data)

| File | Purpose |
|---|---|
| `research/tt/wiki_audit/WIKI_AUDIT_protocol.md` + `PROTOCOL_PIN.json` | **Frozen before any data** (SHA-256 39a926b8…). Contents: 2010–2017 window; point-in-time SEC reference frame; identity classes MATCHED / MISSING-PARTIAL / MISSING-OUT-OF-LIFE / UNRESOLVED-IDENTITY / AMBIGUOUS, with strict vs resolved coverage, so missing price history is separated from unresolved identity; liquidity taken only from WIKI dollar volume, never public float; gates A1–A7 with PASS / FAIL / INCONCLUSIVE; sampling rule drawn from the SEC frame. |
| `sec_reference.py` → `SEC_REFERENCE_summary.json` | Independent reference frame. Uses cached SEC data only, with no network, no QuantConnect and no WIKI data. |
| `wiki_audit.py` | Audit engine. Checks the file's SHA-256 against the manifest, drops rows outside the window when reading, and outputs aggregates only. |
| `acquire_wiki.py` | Official bulk-export download and manifest. The API key is never recorded. |
| `tests/test_wiki_audit.py` | 11 tests on small synthetic fixtures: protocol pin, window filter, schema guard, calendar, spike / invalid-bar / adjustment / dividend checks, identity classes, gate logic, SEC point-in-time and exit rules, manifest refusal, and that the key never reaches the manifest. This is a new file; **no existing test was changed** (D296). |

An end-to-end run on a throwaway synthetic file confirmed that the pipeline executes. Its numbers mean nothing and were discarded; none were committed.

**Not done, as instructed:** no chart rendered or sent, no strategy or backtest, no 1999–2009 inspection, no Holdout, no purchase, no QuantConnect work, no frozen result modified.

**STOPPED.**
