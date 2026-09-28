"""D046: results travel through summary statistics (backtests/read), not QuantConnect logs."""
import pytest

from qresearch import integrity, results
from conftest import ROOT


def test_lines_rebuilt_from_statistics():
    st = {"qr_summary": '{"days": 3}', "qr_msgs_n": "2", "qr_msgs_00": "QRSPLIT|A|2014-06-09|0.1428572000\nQRCA|{",
          "qr_msgs_01": '"x": 1}\nQRCANARY|{}', "Net Profit": "1%"}
    lines = results.lines_from_statistics(st)
    splits, summary, other = results.parse_logs(lines)
    assert summary == {"days": 3} and len(splits) == 1
    assert other == ['QRCA|{"x": 1}', "QRCANARY|{}"]            # chunk boundary inside a line is rejoined


def test_missing_chunk_is_an_error():
    with pytest.raises(ValueError):
        results.lines_from_statistics({"qr_summary": "{}", "qr_msgs_n": "2", "qr_msgs_00": "a"})


def test_no_quantconnect_logging_in_harness_or_strategies():
    for p in [ROOT / "src/qresearch/lean/qr_harness.py", *ROOT.glob("strategies/*/main.py")]:
        assert "self.log(" not in p.read_text(), p
    src = (ROOT / "src/qresearch/lean/qr_harness.py").read_text()
    assert 'self.set_summary_statistic("qr_summary"' in src


def test_runner_reads_statistics_and_uses_logs_only_for_legacy():
    src = (ROOT / "src/qresearch/run.py").read_text()
    assert 'client.read_statistics(handle, must_have="qr_summary")' in src
    assert src.count("client.read_logs(") == 1 and "legacy harness" in src
    assert "MIN_LOG_ALLOWANCE" not in src


def test_reproduce_builds_from_original_commit():
    src = (ROOT / "src/qresearch/run.py").read_text()
    assert 'build_commit = orig["provenance"]["git_commit"]' in src
    assert "files = assemble_files(cfg, build_commit, unlocked)" in src


def test_tradeable_dates_cross_check():
    import pandas as pd
    eq = pd.DataFrame(dict(date=["2012-01-03", "2012-01-04"], equity=[1.0, 1.0], cash=[1.0, 1.0], npos=0, nelig=0))
    s = dict(days=2, timing_violations=0, negative_qty=0, invalid=0)
    c = {x["check"]: x for x in integrity.check_all(eq, results.parse_fills([]), s, "2012-01-01", "2012-12-31",
                                                     tradeable_dates=3)}
    assert not c["equity_matches_qc_tradeable_dates"]["ok"]
