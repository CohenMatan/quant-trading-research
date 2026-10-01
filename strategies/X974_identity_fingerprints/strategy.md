# X974: identity fingerprints, second pass (infrastructure, D111)

- **What it does:** computes SEC public float / (SEC cover shares × QuantConnect raw close) at each float date for candidate pairs not covered by X971 (registrants still listed after 2021, and securities that outlived a registrant), pre-filtered by the strict ticker-name rule.
- **Never:** orders, rankings, returns or exported vendor values.
