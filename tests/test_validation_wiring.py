def test_evaluate_runs_on_committed_is_results(root):
    """The evaluation pipeline works end to end, exercised on IS data only (E005-12 against itself)."""
    from qresearch import validation
    out = validation.evaluate("E005-12", "E005-12", "E901-05", "E900-06", 0.71)
    g = {c["gate"]: c for c in out["gate"]}
    assert set(g) == {"VAL Sharpe", "VAL Sharpe vs IS", "VAL Sharpe vs EW", "VAL max drawdown", "VAL closed trades",
                      "2020 Feb-Mar drawdown", "Deflated Sharpe (IS+VAL)", "PBO (CSCV on IS, from CP3)"}
    assert g["PBO (CSCV on IS, from CP3)"]["ok"] is False
    assert 0 < out["s005"]["invested_mean"] <= 1
    assert out["period"][1] <= "2017-12-31"          # IS only: nothing after IS is read here
