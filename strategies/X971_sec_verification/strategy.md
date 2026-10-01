# X971: SEC verification and identity fingerprints (infrastructure, D111)

- **What it does:** compares QuantConnect/Morningstar fundamentals for a fixed sample of companies with the SEC's as-first-filed XBRL values (ratios, matching filing), records when the point-in-time layer exposed each report, checks the SEC cover-share market-cap method against the vendor's point-in-time market cap, and computes public-float fingerprints that link SEC registrants to securities without fundamentals (D043).
- **Never:** orders, rankings, returns, or exported vendor values (ratios and identifiers only).
