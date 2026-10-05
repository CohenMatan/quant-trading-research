"""Experiment configuration: loading and validation (IDs, split label vs dates, holdout lock)."""
from __future__ import annotations

import json
import pprint
import re
from datetime import date

from . import config
from .holdout import check_dates

EXP_ID = re.compile(r"^E\d{3}-\d{2}$")
# Strategy number ranges keep experiment IDs (E<strategy number>-<run>) unique across prefixes:
# S000 = pipeline demo, S001–S899 research, B900–B949 benchmarks, X950–X999 infrastructure.
STRATEGY_ID = re.compile(r"^(S(?!9)\d{3}|B9[0-4]\d|X9[5-9]\d)$")
HYP_ID = re.compile(r"^H\d{3}$")
VERSION = re.compile(r"^v\d+\.\d+$")
REQUIRED = ("experiment_id", "kind", "strategy_id", "strategy_version", "strategy_dir", "split",
            "start", "end", "cash", "universe", "costs", "portfolio", "params")


class ConfigError(ValueError):
    pass


def withdrawn() -> dict:
    """Experiment id -> reason, for configs withdrawn by an owner decision before they ever ran."""
    import json as _json
    return _json.loads(config.WITHDRAWN_FILE.read_text()) if config.WITHDRAWN_FILE.exists() else {}


def parse(text: str, unlock_file=None) -> dict:
    cfg = json.loads(text)
    validate(cfg, unlock_file=unlock_file)
    return cfg


