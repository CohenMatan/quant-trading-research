# X952 — Corporate actions and delistings check (infrastructure)

The check buys small positions (4% each) in names with known corporate events, then verifies that the engine handles each event correctly.

| Event | Expected behaviour |
|---|---|
| AAPL 2:1 split (2005-02-28) and 7:1 split (2014-06-09) | Share quantity multiplies by 2 and 7; portfolio value is continuous across the split |
| KO and XOM quarterly dividends | Cash rises by quantity × dividend per share on the dividend event |
| Enron (bankruptcy, NYSE delisting 2002-01), WorldCom (2002), Bear Stearns (acquired by JPM, 2008-05-30), Lehman (bankruptcy, 2008-09) | The engine force-liquidates the position at the delisting; the fill price and date are recorded |

This is not a strategy and carries no research meaning.
