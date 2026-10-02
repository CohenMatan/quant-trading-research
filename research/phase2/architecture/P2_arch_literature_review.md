# Research architecture review: literature on the remaining families (P2-CP11, 2026-10-02)

- **Scope:**
  - event-driven / earnings strategies;
  - relative-strength swing;
  - catalyst + continuation;
  - medium-term fundamental strategies (summary; the detailed value review is `research/phase2/P2_final_slot_literature_review.md`).
- **Rules:**
  - no return of any candidate measure was computed;
  - no Holdout-era or post-2021 performance was consulted;
  - citations are from memory with year and venue, and **must be verified before any number is quoted**;
  - where I am unsure of a magnitude, I state only the direction.
- **Evidence labels:**
  - **[<2000]:** published before 2000;
  - **[2000–09]:** published 2000–2009;
  - **[2010+]:** published 2010 or later (often covering our development window);
  - **[practice]:** practitioner experience;
  - **[ours]:** our inference.
- **The central distinction** throughout is **academic anomaly** (gross, long-short, equal-weighted, often small-cap) versus **realistic personal-account strategy** (net, long-only, large-cap, 20–40 positions, $7 per order, beating cap-weighted SPY).

## A. Event-driven / earnings strategies

### A1. Post-earnings-announcement drift (PEAD) and earnings momentum

| Label | Source | Finding |
|---|---|---|
| [<2000] | Ball & Brown (1968), JAR | Returns keep drifting in the direction of the earnings news after the announcement |
| [<2000] | Foster, Olsen & Shevlin (1984), Accounting Review | Drift after standardised unexpected earnings (SUE), strongest in small firms |
| [<2000] | Bernard & Thomas (1989, JAR; 1990, JAE) | Drift lasts about 60 trading days. Prices under-react to the time-series pattern of earnings, and part of the drift recurs at the next announcements. Larger in small firms |
| [<2000] | Chan, Jegadeesh & Lakonishok (1996), JF | Earnings momentum (SUE, analyst revisions, **announcement return**) predicts returns for 6–12 months, separately from price momentum |
| [2000–09] | Livnat & Mendenhall (2006), JAR | Surprise measured against analysts' consensus produces a larger drift than time-series SUE |
| [2000–09] | Brandt, Kishore, Santa-Clara & Venkatachalam (2008, working paper) | Drift after the **earnings-announcement return** (EAR): the price reaction itself is a robust surprise measure that needs no estimates |
| [2000–09] | Hirshleifer, Lim & Teoh (2009), JF; DellaVigna & Pollet (2009), JF | More drift when investors are distracted (busy days, Fridays): **behavioural under-reaction** rationale |
| [2000–09] | Sadka (2006), JFE; Chordia, Goyal, Sadka, Sadka & Shivakumar (2009), FAJ | PEAD is concentrated in **illiquid** stocks; trading costs absorb much of it; liquid large caps show little drift |
| [2010+] | Martineau (2022), Critical Finance Review, "Rest in peace post-earnings announcement drift" | In large, liquid US stocks the drift has **largely disappeared since the mid-2000s**: prices incorporate the surprise on the announcement day |
| [2010+] | Novy-Marx (2015, working paper), "Fundamentally, momentum is fundamental momentum" | Earnings surprises largely subsume price momentum: the "fundamental" part is what predicts |
| [2010+] | McLean & Pontiff (2016), JF | Post-publication decay applies; PEAD is among the oldest published anomalies |

**What it means for us [ours]:**
- **Academic anomaly:** strong, with a clear behavioural rationale.
- **Realistic personal-account strategy:** the evidence points to a **small or vanished** large-cap drift after about 2005, exactly our period and size range.
- A long-only book captures only the positive-surprise leg.

### A2. Earnings-announcement premium (holding stocks through scheduled announcements)

