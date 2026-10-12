# Owner message 2026-10-12: "Phase 13 — P13-CP4 H028 30-Year Objective Alignment Review"

Decision id: **D225**. A descriptive objective-alignment review of H028 against the owner's clarified 30-year objective:
- participate at least as well as SPY in rising markets;
- lose less than SPY in falling markets;
- compound to materially more wealth than SPY over long horizons.

Inputs are the committed 2015–2021 development artifacts and the committed P13-CP3 synthetic outputs only.
- H028 stays permanently REJECTED. The alignment label is descriptive and does not replace the research status.
- B4 is unchanged. No H029, no Holdout.
- No QuantConnect run, no new data, no retraining.
- The owner's long-term objective is recorded prospectively, as a standard for hypotheses from H029 on. It is not applied retroactively to H028.

Recorded and committed before any P13-CP4 statistic was computed. The owner's message follows verbatim.

---

Phase 13 — P13-CP4

H028 30-Year Objective Alignment Review

Does H028 behave like the long-term strategy the owner actually wants?

Continue from:

> P13-CP3 — H028 Long-Horizon Synthetic Path Robustness



Current formal research status remains:

H028 REJECTED

Do not reopen H028.

Do not change B4.

Do not create H029.

Do not access the Holdout.

This is a descriptive objective-alignment review only.


---

1. Owner's clarified long-term objective

The owner clarified that the intended investment horizon is approximately:

30 years

The desired strategy does not need to beat SPY every calendar year.

A small number of isolated losing years is acceptable.

The desired long-run behavior is approximately:

> In rising markets, participate at least as well as SPY, preferably somewhat better.



> In falling markets, lose less than SPY.



> Over long horizons, compound to materially greater wealth than SPY.



Therefore this checkpoint asks:

> Does H028's observed behavior align with that objective?



This clarification applies prospectively to how future strategies should be evaluated.

It must not retroactively convert H028's original B4 failure into a PASS.


---

2. Research status must not change

Regardless of the result of this review:

FORMAL STATUS:
H028 REJECTED

The review may classify H028 as:

OBJECTIVE-ALIGNED
PARTIALLY OBJECTIVE-ALIGNED
NOT OBJECTIVE-ALIGNED

but these are descriptive labels only.

They do not replace the original research status.


---

3. Data restrictions

Use only already-committed development artifacts from:

2015-01-01 → 2021-12-31

and the already-committed P13-CP3 synthetic outputs.

Do not access:

2022-01-01 → 2026-08-31

No QuantConnect research run.

No new data.

No external data.

No retraining.

No new parameters.


---

4. Preserve the frozen strategy

H028 remains exactly:

λ = 100

11 frozen features:
MOM
LOWVOL
GPA
ACC
BM
AG
REV1M
CBOP
HI52
CFP
EQA

Top 15
max 3 per sector
monthly rebalance
next-open execution
long only
no leverage
$100,000 starting capital

$7 BUY
$7 SELL
0.10% slippage per side

Do not modify any of these.


---

PART A — UP-MARKET PERFORMANCE

5. Monthly up-market analysis

Using all aligned months from 2015–2021, define:

UP MONTH = SPY monthly total return > 0

Report:

number of UP months

mean H028 return
mean SPY return
mean H028 - SPY

median H028 return
median SPY return
median H028 - SPY

H028 up capture

percentage of UP months where H028 > SPY

Also report compounded wealth using only UP months:

H028 compounded UP-month return
SPY compounded UP-month return

This is descriptive only.


---

6. Strength of participation

Classify H028's participation in SPY-positive months using the observed data.

Use the following descriptive interpretation:

Strong upside participation:
up capture >= 1.00

Near-full participation:
0.90 <= up capture < 1.00

Material upside sacrifice:
up capture < 0.90

Do not change these thresholds after viewing results.


---

7. Strong SPY-up months

Repeat separately for months where:

SPY >= +2%

and:

SPY >= +5%

Report:

