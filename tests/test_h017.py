"""H017 decision logic (qr_h017) and S017 mechanics, offline:
  * the reaction uses only the closes of E-1 and E+1 (and SPY's); the breakpoint only events with an EARLIER decision
    session; adding future events never changes past signals (truncation test);
  * deterministic capacity ranking (AR, ties by id) and random keys; held/pending stocks ignored; at most min(free, k_t)
    entries; nothing queued;
  * a day-by-day simulation that mirrors S017's order flow (decision at a close, market-on-open at the next session,
    exit order at sessions held = 59): every entry at E+2, every exit exactly 60 sessions after entry, <= 10 holdings,
    no top-up, no early replacement; candidate and random books differ only in the ranking;
  * the canary is a byte copy of S017; the runner uploads the H017 files only for strategies that import them;
    configs: H017 portfolio rules, approval gating."""
import hashlib
import json
import random
from collections import deque

import numpy as np
import pytest

from conftest import ROOT, load_module

H = load_module(ROOT / "src/qresearch/lean/qr_h017.py", "qr_h017_under_test")


# ---------------------------------------------------------------- reaction and breakpoints
def test_reaction_uses_only_e_minus_1_and_e_plus_1_closes_and_spy():
    assert H.reaction(100.0, 110.0, 200.0, 202.0) == pytest.approx(0.10 - 0.01)
    assert H.reaction(100.0, 90.0, 200.0, 180.0) == pytest.approx(0.0)
    for bad in ((None, 1.0, 1.0, 1.0), (0.0, 1.0, 1.0, 1.0), (1.0, -1.0, 1.0, 1.0), (1.0, 1.0, float("nan"), 1.0),
                (1.0, 1.0, 1.0, float("inf"))):
        assert H.reaction(*bad) is None


def test_quantile_matches_numpy_linear():
    rng = np.random.default_rng(1)
    for n in (1, 2, 5, 400, 1001):
        x = rng.normal(size=n)
        for q in (0.0, 0.1, 0.5, 0.8, 0.9, 1.0):
            assert H.quantile(list(x), q) == pytest.approx(float(np.quantile(x, q)))


