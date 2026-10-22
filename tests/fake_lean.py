"""A small fake of the QuantConnect / LEAN objects the shared harness (qr_harness) and the H032 hosts use, for OFFLINE
end-to-end tests: the REAL harness, the REAL pinned X807 host and the S033 trading host run unchanged on top of it.

Broker conventions (the ones the LEAN-verified Phase 3 shadow engine assumes, E984):
  * market-on-open orders fill at the next session's open in which the symbol has a real bar, at open x (1 +/- slip)
    (ConstantSlippageModel), with the security's fee model (the harness FixedPerOrderFeeModel: $7 per executed order);
  * splits (midnight slice of the split day): quantity / factor, whole shares, the fraction paid in cash at the
    reference price x factor; dividends: quantity x amount in cash;
  * delisting: liquidated at the last price with a ZERO fee (the harness debits its forced fee), open orders cancelled;
  * the universe callback is called at midnight with the PREVIOUS session's fundamental objects; returned symbols are
    subscribed and receive daily bars from that session on."""
import sys
import types
from datetime import datetime, timedelta

from conftest import ROOT


class Sym:
    def __init__(self, sid, ticker):
        self.id = sid
        self.value = ticker

    def __repr__(self):
        return f"Sym({self.value})"


def _ns(**kw):
    return types.SimpleNamespace(**kw)


def algorithm_imports():
    m = types.ModuleType("AlgorithmImports")

    class FeeModel:
        def __init__(self):
            pass

    class CashAmount:
        def __init__(self, amount, currency):
            self.amount, self.currency = amount, currency

    class OrderFee:
        def __init__(self, value):
            self.value = value

    class ConstantSlippageModel:
        def __init__(self, slip):
            self.slip = float(slip)

    class Chart:
        def __init__(self, name):
            self.name = name

        def add_series(self, s):
            pass

    class Series:
        def __init__(self, *a, **k):
            pass

    class InteractiveBrokersFeeModel(FeeModel):
        pass

    names = dict(FeeModel=FeeModel, CashAmount=CashAmount, OrderFee=OrderFee, QCAlgorithm=FakeQC,
                 ConstantSlippageModel=ConstantSlippageModel, Chart=Chart, Series=Series,
                 InteractiveBrokersFeeModel=InteractiveBrokersFeeModel,
                 SeriesType=_ns(LINE=0), BrokerageName=_ns(INTERACTIVE_BROKERS_BROKERAGE=1),
                 AccountType=_ns(MARGIN=1), BuyingPowerModel=_ns(NULL=None),
                 DataNormalizationMode=_ns(RAW="RAW", SCALED_RAW="SCALED_RAW"), Resolution=_ns(DAILY="DAILY"),
                 SplitType=_ns(SPLIT_OCCURRED="SPLIT", WARNING="WARN"),
                 DelistingType=_ns(WARNING="WARNING", DELISTED="DELISTED"),
                 OrderStatus=_ns(FILLED="FILLED", PARTIALLY_FILLED="PART", CANCELED="CANCELED", INVALID="INVALID"))
    for k, v in names.items():
        setattr(m, k, v)
    m.__all__ = list(names)
    return m


class Holding:
    def __init__(self, sec):
        self.sec = sec
        self.quantity = 0.0

    @property
    def invested(self):
        return abs(self.quantity) > 1e-12

    @property
    def holdings_value(self):
        return self.quantity * self.sec.price

    def set_holdings(self, price, qty):
        self.quantity = float(qty)


class Portfolio:
    def __init__(self, algo):
        self.algo = algo
        self.h = {}
        self.cash = 0.0
        self.cash_book = {"USD": _ns(add_amount=self._add)}

    def _add(self, x):
        self.cash += float(x)

    def __getitem__(self, sym):
        if sym not in self.h:
            self.h[sym] = Holding(self.algo.securities.get_or_add(sym))
        return self.h[sym]

    def __iter__(self):
        return iter([_ns(key=s, value=h) for s, h in list(self.h.items())])

    @property
    def total_holdings_value(self):
        return sum(h.holdings_value for h in self.h.values())

    @property
    def total_portfolio_value(self):
        return self.cash + self.total_holdings_value


class Security:
    def __init__(self, sym, algo):
        self.symbol = sym
        self.price = 0.0
        self.open = 0.0
        self.fee_model = None
        self.slip = 0.0
        self.exchange = _ns(hours=algo.hours)

    def set_fee_model(self, m):
        self.fee_model = m

    def set_slippage_model(self, m):
        self.slip = m.slip

    def set_buying_power_model(self, m):
        pass

    def set_data_normalization_mode(self, m):
        pass