number of observations
mean H028
mean SPY
mean relative return
up capture
percentage H028 > SPY

This tests whether H028 keeps up when the market is strongly rising.


---

PART B — DOWN-MARKET PERFORMANCE

8. Monthly down-market analysis

Define:

DOWN MONTH = SPY monthly total return < 0

Report:

number of DOWN months

mean H028 return
mean SPY return
mean H028 - SPY

median H028 return
median SPY return
median H028 - SPY

H028 down capture

percentage of DOWN months where H028 > SPY

Also calculate compounded performance using only DOWN months.


---

9. Severe down months

Repeat for:

SPY <= -2%

and:

SPY <= -5%

Report the same statistics.

We specifically want to understand:

> Does H028's protection become stronger when market losses become larger?




---

10. Asymmetry ratio

Create the descriptive metric:

ASYMMETRY_RATIO =
up_capture / down_capture

Handle zero or near-zero denominator carefully.

Interpretation:

> Higher is better because it means retaining more upside relative to the downside absorbed.



Do not use this as a historical gate.

Report H028 and, if already available from committed artifacts:

LV15

for context.


---

PART C — YEAR-LEVEL BEHAVIOR

11. Calendar-year classification

For every year:

2015
2016
2017
2018
2019
2020
2021

report:

SPY annual return
H028 annual return
H028 - SPY
SPY year classification: UP or DOWN

Then calculate:

mean H028-SPY in SPY-positive years
mean H028-SPY in SPY-negative years

Do not overinterpret the small number of years.


---

12. Owner's desired behavior by year

Answer descriptively:

> In SPY-positive years, does H028 generally keep up or outperform?



> In SPY-negative years, does H028 generally protect capital?



A few exceptions are acceptable under the owner's clarified objective.

Do not require every year to satisfy the pattern.


---

PART D — ROLLING INVESTMENT HORIZONS

13. Rolling 12-month results

For every rolling 12-month period calculate:

H028 total return
SPY total return
H028/SPY relative wealth

Report:

% H028 > SPY
median excess return
5th percentile excess return
25th percentile
75th percentile
95th percentile
worst rolling 12m
best rolling 12m


---

14. Rolling 3-year results

For every possible rolling:

36-month

window report:

% H028 > SPY
median H028/SPY wealth ratio
minimum
maximum
median annualized excess return
worst annualized excess return


---

15. Rolling 5-year results

Repeat for:

60-month

windows.

This is especially important for the owner's long horizon.

Report:

% H028 > SPY
median relative wealth ratio
worst relative wealth ratio
best relative wealth ratio
annualized excess-return distribution


---

16. Rolling 10-year limitation

The real development period is only seven years.

Therefore do not pretend that real 10-year rolling windows exist.

State:

NOT AVAILABLE FROM REAL DEVELOPMENT HISTORY

Use the already-created P13-CP3 synthetic paths for 10-, 20- and 30-year descriptive context instead.


---

PART E — COMPOUNDING MECHANISM

17. Explain where H028's wealth advantage comes from

Decompose H028's relative compounding into:

contribution from SPY-positive months
contribution from SPY-negative months

Use cumulative log-relative return:

log((1 + H028_return) / (1 + SPY_return))

for each month.

Sum separately for:

SPY-up months
SPY-down months

Then report:

total relative log wealth contribution from UP months
total relative log wealth contribution from DOWN months

and their percentage contribution to total H028-vs-SPY relative wealth.

This is a key output.


---

18. Critical interpretation

We want to distinguish between:

Pattern A

H028 keeps approximately all SPY upside
AND
loses substantially less in downturns

This is strongly aligned with the owner's objective.

Pattern B

H028 sacrifices meaningful upside
but compensates through crash protection

This is only partially aligned.

Pattern C

H028's entire edge comes from one or two exceptional episodes

This is weak alignment.

Determine which description is best supported by the evidence.


---

PART F — REMOVE 2018 AND 2020 FROM THE MECHANISM ANALYSIS

