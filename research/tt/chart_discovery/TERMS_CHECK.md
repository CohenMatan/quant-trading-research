# Published-terms check before transmitting WIKI chart images (D302 §2)

**Date:** 2026-10-24. **Question:** do the applicable published terms contain an *explicit applicable prohibition* on sending blinded WIKI Prices chart images to Anthropic's Claude for the owner's personal research?

**What could be read.** `data.nasdaq.com/terms` is a JavaScript application. Its content is served from `next-pro.cdn.data.nasdaq.com`, which this environment's network policy refuses, so the full text could not be loaded directly. The clauses below come from search-engine copies of that page.

| Source | Clause | Bearing |
|---|---|---|
| Data License Terms §1.1 (as excerpted) | Licence "to receive, use, process and store the Data … as set out in an Order Form", internal business purposes unless the Order Form says otherwise | Written for paid, ordered datasets. WIKI is a free dataset with no Order Form. |
| §1.3 | "Client shall comply with the applicable third party provider terms … Third party providers shall be deemed third party beneficiaries" | For WIKI, the provider terms are the host's statement that the data was "curated by the Quandl community and released into the public domain" |
| §1.4(b) | Client shall not "sell, lease, rent, furnish, retransmit, redistribute, disseminate, divert, release, license, sublicense or otherwise permit or provide access to the Data in any manner not detailed in Section 1.1 or 1.2 **or in accordance with Section 1.3**" | An explicit restriction, but it carves out uses that follow §1.3. Under public-domain provider terms that carve-out removes the restriction. Its application to this dataset is therefore not explicit. |
| Update notice | New terms effective 2026-11-01; change summary "available upon request" | Not public. Cannot be assessed. |
| AI-specific language | None found in the Data Link terms. AI clauses exist in *other* Nasdaq products (Nasdaq Private Market data terms §2.6; IR Insight AI terms) and in the exchange-data AI policy DN2025-2, which covers "Nasdaq Information", not community-curated WIKI data. | Not applicable to WIKI on its face |

**Conclusion:** no explicit applicable prohibition was identified. The applicability question the owner already acknowledged (D302 §2) remains open. Transmission proceeds under the owner's authorisation, with these safeguards:
- blinded images only (no ticker, date or price text);
- no raw price tables sent;
- the ticker / date mapping kept local;
- nothing published or redistributed.

**Not verifiable from this session:** the "Help improve Claude" model-training setting. It is an account setting this session cannot read or change. The owner must switch it off.
