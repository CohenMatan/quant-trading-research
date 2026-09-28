"""D041/D044: $5,000 minimum position, at most 15 positions (fewer for small accounts), 10% cap,
no leverage, $7 fee in cash planning. Tests the harness's pure plan_orders()."""
import pytest

from test_commission import _load_harness

PF = {"max_position_weight": 0.10, "cash_buffer": 0.02, "min_position_usd": 5000, "max_positions": 15}
FEE = lambda q: 7.0


@pytest.fixture
def plan(monkeypatch):
    return _load_harness(monkeypatch).plan_orders


def entries(n, w=0.10, price=50.0):
    return [(f"S{i:02d}", w, price, 0.0, 0.0, False) for i in range(n)]


def test_weight_cap_and_sizing(plan):
    out = plan([("A", 0.25, 100.0, 0, 0, False)], 100_000, 100_000, PF, 0.001, FEE)
    assert out["buys"] == [("A", 100)]                      # capped at 10% of $100K


def test_max_15_positions_at_100k(plan):
    out = plan(entries(20, w=0.06), 100_000, 100_000, PF, 0.0, FEE)
    assert len(out["buys"]) == 15 and out["skipped_cap"] == 5
    assert [k for k, _ in out["buys"]] == [f"S{i:02d}" for i in range(15)]   # priority order kept


def test_existing_positions_count_toward_the_cap(plan):
    out = plan(entries(5, w=0.06), 100_000, 50_000, PF, 0.0, FEE, n_open_positions=13)
    assert len(out["buys"]) == 2 and out["skipped_cap"] == 3


def test_exits_free_slots_in_the_same_batch(plan):
    items = entries(3, w=0.06) + [("OLD", 0.0, 20.0, 300.0, 0.0, False)]      # exit listed last
    out = plan(items, 100_000, 30_000, PF, 0.0, FEE, n_open_positions=15)
    assert out["sells"] == [("OLD", -300)] and len(out["buys"]) == 1 and out["skipped_cap"] == 2


def test_minimum_position_blocks_small_entries(plan):
    out = plan([("A", 0.04, 10.0, 0, 0, False)], 100_000, 100_000, PF, 0.0, FEE)   # $4,000 < $5,000
    assert out["buys"] == [] and out["skipped_min"] == 1


def test_small_account_caps_positions_by_minimum_size(plan):
    # $30K account: floor(30,000 * 0.98 / 5,000) = 5 positions, even though max_positions is 15
    out = plan(entries(10, w=0.20), 30_000, 30_000, dict(PF, max_position_weight=0.20), 0.0, FEE)
    assert len(out["buys"]) == 5 and out["skipped_cap"] == 5


def test_cash_scaling_never_creates_sub_minimum_positions(plan):
    # only ~$12K of cash for three $10K entries: scaled to ~$3.9K each -> all below $5K -> dropped
    out = plan(entries(3), 100_000, 14_000, PF, 0.001, FEE, n_open_positions=9)
    assert out["scaled"] and out["buys"] == [] and out["skipped_min"] == 3


def test_no_leverage_after_fees_and_slippage(plan):
    out = plan(entries(10), 100_000, 100_000, PF, 0.001, FEE)
    spent = sum(q * 50.0 * 1.001 + 7.0 for _, q in out["buys"])
    assert spent <= 100_000 - 0.02 * 100_000 + 1e-6


def test_resizing_existing_position_is_not_a_new_entry(plan):
    # held position trimmed/added is allowed even below the minimum-size rule for new entries
    out = plan([("A", 0.03, 10.0, 200.0, 0.0, False)], 100_000, 90_000, PF, 0.0, FEE, n_open_positions=15)
    assert out["buys"] == [("A", 100)] and out["skipped_cap"] == 0


def test_long_only_and_delisting_guards(plan):
    with pytest.raises(ValueError):
        plan([("A", -0.1, 10.0, 0, 0, False)], 100_000, 100_000, PF, 0.0, FEE)
    out = plan([("A", 0.1, 10.0, 0, 0, True)], 100_000, 100_000, PF, 0.0, FEE)
    assert out["buys"] == []