def test_breakpoint_uses_only_strictly_earlier_sessions_within_252():
    bp = H.Breakpoints()
    for i in range(500):
        bp.add(i // 2, float(i))                      # two events per session, sessions 0..249
    thr, n, newest = bp.threshold(250)
    assert n == 500 and newest == 249
    assert thr == pytest.approx(np.quantile(np.arange(500.0), 0.9))
    bp.add(250, 1e9)                                  # today's events never enter today's breakpoint
    assert bp.threshold(250)[0] == thr
    thr2, n2, newest2 = bp.threshold(251)
    assert n2 == 501 and newest2 == 250
    # the window is the previous 252 sessions: index >= t - 252
    thr3, n3, _ = bp.threshold(250 + 252)             # sessions 250..501 -> only the single event of session 250
    assert n3 == 1 and thr3 is None                   # fewer than 400 events -> no signal
    with pytest.raises(ValueError):
        bp.add(10, 0.0)                               # history is append-only in session order


def test_minimum_400_events_else_no_signal():
    bp = H.Breakpoints()
    for i in range(399):
        bp.add(0, 0.01 * i)
    thr, n, _ = bp.threshold(1)
    assert thr is None and n == 399
    assert not H.qualifies(10.0, thr)
    bp.add(0, 5.0)
    assert bp.threshold(1)[0] is not None


def test_signal_requires_threshold_and_positive_reaction():
    assert H.qualifies(0.05, 0.04) and H.qualifies(0.04, 0.04)
    assert not H.qualifies(0.03, 0.04)
    assert not H.qualifies(-0.001, -0.01)              # a negative breakpoint never admits a negative reaction
    assert not H.qualifies(0.0, -0.01)
    assert not H.qualifies(None, 0.0)


def _signals_by_day(events, n_days):
    """events: list of (decision day, key, AR) -> {day: [qualifying keys]} using the frozen rules."""
    bp = H.Breakpoints()
    out = {}
    for t in range(n_days):
        today = [(k, a) for d, k, a in events if d == t]
        thr, _, _ = bp.threshold(t)
        out[t] = H.rank_signals([(k, a) for k, a in today if H.qualifies(a, thr)])
        for _, a in today:
            bp.add(t, a)
    return out


def test_truncation_future_events_never_change_past_signals():
    rng = random.Random(7)
    events = [(d, f"S{rng.randrange(300)}#{d}#{j}", rng.gauss(0.0, 0.05)) for d in range(400) for j in range(rng.randrange(0, 12))]
    full = _signals_by_day(events, 400)
    for cut in (150, 260, 333):
        trunc = _signals_by_day([e for e in events if e[0] < cut], cut)
        assert all(trunc[t] == full[t] for t in range(cut))
    # perturbing every FUTURE reaction leaves all past signals unchanged
    shocked = [(d, k, a if d < 300 else a * -7.0 + 1.0) for d, k, a in events]
    alt = _signals_by_day(shocked, 400)
    assert all(alt[t] == full[t] for t in range(300))


# ---------------------------------------------------------------- capacity and controls
def test_capacity_ranking_is_deterministic_by_ar_then_id():
    assert H.rank_signals([("B", 0.2), ("A", 0.2), ("C", 0.5), ("D", 0.1)]) == ["C", "A", "B", "D"]
    sig = [(f"K{i}", round(random.Random(i).random(), 3)) for i in range(50)]
    assert H.rank_signals(sig) == H.rank_signals(list(reversed(sig)))


def test_random_key_is_fixed_sha256_of_seed_id_and_event_date():
    k = H.random_key(3, "AAPL R735QTJ8XC9X", "2015-01-28")
    assert k == int(hashlib.sha256(b"3|AAPL R735QTJ8XC9X|2015-01-28").hexdigest()[:16], 16)
    ev = [(f"S{i}", "2015-01-28") for i in range(30)]
    assert H.rank_random(ev, 1) == H.rank_random(list(reversed(ev)), 1)
    assert H.rank_random(ev, 1) != H.rank_random(ev, 2)
    assert H.rank_random([("X", "2015-01-28")], 1) == ["X"]


def test_plan_entries_takes_at_most_free_and_k_skipping_held_and_never_queues():
    ranked = ["A", "B", "C", "D", "E"]
    assert H.plan_entries(ranked, {"B"}, free=3, cap=10) == ["A", "C", "D"]
    assert H.plan_entries(ranked, set(), free=5, cap=2) == ["A", "B"]
    assert H.plan_entries(ranked, {"A", "B", "C", "D", "E"}, free=5, cap=5) == []
    assert H.plan_entries(ranked, set(), free=0, cap=5) == []
    assert H.free_slots(10, 9, 0) == 1 and H.free_slots(10, 7, 3) == 0 and H.free_slots(10, 12, 0) == 0


def test_exit_is_placed_at_sessions_held_59_and_ew_membership_is_trailing():
    assert not H.exit_due(None) and not H.exit_due(0) and not H.exit_due(58)
    assert H.exit_due(59) and H.exit_due(60)
    assert H.exit_due(39, 40) and not H.exit_due(38, 40)
    assert H.ew_member(100, 100) and H.ew_member(1, 252) and not H.ew_member(0, 252)
    assert not H.ew_member(None, 5) and not H.ew_member(101, 100)


def test_deciles_and_terciles():
    bps = [float(i) for i in range(1, 10)]
    assert H.decile_of(0.5, bps) == 1 and H.decile_of(1.0, bps) == 2 and H.decile_of(9.0, bps) == 10
    assert H.tercile_of(0.0, [1.0, 2.0]) == 1 and H.tercile_of(1.5, [1.0, 2.0]) == 2 and H.tercile_of(2.0, [1.0, 2.0]) == 3
    x = list(np.random.default_rng(3).normal(size=1000))
    assert H.breakpoints_of(x, H.DECILE_QS) == pytest.approx(list(np.quantile(x, H.DECILE_QS)))


def test_bar_date_handles_both_lean_end_time_conventions():
    from datetime import datetime, date
    assert H.bar_date(datetime(2015, 1, 28, 16, 0)) == date(2015, 1, 28)
    assert H.bar_date(datetime(2015, 1, 29, 0, 0)) == date(2015, 1, 28)


# ---------------------------------------------------------------- S017 order flow, day by day
class Book:
    """Mirror of S017's order flow (one code path for every book): at the close of session t, exits due (sessions held
    >= 59), then today's universe events (decision session = E+1 = t) ranked by the book's rule fill the free slots
    (held + pending buys occupy slots); orders execute at the open of t+1. No top-up exists anywhere."""

    def __init__(self, book, seed=0, slots=10):
        self.book, self.seed, self.slots = book, seed, slots
        self.held = {}            # key -> entry session
        self.pending = {}         # key -> ('buy'|'sell', decision session)
        self.log = []             # (kind, key, decision t, fill t)
        self.bp = H.Breakpoints()

    def open(self, t):
        for k, (side, d) in list(self.pending.items()):
            if side == "sell":
                del self.held[k]
            else:
                assert k not in self.held, "a top-up or duplicate entry"
                self.held[k] = t
            self.log.append((side, k, d, t))
        self.pending = {}

    def close(self, t, events):
        exits = [k for k, e in sorted(self.held.items()) if H.exit_due(t - e) and k not in self.pending]
        for k in exits:
            self.pending[k] = ("sell", t)
        thr, _, newest = self.bp.threshold(t)
        assert newest is None or newest < t
        sig = [(k, a) for k, a, _ in events if H.qualifies(a, thr)]
        kt = len(sig)
        for _, a, _ in events:
            self.bp.add(t, a)
        pend_buys = {k for k, (s, _) in self.pending.items() if s == "buy"}
        free = H.free_slots(self.slots, len(self.held), len(pend_buys - set(self.held)))
        blocked = set(self.held) | pend_buys
        if self.book == "candidate":
            ranked = H.rank_signals(sig)
        else:
            ranked = H.rank_random([(k, e) for k, _, e in events], self.seed)
        entries = H.plan_entries(ranked, blocked, free, kt)
        assert len(entries) <= kt and len(entries) <= free
        for k in entries:
            self.pending[k] = ("buy", t)
        return kt, entries


def simulate(book, seed=0, days=900, n_keys=120, rate=6):
    rng = random.Random(11)
    b = Book(book, seed)
    E_of = {}
    kts = []
    for t in range(days):
        b.open(t)
        assert len(b.held) <= b.slots
        ev = []
        for j in range(rng.randrange(0, rate * 2)):
            k = f"S{rng.randrange(n_keys):03d}"
            ev.append((k, rng.gauss(0.0, 0.05), f"E{t - 1}"))
            E_of[(k, t)] = t - 1                           # event session E = decision - 1
        ev = list({k: (k, a, e) for k, a, e in ev}.values())
        kt, _ = b.close(t, ev)
        kts.append(kt)
    return b, E_of, kts


@pytest.mark.parametrize("book,seed", [("candidate", 0), ("random", 0), ("random", 3)])
def test_s017_flow_timing_capacity_holding(book, seed):
    b, E_of, kts = simulate(book, seed)
    buys = [x for x in b.log if x[0] == "buy"]
    sells = [x for x in b.log if x[0] == "sell"]
    assert buys and sells
    for _, k, d, f in buys:
        assert (k, d) in E_of and f == E_of[(k, d)] + 2      # entry at the open of E+2, decided at the close of E+1
    entry_at = {}
    for side, k, d, f in sorted(b.log, key=lambda x: (x[3], x[0] == "buy")):
        if side == "buy":
            entry_at[k] = f
        else:
            assert f - entry_at.pop(k) == 60                # exit exactly 60 sessions after the entry open
    per_day = {}
    for _, k, d, f in buys:
        per_day[d] = per_day.get(d, 0) + 1
    assert all(per_day[d] <= kts[d] for d in per_day)       # never more than k_t entries on a day
    keys_bought = [k for _, k, _, _ in buys]
    # a stock is never bought again while held (no top-up, no add): consecutive buys of a key are >= 60 sessions apart
    last = {}
    for _, k, d, f in buys:
        assert k not in last or f - last[k] >= 60
        last[k] = f
    assert len(set(keys_bought)) > 10


def test_candidate_and_random_differ_only_in_selection():
    c, _, k_c = simulate("candidate")
    r, _, k_r = simulate("random", 0)
    assert k_c == k_r                                      # the same events, breakpoints and k_t in every book
    assert [x for x in c.log if x[0] == "buy"] != [x for x in r.log if x[0] == "buy"]


# ---------------------------------------------------------------- repository wiring
def test_canary_is_a_byte_copy_of_s017():
    s017 = (ROOT / "strategies/S017_earnings_continuation/main.py").read_bytes()
    assert (ROOT / "strategies/X982_h017_canary/main.py").read_bytes() == s017
    assert b"from qr_h017 import" in s017 and b"load_events" in s017


def test_runner_uploads_h017_files_only_for_strategies_that_import_them():
    from qresearch import run
    for eid in ("E982-01", "E017-01", "E017-02", "E983-01"):
        cfg = json.loads((ROOT / "experiments" / eid / "config.json").read_text())
        files = run.assemble_files(cfg, None, False)
        assert files["qr_h017.py"] == (ROOT / "src/qresearch/lean/qr_h017.py").read_text()
        packed = sorted(p.name for p in (ROOT / "src/qresearch/lean").glob("qr_h017_events*.py"))
        assert all(n in files for n in packed) and len(packed) >= 2
        assert all(len(v) < 64000 for v in files.values())  # QuantConnect per-file limit (D111a)
    other = json.loads((ROOT / "experiments/E016-01/config.json").read_text())
    assert not any(n.startswith("qr_h017") for n in run.assemble_files(other, None, False))


def test_configs_use_h017_rules_and_need_owner_approval_except_the_canary():
    from qresearch import experiment, p2h017, run
    can = json.loads((ROOT / "experiments/E982-01/config.json").read_text())
    assert not can.get("owner_approval_required") and can["params"]["seed"] == 0 and can["params"]["canary"]
    assert can["warmup_start"] == "2009-07-01" and can["start"] == "2010-03-01" and can["end"] == "2021-12-31"
    run.approval_gate(can, None)
    for eid in p2h017.APPROVAL_REQUIRED:
        cfg = json.loads((ROOT / "experiments" / eid / "config.json").read_text())
        experiment.validate(cfg)
        assert cfg["owner_approval_required"]
        with pytest.raises(SystemExit):
            run.approval_gate(cfg, None)
        run.approval_gate(cfg, "D999")
        assert cfg["end"] <= "2021-12-31"
    seeds = [json.loads((ROOT / "experiments" / e / "config.json").read_text())["params"]["seed"] for e in p2h017.RANDOM]
    assert seeds == [1, 2, 3, 4, 5]
    bad = json.loads((ROOT / "experiments/E017-01/config.json").read_text())
    bad["portfolio"] = dict(bad["portfolio"], max_positions=12)
    with pytest.raises(experiment.ConfigError):
        experiment.validate(bad)
    bad = json.loads((ROOT / "experiments/E017-01/config.json").read_text())
    bad["params"]["slots"] = 12
    with pytest.raises(experiment.ConfigError):
        experiment.validate(bad)
