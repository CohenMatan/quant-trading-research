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
