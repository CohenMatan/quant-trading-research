# H016 literature review: profitability and quality (P2-CP8, 2026-10-02)

- **Purpose:** choose ONE profitability/quality measure for H016 from external evidence, economic rationale and compatibility with our validated fields **before** any return is computed (owner items 9–11).
- **What was not used:** none of our 2010–2021 returns, factor returns or metric comparisons. The only project data consulted is **coverage** (how often each approved field exists point-in-time; final canary E976-06, no returns).
- **Citations** are from published papers; working-paper dates are given where they matter for timing.

## 1. Evidence available before our development period (published or circulated before 2010)

| Source | Finding | Relevance |
|---|---|---|
| Haugen & Baker (1996), *Commonality in the determinants of expected stock returns*, JFE 41 | Profitability measures (e.g. return on equity) are among the characteristics that predict the cross-section of returns, consistently across countries | Early evidence that more profitable firms earn higher returns |
| Sloan (1996), *Do stock prices fully reflect information in accruals and cash flows about future earnings?*, The Accounting Review 71 | The accrual part of earnings is less persistent than the cash part, and the market over-weights accruals | Earnings-based ratios are "polluted" by accruals; cleaner measures are preferable |
| Piotroski (2000), *Value investing: the use of historical financial statement information…*, JAR 38 (suppl.) | Simple accounting signals (ROA > 0, CFO > 0, accruals, …) separate winners from losers among value stocks | Profitability signals carry information; practitioner-friendly |
| Fama & French (2006), *Profitability, investment, and average returns*, JFE 82 | Controlling for B/M and investment, higher expected profitability implies higher expected returns (valuation-model logic) | **Economic rationale:** with price and book fixed, a firm with higher expected profits must have a higher discount rate |
| Fama & French (2008), *Dissecting anomalies*, JF 63 | Profitability's return relation is weaker and less robust than other anomalies in their earnings-based tests | Earnings-based profitability alone is a mixed signal; motivates better-measured profitability |

## 2. The gross-profitability evidence (circulated at the start of our development period)

**Novy-Marx (2013), *The other side of value: the gross profitability premium*, JFE 108(1)** (first circulated as NBER working paper 15940, April 2010):

- **Measure:** gross profits-to-assets, GP/A = (revenue − cost of goods sold) / total assets.
- **Strength:** it predicts the cross-section of returns roughly as strongly as book-to-market. It works **among large stocks** and within industries, and it is negatively correlated with value (so it hedges a value tilt).
- **Rationale:**
  - Gross profit is the cleanest accounting measure of a firm's economic productivity. "The farther down the income statement one goes, the more polluted profitability measures become."
  - Expenses such as R&D, advertising and sales costs are investments expensed under GAAP, so they depress net income without reducing true profitability.
  - Scaling by **assets** (not equity) keeps leverage out of the measure.
- **Exclusions:** financial firms are excluded (their statements have no comparable gross profit).

**Contemporaneous work:**
- Chen, Novy-Marx & Zhang (2011 working paper) and Hou, Xue & Zhang (2015, RFS 28) model expected returns with an ROE factor.
- Asness, Frazzini & Pedersen's "Quality minus junk" (working paper 2013; RAS 2019) builds quality from profitability (incl. gross profits over assets and cash flow over assets), growth, safety and payout.

**Timing caveat (disclosed):** the canonical GP/A paper became public during our development window (April 2010). Our 2010–2021 data is therefore essentially the **post-discovery** period of the published effect. That makes it a genuine out-of-sample test, and decay should be expected (§4).

## 3. Later replication and reassessment (2014–2017)

- **Fama & French (2015), *A five-factor asset pricing model*, JFE 116.** Operating profitability (RMW) becomes a priced factor.
- **Ball, Gerakos, Linnainmaa & Nikolaev (2015), *Deflating profitability*, JFE 117.**
  - Operating profitability (gross profit minus SG&A, adding back R&D) scaled by assets subsumes GP/A.
  - Part of GP/A's power comes from not deducting SG&A while matching revenue and cost of goods.
  - **We cannot build their measure:** our operating income failed SEC validation (48%), and SG&A is not on the whitelist.
