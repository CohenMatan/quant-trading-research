# WIKI Prices acquisition log (D298)

Raw data, if ever acquired, lives outside Git under `data/wiki/` (git-ignored `data/`); only this log, the manifest and aggregates are committed.

| UTC time | Source tried | Route | Result |
|---|---|---|---|
| 2026-10-24 12:58 | Official: `https://data.nasdaq.com/databases/WIKIP` (API `https://data.nasdaq.com/api/v3/datatables/WIKI/PRICES/...`) | HTTPS through the session's egress proxy | **Refused by the environment network policy**: proxy `connect_rejected` (gateway 403 to CONNECT) for `data.nasdaq.com:443`. No request reached Nasdaq. No Nasdaq Data Link API key is configured in the environment. |
| 2026-10-24 12:59 | Fallback: `https://www.kaggle.com/datasets/marketneutral/quandl-wiki-prices-us-equites` | HTTPS through the egress proxy | **Refused by the environment network policy**: proxy `connect_rejected` for `www.kaggle.com:443`. No Kaggle API credentials are configured. The listing shows its licence as "Unknown" (search excerpt, TT-CP1b), so this route would also need an owner decision on reuse terms. |

No workaround was attempted (no other mirror, no proxy bypass). Nothing was downloaded; no SHA-256, row count or file size exists yet.
