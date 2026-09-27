# X953 — Size-proxy evaluation (infrastructure)

Measures how well price/volume-only universe rules reproduce the MarketCap ≥ $2B reference universe. It places no orders.

The plan, variants and decision thresholds are pre-registered in `docs/data/size_proxy_plan.md`. The results are in `docs/data/size_proxy_evaluation.md`.

Runs:

| Run | Window | Dataset | Use |
|---|---|---|---|
| E953-01 | 2010–2014 | new, LEAN 18131 | Primary comparison; forward returns are measured within IS only |
| E953-02 | 2015–2021 | new, LEAN 18131 | Membership stability only; no returns |
| E953-03 | 1999–2009 | old, LEAN 18130, survivors only | Recall on survivors; capture of later-failed companies; survivorship return gap |
