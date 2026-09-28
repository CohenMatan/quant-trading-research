from qresearch import proxy_eval


def test_scores_pool_months():
    import pandas as pd
    df = pd.DataFrame([dict(year="2010", variant="E1-C20", months=2, nP=20, nR=20, TP=16, FP=4, FN=4, f1_min=0.7, f1_max=0.9),
                       dict(year="2011", variant="E1-C20", months=2, nP=20, nR=24, TP=18, FP=2, FN=6, f1_min=0.8, f1_max=0.9)])
    a = proxy_eval.agreement(df).loc["E1-C20"]
    assert a.TP == 34 and a.FP == 6 and a.FN == 10
    assert abs(a.precision - 34 / 40) < 1e-12 and abs(a.recall - 34 / 44) < 1e-12
    assert abs(a.F1 - 68 / 84) < 1e-12 and a.f1_min == 0.7


def test_parse_lines(tmp_path, monkeypatch):
    d = tmp_path / "E953-99"
    d.mkdir()
    (d / "messages.txt").write_text(
        "QRPX_Y|2010|E1-C20|1|10|10|8|2|2|0.8|0.8\n"
        'QRPX_F|2010-01-04|{"R":[0.01,5,5],"C20_P":[0.02,6,6]}\n'
        "QRPX_SAMPLE|2010-06-01|n=3|AA:R735:10:0.80:0.70;SPY:R735:900:0.99:1.00\n"
        'QRPX_CHK|{"months": 1, "max_diff": 0, "sum_diff": 0}\n')
    monkeypatch.setattr(proxy_eval.config, "EXPERIMENTS_DIR", tmp_path)
    p = proxy_eval.parse("E953-99")
    assert p["y"].iloc[0].TP == 8 and p["f"].iloc[0]["C20_P"] == 0.02
    assert list(p["samples"].ticker) == ["AA", "SPY"] and p["chk"]["max_diff"] == 0
