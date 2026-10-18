"""LH-CP2 (owner D243) PROPOSED fiscal-period validity rule P for a future Stage C amendment / exception. A PROPOSAL
ONLY: not applied to the frozen Stage C result and not used for any coverage figure in LH-CP2 (its coverage is
deliberately not computed before an owner decision, so it cannot be tuned to the 70% floor).

Inputs per history (newest first, all PIT-available at the decision day): contiguous period ends (the frozen 80-100-day
chain), fiscal labels from each original filing (1-3 = Q1-Q3, 4 = FY, None = unknown), whether a transition-period form
(10-KT / 10-QT, incl. amendments) falls inside the span, and whether any quarter fails the filing-mapping check.
Fiscal-year-end codes are NOT used.

Outcome:
  * invalid  - a transition form inside the span; a mapping failure; or a persistent re-basing of the fiscal labels
               (>= 2 consecutive labelled periods off the dominant cycle = a genuine fiscal-year / quarter change)
  * valid    - every labelled period on one cycle, or exactly one isolated off-cycle label (a tagging error; flagged)
  * unknown  - labels missing; variant P-strict excludes, variant P-assume accepts only when at least 4 labelled
               periods are on the cycle and no transition form exists in the span (assumption: no undisclosed fiscal
               change inside an unlabelled stretch)."""
from __future__ import annotations


def _offsets(labels):
    """Matches of each labelled position against the cycle implied by anchor-label a (newest = a)."""
    best = None
    for a in (1, 2, 3, 4):
        exp = [((a - 1 - k) % 4) + 1 for k in range(len(labels))]
        off = [i for i, (x, e) in enumerate(zip(labels, exp)) if x is not None and x != e]
        if best is None or len(off) < len(best[1]):
            best = (a, off)
    return best


def proposed_validity(labels, transition=False, mapping_fail=False, variant="strict"):
    """-> (outcome, flags). variant 'strict' (unknown excluded) or 'assume' (see module doc)."""
    if transition:
        return "invalid", ("transition_form",)
    if mapping_fail:
        return "invalid", ("mapping",)
    _a, off = _offsets(labels)
    if any(b - a == 1 for a, b in zip(off, off[1:])):
        return "invalid", ("persistent_rebasing",)
    flags = ("isolated_tag_error",) if len(off) == 1 else ()
    if len(off) > 1:
        return "invalid", ("multiple_off_cycle",)
    known = sum(x is not None for x in labels)
    if known == len(labels):
        return "valid", flags
    if variant == "assume" and known - len(off) >= 4:
        return "valid", flags + ("labels_assumed",)
    return "unknown", flags + ("labels_missing",)