class Securities(dict):
    def __init__(self, algo):
        super().__init__()
        self.algo = algo

    def contains_key(self, s):
        return s in self

    def get_or_add(self, s):
        if s not in self:
            sec = self[s] = Security(s, self.algo)
            if self.algo._init_sec is not None:
                self.algo._init_sec(sec)
        return self[s]


class Ticket:
    def __init__(self, oid, sym, qty, tag):
        self.order_id, self.symbol, self.quantity, self.tag = oid, sym, float(qty), tag


class Transactions:
    def __init__(self):
        self.open = {}
        self.orders = {}

    def get_open_order_tickets(self, sym=None):
        return [t for t in self.open.values() if sym is None or t.symbol == sym]

    def cancel_open_orders(self, sym):
        for oid in [o for o, t in self.open.items() if t.symbol == sym]:
            del self.open[oid]

    def get_order_by_id(self, oid):
        return self.orders[oid]


class Hours:
    def __init__(self, cal):
        self.cal = cal

    def get_next_market_open(self, t, extended):
        d = t.date()
        nxt = next((c for c in self.cal if c > d or (c == d and t.hour < 9)), d + timedelta(days=3))
        return datetime(nxt.year, nxt.month, nxt.day, 9, 30)


class Bars(dict):
    def contains_key(self, k):
        return k in self

    @property
    def count(self):
        return len(self)


class FakeQC:
    """The QCAlgorithm surface used by the harness and the H032 hosts."""

    def __init__(self):
        pass

    def fake_setup(self, cal, store):
        self.hours = Hours(cal)
        self.securities = Securities(self)
        self._init_sec = None
        self.portfolio = Portfolio(self)
        self.transactions = Transactions()
        self.object_store = _ns(contains_key=lambda k: k in store, read=lambda k: store[k])
        self.universe_settings = _ns()
        self.stats = {}
        self._oid = 0
        self.time = datetime(2000, 1, 1)

    def set_start_date(self, y, m, d):
        self.lean_start = datetime(y, m, d)

    def set_end_date(self, y, m, d):
        self.lean_end = datetime(y, m, d)

    def set_cash(self, c):
        self.portfolio.cash = float(c)

    def set_brokerage_model(self, *a):
        pass

    def set_security_initializer(self, f):
        self._init_sec = f

    def add_chart(self, c):
        pass

    def plot(self, *a):
        pass

    def set_benchmark(self, s):
        pass

    def add_equity(self, ticker, *a, **k):
        sym = Sym(f"{ticker} FAKE", ticker)
        self.securities.get_or_add(sym)
        return _ns(symbol=sym)

    def add_universe(self, fn):
        self.universe_fn = fn

    def set_summary_statistic(self, k, v):
        self.stats[k] = v

    def market_on_open_order(self, sym, qty, tag=""):
        self._oid += 1
        t = Ticket(self._oid, sym, qty, tag)
        self.transactions.open[t.order_id] = t
        self.transactions.orders[t.order_id] = t
        return t


def event(status, sym, oid, qty=0.0, px=0.0, fee=0.0, quantity=None):
    return _ns(status=status, symbol=sym, order_id=oid, fill_quantity=float(qty), fill_price=float(px),
               quantity=float(qty if quantity is None else quantity), message="",
               order_fee=_ns(value=_ns(amount=float(fee))))


def load_stack(monkeypatch, experiment):
    """Install the fake AlgorithmImports, qr_params and the REAL harness, X807 (as qr_x807) and S033 modules."""
    import importlib.util
    ai = algorithm_imports()
    monkeypatch.setitem(sys.modules, "AlgorithmImports", ai)
    params = types.ModuleType("qr_params")
    params.EXPERIMENT = experiment
    monkeypatch.setitem(sys.modules, "qr_params", params)

    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, name, mod)
        spec.loader.exec_module(mod)
        return mod
    h = load("qr_harness", ROOT / "src/qresearch/lean/qr_harness.py")
    x = load("qr_x807", ROOT / "strategies/X807_os1_canary/main.py")
    s = load("s033_main", ROOT / "strategies/S033_h032_os1/main.py")
    return ai, h, x, s


