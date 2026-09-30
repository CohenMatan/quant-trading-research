"""X962 pure helper: a deterministic, seeded random order of the eligible stocks (no price input)."""
import random


def pick_order(sids, seed, session):
    """Eligible security ids in a random order fixed by (seed, session). Input order is irrelevant:
    ids are sorted first, so the result depends only on the eligible SET, the seed and the session."""
    order = sorted(sids)
    random.Random(f"x962:{int(seed)}:{int(session)}").shuffle(order)
    return order
