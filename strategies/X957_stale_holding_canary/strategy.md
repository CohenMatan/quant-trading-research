# X957: stale-holding canary (infrastructure)

Purpose: D059 verification. It holds securities whose QuantConnect data stops without a delisting event, plus two controls: TIF (a normal delisting) and KO (live all period).

With the fix, each dead holding must be taken out at its last real close, and no order may remain open.

It is not a research trial.
