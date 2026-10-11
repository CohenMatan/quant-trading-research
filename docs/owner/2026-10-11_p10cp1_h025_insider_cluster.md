# Owner message 2026-10-11: "Phase 10 — H025 Insider Cluster Buying. Event-Driven Research Using SEC Form 4 Filings"

Decision id: **D204** (closes H024 / Phase 9 as NO ROBUST H024 FEATURE MODEL / No Production Candidate Found and approves H025). Recorded and committed BEFORE any H025 event, null world or return is computed. The owner's message follows verbatim.

---

Phase 10 — H025
Insider Cluster Buying
Event-Driven Research Using SEC Form 4 Filings
Continue from:
P9-CP1 — H024 Feature Redesign and Selection
Owner decision:
Close H024 and Phase 9 as NO ROBUST H024 FEATURE MODEL / No Production Candidate Found.
H022, H023 and H024 remain permanently closed exactly as tested.
I now approve a new and materially different research hypothesis:
H025 — Insider Cluster Buying
This is an event-driven hypothesis based on newly disclosed insider purchases, not a cross-sectional Score model.
Do not reuse or tune Score v1/v2/v3.
1. Research hypothesis
Test:
When multiple corporate insiders independently purchase meaningful amounts of their company's common stock in the open market within a short period, does the stock subsequently outperform the market over the following several weeks?
Economic rationale:
Multiple insiders purchasing their own stock with personal capital may contain information about perceived undervaluation or future company prospects.
The key distinction from prior work is:

```
new publicly disclosed corporate event
→
future return
```

rather than:

```
historical price/fundamental characteristics
→
cross-sectional score
```

2. Development and validation periods
For H025:

```
2011–2017 = DEVELOPMENT / TRAINING
```

Use this period to evaluate the frozen H025 definition.
Do not access future returns after 2017 during this checkpoint.
For a future validation:

```
2018–2021 = H025-specific validation candidate
```

However, permanently disclose that 2018–2021 is not globally pristine across the entire research programme, because unrelated previous hypotheses have already used parts of that period.
It has not been used to design H025.
Therefore later describe it as:

```
H025-SPECIFIC OOS VALIDATION
NOT PROGRAMME-WIDE PRISTINE HOLDOUT
```

The true programme-wide untouched Holdout remains:

```
2022-01-01 → 2026-08-31
```

Do not access it.
3. Data source
Use official SEC Form 4 filings as the primary insider-event source.
Prefer official SEC EDGAR records and filing XML/document data.
For every filing preserve, where available:

```
issuer CIK
issuer ticker / security identity
reporting-owner CIK
reporting-owner name
officer/director status
10% owner status
officer title
transaction date
SEC filing acceptance timestamp
transaction code
acquired/disposed indicator
number of shares
transaction price
direct/indirect ownership
security title
accession number
```

The important PIT timestamp is:
when SEC made the Form 4 filing public, not when the insider executed the trade.
Never assume the market knew about the transaction on the transaction date.
4. SEC timing rule
Use the SEC filing acceptance timestamp as the information-arrival time.
A transaction cannot influence the strategy before its filing is publicly available.
The signal time is therefore determined exclusively from Form 4 filings that had already been accepted by the SEC.
If exact acceptance time is unavailable or ambiguous:

```
exclude the filing
```

unless a conservative, pre-registered fallback can be proven PIT-safe.
Do not use later knowledge to reconstruct an earlier signal.
5. Eligible insider transaction
For the primary H025 definition, count only:

```
Form 4
non-derivative common equity
transaction code P
acquisition
open-market / private purchase represented by code P
```

Exclude:

```
stock awards
option exercises
conversions
gifts
tax withholding
sales
derivative transactions
automatic grants
non-purchase acquisitions
```

Do not infer an open-market purchase from transaction direction alone.
The SEC transaction code must qualify.
6. Insider eligibility
For the primary hypothesis, qualifying reporting owners must be:

```
Director
and/or
Officer
```

A person whose only relationship is:

```
10% Owner
```

