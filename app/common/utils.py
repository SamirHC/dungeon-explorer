"""
Various commonly used functions that are used throughout the application.
"""

import random

from app.common.constants import RNG


def clamp(lower, value, upper):
    """
    Returns a value clamped between a lower and upper bound.
    Assumes lower <= upper.

    :param lower: Lower bound of clamp.
    :param value: Value to be clamped.
    :param upper: Upper bound of clamp.
    :return:      Clamped value such that lower <= clamped value <= upper.
    """
    return max(lower, min(value, upper))


def is_success(chance, generator: random.Random = RNG) -> bool:
    """
    Has a (chance)% probability of returning True.

    :param chance:    Percent chance of returning True. Accepts negative values
                      values over 100.
    :param generator: (optional) A particular random generator to be used.
                      Defaults to None.
    :return:       True iff the random event is succesful based on the given
                   chance.
    """
    return generator.randrange(100) < chance


def sign(x: int) -> int:
    return 0 if x == 0 else 1 if x > 0 else -1
