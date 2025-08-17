import random

from app.common.constants import RNG


def clamp(lower, value, upper):
    return max(lower, min(value, upper))


def is_success(chance, generator: random.Random = RNG) -> bool:
    return generator.randrange(100) < chance


def sign(x: int) -> int:
    return 0 if x == 0 else 1 if x > 0 else -1


def dist_inf_norm(p1: tuple[int, int], p2: tuple[int, int]) -> int:
    return max(abs(i - j) for i, j in zip(p1, p2))