19. Actual-history exclusion diagnostic

Without retraining or creating an alternative strategy, calculate descriptive monthly performance over the existing period excluding all months belonging to:

2018
2020

Then report:

H028 CAGR-like annualized return over remaining months
SPY annualized return
H028-SPY annualized difference

up capture
down capture
monthly win rate vs SPY

This is not a valid independent test.

It is only meant to answer:

> Outside the two already-identified favorable years, does H028 still exhibit the desired upside/downside asymmetry?




---

20. Single-year exclusions

Repeat the core:

up capture
down capture
relative return

excluding only:

2018

and then only:

2020

Do not search other arbitrary exclusions.


---

PART G — SYNTHETIC 30-YEAR OBJECTIVE ALIGNMENT

21. Reuse P13-CP3 outputs

Do not rerun the 30-year bootstrap unless a required statistic was not saved and can be deterministically computed from existing committed path outputs.

Use the already-committed P13-CP3 results.

Summarize:

P(H028 > SPY after 5y)
P(H028 > SPY after 10y)
P(H028 > SPY after 20y)
P(H028 > SPY after 30y)

median 30y wealth ratio
5th percentile
95th percentile

probability of >=5 consecutive losing years
probability of >=10 consecutive losing years

median longest recovery
fraction never recovered

median max relative drawdown
worst relative drawdown


---

22. Owner patience analysis

Translate these numbers into the practical investor experience.

Answer:

> If the owner followed H028 for 30 years, how long could the strategy reasonably look broken relative to SPY even in synthetic paths where it ultimately wins?



Use P13-CP3 numbers only.

Do not estimate psychological behavior or investor probability.


---

PART H — REGIME DEPENDENCE

23. Use P13-CP3 exclusion evidence

Explicitly present:

full donor set:
P(H028 > SPY after 30y)

leave 2018 out:
P(H028 > SPY after 30y)

leave 2020 out:
P(H028 > SPY after 30y)

leave 2018 + 2020 out:
P(H028 > SPY after 30y)

Also show:

median excess CAGR

where already available.


---

24. Interpret regime dependence

Answer:

> Is H028 robustly asymmetric across many environments, or does its long-run success require the recurrence of environments similar to 2018 and/or 2020?



This should be one of the most important conclusions.

Do not attempt to build a regime detector.


---

PART I — COMPARISON WITH OWNER OBJECTIVE

25. Define the objective-alignment dimensions

Score descriptively, not statistically, on:

A. Upside participation
B. Downside protection
C. Long-run compounding
D. Temporal consistency
E. Regime dependence
F. Relative drawdown / patience burden

For each dimension classify:

STRONG
ACCEPTABLE
WEAK

Use pre-existing quantitative evidence.

Do not combine into a numeric composite score.


---

26. Required interpretation

Use these principles:

Strong long-term candidate behavior

Would ideally show:

up capture near or above 1
down capture clearly below 1
positive long-run relative compounding
acceptable rolling-period behavior
edge not dominated by one or two regimes

Weak long-term behavior

Would show:

large upside sacrifice
edge mostly dependent on crashes
very long relative drawdowns
or severe regime dependence

Do not require perfection.

The owner explicitly accepts isolated exceptions.


---

PART J — IMPLICATION FOR H029

27. Do not design H029 yet

Do not create H029.

However, based on the objective-alignment review, identify only the missing capability that a future independent signal should ideally contribute.

Examples of permissible conclusions:

H028 already provides adequate downside protection,
but needs stronger upside participation.

or:

H028's upside is acceptable,
but the edge is excessively regime dependent.

or:

H028 needs improvement in both dimensions.

Do not propose feature weights or optimized rules yet.


---

PART K — OWNER-FACING QUESTIONS

At the top of the checkpoint answer these clearly and simply.

Q1

When SPY goes up, does H028 generally keep up?

Q2

When SPY falls, does H028 generally lose less?

Q3