does not count toward the primary cluster.
If someone is both:

```
Director/Officer + 10% Owner
```

they may qualify because of the Director/Officer role.
Distinct insiders must be identified by reporting-owner CIK where possible.
Do not count multiple filings by the same person as multiple insiders.
7. Ownership type
For the primary specification use only transactions reported as:

```
Direct ownership
```

Exclude indirectly owned purchases from the primary signal.
Reason:
Indirect ownership may represent trusts, family entities, partnerships or other structures whose economic interpretation is less uniform.
Indirect transactions may later be reported as a non-gating diagnostic only.
Do not add them to the primary definition after seeing results.
8. Minimum purchase size
A qualifying insider's purchases must total at least:

```
$25,000
```

within the cluster window.
Calculate purchase value as:

```
shares × transaction price
```

using only valid reported purchase prices.
The combined qualifying purchases of the cluster must total at least:

```
$100,000
```

Do not optimise these thresholds.
9. Cluster definition
Define the primary insider cluster as:

```
at least 2 distinct qualifying insiders
```

whose qualifying purchases become publicly known within:

```
10 calendar days
```

for the same issuer.
Required conditions:

```
distinct insiders >= 2
each insider aggregate purchase >= $25,000
cluster aggregate purchase >= $100,000
```

Do not require the transactions themselves to occur within exactly the same period if filing delays differ.
The primary clustering clock is based on:

```
public SEC filing availability
```

because this is when the strategy could know about them.
10. Online cluster construction
The cluster must be constructed as it would have been known live.
At any timestamp `t`, use only Form 4 filings publicly available by `t`.
A cluster event triggers at the first SEC acceptance timestamp when all frozen criteria become true.
Example:

```
Insider A filing public Monday
Insider B filing public Thursday
```

If Thursday completes the cluster:

```
event timestamp = Thursday filing acceptance timestamp
```

Do not later move the event backward to Monday because we now know Insider B eventually bought.
This is critical.
11. No future cluster leakage
After an event triggers, later insider purchases may not retroactively strengthen the original signal.
Record later purchases descriptively, but the primary event's:

```
signal timestamp
entry
classification
```

must remain exactly as known when the cluster first qualified.
12. Repeated events
To prevent overlapping repeated signals in the same company, after an H025 event triggers impose:

```
20 trading-session issuer cooldown
```

No second primary H025 event may trigger for the same issuer during the cooldown.
Do not optimise the cooldown.
13. Security universe
A signal qualifies only if the issuer was eligible under the already-established large/liquid US-equity research universe.
Use the most recent available frozen monthly Data v2 eligibility determination before the SEC event timestamp.
Required existing filters remain:

```
US common stock
NYSE / Nasdaq
PIT market cap >= $2B
price >= $5
ADV20 >= $5M
```

Do not build a new universe around the event results.
Do not use future month-end eligibility.
14. Security identity
Use the existing verified SEC/security identity infrastructure wherever possible.
The issuer CIK in Form 4 must map safely to the traded security.
If issuer/security identity is:

```
ambiguous
REJECT
unresolved
```

exclude the event.
Do not use modern ticker/name similarity to force historical mappings.
Report all identity exclusions.
15. Primary trade timing
The strategy may never trade at or before the information-arrival timestamp.
For every qualifying cluster:
Enter at the next regular trading-session open after the cluster becomes publicly known.
Even if the SEC filing appears during market hours, do not trade intraday.
Use:

```
signal → next session open
```

16. Primary holding period
Freeze the primary holding period at:

```
20 trading sessions
```

Exit:

```
close of the 20th trading session after entry
```

No:

```
stop loss
take profit
trailing stop
early signal-based exit
```

Do not optimise holding period.
17. Primary return
Calculate total shareholder return from:

```
next-session open
→
20th-session close
```

including corporate actions according to the existing verified price-handling rules.
Primary abnormal return:

```
stock TSR - SPY TSR
```

over the identical entry/exit window.
Use SPY total return consistently.
18. Diagnostics only
Also report, but do not gate or optimise on:

```
5-session excess return
10-session excess return
40-session excess return
60-session excess return
raw stock TSR
sector-relative return
```

20 sessions remains primary.
Do not switch primary horizon after seeing these results.
19. Event-level dataset construction comes first
Before looking at any forward returns, build and freeze the 2011–2017 H025 event ledger.
The event ledger must contain:

```
event_id
issuer
security id
issuer CIK
cluster trigger timestamp
entry session
qualifying insider count
each qualifying insider id
roles
filing accession numbers
transaction dates
filing acceptance timestamps
shares
prices
purchase values
cluster aggregate value
most recent universe review date
eligibility result
identity status
exclusion reason if excluded
```

Do not include future-return columns yet.
20. Feasibility gate before returns
Before computing any H025 return, report:

```
Form 4 filings inspected
qualifying code-P purchases
distinct issuers
cluster events before universe filtering
cluster events after universe filtering
events/year
insiders/event
aggregate purchase-value distribution
identity exclusions
missing-price exclusions
missing-acceptance-time exclusions
```

Minimum required sample:

```
>= 100 primary events total
>= 5 calendar years with >= 10 events
```

If this is not satisfied:

```
STOP
```

Do not weaken the cluster definition simply to increase sample size.
Return for owner review.
21. Event-ledger determinism
Rebuild the event ledger independently.
The same SEC inputs must produce:

```
identical event IDs
identical trigger timestamps
identical insiders
identical entry sessions
identical eligibility states
```

Pin:

```
EVENT_LEDGER_SHA256
```

before any real forward return is attached.
22. Canary
Create an H025 canary that verifies:

```
SEC filing timing
Form 4 transaction parsing
code P handling
insider deduplication
cluster creation
no future cluster leakage
20-session cooldown
issuer/security identity
universe eligibility
next-open timing
corporate actions
20-session response timing
```

Use synthetic/fake returns where possible.
Do not inspect real H025 returns during the canary.
23. Primary statistical unit
Because events occur on arbitrary dates and can cluster through time, do not treat every event as fully independent.
For each calendar month:

```
monthly_H025_excess =
mean 20-session SPY-relative return
of H025 events triggered that month
```

Primary statistical series:

```
monthly H025 excess-return series
```

Calculate:

```
mean monthly event excess
Newey-West t-statistic
```

Use:

```
NW lag = 2
```

unless the frozen implementation demonstrates that the 20-session overlap requires a higher pre-registered lag.
If changing from lag 2 is statistically necessary, decide and document it before real returns are computed.
24. Null calibration
Before examining the real H025 result, create:

```
5,000 null worlds
```

The null must preserve the event timing structure.
For each real event timestamp:

1. preserve the event date;
2. preserve the market environment;
3. choose a different eligible stock that did not have the H025 event;
4. where feasible, match on:


```
FF12 sector
market-cap bucket
```

5. calculate the same next-open → 20-session-close SPY-relative return.

The null therefore asks:
What apparent event performance can be generated merely by these dates, sectors, sizes and market conditions when the insider event is assigned to the wrong stock?
25. Null matching rules
Pre-register exact matching before running real H025 returns.
Recommended hierarchy:

```
same FF12 sector
same market-cap quintile
eligible on same event date
not actual issuer
no overlapping H025 event for selected pseudo-issuer
```

If the matching cell is empty, use a pre-registered deterministic fallback such as:

```
same sector, nearest market-cap bucket
```

Do not choose fallback rules after seeing results.
26. Null threshold
For each null world compute the complete primary H025 statistic.
Set:

```
c_EVENT =
max(
    empirical one-sided 99th percentile null t-statistic,
    2.326
)
```

Use the same empirical order-statistic convention used in previous phases.
Pin:

```
c_EVENT
null result hash
event-ledger hash
response-panel hash
```

before the real event result is computed.
27. Development gates
H025 becomes a development candidate only if all gates pass.
G1 — Statistical significance

```
real t_EVENT > c_EVENT
AND
mean event excess > 0
```

