# S013: lottery-stock avoidance (H013)

**Hypothesis:** `research/hypotheses/H013.md`. Methodology: `research/cycles/C03_statistical_spec.md` (D082). Implementation choices: D083.

**What it is:** the no-skill null X962 (15 slots, hold 60 sessions, seeded random refill order over all eligible stocks), except that it skips stocks in the top fraction q of MAX (the largest daily return over 21 sessions) or MAX5 (the mean of the 5 largest).

**Pairing:** `nullorder.py` is a byte copy of X962's `signals.py`. So S013 walks the null's own order for the same seed and session, and differs only where the null would have bought an excluded name.

Seeds 1, 2 and 3 are paired with E962-22, E962-23 and E962-24.
