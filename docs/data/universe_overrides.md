# Universe overrides (D061 / D065): dated corrections to Morningstar's current-status labels

Morningstar's company flags and names describe each company's **current** status. For companies whose legal form changed during 2010–2021, the harness applies these **dated** verdicts, keyed by QuantConnect security identifier.

- "Common" means eligible US common stock; anything else is excluded.
- Outside the listed dates, the general rules of `non_common_reason()` apply.

| Security | Until | From | Source |
|---|---|---|---|
| Yahoo / Altaba (YHOO R735QTJ8XC9X) | 2017-06-15: common (operating company) | 2017-06-16: registered closed-end fund (general rule, template V) | Altaba press release and SEC Form N-2 (2017) |
| Blackstone (BX TTO1M4GXI99H) | 2019-06-30: partnership units | 2019-07-01: common | Blackstone 8-K, 2019-07-01 |
| Carlyle (CG V69R09HVGXGL) | 2019-12-31: partnership units | 2020-01-01: common | Carlyle release, 2020-01-01 |
| KKR (KKR UO9UUQST4HUT) | 2018-06-30: partnership units | 2018-07-01: common | KKR & Co. Inc. 10-Q Q2 2018 |
| Apollo (APO UVBW6V6CV59H) | 2019-09-04: LLC shares | 2019-09-05: common | Apollo 8-K and release, 2019-09-05 |
| Ares (ARES VQ7JWF5X8XGL) | 2018-11-25: partnership units | 2018-11-26: common | Ares 10-K 2018 (legal conversion 2018-11-26; taxed as a corporation from 2018-03-01) |
| Macquarie Infrastructure (MIC T4K58ANZ9NXH) | 2015-05-20: LLC interests | 2015-05-21: common | MIC 8-K, 2015-05-21 |
| KKR Financial (KFN T9R86261T0F9) | whole life (to its acquisition, 2014-04-30): LLC shares | — | KKR release, 2014-04-30 |
| Texas Pacific Land (TPL R735QTJ8XC9X) | 2021-01-10: trust sub-share certificates | 2021-01-11: common | TPL 8-K, 2021-01-11 |
| Burford Capital (BUR XIT9T96LYYJP) | always common (operating company, although tagged as an investment vehicle) | — | Company filings |
| ACAS (ACAS R735QTJ8XC9X) | whole life: business development company (fund) | — | American Capital 10-K |

**How the list was made.**

- The probe E956-02 recorded every security admitted by the D057 rule from 2010 to 2021.
- It was searched for LLC, partnership, unit, trust and fund wording in legal names and share classes, and for known partnership-to-corporation conversions.
- Everything else found was either correctly excluded already, or an acquired corporation whose current successor is an LLC. Those correctly stay eligible (see D061).

**Correction to earlier reports.** CP4 counted MIC among E005-28's non-common holdings. MIC was a corporation from 2015-05-21, so its 2021 holding in E005-28 was ordinary common stock.