G2 — Economic magnitude
Require:

```
mean 20-session SPY-relative event return >= +2.0%
```

Do not annualize the 20-session event return for this gate.
G3 — Distributional support
Require:

```
median event excess > 0
AND
event win rate > 50%
```

where:

```
win = 20-session stock TSR > SPY TSR
```

G4 — Temporal stability
Require:

```
2011–2014 mean event excess > 0
2015–2017 mean event excess > 0
```

and at least:

```
5 of 7 calendar years
```

have positive mean event excess.
G5 — Sample adequacy
Require:

```
>= 100 total events
>= 5 calendar years with >= 10 events
```

All five gates must pass.
28. Cluster-strength diagnostics
After the primary result, report these as non-gating diagnostics only:

```
2 insiders vs 3+ insiders
$100k–250k cluster value
$250k–1m
>$1m
CEO/CFO involved vs not
director-only clusters
number of purchases
filing delay
```

Do not use any subgroup to rescue H025.
No subgroup becomes the new primary result.
29. Single-insider control
As a diagnostic only, construct comparable events where:

```
one qualifying insider
purchase >= $100,000
```

but no cluster formed.
Compare its outcome with H025 cluster events.
This may help assess whether:

```
multiple insiders
```

adds information beyond a large single purchase.
It is not an alternative H025 specification.
30. Random-event control
Also report performance of matched pseudo-events from the null process.
The real result should not merely reflect:

```
market rebounds
small-cap effects
sector rebounds
calendar timing
```

31. No optimisation after seeing development returns
Do not try:

```
5-day cluster instead of 10
3 insiders instead of 2
$50k instead of $25k
$250k aggregate instead of $100k
indirect ownership
10% owners
10-day hold
40-day hold
```

after seeing the primary result.
Any altered definition becomes:

```
H026 or later
```

and requires a separate owner decision.
32. No score construction
Do not combine H025 with:

```
momentum
LOWVOL
REV1M
valuation
Score v1
Score v2
H024 features
```

during the primary test.
First determine whether the insider event itself contains edge.
Feature combinations may be considered only in a later hypothesis if H025 itself warrants it.
33. No portfolio simulation yet
Do not calculate:

```
portfolio CAGR
terminal wealth
Sharpe
max drawdown
position sizing
concurrent-position rules
turnover
```

in this checkpoint.
This stage tests whether the event has predictive value.
If H025 passes, portfolio mechanics are a later stage.
34. Development run order
Use exactly this order:

```
1. Build SEC Form 4 parser
2. Build historical issuer/insider event ledger
3. Freeze cluster rules
4. Run no-return feasibility audit
5. Verify minimum sample
6. Run deterministic rebuild
7. Pin event-ledger hash
8. Canary
9. Build response/null machinery without exposing real result
10. Run 5,000 matched null worlds
11. Pin c_EVENT
12. One real 2011–2017 H025 development evaluation
13. Apply G1–G5
14. Run pre-registered diagnostics
15. STOP
```

35. If SEC data is insufficient
Do not substitute a commercial or scraped dataset silently.
If official SEC Form 4 data cannot provide reliable historical:

```
acceptance timestamp
reporting owner
transaction code
shares
price
ownership status
```

at adequate coverage:

```
STOP
```

Report precisely what is missing.
Do not purchase anything.
36. QuantConnect is not the source of truth for Form 4 timing
Price/market data may continue to use the existing approved infrastructure.
But Form 4 event timing must come from the frozen SEC event ledger.
Do not infer insider-event timing from modern fundamentals or vendor snapshots.
37. Future H025 validation
If and only if H025 passes G1–G5 on development:
Freeze the complete H025 specification.
Then STOP.
Do not immediately access 2018–2021.
A later owner-approved stage may build a PIT-safe 2018–2021 event/data extension and perform one H025-specific OOS validation.
38. Future validation must use identical rules
No changes after development to:

```
insider roles
code P
direct ownership
$25k per insider
$100k cluster aggregate
2-insider minimum
10-calendar-day cluster
20-session cooldown
next-open entry
20-session holding period
SPY-relative primary response
```

