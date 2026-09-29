# X961: C02 signal-equivalence canary (verification)

**Question:** does the tiny difference between the harness's dividend adjustment and QuantConnect's own (at most 0.06% after five years) change any C02 decision?

**Method:**

- The canary keeps two copies of every price history:
  - the harness's own copy, exactly what the strategies read;
  - a reference copy, adjusted with QuantConnect's exact factor at every dividend and split.
- It runs the unchanged C02 signal code on both copies, for every eligible stock, over the whole IS period. The code files are byte-identical copies, and a test enforces that. It counts every decision that differs:
  - entry signals and rankings for H006, H007, H009 and H010, checked every 10th session;
  - exit rules for H006, H007 and H010;
  - the monthly rankings for H008 and H011, checked on every ranking date.
- The reference copy is itself checked against fresh QuantConnect history.

It places no orders, is not a strategy and is not a trial.