def test_legacy_configs_without_new_rules_behave_as_before(plan):
    legacy = {"max_position_weight": 0.25, "cash_buffer": 0.02}
    out = plan(entries(8, w=0.24, price=100.0), 100_000, 100_000, legacy, 0.0, FEE)
    assert out["skipped_cap"] == 0 and out["skipped_min"] == 0 and out["scaled"]   # 8 x 24% needs scaling


@pytest.fixture
def harness(monkeypatch):
    return _load_harness(monkeypatch)


def test_slot_weight_at_100k_and_small_accounts(harness):
    sw = harness.slot_weight
    assert sw(15, 100_000, PF) == pytest.approx(0.98 / 15)            # ~$6,533 per position
    assert sw(15, 60_000, PF) == pytest.approx(5050 / 60_000)          # minimum binds -> fewer positions
    assert sw(5, 100_000, PF) == 0.10                                  # capped at 10%
    plan = harness.plan_orders
    w = sw(15, 60_000, PF)
    out = plan(entries(15, w=w), 60_000, 60_000, PF, 0.0, FEE)
    assert len(out["buys"]) == 11 and all(q * 50.0 >= 5000 for _, q in out["buys"])


# ---------------------------------------------------------------- D051 no-borrowing execution model
NB = dict(PF, buy_funding="settled_cash_only", gap_reserve=0.15)


def test_same_batch_sell_proceeds_do_not_fund_buys(plan):
    # E005-02 pattern: 15 held, 3 exits planned + 4 entries, only ~$3.5K cash on hand
    items = [(f"X{i}", 0.0, 30.0, 300.0, 0.0, False) for i in range(3)] + entries(4, w=0.065)
    out = plan(items, 142_000, 3_463, NB, 0.001, FEE, n_open_positions=15)
    assert len(out["sells"]) == 3 and out["buys"] == []          # buys wait for the sells to execute
    old = plan(items, 142_000, 3_463, dict(PF), 0.001, FEE, n_open_positions=15)
    assert len(old["buys"]) == 3                                  # the old rule funded them from proceeds


def test_exiting_position_keeps_its_slot_until_sold(plan):
    items = [("OLD", 0.0, 20.0, 300.0, 0.0, False)] + entries(2, w=0.065)
    out = plan(items, 100_000, 60_000, NB, 0.0, FEE, n_open_positions=15)
    assert out["buys"] == [] and out["skipped_cap"] == 2


def test_gap_reserve_covers_observed_opening_gaps(plan):
    # E004-02 pattern (2016-11-30): cash ~$29.3K, equity ~$83.8K, 7 wanted entries of ~$5.6K
    out = plan(entries(7, w=0.067, price=40.0), 83_768, 29_252, NB, 0.001, FEE, n_open_positions=8)
    cost_at_close = sum(q * 40.0 for _, q in out["buys"])
    fees = 7.0 * len(out["buys"])
    worst_gap = 0.129                                            # largest measured gap that day (EGN)
    assert 29_252 - cost_at_close * (1 + worst_gap) * 1.001 - fees >= 0
    assert 29_252 - cost_at_close * 1.15 * 1.001 - fees >= 0.02 * 83_768 - 1e-6


def test_incident_replay_never_negative(plan):
    """Replay all three diagnosed incidents under D051: cash after the open stays >= 0 even if every
    same-batch sell is cancelled and buys gap up by the largest measured gap."""
    cases = [  # (cash, equity, n_open, exits, entries)
        (1_793, 91_129, 15, 2, 2),       # E004-01 2012-06-29 (MATX sell cancelled)
        (29_252, 83_768, 10, 2, 7),      # E004-02 2016-11-29 (OPEC gap)
        (3_463, 142_555, 15, 4, 4),      # E005-02 2012-10-01 (MDLZ sell cancelled)
    ]
    for cash, pv, n_open, n_exit, n_entry in cases:
        items = [(f"X{i}", 0.0, 50.0, 100.0, 0.0, False) for i in range(n_exit)] + entries(n_entry, w=0.065)
        out = plan(items, pv, cash, NB, 0.001, FEE, n_open_positions=n_open)
        spent = sum(q * 50.0 * 1.129 * 1.001 + 7.0 for _, q in out["buys"]) + 7.0 * len(out["sells"])
        assert cash - spent >= 0, (cash, pv, out)
        assert n_open + len(out["buys"]) <= 15