What are H028's up-capture and down-capture?

Q4

Is H028's total advantage primarily produced in rising markets or falling markets?

Q5

If 2018 and 2020 are removed, does the desirable up/down behavior remain?

Q6

Across rolling 1-, 3- and 5-year periods, how consistently does H028 beat SPY?

Q7

How long can H028 remain behind SPY before recovering?

Q8

Over synthetic 30-year paths, how frequently does it ultimately beat SPY?

Q9

How dependent is that result on environments similar to 2018 and 2020?

Q10

Given the owner's actual 30-year objective, is H028:

OBJECTIVE-ALIGNED
PARTIALLY OBJECTIVE-ALIGNED
NOT OBJECTIVE-ALIGNED

Explain why.


---

PART L — FORMAL STATUS

28. Keep the distinction explicit

The checkpoint must contain both:

ORIGINAL RESEARCH STATUS:
H028 REJECTED

and separately:

30-YEAR OBJECTIVE ALIGNMENT:
<OBJECTIVE-ALIGNED / PARTIALLY OBJECTIVE-ALIGNED / NOT OBJECTIVE-ALIGNED>

These answer different questions.

Do not merge them.


---

PART M — FUTURE RESEARCH STANDARD

29. Record the owner's prospective objective

Record that for future hypotheses beginning with H029, the owner's long-term goal is:

> Maximize long-term wealth relative to SPY over an approximately 30-year horizon while seeking strong upside participation and materially better downside protection.



Future strategies do not need:

SPY outperformance every calendar year

or:

zero multi-year relative drawdowns

But future pre-registered gates should evaluate:

up-market participation
down-market protection
rolling multi-year performance
terminal wealth
risk
cost robustness
regime concentration
long-horizon synthetic robustness

This is a prospective methodological clarification.

Do not apply new gates retroactively to H028.


---

30. Required checkpoint

Create:

> P13-CP4 — H028 30-Year Objective Alignment Review



Include at minimum:

1. H028 original rejected status
2. Owner's clarified 30-year objective
3. Data/artifact sources
4. Holdout confirmation
5. Number of up months
6. Number of down months
7. Up capture
8. Down capture
9. Up-month relative return
10. Down-month relative return
11. Strong-up-month analysis
12. Severe-down-month analysis
13. Asymmetry ratio
14. Calendar-year classification
15. Up-year results
16. Down-year results
17. Rolling 12m results
18. Rolling 3y results
19. Rolling 5y results
20. 10y real-data limitation
21. Relative-log contribution from up months
22. Relative-log contribution from down months
23. Ex-2018 results
24. Ex-2020 results
25. Ex-2018-and-2020 results
26. P13-CP3 5y synthetic result
27. 10y result
28. 20y result
29. 30y result
30. Losing-streak statistics
31. Recovery statistics
32. Relative-drawdown statistics
33. 2018 dependence
34. 2020 dependence
35. combined 2018/2020 dependence
36. Upside-participation classification
37. Downside-protection classification
38. Long-run-compounding classification
39. Temporal-consistency classification
40. Regime-dependence classification
41. Patience-burden classification
42. Overall objective-alignment conclusion
43. Missing capability for future H029
44. Prospective future-research standard
45. Confirmation no strategy change
46. Confirmation H028 remains rejected
47. Confirmation Holdout untouched
48. Exact next owner decision


---

31. Final conclusion format

End with exactly two separate conclusions.

First:

ORIGINAL RESEARCH STATUS:
H028 REJECTED

Then:

30-YEAR OBJECTIVE ALIGNMENT:
<OBJECTIVE-ALIGNED / PARTIALLY OBJECTIVE-ALIGNED / NOT OBJECTIVE-ALIGNED>

Follow with a short explanation focused on:

upside participation
downside protection
long-term compounding
regime dependence


---

32. STOP

After committing P13-CP4:

STOP

Do not start H029.

Do not alter H028.

Do not access the Holdout.

Return the results to the owner.