class Market:
    """Drives one algorithm through sessions. prices[day][sym] = (open, close); fundamentals(day) -> objects reflecting
    `day`; splits / dividends / delist: {day: [(sym, ...)]} applied in the midnight slice of `day`."""

    def __init__(self, algo, ai, cal, prices, fundamentals, splits=None, dividends=None, delist=None, warn=None):
        self.a, self.ai, self.cal, self.prices, self.fund = algo, ai, cal, prices, fundamentals
        self.splits, self.divs, self.delist, self.warn = splits or {}, dividends or {}, delist or {}, warn or {}
        self.subs = set()

    def _slice(self, bars=None, splits=None, divs=None, dl=None):
        return _ns(bars=Bars(bars or {}), splits=Bars(splits or {}), dividends=Bars(divs or {}),
                   delistings=Bars(dl or {}))

    def run(self):
        a, ai = self.a, self.ai
        prev = None
        spy = a.spy
        for d in self.cal:
            a.time = datetime(d.year, d.month, d.day, 0, 0)
            if prev is not None:
                chosen = a.universe_fn(self.fund(prev))
                self.subs = set(chosen)
                for s in self.subs:
                    a.securities.get_or_add(s)
            # midnight corporate-action slice (subscribed or held symbols only)
            live = self.subs | {k for k, h in a.portfolio.h.items() if h.invested}
            sp, dv, dl = {}, {}, {}
            for sym, f, ref in self.splits.get(d, []):
                if sym in live:
                    sp[sym] = _ns(type=ai.SplitType.SPLIT_OCCURRED, split_factor=f, reference_price=ref)
                    h = a.portfolio[sym]
                    if h.invested:
                        q = h.quantity / f
                        whole = int(q + 1e-9)
                        a.portfolio.cash += (q - whole) * ref * f
                        h.quantity = float(whole)
                    a.securities[sym].price *= f
            for sym, amt in self.divs.get(d, []):
                if sym in live:
                    dv[sym] = _ns(distribution=amt, reference_price=a.securities[sym].price)
                    h = a.portfolio[sym]
                    if h.invested:
                        a.portfolio.cash += h.quantity * amt
            for sym in self.warn.get(d, []):
                if sym in live:
                    dl[sym] = _ns(type=ai.DelistingType.WARNING)
            for sym in self.delist.get(d, []):
                if sym in live:
                    dl[sym] = _ns(type=ai.DelistingType.DELISTED)
            if sp or dv or dl:
                a.on_data(self._slice(splits=sp, divs=dv, dl=dl))
            for sym in self.delist.get(d, []):
                for t in a.transactions.get_open_order_tickets(sym):
                    a.transactions.open.pop(t.order_id, None)
                    a.on_order_event(event(ai.OrderStatus.CANCELED, sym, t.order_id, quantity=t.quantity))
                h = a.portfolio.h.get(sym)
                if h is not None and h.invested:
                    a._oid += 1
                    q = h.quantity
                    a.portfolio.cash += q * a.securities[sym].price
                    h.quantity = 0.0
                    a.on_order_event(event(ai.OrderStatus.FILLED, sym, a._oid, -q, a.securities[sym].price, 0.0))
            # the open: market-on-open fills for symbols with a bar today
            bars_today = self.prices.get(d, {})
            for sym, (o, c) in bars_today.items():
                if sym in a.securities:
                    a.securities[sym].open = o
            a.time = datetime(d.year, d.month, d.day, 9, 30)
            for t in sorted(a.transactions.get_open_order_tickets(), key=lambda x: x.order_id):
                if t.symbol not in bars_today:
                    continue
                sec = a.securities[t.symbol]
                o = bars_today[t.symbol][0]
                px = o * (1 + sec.slip) if t.quantity > 0 else o * (1 - sec.slip)
                fee = sec.fee_model.get_order_fee(_ns(order=_ns(id=t.order_id))).value.amount
                del a.transactions.open[t.order_id]
                h = a.portfolio[t.symbol]
                h.quantity += t.quantity
                a.portfolio.cash -= t.quantity * px + fee
                a.on_order_event(event(ai.OrderStatus.FILLED, t.symbol, t.order_id, t.quantity, px, fee))
            # the close: daily bars of subscribed / held symbols and SPY
            a.time = datetime(d.year, d.month, d.day, 16, 0)
            live = self.subs | {k for k, h in a.portfolio.h.items() if h.invested} | {spy}
            bars = {}
            for sym, (o, c) in bars_today.items():
                if sym in live:
                    bars[sym] = _ns(open=o, close=c, is_fill_forward=False, volume=1e6, high=c, low=c)
                    a.securities.get_or_add(sym).price = c
            a.on_data(self._slice(bars=bars))
            prev = d
        a.on_end_of_algorithm()