39. Future validation gates
Pre-register the future 2018–2021 validation concept now.
Once the validation event ledger and response panel are independently frozen:
Run a fresh:

```
5,000 matched null calibration
```

and pin:

```
c_EVENT_VALIDATION
```

before the real mapping.
Require:

```
V1: t_EVENT > c_EVENT_VALIDATION and mean > 0
V2: mean 20-session SPY-relative return >= +2.0%
V3: median > 0 and win rate > 50%
V4: both 2018–2019 and 2020–2021 mean excess > 0
V5: adequate event count
```

All must pass.
40. Holdout policy
The 2022–2026 Holdout remains unopened.
Even if H025 passes 2011–2017:

```
do not touch Holdout
```

Even if H025 later passes 2018–2021:

```
do not touch Holdout without a separate owner decision
```

41. Required checkpoint
Create:
P10-CP1 — H025 Insider Cluster Buying
Include at minimum:

1. Owner decision ID.
2. Confirmation H022 closed.
3. Confirmation H023 closed.
4. Confirmation H024 closed.
5. SEC source description.
6. SEC retrieval method.
7. SEC timing rule.
8. Form 4 parsing rules.
9. Transaction-code rules.
10. Insider-role rules.
11. Ownership rule.
12. Per-insider dollar threshold.
13. Cluster dollar threshold.
14. Cluster time window.
15. Minimum distinct insiders.
16. Online trigger rule.
17. Cooldown.
18. Universe eligibility rule.
19. Identity mapping rule.
20. Development period.
21. Form 4 filings inspected.
22. Qualifying purchase count.
23. Pre-universe cluster count.
24. Post-universe event count.
25. Events by year.
26. Insiders/event distribution.
27. Purchase-value distribution.
28. Identity exclusions.
29. Timing/data exclusions.
30. Sample-adequacy PASS/FAIL.
31. Event-ledger hash.
32. Determinism result.
33. Canary status.
34. Response construction.
35. Primary 20-session return definition.
36. Null matching rule.
37. Null-world count.
38. Null determinism result.
39. Null distribution.
40. `c_EVENT`.
41. Real event count.
42. Real mean 20-session SPY-relative return.
43. Median excess.
44. Win rate.
45. Monthly mean event excess.
46. Real t_EVENT.
47. Null percentile/p-value.
48. G1 result.
49. G2 result.
50. G3 result.
51. G4 result.
52. G5 result.
53. Results by year.
54. First/second-period results.
55. 5/10/40/60-session diagnostics.
56. Cluster-size diagnostics.
57. Dollar-size diagnostics.
58. CEO/CFO diagnostic.
59. Single-insider control.
60. Confirmation no definition changed after results.
61. Confirmation no portfolio was evaluated.
62. Confirmation 2018–2021 not accessed for H025.
63. Disclosure that 2018–2021 is not programme-wide pristine.
64. Confirmation Holdout untouched.
65. Confirmation nothing purchased.
66. Final result:


```
DEVELOPMENT CANDIDATE — H025 PASSED, VALIDATION NOT YET RUN
```

or:

```
H025 REJECTED — NO ROBUST INSIDER-CLUSTER EDGE
```

or, if infrastructure/sample is inadequate:

```
H025 BLOCKED — SEC EVENT DATA / SAMPLE INSUFFICIENT
```

67. Exact next owner decision.

42. STOP conditions
STOP without weakening the hypothesis if:

```
SEC timing cannot be made PIT-safe
identity mapping is unreliable
event sample < required minimum
null calibration fails
determinism fails
real H025 fails any gate
```

Do not modify the definition to obtain a better result.
43. Final principle
H025 is deliberately simple:
multiple insiders spend meaningful personal capital buying the same company's common shares, the purchases become publicly disclosed, and we test what happens next.
Keep the event definition interpretable.
Do not turn H025 into another large factor optimisation exercise.
After P10-CP1:
STOP and return for owner review.
