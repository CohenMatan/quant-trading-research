# P2-CP7a — Continue SEC repair / True TTM: blocked at step 1 (SEC contact email)

- **Date:** 2026-10-02.
- **Status:** STOPPED, awaiting the owner.
- **Done in this phase:** only the access check. No data fetched beyond one probe, nothing built, nothing run.

## What was asked

The owner approved continuing the remediation (2026-10-02; `docs/owner/2026-10-02_continue_SEC_repair_true_TTM.md`):

- SEC ticker/company-history repair;
- a True TTM layer from quarterly filings;
- a coverage and bias re-audit;
- a final readiness checkpoint.

Step 1 is the gate: *use a project-specific contact email for SEC requests, not the owner's personal email; if `www.sec.gov` remains blocked, stop and report the exact blocker.*

## The exact blocker

1. **No project-specific contact email exists.** I looked in the repository, the environment variables and the git configuration. The only email available to me is the owner's personal account address, and the owner has excluded it.
2. **I will not invent one.**
   - The SEC asks automated clients to declare a contact address it can actually reach.
   - Writing an address nobody controls (for example a made-up project mailbox) would misrepresent who is accessing EDGAR.
   - If the SEC ever throttled or blocked us, they would have no one to contact.
3. **Current host status:**

| Host | Probe (2026-10-02 05:39 UTC, User-Agent `QuantTradingResearch PIT-audit private-research-project`) | Meaning |
|---|---|---|
| `www.sec.gov` | HTTP **403**, page title "SEC.gov \| Request Rate Threshold Exceeded" | The SEC's response to an undeclared automated client. It is not caused by request volume: this was the session's first request |
| `data.sec.gov` | HTTP 200 | Works as before |
| `www.quantconnect.com` | HTTP 200 | Works; credentials present |

## Why I stopped instead of doing the parts that don't need `www.sec.gov`

The True TTM layer (items 5–9) and the financial/REIT policy (item 10) could be built from `data.sec.gov` and QuantConnect alone. But:

- the owner made step 1 the gate for the whole stage;
- the final coverage and bias re-audit and the readiness verdict depend on the ticker-history repair.

So I followed the stop condition.

## What the owner needs to do (choose one)

1. **Recommended: give a project contact email** that someone actually reads, and that you are content to share with the SEC. A new free mailbox created for this project is fine, for example a dedicated address in your own mail provider.
   - No new session is needed: the network already allows `www.sec.gov`.
   - I will put it only in the SEC User-Agent and keep requests ≤ 8 per second, with caching.
   - It will not be committed to the repository. I will read it from an environment variable, `SEC_CONTACT_EMAIL`, set in the environment settings (that change needs a new session), or from your message.
2. **Allow True TTM and the REIT/financial policy to proceed now** using `data.sec.gov` only.
   - The survivorship ticker-history repair and the final readiness verdict would wait for the email.
3. **Explicitly allow your personal email for SEC requests only.** Not recommended, since you excluded it.

## Unchanged

- No H016, no profitability metric, ranking or factor return; no backtest; no slot used (1 of 3 consumed, 2 remain).
- The Holdout is locked; all D108/D111 protections stay in place; no prior result is rewritten.