def validate(cfg: dict, unlock_file=None) -> None:
    missing = [k for k in REQUIRED if k not in cfg]
    if missing:
        raise ConfigError(f"missing keys: {missing}")
    if not EXP_ID.match(cfg["experiment_id"]):
        raise ConfigError(f"bad experiment_id {cfg['experiment_id']!r} (expected E###-##)")
    if cfg["kind"] not in config.EXPERIMENT_KINDS:
        raise ConfigError(f"bad kind {cfg['kind']!r}")
    if not STRATEGY_ID.match(cfg["strategy_id"]):
        raise ConfigError(f"bad strategy_id {cfg['strategy_id']!r}")
    if not VERSION.match(cfg["strategy_version"]):
        raise ConfigError(f"bad strategy_version {cfg['strategy_version']!r}")
    if cfg["kind"] == "research":
        if not HYP_ID.match(str(cfg.get("hypothesis_id") or "")):
            raise ConfigError("research experiments need a hypothesis_id H###")
        if not cfg["strategy_id"].startswith("S"):
            raise ConfigError("research experiments need an S### strategy")
    # the experiment number's first part must be the strategy number
    if cfg["experiment_id"][1:4] != cfg["strategy_id"][1:4]:
        raise ConfigError("experiment_id E###-## must use the strategy's number")
    start, end = date.fromisoformat(cfg["start"]), date.fromisoformat(cfg["end"])
    check_dates(start, end, unlock_file=unlock_file)
    scheme = cfg.get("split_scheme", "cp1")
    splits = config.SCHEMES.get(scheme)
    if splits is None:
        raise ConfigError(f"unknown split_scheme {scheme!r}")
    split = cfg["split"]
    bounds = splits.get(split)
    if bounds is None:
        raise ConfigError(f"unknown split label {split!r} for scheme {scheme}")
    if not (bounds[0] <= start and end <= bounds[1]):
        raise ConfigError(f"dates {start}..{end} are outside split {split} {bounds[0]}..{bounds[1]}")
    if cfg.get("warmup_start"):
        # D114: history-only warm-up (state initialisation); never performance, selection or evaluation
        try:
            ws = date.fromisoformat(cfg["warmup_start"])
        except ValueError:
            raise ConfigError(f"warmup_start {cfg['warmup_start']!r} is not an ISO date")
        if not (config.WARMUP_EARLIEST <= ws < start):
            raise ConfigError(f"warmup_start must be on/after {config.WARMUP_EARLIEST} and before start {start} (D114)")
    kind = cfg["kind"]
    if kind == "research" and split not in ("IS", "VAL", "WF", "HOLDOUT", "DEV"):
        raise ConfigError("research experiments must run on a single split segment (IS, VAL, WF, HOLDOUT or DEV)")
    if split == "DEV" and cfg.get("programme") != "P2":
        raise ConfigError("the DEV split (2010-2021 development) belongs to Phase 2 configs (programme 'P2', D094)")
    if scheme == config.CURRENT_SCHEME:
        if kind in ("research", "benchmark") and start < config.OFFICIAL_START:
            raise ConfigError(f"{kind} experiments cannot start before {config.OFFICIAL_START} (D033)")
        if split == "AUDIT" and kind != "infrastructure":
            raise ConfigError("the AUDIT window is for data audits (kind 'infrastructure') only")
        if split == "STRESS" and kind != "stress":
            raise ConfigError("the STRESS window (1999-2009) is reserved for kind 'stress' (D035)")
        if kind == "stress":
            if split != "STRESS":
                raise ConfigError("stress experiments must use split STRESS")
            if not str(cfg.get("finalist_of") or "").startswith("S"):
                raise ConfigError("stress experiments must name the finalist strategy in 'finalist_of' (D035)")
    if cfg["strategy_id"] == "S016" and cfg.get("params", {}).get("book") in ("gpa", "random"):
        # D115: every trading H016 book (candidate, random controls, sensitivities) uses the H016 portfolio rules
        approved = dict(config.H016_PORTFOLIO)
        if cfg.get("construction_variant") == "H016_P2":
            # D116: pre-declared perturbation P2 (H016_spec.md section 7): 25 slots, minimum new position x 20/25
            if int(cfg["params"].get("slots", -1)) != 25:
                raise ConfigError("H016 perturbation P2 holds 25 slots")
            approved.update(max_positions=25, min_position_usd=config.H016_PORTFOLIO["min_position_usd"] * 20 // 25)
        if cfg["portfolio"] != approved:
            raise ConfigError(f"S016 books must use the H016 portfolio rules {approved} (D115/D116)")
        if cfg["kind"] == "research" and cfg.get("hypothesis_id") != "H016":
            raise ConfigError("S016 research runs belong to hypothesis H016")
        if float(cfg["costs"].get("slippage_bps", -1)) != 10:
            raise ConfigError("base slippage is 10 bps per side (D024); stress multiples via slippage_stress_multiple")
    if cfg["strategy_id"] == "S017" and cfg.get("params", {}).get("book") in ("candidate", "random"):
        # H017 (owner 2026-10-03): every trading book (candidate, random-event controls, sensitivities) uses the H017
        # portfolio rules; the pre-declared perturbations P5/P6 change only the slot count
        approved = dict(config.H017_PORTFOLIO)
        slots = int(cfg["params"].get("slots", 10))
        variant = cfg.get("construction_variant")
        if variant is not None:
            if config.H017_SLOT_VARIANTS.get(variant) != slots:
                raise ConfigError(f"H017 construction variant {variant!r} needs slots {config.H017_SLOT_VARIANTS.get(variant)}")
            approved["max_positions"] = slots
        elif slots != 10:
            raise ConfigError("H017 books hold 10 slots (8/12 only as the pre-declared perturbations P5/P6)")
        if cfg["portfolio"] != approved:
            raise ConfigError(f"S017 books must use the H017 portfolio rules {approved}")
        if cfg["kind"] == "research" and cfg.get("hypothesis_id") != "H017":
            raise ConfigError("S017 research runs belong to hypothesis H017")
        if float(cfg["costs"].get("slippage_bps", -1)) != 10:
            raise ConfigError("base slippage is 10 bps per side (D024); stress multiples via slippage_stress_multiple")
    if cfg["strategy_id"] in ("X984", "S018"):
        # Phase 3 (P3-CP2): every engine run ends on or before 2017-12-31 (search window; 2018+ is the one-shot internal
        # OOS and is never loaded by the engine); the real search / null runs need explicit owner approval
        if cfg["end"] > "2017-12-31":
            raise ConfigError("Phase 3 engine runs end on or before 2017-12-31 (search window)")
        if cfg.get("params", {}).get("mode") == "search" and not cfg.get("owner_approval_required"):
            raise ConfigError("Phase 3 search / null runs need owner_approval_required (owner 2026-10-04)")
    if cfg["strategy_id"] == "S018":
        # H018 frozen search (research/phase3/P3_spec.md, P3-CP2): exactly the frozen window, account, portfolio,
        # costs and architecture (63 sessions, 10 slots; Stage 2 and 126/20 removed); the real world only in the
        # research run, null worlds only in infrastructure runs
        p = cfg.get("params", {})
        names = [w.get("name") for w in p.get("worlds", [])]
        if (cfg.get("hypothesis_id") != "H018" or cfg.get("programme") != "P3" or p.get("mode") != "search"
                or (cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2010-03-01", "2017-12-31", "2009-07-01")
                or float(cfg["cash"]) != 100000 or int(p.get("slots", -1)) != 10 or int(p.get("hold", -1)) != 63
                or cfg["portfolio"] != dict(config.H017_PORTFOLIO)
                or float(cfg["costs"].get("slippage_bps", -1)) != 10):
            raise ConfigError("S018 runs must follow the frozen Phase 3 specification (H018, P3, search mode, "
                              "2010-03-01..2017-12-31, warm-up 2009-07-01, $100K, 10 slots, 63 sessions, 10 bps)")
        if not names or len(set(names)) != len(names):
            raise ConfigError("S018 runs need distinct world names")
        real = [n for n in names if n == "real"]
        trace = bool(p.get("trace"))
        if real and (names != ["real"] or kind != ("infrastructure" if trace else "research")):
            raise ConfigError("the real world runs alone: as the research run, or as an infrastructure finalist trace "
                              "(params.trace, P3_spec.md section 15)")
        if trace and not real:
            raise ConfigError("a finalist trace runs on the real world")
        if not real and kind != "infrastructure":
            raise ConfigError("null-world runs are infrastructure (never strategy trials)")
    if cfg["strategy_id"] in ("X985", "S020"):
        # H019 (research/phase4/P4_xs_spec.md v2; owner 2026-10-04): the frozen window and universe; nothing after
        # 2017-12-31; X985 = the plumbing canary only; S020 = null batches (infrastructure) and the one real evaluation
        # (research), every S020 run only with explicit owner approval
        from . import p4xs
        p = cfg.get("params", {})
        u = cfg["universe"]
        if ((cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2010-01-04", "2017-12-31", "2009-07-01")
                or not u.get("sec_corrections") or float(u.get("min_market_cap", 0)) != 2e9
                or float(u.get("min_price", 0)) != 5.0 or float(u.get("min_avg_dollar_volume", 0)) != 5e6
                or int(u.get("adv_days", 0)) != 20):
            raise ConfigError("H019 runs use 2010-01-04..2017-12-31, warm-up 2009-07-01 and the data-v1 universe "
                              "(>= $2B, >= $5, ADV20 >= $5M, SEC correction layer)")
        mode = p.get("mode")
        if cfg["strategy_id"] == "X985":
            if mode != "canary" or kind != "infrastructure":
                raise ConfigError("X985 runs only the H019 plumbing canary (infrastructure)")
        else:
            if cfg.get("hypothesis_id") != "H019" or cfg.get("programme") != "P4" or not cfg.get("owner_approval_required"):
                raise ConfigError("S020 runs belong to H019 / P4 and need owner_approval_required")
            if mode == "null":
                if tuple(p.get("seeds", ())) not in p4xs.NULL_BATCHES or kind != "infrastructure":
                    raise ConfigError(f"S020 null runs are infrastructure batches {p4xs.NULL_BATCHES}")
            elif mode == "real":
                if kind != "research" or not all(k in p for k in ("threshold_c", "threshold_commit",
                                                                   "null_result_sha256", "spec_sha256")):
                    raise ConfigError("the S020 real evaluation is the research run and carries the pinned null "
                                      "provenance (threshold_c, threshold_commit, null_result_sha256, spec_sha256)")
            else:
                raise ConfigError("S020 modes: null or real")
    if cfg["strategy_id"] in ("X987", "S021"):
        # H020 (research/phase5/H020_spec.md v1 + addendum 1; owner authorisation 2026-10-05, D154): the frozen window
        # and universe; nothing after 2017-12-31; X987 = the plumbing / fidelity canary only; S021 = null batches
        # (infrastructure) and the one real evaluation (research), every S021 run only with explicit owner approval
        from . import p5h020
        p = cfg.get("params", {})
        u = cfg["universe"]
        if ((cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2010-01-04", "2017-12-31", "2009-07-01")
                or not u.get("sec_corrections") or float(u.get("min_market_cap", 0)) != 2e9
                or float(u.get("min_price", 0)) != 5.0 or float(u.get("min_avg_dollar_volume", 0)) != 5e6
                or int(u.get("adv_days", 0)) != 20):
            raise ConfigError("H020 runs use 2010-01-04..2017-12-31, warm-up 2009-07-01 and the data-v1 universe "
                              "(>= $2B, >= $5, ADV20 >= $5M, SEC correction layer)")
        mode = p.get("mode")
        if p.get("dev_max_columns") and not cfg.get("scratch_only"):
            raise ConfigError("dev_max_columns is for scratch development runs only")
        if cfg["strategy_id"] == "X987":
            if mode != "canary" or kind != "infrastructure":
                raise ConfigError("X987 runs only the H020 plumbing / fidelity canary (infrastructure)")
        else:
            if cfg.get("hypothesis_id") != "H020" or cfg.get("programme") != "P5" or not cfg.get("owner_approval_required"):
                raise ConfigError("S021 runs belong to H020 / P5 and need owner_approval_required")
            if mode == "null":
                if tuple(p.get("seeds", ())) not in p5h020.NULL_BATCHES or kind != "infrastructure":
                    raise ConfigError(f"S021 null runs are infrastructure batches {p5h020.NULL_BATCHES}")
            elif mode == "real":
                if kind != "research" or not all(k in p for k in ("c_ic", "c_inc", "threshold_commit",
                                                                   "null_result_sha256", "spec_sha256",
                                                                   "addendum_sha256", "chart_panel_sha256")):
                    raise ConfigError("the S021 real evaluation is the research run and carries the pinned null "
                                      "provenance (c_ic, c_inc, threshold_commit, null_result_sha256, spec_sha256, "
                                      "addendum_sha256, chart_panel_sha256)")
            else:
                raise ConfigError("S021 modes: null or real")
    if scheme == config.CURRENT_SCHEME:
        c = cfg["costs"]
        if (c.get("commission_model") != config.COMMISSION_MODEL
                or float(c.get("commission_per_order", -1)) != config.COMMISSION_PER_ORDER):
            raise ConfigError(f"costs must use the fixed ${config.COMMISSION_PER_ORDER:g} per-order commission (D039)")
        if "slippage_bps" not in c:
            raise ConfigError("costs need slippage_bps (slippage is modelled separately from commission)")
        if kind in ("research", "sizing", "stress") and cfg["strategy_id"] not in ("S016", "S017", "S018", "S020", "S021"):
            model = cfg.get("execution_model", "d044")
            if model not in config.RESEARCH_PORTFOLIOS:
                raise ConfigError(f"unknown execution_model {model!r}")
            approved = dict(config.RESEARCH_PORTFOLIOS[model])
            if kind == "sizing" and cfg.get("construction_variant") == "S2":
                # D083: C03's pre-declared $200K construction variant S2 (owner-approved, CP3e §2) holds
                # 20 positions; every other portfolio rule stays the approved one
                if not (int(cfg["portfolio"].get("max_positions", 0)) == int(cfg["params"].get("slots", -1)) == 20):
                    raise ConfigError("construction variant S2 uses 20 positions (max_positions = slots = 20)")
                approved["max_positions"] = 20
            if cfg["portfolio"] != approved:
                raise ConfigError(f"portfolio must be the approved rules for {model}: "
                                  f"{config.RESEARCH_PORTFOLIOS[model]} (D041/D044/D051)")
            if float(c["slippage_bps"]) != 10:
                raise ConfigError("base slippage is 10 bps per side (D024); stress multiples are separate experiments "
                                  "declared with costs.slippage_stress_multiple")
        if kind == "research" and float(cfg["cash"]) != config.RESEARCH_CASH:
            raise ConfigError("research experiments use the $100,000 primary account (D044); use kind 'sizing'")
        if kind == "sizing":
            if not str(cfg.get("account_size_test_of") or "").startswith("E"):
                raise ConfigError("sizing experiments must name the tested experiment in 'account_size_test_of' (D044)")
            if split not in ("IS", "VAL", "WF", "DEV"):
                raise ConfigError("sizing experiments use IS, VAL, WF or DEV")
    if float(cfg["universe"].get("min_market_cap", 0)) < config.MIN_MARKET_CAP:
        raise ConfigError("universe min_market_cap is below the approved $2B")


def lean_params(cfg: dict, holdout_unlocked: bool) -> str:
    """Contents of the generated qr_params.py uploaded next to the algorithm."""
    exp = {k: cfg[k] for k in ("experiment_id", "start", "end", "cash", "universe", "costs",
                               "portfolio", "params")}
    if cfg.get("warmup_start"):            # D114; absent keys keep earlier runs' generated files byte-identical
        exp["warmup_start"] = cfg["warmup_start"]
    exp["holdout_unlocked"] = bool(holdout_unlocked)
    return ("# Generated by qresearch.run — do not edit.\n"
            f"EXPERIMENT = {pprint.pformat(exp, sort_dicts=True, width=100)}\n")
