# P2-CP6a — SEC verification and survivorship remediation: blocked at step 0 (SEC access)

Date: 2026-10-01. Status: **STOPPED, awaiting the owner.** No work in this phase has been done beyond the access check.

## What was asked

The owner approved (2026-10-01) SEC verification of the QuantConnect fundamentals, resolution of the 0.3% accession
anomaly, an EDGAR-based repair of the D043 survivorship gap, a coverage/bias re-audit, a financial-exclusion audit and
new canaries, ending with an 18-item checkpoint. H016 is still not approved.

## SEC-access status (checkpoint item 1)

| Host | Result in this session | Meaning |
|---|---|---|
| `data.sec.gov` | refused by the environment proxy (no connection) | blocked by the network policy |
| `www.sec.gov` | refused by the environment proxy (no connection) | blocked by the network policy |
| `www.quantconnect.com` | reachable (HTTP 200) | unchanged |

Probes used the project User-Agent `QuantTradingResearch PIT-audit private-research-project` (no personal data). The
request never left the container, so nothing was sent to the SEC.

## Why I stopped instead of continuing

Every substantive item in this phase depends on SEC data:

- verification of timing and values needs the SEC filing dates and XBRL values;
- the accession anomaly can only be classified (original value / later restatement / wrong reference) against the
  SEC filing index;
- the D043 repair must use historical SEC data only (owner rule), so there is no compliant substitute;
- the coverage, bias and canary items measure the effect of that repair.

The owner's stop condition applies: reliable point-in-time reconstruction cannot be achieved without SEC data, and I
will not approximate it. The financial-format disagreement audit could be run on QuantConnect alone, but it is a
small part of the same checkpoint; I have left it for the same session as the rest, so that the checkpoint is
produced once, on one code version.

## What the owner needs to do

1. In the cloud environment's settings (environment menu in the session title bar → Edit → Network access), add
   `data.sec.gov` and `www.sec.gov` to the allowed domains (or choose a broader access level).
   Reference: https://code.claude.com/docs/en/claude-code-on-the-web
2. Start a **new** session (network settings only take effect in a new session) and re-send the approval.

## Unchanged

H016 not designed; no backtests, no factor results; Holdout locked; Phase 2 budget 1 of 3 slots used; all PIT policies
(D108) unchanged; no prior results rewritten.
