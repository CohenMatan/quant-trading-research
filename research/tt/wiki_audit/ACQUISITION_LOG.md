# WIKI Prices acquisition log (D298)

Raw data, if ever acquired, lives outside Git under `data/wiki/` (git-ignored `data/`); only this log, the manifest and aggregates are committed.

| UTC time | Source tried | Route | Result |
|---|---|---|---|
| 2026-10-24 12:58 | Official: `https://data.nasdaq.com/databases/WIKIP` (API `https://data.nasdaq.com/api/v3/datatables/WIKI/PRICES/...`) | HTTPS through the session's egress proxy | **Refused by the environment network policy**: proxy `connect_rejected` (gateway 403 to CONNECT) for `data.nasdaq.com:443`. No request reached Nasdaq. No Nasdaq Data Link API key is configured in the environment. |
| 2026-10-24 12:59 | Fallback: `https://www.kaggle.com/datasets/marketneutral/quandl-wiki-prices-us-equites` | HTTPS through the egress proxy | **Refused by the environment network policy**: proxy `connect_rejected` for `www.kaggle.com:443`. No Kaggle API credentials are configured. The listing shows its licence as "Unknown" (search excerpt, TT-CP1b), so this route would also need an owner decision on reuse terms. |

No workaround was attempted (no other mirror, no proxy bypass). Nothing was downloaded; no SHA-256, row count or file size exists yet.
| 2026-10-24 15:2x–15:34 | Official: Nasdaq Data Link WIKI/PRICES (owner configured network access + free API key, D300) | `GET /api/v3/datatables/WIKI/PRICES/metadata.json` → 200 (not premium; schema = protocol §1); `GET …/WIKI/PRICES.json` (zero-row query) → 200; bulk export `qopts.export=true` via `acquire_wiki.py` → zip downloaded | **SUCCESS, no cost.** CSV 1,797,003,576 bytes, 15,389,314 data rows, SHA-256 `ca7fb174c7948db85638917d25ff65d438e27d5cb23675da784c54db01e3d003`, data snapshot 2026-02-03 04:33:38 UTC (dataset last refreshed 2018-03-27). Stored under `data/wiki/` (git-ignored); manifest `WIKI_MANIFEST.json`. No row printed or viewed. |
