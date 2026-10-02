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
    if scheme == config.CURRENT_SCHEME:
        c = cfg["costs"]
        if (c.get("commission_model") != config.COMMISSION_MODEL
                or float(c.get("commission_per_order", -1)) != config.COMMISSION_PER_ORDER):
            raise ConfigError(f"costs must use the fixed ${config.COMMISSION_PER_ORDER:g} per-order commission (D039)")
        if "slippage_bps" not in c:
            raise ConfigError("costs need slippage_bps (slippage is modelled separately from commission)")
        if kind in ("research", "sizing", "stress"):
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