| Label | Source | Finding |
|---|---|---|
| [<2000] | Beaver (1968), JAR | Announcements carry more information; returns are higher around them |
| [2000–09] | Frazzini & Lamont (2007, working paper), "The earnings announcement premium and trading volume" | Stocks earn a premium in months with expected announcements, larger for stocks with high past announcement volume |
| [2010+] | Barber, De George, Lehavy & Trueman (2013), JFE | The announcement premium exists around the world |

**What it means for us [ours]:**
- Predictable dates (from the prior year's schedule, point-in-time) make this implementable.
- It is a **risk premium for event risk**, and modest in size.
- Turnover is high: every stock rotates every quarter.
- Long-only at 20–40 positions, the cost and concentration make it doubtful.

### A3. Data feasibility (measured, not assumed)

- **Event timestamps (free, point-in-time).**
  - SEC 8-K filings carry Item 12 "Results of Operations" (2003-03-28 → 2004-08-22) and Item 2.02 (from 2004-08-23), with an **acceptance timestamp** (time of day). That tells a before-open release from an after-close one.
  - **Probe** (`research/phase2/architecture/sec_8k_earnings_probe.json`; metadata only, no prices):
    - 34 of 40 large surviving companies have earnings 8-Ks in 2003;
    - 37–39 of 40 do in every year 2004–2021, at about 4.3 a year (quarterly);
    - large companies that **failed or were acquired** (Lehman, Bear Stearns, Merrill Lynch, Countrywide, Wachovia, Lucent) carry them until their end, so the source is **survivorship-safe**.
  - Before 2003 earnings releases are not identifiable from metadata.
- **Surprise without estimates:** the announcement-day price reaction (EAR) and the abnormal volume, from QuantConnect prices. This is point-in-time: the reaction is known at the close of the event window.
- **Consensus estimates** (not owned):
  - **EODHD "Upcoming Earnings"** on QuantConnect: from January 1998, with report date, report time and an EPS estimate. QuantConnect states 96.8% capture and 97.3% exact-date precision against Nasdaq's calendar. Whether the **estimate is point-in-time** is unverified. Paid; price not verified.
  - **Estimize** (ExtractAlpha): from 2011, crowd-sourced. Paid.
  - **I/B/E/S:** institutional only (WRDS); out of budget.
- **Earnings values at announcement:** Morningstar's file date is the 10-Q/10-K filing date, which **lags the press release by days to weeks**. Building SUE from Morningstar would misdate the surprise, so SUE-based PEAD is **not** point-in-time safe with our data. EAR-based drift is.

## B. Relative-strength swing (vs market, vs sector, with consolidation / re-entry)

| Label | Source | Finding |
|---|---|---|
| [<2000] | Jegadeesh & Titman (1993), JF | 3–12-month winners beat losers over the next 3–12 months |
| [<2000] | Moskowitz & Grinblatt (1999), JF | Much of stock momentum is industry momentum |
| [2000–09] | George & Hwang (2004), JF | Nearness to the 52-week high subsumes much of momentum |
| [2000–09] | Grinblatt & Moskowitz (2004), JFE | Consistency of past returns matters |
| [2010+] | Blitz, Huij & Martens (2011), JEF | Residual (idiosyncratic) momentum is more stable than total-return momentum |
| [2010+] | Daniel & Moskowitz (2016), JFE | Momentum crashes in rebounds after bear markets (e.g. 2009) |
| [practice] | — | Relative-strength-plus-base/consolidation entries are a staple of discretionary swing trading; there is no rigorous large-sample evidence for the consolidation filter itself |

**Overlap with what we tested:**
- H002 (12-1 momentum);
- H003 (52-week high);
- H004 (pullbacks in momentum leaders);
- H008 (residual relative strength);
- H006 / H007 (breakout, squeeze);
- H014 (trend + pullback + recovery).

**What it means for us [ours]:** "strength vs SPY + vs sector + a pause/re-entry condition" is a **combination of five families we have already rejected**. The sector-relative element would be new: point-in-time SIC at filing exists from 2009. But the independent evidence for the combination is practitioner lore, not research. **Not genuinely different; not recommended.**

## C. Catalyst + price continuation

| Label | Source | Finding |
|---|---|---|
| [2000–09] | Chan (2003), JFE, "Stock price reaction to news and no-news" | Large moves **with** public news continue; large moves **without** news tend to reverse |
| [2010+] | Savor (2012), JFE, "Stock returns after major price shocks: the impact of information" | Shocks accompanied by information (analyst reports) drift; uninformed shocks reverse |
| [2000–09] | Gervais, Kaniel & Mingelgrin (2001), JF | Unusually high volume predicts higher returns (visibility) |

**Distinctness from what we tested:**
- Our H010 (gap continuation) and H009 (volume shock) conditioned on **price/volume only**, pooling informed and uninformed moves.
- The literature says exactly that pooling cancels the effect. Conditioning on a **verified information event** is a genuinely different hypothesis.

**Data:**
- The only point-in-time-safe, survivorship-safe catalyst we can source free is the **earnings release** (8-K Item 2.02).
- Other catalysts are either not available or too short:
  - Benzinga news: 2017+ only;
  - Smart Insider buybacks: 2015+ only;
  - other 8-K items (M&A, guidance, management changes) are available but heterogeneous.
- In practice, **C reduces to A with the EAR measure:** "earnings release → large price/volume reaction → continuation".

## D. Medium-term fundamental strategies (summary)

| Family | Evidence summary | Data (point-in-time) | Large-cap long-only |
|---|---|---|---|
| Value (B/M) | [<2000] strong (Fama & French 1992; Lakonishok, Shleifer & Vishny 1994); [2000–09] weaker in large caps (Loughran 1997; Fama & French 2006); [2010+] lower premium 1991–2019 (Fama & French 2021) | Ready (equity, market cap) from 2010 | Weak / modest; 2010s headwind is public knowledge |
| Net issuance / payout | [<2000] Ikenberry et al. 1995; Loughran & Ritter 1995; [2000–09] Daniel & Titman 2006; Pontiff & Woodgate 2008; Fama & French 2008 (robust in big stocks) | Needs an audit (share counts unsafe; market-cap construction unaudited); Smart Insider buybacks only 2015+ | Modest; mainly the short leg |
| Investment / asset growth | [2000–09] Cooper, Gulen & Schill 2008; Fama & French 2008 (weak in big stocks) | Ready | Weak; overlaps value |
| Quality distinct from H016 (accruals, F-score) | [<2000] Sloan 1996; [2000–09] Piotroski 2000 (mostly small value firms); [2010+] decay (Green, Hand & Soliman 2011) | Accruals ready; F-score needs unapproved fields (debt, current ratio, shares) | Weak |
| Value + profitability combination | [2010+] Novy-Marx 2013; Fama & French 2015 | Ready | Owner excluded profitability re-use; background only |

## E. Cross-cutting: academic anomaly vs our account [ours]

1. **Long-short → long-only.**
   - For momentum and issuance, much of the premium sits in the short leg (Stambaugh, Yu & Yuan 2012).
   - For value, a larger share sits on the long side (Israel & Moskowitz 2013).
2. **Small → large.** Almost every anomaly is weaker in large caps; PEAD most of all.
3. **Gross → net.** Low-turnover families (value, issuance) keep their premium (Novy-Marx & Velikov 2016). Event families do not, unless the edge per trade is large.
4. **Universe → SPY.**
   - Academic benchmarks are equal-weighted universes or factor portfolios.
   - Our target is the cap-weighted S&P 500, whose 2010–2021 mega-cap leadership is itself a headwind for every equal-weighted large-cap strategy.
   - In our completed controls, the equal-weight ≥ $2B universe ended with less wealth than SPY in 87% of 10-year windows.
5. **Publication decay.** Expect roughly half of the published premium at best (McLean & Pontiff 2016).
