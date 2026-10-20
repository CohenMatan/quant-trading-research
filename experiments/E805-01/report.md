# E805-01 — X805 v1.0 (infrastructure)

SCA-1 SEC classification audit (owner D267; research/rr/sec_classification/SCA_protocol.md): X805 on QuantConnect's default build, 2009-11-02 .. 2021-12-31, month-end points 2010-01 .. 2021-11. Public SEC registrants (plain JSON, Object Store) matched in-cloud by dated ticker evidence / share fingerprint to the vendor universe: matched / confirmed missing / possible missing / unresolved, gaps, survivorship bounds, frozen verdict. Aggregates only, 0 orders, no returns, no identifiers. Infrastructure.

- **Status:** failed
- **Split:** AUDIT (2009-11-02 → 2021-12-31)
- **Commit:** `c350dfc23ad6117919a2e21ac5ebd69984d05970` · **QC backtest:** `506cd29bc07f6bcddcb226524f627f31` · **LEAN:** v2.5.0.0.18194 · **run:** 2026-10-20T10:10:19Z · **runtime:** 26s
- **Parameters:** `{'sca_protocol_sha256': 'a4cec4f5111adad28fe653f708fc1fd6264700f26538065ac16d5b8692e21b36', 'sca_code_sha256': {'main.py': 'eb88c69e9299c80b416bab339ee2786ac53d5cd3919c67fad072b98367d722ad', 'qr_sca.py': '38045153a769367b41f42c9fb858c9064deaf53fc11558ea5a07fcc14672dba5'}, 'sec_object_key': 'rr/sca_sec_v1.json', 'sec_reference_sha256': '67bc9260f3c5bed6ac723a0ed4b177dee9f9be5814f482200438687b0984a747'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate (no order is placed in this run)'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Error

```
2009-11-02 00:00:00 During the algorithm initialization, the following exception has occurred: X805: the SEC reference object is not in the Object Store
  at qr_initialize
    raise Exception(&quot;X805: the SEC reference object is not in the Object Store&quot;)
 in main.py: line 42
  at initialize
    self.qr_initialize()
 in qr_harness.py: line 368
 X805: the SEC reference object is not in the Object Store
X805: the SEC reference object is not in the Object Store
  at qr_initialize
    raise Exception("X805: the SEC reference object is not in the Object Store")
 in main.py: line 42
  at initialize
    self.qr_initialize()
 in qr_harness.py: line 368
 X805: the SEC reference object is not in the Object Store
```
