# H017 literature review: earnings-event continuation (P2-CP13, 2026-10-03)

- **Purpose:** choose ONE exact design for H017 (reaction measure, threshold, volume yes/no, holding period, exit) from external evidence **before** any return is computed.
- **What was not used:** no event-reaction, post-event, factor or strategy return in our data.
- **Project data used:** only event **timing / frequency** metadata (Event Data v1).
- **Citations:** from memory with year and venue. **Verify before quoting any magnitude.** Where unsure I give the direction only.
- **Labels:**
  - **[orig]:** original PEAD research;
  - **[<2005]:** evidence published before 2005;
  - **[≥2005]:** evidence published 2005 or later;
  - **[practice]:** practitioner experience;
  - **[ours]:** our inference.

## 1. Original post-earnings-announcement drift [orig]

| Source | Finding | Design relevance |
|---|---|---|
| Ball & Brown (1968), JAR | After annual earnings, prices keep drifting in the direction of the news | The phenomenon |
| Foster, Olsen & Shevlin (1984), Accounting Review | Drift after standardised unexpected earnings (SUE) over about 60 trading days; strongest in small firms | Horizon of about one quarter |
| Bernard & Thomas (1989), JAR; (1990), JAE | Drift lasts about **60 trading days**, a sizeable part recurs around the **next** announcements, and it is larger in small firms. Investors under-weight the serial correlation of earnings changes | **Holding period:** about 60 sessions, i.e. up to the next announcement |

## 2. Reaction-based (estimate-free) evidence

| Label | Source | Finding | Design relevance |
|---|---|---|---|
| [<2005] | Chan, Jegadeesh & Lakonishok (1996), JF, "Momentum strategies" | Three measures of earnings news (SUE, analyst revisions, and the **abnormal return around the announcement**, days −2…+1) each predict returns over the next 6–12 months. The announcement-return effect is distinct from price momentum, and strongest in the first months | **Reaction measure:** the market's own announcement reaction carries the news; **decile** sorts |
| [≥2005] | Brandt, Kishore, Santa-Clara & Venkatachalam (2008, working paper), "Earnings announcements are full of surprises" | Drift after the 3-day announcement **return** (EAR, days −1…+1, market-adjusted) is at least as strong and more persistent than SUE drift. It needs no analyst data | **Reaction measure:** a short market-adjusted window around the event; extreme **decile**; holding starts after the window |
| [≥2005] | Novy-Marx (2015, working paper), "Fundamentally, momentum is fundamental momentum" | Earnings momentum, SUE and the 3-day announcement return (CAR3), subsumes much of price momentum | Event reaction is the economically primary signal; price momentum is not needed as a second variable |
| [<2005] | Chan (2003), JFE | Large price moves **with** public news drift; without news they reverse | Event conditioning is the point; it is distinct from our price-only H009 / H010 |
| [≥2005] | Savor (2012), JFE | Information-based price shocks drift; non-information shocks reverse | Same |

## 3. Large caps, decay and costs [≥2005]

| Source | Finding | Relevance |
|---|---|---|
| Sadka (2006), JFE; Chordia, Goyal, Sadka, Sadka & Shivakumar (2009), FAJ, "Liquidity and the post-earnings-announcement drift" | Drift is concentrated in illiquid stocks; after realistic trading costs most of it disappears; liquid large caps show little drift | **Against:** our universe is ≥ $2B, liquid |
| Martineau (2022), Critical Finance Review, "Rest in peace post-earnings announcement drift" | For large, liquid US stocks the drift has **largely disappeared since the mid-2000s**: the announcement-day reaction incorporates the news | **Strongly against** in exactly our period and size range |
| McLean & Pontiff (2016), JF | Anomaly returns fall about 58% after publication | Expect decay |
| Novy-Marx & Velikov (2016), RFS | Higher-turnover anomalies (earnings momentum is mid-turnover) lose more of their premium to costs | Costs matter; keep turnover modest |
| Hirshleifer, Lim & Teoh (2009), JF; DellaVigna & Pollet (2009), JF | More drift when attention is scarce (busy days, Fridays) | Behavioural mechanism; supports persistence in principle, not specifically in large caps |

**Weak points (explicit):**
1. Almost all positive evidence is pre-2005 and size-pooled.
2. The best large-cap evidence after 2005 (Martineau 2022) finds the drift largely gone.
3. Long-only captures only the positive leg.
4. Our 8-K timestamp sometimes lags the press release (in 11.6% of events the 8-K was accepted one or more days after the stated release date; P2-CP12), so part of any very early drift is unavailable to us.

## 4. Abnormal volume

| Label | Source | Finding |
|---|---|---|
| [<2005] | Gervais, Kaniel & Mingelgrin (2001), JF | High trading volume predicts higher returns (a visibility effect), in general rather than earnings-specific |
| [≥2005] | Garfinkel & Sokobin (2006), JAR | Abnormal turnover at the announcement (opinion divergence) is positively related to subsequent drift |
| [≥2005] | Lerman, Livnat & Mendenhall (2008, working paper) | The high-volume premium and SUE drift interact |

**Decision: volume is NOT part of the H017 signal.**
- The volume evidence is real but **secondary**: a distinct visibility / divergence effect, and weaker and less replicated than the reaction effect itself.
- Including it would add a second threshold dimension (exactly the A/B/C freedom to avoid), and would turn the test into a two-signal composite.
- Abnormal event volume is **reported** in the event-level diagnostic, never used to select.

## 5. Practitioner conventions [practice]

- "Earnings gap and go" / post-earnings-drift screens commonly use a gap or 1–2-day move plus volume, and hold days to weeks.
- **Not used to design H017:** no independent evidence for specific practitioner thresholds.

## 6. Design choices that follow [ours]

| Item | Choice | Evidence basis |
|---|---|---|
| Signal | Market-adjusted announcement reaction (price only) | Chan, Jegadeesh & Lakonishok 1996; Brandt et al. 2008; Novy-Marx 2015 |
| Window | Two sessions after the information becomes available: close(E−1) → close(E+1), minus SPY over the same closes | The literature's 3–4-day windows (−2…+1, −1…+1) minus the pre-event days, which the owner excludes (no pre-availability prices). E+1 is included because 8-K timestamps can trail the release and intraday timing is coarse |
| Strength | Top **decile** of reactions (and reaction > 0), breakpoint from the trailing 252 sessions of universe events | Decile sorts in Chan, Jegadeesh & Lakonishok and in Brandt et al.; trailing breakpoints keep it point in time and robust to volatility regimes |
| Horizon | **60 sessions** from entry | Bernard & Thomas: about 60 trading days, up to the next announcement. 60 sessions after an E+2 entry ends about one session before the typical next release (≈ 63 sessions), avoiding a second event-risk exposure the hypothesis does not test |
| Exit | Fixed horizon only | The question is whether the reaction continues, not exit engineering |
| Volume | Excluded (diagnostic only) | §4 |

**Prior expectation (honest):** given §3, the expected large-cap, long-only, post-2005 continuation is **small**, plausibly 0–1% over 60 sessions for the selected events before costs. The design is the cleanest available test of the mechanism with our data; it is not an expectation of success.