- **Ball, Gerakos, Linnainmaa & Nikolaev (2016), *Accruals, cash flows, and operating profitability…*, JFE 121.** Cash-based operating profitability subsumes accruals and operating profitability. Their measure again needs operating expenses and working-capital items we do not have validated; operating cash flow over assets is only a cruder proxy (it includes interest, taxes and other cash items).
- **McLean & Pontiff (2016), *Does academic research destroy stock return predictability?*, JF 71.** Anomaly returns are about 26% lower out of sample and about 58% lower post-publication. **We plan for decay.**
- **Novy-Marx & Velikov (2016), *A taxonomy of anomalies and their trading costs*, RFS 29.** Low-turnover anomalies, gross profitability among them, keep most of their premium after realistic trading costs; high-turnover ones do not.
- **Harvey, Liu & Zhu (2016), RFS 29.** Multiple-testing hurdles for new factors. This is our reason to test **one** pre-chosen measure, not several.

## 4. After 2017 (reassessment only; NOT used for the choice)

**Hou, Xue & Zhang (2020), *Replicating anomalies*, RFS 33.** Most anomalies fail under value-weighting and NYSE breakpoints, but profitability anomalies are among the more robust ones. This post-2017 evidence is reported for context only; the choice below does not rely on it, under the hindsight rule in CLAUDE.md.

## 5. Practitioner conventions

- Quality indices and factor products (index-provider quality indices, academic and asset-manager factor libraries) use profitability ratios (ROE, ROA, gross profitability, cash-flow-to-assets) combined with leverage and earnings stability.
- Profitability sorts customarily **exclude financial firms**, and often utilities, because their statements are not comparable. Our approved policy excludes SIC 6000–6999 (incl. REITs, health insurers, real-estate services, exchanges, brokers and asset managers).
- Long-only implementations typically hold tens to hundreds of names and rebalance annually to quarterly, matching the slow arrival of accounting information.

## 6. Sector and accounting comparability

- GP/A rewards asset-light business models: software, consumer brands, health-care products. It penalises asset-heavy ones: utilities, energy, industrial manufacturing. Novy-Marx shows the effect also holds **within** industries, so it is not only an industry bet.
- In a concentrated long-only portfolio, an industry tilt will nevertheless appear. It is reported as a diagnostic, not constrained (a sector cap would be an extra, unvalidated rule).
- Companies that do not report a gross-profit line (many service and utility companies) have no GP/A and leave the H016 universe. This is a known, non-random coverage cost (§7).

## 7. Candidate measures against our validated fields (coverage only; no returns)

Share of non-financial eligible names with the measure computable. Final canary E976-06 on the frozen infrastructure v1 (2011 cleanup applied).

| Measure | Fields (all approved) | Coverage 2010 / 2011 / 2012–2021 | Literature as a stand-alone measure | Main weakness |
|---|---|---|---|---|
| **Gross profits-to-assets (GP/A)** | gross_profit_ttm4q, total_assets | 82% / 71% / 81–88% | **Dedicated top-journal evidence, incl. large caps** | Firms without a gross-profit line drop out; Ball et al. (2015) prefer operating profitability (not buildable here) |
| Cash flow-to-assets (OCF/A) | operating_cash_flow_ttm4q, total_assets | 90% / 82% / 89–94% | A component of composites (QMJ, Piotroski); cash-based OP is a different measure | Includes interest, taxes and working-capital swings; noisier year to year |
| Return on assets (NI/A) | net_income_ttm4q, total_assets | 87% / 81% / 88–93% | Older, mixed evidence (Fama–French 2008) | Accruals, one-offs, taxes and leverage pollute it |
| Return on equity (NI/E) | net_income_ttm4q, stockholders_equity | 85% / 79% / 84–89% | ROE-factor models | Equity is distorted by buybacks and is negative for 3–7% of names; leverage-driven |

## 8. Recommendation

**Gross profits-to-assets (GP/A)**, alone. It has:
- the strongest stand-alone evidence of the feasible measures, including in large caps and after costs;
- a clear economic rationale;
- low turnover;
- **both inputs independently validated against the SEC** (gross profit TTM 95.3% within 0.5%; total assets 98.8%).

Its coverage cost (about 5–8 points fewer names than OCF/A in most years) is disclosed and handled by the same-universe rule.

OCF/A is the only alternative with a genuinely distinct rationale (cash-based profitability). It is offered as the owner's alternative, not as a second candidate. **Both are never tested.**
