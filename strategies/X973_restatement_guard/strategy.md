# X973: universe-wide SEC restatement guard (infrastructure, D111)

- **What it does:** for every vendor report of an eligible company (2010–2021), compares guarded fields with the SEC filings that reported the same period where those filings disagree (original vs restatement/recast). A report whose value equals only a figure first filed after the vendor's file date is exported for blocking (restatement look-ahead).
- **Never:** orders, rankings, returns or exported vendor values (identifiers, dates and field names only).
