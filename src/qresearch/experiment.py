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
    kind = cfg["kind"]
    if kind == "research" and split not in ("IS", "VAL", "WF", "HOLDOUT"):
        raise ConfigError("research experiments must run on a single split segment (IS, VAL, WF or HOLDOUT)")
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
            if cfg["portfolio"] != config.RESEARCH_PORTFOLIO:
                raise ConfigError(f"portfolio must be the approved rules {config.RESEARCH_PORTFOLIO} (D041/D044)")
            if float(c["slippage_bps"]) != 10:
                raise ConfigError("base slippage is 10 bps per side (D024); stress multiples are separate experiments "
                                  "declared with costs.slippage_stress_multiple")
        if kind == "research" and float(cfg["cash"]) != config.RESEARCH_CASH:
            raise ConfigError("research experiments use the $100,000 primary account (D044); use kind 'sizing'")
        if kind == "sizing":
            if not str(cfg.get("account_size_test_of") or "").startswith("E"):
                raise ConfigError("sizing experiments must name the tested experiment in 'account_size_test_of' (D044)")
            if split not in ("IS", "VAL", "WF"):
                raise ConfigError("sizing experiments use IS, VAL or WF")
    if float(cfg["universe"].get("min_market_cap", 0)) < config.MIN_MARKET_CAP:
        raise ConfigError("universe min_market_cap is below the approved $2B")


def lean_params(cfg: dict, holdout_unlocked: bool) -> str:
    """Contents of the generated qr_params.py uploaded next to the algorithm."""
    exp = {k: cfg[k] for k in ("experiment_id", "start", "end", "cash", "universe", "costs",
                               "portfolio", "params")}
    exp["holdout_unlocked"] = bool(holdout_unlocked)
    return ("# Generated by qresearch.run — do not edit.\n"
            f"EXPERIMENT = {pprint.pformat(exp, sort_dicts=True, width=100)}\n")
