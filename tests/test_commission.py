"""D039: $7 per executed order, buy or sell; slippage separate; metrics net of both."""
import sys
import types

import pandas as pd
import pytest

from qresearch import experiment, integrity, metrics
from qresearch.trades import FILL_COLUMNS, build_trades
from conftest import ROOT
from test_split_scheme import FIXED, research


# ---------------------------------------------------------------- LEAN fee model (stubbed LEAN classes)
def _load_harness(monkeypatch):
    stub = types.ModuleType("AlgorithmImports")

    class FeeModel:
        def __init__(self):
            pass

    class CashAmount:
        def __init__(self, amount, currency):
            self.amount, self.currency = amount, currency

    class OrderFee:
        def __init__(self, value):
            self.value = value

    class _Any:
        def __init__(self, *a, **k):
            pass

    for name, obj in dict(FeeModel=FeeModel, CashAmount=CashAmount, OrderFee=OrderFee, QCAlgorithm=_Any).items():
        setattr(stub, name, obj)
    stub.__all__ = ["FeeModel", "CashAmount", "OrderFee", "QCAlgorithm"]
    params = types.ModuleType("qr_params")
    params.EXPERIMENT = {}
    monkeypatch.setitem(sys.modules, "AlgorithmImports", stub)
    monkeypatch.setitem(sys.modules, "qr_params", params)
    import importlib.util
    spec = importlib.util.spec_from_file_location("qr_harness_under_test", ROOT / "src/qresearch/lean/qr_harness.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _params(order_id):
    return types.SimpleNamespace(order=types.SimpleNamespace(id=order_id))


def test_fee_model_charges_once_per_executed_order(monkeypatch):
    h = _load_harness(monkeypatch)
    fm = h.FixedPerOrderFeeModel(7.0)
    assert fm.get_order_fee(_params(1)).value.amount == 7.0      # buy order 1, first fill
    assert fm.get_order_fee(_params(1)).value.amount == 0.0      # order 1 partially filled again
    assert fm.get_order_fee(_params(2)).value.amount == 7.0      # sell order 2
    assert fm.get_order_fee(_params(3)).value.amount == 7.0      # a separate exit order: charged again
    assert fm.get_order_fee(_params(1)).value.currency == "USD"


def test_harness_uses_the_configured_fee_model():
    src = (ROOT / "src/qresearch/lean/qr_harness.py").read_text()
    assert "security.set_fee_model(self._qr_fee_model)" in src
    assert "FixedPerOrderFeeModel(per_order)" in src
    assert "self._qr_fee_est, band, n_open)" in src                           # plan_orders gets the fee
    assert "fee_est(-q)" in src and "fee_est(q)" in src                        # on sells and on buys


# ---------------------------------------------------------------- configuration rules
def test_new_experiments_must_use_fixed_commission():
    experiment.validate(research())
    for bad in ({"slippage_bps": 10}, dict(FIXED, commission_per_order=1.0), dict(FIXED, commission_model="ib"),
                {"commission_model": "fixed_per_order", "commission_per_order": 7.0}):
        with pytest.raises(experiment.ConfigError):
            experiment.validate(research(costs=bad))


def test_committed_2010_scheme_configs_use_fixed_commission():
    import json
    found = 0
    for p in ROOT.glob("experiments/E*/config.json"):
        c = json.loads(p.read_text())
        if c.get("split_scheme") == "2010":
            found += 1
            assert c["costs"]["commission_model"] == "fixed_per_order" and c["costs"]["commission_per_order"] == 7.0
            assert c["costs"]["slippage_bps"] == 10
    assert found >= 3


# ---------------------------------------------------------------- integrity check on results
def _fills(fees):
    rows = [(i + 1, "A", "A", "2011-01-0%d" % (i + 3), 10 if i % 2 == 0 else -10, 50.0, f, "x|sig=2011-01-01")
            for i, f in enumerate(fees)]
    return pd.DataFrame(rows, columns=FILL_COLUMNS)


def _eq():
    d = pd.bdate_range("2011-01-03", periods=5).strftime("%Y-%m-%d")
    return pd.DataFrame(dict(date=d, equity=100.0, cash=100.0, npos=0, nelig=0))


S = dict(days=5, timing_violations=0, negative_qty=0, invalid=0)


def test_integrity_accepts_exactly_seven_per_order():
    c = {x["check"]: x for x in integrity.check_all(_eq(), _fills([7.0, 7.0]), S, "2011-01-01", "2011-12-31", 7.0)}
    assert c["commission_fixed_per_order"]["ok"]


def test_integrity_accepts_partial_fills_charged_once():
    f = _fills([7.0, 0.0])
    f["order_id"] = [1, 1]                         # one order filled in two pieces
    c = {x["check"]: x for x in integrity.check_all(_eq(), f, S, "2011-01-01", "2011-12-31", 7.0)}
    assert c["commission_fixed_per_order"]["ok"]


@pytest.mark.parametrize("fees", [[1.0, 7.0], [7.0, 14.0], [0.0, 7.0]])
def test_integrity_rejects_other_commissions(fees):
    c = {x["check"]: x for x in integrity.check_all(_eq(), _fills(fees), S, "2011-01-01", "2011-12-31", 7.0)}
    assert not c["commission_fixed_per_order"]["ok"]


# ---------------------------------------------------------------- metrics are net of commissions
def test_trade_pnl_is_net_of_both_commissions():
    f = pd.DataFrame([(1, "A", "A", "2011-01-03", 100, 50.0, 7.0, "e|sig=2011-01-02"),
                      (2, "A", "A", "2011-01-10", -100, 51.0, 7.0, "x|sig=2011-01-07")], columns=FILL_COLUMNS)
    t = build_trades(f).iloc[0]
    assert t.fees == 14.0 and t.pnl == pytest.approx(5100 - 5000 - 14)
    assert metrics.trade_stats(build_trades(f))["expectancy"] == pytest.approx(86 / 5000)


# ---------------------------------------------------------------- D049: forced (delisting) liquidations
def test_forced_liquidation_fee_debit_is_mirrored_locally():
    from qresearch import results
    f = pd.DataFrame([(1, "A", "A", "2011-01-03", 10, 50.0, 7.0, "e|sig=2011-01-02"),
                      (2, "A", "A", "2011-02-01", -10, 40.0, 0.0, "Liquidate from delisting")], columns=FILL_COLUMNS)
    g, n = results.apply_forced_fees(f, ["QRFORCEDFEE|2|7.00", "QRCANARY|{}"])
    assert n == 1 and list(g["fee"]) == [7.0, 7.0]
    c = {x["check"]: x for x in integrity.check_all(_eq(), g, S, "2011-01-01", "2011-12-31", 7.0)}
    assert c["commission_fixed_per_order"]["ok"]
    # without the debit the forced order would show $0 and the commission check must fail
    c2 = {x["check"]: x for x in integrity.check_all(_eq(), f, S, "2011-01-01", "2011-12-31", 7.0)}
    assert not c2["commission_fixed_per_order"]["ok"]


def test_harness_debits_forced_fills_once():
    src = (ROOT / "src/qresearch/lean/qr_harness.py").read_text()
    assert 'self.portfolio.cash_book["USD"].add_amount(-self._qr_forced_fee)' in src
    assert "ev.order_id not in self._qr_forced_debited" in src


# ---------------------------------------------------------------- completeness (E901-02 incident)
def test_empty_download_is_never_clean():
    from qresearch import results
    empty = results.parse_fills([])
    s = dict(S, fills=22037)
    c = {x["check"]: x for x in integrity.check_all(_eq(), empty, s, "2011-01-01", "2011-12-31", 7.0,
                                                    expected_orders=22052, downloaded_orders=0)}
    assert not c["orders_download_complete"]["ok"]
    assert not c["fills_match_harness_count"]["ok"]
    assert not c["commission_fixed_per_order"]["ok"]


def test_order_reader_waits_for_expected_count(monkeypatch):
    from qresearch.qc_client import QCClient

    class Stub(QCClient):
        def __init__(self):
            self.calls = 0

        def _read_orders_once(self, h):
            self.calls += 1
            return [] if self.calls < 3 else [{"id": 1, "status": 3, "events": [{"status": "filled"}]}]

    import qresearch.qc_client as q
    monkeypatch.setattr(q.time, "sleep", lambda s: None)
    c = Stub()
    assert len(c.read_orders(None, expected=1)) == 1 and c.calls == 3
